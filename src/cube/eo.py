import numpy as np
from .model import CubeState, EDGE_COUNT

def encode_eo(state: CubeState) -> np.ndarray:
    return state.edges_flip.astype(np.uint8)

def decode_eo(bits: np.ndarray, state: CubeState) -> None:
    assert bits.shape == (EDGE_COUNT,)
    state.edges_flip[:] = bits % 2
    # (Optional) parity assert: reachable states satisfy even parity
    # assert int(np.sum(state.edges_flip)) % 2 == 0
