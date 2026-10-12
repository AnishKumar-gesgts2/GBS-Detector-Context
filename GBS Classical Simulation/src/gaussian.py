"""Gaussian circuit utilities and small exact references; hbar=1, q-all/p-all.
Full output enumeration is for reference scoring only.
"""
import numpy as np

def isometry(m, n, rng):
    z = rng.normal(size=(m, n)) + 1j*rng.normal(size=(m, n))
    q, r = np.linalg.qr(z)
    return q*(np.diag(r)/abs(np.diag(r)))



def symplectic(u):
    return np.block([[u.real, -u.imag], [u.imag, u.real]])



def distribution(v):
    m = len(v)//2
    vacuum = np.ones(1 << m)
    for mask in range(1, 1 << m):
        sites = [i for i in range(m) if mask >> i & 1]
        ids = sites + [i+m for i in sites]
        sign, ld = np.linalg.slogdet(v[np.ix_(ids, ids)] + np.eye(len(ids))/2)
        assert sign > 0
        vacuum[mask] = np.exp(-ld/2)
    p = vacuum[::-1].copy()
    for j in range(m):
        blocks = p.reshape(-1, 2*(1 << j))
        blocks[:, 1 << j:] -= blocks[:, :1 << j]
    assert p.min() > -2e-10 and abs(p.sum()-1) < 2e-10
    p = np.maximum(p, 0)
    return p/p.sum()



def tor_reference(v):
    """Independent complex-basis inverse/Torontonian reference, no library use."""
    m = len(v)//2
    eye = np.eye(m)
    f = np.block([[eye, 1j*eye], [eye, -1j*eye]])/np.sqrt(2)
    q = f @ (v+np.eye(2*m)/2) @ f.conj().T
    o = np.eye(2*m)-np.linalg.inv(q)
    denom = np.sqrt(np.linalg.det(q)).real
    out = np.zeros(1 << m)
    for c in range(1 << m):
        sub = c
        while True:
            sites = [j for j in range(m) if sub >> j & 1]
            ids = sites + [j+m for j in sites]
            d = np.linalg.det(np.eye(len(ids))-o[np.ix_(ids, ids)])
            out[c] += (-1)**(c.bit_count()-sub.bit_count())/np.sqrt(d).real/denom
            if sub == 0:
                break
            sub = (sub-1) & c
    return out



def tvd(p, q):
    return float(abs(p-q).sum()/2)



def physical_min(v):
    m = len(v)//2
    omega = np.block([[np.zeros((m,m)), np.eye(m)], [-np.eye(m), np.zeros((m,m))]])
    return float(np.linalg.eigvalsh(v+0.5j*omega).min())
