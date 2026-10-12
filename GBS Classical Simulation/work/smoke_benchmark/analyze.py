"""Summarize immutable measurements, including precision follow-ups and limits."""
import json
from pathlib import Path
import statistics
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

OUT=Path(__file__).resolve().parents[2]/'outputs'/'smoke_comparison_v1'
rows=[json.loads(x) for x in (OUT/'rows.jsonl').read_text().splitlines()]
refinements=json.loads((OUT/'accuracy_refinement.json').read_text())
refined={(r['seed'],r['method']):r for r in refinements}
for row in rows:
    replacement=refined.get((row['seed'],row['method']))
    if replacement:
        row['accuracy']=replacement['accuracy']
        row['accuracy_reference']['replicate_distribution_tvd']=replacement['replicate_distribution_tvd']
        row['accuracy_reference']['points_each']=replacement['points_each']
    spread=row.get('accuracy_reference',{}).get('replicate_distribution_tvd',0)
    row['diagnostic_error_radius']=spread/2
dense=[r for r in rows if r['structure']=='haar' and r['m']>=8]
lookup={(r['seed'],r['method']):r for r in rows}
baseline=['dodd3','dodd5','goodman_centered','goodman_literal']
candidates=['context2','context4','context6','source2','source4','blocks2','blocks4']

def error(r):return r['accuracy']['full_tvd']
def total(r):return r['timings']['10000']['median_total_seconds']
def median(a):return float(np.median(a))

summary={'main_completed':sum(r['status']=='completed' for r in rows),
         'main_failed':sum(r['status']!='completed' for r in rows),
         'main_circuits':len({r['seed'] for r in rows}),
         'dense_primary_circuits':len({r['seed'] for r in dense}),
         'precision_followup_rows':len(refinements),
         'goodman_max_replicate_distribution_tvd':max(r['accuracy_reference'].get('replicate_distribution_tvd',0) for r in rows),
         'diagnostic_radius_warning':'Half replicate TVD is an integration sensitivity diagnostic, not a confidence interval or rigorous bound.',
         'medians_10_mode_dense':{},'screen_24_dense':{},'matched_targets_24_dense':{},
         'bulk_dense':{},'structured_moderate':[],'scale_timing_only':json.loads((OUT/'scale.json').read_text()),
         'memory':json.loads((OUT/'memory.json').read_text())}
for method in baseline+candidates:
    cells=[r for r in dense if r['method']==method and r['m']==10]
    summary['medians_10_mode_dense'][method]={
        'tvd':median([error(r) for r in cells]),'total_10000_seconds':median([total(r) for r in cells]),
        'setup_seconds':median([r['setup_seconds'] for r in cells]),
        'total_clicks_tvd':median([r['accuracy']['total_clicks']['tvd'] for r in cells]),
        'two_group_tvd':median([r['accuracy']['two_group_clicks']['tvd'] for r in cells]),
        'click_cumulant_rmse_by_order':[median([r['accuracy']['cumulants'][k]['rmse_click'] for r in cells]) for k in range(5)]}
for method in candidates:
    cells=[r for r in dense if r['method']==method]
    summary['screen_24_dense'][method]={}
    for b in baseline:
        comparisons=[(r,lookup[(r['seed'],b)]) for r in cells]
        def passes(r,t,adjust=0):
            # Conservative diagnostic variation: candidate up, comparator down.
            ce=error(r)+adjust*r['diagnostic_error_radius']
            be=max(0,error(t)-adjust*t['diagnostic_error_radius'])
            return ce<=1.25*be and total(r)<=total(t)/.75
        summary['screen_24_dense'][method][b]={
            'point_passes':sum(passes(r,t) for r,t in comparisons),
            'diagnostic_conservative_passes':sum(passes(r,t,1) for r,t in comparisons),
            'cases':len(cells)}
    summary['matched_targets_24_dense'][method]={}
    for epsilon in (.005,.02,.05):
        qualifies=[];wins=[];speedups=[]
        for r in cells:
            viable=[lookup[(r['seed'],b)] for b in baseline if error(lookup[(r['seed'],b)])<=epsilon]
            if error(r)<=epsilon and viable:
                best=min(viable,key=total);qualifies.append(r)
                if total(r)<total(best):wins.append(r);speedups.append(total(best)/total(r))
        summary['matched_targets_24_dense'][method][str(epsilon)]={
            'meets_target_and_comparator_exists':len(qualifies),'faster_than_best_qualifying_comparator':len(wins),
            'median_speedup_among_wins':median(speedups) if speedups else None}
bulk=json.loads((OUT/'bulk.json').read_text())
batch=json.loads((OUT/'goodman_batch_check.json').read_text())
summary['goodman_batch_sensitivity']={m:{
    'median_empirical_300000_tvd':median([r['empirical_300000_accuracy']['full_tvd'] for r in batch if r['method']==m]),
    'median_total_seconds_by_shots':{str(n):median([r['timings'][str(n)]['median_total_seconds'] for r in batch if r['method']==m]) for n in (1000,10000,100000)},
    'scope':'Paper-style ensemble correction port; empirical accuracy includes sampling noise, and records need not be IID.'}
    for m in ('goodman_batch_centered','goodman_batch_literal')}
