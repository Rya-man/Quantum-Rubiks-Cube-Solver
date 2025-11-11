# Quantum Cube (Phase 0 Starter)
Hybrid quantum–classical 3×3×3 Rubik’s Cube solver. This starter provides Phase 0:
- Reproducible Python env (choose Poetry or venv+pip)
- Minimal cube model with a single face move (U)
- Unit tests and a self-test CLI
- CI workflow (GitHub Actions)

## Quickstart
```bash
# Option A: Poetry
pipx install poetry  # or: pip install --user poetry
poetry install
poetry run python -m src.cube.model --selftest
poetry run pytest -q

# Option B: venv + pip
python -m venv .venv && source .venv/bin/activate
python -m pip install --upgrade pip
pip install qiskit qiskit-aer numpy pytest rich
python -m src.cube.model --selftest
pytest -q
```
