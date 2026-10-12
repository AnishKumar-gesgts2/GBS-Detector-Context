"""Bounded-context threshold sampling diagnostic, not a novelty or speed claim.

Sampler tables use only exact small Gaussian marginals. Full distributions
are constructed separately for scoring. Parents use fixed ordering or pair MI,
not full-distribution error. KL measures omitted conditional information.
"""
import os
for key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[key] = '1'
import hashlib
import json
import time
from pathlib import Path
import numpy as np
from gbs_algorithm_screen import distribution, isometry, symplectic, tor_reference

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'outputs' / 'bounded_context_screen_v1'
SEED = 2026101127


def subset_distribution(v, sites):
    m = len(v)//2
    ids = list(sites) + [j+m for j in sites]
    sub = v[np.ix_(ids, ids)]
    n = len(sites)
    vacuum = np.ones(1 << n)
    for mask in range(1, 1 << n):
        selected = [j for j in range(n) if mask >> j & 1]
        selected_ids = selected + [j+n for j in selected]
        matrix = sub[np.ix_(selected_ids, selected_ids)] + np.eye(len(selected_ids))/2
        sign, logdet = np.linalg.slogdet(matrix)
        assert sign > 0
        vacuum[mask] = np.exp(-logdet/2)
    p = vacuum[::-1].copy()
    for j in range(n):
        blocks = p.reshape(-1, 2*(1 << j))
        blocks[:, 1 << j:] -= blocks[:, :1 << j]
    # Fail rather than silently clip a negative local probability.
    assert p.min() >= 0 and abs(p.sum()-1) < 1e-10
    return p


def pair_information(v):
    m = len(v)//2
    scores = np.zeros((m, m))
    for i in range(m):
        for j in range(i):
            p = subset_distribution(v, [j, i]).reshape(2, 2)
            reference = p.sum(axis=1)[:, None] * p.sum(axis=0)[None, :]
            mask = p > 0
            scores[i, j] = scores[j, i] = np.sum(p[mask]*np.log(p[mask]/reference[mask]))
    return scores


def prepare(v, width, strategy, scores):
    m = len(v)//2
    tables = []
    for i in range(m):
        parents = (list(range(max(0, i-width), i)) if strategy == 'recent'
                   else sorted(sorted(range(i), key=lambda j: (-scores[i, j], j))[:width]))
        local = subset_distribution(v, parents+[i]).reshape(2, -1)
        denominator = local.sum(axis=0)
        assert local.min() >= 0 and abs(local.sum()-1) < 1e-10
        p_zero = np.divide(local[0], denominator, out=np.ones_like(denominator), where=denominator > 0)
        assert np.isfinite(p_zero).all() and p_zero.min() >= 0 and p_zero.max() <= 1
        tables.append((parents, p_zero))
    return tables


def generate(tables, shots, rng):
    """Generate records using local tables only, with no global distribution."""
    records = np.zeros((shots, len(tables)), dtype=np.uint8)
    for i, (parents, p_zero) in enumerate(tables):
        context = np.zeros(shots, dtype=np.int64)
        for k, j in enumerate(parents):
            context |= records[:, j].astype(np.int64) << k
        records[:, i] = rng.random(shots) >= p_zero[context]
    return records


def induced_distribution(tables):
    """Reference-side enumeration for scoring; never used to generate records."""
    patterns = np.arange(1 << len(tables))
    q = np.ones(len(patterns))
    for i, (parents, p_zero) in enumerate(tables):
        context = np.zeros(len(patterns), dtype=np.int64)
        for k, j in enumerate(parents):
            context |= ((patterns >> j) & 1) << k
        probability = p_zero[context]
        q *= np.where((patterns >> i) & 1, 1-probability, probability)
    assert q.min() >= 0 and abs(q.sum()-1) < 1e-10
    return q


def marginal(p, m, sites):
    patterns = np.arange(1 << m)
    indices = np.zeros(len(patterns), dtype=np.int64)
    for k, j in enumerate(sites):
        indices |= ((patterns >> j) & 1) << k
    return np.bincount(indices, weights=p, minlength=1 << len(sites))


def entropy(p):
    nonzero = p[p > 0]
    return float(-np.sum(nonzero*np.log(nonzero)))


def omitted_information(p, tables):
    m = len(tables)
    total = 0.0
    for i, (parents, _) in enumerate(tables):
        # H(X_i|selected past) - H(X_i|entire past).
        selected_h = entropy(marginal(p, m, parents+[i])) - entropy(marginal(p, m, parents))
        full_h = entropy(marginal(p, m, list(range(i+1)))) - entropy(marginal(p, m, list(range(i))))
        assert selected_h-full_h > -1e-10
        total += selected_h-full_h
    return float(max(total, 0))


