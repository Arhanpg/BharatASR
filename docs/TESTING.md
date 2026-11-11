# Running the unit tests

Create your virtual environment, install the development extra, and run:

```powershell
pip install -e ".[dev]"
python -m pytest -q
```

The CI workflow runs the lightweight unit tests on Python 3.10, 3.11 and 3.12. It does not download ASR weights or call a hosted API. Model integration checks require the corresponding optional dependencies, model access and a real audio sample; they are intentionally separate from the fast unit-test suite.
