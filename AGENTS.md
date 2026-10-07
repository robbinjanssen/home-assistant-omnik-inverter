# AGENTS.md

Guidance for AI coding agents working on this repository. Human contributors:
see [CONTRIBUTING](.github/CONTRIBUTING.md).

## Project

A Home Assistant custom integration (distributed through HACS) that reads Omnik
solar inverters, and compatible brands, over the local network. Domain:
`omnik_inverter`. The inverter communication lives in the
[`omnikinverter`](https://github.com/klaasnicolaas/python-omnikinverter)
library, which is maintained in another repository: fix library issues there,
not with workarounds here.

```text
custom_components/omnik_inverter/
  __init__.py        setup, unload, registry migrations, inverter device
  config_flow.py     user (JS/JSON/HTML/TCP), reconfigure and options flow
  coordinator.py     DataUpdateCoordinator polling inverter and Wi-Fi module
  models.py          base entity and device info
  sensor.py, binary_sensor.py, diagnostics.py
  strings.json, translations/{en,nl,de}.json, icons.json, brand/
tests/               pytest-homeassistant-custom-component tests
```

## Commands

The project uses [uv](https://docs.astral.sh/uv/) and
[prek](https://github.com/j178/prek).

```sh
uv sync                        # create .venv with Home Assistant and dev tools
uv run prek install            # git hook running all checks on commit
uv run prek run --all-files    # Ruff, mypy, pylint, codespell, yamllint, ...
uv run pytest                  # tests; CI requires 90% coverage
```

Run all hooks and tests before committing. The hooks refuse commits to `main`;
work on a branch.

## Requirements

- Python 3.14.2+ and Home Assistant 2026.10.0+ (`hacs.json`, README). Only
  raise the minimum on purpose and update both.
- `pytest-homeassistant-custom-component` pins the Home Assistant version used
  for development, typing and tests. `tests-beta.yaml` tests weekly against the
  Home Assistant beta.
- The manifest pins `omnikinverter==1.0.0`; `pyproject.toml` uses the same.

## Conventions

- **Typing**: mypy runs in strict mode from `pyproject.toml` against the real
  Home Assistant types. Use `probatio` for schemas (Home Assistant's validation
  library since 2026.9), not `voluptuous`.
- **Entities**: `_attr_has_entity_name = True` with a `translation_key`; never
  set `entity_id`. Icons belong in `icons.json`.
- **Translations**: Home Assistant loads `translations/*.json` for custom
  integrations. When changing `strings.json`, update `en`, `nl` and `de` too.
- **Devices**: the Wi-Fi module is a child device (`ChildDeviceInfo`) of the
  inverter, which `async_setup_entry` registers first.
- **Unique IDs**: `slugify(f"{entry_id}_{service}_{key}")`. Users keep their
  entities and history only while unique IDs stay stable; when one has to
  change, migrate it in `_async_migrate_entities` and test the migration.
- **Reloading**: use `OptionsFlowWithReload` and `async_update_reload_and_abort`.
  Do not add a config entry update listener next to these; Home Assistant
  2026.12 rejects that combination.
- **Diagnostics**: redact credentials, serial numbers and IP addresses.

## Tests

- `tests/conftest.py` mocks `OmnikInverter.inverter()` and `.device()`; no test
  talks to a real inverter.
- `conftest.py` imports `custom_components.omnik_inverter` up front, because
  pytest-homeassistant-custom-component ships its own `custom_components`
  package. Keep that import.
- Add a test for every bug fix that fails without the fix.

## Pull requests and releases

- Every pull request needs one of these labels: `breaking-change`, `bugfix`,
  `hotfix`, `documentation`, `enhancement`, `refactor`, `performance`,
  `new-feature`, `maintenance`, `ci`, `dependencies`, `skip-changelog`.
- Release Drafter derives the next version from the labels
  (`breaking-change` → major). Bump `version` in `manifest.json` and
  `pyproject.toml` to match before a release.
- Renovate keeps dependencies up to date and automerges minor and patch
  updates.
