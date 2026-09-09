# 信源登记簿

* [ScholarClaw 源码事实清单](facts.md) — R 阶段 64 条事实（F-sc-001~F-sc-064）：服务端配置常量、HTTP 路由方法、类型体系、shell 脚本工具链、SKILL.md 契约细节与三处存疑不一致，逐条附 vendor 源码证据路径。
* [ScholarClaw 架构洞察](insights.md) — I 阶段 4 条洞察：TS 客户端 + Shell 脚本双调用面薄壳、SKILL.md 作为 LLM 运行时契约、curl+jq 零依赖极简主义、源码不一致的"快速演进+防御性兼容"信号，每条附事实证据与行动建议。
* [ScholarClaw 信源登记](sources.md) — 上游仓库与固定基线 commit（`git rev-parse HEAD` 实测核验）、MIT 许可证、版本 1.4.1，以及关键信源文件（`SKILL.md`/`server/config.ts`/`server/index.ts`/`server/types.ts`/`scripts/*`）与事实编号的支撑映射。

```{toctree}
:hidden:
:maxdepth: 7

facts
insights
sources
```
