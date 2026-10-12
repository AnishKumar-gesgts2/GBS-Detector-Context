"""Measured larger shot counts, scale probes and isolated process-memory checks.

Supplemental structured family comes from the pre-existing explicit-decomposition
example; it is not an outcome-selected extension of the Haar claim.
"""
import os
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):
    os.environ[key]='1'
import argparse
import json
import gc
import sys
import subprocess
import threading
import time
from pathlib import Path
import numpy as np
import psutil
from threadpoolctl import threadpool_limits
from experiment import OUT,make_case,create,get_distribution,metrics
from methods import Frugal,ExplicitProduct,covariance
from gaussian import distribution


def moderate(m,eta,rep=0):
    case=make_case(m,'flat',eta,rep,'real_orthogonal')
    case['profile']='moderate_heterogeneous';case['seed']+=700000
    case['r']=np.linspace(.45,.8,m)
    case['u']=np.linalg.qr(np.random.default_rng(case['seed']).normal(size=(m,m)))[0].astype(complex)
    case['cov']=covariance(case['r'],case['u'],eta)
    return case


def instantiate(method,case,dll):
    return ExplicitProduct(case['r'],case['u'],case['eta']) if method=='explicit_product' else create(method,case,dll)


def benchmark(method,case,dll,shots,accuracy=False):
    start=time.perf_counter();model=instantiate(method,case,dll);setup=time.perf_counter()-start
    model.sample(2,4) # Load native caches before steady-state timing.
    elapsed=[]
    for rep in range(3):
        start=time.perf_counter();sample=model.sample(shots,case['seed']+rep);elapsed.append(time.perf_counter()-start)
    row={k:v for k,v in case.items() if k not in ('r','u','cov')}
    row.update({'method':method,'shots':shots,'setup_seconds':setup,'sample_seconds':elapsed,
                'median_sample_seconds':float(np.median(elapsed)),
                'median_total_seconds':setup+float(np.median(elapsed)),
                'records_per_second':shots/float(np.median(elapsed))})
    if accuracy:
        p=distribution(case['cov']);q,info=get_distribution(model,case)
        row['accuracy']=metrics(p,q,case['m']);row['accuracy_reference']=info
    if hasattr(model,'diagnostics'):row['diagnostics']=model.diagnostics
    if hasattr(model,'bytes'):row['persistent_array_bytes']=model.bytes
    if isinstance(model,Frugal):model.close()
    return row


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--dll',type=Path,required=True)
    parser.add_argument('--mode',choices=['bulk','scale','memory','memory_worker'],required=True)
    parser.add_argument('--method')
    args=parser.parse_args()
    if args.mode=='memory_worker':
        case=make_case(10,'flat',.4,10)
        process=psutil.Process();baseline=process.memory_info().rss;peak=[baseline];stop=threading.Event()
        def watch():
            while not stop.is_set():
                peak[0]=max(peak[0],process.memory_info().rss);stop.wait(.002)
        thread=threading.Thread(target=watch,daemon=True);thread.start()
        model=create(args.method,case,args.dll);sample=model.sample(10000,case['seed'])
        peak[0]=max(peak[0],process.memory_info().rss)
        stop.set();thread.join()
        row={'method':args.method,'baseline_rss':baseline,'peak_process_rss':peak[0],'increase':peak[0]-baseline,
             'persistent_array_bytes':int(getattr(model,'bytes',0)),
             'scope':'isolated Python worker including model dependencies/native cache loading; not standalone C++ executable memory'}
        if isinstance(model,Frugal):model.close()
        print(json.dumps(row));return
    if args.mode=='memory':
        rows=[]
        for method in ('dodd5','goodman_centered','context6','source2','blocks2'):
            result=subprocess.run([sys.executable,__file__,'--dll',str(args.dll),'--mode','memory_worker','--method',method],capture_output=True,text=True,timeout=60)
            if result.returncode:rows.append({'method':method,'status':'failed','error':result.stderr[-1500:]})
            else:rows.append(json.loads(result.stdout.strip().splitlines()[-1]))
            print('Memory profile completed: '+method,flush=True)
        (OUT/'memory.json').write_text(json.dumps(rows,indent=2));return
    rows=[]
    if args.mode=='bulk':
        cases=[make_case(10,p,e,0) for p in ('heterogeneous','flat','bright') for e in (.3,.5)]
        for i,case in enumerate(cases):
            for method in ('dodd3','dodd5','goodman_centered','goodman_literal','context4','context6'):
                rows.append(benchmark(method,case,args.dll,100000))
            print(f'100,000-record case {i+1}/{len(cases)} completed',flush=True)
        for eta in (.3,.4,.5):
            case=moderate(10,eta)
            for method in ('dodd3','dodd5','goodman_centered','goodman_literal','context6','blocks2','blocks4','explicit_product'):
                rows.append(benchmark(method,case,args.dll,100000,accuracy=True))
            print(f'Nontrivial real-circuit control eta={eta} completed',flush=True)
    else:
        for m in (16,24,32):
            case=make_case(m,'flat',.4,0)
            for method in ('dodd3','dodd5','goodman_centered','goodman_literal','context4','context6'):
                rows.append(benchmark(method,case,args.dll,1000,accuracy=False))
                (OUT/'scale.json').write_text(json.dumps(rows,indent=2))
                print(f'Scale timing {m} modes: {method}',flush=True)
            for method in ('dodd5','goodman_centered','explicit_product'):
                rows.append(benchmark(method,moderate(m,.4),args.dll,10000,accuracy=False))
                (OUT/'scale.json').write_text(json.dumps(rows,indent=2))
                print(f'Structured scale timing {m} modes: {method}',flush=True)
            print(f'Scale probe {m} modes completed; timing only',flush=True)
    (OUT/(args.mode+'.json')).write_text(json.dumps(rows,indent=2))


if __name__=='__main__':
    with threadpool_limits(limits=1):main()
