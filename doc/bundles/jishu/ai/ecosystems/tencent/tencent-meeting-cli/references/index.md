# References

本目录登记腾讯会议 CLI 知识包的 8 份信源（10 个 URL/文件）。所有概念文档与示例文档均通过 frontmatter `sources` 字段溯源至以下信源，事实不超出信源范围。

| 信源 ID | 文件 | 标题 | 对应事实（摘选） |
|---------|------|------|------------------|
| product-page | [product-page.md](product-page.md) | 腾讯会议 CLI 产品首页 | F-002、F-005 ~ F-007、F-011、F-016、F-018、F-020 |
| install-guide | [install-guide.md](install-guide.md) | CLI 安装指南（面向 AI Agent） | F-012、F-013、F-019、F-020 |
| github-readme | [github-readme.md](github-readme.md) | GitHub README（main 分支） | F-001、F-003、F-017、F-021、F-022、F-024、F-028、F-033、F-035、F-038、F-039、F-097 |
| cloud-doc | [cloud-doc.md](cloud-doc.md) | 腾讯云文档《腾讯会议 CLI 说明》（2026-07-08） | F-004、F-015、F-025、F-029、F-030、F-034、F-040、F-093、F-094、F-096 |
| command-reference | [command-reference.md](command-reference.md) | 官方完整命令参考 docs/command.md（1594 行，v1.0.18） | F-026、F-027、F-041 ~ F-061、F-065、F-067 ~ F-071、F-080 ~ F-091 |
| skill-manifest | [skill-manifest.md](skill-manifest.md) | SKILL.md（v1.0.18）+ CHANGELOG + package.json | F-008 ~ F-010、F-014、F-023、F-032、F-036、F-037、F-062 ~ F-064、F-066、F-072 ~ F-079、F-082、F-086、F-092、F-095、F-098 |
| source-code | [source-code.md](source-code.md) | 源码主体固定 tag v1.0.18（@ e631b35，Go module tmeet） | F-113 ~ F-199 |
| user-manual-qqdoc | [user-manual-qqdoc.md](user-manual-qqdoc.md) | 腾讯文档官方用户手册《腾讯会议 CLI使用说明》（2026-06-25） | F-099 ~ F-112 |

## 信源使用说明

- **产品首页**：产品定位、兼容 Agent、业务宣传场景与 FAQ；
- **安装指南**：CLI+Skill 两步安装与重启验证（面向 Agent 的安装说明书）；
- **GitHub README**：开源属性、源码构建、授权流程、凭证加密、命令树与全局契约、官方风险提示；
- **腾讯云文档**：调用链路、Keychain 口径、套餐条件、旧版 19 命令清单与常见报错；**页面时间 2026-07-08，部分内容滞后于 main 分支**；
- **腾讯文档用户手册**：产品团队维护的最终用户面教程（2026-06-25 保存，比云文档早 13 天、内容高度同源），独有灰度申请表/规则中心/反馈渠道精确 URL、v1.0.0 时期 19 命令逐名表与四个对话式场景；**命令面同样滞后，参数级以 command.md 为准**；
- **命令参考**：44 个子命令的参数级权威来源（v1.0.18）；
- **Skill 清单/变更日志/包清单**：Agent 行为红线、版本演进与包元数据；
- **源码主体（v1.0.18 固定 tag）**：实现侧权威——命令装配、OAuth/凭证内部机制、HTTP 传输、事件总线内核、枚举/输出/日志/崩溃的 How 与 Why；含全部关键计数的机械复核记录；与文档冲突时机制解释以源码为准，用户面文案仍归文档信源。

## 口径差异登记

| 议题 | 口径 A | 口径 B | 处置 |
|------|--------|--------|------|
| Node 版本 | 安装指南/package.json：`>=14`（F-013、F-014） | 腾讯云文档（F-015）与腾讯文档用户手册（F-102）均写 `≥16` | 并列，建议 LTS；≥16 已有两个用户面信源佐证 |
| 命令数量 | README/command.md（v1.0.18）：44 子命令（F-033） | 腾讯云文档（2026-07-08，F-034）与腾讯文档用户手册（2026-06-25，F-104）均为 19 命令 | 以 v1.0.18 command.md 为准；19 个旧命令名已验证全部存活（F-105），44=19+25 纯增量 |
| 凭证存储 | README：AES-256-GCM 加密本地保存（F-024） | 腾讯云文档：系统 Keychain、设备绑定（F-025） | 互补：加密 + Keychain 托管；腾讯文档用户手册在同一句中并列两种表述（F-107）；源码侧进一步深化（F-149）：「系统 Keychain」仅 macOS 字面成立，Linux 为 0600 master.key 文件、Windows 为注册表+DPAPI，三平台业务数据统一 .enc |
| 事件 key 清单 | schemas.go 头注释提及 recording.failed | 源码实际注册 8 个 key，recording.failed 未注册（F-173、F-174） | 以 RegisterKey 注册表为准；新增事件需改代码发版本 |
| Base64 转换编码数 | CHANGELOG v1.0.18：支持 4 种 | 源码 Base64DecodeConverter 实际 3 种（F-189） | 以源码 3 种为准，并列登记 |
| 首个版本号 | 旧文案/构建示例出现「v1.0.0」（F-017、F-106） | CHANGELOG 实测 18 版，自 v1.0.1 始、无 v1.0.0（F-195） | v1.0.0 仅为构建命令示例值；「v1.0.0 时期」为按手册日期的推断措辞 |

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
source-code
user-manual-qqdoc
```
