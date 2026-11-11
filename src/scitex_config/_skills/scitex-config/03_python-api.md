---
description: |
  [TOPIC] Python API
  [DETAILS] Public callables — PriorityConfig, get_config, get_paths, load_dotenv, load_yaml, get_scitex_dir.
tags: [scitex-config-python-api]
---

# Python API

## Imports

```python
from scitex_config import (
    PriorityConfig,
    get_config,
    get_paths,
    load_dotenv,
    load_yaml,
    get_scitex_dir,
)
```

## `PriorityConfig`

The dictionary primitive: `direct_val → config_dict[key] → environment → default`.
Keys are flat, including literal dotted keys. Environment names use `env_prefix`
and uppercase the key, replacing dots with underscores.

```python
pc = PriorityConfig(config_dict={"port": 8000}, env_prefix="APP_")
value = pc.resolve("port", direct_val=None, default=3000, type=int)
```

## `ScitexConfig(config_path=None)`, `get_config(config_path=None)`

Use `ScitexConfig(config_path="config/app.yaml")` for nested YAML data and
`.resolve("section.subkey", direct_val=None, default=None)` for the cascade.
An existing explicit file is loaded; otherwise the packaged `default.yaml` is
used. `get_config()` caches the default instance; supplying `config_path`
creates a new instance. There is no `./config/*.yaml` directory discovery.

## `get_paths() → ScitexPaths`

`$SCITEX_DIR`-aware path manager. Properties: `.logs`, `.cache`, `.capture`,
`.screenshots`, `.scholar`, `.writer`, and more. Method
`.resolve(category, user_supplied)` returns the default or a user-supplied path.

For per-package state resolution (SciTeX-ecosystem packages), use
`from scitex_config._ecosystem import local_state` — see SKILL.md.

## Utilities

| Callable | Purpose |
|---|---|
| `load_dotenv()` | Read `.env` into `os.environ` |
| `load_yaml(path)` | Parse a YAML file (dict result) |
| `get_scitex_dir()` | Resolve `$SCITEX_DIR` (default `~/.scitex/`) |

## Ecosystem-internal (`_ecosystem`)

`from scitex_config._ecosystem import local_state` — project-scope-aware path
helpers for scitex-* package authors only. **Not stable.** See SKILL.md.
