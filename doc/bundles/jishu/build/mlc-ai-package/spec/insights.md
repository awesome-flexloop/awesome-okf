---
type: spec
title: "mlc-ai/package 架构洞察与知识地图"
sources:
  - "external/dev/libs/mlc-ai/package/packages/mlc-llvm-static/scripts/"
  - "external/dev/libs/mlc-ai/package/packages/mlc-llvm-static/verify/"
  - "external/dev/libs/mlc-ai/package/.github/workflows/"
---

# mlc-ai/package 架构洞察与知识地图

> I 阶段产出：基于 F-001 ~ F-162 事实清单提炼的洞察四元组（现象 / 根因 / 影响 / 行动），以及文档知识地图。
> 本文只做归纳，不引入源码之外的新事实。

## 核心洞察

### 洞察 1：这四类轮子卖的不是 Python 代码，而是"可被构建系统消费的原生契约"

- **现象**：三个 PyPI 包（F-027、F-037、F-114、F-119）的 wheel 里几乎没有可 import 的业务逻辑：`mlc-llvm-static` 装的是静态库 + 头文件 + CMake 导出，`mlc-z3-static` 装的是 `libz3` + 头文件 + CMake/pkg-config，`mlc-doxygen-bin` 装的是一个可执行文件。Python 包体只是"定位器 + 元数据读取器"（F-099、F-108）。
- **根因**：目标消费者是 CMake/llvm-config/pkg-config 驱动的 C/C++ 构建，而不是 Python 运行时。发行渠道借用了 pip/PyPI 的分发能力，但契约面在原生侧：`LLVMConfig.cmake`、`LLVM_AVAILABLE_LIBS`、`z3::libz3`、`doxygen` 可执行文件。
- **影响**：升级、ABI、可重定位性、符号可见性这些原生问题全部变成打包问题。一次 `pip install` 之后不能假设"装好了就能用"——必须保证导出文件中的路径在任意安装前缀下都能解析（F-069、F-111）。
- **行动**：阅读本包时先建立"wheel 是契约载体"的视角；判断某个实现细节是否合理，标准是"它是否保护了这条原生契约"，而不是"Python API 是否漂亮"。

### 洞察 2：用"一次 All-target 构建 + 不相交分片"替代"多套 SDK 组合"

- **现象**：`mlc-llvm-static` 与 `mlc-llvm-static-extra-targets` 来自同一次编译（F-087），文件所有权严格不相交（F-091），版本互相精确钉死（F-023），且两个 wheel 各自带一份 profile 元数据（F-085）。安装 add-on 自动切到 all，卸载自动回到 native（F-153）。
- **根因**：LLVM 后端库与通用库之间存在依赖闭包（F-074）。若拆成"基础包 + 后端包"分别编译，就必须处理两套构建的配置差异、版本漂移与重复符号；而一次编译后按组件图做闭包划分，天然保证同一 build_id。
- **影响**：分片正确性成为主要风险点：漏移一个库会导致两个 wheel 都声明它（重叠），多移一个库会让 native 档链接失败。因此代码里同时存在重叠检测（F-091）、缺失导出集检测（F-083）、以及 build_id 一致性检查（F-080）。
- **行动**：修改 `partitions()` 或 `split_sdk()` 后，必须同时跑 `pytest`（覆盖 `test_profiles.py`）与真实 wheel 的四态验证（native / all / 显式 native / 卸载 add-on，F-153），单看单元测试不足以证明分片正确。

### 洞察 3：profile 不是"运行时开关"，而是"安装态的函数"

