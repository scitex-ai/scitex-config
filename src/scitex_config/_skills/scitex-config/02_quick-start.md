---
description: |
  [TOPIC] Quick start
  [DETAILS] Smallest useful example — the direct → yaml → env → default cascade with PriorityConfig.resolve().
tags: [scitex-config-quick-start]
---

# Quick Start

## The cascade

```python
from scitex_config import PriorityConfig, ScitexConfig

# Flat dictionary primitive; APP_PORT is consulted if "port" is absent.
pc = PriorityConfig(config_dict={"port": 8000}, env_prefix="APP_")
port = pc.resolve("port", direct_val=None, default=3000, type=int)

# Explicit YAML file; absent files use the packaged default instead.
config = ScitexConfig(config_path="config/app.yaml")
db_url = config.resolve(
    "database.url", direct_val=None, default="postgresql://localhost/dev",
)
# Order: direct value → YAML key → SCITEX_DATABASE_URL → fallback.
```

## Default config + paths

```python
from scitex_config import get_config, get_paths

config = get_config()                # cached packaged default.yaml
log_level = config.resolve("logging.level", default="INFO")

paths = get_paths()
print(paths.logs)                    # ~/.scitex/logs
print(paths.cache)                   # ~/.scitex/cache
```

For SciTeX-ecosystem packages, use the per-package state resolver:

```python
from scitex_config._ecosystem import local_state

log_path = local_state.runtime_path("hpc", "dispatch.log")
print(log_path)                      # ~/.scitex/hpc/runtime/dispatch.log
```

## Next

- [03_python-api.md](03_python-api.md) — full surface
- [SKILL.md](SKILL.md) — overview + ecosystem-internal `_ecosystem.local_state`
