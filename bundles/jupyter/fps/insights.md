# FPS 架构洞察

> I阶段产出：核心洞察四元组（陈述/证据/反常识/行动）+ 知识地图

## 洞察1：基于Python类型系统的异步发布-订阅依赖注入

**陈述**：fps的模块间服务共享不通过接口/抽象基类/注册表，而是以Python类型对象为key的异步发布-订阅模式。生产者调用`self.put(value, SomeType)`发布值，消费者调用`await self.get(SomeType)`按类型异步获取——若生产者尚未发布，消费者挂起等待。

**证据**：
- F-074：`Context.put` 以 `id(value_type)` 为key将SharedValue注册到`_context`字典
- F-028：`Module.put` 同时向自身context和父context发布（值向上冒泡）
- F-029/F-030：`Module.get` 在自身和父context上用task_group竞争获取，先到先得，返回`value.unwrap()`
- F-064/F-065：`SharedValue.get/get_nowait` 实现带等待/非阻塞的借用机制

**反常识**：
- 传统DI容器（FastAPI的`Depends`、pytest的fixture）在调用时同步解析依赖；fps的`get`是**异步等待**——消费者可以先于生产者请求服务，框架自动协调启动顺序。这意味着模块不需要知道其他模块何时启动，只需声明"我需要某类型的服务"。
- 值发布是"向上冒泡"的：子模块put的值自动对父模块可见，但父模块put的值对子模块不可见（通过父链查找实现）。

**行动**：
- 在`prepare`阶段注册路由等需要框架资源前置就绪的操作
- 在`start`阶段发布服务和启动后台任务
- 获取其他模块服务时使用`await self.get(Type)`，无需关心启动顺序

## 洞察2：三阶段生命周期（prepare→start→stop）通过Event+TaskGroup实现并行协调

**陈述**：Module有三个串行生命周期阶段（prepare→start→stop），每个阶段内所有模块（含子模块）并行执行。阶段间通过anyio Event同步——所有子模块完成当前阶段后，父模块才进入下一阶段。

**证据**：
- F-031：`__aenter__`中先执行`_prepare`（含超时控制），成功后执行`_start`
- F-032：`__aexit__`中执行`_stop`
- F-037：`_prepare`用task_group并行启动所有子模块的`_prepare`和自身的`_prepare_and_done`
- F-034：`done()`根据当前`_phase`设置对应的Event（prepared/started）
- F-043：`_stop`阶段先逆序调用context_manager_exit，再并行停止子模块
- F-014：每个阶段默认超时1秒（prepare_timeout/start_timeout/stop_timeout=1）

**反常识**：
- 默认的`prepare()`/`start()`/`stop()`方法是空的（`pass`），框架的`_prepare_and_done`会自动调用`done()`——空方法不会导致挂起。但如果方法体内启动了**长驻后台任务**（如无限循环服务器），必须**显式调用`self.done()`**通知阶段完成，否则1秒后超时崩溃。
- `stop`阶段的回调执行顺序是**逆序**（LIFO）：teardown_callback按添加顺序的反序调用（F-032中`_teardown_callbacks[::-1]`），这与上下文管理器的栈式退出一致。
- 超时是全局收集的：`_get_all_prepare_timeout`递归遍历所有未完成模块，每个超时模块都添加一个TimeoutError到exceptions列表。

**行动**：
- 启动长驻任务（如Web服务器）时，必须在create_task_group内start_soon后立即调用`self.done()`
- 可通过`global_start_timeout`设置prepare+start的总超时
- teardown_callback的注册顺序与执行顺序相反，注意资源释放的依赖关系

## 洞察3：SharedValue/Value实现类似Rust借用机制的安全资源生命周期

**陈述**：SharedValue是带引用计数的异步资源共享抽象，Value是借用句柄。借用方必须显式drop Value，所有借用方drop后SharedValue才能aclose（关闭并执行teardown_callback）。支持`max_borrowers`限制并发借用数。

**证据**：
- F-060/F-102：SharedValue维护`_borrowers: set[Value]`集合
- F-064：`get()`在`fail_after(timeout)`中循环等待`len(_borrowers) < _max_borrowers`
- F-066：`freed()`等待`_borrowers`为空集合
- F-067：`aclose()`先等待freed，再执行teardown_callback
- F-051/F-058：Value支持同步上下文管理器协议（`__enter__`→unwrap，`__exit__`→drop）
- F-079：Context.aclose在fail_after中并行关闭所有SharedValue

