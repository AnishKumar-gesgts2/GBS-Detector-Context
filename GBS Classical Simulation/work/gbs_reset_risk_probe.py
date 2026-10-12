"""One-mode local reset-error screen for adaptive non-Gaussian retention.

This is NOT an implementation of Lim's trajectory sampler. It compares one
photon-subtracted displaced squeezed state with its moment-matched Gaussian,
using finite Fock matrices. No multimode/runtime/global-error claim follows.
"""
import os
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):
    os.environ[key]='1'
import json
from pathlib import Path
import numpy as np
from scipy.linalg import expm
from scipy.integrate import quad
from scipy.special import ndtr
from scipy.sparse import csr_matrix, eye as speye, kron
from scipy.sparse.linalg import expm_multiply
from threadpoolctl import threadpool_limits

OUT=Path(__file__).resolve().parents[1]/'outputs'/'algorithm_screen_v1'


def conditional(s,alpha,cutoff):
    a=np.diag(np.sqrt(np.arange(1,cutoff)),1).astype(complex)
    ad=a.conj().T
    a2=a@a
    sq=expm(s*(a2-ad@ad)/2)
    disp=expm(alpha*ad-alpha.conjugate()*a)
    before=disp@sq[:,0]
    after=a@before
    rate=float(np.vdot(after,after).real)
    after/=np.sqrt(rate)
    mu=np.vdot(after,a@after)
    nn=float(np.vdot(after,ad@a@after).real)-abs(mu)**2
    mm=np.vdot(after,a2@after)-mu**2
    nu=np.sqrt(max(0,(nn+0.5)**2-abs(mm)**2))
    nth=max(0,float(nu-0.5))
    gs=0.25*np.log((nn+0.5+abs(mm))/(nn+0.5-abs(mm)))
    z=gs*np.exp(1j*np.angle(-mm))
    sg=expm((z.conjugate()*a2-z*ad@ad)/2)
    dg=expm(mu*ad-mu.conjugate()*a)
    thermal=(nth/(1+nth))**np.arange(cutoff)/(1+nth)
    transform=dg@sg
    gaussian=(transform*thermal)@transform.conj().T
    rho=np.outer(after,after.conj())
    dist=float(abs(np.linalg.eigvalsh(rho-gaussian)).sum()/2)
    diag=np.real(np.diag(rho))
    gd=np.real(np.diag(gaussian))
    probs=[]
    for eta in (0.1,0.5,1.0):
        noclick=(1-eta)**np.arange(cutoff)
        probs.append({'remaining_transmission':eta,'click_probability_error':float(abs((diag-gd)@noclick))})
    risk=float(np.sinh(s)**2/(abs(alpha)**2+np.sinh(s)**2))
    return {'s':s,'alpha_real':float(alpha.real),'alpha_imag':float(alpha.imag),'cutoff':cutoff,
            'reset_trace_distance':dist,'risk':risk,'jump_rate':rate,'post_mean_photons':float(nn+abs(mu)**2),
            'thermal_geometric_tail':float((nth/(1+nth))**cutoff),
            'post_state_top_four_mass':float(diag[-4:].sum()),'gaussian_top_four_mass':float(gd[-4:].sum()),
            'threshold_errors':probs}


def two_mode(s,multiplier,cutoff):
    a=np.diag(np.sqrt(np.arange(1,cutoff)),1).astype(complex)
    ad=a.conj().T
    sq=expm(s*(a@a-ad@ad)/2)
    alpha=1j*multiplier*np.sinh(s)
    first=expm(alpha*ad-alpha.conjugate()*a)@sq[:,0]
    state=np.kron(first,sq[:,0])
    a1=kron(csr_matrix(a),speye(cutoff),format='csr')
    a2=kron(speye(cutoff),csr_matrix(a),format='csr')
    phase=np.pi/2
    gen=np.pi/4*(np.exp(-1j*phase)*(a1.conj().T@a2)-np.exp(1j*phase)*(a2.conj().T@a1))
    before=expm_multiply(gen,state)
    mean1=np.vdot(before,a1@before)
    n1=float(np.vdot(before,a1.conj().T@a1@before).real)
    risk=float((n1-abs(mean1)**2)/n1)
    after=a1@before
    after/=np.linalg.norm(after)
    mean=np.vdot(after,a2@after)
    nn=float(np.vdot(after,a2.conj().T@a2@after).real)-abs(mean)**2
    mm=np.vdot(after,a2@a2@after)-mean**2
    v=np.array([[nn+0.5+mm.real,mm.imag],[mm.imag,nn+0.5-mm.real]])
    d=np.sqrt(2)*np.array([mean.real,mean.imag])
    pnumber=(abs(after.reshape(cutoff,cutoff))**2).sum(axis=0)
    errors=[]
    for eta in (0.1,0.5,1.0):
        q=eta*v+(1-eta)*np.eye(2)/2+np.eye(2)/2
        gd=np.sqrt(eta)*d
        gauss_no=float(np.exp(-0.5*gd@np.linalg.solve(q,gd))/np.sqrt(np.linalg.det(q)))
        exact_no=float(pnumber@((1-eta)**np.arange(cutoff)))
        errors.append({'remaining_transmission':eta,'exact_other_mode_click':1-exact_no,
                       'gaussian_reset_other_mode_click':1-gauss_no,'absolute_error':abs(exact_no-gauss_no)})
    return {'s':s,'displacement_multiplier':multiplier,'cutoff':cutoff,'risk':risk,
            'top_four_other_mode_mass':float(pnumber[-4:].sum()),'errors':errors}


