import random, numpy as np
from src.cube.model import CubeState, apply_sequence
from src.cube.eo import encode_eo, decode_eo
from src.cube.co import encode_co, decode_co

MOVES = ["U","D","L","R","F","B","U'","D'","L'","R'","F'","B'","U2","D2","L2","R2","F2","B2"]

def inverse_move(m: str) -> str:
    if m.endswith("2"): return m
    return m[0] if m.endswith("'") else m + "'"

def inverse_sequence(seq):
    return [inverse_move(m) for m in reversed(seq)]

def test_eo_parity_and_roundtrip():
    rng = random.Random(7)
    for _ in range(50):
        st = CubeState.solved()
        seq = rng.choices(MOVES, k=25)
        st = apply_sequence(st, seq)
        eo = encode_eo(st)
        st2 = CubeState.solved()
        decode_eo(eo, st2)
        assert np.array_equal(eo, st2.edges_flip)
        assert int(np.sum(eo)) % 2 == 0  # reachability parity

def test_co_roundtrip_mod3():
    rng = random.Random(11)
    for _ in range(50):
        st = CubeState.solved()
        seq = rng.choices(MOVES, k=10)
        st = apply_sequence(st, seq)
        co = encode_co(st)
        st2 = CubeState.solved()
        decode_co(co, st2)
        assert np.array_equal(co[:-1] % 3, st2.corners_twist[:-1] % 3)
        assert int(np.sum(st2.corners_twist)) % 3 == 0

def test_scramble_and_exact_inverse_is_solved():
    rng = random.Random(42)
    seq = rng.choices(MOVES, k=30)
    inv = inverse_sequence(seq)
    st = CubeState.solved()
    st = apply_sequence(st, seq)
    st = apply_sequence(st, inv)
    assert st.is_solved()
