---
type: Pattern
title: "浏览器端WASM Python内核项目OKF Wiki生成模式"
description: "从pyodide-kernel源码学习中萃取的浏览器WASM内核+构建Addon双语言项目文档生成与架构模式"
tags: [pattern, wasm, kernel, browser, python, typescript, dual-runtime, okf-wiki]
sources:
  - facts.md
  - insights.md
---

# 浏览器端 WASM Python 内核项目 OKF Wiki 生成模式

## 适用场景

浏览器中运行的 WASM 内核/解释器类项目的源码学习和 OKF Wiki 生成，特征：
- 双代码库：构建端（Python/Node.js）+ 运行端（TypeScript + WASM Python）
- Web Worker 隔离架构
- 模拟/兼容 POSIX 环境运行原有 Python 代码
- 纯静态站点部署（构建产出 = 静态文件）
- 涉及跨语言边界通信（JS ↔ Python via WASM FFI）

## 文档结构模式

```
bundle/
├── index.md              # 入口：一句话定义+架构概览图+学习路径
├── facts.md              # R阶段：编号事实清单（按模块分区，零推测）
├── insights.md           # I阶段：架构洞察四元组+知识地图
├── concepts/             # 概念文档（三层分组）
│   ├── 入门篇（2篇）      # 是什么、快速开始（安装/构建/预览）
│   ├── 核心篇（5篇）      # 架构总览、Worker通信、构建系统、包管理、兼容层
│   └── 进阶篇（2篇）      # 消息桥接、性能/高级配置
├── examples/             # 示例文档（2-3个）
│   ├── 基本安装配置
│   └── 自定义包/扩展
└── references/           # 信源文档（按代码语言/层次划分）
    ├── Python构建端信源
    ├── TypeScript主线程+Worker信源
    ├── 浏览器端Python信源
    └── 扩展/插件信源
```

## R阶段事实采集模式

对于双语言（Python+TS）WASM内核项目，事实采集按以下顺序：

1. **pyproject.toml**：Python包元数据、入口点（Addon注册）、依赖、CLI别名
2. **constants.py/constants.ts**：版本号、URL默认值、插件ID等核心常量
3. **Python构建Addon**：按生命周期（post_init→build→post_build→check）理解资源准备
4. **TypeScript主线程Kernel**：IKernel接口实现、Worker初始化、消息处理方法
5. **TypeScript Worker抽象**：初始化流程（initRuntime→initFilesystem→initPackageManager→initKernel→initGlobals）
6. **Worker具体实现**：Comlink vs Coincident 差异点
7. **浏览器端Python包**：__init__.py初始化顺序、Mocks/Patches、Interpreter子类化
8. **包管理器**（piplite）：查找策略、安装API、配置
9. **Extension**：JupyterFrontEndPlugin注册、Kernel Spec、设置Schema

### 事实编号规则

按模块分区编号，便于引用：
- F-001~F-020：项目元数据和常量
- F-021~F-050：Python构建端Addon
- F-051~F-080：TypeScript主线程+Worker
- F-081~F-110：浏览器端Python Kernel
- F-111~F-130：piplite包管理器+Extension

## I阶段架构洞察模式

对于WASM内核项目，重点提炼以下5类洞察：

1. **双层架构洞察**：构建时vs运行时的职责分离，构建产出如何被运行时消费
2. **多模式通信洞察**：Comlink/Coincident双模式的自动选择机制和差异
3. **兼容层洞察**：如何让POSIX-targeted代码（IPython）在WASM中运行——Mock→Patch→Subclass三层
4. **包管理洞察**：WASM环境下的多级包查找策略（内置→本地索引→远程回退）
5. **跨边界消息桥接洞察**：跨语言/跨线程的消息路径（Python→WASM FFI→Worker→postMessage→主线程）

## 可复用架构模式

### 模式1：三层兼容策略（Mock→Patch→Subclass）

**问题**：成熟的Python库（如IPython）依赖POSIX系统调用，无法直接在WASM中运行。

**方案**：
1. **Mock层**：最早时机（__init__.py首行）向sys.modules注入空模块/最小实现，让import不报错
2. **Patch层**：import后修改全局状态（如matplotlib backend、环境变量）
3. **Subclass层**：继承核心类（InteractiveShell、DisplayPublisher等），重写不兼容方法

**关键原则**：Mock必须在任何业务import之前执行（sys.modules缓存机制）

### 模式2：双模式Worker自动切换

**问题**：SharedArrayBuffer+Atomics提供更好性能但需要特殊HTTP头；postMessage兼容性好但无法同步。

**方案**：
- 启动时检测`crossOriginIsolated`全局属性
- 选择加载不同的Worker文件（comlink.worker.js vs coincident.worker.js）
- 两种Worker实现同一接口（IPyodideWorkerKernel）
- 主线程代码完全不感知底层通信差异

### 模式3：回调注入跨边界桥接

**问题**：Python端的stdout/display/comm等回调需要通知主线程JS。

**方案**：
- Worker初始化完成后，从pyodide.globals获取Python对象
- 通过`.set('callback_name', js_function)`注入JS回调函数
- Python调用self.callback_name(...)自动触发JS函数（Pyodide FFI）
- JS端通过send_response统一格式转发到主线程
- 不同消息类型通过`type`字段区分，主线程switch分发

### 模式4：构建时资源准备Addon

**问题**：WASM应用需要大型二进制资源（Pyodide发行包、wheels），运行时从CDN下载可能慢或不可用。

**方案**：
- 构建时Addon生命周期：post_init（下载）→build（复制）→post_build（生成配置/索引）→check（验证）
- 基于URL hash的缓存策略避免重复下载
- 生成JSON索引文件（all.json、pyodide-lock.json）供运行时查询
- 配置通过jupyter-lite.json的litePluginSettings传递

### 模式5：三级包查找链

**问题**：WASM环境包来源多样（内置预编译、本地wheels、远程PyPI），需要统一查找接口。

**方案**：
- 优先级链：内置包（lockfile）→本地索引（all.json）→远程回退（PyPI）
- 每级查找失败后降级到下一级
- 通过disablePyPIFallback控制是否允许最末级
- 版本解析在构建端（uv）和运行端（piplite）分别处理
- 代码预转换（LiteTransformerManager）将熟悉的命令（%pip）映射到WASM实现

## G质量门检查点

- **G1**：facts.md中无因果推断词（"用于"/"目的是"），每个事实有文件:行号溯源
- **G2**：insights.md中每个洞察有陈述/证据/反常识/行动四元组
- **G3**：V阶段用Grep验证关键类名/API名存在，用脚本验证所有.md内部链接可达