for method in baseline+['context4','context6']:
    cells=[r for r in bulk if r['structure']=='haar' and r['method']==method]
    winning=[]
    if method.startswith('context'):
        for r in cells:
            if error(lookup[(r['seed'],method)])>.02:continue
            comparable=[t for t in bulk if t['seed']==r['seed'] and t['method'] in baseline and error(lookup[(t['seed'],t['method'])])<=.02]
            winning.append(min(t['median_total_seconds'] for t in comparable)/r['median_total_seconds'])
    summary['bulk_dense'][method]={
        'median_total_100000_seconds':median([r['median_total_seconds'] for r in cells]),
        'epsilon_002_qualifying_cases':len(winning) if method.startswith('context') else None,
        'epsilon_002_median_speedup':median(winning) if winning else None}
for eta in (.3,.4,.5):
    cells=[r for r in bulk if r['profile']=='moderate_heterogeneous' and r['eta']==eta]
    summary['structured_moderate'].append({'eta':eta,'methods':{r['method']:{
        'tvd':error(r),'total_100000_seconds':r['median_total_seconds'],
        'diagnostics':r.get('diagnostics',{}),
        'integration_replicate_tvd':r.get('accuracy_reference',{}).get('replicate_distribution_tvd',0)} for r in cells}})
for row in summary['memory']:
    if row['method'].startswith('dodd'):
        row['persistent_array_bytes']=None
        row['persistent_array_note']='Uninstrumented in native wrapper; raw zero was a missing-value default, not zero native memory.'
summary['validation']={
    'max_sample_to_own_law_control_ratio':max(r['last_batch_tvd_to_own_law']/r['own_law_iid_control_95'] for r in rows if r['own_law_iid_control_95']>0),
    'max_source_conditional_roundoff':max(r.get('largest_conditional_roundoff',0) for r in rows),
    'min_block_local_probability':min(r['minimum_local_probability'] for r in rows if 'minimum_local_probability' in r),
    'source_certificate_violations':sum(error(r)>r['certificate']+1e-8 for r in rows if 'certificate' in r)}
(OUT/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')

labels={'dodd3':'Dodd order 3','dodd5':'Dodd order 5','goodman_centered':'Goodman port (centered)',
        'goodman_literal':'Goodman port (literal)','context2':'Context 2','context4':'Context 4',
        'context6':'Context 6','source2':'Retain 2 sources','source4':'Retain 4 sources','blocks2':'Blocks 2','blocks4':'Blocks 4'}
colors={m:('#526273' if m.startswith('dodd') else '#9c68b0' if m.startswith('goodman') else '#087e8b' if m.startswith('context') else '#bb7638' if m.startswith('source') else '#ab5365') for m in labels}
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'figure.facecolor':'#f5f6f8','axes.facecolor':'#f5f6f8'})
fig,axes=plt.subplots(1,2,figsize=(13,5.7),gridspec_kw={'width_ratios':[1.25,1]})
for method in labels:
    r=summary['medians_10_mode_dense'][method]
    axes[0].scatter(r['total_10000_seconds'],r['tvd'],s=55,c=colors[method],marker='s' if method in baseline else 'o')
    axes[0].annotate(labels[method],(r['total_10000_seconds'],r['tvd']),xytext=(4,4 if method not in ('goodman_literal','blocks4','context2') else -13),textcoords='offset points',fontsize=8)
axes[0].set(xscale='log',yscale='log',xlabel='Setup + 10,000 records (seconds)',ylabel='Full-distribution TVD (lower is better)',title='Dense complex Haar circuits: median of 12 cases')
axes[0].axhline(.02,color='#087e8b',alpha=.35,ls='--');axes[0].grid(alpha=.15)
names=['dodd3','dodd5','goodman_centered','explicit_product']
times=[median([r['methods'][m]['total_100000_seconds'] for r in summary['structured_moderate']]) for m in names]
bars=axes[1].barh(['Dodd order 3','Dodd order 5','Goodman centered port','Exact product core'],times,color=['#526273','#526273','#9c68b0','#087e8b'])
for b,t in zip(bars,times):axes[1].text(t+.007,b.get_y()+b.get_height()/2,f'{t:.3f} s',va='center')
axes[1].set(xlim=(0,.53),ylim=(-.6,4.4),xlabel='Setup + 100,000 records (seconds)',title='Eligible real circuits: median of 3 cases')
axes[1].text(.02,.98,'Exact target for this eligible circuit family.\nGeneral complex Haar mixing is excluded.',transform=axes[1].transAxes,fontsize=9,va='top')
fig.suptitle('GBS mechanism screen: useful niches, no general winner',fontsize=15)
fig.text(.02,.015,'Single-thread CPU, warm native caches. Goodman points use frozen calibration ports, not author MATLAB or batch correction.\nDodd: original CPU code, SSE2 generation. Small synthetic systems; medians do not establish matched-error superiority in all cases.',fontsize=8,color='#45515e')
fig.tight_layout(rect=(0,.08,1,.94))
fig.savefig(OUT/'comparison.png',dpi=170)
print(json.dumps({k:summary[k] for k in ('main_completed','main_failed','goodman_max_replicate_distribution_tvd','screen_24_dense','matched_targets_24_dense','bulk_dense','validation')},indent=2))
