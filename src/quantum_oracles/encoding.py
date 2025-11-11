from dataclasses import dataclass
from typing import List

@dataclass
class QubitLayout:
    d: int                 # sequence length
    k: int                 # alphabet size (<=8 if using 3 bits/symbol)
    seq_bits_per_symbol: int = 3
    eo_bits: int = 12      # EO register size

    @property
    def seq_bits(self) -> int:
        return self.d * self.seq_bits_per_symbol

    def symbol_bits_slice(self, i: int):
        a = i * self.seq_bits_per_symbol
        b = a + self.seq_bits_per_symbol
        return slice(a, b)

    @staticmethod
    def default_alphabet() -> List[str]:
        # Restricted move set good for small demos (EO changes only on F quarter-turns)
        return ['U', 'R', 'F', "U'", "R'", "F'"]
