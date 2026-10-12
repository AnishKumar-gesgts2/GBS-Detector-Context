"""Small diagnostics for the four-review synthesis; no new sampler benchmark.

Conditional cumulants use exact six-mode displaced Gaussian distributions.
Signed mass describes the unreduced threshold Gaussian expansion, not a lower
bound on all simulators. No invalid probabilities are clipped into a sampler.
"""
import os
for key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[key] = '1'
import json
import hashlib
import time
from pathlib import Path
import numpy as np
from scipy.special import ndtri
from scipy.stats import qmc
from gbs_algorithm_screen import distribution, tor_reference, isometry, symplectic

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'outputs' / 'review_synthesis_v1'
SEED = 2026101120


def walsh(values):
    out = np.array(values, copy=True)
    size = out.shape[-1]
    width = 1
    while width < size:
        shaped = out.reshape(*out.shape[:-1], -1, 2 * width)
        left = shaped[..., :width].copy()
        right = shaped[..., width:].copy()
        shaped[..., :width] = left + right
        shaped[..., width:] = left - right
        width *= 2
    return out


def cumulants(moments):
    result = np.zeros_like(moments)
    for mask in range(1, moments.shape[-1]):
        anchor = mask & -mask
        result[..., mask] = moments[..., mask]
        block = (mask - 1) & mask
        while block:
            if block & anchor:
                result[..., mask] -= result[..., block] * moments[..., mask ^ block]
            block = (block - 1) & mask
    return result


def vacuum_table(v, means):
    m = len(v) // 2
    out = np.ones((len(means), 1 << m))
    for mask in range(1, 1 << m):
        sites = [i for i in range(m) if mask >> i & 1]
        ids = sites + [i + m for i in sites]
        mat = v[np.ix_(ids, ids)] + np.eye(len(ids)) / 2
        sign, logdet = np.linalg.slogdet(mat)
        assert sign > 0
        selected = means[:, ids]
        expo = np.einsum('bi,ib->b', selected, np.linalg.solve(mat, selected.T))
        out[:, mask] = np.exp(-logdet / 2 - expo / 2)
    return out


def from_vacuum(vacuum):
    out = vacuum[:, ::-1].copy()
    width = 1
    while width < out.shape[-1]:
        blocks = out.reshape(len(out), -1, 2 * width)
        blocks[..., width:] -= blocks[..., :width]
        width *= 2
    assert out.min() > -2e-10
    assert abs(out.sum(axis=1) - 1).max() < 2e-10
    return out


def reconstruct(cums, order):
    moments = np.zeros_like(cums)
    moments[..., 0] = 1
    for mask in range(1, cums.shape[-1]):
        anchor = mask & -mask
        block = mask
        while block:
            if block & anchor and block.bit_count() <= order:
                moments[..., mask] += cums[..., block] * moments[..., mask ^ block]
            block = (block - 1) & mask
    return walsh(moments) / cums.shape[-1]


def signed_mass(p, vacuum):
    m = int(np.log2(len(p)))
    result = []
    for prefix_length in range(1, m + 1):
        prefmask = (1 << prefix_length) - 1
        pp = p.reshape(-1, 1 << prefix_length).sum(axis=0)
        masses = []
        for clicks in range(1 << prefix_length):
            zeros = prefmask ^ clicks
            numerator = 0.0
            subset = clicks
            while True:
                numerator += vacuum[zeros | subset]
                if subset == 0:
                    break
                subset = (subset - 1) & clicks
            masses.append(numerator / pp[clicks])
        masses = np.array(masses)
        indices = np.argsort(masses)
        cumulative = np.cumsum(pp[indices])
        quantiles = [float(masses[indices[min(np.searchsorted(cumulative, q), len(indices)-1)]])
                     for q in (0.5, 0.9, 0.99)]
        result.append({'prefix_modes': prefix_length,
                       'probability_weighted_mean_mass': float(pp @ masses),
                       'weighted_quantiles_50_90_99': quantiles,
                       'maximum_mass': float(masses.max()),
                       'probability_of_mass_above_100': float(pp[masses > 100].sum())})
    return result


def self_checks():
    m = 4
    bits = np.array([[(x >> j) & 1 for j in range(m)] for x in range(1 << m)])
    rates = np.array([0.1, 0.25, 0.4, 0.7])
    p = np.prod(np.where(bits, rates, 1-rates), axis=1)
    c = cumulants(walsh(p))
    assert max(abs(c[i]) for i in range(1 << m) if i.bit_count() > 1) < 1e-12
    assert abs(reconstruct(c, m)-p).max() < 1e-12
    mean = np.array([[0.3, -0.4, 0.2, 0.1, -0.2, 0.1, 0.4, -0.3]])
    pure = np.eye(2*m)/2
    vp = vacuum_table(pure, mean)
    cp = from_vacuum(vp)[0]
    nr = (mean[0, :m]**2 + mean[0, m:]**2)/2
    expected = np.prod(np.where(bits, 1-np.exp(-nr), np.exp(-nr)), axis=1)
    assert abs(cp-expected).max() < 1e-12


