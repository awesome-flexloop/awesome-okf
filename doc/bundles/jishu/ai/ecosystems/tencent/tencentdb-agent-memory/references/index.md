# References

本目录登记 TencentDB Agent Memory 知识包的 5 份信源文件，覆盖仓库截面、产品文档、API 三卷、部署安装与 SDK/CI。所有概念与示例文档均通过 frontmatter `sources` 字段溯源至以下信源，事实不超出 [spec/facts.md](../spec/facts.md) 登记范围。

| 信源 ID | 文件 | 标题 | 对应事实（摘选） |
|---------|------|------|------------------|
| s-repo / s-core-code 等 | [01-source-code-map.md](01-source-code-map.md) | 源码地图（commit 8b86874） | F-001~F-004、F-057~F-300 的路径锚点与计数复核 |
| s-readme / s-changelog / s-roadmap | [02-readme-changelog.md](02-readme-changelog.md) | README、五版本时间线、ROADMAP、口径差异表 | F-005~F-056、F-241 |
| s-core-api / s-know-doc / s-proxy-doc | [03-api-references.md](03-api-references.md) | v3 API 三卷与 OpenAPI 结构登记 | F-093、F-128、F-151~F-163、F-193~F-234 |
| s-install / s-deploy / s-deploy-doc | [04-deploy-install.md](04-deploy-install.md) | 八客户端接入、一键部署、env/端口/卷、两形态 | F-009~F-036、F-164~F-286 |
| s-sdk-ts / s-sdk-py / s-ci | [05-sdk-ci.md](05-sdk-ci.md) | TS/Python SDK、CI、测试与运维脚本 | F-287~F-300 |

## 信源使用说明

- **源码地图**：学习截面固定在 commit `8b86874a2daea49e3ff0fb53d699203146c5c77d`（feat/server_team 分支，tag v2.0.2-beta.3 后第 7 个提交）；含 10 项关键计数的机械复核记录。
- **README/CHANGELOG**：5 个版本（2.0.2-beta.1 ~ 2.0.0-beta.1）的完整时间线；版本号/端口/客户端数量/数据目录等 7 组口径差异并列登记。
- **v3 API 三卷**：MemoryCore 108 个文档化端点（18 数据面 + 17 Skill + 55 Meta 等）、MemoryKnowledge Wiki16/CodeGraph14/Tools2/Binding3/AutoSync2、Proxy 6 管理接口。
- **部署安装**：INSTALL_CN 8 类客户端与 deploy/global-images 脚本事实。
- **SDK/CI**：TS `@tencentdb-agent-memory/memory-sdk-ts-v2` 与 Python `tencentdb-agent-memory-sdk-python` 的 v3 结构。

完整编号事实见 [spec/facts.md](../spec/facts.md)，架构洞察见 [spec/insights.md](../spec/insights.md)。

```{toctree}
:hidden:
:maxdepth: 7

01-source-code-map
02-readme-changelog
03-api-references
04-deploy-install
05-sdk-ci
```
