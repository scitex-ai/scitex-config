---
description: |
  [TOPIC] Installation
  [DETAILS] pip install scitex-config (no system deps, pure Python). PyYAML and scitex-logging are mandatory runtime dependencies.
tags: [scitex-config-installation]
---

# Installation

## Standard

```bash
pip install scitex-config
```

Runtime requirements are `PyYAML>=6.0.2` and `scitex-logging>=0.2.2`.
The package supplies its own dotenv parser; `python-dotenv` is not required.
YAML support is part of the base installation, with no `yaml` extra.

## Verify

```bash
python -c "import scitex_config; print(scitex_config.__version__)"
python -c "from scitex_config import PriorityConfig, get_config, get_paths; print('ok')"
```

## Editable install (development)

```bash
git clone https://github.com/scitex-ai/scitex-config
cd scitex-config
pip install -e .
```

## Used by

scitex-config is a foundational dependency — pulled in transitively by most
`scitex-*` packages. You rarely install it standalone unless writing a new
SciTeX package or using its primitives directly.