def run():
    rows=[]
    for s in (0.05,0.12,0.25):
        for multiplier in (0,0.5,1,2,4,8):
            alpha=1j*multiplier*np.sinh(s)
            row=conditional(s,alpha,48)
            check=conditional(s,alpha,72)
            row['cutoff48_72_trace_distance_difference']=abs(row['reset_trace_distance']-check['reset_trace_distance'])
            assert row['cutoff48_72_trace_distance_difference']<2e-8
            if multiplier==0:
                assert abs(row['reset_trace_distance']-0.75)<1e-9
            rows.append(row)
    ensemble=[]
    for eta in (0.3,0.5):
        r=0.8
        aa=1-eta+eta*np.exp(-2*r)
        bb=1-eta+eta*np.exp(2*r)
        s=-np.log(aa)/2
        wp=(bb-1/aa)/2
        sigma=np.sqrt(wp/2)
        core=np.sinh(s)**2
        def integrand(z):
            point=conditional(s,1j*sigma*z,64)
            return 2*np.exp(-z*z/2)/np.sqrt(2*np.pi)*(core+sigma*sigma*z*z)/(core+sigma*sigma)*point['reset_trace_distance']
        total,total_error=quad(integrand,0,8,epsabs=2e-8,limit=100)
        for threshold in (0.1,0.2,0.4):
            zcut=np.sqrt(core*(1-threshold)/threshold)/sigma
            normal_mass=2*ndtr(zcut)-1
            second_mass=normal_mass-2*zcut*np.exp(-zcut*zcut/2)/np.sqrt(2*np.pi)
            fraction=float((core*normal_mass+sigma*sigma*second_mass)/(core+sigma*sigma))
            remaining,remaining_error=quad(integrand,zcut,8,epsabs=2e-8,limit=100)
            ensemble.append({'r':r,'eta':eta,'integration':'adaptive quadrature of even normal integrand, |z|<=8; retained fraction analytic','risk_threshold':threshold,
                             'fraction_initial_detections_retained':fraction,
                             'rate_weighted_local_error_all_resets':total,
                             'rate_weighted_local_error_after_exact_retention':remaining,
                             'fraction_local_error_removed':1-remaining/total,
                             'quadrature_reported_error':float(total_error+remaining_error),
                             'scope':'initial displacement ensemble, jump-rate weighted; not full trajectories or global TVD'})
    two_rows=[]
    for s in (0.12,0.25):
        for multiplier in (0,0.5,1,2,4):
            row=two_mode(s,multiplier,24)
            check=two_mode(s,multiplier,32)
            delta=max(abs(a['absolute_error']-b['absolute_error']) for a,b in zip(row['errors'],check['errors']))
            assert delta<2e-7
            row['cutoff24_32_max_error_difference']=delta
            two_rows.append(row)
    result={'status':'local mechanism evidence only; Gaussian moments retained; no integrated hybrid sampler',
            'rows':rows,'initial_ensemble':ensemble,
            'two_mode_conditional_threshold':two_rows,
            'limits':['finite cutoff agreement is numerical evidence, not a rigorous infinite-dimensional bound',
                      'trace distance is a local upper bound on subsequent measurement error, not its equality',
                      'the trigger is a heuristic, not a proven multimode error estimator',
                      'branch growth and no-click evolution require implementation and a global analysis']}
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/'reset_risk.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps({'ensemble':ensemble,'max_cutoff_difference':max(row['cutoff48_72_trace_distance_difference'] for row in rows)},indent=2))


if __name__=='__main__':
    with threadpool_limits(1):
        run()
