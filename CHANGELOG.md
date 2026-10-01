# Changelog

All notable changes to `scitex-config` are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/);
versions follow [Semantic Versioning](https://semver.org/).

## [Unreleased]

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
