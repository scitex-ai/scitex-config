# Changelog

All notable changes to `scitex-config` are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/);
versions follow [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [0.3.8] - 2026-11-12

### Fixed

- Require PyYAML 6.0.2 or newer so minimum dependency resolution does not
  select obsolete releases that cannot build on supported Python versions.
- Correct README and shipped skill examples for dictionary configuration,
  explicit YAML paths, direct values, environment names and default caching.
  Document the actual mandatory dependencies and built-in dotenv parser.

### Changed

- Admit release jobs through the shared organization CPU policy, validate tag
  inputs as data, require main ancestry and pin publishing helpers to the
  source revision used by the build. Preserve verified-image, full test,
  entry-point and OIDC publication gates.
- Supersede only older pull-request checks; retain protected-branch runs.

## [0.3.7] - 2026-10-02

### Fixed

- Keep explicitly requested resolution reports visible independently of the
  diagnostic threshold and PrintCapture; preserve masking, values and returns.
- Use Logger 0.2.2 for unconditional PlainConsole results. Declare Python 3.10
  or newer to match the required Logger's actual interpreter support.

### Changed

- Require the published Dev 0.62.1 contributor auditor.
- Verify the release image digest and use owned scratch, complete declared
  dependencies and the original full Config suite before publishing.

## [0.3.1]

- Initial CHANGELOG entry — see git log for prior history.
