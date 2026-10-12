"""Bounded sensitivity check of paper-style per-batch Goodman correction.

    This port supplements, rather than replaces, the IID frozen-map benchmark.
    Empirical errors are labeled and cannot be compared to exact law TVDs as
    though they were equal-precision estimates. Batch output dependence remains.
"""
import os
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import json
import time
import numpy as np
from threadpoolctl import threadpool_limits
from experiment import OUT,make_case,metrics
from methods import GoodmanBatch
from gaussian import distribution

rows=[]
with threadpool_limits(limits=1):
    for profile in ('heterogeneous','flat','bright'):
        for eta in (.3,.5):
            case=make_case(10,profile,eta,0)
            p=distribution(case['cov'])
            for centered in (True,False):
                start=time.perf_counter();model=GoodmanBatch(case['r'],case['u'],eta,centered)
                setup=time.perf_counter()-start
                model.sample(32,1)
                times={};hist=np.zeros(1024)
                for shots in (1000,10000,100000):
                    elapsed=[]
                    for rep in range(3):
                        start=time.perf_counter();samples=model.sample(shots,case['seed']+800+rep)
                        elapsed.append(time.perf_counter()-start)
                        if shots==100000:hist+=np.bincount(samples.astype(np.int64),minlength=1024)
                    times[str(shots)]={'sample_seconds':elapsed,'median_total_seconds':setup+float(np.median(elapsed))}
                rng=np.random.default_rng(case['seed'])
                iid=[float(abs(rng.multinomial(300000,p)/300000-p).sum()/2) for _ in range(20)]
                rows.append({'seed':case['seed'],'profile':profile,'eta':eta,
                    'method':'goodman_batch_centered' if centered else 'goodman_batch_literal',
                    'setup_seconds':setup,'timings':times,
                    'empirical_300000_accuracy':metrics(p,hist/hist.sum(),10),
                    'exact_target_iid_300000_tvd_95':float(np.quantile(iid,.95)),
                    'accuracy_scope':'Three separate 100000-record batches pooled. Empirical error includes sampling noise; output need not be IID within a batch.'})
                (OUT/'goodman_batch_check.json').write_text(json.dumps(rows,indent=2))
            print(f'Goodman batch correction checked: {profile}, eta={eta}',flush=True)
