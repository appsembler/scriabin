# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
### Changed
### Removed

## [v2.0.0] - 2021-03-16

### Removed
- remove push to pushgateway functionality. Now that we are
  consistently deploying node_exporter, the textfile collectors are
  the preferred approach.

## [v1.0.1] - 2021-03-15

### Added
- bugfix: ensure that script user is in the right group to write to
  the textfiles collector directory

## [v1.0.0] - 2020-12-18
### Added
- initial version. copied in from old `roles` repo.

[Unreleased]: https://github.com/appsembler/scriabin/compare/v2.0.0...HEAD
[v2.0.0]: https://github.com/appsembler/scriabin/compare/v1.0.1...v2.0.0
[v1.0.1]: https://github.com/appsembler/scriabin/compare/v1.0.0...v1.0.1
[v1.0.0]: https://github.com/appsembler/scriabin/releases/tag/v1.0.0
