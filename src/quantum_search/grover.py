import math
from typing import List, Dict
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit_aer import AerSimulator
from qiskit.circuit.library import MCXGate
from ..quantum_oracles.encoding import QubitLayout
from ..quantum_oracles.eo_oracle import build_eo_zero_oracle

def diffuser_on(circ: QuantumCircuit, reg):
    circ.h(reg); circ.x(reg)
    # multi-controlled Z implemented via H on last then MCX
    last = reg[-1]
    circ.h(last)
    circ.mcx(list(reg[:-1]), last)
    circ.h(last)
    circ.x(reg); circ.h(reg)

def run_grover_eo(layout: QubitLayout, alphabet: List[str], eo_bits_init: List[int], iters: int, shots: int=2048):
    seq = QuantumRegister(layout.seq_bits, 'seq')
    eo  = QuantumRegister(layout.eo_bits, 'eo')
    anc = QuantumRegister(1, 'anc')
    creg = ClassicalRegister(layout.seq_bits, 'cseq')
    qc = QuantumCircuit(seq, eo, anc, creg)

    # init sequence register in uniform superposition
    qc.h(seq)

    # set EO scramble bits
    for i, b in enumerate(eo_bits_init):
        if b % 2 == 1:
            qc.x(eo[i])

    # anc in |-> for phase kickback
    qc.h(anc)

    oracle = build_eo_zero_oracle(layout, alphabet)

    for _ in range(iters):
        qc.compose(oracle, qubits=[*seq, *eo, *anc], inplace=True)
        diffuser_on(qc, seq)

    # measure sequence only
    qc.measure(seq, creg)

    sim = AerSimulator()
    res = sim.run(qc, shots=shots).result().get_counts()
    return res, qc
