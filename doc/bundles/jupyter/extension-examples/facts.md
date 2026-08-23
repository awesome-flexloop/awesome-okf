---
okf_version: '0.2'
generated: '2026-08-22'
tags:
- jupyter
- jupyterlab
- extension
- examples
sources:
- ../../../../../external/libs/jupyter/extension-examples/README.md
- ../../../../../external/libs/jupyter/extension-examples/lerna.json
- ../../../../../external/libs/jupyter/extension-examples/environment.yml
- ../../../../../external/libs/jupyter/extension-examples/hello-world/package.json
- ../../../../../external/libs/jupyter/extension-examples/hello-world/pyproject.toml
- ../../../../../external/libs/jupyter/extension-examples/hello-world/install.json
- ../../../../../external/libs/jupyter/extension-examples/hello-world/jupyterlab_examples_hello_world/__init__.py
- ../../../../../external/libs/jupyter/extension-examples/hello-world/src/index.ts
- ../../../../../external/libs/jupyter/extension-examples/commands/src/index.ts
- ../../../../../external/libs/jupyter/extension-examples/widgets/src/index.ts
- ../../../../../external/libs/jupyter/extension-examples/mimerenderer/src/index.ts
- ../../../../../external/libs/jupyter/extension-examples/server-extension/jupyterlab_examples_server/handlers.py
- ../../../../../external/libs/jupyter/extension-examples/server-extension/jupyter-config/server-config/jupyterlab_examples_server.json
- ../../../../../external/libs/jupyter/extension-examples/server-extension/src/handler.ts
- ../../../../../external/libs/jupyter/extension-examples/server-extension/src/index.ts
- ../../../../../external/libs/jupyter/extension-examples/settings/src/index.ts
- ../../../../../external/libs/jupyter/extension-examples/state/src/index.ts
- ../../../../../external/libs/jupyter/extension-examples/signals/src/index.ts
- ../../../../../external/libs/jupyter/extension-examples/react-widget/src/index.ts
- ../../../../../external/libs/jupyter/extension-examples/launcher/src/index.ts
- ../../../../../external/libs/jupyter/extension-examples/main-menu/src/index.ts
- ../../../../../external/libs/jupyter/extension-examples/toolbar-button/src/index.ts
- ../../../../../external/libs/jupyter/extension-examples/toolbar-button/schema/plugin.json
- ../../../../../external/libs/jupyter/extension-examples/notifications/src/index.ts
- ../../../../../external/libs/jupyter/extension-examples/completer/src/index.ts
- ../../../../../external/libs/jupyter/extension-examples/datagrid/src/index.ts
- ../../../../../external/libs/jupyter/extension-examples/toparea-text-widget/src/index.ts
- ../../../../../external/libs/jupyter/extension-examples/documents/src/index.ts
- ../../../../../external/libs/jupyter/extension-examples/kernel-messaging/src/index.ts
- ../../../../../external/libs/jupyter/extension-examples/hello-world/ui-tests/jupyter_server_test_config.py
- ../../../../../external/libs/jupyter/extension-examples/hello-world/ui-tests/package.json
- ../../../../../external/libs/jupyter/extension-examples/hello-world/ui-tests/playwright.config.js
type: Facts
title: extension-examples 源码事实清单
---

# extension-examples 事实清单

> JupyterLab 扩展示例教程集，通过 ~26 个独立示例覆盖 JupyterLab 4.0+ 各类扩展点（commands/widgets/MIME renderer/server extension/settings/state/signals/kernel messaging/completer/datagrid/notifications 等）。

## 仓库概览