**反常识**：
- Value的drop不是自动的（不像Rust的RAII）——Python没有作用域结束自动drop的机制，必须显式调用`value.drop()`或使用`with value:`上下文管理器。忘记drop会导致SharedValue永远无法freed，最终aclose超时。
- `SharedValue.get()`返回的是Value包装器，必须通过`.unwrap()`获取实际对象。这与直接返回对象不同——包装器追踪借用状态。
- teardown_callback支持同步和异步函数，通过`count_parameters`+`isawaitable`自动适配（F-080/F-081），且接收exception参数（如果有异常发生）。
- `_drop`方法每次移除borrower后会创建新的Event实例（F-062），这是anyio Event不可重置特性的变通方案。

**行动**：
- 优先使用`with await context.get(Type) as obj:`语法，确保自动drop
- 资源拥有者在发布时提供teardown_callback用于清理
- 需要独占访问资源时设置`max_borrowers=1`

## 洞察4：声明式配置+entry-points实现零代码插件组装

**陈述**：fps应用可以通过Python dict或JSON文件完全声明式定义。模块类型支持三种引用方式：Python完整路径（`"module.path:ClassName"`）、entry-points注册名（如`"fps_module"`）、直接类引用。CLI的`--set`参数支持点分路径覆盖任意深度嵌套模块的配置。

**证据**：
- F-088：`import_from_string`对无`:`字符串查找`"fps.modules"` entry-points组，有`:`按`module:attr.attr`解析
- F-007：`pyproject.toml`注册`fps_module = "fps:Module"`作为内置entry-point
- F-090：`get_root_module`从config dict第一项递归构建模块树
- F-108：CLI的`--set`解析`key=value`，key按`.`分割在config中逐级创建modules子字典
- F-094：`get_config_description`可自动生成Pydantic model配置的文档（字段名、默认值、类型、描述）
- F-052/F-053：`initialize`递归实例化时，通过`get_kwargs_with_default`提取`__init__`默认值并与config合并

**反常识**：
- `"fps_module"`这个entry-point指向fps的`Module`基类本身——这意味着可以通过纯JSON配置组装一个容器模块，添加其他功能模块作为子模块，完全不需要编写Python代码。
- CLI的`--set`值都是字符串，但如果模块使用Pydantic BaseModel作为config属性（如guide.md中的Router例子），Pydantic会自动做类型转换和校验，类型错误时抛出清晰的验证错误。
- 配置合并是深度递归的（F-091）：dict值递归merge，非dict值覆盖。这意味着JSON配置和CLI的--set可以叠加使用。

**行动**：
- 插件包通过注册`fps.modules` entry-points即可被fps发现和加载
- 使用Pydantic BaseModel定义模块配置获得自动类型校验和文档生成
- 使用`fps --help-all`自动生成完整的配置参数文档

## 知识地图

### 文档分组与学习路径

```
入门路径：
  00-introduction.md    → 01-getting-started.md     → 02-module-system.md
  （fps是什么）           （安装、CLI、第一个应用）     （Module核心类与生命周期）

核心概念：
  03-context-sharing.md → 04-lifecycle-phases.md → 05-configuration-system.md
  （Context/SharedValue）  （三阶段详解与done()）   （声明式配置与CLI）

高级主题：
  06-signal-system.md → 07-web-modules.md → 08-plugin-architecture.md
  （Signal信号机制）     （FastAPI/Server）  （entry-points插件化）
```

### 概念文档覆盖事实映射

| 文档 | 覆盖事实 |
|------|---------|
| 00-introduction | F-001, F-003, F-008, F-009 |
| 01-getting-started | F-004, F-005, F-006, F-103~F-121 |
| 02-module-system | F-013~F-053 |
| 03-context-sharing | F-054~F-086 |
| 04-lifecycle-phases | F-031~F-049, F-034~F-045 |
| 05-configuration-system | F-090~F-095, F-103~F-121 |
| 06-signal-system | F-096~F-102 |
| 07-web-modules | F-112~F-121 |
| 08-plugin-architecture | F-007, F-087~F-089 |

### 示例文档规划

| 示例 | 对应概念 | 来源 |
|------|---------|------|
| 01-first-app | 入门/模块基础 | guide.md最简应用 |
| 02-sharing-objects | 模块间通信 | guide.md对象共享 |
| 03-web-server | Web模块 | guide.md可插拔服务器 |
| 04-declarative-config | 配置系统 | guide.md声明式配置 |
| 05-standalone-context | Context独立使用 | guide.md Contexts章节 |
| 06-signals-usage | Signal信号 | guide.md Signals章节 |

