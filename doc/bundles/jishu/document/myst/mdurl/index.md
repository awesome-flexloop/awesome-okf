---
type: bundle
title: mdurl — Markdown URL 工具库
okf_version: '0.2'
generated:
  by: reference_agent/trae-cn
  at: '2026-08-23'
verified: grep-verified
status: stable
stale_after: '2027-08-23'
tags:
- mdurl
---

# mdurl — Markdown URL 工具库

本知识包是 [mdurl](https://github.com/executablebooks/mdurl)（MIT 许可证）的系统化中文源码教程。mdurl 是 JavaScript mdurl 包的 Python 端口，提供 URL 的解析、格式化、编码、解码四大核心功能，是 [markdown-it-py](../markdown-it-py/concepts/00-introduction.md) Markdown 解析器的直接依赖。所有内容均溯源至 mdurl v0.1.2 源码（`external/libs/ai/executablebooks/mdurl/src/mdurl/` 目录），遵循 [OKF v0.2 规范](concepts/00-introduction.md) 的 R→I→E 三阶段工作流生成。

## 概念文档（concepts/）

* [mdurl 简介](concepts/00-introduction.md) — mdurl 是什么、起源（Node.js url 模块移植）、核心 API 概览、函数式设计哲学、环境要求
* [URL 数据结构](concepts/01-url-data-structure.md) — URL namedtuple 的 8 个字段详解（protocol/slashes/auth/port/hostname/hash/search/pathname）、MutableURL 内部可变构建器、不可变设计模式、TYPE_CHECKING 条件类型标注
* [URL 解析与格式化](concepts/02-parse-and-format.md) — parse() 函数的 7 步解析流程（预处理→快速路径→协议提取→slashes判断→主机解析→尾部组件→特殊协议）、slashes_denote_host 参数、format() 逆向拼接规则、parse/format 往返一致性、与 urllib.parse 的 6 项关键差异
* [URL 编码与解码](concepts/03-encode-and-decode.md) — 百分号编码原理、encode() 函数（DEFAULT/COMPONENT 两种模式、keep_escaped 参数、Unicode 代理对处理）、decode() 函数（UTF-8 多字节解码、非法序列替换）、128 项 ASCII 查找表缓存机制

## 示例文档（examples/）

* [mdurl 基础使用](examples/basic-usage.md) — URL 解析与字段访问、slashes_denote_host 参数对比、URL 修改与格式化（_replace）、IPv6 地址格式化、encode/decode 两种模式演示、UTF-8 多字节编解码、完整流水线示例

## 信源登记簿（references/）

* [mdurl 源码路径映射](references/mdurl-source.md) — 6 个核心源文件（__init__.py/_url.py/_decode.py/_encode.py/_format.py/_parse.py）的路径、行数、职责、关键代码位置，10 个公共 API 签名一览表

## 信任与生命周期说明

* **status 判定依据**：全部 6 个内容文档（4 个概念 + 1 个示例 + 1 个信源登记）均 `status: stable`。内容基于对 mdurl v0.1.2 源码（`src/mdurl/` 目录下 6 个 Python 文件，共约 577 行）的逐文件阅读与事实提取（45 条源码事实 F-001~F-045），经 R→I→E 三阶段流程生成。
* **stale_after 解释**：统一设置为 `2027-08-23`。mdurl 是一个稳定的小型工具库，自 0.1.0 以来核心 API 无 breaking change；该日期作为针对未来大版本变更的保守重新评估节点。
* **核验链路**：`generated.at` 记录各文档原始生成时刻，遵循 seven-concepts 方法论 R→I→E 三阶段流程，事实零推测、API 均经源码验证。

本知识包共收录 6 个内容文档（4 个概念 + 1 个示例 + 1 个信源登记），另含 3 个子目录 index.md 与根 index.md、log.md。

```{toctree}
:hidden:
:maxdepth: 7

concepts/index
examples/index
references/index
spec/facts
spec/insights
log
```
