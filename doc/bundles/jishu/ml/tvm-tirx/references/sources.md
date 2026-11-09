---
type: Reference
title: 信源台账与 P0 核验记录
description: tvm-tirx 知识包的信源清单、采集方式、P0 核验结论、两源冲突记录与本次核验的覆盖边界
tags: [tvm-tirx, 信源, 核验, p0, 冲突, 边界]
generated: { by: seven-concepts-cmd/1.1.0, at: 2026-11-09T00:00:00+08:00 }
verified: { by: process:seven-concepts-v, at: 2026-11-09T00:00:00+08:00 }
status: stable
stale_after: 2027-02-09
sources:
  - id: zhihu-article
    resource: https://zhuanlan.zhihu.com/p/2101651274798196721
  - id: apache-blog
    resource: https://tvm.apache.org/2026/11/03/rethinking-abstractions-in-the-agentic-era
  - id: tvm-tirx-repo
    resource: https://github.com/apache/tvm-tirx
  - id: tvm-tirx-docs
    resource: https://tvm.apache.org/tirx/
  - id: pypi
    resource: https://pypi.org/project/apache-tvm-tirx/
---

# 信源台账与 P0 核验记录

## 1. 信源台账

| ID | 信源 | 类型 | 采集方式 | 采集日 | 本包用途 |
|----|------|------|----------|--------|----------|
| zhihu-article | [知乎专栏文章](https://zhuanlan.zhihu.com/p/2101651274798196721) | 作者专栏（中文） | 浏览器渲染后逐段提取（直接 HTTP 返回 403） | 2026-11-09 | 问题背景、论证链、设计判断、Rust 表述 |
| apache-blog | [Apache TVM 官方博客](https://tvm.apache.org/2026/11/03/rethinking-abstractions-in-the-agentic-era) | 官方一手（英文） | HTTP 抓取 + 正文提取 | 2026-11-09 | 技术细节、验证需求、Rust WIP、代码示例 |
| tvm-tirx-repo | [apache/tvm-tirx](https://github.com/apache/tvm-tirx) | 官方仓库 | GitHub API（元信息）+ raw README | 2026-11-09 | 许可证、版本、目录、README 五项特征 |
| tvm-tirx-docs | [TIRx 文档站](https://tvm.apache.org/tirx/) | 官方文档 | HTTP 抓取 + 正文提取（8 个关键页） | 2026-11-09 | IR 指南、编程指南、扩展指南、Quick Start |
| pypi | [PyPI apache-tvm-tirx](https://pypi.org/project/apache-tvm-tirx/) | 官方包索引 | PyPI JSON API | 2026-11-09 | 版本 `0.1.0b1`、Python 版本下限、发布序列 |
| june-blog | [TIRx: An Open Compiler Stack for Evolving Frontier ML Kernels](https://tvm.apache.org/2026/06/22/tirx) | 官方一手（英文） | HTTP 抓取 + 正文提取 | 2026-11-09 | 第一代定位、编程模型、layout/dispatch、54 配置基准、megakernel、L1–L4 |
| june-zhihu | [TIRx：面向持续演进的前沿 ML Kernel 的开放编译器栈](https://zhuanlan.zhihu.com/p/2052656701392920995) | 作者专栏（中文，侯博涵） | 浏览器渲染 + `innerText` 提取（直接 HTTP 返回 403） | 2026-11-09 | 第一代中文对照、术语译法、「取代原 TensorIR」表述 |
| tvm-june-pypi | [PyPI apache-tvm 0.25.0](https://pypi.org/project/apache-tvm/0.25.0/) | 官方包索引 | 官方博客给出的链接（本次未单独抓取 JSON） | 2026-11-09 | 第一代安装命令与包名 |
| local-checkout | 本地源码检出 `external/dev/libs/TIRx/tvm-tirx`（commit `cdc7a377`） | 官方源码 | `git rev-parse` / `git log` / 直接读取文件 | 2026-11-09 | 仓库结构、后端矩阵、编译流水线、构建/测试、API 细节 |

### 采集过程中的技术事实

- 两个知乎页面直接 `curl` 均返回 **403**；经 `r.jina.ai` 代理返回「安全验证」页；最终由浏览器渲染取得正文（6 月文用 `innerText` 一次取全，11 月文分段提取）。
- Apache 博客与文档站可直接抓取，无访问控制。
- 2026-06 与 2026-11 两组中英文文章在论点与数字上高度一致；中文版分别晚 1–2 天发布。
- GitHub 元信息（star/fork/创建时间/许可证/默认分支/topics）通过 `api.github.com` 获取。
- PyPI 元信息（版本、requires-python、发布列表）通过 `pypi.org/pypi/<pkg>/json` 获取。

## 2. P0 核验结论

| # | 声明 | 结论 | 依据 |
|---|------|------|------|
| 1 | 仓库 `apache/tvm-tirx` 存在且开源 | ✅ | GitHub API：Apache-2.0、public、非 fork |
| 2 | 项目定位为 Agent 时代 ML 编译基础层 | ✅ | 仓库描述 + README 标题 + 官方博客 |
| 3 | 文档站可访问且结构完整 | ✅ | 文档站首页与 8 个页面抓取成功 |
| 4 | PyPI 包名与版本 | ✅ | `apache-tvm-tirx` 最新 `0.1.0b1` |
| 5 | Python 版本要求 | ✅ | `requires-python >= 3.10` |
| 6 | 安装命令 | ✅ | 文档站首页与 Quick Start 一致 |
| 7 | 编译目标 `llvm` / `cuda` | ✅ | Quick Start 代码与正文 |
| 8 | 导出共享库 + 小于 1 MB 运行时 | ✅ | Quick Start「Export and Load」节 |
| 9 | 64 字节对齐要求 | ✅ | Quick Start C++ 示例注释与分配器用法 |
| 10 | 三语言支持 | ⚠️ | Python/C++ 有完整文档；Rust 被官方博客标为 WIP [F-006] |
| 11 | 「世界首个较完美 Rust+C++ 混编 ML 编译器」 | ❌ | 无法穷举验证；与官方 WIP 表述冲突 [F-030] |
| 12 | 七项 Agent 工作均在自动化 GPU kernel | ⚠️ | 仅确认官方博客点名，未逐项核验 [F-042] |
| 13 | Agent 将全面超越人类 kernel 开发 | ⚠️ | 作者判断，无量化证据 [F-038] |
| 14 | TIRx 能显著提升 Agent 开发效率 | ❌ | 未找到对照基准或性能数据 [F-040] |
| 15 | 中文文章与官方博客为同一思想的双语版本 | ✅ | 结构、论点、技术细节高度对应；博客日期早 2 天 |
| 16 | 第一代 TIRx 于 2026-06-22 发布，构建在 Apache TVM 之上 | ✅ | 官方博客标题/日期/正文；中文版 2026-06-23 [F-065][F-066][F-093] |
| 17 | 第一代安装包为 `apache-tvm` 0.25.0 | ✅ | 官方博客给出的 PyPI 链接与 `pip install` 命令 [F-071][F-095] |
| 18 | 第一代支持 `@T.jit` / `@T.prim_func` 与 `Tx.*` 粒度命名空间 | ✅ | 官方博客正文 [F-068][F-074] |
| 19 | 54 配置 B200 基准数字（1517/1404/2895/5930 TFLOPS 等） | ✅（转录） | 官方博客与中文文章数字一致；本次未独立复现 [F-081]~[F-086][F-099] |
| 20 | 第一代基准可代表第二代 `apache-tvm-tirx` 0.1.0b1 | ❌ | 包名、文档、API 均不同，官方未声明性能等价 [F-097][F-099] |
| 21 | 本地源码快照可追溯 | ✅ | HEAD `cdc7a377`（2026-11-08），工作树干净 [F-100] |
| 22 | 内置后端共 10 个（cuda/metal/rocm/trn/opencl/vulkan/webgpu/hexagon/adreno/rust） | ✅ | `_autoload_backends.py` [F-112] |
| 23 | 默认 lowering 流水线顺序 | ✅ | `compilation_pipeline.py` [F-110] |
| 24 | 构建系统为 scikit-build-core + uv，依赖 TVM-FFI | ✅ | `pyproject.toml`、`AGENTS.md` [F-101][F-113][F-115] |
| 25 | 「有后端目录」等于「该后端可用/已验证」 | ❌ | CI 的 EXTRA 分支只构建不测试 [F-108] |
| 26 | 「`compile` 无启发式」等于「零 pass」 | ❌ | 存在确定性 lowering 流水线（dispatch/layout/向量化/展开/CSE/校验）[F-110] |

## 3. 两源冲突与处理

### 冲突 1：Rust 成熟度

| 来源 | 表述 |
|------|------|
| 知乎文章 | 「这应该是世界上第一个比较完美支持 Rust 和 C++ 直接混动开发机器学习编译器的尝试」 |
| 官方博客 | First-class cross-language support: Python, C++, and **Rust (work in progress)** |
| 官方仓库 README | 写作 "Python, C++, and Rust"，未标 WIP |
| 处理 | **以官方博客 + PyPI 版本为准**：Rust 存在且可用，但成熟度未达「完美支持」；正文统一标注「WIP」 |

### 冲突 2：首发时间与文本关系

| 来源 | 时间 |
|------|------|
| 官方博客 | 2026-11-03 |
| 知乎文章 | 编辑于 2026-11-05 20:58 |

两文结构高度一致，判断为「官方博客先行、中文专栏随后发布」。引用技术细节时**优先引官方博客**，引用作者判断时引中文专栏。

### 冲突 3：热度数据

star / fork / 赞同数均为采集时点值，会随时间变化。本包只在 [index.md](../index.md)「版本与时效提示」中标注一次，不作为论据。

### 冲突 4：两个 TIRx

「TIRx」在 TVM 主仓、第一代 TVM 内嵌 DSL 与独立仓库中指向不同交付物。本包以独立仓库为主线，并在 [00-overview](../concepts/00-overview.md) 与 [08-two-generations](../concepts/08-two-generations.md) 显式辨析。

### 冲突 5：两代基准的适用范围

| 来源 | 表述 |
|------|------|
| 2026-06 官方博客 | 54 配置 B200 基准，TIRx 达到 1517/1404/2895/5930 TFLOPS 等 |
| 2026-11 官方博客 | 拆分并面向 Agent 重新设计，未给出第二代基准 |
| 处理 | 基准只能标注为「第一代 `apache-tvm` 0.25.0 的成绩」；第二代性能待官方或第三方基准 [F-099] |

### 冲突 6：API 命名

| 来源 | 表述 |
|------|------|
| 第一代 | `@T.jit` / `@T.prim_func`、`Tx.*` / `Tx.wg.*` |
| 第二代 | `@T.function`、`tvm_tirx.script.tirx`、`ir` / `ir.prim` / `tirx` |
| 处理 | 示例按代际标注；禁止把两代代码片段拼在同一示例里 [F-097] |

### 冲突 7：README 的后端范围 vs 源码后端矩阵

| 来源 | 表述 |
|------|------|
| README 五项特征 | 「minimal code generation for CUDA and host LLVM」 |
| 源码 `_autoload_backends.py` | 10 个内置后端：cuda/metal/rocm/trn/opencl/vulkan/webgpu/hexagon/adreno/rust |
| 处理 | 对外承诺以 README/博客为准；架构能力以源码为准，并标注「已注册 ≠ 已验证」[F-004][F-112] |

### 冲突 8：「无启发式」vs 确定性 lowering

| 来源 | 表述 |
|------|------|
| 官方博客 | `tirx.compile` 不施加额外启发式优化 |
| 源码 `compilation_pipeline.py` | 固定顺序的 dispatch/layout/化简/向量化/展开/CSE/校验流水线 |
| 处理 | 区分「无搜索式调优」与「无 pass」；正文统一写「确定性 lowering，不做搜索式调优」[F-022][F-110] |

## 4. 覆盖边界（未做什么）

| 未覆盖项 | 原因 | 影响 |
|----------|------|------|
| 源码逐行精读 | 本任务为文章学习 + 项目教程，不是源码精读 | 内部实现细节（如注册表具体结构）以文档为准 |
| 独立安装与运行 | 未在本次会话中执行 `pip install` 与 GPU 测试 | 示例代码可信度依赖官方文档，未做本地复现 [F-054] |
| 性能基准 | 已转录第一代官方 54 配置数据，但未独立复现；第二代无公开基准 | 引用时必须标注代际与硬件，不把第一代数字当作第二代能力 [F-099] |
| 七项 Agent 工作逐篇核验 | 超出本包范围 | 仅作为「作者引用的背景」呈现 [F-042] |
| 与 MLIR/TileLang 的深度对比 | 需要单独知识包 | 仅在 [07](../concepts/07-agent-workflow-boundary.md) 给出边界性讨论 |
| 源码构建与测试 | 未执行 `uv sync`/CMake 构建或 pytest | 源码结论来自静态阅读；构建可行性以官方 CI 为准 [F-100] |
| 非 CUDA 后端实测 | 仅确认目录/开关/文档页存在 | 「已注册」不等于「已验证」[F-108] |

## 5. 置信等级定义

| 等级 | 含义 | 使用方式 |
|------|------|----------|
| A | 官方一手且可直接复核 | 可作为事实引用 |
| B | 作者专栏，与官方博客同源 | 引用时标注「作者判断/文章表述」 |
| C | 本次核验的观察（如「未找到」） | 只用于说明覆盖边界，不当事实断言 |
| D | 无法核验的主张 | 必须显式标注，不进入结论 |

## 6. 复核建议

若需在 2027 年后再使用本包，优先复核以下易变项：

1. 第二代 PyPI 版本是否已脱离 `0.1.0b*`；
2. 官方博客/README 是否仍标 Rust 为 WIP；
3. 文档站目录是否新增「验证/形式化」章节；
4. 是否出现第三方扩展包生态；
5. 是否发布第二代性能基准（若有，需重新标注代际）；
6. 第一代 `apache-tvm` 0.25.0 文档是否仍可访问；
7. 本地源码快照是否仍为 `cdc7a377`（若更新，需重跑源码核对）；
8. 后端矩阵/CMake 开关是否变化；
9. 仓库 star/fork 与 issue 数（仅作活跃度参考）。
