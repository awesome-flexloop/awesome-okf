# p5-kernel 源码事实清单

> R阶段（事实采集）产出的零推测事实清单，每个事实均可通过源码路径验证。

## 项目元数据

- **F-001**: 根包名 `@jupyterlite/p5-kernel-root`，私有 monorepo，版本 `0.4.0-a2`
- **F-002**: 使用 yarn workspaces + lerna（independent 版本模式），workspaces 路径 `packages/*`
- **F-003**: 许可证 BSD-3-Clause，仓库 https://github.com/jupyterlite/p5-kernel
- **F-004**: npm 客户端配置为 `jlpm`（JupyterLab 自带的 yarn）
- **F-005**: 包含两个子包：`@jupyterlite/p5-kernel`（内核，0.4.0-alpha.2）和 `@jupyterlite/p5-kernel-extension`（扩展，0.4.0-alpha.2）
- **F-006**: Python 包名 `jupyterlite-p5-kernel`，requires-python >=3.10，使用 hatchling 构建
- **F-007**: Python 包无运行时依赖（dependencies = []）

## npm 依赖

- **F-008**: `@jupyterlite/p5-kernel` 依赖 `@jupyterlab/nbformat: ^4.5.0`, `@jupyterlite/javascript-kernel: ^0.4.0-alpha.3`, `@jupyterlite/services: ^0.7.0`
- **F-009**: `@jupyterlite/p5-kernel` devDependencies 包含 `@types/p5: ^1.7.7`, `typescript: ~5.0.2`
- **F-010**: `@jupyterlite/p5-kernel-extension` 依赖 `@jupyterlab/application: ^4.5.0`, `@jupyterlite/p5-kernel: ^0.4.0-alpha.2`, `@jupyterlite/services: ^0.7.0`
- **F-011**: 扩展的 `sharedPackages` 配置中 `@jupyterlite/services` 标记为 bundled=false, singleton=true

## 源码结构

- **F-012**: `packages/p5-kernel/src/index.ts` 仅 re-export `./kernel` 和 `./executor`
- **F-013**: `P5Kernel` 类继承自 `JavaScriptKernel`（来自 `@jupyterlite/javascript-kernel`）
- **F-014**: `P5Executor` 类继承自 `JavaScriptExecutor`（来自 `@jupyterlite/javascript-kernel`）
- **F-015**: `src/p5-docs.ts` 是自动生成文件，由 `scripts/generate-p5-docs.mjs` 构建前生成

## P5Kernel 类

- **F-016**: 构造函数强制设置 `runtime: 'iframe'`，并使用 `P5Executor` 作为 `executorFactory`
- **F-017**: `IOptions` 接口扩展 `JavaScriptKernel.IOptions`，必填 `p5Url: string`，可选 `runtime?: 'iframe'`
- **F-018**: `_displayId` 初始化为 `this.id`（kernel id）
- **F-019**: `_bootstrap` 代码通过动态 `import('${p5Url}')` 加载 p5.js，创建 `window.__globalP5 = new p5()`
- **F-020**: `kernelInfoRequest()` 返回 implementation='p5.js', language_info.name='p5js', codemirror_mode.name='javascript', file_extension='.js', pygments_lexer='javascript', protocol_version='5.3'
- **F-021**: `executeRequest()` 先检查 `%show` magic，再调用 `super.executeRequest()`，然后注册代码和提取 imports，最后更新已有 display
- **F-022**: `onRuntimeReady()` 断言 runtime==='iframe'，获取 executor，创建 codeRegistry，执行 bootstrap
- **F-023**: `onRuntimeReady()` 中 runtime 不为 iframe 时抛出 `Error('P5Kernel requires iframe runtime')`
- **F-024**: 私有字段：`_displayId: string`, `_bootstrap: string`, `_codeRegistry?: ICodeRegistry`, `_imports: IImportInfo[]`, `_parentHeaders: IHeader[]`, `_p5Executor?: P5Executor`
- **F-025**: 非 magic 代码通过 `_p5Executor.registerCode(code, this._codeRegistry)` 注册到 CodeRegistry
- **F-026**: imports 通过 `executor.extractImports(code)` 提取，按 `source` 去重存入 `_imports`

## %show Magic

