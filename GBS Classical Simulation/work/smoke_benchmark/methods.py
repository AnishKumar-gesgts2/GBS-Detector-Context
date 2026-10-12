"""Mechanism prototypes and a thin binding to the authors' FrugalGBS CPU code.

All numerical work uses hbar=1, q-all/p-all ordering. Candidate generation
does not enumerate the complete output space. Native kernels have no fastmath.
"""
import os
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):
    os.environ[key]='1'
import ctypes
import itertools
import time
from pathlib import Path
import sys
import numpy as np
from numba import njit
from scipy.special import ndtri
from scipy.stats import qmc
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from gbs_algorithm_screen import symplectic, distribution
from gbs_bounded_context_probe import prepare as context_prepare, pair_information


class Frugal:
    def __init__(self,dll,cov,order):
        self.directory=os.add_dll_directory('C:/Strawberry/c/bin') if os.name=='nt' else None
        self.lib=ctypes.CDLL(str(dll))
        lib=self.lib
        lib.fb_prepare.argtypes=[ctypes.c_int,ctypes.c_int,ctypes.c_void_p,ctypes.c_void_p]
        lib.fb_prepare.restype=ctypes.c_void_p
        lib.fb_sample.argtypes=[ctypes.c_void_p,ctypes.c_size_t,ctypes.c_uint,ctypes.c_void_p]
        lib.fb_sample.restype=ctypes.c_int
        lib.fb_coefficients.argtypes=[ctypes.c_void_p,ctypes.c_void_p,ctypes.c_void_p]
        lib.fb_coefficients.restype=ctypes.c_size_t
        lib.fb_free.argtypes=[ctypes.c_void_p]
        lib.fb_probabilities.argtypes=[ctypes.c_void_p,ctypes.c_void_p]
        lib.fb_error.restype=ctypes.c_char_p
        data=np.ascontiguousarray(cov,dtype=float)
        phases=np.zeros(2)
        self.handle=lib.fb_prepare(len(cov)//2,order,data.ctypes.data,phases.ctypes.data)
        if not self.handle: raise RuntimeError(lib.fb_error().decode())
        self.phases=phases.tolist()
        self.m=len(cov)//2
    def sample(self,shots,seed):
        out=np.empty(shots,dtype=np.uint64)
        if self.lib.fb_sample(self.handle,shots,seed,out.ctypes.data):
            raise RuntimeError(self.lib.fb_error().decode())
        return out
    def coefficients(self):
        length=self.lib.fb_coefficients(self.handle,None,None)
        masks=np.empty(length,dtype=np.uint64); values=np.empty(length)
        self.lib.fb_coefficients(self.handle,masks.ctypes.data,values.ctypes.data)
        return masks,values
    def close(self):
        if self.handle: self.lib.fb_free(self.handle); self.handle=None
    def probabilities(self):
        out=np.zeros(1<<self.m)
        if self.lib.fb_probabilities(self.handle,out.ctypes.data):raise RuntimeError(self.lib.fb_error().decode())
        return out


@njit(cache=True)
def sample_context_kernel(parents,counts,probabilities,random):
    shots,m=random.shape
    out=np.zeros(shots,dtype=np.uint64)
    for row in range(shots):
        record=np.uint64(0)
        for i in range(m):
            context=0
            for k in range(counts[i]):
                context|=int((record>>np.uint64(parents[i,k]))&np.uint64(1))<<k
            if random[row,i]>=probabilities[i,context]:record|=np.uint64(1)<<np.uint64(i)
        out[row]=record
    return out


class Context:
    def __init__(self,cov,width):
        scores=pair_information(cov)
        self.tables=context_prepare(cov,width,'pair_mi',scores)
        m=len(self.tables)
        self.parents=np.zeros((m,width),dtype=np.int64)
        self.counts=np.zeros(m,dtype=np.int64)
        self.probs=np.zeros((m,1<<width))
        for i,(parents,p) in enumerate(self.tables):
            self.parents[i,:len(parents)]=parents
            self.counts[i]=len(parents)
            self.probs[i,:len(p)]=p
        self.bytes=self.parents.nbytes+self.counts.nbytes+self.probs.nbytes
        self.m=m
    def sample(self,shots,seed):
        random=np.random.default_rng(seed).random((shots,self.m))
        return sample_context_kernel(self.parents,self.counts,self.probs,random)


def covariance(r,u,eta):
    o=symplectic(u)
    return eta*(o@np.diag(np.r_[np.exp(-2*r),np.exp(2*r)]/2)@o.T)+(1-eta)*np.eye(2*len(r))/2


def noise_factor(w):
    eig,vec=np.linalg.eigh((w+w.T)/2)
    if eig.min() < -1e-7:raise ValueError('nonpositive classical noise')
    return vec[:,eig>1e-12]*np.sqrt(np.maximum(eig[eig>1e-12],0))[None,:]


@njit(cache=True)
def rank_vacuum(mask,mean,frame,gram_modes,d):
    m=len(mean)//2
    rank=len(d)
    gram=np.zeros((rank,rank)); h=np.zeros(rank); squared=0.0
    for i in range(m):
        if (mask>>i)&1:
            squared+=mean[i]**2+mean[i+m]**2
            for j in range(rank):
                h[j]+=frame[i,j]*mean[i]+frame[i+m,j]*mean[i+m]
                for k in range(rank):gram[j,k]+=gram_modes[i,j,k]
    if rank==0:return np.exp(-squared/2)
    matrix=np.eye(rank)+d[:,None]*gram
    sign,ld=np.linalg.slogdet(matrix)
    if sign<=0:raise ValueError('rank determinant sign')
    correction=h@np.linalg.solve(matrix,d*h)
    return np.exp(-0.5*(ld+squared-correction))


@njit(cache=True)
def rank_samples(means,random,frame,grams,d):
    shots,m=random.shape
    out=np.zeros(shots,dtype=np.uint64)
    largest_invalid=0.0
    for row in range(shots):
        clicks=0; zeros=0; previous=1.0
        for i in range(m):
            next_zeros=zeros|(1<<i)
            total=0.0; subset=clicks
            while True:
                parity=0; tmp=subset
                while tmp:
                    parity^=1;tmp&=tmp-1
                term=rank_vacuum(next_zeros|subset,means[row],frame,grams,d)
                total+=(-1 if parity else 1)*term
                if subset==0:break
                subset=(subset-1)&clicks
            if previous<=1e-15:raise ValueError('vanishing conditional prefix')
            pzero=total/previous
            largest_invalid=max(largest_invalid,max(-pzero,pzero-1))
            if pzero < -1e-7 or pzero > 1+1e-7:raise ValueError('unstable conditional probability')
            pzero=min(1.0,max(0.0,pzero))
            if random[row,i]<pzero:
                zeros=next_zeros;previous=total
            else:
                clicks|=1<<i;previous-=total
        out[row]=clicks
    return out,largest_invalid


class SourceCompression:
    def __init__(self,r,u,eta,keep):
        m=len(r);o=symplectic(u)
        a=1-eta+eta*np.exp(-2*r); b=1-eta+eta*np.exp(2*r)
        residual=-.5*np.log(a)
        order=np.argsort(-residual)
        self.keep=order[:keep]
        active=np.r_[self.keep,self.keep+m]
        self.frame=np.ascontiguousarray(o[:,active])
        self.d=np.r_[(a[self.keep]-1)/2,(1/a[self.keep]-1)/2]
        self.grams=np.array([np.outer(self.frame[i],self.frame[i])+np.outer(self.frame[i+m],self.frame[i+m]) for i in range(m)])
        wdiag=(b-1/a)/2
        self.factor=np.ascontiguousarray(o[:,m:]*np.sqrt(np.maximum(wdiag,0))[None,:])
        sq=np.zeros(m);sq[self.keep]=residual[self.keep]
        self.target=o@np.diag(np.r_[np.exp(-2*sq),np.exp(2*sq)+b-1/a]/2)@o.T
        dropped=order[keep:]
        self.bound=float(np.sqrt(-np.expm1(-np.log(np.cosh(residual[dropped])).sum())))
        self.bytes=self.frame.nbytes+self.grams.nbytes+self.factor.nbytes+self.d.nbytes
        self.m=m
        self.roundoff=0.0
    def sample(self,shots,seed):
        rng=np.random.default_rng(seed)
        means=np.ascontiguousarray(rng.normal(size=(shots,self.m))@self.factor.T)
        out,error=rank_samples(means,rng.random((shots,self.m)),self.frame,self.grams,self.d)
        self.roundoff=max(self.roundoff,error)
        return out


def psd_root(matrix,inverse=False):
    values,vectors=np.linalg.eigh((matrix+matrix.T)/2)
    floor=max(1e-12,np.max(np.abs(values))*1e-10)
    if inverse:
        vals=np.where(values>floor,1/np.sqrt(np.maximum(values,floor)),0)
    else:
        vals=np.sqrt(values.astype(complex))
    return (vectors*vals)@vectors.T


class Goodman:
    """Equation-based port, analytic target moments; two Eq.11 conventions.

    No MATLAB execution claim. Corrections are learned on an independent fixed
    calibration ensemble, then frozen before IID output generation. This differs
    from updating ensemble corrections on the requested output batch.
"""
    def __init__(self,r,u,eta,centered=True,calibration=16384,seed=2026101147):
        self.m=len(r);self.u=u;self.eta=eta;self.centered=centered
        n=np.sinh(r)**2; anomalous=-np.sinh(r)*np.cosh(r)
        self.dp=np.sqrt(((n+anomalous)/2).astype(complex))
        self.dm=np.sqrt(((n-anomalous)/2).astype(complex))
        cov=covariance(r,u,eta)
        target=np.zeros((self.m,self.m)); mean=np.zeros(self.m)
        for i in range(self.m):
            ids=[i,i+self.m]
            vi=cov[np.ix_(ids,ids)]
            mean[i]=1/np.sqrt(np.linalg.det(vi+np.eye(2)/2))
            ni=(vi.trace()-1)/2
            mi=(vi[0,0]-vi[1,1]+2j*vi[0,1])/2
            target[i,i]=1/np.sqrt((1+2*ni)**2-4*abs(mi)**2)
            for j in range(i):
                ij=[i,j,i+self.m,j+self.m]
                target[i,j]=target[j,i]=1/np.sqrt(np.linalg.det(cov[np.ix_(ij,ij)]+np.eye(4)/2))
        self.mean=mean
        self.target=target-np.outer(mean,mean) if centered else target
        self.root=psd_root(self.target)
        self.minimum_target_eigenvalue=float(np.linalg.eigvalsh(self.target).min())
        self.transforms=[]
        if calibration==0:
            self.bytes=self.u.nbytes+self.root.nbytes
            return
        projected=np.clip(self.raw(np.random.default_rng(seed).normal(size=(calibration,2*self.m))).real,0,1)
        for _ in range(10):
            mu=projected.mean(axis=0)
            centered_data=projected-mu
            moment=(centered_data.T@centered_data)/len(projected) if self.centered else (projected.T@projected)/len(projected)
            transform=psd_root(moment,inverse=True)@self.root
            self.transforms.append((mu,transform))
            projected=np.clip((centered_data@transform+self.mean).real,0,1)
        self.bytes=self.u.nbytes+self.root.nbytes+sum(a.nbytes+b.nbytes for a,b in self.transforms)
    def raw(self,z):
        m=self.m
        alpha=self.dp*z[:,:m]+1j*self.dm*z[:,m:]
        beta=self.dp*z[:,:m]-1j*self.dm*z[:,m:]
        return np.exp(-self.eta*(alpha@self.u.T)*(beta@self.u.conj().T))
    def probabilities(self,z):
        projected=np.clip(self.raw(z).real,0,1)
        for mu,transform in self.transforms:
            projected=np.clip(((projected-mu)@transform+self.mean).real,0,1)
        return projected
    def sample(self,shots,seed):
        rng=np.random.default_rng(seed)
        p=self.probabilities(rng.normal(size=(shots,2*self.m)))
        bits=rng.random(p.shape)>=p
        return pack(bits)


class GoodmanBatch(Goodman):
    """Paper-style batch correction port; output records need not be IID.

    Target moments and both Eq.11 interpretations follow Goodman above. Unlike
    the primary frozen-calibration comparison, all ten transformations are
    estimated on each requested output batch and their cost is timed.
    """
    def __init__(self,r,u,eta,centered=True):
        super().__init__(r,u,eta,centered=centered,calibration=0)
    def sample(self,shots,seed):
        rng=np.random.default_rng(seed)
        projected=np.clip(self.raw(rng.normal(size=(shots,2*self.m))).real,0,1)
        for _ in range(10):
            mu=projected.mean(axis=0); data=projected-mu
            moment=(data.T@data if self.centered else projected.T@projected)/len(projected)
            transform=psd_root(moment,inverse=True)@self.root
            projected=np.clip((data@transform+self.mean).real,0,1)
        return pack(rng.random(projected.shape)>=projected)


@njit(cache=True)
def pack(bits):
    out=np.zeros(len(bits),dtype=np.uint64)
    for row in range(len(bits)):
        for j in range(bits.shape[1]):
            if bits[row,j]:out[row]|=np.uint64(1)<<np.uint64(j)
    return out


def project_blocks(cov,block_size):
    import cvxpy as cp
    m=len(cov)//2
    blocks=[list(range(j,min(j+block_size,m))) for j in range(0,m,block_size)]
    assignment=np.zeros(m,dtype=int)
    for k,block in enumerate(blocks):assignment[block]=k
    aq=np.r_[assignment,assignment]
    off=aq[:,None]!=aq[None,:]
    omega=np.block([[np.zeros((m,m)),np.eye(m)],[-np.eye(m),np.zeros((m,m))]])
    x=cp.Variable((2*m,2*m),symmetric=True); delta=cp.Variable(nonneg=True)
    physical=cp.bmat([[x,-omega/2],[omega/2,x]])
    problem=cp.Problem(cp.Minimize(delta+1e-7*cp.trace(x)),[x[off]==0,physical>>0,cov+delta*np.eye(2*m)-x>>0])
    problem.solve(solver='CLARABEL',tol_gap_abs=1e-8,tol_feas=1e-8,tol_gap_rel=1e-8,max_iter=100)
    if x.value is None:raise ValueError('block SDP '+str(problem.status))
    core=(x.value+x.value.T)/2
    core[off]=0
    min_physical=np.linalg.eigvalsh(core+0.5j*omega).min()
    repair=max(0,-float(min_physical))+1e-10
    core+=repair*np.eye(2*m)
    w=cov+float(delta.value)*np.eye(2*m)-core
    min_w=np.linalg.eigvalsh(w).min()
    noise_repair=max(0,-float(min_w))+1e-10
    w+=noise_repair*np.eye(2*m)
    return core,w,blocks,{'solver_status':problem.status,'added_covariance_noise':float(delta.value),
                         'physicality_repair':repair,'noise_repair':noise_repair,'solver_seconds':problem.solver_stats.solve_time}


@njit(cache=True)
def local_block_samples(means,random,modes,blocks,starts,lengths,inverses,logdets,submasks):
    shots=means.shape[0]
    out=np.zeros(shots,dtype=np.uint64)
    minimum=1.0
    for row in range(shots):
        for bi in range(len(lengths)):
            width=lengths[bi]; start=starts[bi]; size=1<<width
            vacuum=np.ones(size)
            for mask in range(1,size):
                ids=np.zeros(2*width,dtype=np.int64);count=0
                for j in range(width):
                    if (mask>>j)&1:
                        ids[count]=blocks[bi,j];count+=1
                for j in range(count):ids[count+j]=ids[j]+modes
                exponent=0.0
                for j in range(2*count):
                    for k in range(2*count):exponent+=means[row,ids[j]]*inverses[start+mask,j,k]*means[row,ids[k]]
                vacuum[mask]=np.exp(-0.5*(logdets[start+mask]+exponent))
            probabilities=vacuum[::-1].copy()
            for j in range(width):
                jump=1<<j
                for begin in range(0,size,2*jump):
                    for k in range(jump):probabilities[begin+jump+k]-=probabilities[begin+k]
            minimum=min(minimum,np.min(probabilities))
            if np.min(probabilities)<-1e-8:raise ValueError('negative block probability')
            cdf=0.0;chosen=size-1
            for pattern in range(size):
                cdf+=max(probabilities[pattern],0)
                if random[row,bi]<cdf:chosen=pattern;break
            for j in range(width):
                if (chosen>>j)&1:out[row]|=np.uint64(1)<<np.uint64(blocks[bi,j])
    return out,minimum


class Blocks:
    def __init__(self,cov,width,decomposition=None):
        core,w,blocks,self.diagnostics=project_blocks(cov,width) if decomposition is None else decomposition
        self.target=core+w
        self.factor=noise_factor(w);self.m=len(cov)//2
        self.lengths=np.array([len(b) for b in blocks],dtype=np.int64)
        self.blocks=np.zeros((len(blocks),width),dtype=np.int64)
        self.starts=np.cumsum(np.r_[0,1<<self.lengths[:-1]]).astype(np.int64)
        count=int(np.sum(1<<self.lengths))
        self.inverses=np.zeros((count,2*width,2*width));self.logdets=np.zeros(count)
        for bi,block in enumerate(blocks):
            self.blocks[bi,:len(block)]=block
            for mask in range(1,1<<len(block)):
                sub=[block[j] for j in range(len(block)) if (mask>>j)&1]
                ids=sub+[j+self.m for j in sub]
                mat=core[np.ix_(ids,ids)]+np.eye(len(ids))/2
                self.inverses[self.starts[bi]+mask,:len(ids),:len(ids)]=np.linalg.inv(mat)
                self.logdets[self.starts[bi]+mask]=np.linalg.slogdet(mat)[1]
        self.bytes=self.factor.nbytes+self.inverses.nbytes+self.logdets.nbytes+self.blocks.nbytes
        self.minimum=1.0
    def sample(self,shots,seed):
        rng=np.random.default_rng(seed)
        means=np.ascontiguousarray(rng.normal(size=(shots,self.factor.shape[1]))@self.factor.T)
        out,minimum=local_block_samples(means,rng.random((shots,len(self.lengths))),self.m,self.blocks,self.starts,self.lengths,self.inverses,self.logdets,np.zeros(1,dtype=np.int64))
        self.minimum=min(self.minimum,minimum)
        return out


class ExplicitProduct(Blocks):
    """Exact output-product Gaussian core for an eligible real interferometer.

The correlated classical noise is retained. The sufficient spectral condition
is checked, so this is not substituted on generic complex-Haar circuits.
"""
    def __init__(self,r,u,eta):
        m=len(r)
        if abs(u.imag).max()>1e-12:raise ValueError('explicit product requires real interferometer')
        a=1-eta+eta*np.exp(-2*r);b=1-eta+eta*np.exp(2*r)
        smallest=float(a.min())
        if b.min()<1/smallest-1e-12:raise ValueError('product spectral condition fails')
        cov=covariance(r,u,eta)
        core=np.diag(np.r_[np.full(m,smallest),np.full(m,1/smallest)]/2)
        w=cov-core
        omega=np.block([[np.zeros((m,m)),np.eye(m)],[-np.eye(m),np.zeros((m,m))]])
        assert np.linalg.eigvalsh(core+.5j*omega).min()>-1e-10
        assert np.linalg.eigvalsh(w).min()>-1e-10
        diagnostics={'construction':'explicit common-squeezing product core','added_covariance_noise':0.0,
                     'target_covariance_max_error':float(abs(core+w-cov).max()),'classical_noise_min_eigenvalue':float(np.linalg.eigvalsh(w).min())}
        super().__init__(cov,1,(core,w,[[i] for i in range(m)],diagnostics))
