# JupyterLite Terminal 架构洞察

> I阶段产出：核心洞察四元组（陈述/证据/反常识/行动）+ 知识地图

## 洞察1：六插件分层架构——通过JupyterLab ServiceManager替换模式实现浏览器端终端

**陈述**：jupyterlite-terminal不直接提供终端UI，而是通过6个JupyterLab插件协作，替换JupyterLab标准的TerminalManager和TerminalAPIClient，将原本走WebSocket到后端服务器的终端通信重定向到浏览器内的cockle Shell（WebAssembly shell），实现完全浏览器端的终端体验。

**证据**：
- F-027~F-030：terminalClientPlugin提供ILiteTerminalAPIClient，注入mock-socket的WebSocket
- F-031~F-034：terminalManagerPlugin提供ITerminalManager，使用LiteTerminalAPIClient创建TerminalManager
- F-035~F-038：terminalContentsPlugin连接contentsManager实现DriveFS
- F-039~F-043：terminalServiceWorkerPlugin连接Service Worker处理stdin
- F-044~F-049：terminalThemeChangePlugin监听主题变更同步到终端
- F-138~F-139：terminalExecPlugin注册无头shell命令
- F-063~F-067：使用mock-socket的WebSocketServer在浏览器内模拟终端WebSocket端点

**反常识**：
- 终端的WebSocket连接不是连到远程服务器，而是连到浏览器内mock-socket创建的本地WebSocketServer（F-066）。xterm.js前端完全不知道后端是浏览器内的WASM shell——它看到的是标准的WebSocket协议。
- 6个插件不是平铺关系，而是有严格的依赖链：client→manager→contents/service-worker/theme-change/exec，后者都requires ILiteTerminalAPIClient。
- mock-socket库在这里的用途不是测试，而是生产环境——它拦截WebSocket构造函数，让JupyterLab的终端代码在无后端情况下正常工作。

**行动**：
- 理解这不是一个独立终端应用，而是JupyterLab终端的"后端替换层"
- 扩展终端功能时通过registerAlias/registerEnvironmentVariable/registerExternalCommand注入，而非修改源码
- 配置jupyter-lite.json的terminalsAvailable=true是启用前提

## 洞察2：双Worker模式——Coincident(SAB)与Comlink(SW)的自动选择机制

**陈述**：TerminalShell根据运行环境自动选择两种Web Worker通信模式：Coincident模式使用SharedArrayBuffer（SAB）实现主线程-Worker间的零拷贝同步通信；Comlink模式使用Service Worker作为中转进行异步通信。两种模式分别有独立的Worker文件和DriveFS实现。

**证据**：
- F-092：initWorker根据workerType选择加载coincident.worker.js或comlink.worker.js
- F-090~F-091：coincident模式下createRemote为remote设置processDriveRequest回调
- F-095~F-104：coincident.worker.ts中SharedBufferContentsAPI通过coincident的proxy同步调用主线程的processDriveRequest
- F-105~F-107：comlink.worker.ts中DriveFS使用browsingContextId通过Service Worker进行文件操作
- F-098：SharedArrayBufferFS.createAPI返回SharedBufferContentsAPI（同步API）
- F-160：SAB模式需要COOP/COEP HTTP头

**反常识**：
- Coincident模式下，Worker线程调用`proxy.processDriveRequest(data)`看起来是普通函数调用，但实际上是通过SharedArrayBuffer跨线程同步调用主线程的DriveContentsProcessor——这意味着WASM程序里的文件IO操作会同步阻塞等待主线程响应，这在JavaScript中通常是不可能的（coincident库利用Atomics实现了这一点）。
- Comlink模式（Service Worker）不需要特殊HTTP头，但stdin需要通过Service Worker路由（F-089~F-092注册stdin handler）。
- workerType不是配置项，而是由cockle的BaseShell根据浏览器能力自动检测选择。

**行动**：
- 部署时如果能设置COOP/COEP头，优先使用SAB模式获得更好性能
- 无法设置跨源头时（如GitHub Pages等静态托管），自动降级到Service Worker模式
- 外部命令实现中文件IO在两种模式下都能工作，无需关心底层传输

## 洞察3：HeadlessShellPool——独立于UI的无头命令执行层

