# 变更日志

## 2026-11-10 · v1.0.0

**新增**

- 首版知识包：10 篇概念、5 篇示例、3 份信源、facts/insights 两份 R/I 产物。
- 固定信源：`v1.4.0-18-g5c995c3`（commit `5c995c3`，2026-03-02）。
- 事实清单 F-001 ~ F-114；洞察 I-01 ~ I-06；验证 V-01 ~ V-12。

**核验**

- 计数脚本复核：29 个 Python 文件、3,715 行、89 个测试、10 个路由、7 个部署配置、12 个异常类。
- API 存在性：文档引用的类/方法/字段逐个在源码中定位。
- 链接与 frontmatter：全部子目录 index 含 toctree；bundle-relative 链接无断裂。

**发现的信源漂移**

- `CHANGELOG.md` 最新 1.2.1，`__version__` 为 1.4.0。
- `mkdocs.yml` 与 `docs/api/deployments/` 未收录 Daytona。
- `pyproject.toml` 未声明 `aiohttp`、`typing_extensions`；`requests` 仅测试使用。
- `docs/installation.md` 未列 `[daytona]` extras。

**来源**

- 源码：`external/dao/SWE-agent/SWE-ReX/`（env-bound，按 commit 固定）。
- 官方文档：README、docs/architecture、docs/usage、docs/installation、mkdocs.yml。