- F-001: README.md:47 — 仓库目标：以简短教程系列展示如何为 JupyterLab 开发扩展（"show how to develop extensions for JupyterLab, presented as short tutorial series"）
- F-002: README.md:87 — 示例面向 JupyterLab 4.0 或更高版本（"The examples currently target JupyterLab 4.0 or later"）
- F-003: README.md:89-95 — 旧版本分支（1.x/2.x/3.x）不再更新（"the 1.x, 2.x and 3.x branches are not updated anymore"）
- F-004: README.md:103-132 — 包含 26 个示例分类：cell-toolbar、codemirror-extension、commands、command-palette、completer、contentheader、context-menu、custom-log-console、datagrid、dual compatibility（toparea-text-widget/shout-button-message/clap-button-message）、documents、hello-world、kernel-messaging、kernel-output、launcher、log-messages、main-menu、metadata-form、mimerenderer、notifications、react-widget、server-extension、settings、signals、state、toolbar-button、widgets
- F-005: README.md:134-139 — 每个示例包含：功能说明、截图/录屏、所用 JupyterLab API 和扩展点列表、带代码片段的内部工作原理解释
- F-006: README.md:502 — 使用 embedme 工具将代码片段嵌入 Markdown README（"We are using embedme to embed code snippets into the markdown READMEs"）

## Monorepo 管理

- F-007: lerna.json:2-3 — 使用 Lerna 管理 monorepo，npmClient 设为 jlpm，版本策略为 independent（各包独立版本号）
- F-008: environment.yml:1-10 — Conda 环境依赖：jupyterlab >=4.3.0、nodejs=22、pytest、pytest-check-links、pytest-jupyter >=0.6.0、python=3，channel 为 conda-forge
- F-009: README.md:441-446 — 批量构建命令：jlpm → jlpm build-ext → jlpm install-py → jlpm install-ext → jupyter lab
- F-010: README.md:449-453 — 批量重建：jlpm build-ext；清理 lib 目录：jlpm clean-ext
- F-011: README.md:508-510 — 模板更新脚本：./scripts/update-template.sh（从 extension-template 更新后修复冲突）

## 通用项目结构（每个示例）