- **现象**：`auto` 档的判定依据是 `extra.json` 是否存在（F-101），而不是环境变量或命令行。头文件用 `__has_include("llvm/Config/mlc-all/...")` 做编译期派发（F-079），CMake 侧用 `base.json`/`extra.json` 的 `build_id` 决定可用库集合（F-080、F-081），Python 侧用 `Configuration` 复现同一判定（F-101）。
- **根因**：两个 wheel 写同一个前缀目录，任何一方都不能"改写另一方的文件"，否则卸载会破坏另一方。因此只能在**读取侧**做派发：谁存在，谁生效。
- **影响**：这套设计把"安装/卸载"变成了 profile 切换机制，代价是三处实现（C 头文件、CMake、Python）必须语义一致。任何一处漏改都会出现"CMake 认为有 all、头文件却按 native 编译"的错配。
- **行动**：变更 profile 逻辑时按"三处同改"检查：`filter_headers()`、`profile_cmake()`、`Configuration.__init__()`。验证方式是 `verify_split_wheels.py` 的四态矩阵，而不是只跑其中一条路径。

### 洞察 4：可重定位性是被"构造 + 校验"出来的，不是被"期望"出来的

- **现象**：`LLVM_SYSTEM_LIBS` 中的绝对库路径被改写为库名（F-063），`.pc` 文件统一改成 `${pcfiledir}/../..`（F-071），Z3 的 CMake 导出把 `set(_IMPORT_PREFIX "<abs>")` 换成四层相对推导（F-111）并强制校验无残留（F-112），验证阶段还会把 SDK 复制到"带空格的目录"重跑（F-144）。
- **根因**：上游 CMake 的导出机制天然会写入配置时的绝对前缀；只要安装前缀变化，任何残留都会让 `find_package` 指错。Python 的安装路径（site-packages、`--user`、venv）不可预测，所以必须相对化。
- **影响**：可重定位性一旦失效，症状是"在 CI 机器上全绿、用户机器上找不到库"，属于最难远程排查的一类问题。
- **行动**：任何新增的导出文件、pkg-config、脚本路径写入，都必须同时增加"相对化 + 残留检测"两步，并在验证里覆盖含空格路径。

### 洞察 5：体积预算是发布门禁，压缩与符号裁剪都要"可证明无损"

- **现象**：两个 LLVM wheel 硬性小于 100,000,000 字节（F-090），重压缩用 7-Zip 最高 DEFLATE 档并逐项比对成员名、CRC、大小、属性（F-092），Windows 侧用 `llvm-objcopy` 只删"无引用的局部标签与未定义声明"（F-095、F-096），删除后重新解析归档逐项比对（F-097），并把工具版本写进指纹（F-098）。
- **根因**：PyPI 单文件体积限制与 wheel 数量约束共同构成硬上限；但静态 LLVM 归档天然巨大，通用 `--strip-unneeded` 会删掉 MSVC 链接器必需的 COMDAT 记录。
- **影响**：压缩逻辑必须"可证明不改变语义"，否则会出现"链接时才报错"的滞后故障；这也是为什么压缩前后要做结构级比对，而不是只看大小。
- **行动**：调整压缩或裁剪策略时，把"结构不变量"写进校验（成员集合、CRC、节内容哈希、公共定义、COMDAT），不要只以体积下降为成功标准。

### 洞察 6：缓存键由"配方源码"决定，而不是由版本号决定

- **现象**：`cache_key.py` 把上游版本+SHA、构建函数源码文本、CMake 选项文件全文、显式 CC/CXX 一起哈希（F-136），缓存键为 `llvm-all-sdk-<platform>-<key>`（F-137）；缓存保存放在 `if: always()`，即使打包失败也保留已编译 SDK（F-137）。
- **根因**：LLVM 编译是小时级成本，而版本号无法表达"构建配方变了"（例如关掉一个 LLVM 选项、换编译器）。用源码文本做键，可以做到"改配方即失效、改前端/打包即复用"。
- **影响**：缓存粒度过粗会拖慢 CI，过细则缓存命中率低；此处选择了"编译与图生成配方"作为边界，把打包、前端、验证改动排除在键外。
- **行动**：修改 `prepare_llvm.py` 的编译选项或 `split_sdk.py` 的图生成函数时，不需要手动清缓存——键会自动变化；但修改 `build_wheels.py` 或 wheel 打包逻辑时不会失效，这是有意设计。

### 洞察 7：验证的对象是"用户实际会做的链接"，而不是"文件是否存在"

