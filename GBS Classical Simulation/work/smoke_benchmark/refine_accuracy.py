"""Bounded precision follow-up for uncertain Goodman port integrations.

Refinement changes scoring precision only, not calibration or held-out policies.
Original results are retained; the higher-point estimates live separately.
"""
import os
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[key]='1'
import argparse
import json
from pathlib import Path
import numpy as np
from scipy.special import ndtri
from scipy.stats import qmc
from threadpoolctl import threadpool_limits
from experiment import OUT,make_case,create,phase_mixture,metrics
from gbs_algorithm_screen import distribution
parser=argparse.ArgumentParser()
parser.add_argument('--dll',type=Path,required=True)
args=parser.parse_args()
rows=[json.loads(line) for line in (OUT/'rows.jsonl').read_text().splitlines()]
selected=[r for r in rows if r['method'].startswith('goodman') and r['accuracy_reference']['replicate_distribution_tvd']>.004]
results=[]
with threadpool_limits(limits=1):
    for j,row in enumerate(selected):
        case=make_case(row['m'],row['profile'],row['eta'],row['rep'],row['structure'])
        model=create(row['method'],case,args.dll)
        estimates=[]
        for rep in range(2):
            z=ndtri(qmc.Sobol(2*case['m'],scramble=True,seed=case['seed']+9000+rep).random_base2(17))
            estimates.append(phase_mixture(model.probabilities(z)))
        mean=np.mean(estimates,axis=0)
        results.append({'seed':row['seed'],'method':row['method'],'points_each':131072,
                        'replicate_distribution_tvd':float(abs(estimates[0]-estimates[1]).sum()/2),
                        'accuracy':metrics(distribution(case['cov']),mean,case['m'])})
        (OUT/'accuracy_refinement.json').write_text(json.dumps(results,indent=2))
        print(f'Precision follow-up {j+1}/{len(selected)} completed',flush=True)