**陈述**：除了用户可见的交互式终端Widget，terminalExecPlugin维护了一个独立的HeadlessShellPool，提供4个编程式命令（execute-shell/start-shell/shutdown-shell/list-shells），允许其他扩展在不打开终端UI的情况下执行shell命令并捕获输出和退出码。

**证据**：
- F-108~F-140：exec.ts实现HeadlessShellPool和4个命令
- F-116~F-119：HeadlessShellPool.create设置PS1=''（空提示符）避免输出污染
- F-124~F-131：runOnSession实现命令执行、超时控制（Promise.race）、输出清理
- F-123：cleanCapturedOutput去除命令回显和\r\n转换
- F-126~F-128：超时或重叠命令的安全防护（timedOut/busy标志）
- F-074~F-078：createHeadlessShell通过LiteTerminalAPIClient创建shell，包含ready超时保护

**反常识**：
- 无头shell的会话独立于终端Widget——list-shells不会列出用户打开的终端（F-47注释说明），反之亦然。两套shell系统共享aliases/environment/externalCommands但各自维护生命周期。
- 超时后的shell被标记为timedOut=true，永久不可复用（F-126、F-147~F-148注释解释：cockle无法中断正在运行的命令，超时后shell状态未知）。这不是bug，是设计决策。
- 一次性shell（不传shellName的execute-shell）在命令执行后自动销毁，而命名shell保持cwd等状态——类似数据库连接池的短连接/长连接模式。
- 输出清理必须去掉echo回来的命令本身（F-113~F-120），因为cockle shell会回显输入的命令，不像exec()系统调用只返回stdout。

**行动**：
- 一次性命令使用execute-shell不传shellName，自动清理
- 需要保持工作目录等状态的多步操作使用start-shell→execute-shell（带shellName）→shutdown-shell
- 命令默认30秒超时，长时间运行命令需显式设置timeout参数
- 注意shell命令的限制：不支持&&/||、命令替换、变量展开（F-167~F-168）

## 洞察4：Python端构建插件——WASM资源的延迟获取与复制机制

**陈述**：Python端TerminalAddon在JupyterLite构建阶段（post_build钩子）运行，负责将cockle所需的WASM文件复制到输出目录。它支持两种模式：使用已安装的cockle包，或临时npm安装cockle到.cockle_temp目录。通过prepare_wasm.js工具获取文件列表后逐个复制。

**证据**：
- F-143~F-151：TerminalAddon.post_build实现
- F-146~F-147：cockleTool路径检查，不存在则执行npm install到.cockle_temp
- F-148~F-150：执行node prepare_wasm.js --list获取文件列表，逐个yield copy action
- F-154：WASM文件目标路径为extensions/@jupyterlite/terminal/static/wasm/
- F-060/F-070：运行时wasmBaseUrl指向上述路径
- F-008：entry-point注册为jupyterlite.addon.v0

**反常识**：
- prepare_wasm.js本身有能力复制WASM文件，但TerminalAddon选择让它只输出文件列表（--list参数），然后自己执行复制——注释说明这是为了"与其他扩展保持一致"（F-037~F-038）。
- .cockle_temp目录是构建时临时依赖，不会出现在最终产物中，避免了对node_modules的硬依赖。
- WASM文件不在npm包的files字段中直接发布，而是构建时从cockle包动态提取——这确保了WASM版本与cockle JS版本一致。

**行动**：
- pip install jupyterlite-terminal后需运行jupyter lite build触发post_build复制WASM
- 自定义部署时确保构建环境有Node.js（post_build中调用node和npm）
- 开发模式下pip install -e "."后需jlpm build构建前端资源

## 知识地图

### 文档分组与学习路径

```
入门路径：
  00-introduction.md       → 01-getting-started.md   → 02-architecture-overview.md
  （终端是什么/功能特性）     （安装/配置/快速使用）     （六插件架构+双Worker模式）

核心概念：
  03-plugin-system.md    → 04-shell-and-worker.md    → 05-headless-exec.md
  （六插件协作机制）         （TerminalShell/双Worker）  （无头命令执行API）

高级主题：
  06-drivefs-and-stdin.md → 07-theme-and-settings.md → 08-build-and-extension.md
  （文件系统/Stdin路由）      （主题同步/设置监听）       （Python构建/扩展注册）
```

