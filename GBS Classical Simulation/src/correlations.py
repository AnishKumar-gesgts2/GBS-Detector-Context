"""Walsh transforms and connected-correlation reference diagnostics."""
import numpy as np

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
