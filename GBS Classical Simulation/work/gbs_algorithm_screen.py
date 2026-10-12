"""Exploratory algorithm mechanisms; not a reproduction of a published sampler.

Run from the project directory: python work/gbs_algorithm_screen.py
Independent seeded circuits, hbar=1, ideal threshold detection, pure loss only.
All numerical outputs are exploratory; the grids were chosen to screen mechanisms.
"""
import os
for key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[key] = '1'
import hashlib
import json
import platform
import time
from pathlib import Path
import numpy as np
import scipy
from scipy.special import ndtri
from scipy.stats import qmc
from threadpoolctl import threadpool_limits, threadpool_info

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'outputs' / 'algorithm_screen_v1'
SEED = 2026101101


def isometry(m, n, rng):
    z = rng.normal(size=(m, n)) + 1j*rng.normal(size=(m, n))
    q, r = np.linalg.qr(z)
    return q*(np.diag(r)/abs(np.diag(r)))


def symplectic(u):
    return np.block([[u.real, -u.imag], [u.imag, u.real]])


def distribution(v):
    m = len(v)//2
    vacuum = np.ones(1 << m)
    for mask in range(1, 1 << m):
        sites = [i for i in range(m) if mask >> i & 1]
        ids = sites + [i+m for i in sites]
        sign, ld = np.linalg.slogdet(v[np.ix_(ids, ids)] + np.eye(len(ids))/2)
        assert sign > 0
        vacuum[mask] = np.exp(-ld/2)
    p = vacuum[::-1].copy()
    for j in range(m):
        blocks = p.reshape(-1, 2*(1 << j))
        blocks[:, 1 << j:] -= blocks[:, :1 << j]
    assert p.min() > -2e-10 and abs(p.sum()-1) < 2e-10
    p = np.maximum(p, 0)
    return p/p.sum()


def tor_reference(v):
    """Independent complex-basis inverse/Torontonian reference, no library use."""
    m = len(v)//2
    eye = np.eye(m)
    f = np.block([[eye, 1j*eye], [eye, -1j*eye]])/np.sqrt(2)
    q = f @ (v+np.eye(2*m)/2) @ f.conj().T
    o = np.eye(2*m)-np.linalg.inv(q)
    denom = np.sqrt(np.linalg.det(q)).real
    out = np.zeros(1 << m)
    for c in range(1 << m):
        sub = c
        while True:
            sites = [j for j in range(m) if sub >> j & 1]
            ids = sites + [j+m for j in sites]
            d = np.linalg.det(np.eye(len(ids))-o[np.ix_(ids, ids)])
            out[c] += (-1)**(c.bit_count()-sub.bit_count())/np.sqrt(d).real/denom
            if sub == 0:
                break
            sub = (sub-1) & c
    return out


def tvd(p, q):
    return float(abs(p-q).sum()/2)


def physical_min(v):
    m = len(v)//2
    omega = np.block([[np.zeros((m,m)), np.eye(m)], [-np.eye(m), np.zeros((m,m))]])
    return float(np.linalg.eigvalsh(v+0.5j*omega).min())