def run():
    self_checks()
    start = time.perf_counter()
    rows = []
    m = 6
    orders = np.array([i.bit_count() for i in range(1 << m)])
    for profile in ('heterogeneous', 'flat', 'bright_flat'):
        r = (np.r_[0.8, 0.65, np.linspace(0.04, 0.12, m-2)]
             if profile == 'heterogeneous' else np.full(m, 1.0 if profile == 'bright_flat' else 0.7))
        for eta in (0.3, 0.5):
            a = 1-eta+eta*np.exp(-2*r)
            b = 1-eta+eta*np.exp(2*r)
            pure_diag = np.r_[a, 1/a]/2
            noise_p = (b-1/a)/2
            for circuit_rep in range(2):
                seed = SEED + circuit_rep + int(eta*100)*10 + ('heterogeneous', 'flat', 'bright_flat').index(profile)*1000
                o = symplectic(isometry(m, m, np.random.default_rng(seed)))
                v = o @ np.diag(np.r_[a, b]/2) @ o.T
                core = o @ np.diag(pure_diag) @ o.T
                target = distribution(v)
                assert abs(target-tor_reference(v)).max() < 1e-9
                unconditional = cumulants(walsh(target))
                assert abs(reconstruct(unconditional, m)-target).max() < 1e-10
                vacuum = vacuum_table(v, np.zeros((1, 2*m)))[0]
                replicates = []
                for integration_rep in range(4):
                    power = 11 if integration_rep < 2 else 14
                    z = ndtri(qmc.Sobol(m, scramble=True, seed=seed+10000+integration_rep%2).random_base2(power))
                    means = (z*np.sqrt(noise_p)) @ o[:, m:].T
                    pd = from_vacuum(vacuum_table(core, means))
                    cd = cumulants(walsh(pd))
                    assert abs(reconstruct(cd, m)-pd).max() < 1e-10
                    mixture_error = float(abs(pd.mean(axis=0)-target).sum()/2)
                    assert mixture_error < 0.005
                    per_order = []
                    for k in range(2, m+1):
                        mask = orders == k
                        un = float(abs(unconditional[mask]).sum())
                        co = float(abs(cd[:, mask]).sum(axis=1).mean())
                        per_order.append({'order': k, 'unconditional_sum_absolute': un,
                                          'mean_conditional_sum_absolute': co, 'ratio': co/un})
                    truncations = []
                    for k in (2, 3, 4):
                        raw_un = reconstruct(unconditional, k)
                        raw_co = reconstruct(cd, k)
                        truncations.append({'order': k,
                            'unconditional_raw_half_l1_error': float(abs(raw_un-target).sum()/2),
                            'unconditional_negative_mass': float(-raw_un[raw_un < 0].sum()),
                            'conditional_mixture_raw_half_l1_error': float(abs(raw_co.mean(axis=0)-target).sum()/2),
                            'conditional_mean_negative_mass': float(np.maximum(-raw_co, 0).sum(axis=1).mean()),
                            'conditional_fraction_invalid_below_minus_1e_minus_10': float((raw_co.min(axis=1) < -1e-10).mean())})
                    replicates.append({'integration_rep': integration_rep, 'points': len(z),
                                       'exact_conditional_mixture_tvd_integration_error': mixture_error,
                                       'per_order': per_order, 'truncations': truncations})
                rows.append({'m': m, 'eta': eta, 'profile': profile, 'r': r.tolist(), 'seed': seed,
                             'replicates': replicates, 'signed_mass_by_prefix': signed_mass(target, vacuum)})
    report = {'date': '2026-10-11', 'seed': SEED, 'hbar': 1,
              'scope': 'exploratory exact-small-distribution mechanism diagnostics; not Dodd implementation, not a complete sampler or end-to-end timing comparison',
              'warning': 'raw cumulant truncations can be signed; half-L1 is not TVD of a valid sampler when negative; no clipping applied',
              'integration': 'two independent scrambled Sobol replicates at 2048 and 16384 latent displacements per circuit; point counts share nested sequences',
              'signed_mass_scope': 'unreduced normalized threshold Gaussian expansion; not a representation-independent complexity lower bound',
              'numpy_version': np.__version__, 'elapsed_seconds': time.perf_counter()-start,
              'rows': rows,
              'script_sha256_lf': hashlib.sha256(Path(__file__).read_text(encoding='utf-8').replace('\r\n', '\n').encode()).hexdigest()}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'mechanism_probe.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    ratios = [rep['per_order'][k-2]['ratio'] for row in rows for rep in row['replicates'] for k in (3, 4, 5)]
    print(json.dumps({'circuits': len(rows), 'seconds': report['elapsed_seconds'],
                      'conditional_order3to5_ratio_min_median_max': [min(ratios), float(np.median(ratios)), max(ratios)],
                      'largest_exact_mixture_integration_tvd': max(rep['exact_conditional_mixture_tvd_integration_error'] for row in rows for rep in row['replicates'])}))


if __name__ == '__main__':
    run()