### references信源文件

| 信源文件 | 对应源码 |
|---------|---------|
| module-source.md | _module.py（Module类+initialize） |
| context-source.md | _context.py（Context/SharedValue/Value） |
| config-source.md | _config.py + _importer.py |
| signal-source.md | _signal.py |
| cli-source.md | cli/_cli.py |
| web-source.md | web/fastapi.py + web/server.py |

---

## 可复用设计模式（C阶段沉淀）

从FPS源码中萃取的5个可迁移到其他异步Python项目的设计模式：

### 模式1：三阶段生命周期 + 全屏障同步

**问题**：异步组件树需要协调启动/关闭顺序，避免"服务器在路由注册前启动"之类的竞态。

**FPS方案**：
- 三阶段串行（prepare→start→stop），阶段内并行，阶段间Event全屏障同步
- `done()` 显式标记阶段完成（长驻任务必须调用，空方法自动完成）
- 默认超时1秒，防止忘记done()导致挂死

**迁移要点**：使用 `anyio.Event` + `create_task_group` 实现，每个阶段结束后set Event，下一阶段wait Event。适合需要明确初始化/运行/清理阶段的组件系统。

### 模式2：类型驱动的异步发布-订阅

**问题**：模块间服务共享需要解耦生产者和消费者，但同步DI容器在异步场景下无法处理"先请求后发布"的时序。

**FPS方案**：
- 以Python类型对象（`id(type)`）为key的异步put/get
- `await get(Type)` 在值未发布时自动挂起，发布后唤醒
- 值向上冒泡（子→父链），兄弟模块通过共同祖先共享
- 模块级 `put()`/`get()` 函数通过ContextVar绑定当前Context

**迁移要点**：类似asyncio.Future，但按类型keyed；支持多个消费者通过task_group竞争获取。适合插件化、模块化的异步应用框架。

### 模式3：借用计数 + teardown回调的资源管理

**问题**：异步资源（数据库连接、文件句柄、锁）需要安全的生命周期管理，确保所有使用者释放后才清理。

**FPS方案**：
- SharedValue（资源持有方）维护borrowers集合，Value（借用方）是带drop的句柄
- `with await get(Type) as obj:` 同步上下文管理器确保自动drop
- `max_borrowers` 限制并发借用数（=1实现独占访问）
- teardown_callback在所有借用者释放后执行，支持同步/异步，可接收exception参数
- `freed()` 等待所有借用者释放

**迁移要点**：参考Rust的RefCell/RAII模式在Python async中的实现。ContextVar绑定当前Context，使得 `with get(Type)` 语法简洁。

### 模式4：entry-points + 声明式配置的插件组装

**问题**：插件化应用需要在运行时发现和加载第三方模块，同时保持配置的声明性。

**FPS方案**：
- Python entry-points（`fps.modules`组）实现零import插件发现
- JSON配置声明模块树，type字段支持三种引用（Python路径/entry-point名/本地模块）
- CLI `--set key=value` 点分路径覆盖任意深度配置
- Pydantic BaseModel提供自动类型校验和配置文档生成
- 内置 `"fps_module"` entry-point指向Module基类，实现零代码容器

**迁移要点**：Python packaging的entry-points是标准机制，配合 `importlib.metadata.entry_points()` 使用。深度merge字典配置支持CLI+配置文件叠加。

### 模式5：轻量级异步信号（Signal）

**问题**：事件通知场景不需要资源生命周期管理，但需要支持一对多广播和异步迭代。

**FPS方案**：
- `Signal` 使用 `MemoryObjectSendStream` 集合 + 回调列表
- `connect()`/`disconnect()` 管理回调，支持同步/异步
- `iterate()` 返回MemoryObjectReceiveStream，支持async for迭代
- emit时task_group并行发送，BrokenResourceError自动清理断开的stream
- 不涉及借用/释放/teardown，纯粹的事件分发

**迁移要点**：基于anyio的MemoryObjectStream实现，~40行代码。适合状态变更通知、事件总线场景，与资源共享（Context）互补。

### 反模式警示

1. **不要在start()中启动长驻任务而忘记done()** → 1秒后超时崩溃
2. **不要忘记drop Value** → SharedValue永远无法freed，aclose超时
3. **不要在stop()中假设所有资源仍可用** → teardown是LIFO逆序，子模块可能已清理
4. **不要用父Context put被子模块get的方式共享** → 值只向上冒泡，父对子不可见
5. **不要混用Signal和Context共享** → 事件通知用Signal，资源共享用Context
