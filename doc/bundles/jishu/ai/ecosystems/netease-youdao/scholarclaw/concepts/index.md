# 概念文档

ScholarClaw 核心架构概念，共 5 篇，按依赖顺序组织：从项目定位与双层调用面，到 TS 客户端与 shell 工具链两个实现层，再到 SKILL.md 契约层与源码不一致的防御性解读。

* [00 ScholarClaw 项目概览与定位](00-overview.md) — 零依赖 skill 包定位：远端 SaaS 薄客户端、TS + Shell 双层调用面总览、配置接口与五级合并链、安装方式。
* [01 TypeScript 客户端与 HTTP 路由](01-server-client.md) — `ScholarClawClient` 9 组 20 个方法、统一 request 通道与 submitBlog 例外、类型体系与错误判定。
* [02 Shell 脚本工具链与命令体系](02-shell-toolchain.md) — `common.sh` 公共库调用模式、15 个功能脚本清单、URL 编码与超时常量差异、安装打包与 npm 别名桥接。
* [03 SKILL.md 技能契约与调用时序](03-skill-contract.md) — 五重契约：触发条件、响应时间期望、SSE 事件过滤、博客异步三步法、重试退避；契约层 vs 实现层时序差异。
* [04 源码不一致与防御性兼容模式](04-evolution-inconsistency.md) — 引擎清单、博客状态枚举、命令清单三处不一致登记；实现层超集兼容解读与防御性集成实践。

```{toctree}
:hidden:
:maxdepth: 7

00-overview
01-server-client
02-shell-toolchain
03-skill-contract
04-evolution-inconsistency
```
