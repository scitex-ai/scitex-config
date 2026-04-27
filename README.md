# scitex-config

<!-- scitex-badges:start -->
[![PyPI](https://img.shields.io/pypi/v/scitex-config.svg)](https://pypi.org/project/scitex-config/)
[![Python](https://img.shields.io/pypi/pyversions/scitex-config.svg)](https://pypi.org/project/scitex-config/)
[![Tests](https://github.com/ywatanabe1989/scitex-config/actions/workflows/test.yml/badge.svg)](https://github.com/ywatanabe1989/scitex-config/actions/workflows/test.yml)
[![Install Test](https://github.com/ywatanabe1989/scitex-config/actions/workflows/install-test.yml/badge.svg)](https://github.com/ywatanabe1989/scitex-config/actions/workflows/install-test.yml)
[![Coverage](https://codecov.io/gh/ywatanabe1989/scitex-config/graph/badge.svg)](https://codecov.io/gh/ywatanabe1989/scitex-config)
[![Docs](https://readthedocs.org/projects/scitex-config/badge/?version=latest)](https://scitex-config.readthedocs.io/en/latest/)
[![License: AGPL v3](https://img.shields.io/badge/license-AGPL_v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
<!-- scitex-badges:end -->


Configuration helpers (YAML + dotenv with layered priority) extracted from the [SciTeX](https://github.com/ywatanabe1989/scitex-python) ecosystem as a standalone package.

## Install

```bash
pip install scitex-config
```

## API

```python
import scitex_config as cfg

# YAML-based (recommended)
config = cfg.get_config()
print(config.MY_KEY)

# Path resolution
paths = cfg.get_paths()
paths.function_cache  # ~/.scitex/cache/function/...

# Layered (env > .env > yaml > defaults)
pc = cfg.PriorityConfig()
pc["DATABASE_URL"]
```

## Status

Standalone fork of `scitex.config`. Only dep is `PyYAML`. The umbrella
package's `scitex.config` import path is preserved via a `sys.modules`-alias
bridge.

## License

AGPL-3.0-only (see [LICENSE](./LICENSE)).
