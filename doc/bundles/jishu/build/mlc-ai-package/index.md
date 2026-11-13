---
okf_version: "0.2"
type: bundle
title: "MLC AI 原生工具链 wheel 打包基建"
description: "mlc-ai/package 源码教程——把 LLVM/Z3/Doxygen 原生 SDK 打包成可重定位、可验证的 Python wheel，并运行 TVM/MLC-LLM 的 nightly 与稳定版流水线"
---

# MLC AI 原生工具链 wheel 打包基建

本知识包是对 [`mlc-ai/package`](https://github.com/mlc-ai/package) 仓库的系统化中文教程，基于源码逐模块阅读生成。

它讲的是一个不常见但很有代表性的工程问题：**如何把编译好的原生 C/C++ 工具链，做成 pip 能装、构建系统能用、卸载不出事的 Python wheel**。仓库里有四个发行物：

| 发行物 | 内容 | 分发目标 |
|---|---|---|
| `mlc-llvm-static` | LLVM 静态开发 SDK（库 + 头文件 + CMake 导出 + `llvm-config` 前端） | PyPI |
| `mlc-llvm-static-extra-targets` | 同一份 SDK 的全部代码生成后端分片 | PyPI |
| `mlc-z3-static` | Z3 静态库 + CMake/pkg-config 元数据 | PyPI |
| `mlc-doxygen-bin` | Doxygen CLI 可执行文件 | PyPI |
| `mlc-ai` / `mlc-llm` | TVM / MLC-LLM 的 nightly 与稳定版 wheel | GitHub Release + `mlc.ai/wheels` |

三个技术要点构成了整个仓库的骨架：

1. **一次 All-target 构建切两个 wheel**，文件所有权严格互斥，安装态决定 profile；
2. **可重定位性是被构造并强制校验的**——CMake 导出、pkg-config、`--system-libs` 三条路径都要相对化；
3. **验证的对象是"用户实际会做的链接"**——两种发现路径、四态安装矩阵、符号与 ABI 上限。

遵循 [OKF v0.2 规范](../../../meta/okf-spec/index.md)。

## 入门层（concepts/）

* [mlc-ai/package 简介](concepts/00-introduction.md) — 仓库定位、四个发行物、与 conda/系统包管理的取舍、读法建议与不适用场景。
* [仓库布局与发布模型](concepts/01-repo-layout-and-release-model.md) — `packages/` 标准布局、辅助脚本为何复制而非共享、PR/手动/夜间三类触发语义。
* [单一版本源与版本戳记](concepts/02-single-version-source.md) — `version.py` 的四个消费者、PEP 440 后缀规则、两包互钉的自动同步与升级动作。

## 构建层（concepts/）

* [scikit-build-core 与内层 CMake 流水线](concepts/03-scikit-build-inner-cmake-pipeline.md) — 外层 PEP 517 后端只做 staging/install，内层 `LANGUAGES NONE` 工程接管原生构建；`py3-none` 标签与 sdist 排除。
* [上游源码钉扎与供应链校验](concepts/04-source-pinning-and-provenance.md) — `SOURCES` 三元组、镜像回退、安全解压、许可证强制、7-Zip 与 `llvm-objcopy` 的钉扎。
* [LLVM SDK 构建配方](concepts/05-llvm-sdk-build-recipe.md) — 五类 CMake 选项、三套导出集（Base/Extra/Reference）、两次 configure、`LLVM_SYSTEM_LIBS` 改写与 Linux ORC 运行时。
* [SDK 分片：一次构建、两个 wheel](concepts/06-split-sdk-partitioning.md) — 组件图解析、依赖闭包划分、头文件三分、`base.json`/`extra.json` 与 `build_id` 一致性。

## 契约层（concepts/）

* [profile 选择与派发](concepts/07-profile-selection.md) — `auto/native/all` 三态在 C 预处理器、CMake 与 Python 三处的同构实现与一致性问题。
* [llvm-config 兼容前端](concepts/08-llvm-config-frontend.md) — 直出表、依赖后序反转的链接顺序、`--quote-paths` 跨平台、Windows launcher 定位。
* [Windows COFF 裁剪与 wheel 重压缩](concepts/09-windows-coff-and-wheel-recompression.md) — 为何 `--strip-unneeded` 不可用、COMDAT 保护清单、变换前后结构比对、7-Zip 重压缩与 100 MB 预算。

## 姊妹包（concepts/）

* [mlc-z3-static 包](concepts/10-z3-static-package.md) — 只构建静态库的裁剪、Windows `-A` 平台传递、CMake 导出与 pkg-config 相对化、许可证强制。
* [mlc-doxygen-bin 包](concepts/11-doxygen-bin-package.md) — 只构建 CLI、Flex/Bison 三级探测、Homebrew 优先、Windows ARM64 的 iconv 限制。

## 流水线层（concepts/）

* [nightly 与稳定版 wheel 流水线](concepts/12-nightly-and-stable-wheels.md) — 克隆-改名-容器编译-发布-清理闭环、GPU 变体命名、auditwheel 排除项、分组剪枝与索引页更新。
* [CI 工作流与 SDK 缓存](concepts/13-ci-workflows-and-caching.md) — 五平台矩阵、路径过滤、以"编译配方源码"为键的缓存、可信发布与构建溯源。

## 验证层（concepts/）

* [验证体系](concepts/14-verification-strategy.md) — 四层防线：单测、安装后自检、消费方探针（含压缩 DWARF 与跨目标对象）、四态安装矩阵。

## 实战示例（examples/）

* [消费 LLVM SDK](examples/00-consume-llvm-sdk.md) — pip 安装、`python -m mlc_llvm_static.config` 取路径、CMake 最小工程、裸 `llvm-config` 链接命令与常见错误排查。
* [从源码构建 LLVM SDK](examples/01-build-llvm-sdk-from-source.md) — `build_wheels.py` 全流程、覆盖项、分步执行、失败信息对照、缓存加速与只重打包。
* [消费 Z3 与 Doxygen](examples/02-consume-z3-and-doxygen.md) — 静态 Z3 的 CMake 接入与"无动态 libz3"验证、pip 版 Doxygen 生成文档、能力边界与 CI 组合脚本。

## 信源参考（references/）

* [源码与模块索引](references/00-source-map.md) — 仓库文件地图：每个路径的职责、关键函数与对应概念文档。
* [环境变量与输入参数](references/01-env-vars-and-inputs.md) — 四个包与全部 workflow 的环境变量、CLI 参数、优先级与互斥关系。
* [依赖审计要点](references/02-dependency-audit.md) — LLVM 可选依赖矩阵、静态链接闭包、平台剩余依赖、元数据需求与验证要求。

## 过程产物（spec/）

* [源码事实清单](spec/facts.md) — R 阶段产出：F-001 ~ F-162 编号事实，逐条指向具体文件或配置项。
* [架构洞察与知识地图](spec/insights.md) — I 阶段产出：八条洞察的四元组（现象/根因/影响/行动）与文档映射。

## 信任与生命周期说明

* **status 判定依据**：全部 21 个内容文档（15 个概念 + 3 个示例 + 3 个信源参考）均为 `status: stable`。内容基于对仓库 `README.md`、四个包的 `README.md`/`pyproject.toml`/`CMakeLists.txt`/`version.py`、`scripts/` 下全部 Python/shell/CMake 脚本、`verify/` 探针、`tests/python/` 套件、`.github/workflows/` 九个 workflow 与 `docker/` 镜像定义的逐文件阅读，经 seven-concepts 方法论 R→I→E→V 流程生成。
* **stale_after 解释**：统一设为 `2027-05-01`。仓库处于活跃演进期（版本号、上游 release、CI 矩阵与安全策略都可能变动），该日期作为保守的重新评估节点；引用具体版本号/哈希时请回源核对。
* **核验链路**：`generated: true` 标记由源码→OKF 工作流生成；`verified: false` 表示尚未经过人工逐条复核。事实与推断已分离——`spec/facts.md` 只记可指认到文件的事实，概念文档中的"为什么"属于归纳，冲突时以源码为准。
* **不做的事**：本包不复制上游源码，不评测产物性能，不预测 MLC AI 的路线图，也不替代该仓库自身 README（后者是使用上的第一权威）。

```{toctree}
:hidden:
:maxdepth: 7

concepts/00-introduction
concepts/01-repo-layout-and-release-model
concepts/02-single-version-source
concepts/03-scikit-build-inner-cmake-pipeline
concepts/04-source-pinning-and-provenance
concepts/05-llvm-sdk-build-recipe
concepts/06-split-sdk-partitioning
concepts/07-profile-selection
concepts/08-llvm-config-frontend
concepts/09-windows-coff-and-wheel-recompression
concepts/10-z3-static-package
concepts/11-doxygen-bin-package
concepts/12-nightly-and-stable-wheels
concepts/13-ci-workflows-and-caching
concepts/14-verification-strategy
examples/00-consume-llvm-sdk
examples/01-build-llvm-sdk-from-source
examples/02-consume-z3-and-doxygen
references/00-source-map
references/01-env-vars-and-inputs
references/02-dependency-audit
spec/facts
spec/insights
log
```