def run():
    rows = []
    start = time.perf_counter()
    for m in (6, 8, 10):
        for profile in ('heterogeneous', 'flat', 'bright_flat'):
            r = (np.r_[0.8, 0.65, np.linspace(0.04, 0.12, m-2)] if profile == 'heterogeneous'
                 else np.full(m, 1.0 if profile == 'bright_flat' else 0.7))
            for eta in (0.3, 0.5):
                for rep in range(2):
                    seed = SEED+m*10000+('heterogeneous', 'flat', 'bright_flat').index(profile)*1000+int(eta*100)*10+rep
                    o = symplectic(isometry(m, m, np.random.default_rng(seed)))
                    cov = eta*(o @ np.diag(np.r_[np.exp(-2*r), np.exp(2*r)]/2) @ o.T)+(1-eta)*np.eye(2*m)/2
                    truth = distribution(cov)
                    if m == 6:
                        assert abs(truth-tor_reference(cov)).max() < 1e-9
                    score_start = time.perf_counter()
                    scores = pair_information(cov)
                    score_seconds = time.perf_counter()-score_start
                    # Full-context limit validates the complete chain and bit ordering.
                    full = prepare(cov, m-1, 'recent', scores)
                    assert abs(induced_distribution(full)-truth).max() < 1e-10
                    for strategy in ('recent', 'pair_mi'):
                        for width in (0, 1, 2, 3, 4):
                            table_start = time.perf_counter()
                            tables = prepare(cov, width, strategy, scores)
                            table_seconds = time.perf_counter()-table_start
                            q = induced_distribution(tables)
                            nonzero = truth > 0
                            assert (q[nonzero] > 0).all()
                            kl = float(np.sum(truth[nonzero]*np.log(truth[nonzero]/q[nonzero])))
                            info = omitted_information(truth, tables)
                            assert abs(kl-info) < 1e-9
                            tvd = float(abs(truth-q).sum()/2)
                            bound = min(1.0, float(np.sqrt(max(kl, 0)/2)))
                            assert tvd <= bound+1e-9
                            gen_start = time.perf_counter()
                            records = generate(tables, 10000, np.random.default_rng(seed+width))
                            gen_seconds = time.perf_counter()-gen_start
                            assert records.shape == (10000, m)
                            rows.append({'m': m, 'profile': profile, 'r': r.tolist(), 'eta': eta,
                                         'rep': rep, 'seed': seed, 'strategy': strategy, 'context_width': width,
                                         'full_tvd': tvd, 'kl_nats': kl, 'omitted_cmi_sum_nats': info,
                                         'pinsker_bound': bound,
                                         'parent_selection_seconds': score_seconds if strategy == 'pair_mi' else 0,
                                         'table_setup_seconds': table_seconds,
                                         'local_probability_entries': sum(len(x[1]) for x in tables),
                                         'probability_table_bytes': sum(x[1].nbytes for x in tables),
                                         'sample_seconds_10000_vectorized': gen_seconds,
                                         'parents': [x[0] for x in tables]})
    vacuum = np.eye(12)/2
    vt = prepare(vacuum, 3, 'recent', np.zeros((6, 6)))
    assert not generate(vt, 10000, np.random.default_rng(SEED)).any()
    assert induced_distribution(vt)[0] == 1
    report = {'date': '2026-10-11', 'scope': 'exploratory bounded-context mechanism screen, no published-baseline or novelty claim',
              'convention': 'hbar=1, q-all then p-all, bit i denotes detector i, log in nats',
              'selection': 'fixed recent context or largest pair mutual information among earlier modes; no full-TVD selection',
              'timing_scope': 'illustrative table and vectorized sampling timings; no competitive speed claim; exact scoring excluded',
              'limit': 'full-distribution-derived CMI used only for evaluation, not a scalable certificate',
              'numpy': np.__version__, 'seed': SEED, 'rows': rows,
              'elapsed_seconds': time.perf_counter()-start,
              'script_sha256_lf': hashlib.sha256(Path(__file__).read_text(encoding='utf-8').replace('\r\n', '\n').encode()).hexdigest()}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT/'probe.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    summary = {}
    for profile in ('heterogeneous', 'flat', 'bright_flat'):
        cells = [x for x in rows if x['profile'] == profile and x['strategy'] == 'pair_mi']
        summary[profile] = {str(w): {'median_tvd': float(np.median([x['full_tvd'] for x in cells if x['context_width'] == w])),
                                   'min_tvd': min(x['full_tvd'] for x in cells if x['context_width'] == w),
                                   'max_tvd': max(x['full_tvd'] for x in cells if x['context_width'] == w)} for w in (0, 2, 4)}
    print(json.dumps({'circuits': 36, 'comparisons': len(rows), 'seconds': report['elapsed_seconds'], 'summary': summary}))


if __name__ == '__main__':
    run()
