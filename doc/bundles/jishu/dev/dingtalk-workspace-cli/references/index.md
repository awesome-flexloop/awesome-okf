---
okf_version: "0.2"
type: Reference
title: "dws 信源登记簿"
description: "dws 知识包信源层——81 项逐条事实登记（F-001 ~ F-081）与核验/对抗审查报告"
---

# 信源登记簿

| 文档 | 内容 | 何时读 |
|------|------|--------|
| [源码事实登记](facts.md) | F-001 ~ F-081 逐条登记：事实、依据文件、级别、性质标注 | 引用任何数字/结论前 |
| [核验报告](verification.md) | 核验方法、口径冲突 C-1 ~ C-4、未核验边界、对抗审查 D-1 ~ D-7 | 判断可信度与复核时点 |

## 信源分层

| 层 | 信源 | 性质 |
|----|------|------|
| L1 一手 | 仓库 `README.md`、`docs/`（architecture / command-framework-architecture / command-domain-model / reference / command-index / ci-pr-gates） | 项目方官方文档 |
| L1 一手 | 仓库源码：`cmd/main.go`、`go.mod`、`internal/` 包结构、`skills/` 布局、`.github/workflows/` | 仓库实况 |
| L1 一手 | `CHANGELOG.md`、`LICENSE`、`git log`（HEAD c631e4fb） | 发布与许可事实 |

## 采集口径

- 仓库路径：`\\10.16.11.3\ai\notebook\dev\libs\dws\dingtalk-workspace-cli`
- 采集时点：2026-11-09
- 采集方式：只读检索与文件读取；**未执行 dws 二进制、未逐包审阅源码、未访问钉钉服务端**
- 版本口径：HEAD `c631e4fb`，`v1.0.68-beta.1`

```{toctree}
:hidden:
:maxdepth: 2

facts
verification
```