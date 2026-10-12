"""Summarize the exploratory screen and regenerate its figure/checksums."""
import hashlib
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs'/'algorithm_screen_v1'


def read(name):
    return json.loads((OUT/f'{name}.json').read_text(encoding='utf-8'))


def stats(values):
    return {'min':float(np.min(values)),'median':float(np.median(values)),'max':float(np.max(values))}


def main():
    comp=read('compression')['rows']
    rank=read('rank_kernel')['rows']
    qmc=read('qmc')['rows']
    reset=read('reset_risk')
    sparse=read('sparse_events')
    summary={'status':'exploratory; none is a matched end-to-end win against published samplers',
             'compression_comparisons':len(comp),'rank_kernel_cells':len(rank),
             'qmc_cells':len(qmc),'block_cells':len(read('blocks')['rows']),
             'decomposition_cells':len(read('decomposition')['rows']),
             'reset_one_mode_cells':len(reset['rows']),
             'reset_two_mode_cells':len(reset['two_mode_conditional_threshold']),
             'compression':{},'rank_speedup':stats([r['speedup'] for r in rank]),
             'rank_max_log_probability_error':max(r['max_log_probability_error'] for r in rank),
             'qmc_vacuum_rmse_improvement':stats([r['rmse_improvement'][0] for r in qmc]),
             'qmc_derivative_rmse_improvement':stats([r['rmse_improvement'][1] for r in qmc]),
             'reset_initial_ensemble':reset['initial_ensemble'],
             'sparse_failed_repeats':sum(len(r['failures']) for r in sparse['rows']),
             'sparse_complete_speedups':[{'m':r['m'],'sources':r['sources'],'speedup':r['speedup']} for r in sparse['rows'] if r['speedup'] is not None]}
    for profile in ('heterogeneous','flat'):
        for rr in (0,2):
            rows=[r for r in comp if r['profile']==profile and r['retained_rank']==rr]
            summary['compression'][f'{profile}_rank{rr}']={'tvd':stats([r['full_tvd'] for r in rows]),
                                                         'bound':stats([r['tvd_bound'] for r in rows])}
    (OUT/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,
                         'axes.labelcolor':'#303742','text.color':'#303742'})
    fig,axes=plt.subplots(1,2,figsize=(11.6,4.1),layout='constrained')
    for profile,color in (('heterogeneous','#2563A6'),('flat','#BC597A')):
        cells=[r for r in comp if r['m']==8 and r['eta']==0.4 and r['profile']==profile]
        ranks=sorted(set(r['retained_rank'] for r in cells))
        med=[np.median([r['full_tvd'] for r in cells if r['retained_rank']==k]) for k in ranks]
        bound=[max(r['tvd_bound'] for r in cells if r['retained_rank']==k) for k in ranks]
        axes[0].plot(ranks,med,'o-',color=color,label=f'{profile}: exact TVD')
        axes[0].plot(ranks,bound,'--',color=color,alpha=.65,label=f'{profile}: certificate')
    axes[0].set(xlabel='Retained quantum sources (8 total)',ylabel='Full click-distribution TVD / upper bound',
                title='Source-spectrum compression: 60% loss')
    axes[0].legend(fontsize=8)
    for ss,color in ((0.12,'#237E73'),(0.25,'#7653A5')):
        cells=[r for r in reset['two_mode_conditional_threshold'] if r['s']==ss]
        axes[1].plot([r['risk'] for r in cells],[r['errors'][1]['absolute_error'] for r in cells],
                     'o-',color=color,label=f'Residual squeeze s = {ss}')
    axes[1].set(xlabel='Quantum fraction of detected intensity (risk R)',
                ylabel='Other-detector conditional click error',
                title='After one subtraction and 50% further transmission')
    axes[1].legend(fontsize=8)
    for ax in axes:
        ax.grid(alpha=.2)
    fig.savefig(OUT/'mechanism_screen.png',dpi=170)
    plt.close(fig)
    files=list(OUT.glob('*'))+[ROOT/'work'/name for name in ('gbs_algorithm_screen.py','gbs_sparse_event_probe.py','gbs_reset_risk_probe.py','gbs_screen_report_assets.py')]
    manifest={}
    for p in sorted(files):
        if not p.is_file() or p.name=='artifact_manifest.json':
            continue
        binary=p.suffix=='.png'
        content=p.read_bytes() if binary else p.read_bytes().replace(b'\r\n',b'\n')
        manifest[str(p.relative_to(ROOT)).replace('\\','/')]={
            'canonical_bytes':len(content),'sha256':hashlib.sha256(content).hexdigest(),
            'normalization':'binary unchanged' if binary else 'UTF-8 text with LF newlines'}
    (OUT/'artifact_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    print(json.dumps({'artifact_count':len(manifest),'sparse_failed_repeats':summary['sparse_failed_repeats'],
                      'max_log_probability_error':summary['rank_max_log_probability_error']},indent=2))


if __name__=='__main__':
    main()
