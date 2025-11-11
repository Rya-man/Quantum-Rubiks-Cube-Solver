from typing import List
from qiskit import QuantumCircuit, QuantumRegister
from qiskit.circuit.library import MCXGate
from .encoding import QubitLayout
from .move_circuits import apply_moves_eo_effect

def build_eo_zero_oracle(layout: QubitLayout, alphabet: List[str]) -> QuantumCircuit:
    """Return a *gate-like* circuit that expects [seq|eo|anc] registers.
    It phase-flips |anc> iff EO becomes all-zero after applying the sequence EO effects.
    """
    seq = QuantumRegister(layout.seq_bits, 'seq')
    eo  = QuantumRegister(layout.eo_bits, 'eo')
    anc = QuantumRegister(1, 'anc')
    qc = QuantumCircuit(seq, eo, anc, name='U_f')

    # Apply EO effects of sequence
    apply_moves_eo_effect(qc, layout, seq, eo, alphabet)

    # Check EO==0 via multi-controlled X on anc with inverted controls (X-...-X sandwich)
    for q in eo:
        qc.x(q)
    qc.append(MCXGate(layout.eo_bits), [*eo, anc[0]])
    for q in eo:
        qc.x(q)

    # Uncompute EO effects
    apply_moves_eo_effect(qc, layout, seq, eo, alphabet)

    # Convert to a gate for easy reuse if needed
    return qc
