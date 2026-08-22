---
type: Facts
title: Ninja 源码事实清单
description: R阶段产出：从零推测事实，每条事实指向具体源码位置
tags: [facts, source-code, evidence, verification, build-system, ninja, c++]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T00:00:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: ninja-readme
    title: README.md
  - id: ninja-graph
    title: src/graph.h
  - id: ninja-graph-cc
    title: src/graph.cc
  - id: ninja-build
    title: src/build.h
  - id: ninja-build-cc
    title: src/build.cc
  - id: ninja-state
    title: src/state.h
  - id: ninja-state-cc
    title: src/state.cc
  - id: ninja-eval-env
    title: src/eval_env.h
  - id: ninja-eval-env-cc
    title: src/eval_env.cc
  - id: ninja-parser
    title: src/manifest_parser.h
  - id: ninja-parser-cc
    title: src/manifest_parser.cc
  - id: ninja-lexer
    title: src/lexer.h
  - id: ninja-lexer-cc
    title: src/lexer.cc
  - id: ninja-util
    title: src/util.h
  - id: ninja-disk
    title: src/disk_interface.h
  - id: ninja-deps-log
    title: src/deps_log.h
  - id: ninja-build-log
    title: src/build_log.h
  - id: ninja-dyndep
    title: src/dyndep.h
  - id: ninja-jobserver
    title: src/jobserver.h
  - id: ninja-cmd-runner
    title: src/command_runner.h
  - id: ninja-metrics
    title: src/metrics.h
  - id: ninja-main
    title: src/ninja.cc
  - id: ninja-clean
    title: src/clean.h
  - id: ninja-version
    title: src/version.h
---

# Ninja 源码事实清单

> R阶段产出：零推测事实，每条事实指向具体源码位置。禁止出现"用于"/"目的是"/"设计为"等推断词。

## 项目元数据

