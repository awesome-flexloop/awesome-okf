# protobuf 知识包生成日志

## 2026-09-02

**Merge**: 从 SpecWeave docs/knowledge/learning/01-agent-protocols-interfaces/protobuf-wiki/ 合并独有内容

- 新增 `concepts/17-version-selection-and-migration.md`：版本选型与迁移实践（版本演进速查表、线格式兼容性边界、选型决策树与场景矩阵、六大反模式、最佳实践清单、proto2→proto3 十项迁移检查清单、渐进式灰度迁移五阶段、Editions feature 映射、可迁移通用模式），源自 learning 侧 00-overview.md、04-selection-guide.md、05-migration-guide.md
- 更新 `concepts/index.md`、根 `index.md` 导航与 toctree（17→18 概念）
- 重复确认：learning 侧仅存 00/04/05 三章实质内容，均已整合进 17 篇；其导航中引用的 01/02/03 章（版本时间轴、对比矩阵、功能演进）在源侧缺失，而 Editions 机制已由既有 15-editions-feature-system 从源码视角覆盖，无额外内容需迁入

## R 阶段（事实采集）

- 逐模块阅读 protobuf 主仓 v37.0-dev 源码（`external/libs/protocolbuffers/protobuf/`），按五个主题并行采集，产出 5 份事实清单共 **486 条**编号事实（`.trae/specs/protocolbuffers-okf-wiki/`）：
  - `facts-repo-structure.md` — 仓库结构、版本常量、Bazel/CMake 双构建系统（F-REPO-001~067，67 条）
  - `facts-cpp-core.md` — C++ 运行时核心：消息模型、Arena、descriptor、wire format、IO、JSON、WKT（F-CPP-001~144，144 条）
  - `facts-compiler.md` — protoc 编译器：命令行框架、Parser/Importer、生成器、插件协议（F-CMP-001~090，90 条）
  - `facts-runtimes.md` — Python/Rust/hpb/Java/C#/ObjC/PHP/Ruby/Lua 多语言运行时（F-RT-001~105，105 条）
  - `facts-testing.md` — conformance、benchmarks、examples、editions 测试（F-TST-001~080，80 条）

## I 阶段（架构洞察）

- 提炼 **5 个核心架构洞察**，输出至 `.trae/specs/protocolbuffers-okf-wiki/insights.md`：
  1. 双运行时内核架构——"多语言"实为"多绑定"（C++ 全功能内核与 upb 轻量内核，Python 默认 upb）
  2. descriptor 体系是贯穿全生命周期的单一事实源（protobuf 用 protobuf 描述 protobuf 的自举设计）
  3. protoc 生成器统一接口——内置生成器与外部插件同构（main_no_generators.cc 变体证明扩展能力完全开放）
  4. Editions 特性系统——proto2/proto3 被降维为 feature 预设（Edition 八值枚举 + 生成器协商矩阵）
  5. 双一等公民构建系统 × CI 分层缓存治理（Bazel/CMake 并列 + protobuf-ci 五层缓存）
- 设计知识地图：concepts/ 17 篇分 5 组（入门 00-02 / 核心机制 03-06 / 编译器 07-10 / 运行时 11-14 / 高级 15-16）+ examples/ 5 篇 + references/ 5 篇

## E 阶段（批量生成）

### Step 1: 目录结构
- `bundles/comm/serialization/protobuf/{concepts,examples,references}/`

### Step 2: 信源先行
- `references/repo-structure.md`、`references/cpp-core.md`、`references/compiler.md`、`references/runtimes.md`、`references/testing.md`

### Step 3: concepts/（17 篇，分 3 批）
- 批 1（入门+核心机制 00-06）、批 2（编译器+运行时 07-13）、批 3（14-16）

### Step 4: examples/（5 篇）
- `01-addressbook-proto.md` ~ `05-examples-build-systems.md`

### Step 5: index 与日志（最后写）
- `concepts/index.md`、`examples/index.md`、`references/index.md`、根 `index.md`（带 okf_version frontmatter）、`log.md`（本文件）

## V 阶段（独立验证）

### Grep API 验证结果（抽样验证，全部通过）

| 标识符 | 源码位置 | 状态 |
|--------|---------|------|
| MessageLite::ByteSizeLong | src/google/protobuf/*.pb.h（生成代码） | ✅ |
| internal::ArenaStringPtr | src/google/protobuf/any.pb.h 等生成代码 | ✅ |
| UnknownFieldSet | src/google/protobuf/any.pb.h 等 | ✅ |
| MessageToJsonString / JsonStringToMessage | src/google/protobuf/json/json.h | ✅ |
| CommandLineInterface::RegisterGenerator | compiler/command_line_interface.h | ✅ |
| CommandLineInterface::AllowPlugins | compiler/command_line_interface.h | ✅ |
| PluginMain | compiler/plugin.h:56 | ✅ |
| EDITION_PROTO2 = 998 / EDITION_2026 = 1002 | descriptor.pb.h:1002/1006 | ✅ |
| _IS_UPB（PyModule_AddIntConstant） | python/protobuf.c:676 | ✅ |
| PyUpb_DescriptorPool | python/descriptor_pool.h:20 | ✅ |
| AddSerializedFile | docs/upb/design.md + python 运行时 | ✅ |
| use protobuf_cpp as kernel / use protobuf_upb as kernel | rust/protobuf_lite.rs:19/22 | ✅ |
| HPB_INTERNAL_BACKEND_UPB | hpb/multibackend.h | ✅ |

### 结构与链接检查

- Frontmatter：33 个内容文档 type/title/description/tags/generated/verified/status/stale_after/sources 九字段覆盖率 100%。
- 交叉链接：束内 `/` 前缀链接目标全部存在；无 `file:///`；修复 2 处束根 index 的 `../../meta/okf-spec/` 层级错误（应为 `../../../meta/`）。
- Index 完整性：concepts（17 篇）/examples（5 篇）/references（5 篇）子索引与文件清点一致，无遗漏。

### 质量门

- `invoke gates.utf8`：通过（5601 个文件均为有效 UTF-8）。
- `invoke gates.toctrees`：serialization 域零问题（本次 52 个失败项全部位于 containers/ 域，系既有历史问题，与本次变更无关）。

### 验证结论

- 零虚构 API（抽样 15+ 关键标识符经 Grep 源码验证存在）
- Frontmatter 完整率 100%，交叉链接无断裂
- 事实清单 486 条主仓事实均溯源至具体源码行

## C 阶段（模式沉淀）

- 经验已沉淀至 `.agents/docs/retrospective/patterns/methodology-patterns/ai-collaboration/source-code-to-okf-wiki-workflow.md`：
  - 新增第 3 次迁移验证案例「Protocol Buffers v37.0 + protobuf-ci @v6」（超大规模 monorepo 主题分片采集、姊妹仓库拆束、洞察驱动文档拓扑）
  - 新增反模式 9（束根 index 跨域链接照抄旧束模板层级）与反模式 10（并行会话下基于陈旧快照更新共享总索引）
- 本次踩坑实例：两束根 index 的 `../../meta/okf-spec/` 链接层级错误（三层分组需 `../../../`）；总索引计数被并行 Rust 域会话修改，需重读后按 268 束 / 32 组 / 13 域重新核算。
