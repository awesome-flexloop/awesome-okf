# References

本目录登记腾讯会议 CLI 知识包的 6 份信源（8 个 URL/文件）。所有概念文档与示例文档均通过 frontmatter `sources` 字段溯源至以下信源，事实不超出信源范围。

| 信源 ID | 文件 | 标题 | 对应事实（摘选） |
|---------|------|------|------------------|
| product-page | [product-page.md](product-page.md) | 腾讯会议 CLI 产品首页 | F-002、F-005 ~ F-007、F-011、F-016、F-018、F-020 |
| install-guide | [install-guide.md](install-guide.md) | CLI 安装指南（面向 AI Agent） | F-012、F-013、F-019、F-020 |
| github-readme | [github-readme.md](github-readme.md) | GitHub README（main 分支） | F-001、F-003、F-017、F-021、F-022、F-024、F-028、F-033、F-035、F-038、F-039、F-097 |
| cloud-doc | [cloud-doc.md](cloud-doc.md) | 腾讯云文档《腾讯会议 CLI 说明》（2026-07-08） | F-004、F-015、F-025、F-029、F-030、F-034、F-040、F-093、F-094、F-096 |
| command-reference | [command-reference.md](command-reference.md) | 官方完整命令参考 docs/command.md（1594 行，v1.0.18） | F-026、F-027、F-041 ~ F-061、F-065、F-067 ~ F-071、F-080 ~ F-091 |
| skill-manifest | [skill-manifest.md](skill-manifest.md) | SKILL.md（v1.0.18）+ CHANGELOG + package.json | F-008 ~ F-010、F-014、F-023、F-032、F-036、F-037、F-062 ~ F-064、F-066、F-072 ~ F-079、F-082、F-086、F-092、F-095、F-098 |

## 信源使用说明

- **产品首页**：产品定位、兼容 Agent、业务宣传场景与 FAQ；
- **安装指南**：CLI+Skill 两步安装与重启验证（面向 Agent 的安装说明书）；
- **GitHub README**：开源属性、源码构建、授权流程、凭证加密、命令树与全局契约、官方风险提示；
- **腾讯云文档**：调用链路、Keychain 口径、套餐条件、旧版 19 命令清单与常见报错；**页面时间 2026-07-08，部分内容滞后于 main 分支**；
- **命令参考**：44 个子命令的参数级权威来源（v1.0.18）；
- **Skill 清单/变更日志/包清单**：Agent 行为红线、版本演进与包元数据。

## 口径差异登记

| 议题 | 口径 A | 口径 B | 处置 |
|------|--------|--------|------|
| Node 版本 | 安装指南/package.json：`>=14`（F-013、F-014） | 腾讯云文档：`≥16`（F-015） | 并列，建议 LTS |
| 命令数量 | README/command.md（v1.0.18）：44 子命令（F-033） | 腾讯云文档（2026-07-08）：19 命令（F-034） | 以 v1.0.18 command.md 为准，旧口径保留 |
| 凭证存储 | README：AES-256-GCM 加密本地保存（F-024） | 腾讯云文档：系统 Keychain、设备绑定（F-025） | 互补：加密 + Keychain 托管 |

完整编号事实见 [spec/facts.md](../spec/facts.md)，架构洞察见 [spec/insights.md](../spec/insights.md)。

```{toctree}
:hidden:
:maxdepth: 7

command-reference
cloud-doc
github-readme
install-guide
product-page
skill-manifest
```
