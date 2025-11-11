import numpy as np, itertools
from src.cube.model import CubeState, apply_move, apply_sequence

MOVES = ['U','D','L','R','F','B']

def invert_move(m: str) -> str:
    if m.endswith('2'): return m
    return m[0] if m.endswith("'") else m+"'"

def inverse_sequence(seq):
    return [invert_move(m) for m in reversed(seq)]

def test_face_and_inverse_all():
    s0 = CubeState.solved()
    for f in MOVES:
        s = apply_move(s0, f)
        s = apply_move(s, f+"'")
        assert s.is_solved()

def test_double_equals_twice_all():
    s0 = CubeState.solved()
    for f in MOVES:
        a = apply_move(apply_move(s0, f), f)
        b = apply_move(s0, f+'2')
        assert np.array_equal(a.edges_perm, b.edges_perm)
        assert np.array_equal(a.corners_perm, b.corners_perm)

def test_random_scramble_then_inverse_all_faces():
    s = CubeState.solved()
    seq = ['U', 'R', 'F', "L'", 'D2', 'B', 'U2', "R'", 'F2', 'B2', 'L', 'D']
    inv = inverse_sequence(seq)
    s = apply_sequence(s, seq)
    s = apply_sequence(s, inv)
    assert s.is_solved()