### 概念文档覆盖事实映射

| 文档 | 覆盖事实 |
|------|---------|
| 00-introduction | F-001~F-012, F-167~F-171 |
| 01-getting-started | F-004, F-157~F-160 |
| 02-architecture-overview | F-013~F-026, F-050~F-085 |
| 03-plugin-system | F-027~F-049, F-138~F-139 |
| 04-shell-and-worker | F-086~F-107 |
| 05-headless-exec | F-108~F-140 |
| 06-drivefs-and-stdin | F-018~F-019, F-042~F-043, F-090~F-091, F-095~F-107 |
| 07-theme-and-settings | F-044~F-049, F-081 |
| 08-build-and-extension | F-140~F-156 |

### 示例文档规划

| 示例 | 对应概念 | 来源 |
|------|---------|------|
| 01-basic-terminal-usage | 入门/交互式终端 | README基本用法+ui-tests |
| 02-execute-shell-command | 无头命令执行 | README编程式API+exec.spec.ts |
| 03-reusable-shell-session | 状态保持shell | README复用示例+exec.spec.ts |
| 04-custom-command | 扩展外部命令 | registerExternalCommand API |

### references信源文件

| 信源文件 | 对应源码 |
|---------|---------|
| metasource.md | package.json+pyproject.toml（项目元数据/依赖/构建） |
| plugin-source.md | src/index.ts（六插件定义） |
| client-source.md | src/client.ts（LiteTerminalAPIClient） |
| shell-source.md | src/shell.ts+coincident.worker.ts+comlink.worker.ts |
| exec-source.md | src/exec.ts（HeadlessShellPool+命令注册） |
| python-source.md | jupyterlite_terminal/__init__.py+add_on.py |

---

## 可复用设计模式（C阶段沉淀）

从JupyterLite Terminal源码中萃取的可迁移设计模式：

### 模式1：ServiceManager替换模式——浏览器内模拟后端服务

**问题**：JupyterLab/JupyterLite的前端代码期望通过WebSocket连接后端服务（终端、内核等），但浏览器环境没有传统后端。

**Terminal方案**：
- 定义ILiteTerminalAPIClient Token继承标准Terminal.ITerminalAPIClient
- 使用mock-socket库在浏览器内创建WebSocketServer，拦截WebSocket连接
- 提供自定义TerminalManager替换默认实现
- 多个插件分层提供客户端连接、文件系统、stdin、主题等能力

**迁移要点**：类似依赖倒置原则——前端依赖抽象接口（ITerminalAPIClient/ITerminalManager），通过Lumino Token注入不同实现。mock-socket可用于任何需要拦截WebSocket的浏览器端场景。

### 模式2：双传输层自动选择——SAB同步与Service Worker异步

**问题**：Web Worker与主线程通信需要支持不同浏览器环境——有跨源头时用SharedArrayBuffer（需要COOP/COEP），无跨源头时降级到Service Worker。

**Terminal方案**：
- TerminalShell.initWorker根据workerType选择加载不同Worker文件
- Coincident模式：coincident库+Atomics实现同步函数调用代理
- Comlink模式：comlink库+Service Worker实现异步消息传递
- 上层Shell接口统一，两种模式对调用方透明

**迁移要点**：将传输层抽象为createRemote/initWorker工厂方法，具体实现延迟到子类。Worker文件作为独立entry point打包。

### 模式3：HeadlessShellPool——UI与会话分离的命令执行池

**问题**：需要在不打开UI组件的情况下编程式执行命令，同时支持一次性和可复用会话。

**Terminal方案**：
- HeadlessShellPool管理shell生命周期（创建/获取/关闭/列表）
- 一次性shell（不传shellName）：自动创建→执行→销毁
- 命名shell（传shellName）：创建后复用，保持cwd等状态
- 超时shell标记为不可复用（timedOut=true）防止状态污染
- PS1=''空提示符避免输出污染
- cleanCapturedOutput去除命令回显，模拟exec()语义

**迁移要点**：区分交互式UI会话和编程式会话池；超时资源不可复用是安全的保守策略；输出清理是shell场景特有的需求。
