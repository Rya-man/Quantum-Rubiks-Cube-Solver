from collections import Counter
import math, random
from src.quantum_oracles.encoding import QubitLayout
from src.quantum_search.grover import run_grover_eo

# ALPHABET = ['U','R','F',"U'","R'","F'"]
ALPHABET = ['U','F',"U'","F'"]

def find_solutions_bruteforce(d, eo_init):
    # A small brute-force over the limited alphabet for tiny d
    sols = []
    moves = ALPHABET
    sym_map = {i:m for i,m in enumerate(moves)}
    idxs = list(range(len(moves)))

    def classical_eo_after(vals):
        F_IDX = [0,4,8,7]
        out = eo_init[:]
        for v in vals:
            mv = sym_map[v]
            if mv[0]=='F' and (len(mv)==1 or mv[1]=="'"):
                for e in F_IDX:
                    out[e] ^= 1
        return out

    def dfs(vals, depth):
        if depth == d:
            if sum(classical_eo_after(vals)) == 0:
                sols.append(tuple(vals))
            return
        for v in idxs:
            vals.append(v); dfs(vals, depth+1); vals.pop()

    dfs([], 0)
    return set(sols)

def test_grover_amplifies_solution_mode():
    rng = random.Random(99)
    layout = QubitLayout(d=3, k=len(ALPHABET),seq_bits_per_symbol=2)
    # init EO with ones on F edges so that an odd number of F moves solves EO
    eo_init = [0]*layout.eo_bits
    for e in [0,4,8,7]:
        eo_init[e] = 1

    sols = find_solutions_bruteforce(layout.d, eo_init)
    assert len(sols) > 0

    # number of Grover iterations for N=k^d, assume ~1 solution for simple test
    N = layout.k ** layout.d
    r = max(1, int(round(0.25*math.pi*math.sqrt(N))))
    counts, _ = run_grover_eo(layout, ALPHABET, eo_init, iters=r, shots=1024)

    # map bitstrings to tuples of symbol values (little-endian 3-bit chunks)
    def bits_to_vals(bitstr):
        s = bitstr.replace(' ', '')[::-1]
        vals = []
        for i in range(layout.d):
            chunk = s[i*layout.seq_bits_per_symbol:(i+1)*layout.seq_bits_per_symbol]
            v = int(chunk[::-1], 2)  # restore our encoding order
            vals.append(v)
        return tuple(vals)

    modes = Counter({bits_to_vals(k): v for k,v in counts.items()})
    # The most frequent measured sequence should be a known solution (or tied among solutions)
    top = modes.most_common(1)[0][0]
    assert top in sols
