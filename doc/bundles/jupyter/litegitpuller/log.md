# Changelog

All notable changes to this documentation bundle.

## [0.3.0] - 2026-08-22

### Added
- Initial OKF v0.2 documentation bundle for litegitpuller v0.3.0
- 9 concept documents covering introduction, architecture, core classes, platform implementations, plugin mechanism, URL parameters, limitations, and custom providers
- 4 practical examples: GitHub pull, GitLab pull, auto-open notebook, custom upload path
- 4 source reference documents: index.ts, gitpuller.ts, Python package, build configuration
- R-phase facts collection (66 zero-inference facts)
- I-phase architecture insights (5 core insights with knowledge map)

### Verified (V-phase)
- Directory structure: 22 files (4 references + 9 concepts + 4 examples + 3 indexes + facts + insights + log) confirmed complete
- YAML frontmatter: all concept/reference/example documents contain required fields (type, title, description, tags, generated, verified, status, stale_after, sources)
- Link format: zero `../` relative path violations; all cross-references use OKF-standard paths
- API authenticity: core classes (`GitPuller`, `GithubPuller`, `GitlabPuller`) and methods (`clone`, `getFileList`, `getFile`, `testNbGitPuller`) verified against source via grep
- Plugin metadata: `JupyterFrontEndPlugin`, `autoStart: true`, `IDefaultFileBrowser` dependency confirmed in src/index.ts
