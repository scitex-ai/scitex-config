#!/usr/bin/env bash
# Config's owning tests run inside the digest-verified reused CI image.
# exec-in-sif.sh binds a new RUNNER_TEMP job directory over container /tmp.
# Install the full declared environment; a reduced dependency fallback cannot
# stand in for the same source, audit and real subprocess assertions.
set -euo pipefail

V="${1:?python version arg required (3.11/3.12/3.13)}"
VENV="/opt/venv-$V"
PY="$VENV/bin/python"
[ -x "$PY" ] || { echo "::error::baked Python missing: $PY"; exit 1; }
export LC_ALL=C.UTF-8 LANG=C.UTF-8
export TMPDIR="/tmp/ci-scitex_config-${GITHUB_RUN_ID:-0}-${GITHUB_RUN_ATTEMPT:-0}-$V"
rm -rf "${TMPDIR:?Config test scratch is empty}"
mkdir -p "$TMPDIR/uv-cache" "$TMPDIR/pip-cache" \
    "$TMPDIR/scitex" "$TMPDIR/pycache"
export SCITEX_DIR="$TMPDIR/scitex"
export PYTHONPYCACHEPREFIX="$TMPDIR/pycache"
export UV_CACHE_DIR="$TMPDIR/uv-cache" XDG_CACHE_HOME="$TMPDIR"
export PIP_CACHE_DIR="$TMPDIR/pip-cache"
export RUN_E2E=1
export COVERAGE_FILE="$TMPDIR/.coverage"
unset VIRTUAL_ENV || true
# Clean-environment subprocess fixtures deliberately drop PYTHONPATH. A target
# overlay would make them import the old baked Config; install the candidate
# physically into this job's writable venv so sys.executable remains genuine.
"$PY" -m venv "$TMPDIR/venv"
PY="$TMPDIR/venv/bin/python"
export PATH="$TMPDIR/venv/bin:$VENV/bin:$PATH"
uv pip install --python "$PY" -e ".[all,dev]"
export PYTHONPATH="$PWD/src${PYTHONPATH:+:$PYTHONPATH}"
"$PY" - <<'PYENV'
from importlib.metadata import version
from packaging.version import Version
assert Version(version("scitex-dev")) >= Version("0.62.1")
print("Config test auditor:", version("scitex-dev"))
PYENV
# Run the unchanged Config cascade, path and parser tests with their owning
# fixtures. Coverage artifacts stay in this job's scratch directory.
exec nice -n 19 ionice -c 3 "$PY" -m pytest tests/ -q \
    --cov=src/scitex_config --cov-report="xml:$TMPDIR/coverage.xml" --cov-report=term \
    -p no:cacheprovider