- F-012: hello-world/ — 每个示例具有统一结构：src/（TypeScript 源码）、style/（CSS/图标）、ui-tests/（Playwright 测试）、pyproject.toml、package.json、tsconfig.json、install.json、setup.py、LICENSE
- F-013: hello-world/package.json:93-96 — package.json 中 `"jupyterlab": { "extension": true, "outputDir": "..." }` 声明 JupyterLab 扩展及输出目录
- F-014: hello-world/package.json:16-20 — npm files 字段包含 lib/**/*.{d.ts,...js,...}、style/**/*.{css,...}、src/**/*.{ts,tsx}
- F-015: hello-world/package.json:21-23 — main 入口为 lib/index.js，types 为 lib/index.d.ts，style 为 style/index.css
- F-016: hello-world/package.json:85-88 — sideEffects 声明 style/*.css 和 style/index.js，styleModule 为 style/index.js
- F-017: hello-world/pyproject.toml:1-3 — Python 构建后端使用 hatchling + hatch-nodejs-version + jupyterlab>=4.0.0,<5
- F-018: hello-world/pyproject.toml:29-33 — Hatch version source 为 nodejs，metadata hooks 从 package.json 读取 description/authors/urls/keywords
- F-019: hello-world/pyproject.toml:39-41 — Wheel shared-data 将 labextension 目录映射到 share/jupyter/labextensions/@jupyterlab-examples/<name>
- F-020: hello-world/pyproject.toml:46-63 — 使用 hatch-jupyter-builder，构建命令 build:prod（npm=jlpm），editable 模式用 install:extension
- F-021: hello-world/install.json:1-5 — install.json 指定 packageManager 为 python，packageName 为 Python 包名，含卸载说明
- F-022: hello-world/jupyterlab_examples_hello_world/__init__.py:12-16 — Python 包 `_jupyter_labextension_paths()` 返回 `[{"src": "labextension", "dest": "@jupyterlab-examples/<name>"}]`
- F-023: hello-world/jupyterlab_examples_hello_world/__init__.py:1-9 — 版本导入 fallback：优先从 _version 导入，失败则 warn 并设为 "dev"
- F-024: hello-world/package.json:28-53 — 标准 npm scripts：build（build:lib + build:labextension:dev）、build:prod、build:labextension、build:lib（tsc --sourceMap）、clean、watch（tsc -w + jupyter labextension watch）
- F-025: hello-world/package.json:58-83 — devDependencies 包含 @jupyterlab/builder、@jupyterlab/testutils、typescript ~5.8.0、eslint、prettier、stylelint、jest、yjs 等
- F-026: hello-world/package.json:106-158 — ESLint 配置：extends recommended + @typescript-eslint + prettier，强制 interface 命名 I 前缀（PascalCase + I[A-Z]）、eqeqeq、curly all、prefer-arrow-callback
- F-027: hello-world/package.json:160-173 — Prettier 配置：singleQuote、trailingComma none、arrowParens avoid、package.json tabWidth 4
- F-028: hello-world/package.json:174-190 — Stylelint 配置：extends recommended + standard + csstree-validator，selector-class-pattern 为 kebab-case

## Hello World 示例（最小前端扩展）

- F-029: hello-world/src/index.ts:1-4 — 导入 JupyterFrontEnd 和 JupyterFrontEndPlugin 来自 @jupyterlab/application
- F-030: hello-world/src/index.ts:9-16 — 最小 plugin 对象：id、description、autoStart: true、activate 回调接收 JupyterFrontEnd 实例，console.log 输出 app 对象
- F-031: hello-world/src/index.ts:18 — export default plugin（默认导出 plugin 对象）

## Commands 示例

- F-032: commands/src/index.ts:9-12 — extension 定义：id 为 'commands'，autoStart: true
- F-033: commands/src/index.ts:14-29 — app.commands.addCommand() 注册命令，包含 label、caption、execute 回调；execute 接收 args 参数
- F-034: commands/src/index.ts:32-36 — commands.execute() 可在 activate 中主动调用命令，通过 .catch() 处理错误

## Widgets 示例（自定义 Lumino Widget）

- F-035: widgets/src/index.ts:6-10 — 导入 ICommandPalette、@lumino/messaging Message、@lumino/widgets Widget
- F-036: widgets/src/index.ts:15-19 — plugin requires: [ICommandPalette]，声明对 Command Palette 的依赖
- F-037: widgets/src/index.ts:20-33 — activate 解构 app.commands 和 app.shell；addCommand 创建 widget 并通过 shell.add(widget, 'main') 添加到主区域
- F-038: widgets/src/index.ts:32 — palette.addItem({ command, category: 'Extension Examples' }) 添加到命令面板
- F-039: widgets/src/index.ts:38-45 — ExampleWidget 继承 Widget，在构造函数中 addClass、设置 id、title.label、title.closable
- F-040: widgets/src/index.ts:52-61 — handleEvent 方法实现 EventListener 接口，通过 switch(event.type) 分发 pointerenter/pointerleave
- F-041: widgets/src/index.ts:68-76 — onAfterAttach 生命周期方法：DOM 挂载后通过 addEventListener 监听事件，推荐在此处绑定 DOM 事件
- F-042: widgets/src/index.ts:83-87 — onBeforeDetach 生命周期方法：DOM 卸载前 removeEventListener 清理事件监听
- F-043: widgets/src/index.ts:92-108 — 私有回调方法：_onEventClick（alert）、_onMouseEnter（橙色背景）、_onMouseLeave（aliceblue 背景）

## MIME Renderer 示例

- F-044: mimerenderer/src/index.ts:1-5 — 导入 IRenderMime 来自 @jupyterlab/rendermime-interfaces，Widget 来自 @lumino/widgets
- F-045: mimerenderer/src/index.ts:10 — MIME 类型常量：const MIME_TYPE = 'video/mp4'
- F-046: mimerenderer/src/index.ts:20-31 — VideoWidget 继承 Widget 并实现 IRenderMime.IRenderer 接口；构造函数创建 <video controls> 元素
- F-047: mimerenderer/src/index.ts:36-41 — renderModel 方法从 model.data 读取 MIME 数据，设置 video.src 为 base64 data URI，返回 Promise.resolve()
- F-048: mimerenderer/src/index.ts:50-54 — rendererFactory：safe: true、mimeTypes: [MIME_TYPE]、createRenderer 返回 VideoWidget 实例
- F-049: mimerenderer/src/index.ts:59-84 — extension 类型为 IRenderMime.IExtension（非 JupyterFrontEndPlugin），包含 id、rendererFactory、rank、dataType、fileTypes（含 extensions/fileFormat/icon/mimeTypes）、documentWidgetFactoryOptions
- F-050: mimerenderer/src/index.ts:65-75 — fileTypes 定义：name 'mp4'、extensions ['.mp4']、fileFormat 'base64'、icon 使用 SVG 字符串
- F-051: mimerenderer/src/index.ts:77-83 — documentWidgetFactoryOptions 指定 name、primaryFileType、modelName 'base64'、defaultFor

## Server Extension 示例（前后端混合）

- F-052: server-extension/jupyterlab_examples_server/handlers.py:4-7 — 后端基于 jupyter_server.base.handlers.APIHandler 和 tornado
- F-053: server-extension/jupyterlab_examples_server/handlers.py:10-18 — RouteHandler 继承 APIHandler，GET 方法带 @tornado.web.authenticated 装饰器，返回 JSON 数据
- F-054: server-extension/jupyterlab_examples_server/handlers.py:20-25 — POST 方法通过 self.get_json_body() 获取输入，返回个性化问候 JSON
- F-055: server-extension/jupyterlab_examples_server/handlers.py:28-35 — setup_handlers() 使用 url_path_join 拼接 base_url（兼容 JupyterHub），通过 web_app.add_handlers 注册路由
- F-056: server-extension/jupyterlab_examples_server/handlers.py:38-44 — 静态文件服务：StaticFileHandler 挂载 public 目录，支持 JLAB_SERVER_EXAMPLE_STATIC_DIR 环境变量覆盖
- F-057: server-extension/jupyter-config/server-config/jupyterlab_examples_server.json:1-7 — Jupyter Server 配置通过 JSON 文件声明 jpserver_extensions，启用 jupyterlab_examples_server
- F-058: server-extension/src/handler.ts:1-4 — 前端使用 URLExt（@jupyterlab/coreutils）和 ServerConnection（@jupyterlab/services）与后端通信
- F-059: server-extension/src/handler.ts:12-46 — requestAPI 泛型函数：通过 ServerConnection.makeSettings() 获取配置，URLExt.join 拼接 URL，ServerConnection.makeRequest 发送请求，处理 JSON 解析和错误
- F-060: server-extension/src/handler.ts:20 — API Namespace 硬编码为 'jupyterlab-examples-server'
- F-061: server-extension/src/handler.ts:41-43 — 非 ok 响应抛出 ServerConnection.ResponseError
- F-062: server-extension/src/index.ts:6-11 — 导入 IFrame（@jupyterlab/apputils）、PageConfig（@jupyterlab/coreutils）、ILauncher（@jupyterlab/launcher）
- F-063: server-extension/src/index.ts:29-30 — plugin optional: [ILauncher]（可选依赖）、requires: [ICommandPalette]（必需依赖）
- F-064: server-extension/src/index.ts:40-41 — 注释警告：activate 中避免 await 以免延迟应用启动（"Try avoiding awaiting in the activate function"）
- F-065: server-extension/src/index.ts:42-50 — activate 中通过 .then()/.catch() 异步调用 requestAPI（非阻塞）
- F-066: server-extension/src/index.ts:94-103 — IFrameWidget 继承 IFrame，通过 PageConfig.getBaseUrl() 获取 baseUrl，设置 url 指向 server 提供的静态页面
- F-067: server-extension/src/index.ts:82-88 — optional 依赖需 null 检查：if (launcher) { launcher.add({...}) }

## Settings 示例

- F-068: settings/src/index.ts:6 — ISettingRegistry 来自 @jupyterlab/settingregistry
- F-069: settings/src/index.ts:8 — PLUGIN_ID 常量（必须与 package.json 中 jupyterlab 配置的 id 匹配）
- F-070: settings/src/index.ts:19 — plugin requires: [ISettingRegistry]
- F-071: settings/src/index.ts:30-38 — loadSetting 函数通过 setting.get('key').composite 读取设置值（composite 合并用户/系统默认值）
- F-072: settings/src/index.ts:42-43 — Promise.all([app.restored, settings.load(PLUGIN_ID)]) 等待应用恢复和设置加载完成
- F-073: settings/src/index.ts:48 — setting.changed.connect(loadSetting) 通过 Signal 监听设置变更
- F-074: settings/src/index.ts:55-58 — setting.set('flag', !flag) 和 setting.set('limit', limit + 1) 程序化修改设置
- F-075: settings/src/index.ts:52 — commands.addCommand 中 isToggled: () => flag 用于命令切换状态显示

## State 示例（状态持久化）

- F-076: state/src/index.ts:6 — IStateDB 来自 @jupyterlab/statedb
- F-077: state/src/index.ts:18 — plugin requires: [IStateDB]
- F-078: state/src/index.ts:23-25 — app.restored.then(() => state.fetch(PLUGIN_ID)) 在应用恢复后获取持久化状态
- F-079: state/src/index.ts:28-30 — state.fetch 返回值可能为 null，需做存在性检查
- F-080: state/src/index.ts:34-38 — InputDialog.getItem 显示选择对话框，current 设置默认选项索引
- F-081: state/src/index.ts:47 — state.save(PLUGIN_ID, { option }) 保存状态到 StateDB
- F-082: state/src/index.ts:7 — ReadonlyJSONObject 来自 @lumino/coreutils，用于类型安全的 JSON 值读取

## Signals 示例（Widget 间通信）

- F-083: signals/src/index.ts:7 — ITranslator 来自 @jupyterlab/translation（国际化支持）
- F-084: signals/src/index.ts:26 — plugin requires: [ICommandPalette, ITranslator]
- F-085: signals/src/index.ts:25 — plugin optional: [ILauncher]
- F-086: signals/src/index.ts:47 — translator.load('jupyterlab') 加载翻译 bundle
- F-087: signals/src/index.ts:73 — trans.__('label') 包装可翻译字符串
- F-088: signals/src/index.ts:44 — app.serviceManager 获取服务管理器（kernel/session 等）

## React Widget 示例

- F-089: react-widget/src/index.ts:5 — MainAreaWidget 来自 @jupyterlab/apputils（包装 React 组件的标准容器）
- F-090: react-widget/src/index.ts:7 — reactIcon 来自 @jupyterlab/ui-components（内置 React 图标）
- F-091: react-widget/src/index.ts:24 — plugin optional: [ILauncher]
- F-092: react-widget/src/index.ts:32 — icon: args => (args['isPalette'] ? undefined : reactIcon) 条件性显示图标（面板中不显示图标）
- F-093: react-widget/src/index.ts:34-35 — 创建 CounterWidget React 组件，包装为 MainAreaWidget<CounterWidget>({ content })
- F-094: react-widget/src/index.ts:38 — app.shell.add(widget, 'main') 添加到主区域

## Launcher 示例

- F-095: launcher/src/index.ts:7 — IFileBrowserFactory 来自 @jupyterlab/filebrowser
- F-096: launcher/src/index.ts:8 — LabIcon 来自 @jupyterlab/ui-components，用于自定义图标
- F-097: launcher/src/index.ts:23 — plugin requires: [IFileBrowserFactory]
- F-098: launcher/src/index.ts:33-36 — new LabIcon({ name, svgstr }) 从 SVG 字符串创建自定义图标
- F-099: launcher/src/index.ts:39-44 — label 和 icon 支持 args 条件渲染：args['isPalette'] 时使用不同 label 和隐藏图标
- F-100: launcher/src/index.ts:48-49 — 通过 browserFactory.tracker.currentWidget?.model.path 获取当前文件浏览器目录
- F-101: launcher/src/index.ts:52-56 — commands.execute('docmanager:new-untitled', { path, type: 'file', ext: 'py' }) 调用内置命令创建新文件
- F-102: launcher/src/index.ts:59-62 — commands.execute('docmanager:open', { path, factory: 'Editor' }) 用指定工厂打开文件
- F-103: launcher/src/index.ts:68-72 — launcher.add({ command, category, rank: 1 }) rank 控制启动器中排序
- F-104: launcher/src/index.ts:77-81 — palette.addItem 可传 args: { isPalette: true } 给命令 execute

## Main Menu 示例

- F-105: main-menu/src/index.ts:15 — plugin requires: [ICommandPalette]
- F-106: main-menu/src/index.ts:36-40 — palette.addItem 可传 args: { origin: 'from the palette' } 传递上下文参数到 execute 回调

## Toolbar Button 示例（声明式工具栏按钮）

- F-107: toolbar-button/src/index.ts:6-14 — plugin activate 为空函数——按钮完全通过 schema 声明式注册
- F-108: toolbar-button/schema/plugin.json:2-8 — "jupyter.lab.toolbars" 键声明式添加工具栏按钮：Notebook 工具栏添加 "clear-all-outputs" 按钮，绑定 notebook:clear-all-cell-outputs 命令
- F-109: toolbar-button/schema/plugin.json:10-14 — schema 同时是 JSON Schema，定义 settings 的 type/properties/additionalProperties

## Notifications 示例

- F-110: notifications/src/index.ts:6 — Notification 来自 @jupyterlab/apputils
- F-111: notifications/src/index.ts:8 — PromiseDelegate 来自 @lumino/coreutils（可外部 resolve/reject 的 Promise 包装器）
- F-112: notifications/src/index.ts:22 — Notification.success(message) 显示成功通知
- F-113: notifications/src/index.ts:25-30 — Notification.error(message, { actions: [...], autoClose: 3000 }) 错误通知可带操作按钮和自动关闭时间
- F-114: notifications/src/index.ts:33-41 — new PromiseDelegate() + setTimeout 模拟异步任务
- F-115: notifications/src/index.ts:42-52 — Notification.promise(promise, { pending, success, error }) 为异步任务显示进度通知，success/error 支持函数动态生成消息

## Completer 示例（自定义补全）

- F-116: completer/src/index.ts:5 — ICompletionProviderManager 来自 @jupyterlab/completer
- F-117: completer/src/index.ts:6 — INotebookTracker 来自 @jupyterlab/notebook
- F-118: completer/src/index.ts:17 — plugin requires: [ICompletionProviderManager, INotebookTracker]
- F-119: completer/src/index.ts:18 — activate 为 async 函数（异步激活）
- F-120: completer/src/index.ts:23 — completionManager.registerProvider(new CustomCompleterProvider()) 注册自定义补全提供者

## Datagrid 示例

- F-121: datagrid/src/index.ts:14 — DataGrid、DataModel 来自 @lumino/datagrid
- F-122: datagrid/src/index.ts:16 — StackedPanel 来自 @lumino/widgets
- F-123: datagrid/src/index.ts:26 — plugin requires: [ICommandPalette, ITranslator]
- F-124: datagrid/src/index.ts:50-66 — DataGridPanel 继承 StackedPanel，构造函数中创建 LargeDataModel 和 DataGrid，设置 grid.dataModel = model
- F-125: datagrid/src/index.ts:72-92 — LargeDataModel 继承 DataModel，实现 rowCount（body 1万亿行）、columnCount（body 1万亿列）、data 方法，演示虚拟滚动大数据集
- F-126: datagrid/src/index.ts:73-74 — rowCount 区分 'body' 区域和其他区域（row-header），body 返回超大值启用虚拟滚动

## Top Area Widget 示例

- F-127: toparea-text-widget/src/index.ts:6 — DOMUtils 来自 @jupyterlab/apputils（DOM ID 生成工具）
- F-128: toparea-text-widget/src/index.ts:25-29 — 创建 DOM 元素，用 new Widget({ node }) 包装已有 DOM 节点
- F-129: toparea-text-widget/src/index.ts:30 — DOMUtils.createDomID() 生成唯一 DOM ID
- F-130: toparea-text-widget/src/index.ts:34 — app.shell.add(widget, 'top', { rank: 1000 }) 添加到顶部区域，rank 控制位置排序

## Documents 示例（协作文档）

- F-131: documents/src/index.ts:1 — ICollaborativeDrive 来自 @jupyter/collaborative-drive（可选协作驱动）
- F-132: documents/src/index.ts:6 — ILayoutRestorer 来自 @jupyterlab/application（布局恢复）
- F-133: documents/src/index.ts:9 — WidgetTracker、IWidgetTracker 来自 @jupyterlab/apputils
- F-134: documents/src/index.ts:11 — Token 来自 @lumino/coreutils（用于定义可注入的服务 Token）
- F-135: documents/src/index.ts:23-25 — export const IExampleDocTracker = new Token<IWidgetTracker<ExampleDocWidget>>('exampleDocTracker') 导出 Token 供其他扩展依赖
- F-136: documents/src/index.ts:35 — plugin requires: [ILayoutRestorer]
- F-137: documents/src/index.ts:36 — plugin optional: [ICollaborativeDrive]
- F-138: documents/src/index.ts:37 — plugin provides: IExampleDocTracker（声明提供此 Token）
- F-139: documents/src/index.ts:46 — new WidgetTracker<ExampleDocWidget>({ namespace }) 创建 widget 追踪器
- F-140: documents/src/index.ts:49-56 — restorer.restore(tracker, { command, args, name }) 配置布局恢复：command 指定恢复命令，args 从 widget 提取参数，name 生成唯一标识
- F-141: documents/src/index.ts:59-66 — app.docRegistry.addFileType() 注册自定义文件类型：name、displayName、mimeTypes、extensions、fileFormat、contentType
- F-142: documents/src/index.ts:71-79 — drive 存在时注册 sharedModelFactory（协作功能可选）
- F-143: documents/src/index.ts:82-83 — app.docRegistry.addModelFactory(modelFactory) 注册文档模型工厂
- F-144: documents/src/index.ts:87-92 — new ExampleWidgetFactory({ name, modelName, fileTypes, defaultFor }) 创建 widget 工厂
- F-145: documents/src/index.ts:95-101 — widgetFactory.widgetCreated.connect() 通过 Signal 连接 widget 创建事件，添加到 tracker 并监听 pathChanged

## Kernel Messaging 示例

- F-146: kernel-messaging/src/index.ts:47 — const manager = app.serviceManager 获取服务管理器（用于 kernel/session 交互）
- F-147: kernel-messaging/src/index.ts:65-68 — createPanel 为 async 函数，创建 ExamplePanel 并添加到主区域

## 测试

- F-148: hello-world/ui-tests/ — 每个示例包含 ui-tests/ 目录，使用 Playwright 进行集成测试
- F-149: README.md:523-526 — UI 测试使用 Playwright 模拟用户操作验证扩展行为，测试定义在各示例的 ui-tests 子文件夹中
- F-150: hello-world/ui-tests/jupyter_server_test_config.py — UI 测试包含 Jupyter Server 测试配置
- F-151: README.md:518-522 — 自动化测试检查：配置一致性（与 hello-world 对比）、TypeScript lint、JupyterLab 安装验证（browser_check）、集成测试

## UI 测试配置

- F-152: hello-world/ui-tests/playwright.config.js — Playwright 测试配置文件
- F-153: hello-world/ui-tests/package.json — UI 测试有独立的 package.json（独立依赖管理）

## 开发流程

- F-154: README.md:463-469 — 单示例安装：cd 示例目录 → touch yarn.lock（Yarn 3 workspace 规则）→ pip install -e . → jupyter labextension develop . --overwrite
- F-155: README.md:487-500 — 开发模式：终端1运行 jlpm watch（tsc -w + labextension watch），终端2运行 jupyter lab，修改源码自动重编译，刷新浏览器即可
