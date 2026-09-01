---
type: Index
title: API Token 与源码参考
description: jupyterlab-ui-profiler 核心接口定义、Benchmark/Scenario/Dramaturg源码分析参考
tags: [jupyterlab, ui-profiler, reference, api, source-code]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T13:40:00Z" }
status: stable
stale_after: "2027-02-22"
---

## 核心API与接口定义

| 文件 | 说明 |
|------|------|
| [api-tokens.md](api-tokens.md) | IScenario、IBenchmark、IUIProfiler 等核心Token接口定义，插件入口，服务端扩展配置 |

## 源码分析

| 文件 | 说明 |
|------|------|
| [benchmarks-source.md](benchmarks-source.md) | 6种Benchmark（execution-time/style-sheets/style-rules/style-rule-groups/rule-usage/self-profile）的源码实现分析 |
| [scenarios-source.md](scenarios-source.md) | 10种内置Scenario（menuOpen/menuSwitch/tabSwitch/sidebarOpen/completer/scroll/debugger/create-cells/custom等）的源码实现分析 |
| [dramaturg-source.md](dramaturg-source.md) | Dramaturg浏览器自动化层的源码分析（waitForSelector/waitForLayout/click/hover/fill等） |

```{toctree}
:hidden:
:maxdepth: 7

api-tokens
benchmarks-source
dramaturg-source
scenarios-source
```