def compression():
    rows = []
    reference_errors = []
    for m in (6, 8, 10):
        for profile in ('heterogeneous', 'flat'):
            r = (np.r_[0.8, 0.65, np.linspace(0.04, 0.12, m-2)]
                 if profile == 'heterogeneous' else np.full(m, 0.7))
            for eta in (0.3, 0.4, 0.5):
                a = 1-eta+eta*np.exp(-2*r)
                b = 1-eta+eta*np.exp(2*r)
                s = -0.5*np.log(a)
                w = np.r_[np.zeros(m), (b-1/a)/2]
                assert w.min() > -1e-12
                for rep in range(2):
                    seed = SEED + m*10000 + (1000 if profile == 'flat' else 0) + int(eta*100)*10 + rep
                    u = isometry(m, m, np.random.default_rng(seed))
                    o = symplectic(u)
                    v = o @ np.diag(np.r_[a,b]/2) @ o.T
                    p = distribution(v)
                    if m == 6 and eta == 0.4 and rep == 0:
                        reference_errors.append(tvd(p, tor_reference(v)))
                    order = np.argsort(-s)
                    counts = np.array([i.bit_count() for i in range(1 << m)])
                    for rank in sorted(set((0,1,2,m//2,m-1,m))):
                        keep = order[:rank]
                        sq = np.zeros(m)
                        sq[keep] = s[keep]
                        pure = np.r_[np.exp(-2*sq), np.exp(2*sq)]/2
                        va = o @ np.diag(pure+w) @ o.T
                        q = distribution(va)
                        drop = order[rank:]
                        bound = float(np.sqrt(-np.expm1(-np.log(np.cosh(s[drop])).sum())))
                        err = tvd(p,q)
                        assert err <= bound + 1e-9
                        sectors = []
                        for c in range(2,m+1):
                            mask = counts == c
                            mass, aqmass = float(p[mask].sum()), float(q[mask].sum())
                            if mass > 1e-9 and aqmass > 1e-9:
                                sectors.append({'clicks':c,'p_mass':mass,'q_mass':aqmass,
                                                'conditional_tvd':tvd(p[mask]/mass,q[mask]/aqmass)})
                        rows.append({'m':m,'profile':profile,'eta':eta,'rep':rep,'seed':seed,
                                     'r':r.tolist(),'retained_rank':rank,'full_tvd':err,'tvd_bound':bound,
                                     'physical_min_eigenvalue':physical_min(va),
                                     'target_mean_clicks':float(p@counts),
                                     'quantum_photons_original':float(np.sinh(s)**2 @ np.ones(m)),
                                     'quantum_photons_retained':float(np.sinh(sq)**2 @ np.ones(m)),
                                     'sectors':sectors})
    assert max(reference_errors) < 1e-9
    return {'scope':'exact distribution comparison, not a runtime or sampler benchmark',
            'independent_tor_reference_tvds':reference_errors,'rows':rows}


def kernel_bench():
    rows = []
    for m in (64,128,256):
        for n in (2,8,32):
            rng = np.random.default_rng(SEED+m*100+n)
            u = isometry(m,n,rng)
            frame = symplectic(u)
            r = np.linspace(0.4,0.8,n)
            d = np.r_[np.expm1(-2*r),np.expm1(2*r)]/2
            for k in sorted(set((8,32,min(m,128)))):
                subsets = [np.sort(rng.choice(m,k,replace=False)) for _ in range(12)]
                ids = [np.r_[ss,ss+m] for ss in subsets]
                etas = np.linspace(0.3,0.5,21)
                times = {'dense':[],'rank':[]}
                prep = {'dense':[],'rank':[]}
                logs = {}
                for label in times:
                    for rep in range(3):
                        start=time.perf_counter()
                        if label == 'dense':
                            mats=[(frame[ii]*d)@frame[ii].T for ii in ids]
                        else:
                            mats=[(frame[ii].T@frame[ii])*d[None,:] for ii in ids]
                        pt=time.perf_counter()-start
                        out=[]
                        start=time.perf_counter()
                        for mat in mats:
                            for eta in etas:
                                sign, ld=np.linalg.slogdet(np.eye(len(mat))+eta*mat)
                                assert sign>0
                                out.append(-ld/2)
                        times[label].append(time.perf_counter()-start)
                        prep[label].append(pt)
                        logs[label]=np.array(out)
                error=float(abs(logs['dense']-logs['rank']).max())
                assert error<1e-10
                dt=float(np.median(np.array(times['dense'])+prep['dense']))
                rt=float(np.median(np.array(times['rank'])+prep['rank']))
                rows.append({'m':m,'sources':n,'subset_modes':k,'queries':252,
                             'dense_matrix_dimension':2*k,'rank_matrix_dimension':2*n,
                             'dense_total_seconds':dt,'rank_total_seconds':rt,'speedup':dt/rt,
                             'dense_query_seconds':times['dense'],'rank_query_seconds':times['rank'],
                             'dense_prep_seconds':prep['dense'],'rank_prep_seconds':prep['rank'],
                             'max_log_probability_error':error,
                             'dense_cached_matrix_bytes':12*(2*k)**2*8,
                             'rank_cached_matrix_bytes':12*(2*n)**2*8})
    return {'scope':'exact no-click marginal kernel, 12 subsets and 21 loss settings; includes cache construction; excludes common isometry generation; not full sampling', 'rows':rows}


def qmc_bench():
    rows=[]
    for m,n in ((32,4),(64,16)):
        rng=np.random.default_rng(SEED+m)
        u=isometry(m,n,rng)
        r=np.linspace(0.4,0.8,n)
        nn=np.sinh(r)**2
        anomalous=-np.sinh(r)*np.cosh(r)
        dp=np.sqrt(((nn+anomalous)/2).astype(complex))
        dm=np.sqrt(((nn-anomalous)/2).astype(complex))
        frame=symplectic(u)
        d=np.r_[np.expm1(-2*r),np.expm1(2*r)]/2
        for k in (4,m):
            ids=np.r_[np.arange(k),np.arange(k)+m]
            mat=(frame[ids]*d)@frame[ids].T
            for eta in (0.3,0.5):
                qmat=np.eye(2*k)+eta*mat
                truth=float(np.exp(-np.linalg.slogdet(qmat)[1]/2))
                deriv=float(-0.5*truth*np.trace(np.linalg.solve(qmat,mat)))
                for power in (10,12):
                    estimates={}; elapsed={}
                    for method in ('iid','sobol'):
                        vals=[]
                        start=time.perf_counter()
                        for rep in range(16):
                            seed=SEED+rep*100+power
                            if method=='iid':
                                z=np.random.default_rng(seed).normal(size=(2*n,1<<power))
                            else:
                                uniforms=qmc.Sobol(2*n,scramble=True,seed=seed).random_base2(power)
                                z=ndtri(np.clip(uniforms,1e-15,1-1e-15)).T
                            alpha=dp[:,None]*z[:n]+1j*dm[:,None]*z[n:]
                            beta=dp[:,None]*z[:n]-1j*dm[:,None]*z[n:]
                            prod=np.sum((u[:k]@alpha)*(u[:k].conj()@beta),axis=0)
                            f=np.exp(-eta*prod)
                            vals.append([float(f.real.mean()),float((-prod*f).real.mean())])
                        elapsed[method]=time.perf_counter()-start
                        estimates[method]=np.array(vals)
                    rms={key:np.sqrt(np.mean((value-np.array([truth,deriv]))**2,axis=0))
                         for key,value in estimates.items()}
                    rows.append({'m':m,'sources':n,'subset_modes':k,'eta':eta,'samples_per_rep':1<<power,
                                 'replicates':16,'vacuum_truth':truth,'derivative_truth':deriv,
                                 'iid_rmse':rms['iid'].tolist(),'sobol_rmse':rms['sobol'].tolist(),
                                 'rmse_improvement':(rms['iid']/rms['sobol']).tolist(),
                                 'seconds':elapsed,'estimates':{key:val.tolist() for key,val in estimates.items()}})
    return {'scope':'unprojected positive-P vacuum observable and analytic loss derivative; NOT a click-record sampler; deterministic determinant is an easier oracle for these observables', 'rows':rows}


def block_screen():
    rows=[]
    m=8
    r=np.linspace(0.45,0.8,m)
    for structure in ('block_local','haar'):
        for boundary in (0.0,0.05,0.2):
            rng=np.random.default_rng(SEED+300)
            if structure=='haar':
                u=isometry(m,m,rng)
            else:
                u=np.zeros((m,m),complex)
                for j in range(0,m,2):
                    u[j:j+2,j:j+2]=isometry(2,2,rng)
                for j in (1,3,5):
                    rotation=np.eye(m)
                    rotation[j:j+2,j:j+2]=[[np.cos(boundary),-np.sin(boundary)],[np.sin(boundary),np.cos(boundary)]]
                    u=rotation@u
            o=symplectic(u)
            for eta in (0.3,0.5):
                v=eta*(o@np.diag(np.r_[np.exp(-2*r),np.exp(2*r)]/2)@o.T)+(1-eta)*np.eye(2*m)/2
                p=distribution(v)
                va=np.zeros_like(v)
                for j in range(0,m,2):
                    ids=np.r_[np.arange(j,j+2),np.arange(j,j+2)+m]
                    va[np.ix_(ids,ids)]=v[np.ix_(ids,ids)]
                q=distribution(va)
                rows.append({'structure':structure,'boundary_mixing_angle':boundary,'eta':eta,
                             'full_tvd':tvd(p,q),'physical_min_eigenvalue':physical_min(va),
                             'scope':'product of exact two-mode marginals; not a treewidth algorithm'})
    return {'rows':rows}


def cut_entropy(p):
    m=len(p)//2
    ent=[]
    for cut in range(1,m):
        ids=np.r_[np.arange(cut),np.arange(cut)+m]
        v=p[np.ix_(ids,ids)]
        omega=np.block([[np.zeros((cut,cut)),np.eye(cut)],[-np.eye(cut),np.zeros((cut,cut))]])
        nu=np.sort(abs(np.linalg.eigvals(1j*omega@v)))[::2]
        occupation=np.maximum(nu.real-0.5,0)
        entropy=0.0
        for n in occupation:
            entropy+=(n+1)*np.log(n+1)-(n*np.log(n) if n>1e-14 else 0)
        ent.append(float(entropy))
    return max(ent)


def cost_decomposition():
    rows=[]
    for m in (8,16,32):
        r=np.linspace(0.45,0.8,m)
        for eta in (0.3,0.5):
            a=1-eta+eta*np.exp(-2*r)
            b=1-eta+eta*np.exp(2*r)
            s=-np.log(a)/2
            common=float(s.max())
            assert common<=np.log(b).min()/2
            for family in ('real_orthogonal','complex_haar'):
                rng=np.random.default_rng(SEED+m+800)
                u=np.linalg.qr(rng.normal(size=(m,m)))[0] if family=='real_orthogonal' else isometry(m,m,rng)
                o=symplectic(u)
                v=o@np.diag(np.r_[a,b]/2)@o.T
                pmin=o@np.diag(np.r_[np.exp(-2*s),np.exp(2*s)]/2)@o.T
                pproduct=np.diag(np.r_[np.full(m,np.exp(-2*common)),np.full(m,np.exp(2*common))]/2)
                feasibility=float(np.linalg.eigvalsh(v-pproduct).min())
                rows.append({'m':m,'eta':eta,'family':family,
                             'min_photon_core_max_cut_entropy_nats':cut_entropy(pmin),
                             'product_core_max_cut_entropy_nats':cut_entropy(pproduct),
                             'min_photon_core_mean_photons':float(np.sum(np.sinh(s)**2)),
                             'product_core_mean_photons':float(m*np.sinh(common)**2),
                             'product_residue_min_eigenvalue':feasibility,'product_core_feasible':feasibility>=-1e-10})
                if family=='real_orthogonal':
                    assert feasibility>=-1e-10
    return {'scope':'two exact covariance decompositions, structured real-interferometer example; entropy proxy only, not MPS sampling runtime', 'rows':rows}


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    started=time.perf_counter()
    with threadpool_limits(limits=1):
        env={'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__,
             'platform':platform.platform(),'logical_cpu_count':os.cpu_count(),'seed':SEED,
             'blas':[{key:value for key,value in entry.items() if key!='filepath'} for entry in threadpool_info()],
             'status':'exploratory mechanism screen; no published sampler reproduced',
             'date':'2026-10-11'}
        for label,fn in (('compression',compression),('rank_kernel',kernel_bench),('qmc',qmc_bench),('blocks',block_screen),('decomposition',cost_decomposition)):
            start=time.perf_counter()
            result=fn()
            result['wall_seconds']=time.perf_counter()-start
            (OUT/f'{label}.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
            print(label,len(result.get('rows',[])),round(result['wall_seconds'],2),flush=True)
        env['total_wall_seconds']=time.perf_counter()-started
        env['script_sha256']=hashlib.sha256(Path(__file__).read_bytes().replace(b'\r\n',b'\n')).hexdigest()
        env['script_hash_normalization']='UTF-8 text with LF newlines'
        (OUT/'environment.json').write_text(json.dumps(env,indent=2),encoding='utf-8')


if __name__=='__main__':
    main()
