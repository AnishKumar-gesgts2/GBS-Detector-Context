"""Bounded, fixed-protocol prototype comparison; not a hardware reproduction.

Author CPU sampler for Dodd; explicit equation ports for Goodman. Reference
enumeration is scoring-only. Raw per-cell failures and uncertainties retained.
"""
import os
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):
    os.environ[key]='1'
import argparse
import gc
import hashlib
import itertools
import json
import platform
import sys
import time
import threading
from pathlib import Path
import numpy as np
from scipy.special import ndtri
from scipy.stats import qmc,pearsonr
import psutil
from threadpoolctl import threadpool_limits,threadpool_info
from methods import Frugal,Context,SourceCompression,Goodman,Blocks,covariance,rank_vacuum,pack
from gaussian import distribution,isometry,tor_reference
from context_tables import induced_distribution
from correlations import walsh,cumulants

from benchmark_paths import PROJECT as ROOT, OUT
SEED=2026101171
METHODS=['dodd3','dodd5','goodman_centered','goodman_literal','context2','context4','context6','source2','source4','blocks2','blocks4']


def make_case(m,profile,eta,rep,structure='haar'):
    seed=SEED+10000*m+1000*['heterogeneous','flat','bright'].index(profile)+int(eta*100)*10+rep+(500000 if structure!='haar' else 0)
    rng=np.random.default_rng(seed)
    r=np.r_[.8,.65,np.linspace(.04,.12,m-2)] if profile=='heterogeneous' else np.full(m,1.0 if profile=='bright' else .7)
    u=isometry(m,m,rng) if structure=='haar' else np.linalg.qr(rng.normal(size=(m,m)))[0].astype(complex)
    return {'m':m,'profile':profile,'eta':eta,'rep':rep,'structure':structure,'seed':seed,'r':r,'u':u,'cov':covariance(r,u,eta)}


def create(method,case,dll):
    v=case['cov'];r=case['r'];u=case['u'];eta=case['eta']
    if method.startswith('dodd'):return Frugal(dll,v,int(method[-1]))
    if method.startswith('context'):return Context(v,int(method[-1]))
    if method.startswith('source'):return SourceCompression(r,u,eta,min(int(method[-1]),len(r)))
    if method.startswith('blocks'):return Blocks(v,int(method[-1]))
    return Goodman(r,u,eta,centered=method=='goodman_centered',seed=case['seed']+77)


def phase_mixture(pzero):
    m=pzero.shape[1]
    total=np.zeros(1<<m)
    for begin in range(0,len(pzero),128):
        p=pzero[begin:begin+128]
        terms=np.ones((len(p),1))
        for i in range(m):
            terms=np.concatenate([terms*p[:,i,None],terms*(1-p[:,i,None])],axis=1)
        total+=terms.sum(axis=0)
    return total/len(pzero)


def get_distribution(model,case):
    if isinstance(model,Frugal):return model.probabilities(),{'reference_kind':'forced paths using original marginal helpers'}
    if isinstance(model,Context):return induced_distribution(model.tables),{'reference_kind':'exact local-table product'}
    if isinstance(model,(SourceCompression,Blocks)):
        return distribution(model.target),{'reference_kind':'exact Gaussian covariance of implemented target'}
    estimates=[]
    for rep in range(2):
        z=ndtri(qmc.Sobol(2*case['m'],scramble=True,seed=case['seed']+9000+rep).random_base2(15))
        estimates.append(phase_mixture(model.probabilities(z)))
    mean=np.mean(estimates,axis=0)
    spread=float(np.abs(estimates[0]-estimates[1]).sum()/2)
    return mean,{'reference_kind':'two scrambled Sobol integrations of frozen probability map','points_each':32768,
                 'replicate_distribution_tvd':spread,'replicate_full_tvds':[]}


def grouped(p,m,groups):
    states=np.arange(1<<m,dtype=np.int64)
    index=np.zeros(len(p),dtype=np.int64);radix=1
    for group in groups:
        count=sum((states>>j)&1 for j in group)
        index+=radix*count;radix*=len(group)+1
    return np.bincount(index,weights=p,minlength=radix)


