# Validation

The standalone test suite exercises the public API, protocol contracts and failure handling with synthetic data. Automated tests block network traffic; they do not establish live-service acceptance or validate login, reservations, cancellation, payment or refunds.

## Source distribution

The source distribution includes the standalone tests and packaging checker. With the development dependencies installed, run:

```sh
python -m pytest
ruff check .
ruff format --check .
mypy
python -m build
python -m twine check dist/*
python tools/packaging/check_artifacts.py dist/*.whl --sdist dist/*.tar.gz
```

The artifact checker installs the wheel in an isolated temporary directory, checks its public namespace and a synthetic search, and runs the standalone tests from the extracted source archive.

## Repository-only checks

The repository also includes synthetic decoder observations and performance tools. These are development inputs and are not included in the wheel or source distribution. From a repository checkout, run:

```sh
python tools/validation/check_decoder_equivalence.py
python tools/performance/search_matrix.py
```

The decoder validator compares retained, distinct synthetic outcomes and prints its results without writing a report. Performance tools use mock transports and do not measure live-service latency or transaction acceptance. See the repository's `.github/CONTRIBUTING.md` for documentation builds and development details.