- **现象**：验证探针用两套发现路径（CMake 导入目标 / 裸 `llvm-config` 旗标）构建同一个消费方（F-146），要求它不依赖动态 LLVM/zlib/zstd、导出符号只有自身 API、Linux 上 ABI 版本不超过 manylinux_2_28 上限（F-148），并真正跑一次 IR 解析 → O2 优化 → 写 bitcode → JIT 执行返回 42（F-147）。此外还构造压缩 ELF 的 DWARF 编译单元，强制走 zlib 与 zstd 两条解压路径（见 `verify/dependencies.cpp`）。
- **根因**：静态库"存在"不等于"能按正确顺序链接"，更不等于"符号不泄漏"。任何一环出错，下游（TVM-FFI ORC addon、TIRx）才会暴雷，届时定位成本极高。
- **影响**：验证代码本身成为规格说明：它明确了 SDK 的边界（不含工具、不含共享库、不含未启用的可选依赖）。改 SDK 若不改验证，等于放弃这层保护。
- **行动**：新增后端或新增导出集时，同步扩展 `verify/` 与 `verify/targets/`；把"消费者视角"作为验收口径，而非"归档清单齐全"。

### 洞察 8：nightly 与稳定版共享同一条构建路径，差异只在"检出点 + 包名 + 清理策略"

- **现象**：`PKG_KIND` 只由是否有 `tag` 决定（F-125），包名在后缀上区分 `-nightly` 与稳定版（F-123），稳定版强制要求 `MLC_STABLE_BUILD_VER`（F-121），nightly 产物统一塞进同一个 `v0.9.dev0` prerelease（F-127），由 `prune_nightly` 每天按组保留最新若干条并重写索引页（F-131、F-132）。
- **根因**：如果 nightly 与 stable 走两套脚本，构建逻辑会漂移；把差异收敛到三个变量上，可以让同一份构建脚本同时服务两条流水线。
- **影响**：稳定版的安全性依赖"tag 必须存在且递归同步子模块"（F-122）；nightly 的可用性依赖"分组的正确性"——分组键算错会导致误删稳定版资产。
- **行动**：修改版本或分组逻辑时，先用 `--dry-run` 走一遍 `wheel_prune_and_sync.py`；改动 `sync_package.py` 的检出逻辑时，重点回归嵌套子模块。

## 知识地图

```text
入门层（Getting Started）
├── 00-introduction.md                    → F-001~F-011, F-157~F-162
├── 01-repo-layout-and-release-model.md   → F-001~F-018, F-120
└── 02-single-version-source.md           → F-019~F-026

构建层（Build Pipeline）
├── 03-scikit-build-inner-cmake-pipeline.md → F-027~F-039
├── 04-source-pinning-and-provenance.md     → F-040~F-055
├── 05-llvm-sdk-build-recipe.md             → F-056~F-072
└── 06-split-sdk-partitioning.md            → F-073~F-086

契约层（Runtime Contract）
├── 07-profile-selection.md     → F-079~F-082, F-101, F-153
├── 08-llvm-config-frontend.md  → F-099~F-108
└── 09-windows-coff-and-wheel-recompression.md → F-087~F-098

姊妹包（Sibling Packages）
├── 10-z3-static-package.md     → F-109~F-114, F-155
└── 11-doxygen-bin-package.md   → F-115~F-119, F-156

流水线层（CI & Release）
├── 12-nightly-and-stable-wheels.md → F-120~F-135
└── 13-ci-workflows-and-caching.md  → F-136~F-142

验证层（Verification）
└── 14-verification-strategy.md → F-143~F-156
```

## 写作决策

- **不逐行翻译源码**：本包面向"要读懂/复用这套打包基建"的读者，重点解释**为什么这样设计**与**改哪里会坏**；逐行 API 说明交由 `references/00-source-map.md` 的索引承担。
- **事实与推断分离**：`spec/facts.md` 只记录可指认到文件的事实；本文的"根因"属于归纳，若与源码冲突以源码为准。
- **验证优先**：每个概念文档末尾给出"可执行的自检方式"，避免读者停在"读懂了"的层面。
