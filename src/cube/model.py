from dataclasses import dataclass
from typing import List, Sequence
import numpy as np

EDGE_COUNT, CORNER_COUNT = 12, 8

# Indexing convention (internal):
# Corners: 0 UFR, 1 URB, 2 UBL, 3 ULF, 4 DFR, 5 DRB, 6 DBL, 7 DLF
# Edges:   0 UF,  1 UR,  2 UB,  3 UL,  4 FR,  5 RB,  6 BL,  7 LF,
#          8 DF,  9 DR, 10 DB, 11 DL

@dataclass
class CubeState:
    edges_perm: np.ndarray  # (12,) values 0..11
    edges_flip: np.ndarray  # (12,) values 0/1
    corners_perm: np.ndarray  # (8,) values 0..7
    corners_twist: np.ndarray # (8,) values 0/1/2

    @staticmethod
    def solved():
        return CubeState(
            edges_perm=np.arange(EDGE_COUNT, dtype=np.int8),
            edges_flip=np.zeros(EDGE_COUNT, dtype=np.int8),
            corners_perm=np.arange(CORNER_COUNT, dtype=np.int8),
            corners_twist=np.zeros(CORNER_COUNT, dtype=np.int8),
        )

    def copy(self):
        return CubeState(
            self.edges_perm.copy(),
            self.edges_flip.copy(),
            self.corners_perm.copy(),
            self.corners_twist.copy(),
        )

    def is_solved(self) -> bool:
        return (
            np.all(self.edges_perm == np.arange(EDGE_COUNT))
            and np.all(self.edges_flip == 0)
            and np.all(self.corners_perm == np.arange(CORNER_COUNT))
            and np.all(self.corners_twist == 0)
        )

# ----- helpers -----

def _cycle_in_place(arr: np.ndarray, indices: List[int]):
    if len(indices) < 2:
        return
    first = arr[indices[-1]]
    for i in reversed(range(1, len(indices))):
        arr[indices[i]] = arr[indices[i-1]]
    arr[indices[0]] = first

# Face cycles (clockwise turns) using the above indexing
_U_CORNERS = [0, 1, 2, 3]
_U_EDGES   = [0, 1, 2, 3]

_D_CORNERS = [4, 5, 6, 7]
_D_EDGES   = [8, 9,10,11]

_R_CORNERS = [0, 1, 5, 4]
_R_EDGES   = [1, 5, 9, 4]

_L_CORNERS = [2, 3, 7, 6]
_L_EDGES   = [3, 7,11, 6]

_F_CORNERS = [3, 0, 4, 7]
_F_EDGES   = [0, 4, 8, 7]

_B_CORNERS = [1, 2, 6, 5]
_B_EDGES   = [2, 5,10, 6]

_FACE_TO_CYCLES = {
    'U': (_U_CORNERS, _U_EDGES),
    'D': (_D_CORNERS, _D_EDGES),
    'R': (_R_CORNERS, _R_EDGES),
    'L': (_L_CORNERS, _L_EDGES),
    'F': (_F_CORNERS, _F_EDGES),
    'B': (_B_CORNERS, _B_EDGES),
}

# Orientation effects: EO flips occur on F/B quarter-turns; CO twists omitted for Phase 1.
_EDGE_FLIP_ON_FACE = {
    'U': [], 'D': [], 'R': [], 'L': [], 'F': _F_EDGES, 'B': _B_EDGES
}

def apply_move(state: CubeState, move: str) -> CubeState:
    """Apply a face move to a copy of state.
    Supports all faces with suffixes: '', "'", '2'.
    Orientation: applies EO flips on F/B; corner twists are deferred to Phase 2.
    """
    face = move[0]
    if face not in _FACE_TO_CYCLES:
        raise NotImplementedError(f"Move for face {face} not implemented yet")
    turns = 1
    if len(move) > 1:
        if move[1] == '2':
            turns = 2
        elif move[1] == "'":
            turns = 3  # three clockwise turns = one counterclockwise
        else:
            raise ValueError(f"Bad move suffix in {move}")

    st = state.copy()
    for _ in range(turns):
        ccyc, ecyc = _FACE_TO_CYCLES[face]
        _cycle_in_place(st.corners_perm, ccyc)
        _cycle_in_place(st.edges_perm, ecyc)
        # Edge orientation flips for F/B only
        for e in _EDGE_FLIP_ON_FACE.get(face, []):
            st.edges_flip[e] ^= 1
        # Corner twists would go here (Phase 2+)
    return st

def apply_sequence(state: CubeState, seq: Sequence[str]) -> CubeState:
    st = state
    for mv in seq:
        st = apply_move(st, mv)
    return st

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args()
    if args.selftest:
        s = CubeState.solved()
        # Basic inverses for all faces
        for f in ['U','D','L','R','F','B']:
            a = apply_move(s, f)
            b = apply_move(a, f+"'")
            assert b.is_solved(), f"{f} followed by {f}' should solve"
            s4 = s
            for _ in range(4):
                s4 = apply_move(s4, f)
            assert s4.edges_perm.tolist() == list(range(EDGE_COUNT))
            assert s4.corners_perm.tolist() == list(range(CORNER_COUNT))
        print("[selftest] OK")