- **F-027**: `%show` 正则为 `/^%show(?: (.+)\s+(.+))?\s*$/`，捕获 width 和 height
- **F-028**: 默认 width='100%', height='400px'
- **F-029**: `_magics()` 生成 script：bootstrap.then(async () => { importCode; combinedCode; window.__globalP5._start(); }).catch()
- **F-030**: combinedCode 来自 `_p5Executor.generateCodeFromRegistry(this._codeRegistry)`，基于 AST 去重
- **F-031**: iframe srcdoc 为 `<body style="overflow: hidden; margin: 0; padding: 0;"><script>${script}</script></body>`
- **F-032**: srcdoc 进行 HTML 转义：&→&amp;, '→&#39;, "→&quot;
- **F-033**: 输出格式为 `<iframe width="${width}" height="${height}" frameborder="0" srcdoc="${escapedSrcdoc}"></iframe>`
- **F-034**: `%show` 执行时将 parentHeader 推入 `_parentHeaders` 数组
- **F-035**: 每次普通代码执行后遍历 `_parentHeaders` 调用 `updateDisplayData` 更新所有已有 display

## P5Executor 类

- **F-036**: `getMimeBundle()` 检测 value.constructor?.name === 'p5.Graphics' 且 value.elt 存在
- **F-037**: p5.Graphics 渲染：canvas.toDataURL('image/png') → 提取 base64 → 返回 { 'image/png': base64, 'text/plain': `p5.Graphics(${width}x${height})` }
- **F-038**: p5.Graphics 异常时 fallback 为 { 'text/plain': 'p5.Graphics' }
- **F-039**: 非 p5.Graphics 对象调用 super.getMimeBundle(value)
- **F-040**: `getBuiltinDocumentation()` 从 `P5_DOCS[expression]` 查找，找不到则 fallback 到 super

## P5_DOCS 生成

- **F-041**: `generate-p5-docs.mjs` 使用 TypeScript Compiler API 解析 `@types/p5/global.d.ts`
- **F-042**: 遍历 FunctionDeclaration 提取函数名、JSDoc 第一句话、参数列表
- **F-043**: 重载函数保留参数最多的版本
- **F-044**: 参数中 questionToken 或 initializer 标记为可选（方括号包裹）
- **F-045**: 遍历 VariableStatement 提取全局变量（mouseX, width, frameCount 等）的 JSDoc
- **F-046**: 输出按字母序排序，格式为 `key: 'description. Usage: signature'`
- **F-047**: 构建脚本顺序：`generate:docs`（node scripts/generate-p5-docs.mjs）→ `tsc -b`
- **F-048**: clean 命令删除 `src/p5-docs.ts`

## 扩展注册

- **F-049**: 插件 id 为 `'@jupyterlite/p5-kernel-extension:kernel'`，autoStart=true，requires=[IKernelSpecs]
- **F-050**: 默认 p5 CDN URL 为 `https://cdn.jsdelivr.net/npm/p5@1.9.0/lib/p5.js`
- **F-051**: p5Url 通过 `PageConfig.getOption('p5Url')` 获取，未设置则使用默认 CDN
- **F-052**: 本地 URL 通过 `URLExt.join(window.location.origin, url)` 拼接
- **F-053**: 注册的 kernel spec: name='p5js', display_name='p5.js', language='javascript', interrupt_mode='message'
- **F-054**: logo-64x64 使用从 `../style/icons/p5js.png` 导入的 PNG
- **F-055**: create 工厂返回 `new P5Kernel({...options, p5Url})`
- **F-056**: 扩展标记 `jupyterlab.extension: true` 和 `jupyterlite.liteExtension: true`
- **F-057**: labextension 输出目录为 `../../jupyterlite_p5_kernel/labextension`
- **F-058**: PNG 模块声明在 `declarations.d.ts` 中

## Python 包

- **F-059**: `_jupyter_labextension_paths()` 返回 `[{"src": "labextension", "dest": data["name"]}]`
- **F-060**: 版本号通过 hatch-nodejs-version 从 package.json 读取
- **F-061**: hatch-jupyter-builder 的 build_cmd 为 `build:prod`，npm client 为 `jlpm`
- **F-062**: wheel shared-data 将 labextension 安装到 `share/jupyter/labextensions/@jupyterlite/p5-kernel-extension/`
- **F-063**: install.json 指定 packageManager=python, packageName=jupyterlite_p5_kernel

## 示例 Notebooks

- **F-064**: 提供 7 个示例 notebook：intro, particle-system, flow-field, interactive-circles, recursive-tree, spiral-galaxy, external-packages
- **F-065**: intro.ipynb 展示基础的 setup/draw + %show + 实时调参工作流
- **F-066**: particle-system.ipynb 展示粒子系统（对象数组、边界反弹、HSB颜色、拖尾）
- **F-067**: external-packages.ipynb 展示 ES import 语法（canvas-confetti、dayjs），支持默认/命名/命名空间/GitHub/URL 导入
