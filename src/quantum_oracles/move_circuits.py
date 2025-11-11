from typing import List, Dict
from qiskit import QuantumCircuit, QuantumRegister
from .encoding import QubitLayout

# EO flips for F/B quarter turns in our cube indexing (see model.py)
F_EDGE_IDX = [0, 4, 8, 7]
B_EDGE_IDX = [2, 5,10, 6]

def _controls_for_value(circ: QuantumCircuit, bits, value: int):
    # Return list of bit qubits after applying X to match the pattern (value)
    # Caller must undo the X after controlled op.
    pat = []
    for j, qb in enumerate(bits):
        want = (value >> j) & 1
        if want == 0:
            circ.x(qb)
        pat.append(qb)
    return pat

def _undo_controls_for_value(circ: QuantumCircuit, bits, value: int):
    for j, qb in enumerate(bits):
        want = (value >> j) & 1
        if want == 0:
            circ.x(qb)

def apply_moves_eo_effect(
    circ: QuantumCircuit,
    layout: QubitLayout,
    seq: QuantumRegister,
    eo: QuantumRegister,
    alphabet: List[str],
):
    """Apply only the EO *flip* effects of each symbol in the sequence register.
    This ignores permutations (unnecessary for EO oracle).
    """
    assert len(alphabet) <= (1 << layout.seq_bits_per_symbol)
    for i in range(layout.d):
        sl = layout.symbol_bits_slice(i)
        sym_bits = seq[sl]
        for val, mv in enumerate(alphabet):
            # For F/F' flip EO of the four F edges; U/R (and inverses) do nothing.
            flip_edges = []
            if mv[0] == 'F' and (len(mv) == 1 or mv[1] == "'"):
                flip_edges = F_EDGE_IDX
            elif mv[0] == 'B' and (len(mv) == 1 or mv[1] == "'"):
                flip_edges = B_EDGE_IDX

            if not flip_edges:
                continue

            ctrls = _controls_for_value(circ, sym_bits, val)
            for e in flip_edges:
                circ.mcx(ctrls, eo[e])
            _undo_controls_for_value(circ, sym_bits, val)
