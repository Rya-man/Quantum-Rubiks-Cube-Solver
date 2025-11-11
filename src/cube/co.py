import numpy as np
from .model import CubeState, CORNER_COUNT

def encode_co(state: CubeState) -> np.ndarray:
    return state.corners_twist.astype(np.int8)

def decode_co(trits: np.ndarray, state: CubeState) -> None:
    assert trits.shape == (CORNER_COUNT,)
    tr = (trits % 3).astype(np.int8)
    # Enforce mod-3 constraint by adjusting the last entry
    s = int(np.sum(tr[:-1])) % 3
    tr[-1] = (-s) % 3
    state.corners_twist[:] = tr
