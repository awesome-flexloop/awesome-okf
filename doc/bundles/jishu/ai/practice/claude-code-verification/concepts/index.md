# 概念文档

```{toctree}
:hidden:
:maxdepth: 2

00-verification-loops
01-three-test-types
02-run-the-change
03-team-pipeline
04-gate-governance
05-misses-into-rules
```

- [验证循环与委派规模化](00-verification-loops.md) — 为什么验证是并行委派的前提，四要素模式与反模式。
- [三类测试与前置失败模式](01-three-test-types.md) — E2E / 属性 / 差分的判据、工具与选型决策树。
- [验证就是跑起来改动](02-run-the-change.md) — `verify` skill、冒烟基座与「手和眼」。
- [团队验证流水线](03-team-pipeline.md) — 人介入点、所有者写检查、按 diff 触发的清单、检查不可自改。
- [门禁治理与评审者评测](04-gate-governance.md) — observe 三态、分层召回率与重要性标签。
- [把漏检变成规则](05-misses-into-rules.md) — 两条规则化路径、flaky 处置与规则清理。
