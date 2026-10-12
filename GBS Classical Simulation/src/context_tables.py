"""Exact local threshold tables and small-system information diagnostics.
Global reference enumeration is separate from ancestral record generation.
"""
import numpy as np

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