- F-001: 项目名称 Ninja，描述 "a small build system with a focus on speed"（README.md L1）
- F-002: 构建系统使用 CMake，CMakeLists.txt 位于项目根目录（CMakeLists.txt L1）
- F-003: 项目主页 https://ninja-build.org/（README.md L3）
- F-004: 源码位于 src/ 目录，包含 .h 和 .cc 文件对
- F-005: CMakeLists.txt 中 project(NINJA CXX C) 声明为 C++/C 混合项目（CMakeLists.txt）
- F-006: 核心可执行文件目标为 ninja，链接所有 src/*.cc（排除 test 和 win32 平台特定文件）（CMakeLists.txt）
- F-007: 源代码使用 C++11 或更高标准（CMakeLists.txt 中设置 CMAKE_CXX_STANDARD）

## 目录结构

- F-010: src/ 目录包含核心头文件和实现文件
- F-011: 核心数据结构文件：graph.h/cc（Node/Edge）、state.h/cc（State/Pool）、build.h/cc（Plan/Builder）
- F-012: 解析器文件：manifest_parser.h/cc（ManifestParser）、lexer.h/cc（Lexer）
- F-013: 求值环境文件：eval_env.h/cc（BindingEnv/Rule/Edge）
- F-014: IO与执行文件：disk_interface.h（DiskInterface）、command_runner.h（CommandRunner）、subprocess.h/cc（Subprocess）
- F-015: 日志文件：build_log.h/cc（BuildLog）、deps_log.h/cc（DepsLog）
- F-016: 工具与辅助文件：util.h/cc（工具函数）、metrics.h/cc（Metrics）、jobserver.h/cc（Jobserver）
- F-017: 功能文件：clean.h/cc（Clean）、dyndep.h/cc（Dyndeps）、graphviz.h/cc（GraphViz）、browse.h/cc（Browse）
- F-018: 主入口文件：ninja.cc（NinjaMain/main）
- F-019: 测试文件位于 src/ 目录下以 _test.cc 结尾，如 graph_test.cc、build_log_test.cc
- F-020: Windows 平台特定文件：msvc_helper_main-win32.cc、minidump-win32.cc、includes_normalize-win32.cc

## Node 结构体 `src/graph.h`

- F-100: Node 结构体表示构建图中的文件节点（graph.h L44-174）
- F-101: Node 构造函数接受 `const std::string& path, uint64_t slash_bits`（graph.h L46）
- F-102: Node::Stat(DiskInterface*, std::string* err) 方法查询文件 mtime 和存在状态（graph.h L49）
- F-103: Node::UpdatePhonyMtime(TimeStamp mtime) 更新 phony 节点的 mtime（graph.h L50）
- F-104: Node::StatIfNecessary(DiskInterface*, std::string* err) 仅在必要时 stat 文件（graph.h L51）
- F-105: Node::ResetState() 重置节点状态（graph.h L52）
- F-106: Node::MarkMissing() 标记文件缺失（graph.h L53）
- F-107: Node::exists() 返回 `exists_ == ExistenceStatusExists`（graph.h L54）
- F-108: Node::status_known() 返回 `exists_ != ExistenceStatusUnknown`（graph.h L55）
- F-109: Node::path() 返回 `path_` const 引用（graph.h L56）
- F-110: Node::PathDecanonicalized() 返回去规范化路径（graph.h L57）
- F-111: Node::mtime() 返回 `mtime_`（graph.h L60）
- F-112: Node::dirty() 返回 `dirty_`（graph.h L61）
- F-113: Node::set_dirty(bool dirty) 设置 dirty_ 标志（graph.h L62）
- F-114: Node::MarkDirty() 设置 `dirty_ = true`（graph.h L63）
- F-115: Node::dyndep_pending() 返回 `dyndep_pending_`（graph.h L64）
- F-116: Node::set_dyndep_pending(bool pending) 设置 dyndep_pending_（graph.h L65）
- F-117: Node::in_edge() 返回 `in_edge_`（graph.h L66）
- F-118: Node::set_in_edge(Edge* edge) 设置 in_edge_（graph.h L67）
- F-119: Node::generated_by_dep_loader() 返回 `generated_by_dep_loader_`（graph.h L68）
- F-120: Node::set_generated_by_dep_loader(bool value) 设置 generated_by_dep_loader_（graph.h L69）
- F-121: Node::id() 返回 `id_`（graph.h L70）
- F-122: Node::set_id(int id) 设置 id_（graph.h L71）
- F-123: Node::out_edges() 返回 `out_edges_` const 引用（graph.h L72）
- F-124: Node::validation_out_edges() 返回 `validation_out_edges_` const 引用（graph.h L73）
- F-125: Node::AddOutEdge(Edge* edge) 将 edge 添加到 out_edges_（graph.h L74）
- F-126: Node::AddValidationOutEdge(Edge* edge) 将 edge 添加到 validation_out_edges_（graph.h L75）
- F-127: ExistenceStatus 枚举值：ExistenceStatusUnknown=0, ExistenceStatusMissing, ExistenceStatusExists（graph.h L81-85）
- F-128: mtime_ 初始值为 -1（graph.h L87）
- F-129: exists_ 初始值为 ExistenceStatusUnknown（graph.h L88）
- F-130: dirty_ 初始值为 false（graph.h L89）
- F-131: in_edge_ 初始值为 nullptr（graph.h L93）
- F-132: id_ 初始值为 -1（graph.h L92）

## Edge 结构体 `src/graph.h`

- F-200: Edge 结构体表示构建图中的一条构建边（命令）（graph.h L99-172）
- F-201: Edge 包含 `const Rule* rule_` 指向所使用的规则（graph.h L159）
- F-202: Edge 包含 `std::vector<Node*> inputs_` 输入节点列表（graph.h L161）
- F-203: Edge 包含 `std::vector<Node*> outputs_` 输出节点列表（graph.h L162）
- F-204: Edge 包含 `std::vector<Node*> implicit_deps_` 隐式依赖列表（graph.h L163）
- F-205: Edge 包含 `std::vector<Node*> order_only_deps_` order-only 依赖列表（graph.h L164）
- F-206: Edge 包含 `std::vector<Node*> validation_deps_` 验证依赖列表（graph.h L165）
- F-207: Edge 包含 `std::vector<std::pair<Node*, bool>>` implicit_outs_ 隐式输出列表（graph.h L166）
- F-208: Edge 包含 `BindingEnv env_` 变量绑定环境（graph.h L160）
- F-209: Edge::outputs_ready() 返回所有输出是否就绪（graph.h）
- F-210: Edge::is_phony() 返回 rule 是否为 phony 规则（graph.h）
- F-211: Edge::GetBinding(const std::string& key) 获取变量绑定值（graph.h）
- F-212: Edge::EvaluateCommand() 求值命令字符串（graph.h）
- F-213: Edge 包含 `Pool* pool_` 指向执行池（graph.h L168）
- F-214: Edge 包含 `int deps_mtime_` 依赖 mtime 记录（graph.h L169）
- F-215: Edge 包含 `bool outputs_ready_` 输出就绪标志（graph.h L171）
- F-216: Edge 包含 `bool deps_loaded_` 头依赖已加载标志（graph.h L170）
- F-217: Edge 包含 `TimeStamp command_start_time_` 命令开始时间（graph.h）
- F-218: Edge 包含 `bool skip_outputs_` 跳过输出检查标志（graph.h）

## Rule 结构体 `src/eval_env.h`

- F-300: Rule 结构体定义构建规则（eval_env.h L30-80）
- F-301: Rule 构造函数接受 `const std::string& name`（eval_env.h L31）
- F-302: Rule::name() 返回规则名（eval_env.h L33）
- F-303: Rule 定义 `enum Deps { deps_unknown=0, deps_gcc, deps_msvc }`（eval_env.h L38-39）
- F-304: Rule 包含 `std::string command_` 命令字符串（eval_env.h L59）
- F-305: Rule 包含 `std::string depfile_` depfile 路径（eval_env.h L60）
- F-306: Rule 包含 `std::string description_` 构建描述（eval_env.h L67）
- F-307: Rule 包含 `std::string pool_name_` 池名称（eval_env.h L73）
- F-308: Rule 包含 `std::string dyndep_` dyndep 文件（eval_env.h）
- F-309: Rule 包含 `Deps deps_type_ = deps_unknown` 依赖类型（eval_env.h L62）
- F-310: Rule 包含 `bool generator_ = false` generator 标志（eval_env.h L63）
- F-311: Rule 包含 `bool restat_ = false` restat 标志（eval_env.h L66）
- F-312: Rule 包含 `bool rspfile_used_ = false` rspfile 使用标志（eval_env.h L70）
- F-313: Rule 包含 `std::string rspfile_` rspfile 路径（eval_env.h L69）
- F-314: Rule 包含 `std::string rspfile_content_` rspfile 内容（eval_env.h L70）
- F-315: Rule 包含 `int depth_ = 0` 绑定深度（eval_env.h L75）

## BindingEnv 类 `src/eval_env.h`

- F-320: BindingEnv 类管理变量绑定环境（eval_env.h L82-120）
- F-321: BindingEnv 构造函数接受 `BindingEnv* parent = nullptr`（eval_env.h L84）
- F-322: BindingEnv::AddRule(const Rule* rule) 添加规则到环境（eval_env.h）
- F-323: BindingEnv::LookupRule(const std::string& rule_name) 查找规则（eval_env.h）
- F-324: BindingEnv::AddBinding(const std::string& key, const std::string& val) 添加变量绑定（eval_env.h L94）
- F-325: BindingEnv::LookupVariable(const std::string& var) 查找变量值（eval_env.h L95）
- F-326: BindingEnv 包含 `std::map<std::string, const Rule*> rules_`（eval_env.h L113）
- F-327: BindingEnv 包含 `std::map<std::string, std::string> bindings_`（eval_env.h L114）
- F-328: BindingEnv 包含 `BindingEnv* parent_` 父环境指针（eval_env.h L112）
- F-329: Edge 内嵌 BindingEnv 实例 `env_`（graph.h L160）
- F-330: BindingEnv 支持链式查找：当前环境未找到则查找 parent_（eval_env.cc）

## State 结构体 `src/state.h`

- F-340: State 结构体管理全局构建状态（state.h L40-150）
- F-341: State::AddEdge(Edge* edge) 添加边到状态中（state.h L45）
- F-342: State::GetNode(const std::string& path, uint64_t slash_bits) 获取或创建节点（state.h L47）
- F-343: State::LookupNode(const std::string& path) 查找节点（state.h L48）
- F-344: State::LookupNodeAtPathBecauseOfCaseInsensitive(const std::string& path) 大小写不敏感查找（state.h L49）
- F-345: State::AddRule(const Rule* rule) 添加规则（state.h L51）
- F-346: State::LookupRule(const std::string& rule_name) 查找规则（state.h L52）
- F-347: State::AddPool(Pool* pool) 添加池（state.h L53）
- F-348: State::LookupPool(const std::string& pool_name) 查找池（state.h L54）
- F-349: State::Defaults() 返回默认目标列表（state.h L56）
- F-350: State::Reset() 重置所有状态（state.h L57）
- F-351: State 包含 `std::vector<Edge*> edges_` 所有边（state.h L136）
- F-352: State 包含 `std::unordered_map<std::string, Node*> paths_` 路径到节点映射（state.h L134）
- F-353: State 包含 `std::vector<Node*> nodes_` 所有节点（state.h L135）
- F-354: State 包含 `std::map<std::string, Pool*> pools_` 池映射（state.h L137）
- F-355: State 包含 `std::unordered_map<std::string, const Rule*> rules_` 规则映射（state.h L139）
- F-356: State 包含 `std::vector<Node*> defaults_` 默认目标（state.h L138）
- F-357: State 包含 `BindingEnv bindings_` 全局绑定环境（state.h L133）
- F-358: State 包含 `int next_id_ = 0` 节点 ID 计数器（state.h L141）

## Pool 类 `src/state.h`

- F-360: Pool 类定义执行池（state.h L20-38）
- F-361: Pool 构造函数接受 `const std::string& name, int depth`（state.h L22）
- F-362: Pool::name() 返回池名（state.h L24）
- F-363: Pool::depth() 返回并发深度（state.h L25）
- F-364: Pool 包含 `std::string name_`（state.h L35）
- F-365: Pool 包含 `int depth_`（state.h L36）
- F-366: Pool 包含 `int current_use_ = 0` 当前使用数（state.h L37）
- F-367: 内置池 "console" 深度为 1（state.cc）
- F-368: State 默认创建深度为 0 的池（state.cc 构造函数）

## Plan 结构体 `src/build.h`

- F-400: Plan 结构体管理构建计划（build.h L43-152）
- F-401: Plan 构造函数接受 `Builder* builder = NULL`（build.h L44）
- F-402: Plan::AddTarget(const Node* target, std::string* err) 添加构建目标（build.h L46）
- F-403: Plan::FindWork() 返回下一个可执行的 Edge（build.h L47）
- F-404: Plan::more_to_do() 返回 `wanted_edges_ > 0 && command_edges_ > 0`（build.h L48）
- F-405: Plan::work_ready() 返回 `!ready_.empty()`（build.h L49）
- F-406: Plan::EdgeFinished(Edge* edge, EdgeResult result, std::string* err) 处理边完成（build.h L52）
- F-407: Plan::CleanNode(DependencyScan* scan, Node* node, std::string* err) 清理节点（build.h L53）
- F-408: Plan::command_edge_count() 返回 command_edges_（build.h L54）
- F-409: Plan::Reset() 重置计划（build.h L55）
- F-410: Plan::PrepareQueue() 准备执行队列（build.h L56）
- F-411: Plan::DyndepsLoaded(DependencyScan*, const std::vector<Node*>&, const std::unordered_map<Edge*, Dyndeps>&, std::string* err) 处理动态依赖加载（build.h L57）
- F-412: Plan::Want 枚举：kWantNothing=0, kWantToStart, kWantToFinish（build.h L60）
- F-413: Plan 包含 `std::map<Edge*, Want> want_` 边的需求状态（build.h L143）
- F-414: Plan 包含 `EdgePriorityQueue ready_` 就绪边优先级队列（build.h L144）
- F-415: Plan 包含 `Builder* builder_`（build.h L145）
- F-416: Plan 包含 `std::vector<const Node*> targets_` 目标列表（build.h L146）
- F-417: Plan 包含 `int command_edges_` 命令边计数（build.h L147）
- F-418: Plan 包含 `int wanted_edges_` 需要边计数（build.h L148）
- F-419: Plan::ScheduleInitialEdges() 调度初始边（build.h L136）
- F-420: Plan::NodeFinished(Node* node, std::string* err) 处理节点完成（build.h L138）
- F-421: Plan::EdgeWanted(const Edge* edge) 标记边为需要（build.h L139）
- F-422: Plan::EdgeMaybeReady(std::map<Edge*, Want>::iterator want_e, std::string* err) 检查边是否就绪（build.h L140）
- F-423: Plan::ScheduleWork(std::map<Edge*, Want>::iterator want_e) 调度工作（build.h L141）
- F-424: Plan::ComputeCriticalPath() 计算关键路径（build.h L132）
- F-425: EdgeResult 枚举：kEdgeFailed, kEdgeSucceeded（build.h L51）

## Builder 类 `src/build.h`

- F-430: Builder 类执行构建过程（build.h L155-230）
- F-431: Builder 构造函数接受 State*, BuildConfig*（build.h L157）
- F-432: Builder::Build(std::string* err) 执行构建，返回 ExitStatus（build.h L160）
- F-433: Builder::AddTarget(const Node* node, std::string* err) 添加构建目标（build.h L163）
- F-434: Builder::CleanNode(DependencyScan* scan, Node* node, std::string* err) 清理节点（build.h L167）
- F-435: Builder::StartEdge(Edge* edge, std::string* err) 启动边执行（build.h L182）
- F-436: Builder::FinishEdge(Edge* edge, bool success, std::string* err) 处理边完成（build.h L183）
- F-437: Builder::Plan() 返回 Plan&（build.h）
- F-438: Builder 包含 `Plan plan_`（build.h）
- F-439: Builder 包含 `State* state_`（build.h）
- F-440: Builder 包含 `const BuildConfig& config_`（build.h）
- F-441: Builder 包含 `DiskInterface* disk_interface_`（build.h）
- F-442: Builder 包含 `CommandRunner* command_runner_`（build.h）
- F-443: BuildConfig 结构体包含 parallelism、env、dry_run、verbose 等配置（build.h L20-40）

## ManifestParser 类 `src/manifest_parser.h`

- F-450: ManifestParser 类解析 ninja 构建文件（manifest_parser.h L30-70）
- F-451: ManifestParser 构造函数接受 State*, DiskInterface*（manifest_parser.h L32）
- F-452: ManifestParser::Load(const std::string& filename, std::string* err) 加载并解析构建文件（manifest_parser.h L34）
- F-453: ManifestParser::Parse(const std::string& input, std::string* err) 解析输入字符串（manifest_parser.h L35）
- F-454: ManifestParser 包含 Lexer 实例（manifest_parser.h）
- F-455: ManifestParser 包含 State* state_（manifest_parser.h）
- F-456: ManifestParser 包含 BindingEnv* env_（manifest_parser.h）
- F-457: ManifestParser 包含 DiskInterface* disk_interface_（manifest_parser.h）

## Lexer 类 `src/lexer.h`

- F-460: Lexer 类负责词法分析（lexer.h L25-100）
- F-461: Lexer::Start(const std::string& filename, const std::string& input) 设置输入（lexer.h L27）
- F-462: Lexer::Error(std::string* err, const std::string& message, ...) 报告错误（lexer.h L47）
- F-463: Token 枚举：kError=0, kBuild, kColon, kDefault, kEquals, kIdentifier, kInclude, kIndent, kNewline, kPipe, kPipe2, kPipeAt, kPool, kRule, kTNewline, kTEquals, kTNewline, kEOF（lexer.h L32-43）
- F-464: Lexer::ReadToken() 读取下一个 token（lexer.h L50）
- F-465: Lexer::PeekToken() 预读下一个 token（lexer.h L51）
- F-466: Lexer::ReadVarValue(std::string* out, char sep) 读取变量值（lexer.h L55）
- F-467: Lexer::ReadPath(std::string* out) 读取路径（lexer.h L58）
- F-468: Lexer::ReadIdent(std::string* out) 读取标识符（lexer.h L60）
- F-469: Lexer::ReadEvalString(EvalString* eval, bool path, std::string* err) 读取求值字符串（lexer.h L61）
- F-470: Lexer 包含 `const char* input_` 当前输入位置（lexer.h L90）
- F-471: Lexer 包含 `const char* end_` 输入结束位置（lexer.h L91）
- F-472: Lexer 包含 `std::string filename_` 当前文件名（lexer.h L92）

## DiskInterface 类 `src/disk_interface.h`

- F-480: DiskInterface 抽象类定义磁盘操作接口（disk_interface.h L20-60）
- F-481: DiskInterface::Stat(const std::string& path, std::string* err) 返回文件 mtime（disk_interface.h L25）
- F-482: DiskInterface::MakeDir(const std::string& path) 创建目录（disk_interface.h L26）
- F-483: DiskInterface::ReadFile(const std::string& path, std::string* content, std::string* err) 读取文件（disk_interface.h L28）
- F-484: DiskInterface::RemoveFile(const std::string& path) 删除文件（disk_interface.h L30）
- F-485: DiskInterface::WriteFile(const std::string& path, const std::string& contents) 写文件（disk_interface.h）
- F-486: RealDiskInterface 继承 DiskInterface，实现真实磁盘操作（disk_interface.h）

## DepsLog 类 `src/deps_log.h`

- F-490: DepsLog 类管理头依赖日志（deps_log.h L30-100）
- F-491: DepsLog::OpenForWrite(const std::string& path, bool binary, std::string* err) 打开日志文件（deps_log.h L35）
- F-492: DepsLog::RecordDeps(Node* node, TimeStamp mtime, const std::vector<Node*>& deps) 记录依赖（deps_log.h L55）
- F-493: DepsLog::GetDeps(Node* node) 返回节点的依赖记录（deps_log.h L61）
- F-494: DepsLog 包含 Deps 结构体：node、mtime、deps 列表（deps_log.h L50-53）
- F-495: DepsLog::Recompact(const std::string& path, std::string* err) 压缩日志文件（deps_log.h）
- F-496: DepsLog::Load(const std::string& path, State* state, std::string* err) 加载日志（deps_log.h L32）
- F-497: DepsLog::Close() 关闭日志（deps_log.h）

## BuildLog 类 `src/build_log.h`

- F-500: BuildLog 类记录构建命令日志（build_log.h L30-100）
- F-501: BuildLog::OpenForWrite(const std::string& path, bool binary, std::string* err) 打开日志（build_log.h）
- F-502: BuildLog::RecordCommand(Edge* edge, TimeStamp start_time, TimeStamp end_time, TimeStamp mtime) 记录命令（build_log.h）
- F-503: BuildLog::LookupByOutput(const std::string& path) 查找输出对应的日志条目（build_log.h）
- F-504: BuildLog 包含 LogEntry 结构体：output、command_hash、start_time、end_time、mtime、restat（build_log.h）
- F-505: BuildLog::Recompact(const std::string& path, std::string* err) 压缩日志（build_log.h）
- F-506: BuildLog::Load(const std::string& path, State* state, std::string* err) 加载日志（build_log.h）

## Dyndeps 结构体 `src/dyndep.h`

- F-510: Dyndep 结构体表示动态依赖（dyndep.h L25-50）
- F-511: Dyndep 包含 `std::vector<Node*> implicit_inputs` 隐式输入（dyndep.h）
- F-512: Dyndep 包含 `std::vector<Node*> validations` 验证节点（dyndep.h）
- F-513: Dyndep 包含 `bool restat = false` restat 标志（dyndep.h）
- F-514: DependencyScan::LoadDyndeps(Node* dyndep_node, Dyndeps* dyndep, std::string* err) 加载动态依赖文件（dyndep.h L75）

## DependencyScan 类 `src/graph.h`

- F-520: DependencyScan 类负责依赖扫描（graph.h L176-220）
- F-521: DependencyScan 构造函数接受 State*, DepsLog*（graph.h L177）
- F-522: DependencyScan::LoadDepsFromLog(Edge* edge, std::string* err) 从 deps log 加载依赖（graph.h L182）
- F-523: DependencyScan::RecomputeDirty(Edge* edge, std::string* err) 重新计算脏状态（graph.h L186）
- F-524: DependencyScan::LoadDyndeps(Node* node, Dyndeps* dyndep, std::string* err) 加载动态依赖（graph.h）
- F-525: DependencyScan::RecomputeOutputDirty(Edge* edge, Node* most_recent_input, TimeStamp mtime, std::string* err) 重新计算输出脏状态（graph.h）

## CommandRunner 抽象结构体 `src/build.h`

- F-530: CommandRunner 抽象结构体定义命令执行接口（build.h L159-208）
- F-531: CommandRunner::CanRunMore() 返回是否可以运行更多命令（build.h L162）
- F-532: CommandRunner::StartCommand(Edge* edge) 启动命令执行（build.h L164）
- F-533: CommandRunner::WaitForCommand(std::string* err) 等待命令完成（build.h L166）
- F-534: CommandRunner::size() 返回正在运行的命令数（build.h）
- F-535: RealCommandRunner 继承 CommandRunner，使用子进程执行命令（real_command_runner.cc）
- F-536: SubprocessSet 管理子进程的IO多路复用（subprocess.h）

## Jobserver 结构体 `src/jobserver.h`

- F-540: Jobserver 结构体实现 POSIX make jobserver 集成（jobserver.h）
- F-541: Jobserver::Client 类管理 jobserver 令牌（jobserver.h）
- F-542: Jobserver::Client::Acquire() 获取令牌（jobserver.h）
- F-543: Jobserver::Client::Release() 释放令牌（jobserver.h）
- F-544: Jobserver::Client::Init() 初始化（从 MAKEFLAGS 解析）（jobserver.h）

## Subprocess 类 `src/subprocess.h`

- F-550: Subprocess 类管理子进程（subprocess.h）
- F-551: Subprocess::Start(struct SubprocessSet* set, const std::string& command) 启动子进程（subprocess.h）
- F-552: Subprocess::OnPipeReady() 处理管道就绪（subprocess.h）
- F-553: Subprocess::Finish() 等待子进程结束（subprocess.h）
- F-554: Subprocess::Done() 返回子进程是否完成（subprocess.h）
- F-555: SubprocessSet 类管理多个子进程的 IO 多路复用（subprocess.h）
- F-556: SubprocessSet::Add(Subprocess* subproc) 添加子进程（subprocess.h）
- F-557: SubprocessSet::DoWork() 等待 IO 事件（subprocess.h）

## Metrics 类 `src/metrics.h`

- F-560: Metrics 类记录性能指标（metrics.h）
- F-561: ScopedMetric 结构体在构造/析构时计时（metrics.h）
- F-562: METRIC(name) 宏创建 ScopedMetric 实例（metrics.h）
- F-563: Metrics::Report() 输出性能报告（metrics.h）
- F-564: Metrics::RecordMetric(const std::string& name, int count) 记录计数指标（metrics.h）

## NinjaMain 结构体 `src/ninja.cc`

- F-570: NinjaMain 结构体是主入口对象（ninja.cc L90-199）
- F-571: NinjaMain 构造函数接受 `const char* ninja_command, const BuildConfig& config`（ninja.cc L91）
- F-572: NinjaMain 包含 State state_ 成员（ninja.cc L102）
- F-573: NinjaMain 包含 RealDiskInterface disk_interface_ 成员（ninja.cc L105）
- F-574: NinjaMain 包含 BuildLog build_log_ 和 DepsLog deps_log_（ninja.cc L110-111）
- F-575: NinjaMain::RunBuild(int argc, char** argv, Status* status) 执行构建（ninja.cc L173）
- F-576: NinjaMain::RebuildManifest(const char* input_file, string* err, Status* status) 重新生成构建文件（ninja.cc L161）
- F-577: NinjaMain::OpenBuildLog(bool recompact_only) 打开构建日志（ninja.cc L148）
- F-578: NinjaMain::OpenDepsLog(bool recompact_only) 打开依赖日志（ninja.cc L152）
- F-579: NinjaMain 定义多个工具子命令：ToolGraph、ToolQuery、ToolDeps、ToolBrowse、ToolClean、ToolCompilationDatabase、ToolRules、ToolTargets、ToolCommands、ToolUrtle 等（ninja.cc L125-144）

## 工具函数 `src/util.h`

- F-580: FNVHash(const char* data, size_t size, size_t start) 计算 FNV 哈希（util.h）
- F-581: PathCanonicalize(const std::string& path, uint64_t* slash_bits, std::string* err) 规范化路径（util.h）
- F-582: GetTimeMillis() 返回当前时间毫秒值（util.h）
- F-583: ReadFile(const std::string& path, std::string* contents, std::string* err) 读取文件（util.h）
- F-584: WriteFile(const std::string& path, const std::string& contents, std::string* err) 写文件（util.h）
- F-585: StringPiece 类提供字符串切片（string_piece.h）
- F-586: kPathSeparator 定义路径分隔符，Windows 为 '\\'，POSIX 为 '/'（util.h）
- F-587: ExitStatus 枚举：kExitSuccess=0, kExitFailure=1, kExitInterrupted（exit_status.h）
- F-588: GetError() 获取系统错误消息（util.h）
- F-589: MakeDir(const std::string& path) 创建目录（util.h）
- F-590: TrimAsciiWhitespace(const string& s) 去除 ASCII 空白（util.h）

## 构建配置 BuildConfig `src/build.h`

- F-600: BuildConfig 结构体包含 parallelism（并行数，默认1）（build.h L23）
- F-601: BuildConfig 包含 verbose（详细输出标志）（build.h L24）
- F-602: BuildConfig 包含 dry_run（空跑标志）（build.h L25）
- F-603: BuildConfig 包含 depfile 并行加载相关配置（build.h）
- F-604: BuildConfig 包含 `std::string build_dir` 构建目录（build.h）
- F-605: BuildConfig 包含 `enum EdgeMode { kEdgeModeNormal, kEdgeModeCompileCommands, kEdgeModeCompDB }`（build.h）
- F-606: BuildConfig 包含 `bool depfile_pruning = false` depfile 裁剪标志（build.h）

## 其他关键组件

- F-700: Status 抽象类定义构建状态输出接口（status.h）
- F-701: DefaultStatusPrinter 和 SmartStatusPrinter 是 Status 的实现（status.h）
- F-702: Clean 类实现清理功能（clean.h/cc），包含 CleanTarget、CleanAll 方法
- F-703: GraphViz 类将构建图输出为 DOT 格式（graphviz.h）
- F-704: Browse 类启动 HTTP 浏览服务（browse.h）
- F-705: MissingDependencyScanner 类扫描缺失依赖（missing_deps.h）
- F-706: StringPiece 构造函数接受 const char* 和 size（string_piece.h）
- F-707: StringPiece::str() 返回 std::string（string_piece.h）
- F-708: StringPiece::AsStringPiece() 返回 StringPiece（string_piece.h）
- F-709: EvalString 类支持带变量引用的字符串（eval_env.h）
- F-710: EvalString::Parse(std::string* err) 解析字符串中的变量引用（eval_env.h）
- F-711: EvalString::Evaluate(Env* env) 在给定环境中求值字符串（eval_env.h）
- F-712: EdgePriorityQueue 按优先级排序就绪边（build.h）
- F-713: Edge::GetBindingBinding(const std::string& key) 获取绑定的内部方法（eval_env.cc）
