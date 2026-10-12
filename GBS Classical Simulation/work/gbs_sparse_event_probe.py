"""Exact next-click inverse-CDF prototype for sparse, few-source GBS.

Uses source-space determinant identities and inclusion-exclusion; complexity
remains exponential in clicks already observed. No claim of general speedup.
Run: python work/gbs_sparse_event_probe.py
"""
import os
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):
    os.environ[key]='1'
import itertools
import json
import time
from pathlib import Path
import numpy as np
from threadpoolctl import threadpool_limits
from gbs_algorithm_screen import isometry, symplectic, distribution, tvd, SEED

OUT=Path(__file__).resolve().parents[1]/'outputs'/'algorithm_screen_v1'


class Oracle:
    def __init__(self,u,r,eta):
        self.m,self.n=u.shape
        f=symplectic(u)
        self.d=eta*np.r_[np.expm1(-2*r),np.expm1(2*r)]/2
        self.grams=np.stack([np.outer(f[j],f[j])+np.outer(f[j+self.m],f[j+self.m]) for j in range(self.m)])
        self.prefix=np.concatenate([np.zeros((1,2*self.n,2*self.n)),np.cumsum(self.grams,axis=0)])
        self.eye=np.eye(2*self.n)
        self.calls=0
        self.dets=0

    def weight(self,t,clicked):
        """Probability of the specified click history on the first t modes."""
        self.calls+=1
        total=0.0
        for omit_mask in range(1<<len(clicked)):
            gram=self.prefix[t].copy()
            for pos,j in enumerate(clicked):
                if omit_mask>>pos&1:
                    gram-=self.grams[j]
            sign,ld=np.linalg.slogdet(self.eye+gram*self.d[None,:])
            assert sign>0
            self.dets+=1
            total+=(-1)**(len(clicked)-omit_mask.bit_count())*np.exp(-ld/2)
        return total


def safe_prob(value):
    assert -1e-8<=value<=1+1e-8,value
    return float(np.clip(value,0,1))


def sample_scan(oracle,rng):
    clicked=[]
    den=1.0
    for j in range(oracle.m):
        num=oracle.weight(j+1,clicked)
        no=safe_prob(num/den)
        if rng.random()<no:
            den=num
        else:
            clicked.append(j)
            den=den-num
        assert den>1e-13, 'Rare-history precision guard: do not clip/replace silently.'
    return clicked


def sample_jump(oracle,rng):
    clicked=[]
    start=0
    den=1.0
    while start<oracle.m:
        u=rng.random()
        if u<=safe_prob(oracle.weight(oracle.m,clicked)/den):
            break
        lo,hi=start,oracle.m-1
        while lo<hi:
            mid=(lo+hi)//2
            no=safe_prob(oracle.weight(mid+1,clicked)/den)
            if no<u:
                hi=mid
            else:
                lo=mid+1
        j=lo
        den=oracle.weight(j,clicked)-oracle.weight(j+1,clicked)
        clicked.append(j)
        assert den>1e-13, 'Rare-history precision guard: do not clip/replace silently.'
        start=j+1
    return clicked


def next_event_distribution(oracle):
    """Enumerate the jump transition tree only to verify a tiny test case."""
    p=np.zeros(1<<oracle.m)
    def visit(start,clicked,den):
        mask=sum(1<<j for j in clicked)
        p[mask]+=oracle.weight(oracle.m,clicked)
        previous=den
        for j in range(start,oracle.m):
            now=oracle.weight(j+1,clicked)
            mass=previous-now
            if mass>1e-14:
                visit(j+1,clicked+[j],mass)
            previous=now
    visit(0,[],1.0)
    return p


def run():
    OUT.mkdir(parents=True,exist_ok=True)
    validation=[]
    for eta in (0.3,0.5):
        rng=np.random.default_rng(SEED+445)
        u=isometry(8,2,rng)
        r=np.array([0.6,0.45])
        frame=symplectic(u)
        d=eta*np.r_[np.expm1(-2*r),np.expm1(2*r)]/2
        v=np.eye(16)/2+(frame*d)@frame.T
        exact=distribution(v)
        transitions=next_event_distribution(Oracle(u,r,eta))
        err=tvd(exact,transitions)
        assert err<1e-10 and abs(transitions.sum()-1)<1e-10
        oracle=Oracle(u,r,eta)
        rng=np.random.default_rng(SEED+600)
        histogram=np.zeros(256)
        for _ in range(8192):
            histogram[sum(1<<j for j in sample_jump(oracle,rng))]+=1
        reference_rng=np.random.default_rng(SEED+601)
        reference_tvds=[tvd(exact,reference_rng.multinomial(8192,exact)/8192) for _ in range(100)]
        empirical=tvd(exact,histogram/8192)
        validation.append({'eta':eta,'exact_transition_tree_tvd':err,'transition_sum':float(transitions.sum()),
                           'shots':8192,'jump_empirical_tvd':empirical,
                           'exact_iid_tvd_5_95_percentiles':np.percentile(reference_tvds,[5,95]).tolist()})
    rows=[]
    for m,n,rvalue in ((32,2,0.6),(128,2,0.6),(256,2,0.6),(128,8,0.4)):
        u=isometry(m,n,np.random.default_rng(SEED+m+n))
        r=np.full(n,rvalue)
        eta=0.4
        timings={}; records={}; failures=[]
        for label,fn in (('scan',sample_scan),('jump',sample_jump)):
            repeats=[]
            for rep in range(3):
                start=time.perf_counter()
                oracle=Oracle(u,r,eta)
                rng=np.random.default_rng(SEED+rep)
                samples=np.zeros((512,m),dtype=bool)
                try:
                    for shot in range(512):
                        samples[shot,fn(oracle,rng)]=True
                except AssertionError as exc:
                    failures.append({'method':label,'repeat':rep,'completed_shots':shot,'error':str(exc),
                                     'partial_wall_seconds':time.perf_counter()-start})
                    continue
                repeats.append(time.perf_counter()-start)
                records[label]={'mean_clicks':float(samples.sum(axis=1).mean()),'max_clicks':int(samples.sum(axis=1).max()),
                                'probability_calls':oracle.calls,'determinants':oracle.dets}
            timings[label]=repeats
        rows.append({'m':m,'sources':n,'r':rvalue,'eta':eta,'shots':512,
                     'target_mean_photons':float(n*eta*np.sinh(rvalue)**2),
                     'timings_seconds':timings,'speedup':(float(np.median(timings['scan'])/np.median(timings['jump']))
                                                          if len(timings['scan'])==3 and len(timings['jump'])==3 else None),
                     'failures':failures,
                     'records':records,'output':'same dense boolean array in both methods; materialization and oracle preprocessing included'})
    result={'status':'exact arithmetic identity plus tiny full-distribution validation; sparse few-source prototype; no published optimized sampler comparison',
            'limitations':['exponential in observed clicks','prefix Gram storage O(M N^2)','rare-history cancellation; guard raises instead of silently biasing','only 512 shots per timing repeat'],
            'validation':validation,'rows':rows}
    (OUT/'sparse_events.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    with threadpool_limits(1):
        run()