def metrics(p,q,m):
    assert p.min()>=0 and q.min()>=-1e-12 and abs(q.sum()-1)<1e-8
    cp=cumulants(walsh(p));cq=cumulants(walsh(q))
    cumulant_metrics=[]
    for order in range(1,min(5,m)+1):
        ids=[i for i in range(1<<m) if i.bit_count()==order]
        a=cp[ids];b=cq[ids]
        slope=float(a@b/(a@a)) if a@a>1e-20 else None
        corr=float(np.corrcoef(a,b)[0,1]) if len(ids)>1 and a.std()>1e-15 and b.std()>1e-15 else None
        # parity cumulants -> click cumulants, except singles.
        factor=2**order if order>1 else 2
        cumulant_metrics.append({'order':order,'rmse_click':float(np.sqrt(np.mean((a-b)**2))/factor),
                                 'max_abs_click':float(abs(a-b).max()/factor),'slope_through_origin_parity':slope,'pearson':corr})
    gp=grouped(p,m,[list(range(m))]);gq=grouped(q,m,[list(range(m))])
    hp=grouped(p,m,[list(range(m//2)),list(range(m//2,m))]);hq=grouped(q,m,[list(range(m//2)),list(range(m//2,m))])
    def diagnostic(a,b):
        valid=a>1e-12
        return {'tvd':float(abs(a-b).sum()/2),'pearson_discrepancy_per_shot':float(np.sum((a[valid]-b[valid])**2/a[valid]))}
    counts=np.array([i.bit_count() for i in range(1<<m)])
    sectors=[]
    for c in range(m+1):
        mask=counts==c;mass=p[mask].sum();qmass=q[mask].sum()
        if mass>1e-9 and qmass>1e-9:
            pp=p[mask]/mass;qq=q[mask]/qmass
            cross=float(-np.sum(qq*np.log(np.maximum(pp,1e-300))))
            entropy=float(-np.sum(pp*np.log(np.maximum(pp,1e-300))))
            linear=float(np.sum(pp*qq)/np.sum(pp*pp))
            sectors.append({'clicks':c,'target_mass':float(mass),'candidate_mass':float(qmass),
                            'conditional_tvd':float(abs(pp-qq).sum()/2),
                            'goodman_log_cross_entropy':cross,'target_entropy':entropy,
                            'dodd_linear_overlap_ratio':linear})
    return {'full_tvd':float(abs(p-q).sum()/2),'cumulants':cumulant_metrics,
            'total_clicks':diagnostic(gp,gq),'two_group_clicks':diagnostic(hp,hq),'sectors':sectors}


def self_checks(dll):
    results=[]
    for k in (3,5):
        f=Frugal(dll,np.eye(12)/2,k)
        assert np.all(f.sample(4096,9)==0)
        assert abs(f.probabilities()[0]-1)<1e-12
        f.close()
    case=make_case(6,'heterogeneous',.4,9)
    truth=distribution(case['cov'])
    assert abs(truth-tor_reference(case['cov'])).max()<1e-9
    direct=cumulants(walsh(truth))
    f=Frugal(dll,case['cov'],5)
    masks,coefficients=f.coefficients()
    error=max(abs(coefficients[j]-direct[int(mask)]) for j,mask in enumerate(masks) if mask)
    assert error<1e-8
    q=f.probabilities();assert abs(q.sum()-1)<1e-10
    observed=np.bincount(f.sample(200000,8).astype(np.int64),minlength=64)/200000
    controls=[]
    rng=np.random.default_rng(5)
    for _ in range(20):controls.append(float(abs(rng.multinomial(200000,q)/200000-q).sum()/2))
    sample_error=float(abs(observed-q).sum()/2)
    assert sample_error<max(controls)*2
    results.append({'frugal_cumulant_max_error':float(error),'frugal_sampling_tvd_to_own_law':sample_error,'iid_control_max':max(controls)})
    f.close()
    f=Frugal(dll,np.eye(12)*1.2,5)
    qq=f.probabilities();pzero=1/1.7
    expected=np.array([pzero**(6-i.bit_count())*(1-pzero)**i.bit_count() for i in range(64)])
    assert abs(qq-expected).max()<1e-10
    f.close()
    for width in (2,4):
        ctx=Context(case['cov'],width);ctx.sample(2,4)
    for keep in (2,4,6):
        source=SourceCompression(case['r'],case['u'],case['eta'],keep)
        source.sample(2,7)
        rng=np.random.default_rng(6)
        mean=rng.normal(size=12)*.2
        for mask in (1,7,31,63):
            sites=[i for i in range(6) if (mask>>i)&1];ids=sites+[j+6 for j in sites]
            pure=source.target-source.factor@source.factor.T
            mat=pure[np.ix_(ids,ids)]+np.eye(len(ids))/2
            dense=np.exp(-.5*(np.linalg.slogdet(mat)[1]+mean[ids]@np.linalg.solve(mat,mean[ids])))
            rank=rank_vacuum(mask,mean,source.frame,source.grams,source.d)
            assert abs(dense-rank)<1e-10
        actual=source.sample(30000,18)
        pq=distribution(source.target)
        hist=np.bincount(actual.astype(np.int64),minlength=64)/len(actual)
        assert abs(hist-pq).sum()/2<.025
    structured=make_case(6,'flat',.4,9,'real_orthogonal')
    block=Blocks(structured['cov'],2)
    assert block.diagnostics['added_covariance_noise']<1e-7
    block.sample(2,8)
    pq=distribution(block.target)
    assert abs(pq-distribution(structured['cov'])).sum()/2<1e-6
    actual=block.sample(30000,8)
    assert abs(np.bincount(actual.astype(np.int64),minlength=64)/30000-pq).sum()/2<.025
    for centered in (True,False):
        good=Goodman(case['r'],case['u'],case['eta'],centered)
        z=ndtri(qmc.Sobol(12,scramble=True,seed=19).random_base2(16))
        raw=good.raw(z)
        error=float(abs(raw.mean(axis=0).real-good.mean).max())
        assert error<.01
        probs=good.probabilities(z)
        assert probs.min()>=0 and probs.max()<=1
        results.append({'goodman_centered':centered,'unprojected_mean_max_error':error,'target_min_eigenvalue':good.minimum_target_eigenvalue})
    return results


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--dll',type=Path,required=True)
    parser.add_argument('--limit',type=int)
    parser.add_argument('--checks-only',action='store_true')
    parser.add_argument('--resume',action='store_true')
    args=parser.parse_args()
    OUT.mkdir(parents=True,exist_ok=True)
    checks=self_checks(args.dll)
    print('Physics and author-sampler checks passed.',flush=True)
    if args.checks_only:
        (OUT/'checks.json').write_text(json.dumps(checks,indent=2));return
    cases=[make_case(m,profile,eta,rep) for m in (6,8,10) for profile in ('heterogeneous','flat','bright') for eta in (.3,.5) for rep in (0,1)]
    cases += [make_case(10,profile,.4,0,'real_orthogonal') for profile in ('heterogeneous','flat','bright')]
    if args.limit:cases=cases[:args.limit]
    protocol={'date':'2026-10-11','base_seed':SEED,'cases':[{k:v for k,v in c.items() if k not in ('r','u','cov')} for c in cases],
              'methods':METHODS,'sample_counts':[1000,10000],'timing_repeats':3,'goodman_calibration':16384,
              'accuracy':'exact induced distributions except two 32768-point integrations for Goodman',
              'gate':'candidate error <=1.25 competitor error, throughput >=0.75 competitor; uncertainty and matched-target frontier take precedence',
              'baseline':'pinned unmodified FrugalGBS CPU generation; Goodman equation ports with frozen independent calibration, two moment interpretations',
              'not_claimed':'hardware reproduction, production MATLAB speed, rigorous scalable certificate, predicted polished improvement'}
    (OUT/'protocol.json').write_text(json.dumps(protocol,indent=2))
    path=OUT/'rows.jsonl'
    rows=[]
    if args.resume and path.exists():rows=[json.loads(line) for line in path.read_text().splitlines() if line]
    done={(r['seed'],r['method']) for r in rows}
    process=psutil.Process()
    for ci,case in enumerate(cases):
        ref_start=time.perf_counter();p=distribution(case['cov']);ref_time=time.perf_counter()-ref_start
        np.savez(OUT/f"case_{case['seed']}.npz",r=case['r'],u=case['u'],cov=case['cov'],target=p)
        # Fixed rotating order counters a systematic warm-cache advantage.
        rotated=METHODS[ci%len(METHODS):]+METHODS[:ci%len(METHODS)]
        for method in rotated:
            if (case['seed'],method) in done:continue
            row={k:v for k,v in case.items() if k not in ('r','u','cov')}
            row.update({'method':method,'reference_setup_seconds_excluded':ref_time})
            model=None
            try:
                t=time.perf_counter();model=create(method,case,args.dll);setup=time.perf_counter()-t
                q,accuracy_info=get_distribution(model,case)
                result=metrics(p,q,case['m'])
                if isinstance(model,Goodman):accuracy_info['full_tvd_uncertainty_scale']=accuracy_info['replicate_distribution_tvd']/2
                timings={};sampler_diagnostics={}
                for shots in (1000,10000):
                    elapsed=[]
                    for rep in range(3):
                        t=time.perf_counter();samples=model.sample(shots,case['seed']+rep+100);elapsed.append(time.perf_counter()-t)
                    timings[str(shots)]={'sample_seconds':elapsed,'median_sample_seconds':float(np.median(elapsed)),
                                         'median_total_seconds':setup+float(np.median(elapsed)),
                                         'records_per_second':shots/float(np.median(elapsed))}
                sampled=np.bincount(samples.astype(np.int64),minlength=1<<case['m'])/len(samples)
                ownlaw_error=float(abs(sampled-q).sum()/2)
                rng=np.random.default_rng(case['seed']+1)
                controls=[float(abs(rng.multinomial(len(samples),q)/len(samples)-q).sum()/2) for _ in range(20)]
                row.update({'status':'completed','setup_seconds':setup,'timings':timings,'accuracy':result,'accuracy_reference':accuracy_info,
                            'last_batch_tvd_to_own_law':ownlaw_error,'own_law_iid_control_95':float(np.quantile(controls,.95)),
                            'process_rss_after_bytes_not_isolated_peak':process.memory_info().rss,
                            'persistent_array_bytes':int(getattr(model,'bytes',0))})
                if isinstance(model,Frugal):
                    row['setup_phases']=model.phases;row['coefficient_count']=len(model.coefficients()[0])
                if isinstance(model,SourceCompression):row['certificate']=model.bound;row['largest_conditional_roundoff']=model.roundoff
                if isinstance(model,Blocks):row['block_diagnostics']=model.diagnostics;row['minimum_local_probability']=model.minimum
                if isinstance(model,Goodman):row['target_min_eigenvalue']=model.minimum_target_eigenvalue
            except Exception as error:
                row.update({'status':'failed','failure':str(error)})
            finally:
                if isinstance(model,Frugal):model.close()
                del model;gc.collect()
            with path.open('a',encoding='utf-8') as file:file.write(json.dumps(row)+'\n')
            rows.append(row)
        print(f"Completed circuit {ci+1}/{len(cases)}: {case['m']} modes, {case['profile']}, eta={case['eta']}, {case['structure']}",flush=True)
    env={'python':platform.python_version(),'numpy':np.__version__,'platform':platform.platform(),'blas':threadpool_info(),
         'logical_cpu_count':os.cpu_count(),'checks':checks,
         'frugal_commit':'fa8b796f2afebd4845a2e335e457735952617ef8','xqsim_checked_commit':'32609f3644ae18bff872b53a32a3a7f58f883b3b',
         'dll_sha256':hashlib.sha256(args.dll.read_bytes()).hexdigest()}
    (OUT/'environment.json').write_text(json.dumps(env,indent=2))


if __name__=='__main__':
    with threadpool_limits(limits=1):main()
