import random, numpy as np
from qiskit_aer import AerSimulator
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from src.cube.model import CubeState, apply_sequence
from src.quantum_oracles.encoding import QubitLayout
from src.quantum_oracles.move_circuits import apply_moves_eo_effect
from src.quantum_oracles.eo_oracle import build_eo_zero_oracle

ALPHABET = ['U','R','F',"U'","R'","F'"]

def classical_eo_after_sequence(eo_bits, seq_moves):
    # quarter-turn F/F' flip EO for F-edge indices only; others unaffected (EO)
    F_IDX = [0,4,8,7]
    out = eo_bits.copy()
    for mv in seq_moves:
        if mv[0]=='F' and (len(mv)==1 or mv[1]=="'"):
            for e in F_IDX:
                out[e] ^= 1
    return out

def sample_random_seq(rng, d):
    return [rng.choice(ALPHABET) for _ in range(d)]

def test_apply_moves_eo_matches_classical():
    rng = random.Random(123)
    layout = QubitLayout(d=5, k=len(ALPHABET))
    for _ in range(5):
        # random EO scramble with even parity (enforce parity by last bit)
        eo = [rng.randint(0,1) for _ in range(layout.eo_bits)]
        eo[-1] = (sum(eo[:-1]) % 2 == 0) and eo[-1] or (eo[-1]^1)

        # random sequence
        seq_moves = sample_random_seq(rng, layout.d)

        # Quantum: apply and measure EO
        seq = QuantumRegister(layout.seq_bits, 'seq')
        qeo = QuantumRegister(layout.eo_bits, 'eo')
        cre = ClassicalRegister(layout.eo_bits, 'ceo')
        qc = QuantumCircuit(seq, qeo, cre)

        # encode sequence basis state: just pick the exact symbol values (deterministic test)
        # Using 3 bits per symbol, little-endian in each 3-bit chunk
        sym_map = {mv:i for i,mv in enumerate(ALPHABET)}
        for i, mv in enumerate(seq_moves):
            v = sym_map[mv]
            for j in range(layout.seq_bits_per_symbol):
                if (v >> j) & 1:
                    qc.x(seq[layout.symbol_bits_slice(i)][j])

        # init EO
        for i, b in enumerate(eo):
            if b % 2 == 1:
                qc.x(qeo[i])

        apply_moves_eo_effect(qc, layout, seq, qeo, ALPHABET)
        qc.measure(qeo, cre)
        res = AerSimulator().run(qc, shots=1).result().get_counts()
        measured = [0]*layout.eo_bits
        for bitstr, _ in res.items():
            # bitstr is eo bits little-endian per qiskit output; reverse
            bitstr = bitstr.replace(' ', '')
            bits = list(map(int, bitstr[::-1]))
            measured = bits
        expected = classical_eo_after_sequence(eo[:], seq_moves)
        assert measured == expected

def test_oracle_marks_zero():
    rng = random.Random(7)
    layout = QubitLayout(d=4, k=len(ALPHABET))
    seq = QuantumRegister(layout.seq_bits, 'seq')
    eo  = QuantumRegister(layout.eo_bits, 'eo')
    anc = QuantumRegister(1, 'anc')
    c   = ClassicalRegister(1, 'c')
    qc = QuantumCircuit(seq, eo, anc, c)

    # Pick sequence that flips EO exactly back to zero: choose even number of F/F'
    # We'll brute-force over small space to find one quickly
    sym_map = {i:mv for i,mv in enumerate(ALPHABET)}
    target_seq_vals = [0,0,2,2]  # e.g., ['U','U','F','F'] -> F twice cancels EO
    # encode seq values
    for i, v in enumerate(target_seq_vals):
        for j in range(layout.seq_bits_per_symbol):
            if (v >> j) & 1:
                qc.x(seq[layout.symbol_bits_slice(i)][j])

    # scramble EO to something with ones at F edge indices
    F_IDX = [0,4,8,7]
    for e in F_IDX:
        qc.x(eo[e])

    # put anc in |-> so a phase flip becomes a bit flip after H
    # qc.x(anc)
    # qc.h(anc)

    oracle = build_eo_zero_oracle(layout, ALPHABET)
    qc.compose(oracle, qubits=[*seq, *eo, *anc], inplace=True)
    # qc.h(anc)
    # qc.x(anc)
    qc.measure(anc, c)

    res = AerSimulator().run(qc, shots=1).result().get_counts()
    # Expect anc to be '1' (marked) because EO returns to zero after two F's
    assert '1' in res
