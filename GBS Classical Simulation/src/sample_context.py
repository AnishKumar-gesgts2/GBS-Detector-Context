"""Run our bounded detector-context sampler without the vendor baseline DLL.

    python src/sample_context.py --modes 10 --context 6 \
        --shots 10000 --loss 0.6 --check-small --output samples/demo.npz

Zero-mean Gaussian states, hbar=1, q-all/p-all covariance ordering. Optional
full-distribution scoring is separate from record generation and limited to
ten modes. The probability model is unchanged from the measured Context class.
"""
import os
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):
    os.environ[key]='1'
import argparse
import json
from pathlib import Path
import time
import numpy as np
from threadpoolctl import threadpool_limits
from methods import Context,covariance
from gaussian import isometry,physical_min,distribution
from context_tables import induced_distribution


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--modes',type=int,default=10,help='Generated complex-Haar circuit size, 1–64.')
    parser.add_argument('--context',type=int,default=6,help='Parent cap, 0–12; capped at modes minus one.')
    parser.add_argument('--shots',type=int,default=10000)
    parser.add_argument('--loss',type=float,default=.6,help='Total photon loss fraction, 0–1.')
    parser.add_argument('--squeezing',type=float,default=.7,help='Flat input squeezing for generated circuit.')
    parser.add_argument('--seed',type=int,default=2026101171)
    parser.add_argument('--covariance',type=Path,help='Optional .npy matrix or .npz containing cov; zero mean, hbar=1.')
    parser.add_argument('--check-small',action='store_true',help='Score exact induced-law TVD, modes <=10; separate reference enumeration.')
    parser.add_argument('--output',type=Path,default=Path('samples/context_run.npz'))
    args=parser.parse_args()
    if not 1<=args.modes<=64 or not 0<=args.context<=12 or args.shots<1 or args.seed<0:
        parser.error('Require modes 1–64, context 0–12, positive shots, and nonnegative seed.')
    if not 0<=args.loss<=1 or not np.isfinite(args.squeezing) or not 0<=args.squeezing<=3:
        parser.error('Require loss 0–1 and squeezing 0–3.')
    if args.output.suffix.lower()!='.npz':parser.error('--output must have a .npz suffix.')
    if args.output.exists() or args.output.with_suffix('.json').exists():
        parser.error('Output already exists; choose a different path to preserve previous records.')
    if args.covariance:
        loaded=np.load(args.covariance,allow_pickle=False)
        if isinstance(loaded,np.lib.npyio.NpzFile):
            try:v=np.array(loaded['cov'])
            finally:loaded.close()
        else:v=np.array(loaded)
        input_info={'kind':'provided zero-mean covariance','file':str(args.covariance)}
    else:
        rng=np.random.default_rng(args.seed)
        u=isometry(args.modes,args.modes,rng)
        v=covariance(np.full(args.modes,args.squeezing),u,1-args.loss)
        input_info={'kind':'generated complex-Haar circuit','loss':args.loss,'squeezing':args.squeezing}
    if v.ndim!=2 or v.shape[0]!=v.shape[1] or v.shape[0]%2 or not 2<=v.shape[0]<=128:
        parser.error('Covariance must be a square 2M by 2M matrix with 1–64 modes.')
    if np.iscomplexobj(v) or not np.isfinite(v).all() or not np.allclose(v,v.T,atol=1e-10,rtol=0):
        parser.error('Covariance must be finite, real, and symmetric.')
    if np.linalg.eigvalsh(v).min()<=0 or physical_min(v)<-1e-9:
        parser.error('Covariance fails positivity or the hbar=1 uncertainty condition.')
    m=len(v)//2;width=min(args.context,m-1)
    if args.check_small and m>10:parser.error('--check-small is limited to at most 10 modes.')
    start=time.perf_counter();model=Context(v,width);compile_time=time.perf_counter()-start
    start=time.perf_counter();records=model.sample(args.shots,args.seed+1);generation_time=time.perf_counter()-start
    clicks=((records[:,None]>>np.arange(m,dtype=np.uint64))&np.uint64(1)).astype(np.uint8)
    metadata={'algorithm':'exact-marginal pair-MI bounded detector context','modes':m,
        'requested_parent_cap':args.context,'effective_parent_cap':width,'shots':args.shots,'seed':args.seed,
        'input':input_info,'covariance_convention':'zero mean, hbar=1, q-all/p-all',
        'compile_seconds':compile_time,'first_batch_generation_seconds':generation_time,
        'timing_scope':'First batch can include native cache loading or JIT compilation; not comparable to warmed benchmark timing. Saving and optional exact scoring excluded.',
        'table_bytes':model.bytes,'target_accuracy':'Approximate global law; locally exact retained conditionals.',
        'novelty':'Potentially original GBS combination; existing graphical-model ingredients.'}
    if args.check_small:
        p=distribution(v);q=induced_distribution(model.tables)
        metadata['exact_induced_law_tvd']=float(abs(p-q).sum()/2)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    np.savez_compressed(args.output,records=records,clicks=clicks,cov=v,
        parents=model.parents,parent_counts=model.counts,p_zero=model.probs)
    args.output.with_suffix('.json').write_text(json.dumps(metadata,indent=2),encoding='utf-8')
    print(json.dumps({'output':str(args.output),'metadata':str(args.output.with_suffix('.json')),
        'modes':m,'shots':args.shots,'parent_cap':width,
        'exact_induced_law_tvd':metadata.get('exact_induced_law_tvd')},indent=2))


if __name__=='__main__':
    with threadpool_limits(limits=1):main()
