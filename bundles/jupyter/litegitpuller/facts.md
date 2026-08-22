# litegitpuller 事实清单（R阶段采集）

> 零推测原则：以下事实均从源码中直接提取，不含推断性表述。每个事实指向具体源码位置。

## 项目元数据

F-001: npm 包名为 `@jupyterlite/litegitpuller`，版本 `0.3.0`，定义于 `package.json:2-3`
F-002: Python 包名为 `litegitpuller`，要求 Python `>=3.8`，定义于 `pyproject.toml:6-9`
F-003: 许可证为 BSD-3-Clause，定义于 `package.json:14`
F-004: 构建系统使用 hatchling（`hatchling>=1.5.0`）+ hatch-jupyter-builder（`hatch-jupyter-builder>=0.5`），定义于 `pyproject.toml:2,56`
F-005: JupyterLab 扩展 ID 为 `@jupyterlite/litegitpuller:plugin`，autoStart 为 true，定义于 `src/index.ts:37-38`
F-006: 扩展依赖 JupyterLab `>=4.0.0`，定义于 `package.json:58` 和 `README.md:12`
F-007: Python 包无运行时依赖（dependencies 为空列表），定义于 `pyproject.toml:25-26`
F-008: npm 运行时依赖为 `@jupyterlab/application: ^4.0.0`、`@jupyterlab/coreutils: ^6.0.0`、`@jupyterlab/filebrowser: ^4.0.0`、`@jupyterlab/services: ^7.0.0`，定义于 `package.json:57-62`

## 模块与文件结构

F-009: TypeScript 入口文件为 `src/index.ts`，导出默认对象 `gitPullerExtension`，定义于 `src/index.ts:110`
F-010: `src/gitpuller.ts` 文件定义三个导出类：`GitPuller`（抽象类）、`GithubPuller`、`GitlabPuller`，定义于 `src/gitpuller.ts:8,221,287`
F-011: Python 包入口 `litegitpuller/__init__.py` 定义函数 `_jupyter_labextension_paths()`，返回 `[{"src": "labextension", "dest": "@jupyterlite/litegitpuller"}]`，定义于 `litegitpuller/__init__.py:12-16`
F-012: Python 包尝试从 `._version` 导入 `__version__`，失败时设为 `"dev"` 并发出警告，定义于 `litegitpuller/__init__.py:1-9`
F-013: `install.json` 指定 packageManager 为 `"python"`，packageName 为 `"litegitpuller"`，定义于 `install.json:2-3`
F-014: 样式文件 `style/index.js` 仅导入 `./base.css`，定义于 `style/index.js:1`
F-015: 样式文件 `style/index.css` 仅导入 `base.css`，定义于 `style/index.css:1`
F-016: 样式文件 `style/base.css` 仅含注释，无实际CSS规则，定义于 `style/base.css:1-5`

## GitPuller 抽象类

F-017: `GitPuller` 是抽象类（`abstract class`），构造函数接受 `GitPuller.IOptions` 类型参数 `options`，定义于 `src/gitpuller.ts:8,12`
F-018: `GitPuller` 构造函数将 `options.defaultFileBrowser` 赋值给 `this._defaultFileBrowser`，将 `options.contents` 赋值给 `this._contents`，定义于 `src/gitpuller.ts:13-14`
F-019: `GitPuller.clone(url: string, branch: string, basePath: string): Promise<string>` 是异步方法，返回 `Promise<string>`，定义于 `src/gitpuller.ts:25`
F-020: `GitPuller.clone()` 方法内部先将 `basePath` 按 `/` 拆分为组件，生成前缀路径数组 `basePathPrefixes`（如 `a/b/c` → `['a', 'a/b', 'a/b/c']`），然后调用 `this.createTree(basePathPrefixes)` 创建目录树，定义于 `src/gitpuller.ts:26-33`
F-021: `GitPuller.clone()` 调用 `this.getFileList(url, branch)` 获取文件列表，然后调用 `this.createTree(fileList.directories, basePath)` 创建仓库目录，定义于 `src/gitpuller.ts:35-37`
F-022: `GitPuller.clone()` 遍历 `fileList.files`，对每个文件先调用 `this.fileExists(filePath)` 检查是否存在，已存在的文件调用 `this.addUploadError('File already exist', filePath)` 记录错误并跳过，定义于 `src/gitpuller.ts:38-43`
F-023: `GitPuller.clone()` 对不存在的文件调用 `this.getFile(url, file, branch)` 获取内容，然后调用 `this.createFile(filePath, fileContent.blob, fileContent.type)` 创建文件，定义于 `src/gitpuller.ts:46-48`
F-024: `GitPuller.clone()` 在所有文件处理完成后，遍历 `this._errors` Map，对每个错误 key 输出 console.warn，然后返回 `basePath`，定义于 `src/gitpuller.ts:52-59`
F-025: `GitPuller.getFileList(url: string, branch: string): Promise<GitPuller.IFileList>` 是抽象方法，定义于 `src/gitpuller.ts:69-72`
F-026: `GitPuller.getFile(url: string, path: string, branch: string): Promise<GitPuller.IFile>` 是抽象方法，定义于 `src/gitpuller.ts:82-86`
F-027: `GitPuller.createTree(directories: string[], basePath: string | null = null): Promise<void>` 是 protected 异步方法，定义于 `src/gitpuller.ts:94-97`
F-028: `GitPuller.createTree()` 对目录列表先排序（`directories.sort()`），然后遍历每个目录，拼接 basePath 后通过 `this._contents.get(directory, { content: false })` 检查目录是否存在，不存在时调用 `this._contents.newUntitled(options)` 创建新目录再 `rename` 到目标路径，定义于 `src/gitpuller.ts:98-112`
F-029: `GitPuller.createTree()` 创建目录时 options 对象为 `{ type: 'directory' as Contents.ContentType, path: PathExt.dirname(directory) }`，定义于 `src/gitpuller.ts:101-104`
F-030: `GitPuller.fileExists(filePath: string): Promise<boolean>` 是 protected 异步方法，通过 `this._contents.get(filePath, { content: false }).then(() => true).catch(() => false)` 判断文件是否存在，定义于 `src/gitpuller.ts:120-125`
F-031: `GitPuller.createFile(filePath: string, blob: Blob, type: string): Promise<void>` 是 protected 异步方法，定义于 `src/gitpuller.ts:134-138`
F-032: `GitPuller.createFile()` 先获取 `filename = PathExt.basename(filePath)`，通过 while 循环检查根路径下是否存在同名文件，存在则在文件名前加 `{inc}_` 前缀（inc 从0递增），定义于 `src/gitpuller.ts:139-155`
F-033: `GitPuller.createFile()` 用 `new File([blob], filename, { type })` 创建 File 对象，调用 `this._defaultFileBrowser.model.upload(file)` 上传文件，上传后如果路径不匹配则调用 `this._contents.rename(model.path, filePath)` 移动到目标路径，定义于 `src/gitpuller.ts:157-162`
F-034: `GitPuller.addUploadError(error: string, path: string)` 是 protected 方法，从 `this._errors` Map 获取对应错误的文件列表（不存在则为空数组），追加 path 后设回 Map，定义于 `src/gitpuller.ts:171-174`
F-035: `GitPuller._errors` 是 protected 属性，类型为 `Map<string, string[]>`，初始值为 `new Map()`，定义于 `src/gitpuller.ts:176`
F-036: `GitPuller._defaultFileBrowser` 是 protected 属性，类型为 `IDefaultFileBrowser`，定义于 `src/gitpuller.ts:177`
F-037: `GitPuller._contents` 是 protected 属性，类型为 `Contents.IManager`，定义于 `src/gitpuller.ts:178`

## GitPuller 命名空间（接口定义）

F-038: `GitPuller.IOptions` 接口包含两个字段：`defaultFileBrowser: IDefaultFileBrowser` 和 `contents: Contents.IManager`，定义于 `src/gitpuller.ts:188-191`
F-039: `GitPuller.IFileList` 接口包含两个字段：`directories: string[]` 和 `files: string[]`，定义于 `src/gitpuller.ts:196-199`
F-040: `GitPuller.IFile` 接口包含两个字段：`blob: Blob` 和 `type: string`，定义于 `src/gitpuller.ts:204-207`
F-041: `GitPuller.IUploadError` 接口包含两个字段：`type: string` 和 `file: string`，定义于 `src/gitpuller.ts:212-215`

## GithubPuller 类

F-042: `GithubPuller` 继承自 `GitPuller`，定义于 `src/gitpuller.ts:221`
F-043: `GithubPuller.getFileList(url, branch)` 构造 fetchUrl 为 `${url}/git/trees/${branch}?recursive=true`，使用 GET 方法请求，headers 包含 `Accept: 'application/vnd.github+json'`、`'X-GitHub-Api-Version': '2022-11-28'`、`'User-Agent': 'request'`，定义于 `src/gitpuller.ts:228-237`
F-044: `GithubPuller.getFileList()` 将响应 JSON 的 `tree` 数组中 `type === 'tree'` 的项映射为 `directories`（取 path 字段），`type === 'blob'` 的项映射为 `files`（取 path 字段），定义于 `src/gitpuller.ts:239-249`
F-045: `GithubPuller.getFile(url, path, branch)` 构造 fetchUrl 为 `${url}/contents/${path}?ref=${branch}`，使用相同的 headers 请求，从响应 JSON 获取 `download_url`，然后 fetch 该 URL 获取 blob 和 Content-Type，定义于 `src/gitpuller.ts:259-280`

## GitlabPuller 类

F-046: `GitlabPuller` 继承自 `GitPuller`，定义于 `src/gitpuller.ts:287`
F-047: `GitlabPuller.getFileList(url, branch)` 构造 fetchUrl 为 `${url}/repository/tree?ref=${branch}&recursive=true`，使用 GET 方法请求（无特殊 headers），将响应 JSON 数组中 `type === 'tree'` 映射为 directories，`type === 'blob'` 映射为 files，定义于 `src/gitpuller.ts:294-310`
F-048: `GitlabPuller.getFile(url, path, branch)` 构造 fetchUrl 为 `${url}/repository/files/${encodeURIComponent(path)}/raw?ref=${branch}`，fetch 后获取 blob 和 Content-Type，定义于 `src/gitpuller.ts:320-333`

## 扩展激活逻辑（index.ts）

F-049: `testNbGitPuller(): Promise<boolean>` 是导出的异步函数，定义于 `src/index.ts:14`
F-050: `testNbGitPuller()` 通过 `ServerConnection.makeSettings()` 获取设置，构造 URL 为 `URLExt.join(settings.baseUrl, 'git-pull', 'api')`，发起 GET 请求，请求成功且 `response.ok` 时返回 true，否则返回 false（catch 块也返回 false），定义于 `src/index.ts:15-33`
F-051: 扩展 activate 函数中，首先调用 `testNbGitPuller()`，如果返回 true 则输出 console.log 说明不激活以避免与 nbgitpuller 冲突，然后 return，定义于 `src/index.ts:44-49`
F-052: 扩展激活时从 URL 查询参数中读取：`repo`（通过 `urlParams.get('repo')`）、`branch`（默认 `'main'`）、`provider`（默认 `'github'`）、`urlpath`、`uploadpath`（默认 `'/'`），定义于 `src/index.ts:55-67`
F-053: 如果 `repo` 参数不存在（`!repo`），扩展直接 return 不执行任何操作，定义于 `src/index.ts:58-60`
F-054: `basePath` 通过 `PathExt.join(uploadPath, PathExt.basename(repo))` 计算，定义于 `src/index.ts:69`
F-055: provider 为 `'github'` 时，创建 `new URL(repo)` 解析仓库URL，检查 `repoUrl.hostname !== 'github.com'` 时输出警告并 return；将 hostname 改为 `'api.github.com'`，pathname 改为 `/repos${repoUrl.pathname}`，然后创建 `new GithubPuller({defaultFileBrowser, contents: app.serviceManager.contents})`，定义于 `src/index.ts:71-84`
F-056: provider 为 `'gitlab'` 时，将 pathname 改为 `/api/v4/projects/${encodeURIComponent(repoUrl.pathname.slice(1))}`，然后创建 `new GitlabPuller({defaultFileBrowser, contents: app.serviceManager.contents})`，定义于 `src/index.ts:85-94`
F-057: puller 创建成功后，调用 `puller.clone(repoUrl.href, branch, basePath)`，完成后如果 `filePath` 存在，执行 `app.commands.execute('filebrowser:open-path', {path: PathExt.join(repoPath, filePath)})` 打开目标文件，定义于 `src/index.ts:100-106`
F-058: 扩展 requires 声明为 `[IDefaultFileBrowser]`，定义于 `src/index.ts:39`
F-059: 扩展从 `./gitpuller` 导入 `GitPuller, GithubPuller, GitlabPuller` 三个类，定义于 `src/index.ts:8`

## 文档中描述的URL参数

F-060: 文档列出的URL参数：`repo`（必填）、`branch`（默认main）、`urlpath`（相对于仓库根目录的notebook路径）、`provider`（支持github和gitlab）、`uploadpath`（仓库目录创建位置），定义于 `docs/index.md:24-29`
F-061: 文档说明 GitHub API 未认证请求限制为每小时60个文件，定义于 `docs/index.md:33-35`

## 构建配置

F-062: hatch 构建 wheel 时，将 `litegitpuller/labextension` 映射到 `share/jupyter/labextensions/@jupyterlite/litegitpuller`，将 `install.json` 映射到同目录下的 install.json，定义于 `pyproject.toml:48-50`
F-063: hatch-jupyter-builder 构建命令为 `build:prod`，npm 命令为 `jlpm`，定义于 `pyproject.toml:64-66`
F-064: 构建确保目标文件为 `litegitpuller/labextension/static/style.js` 和 `litegitpuller/labextension/package.json`，定义于 `pyproject.toml:58-61`
F-065: npm build 脚本执行 `jlpm build:lib && jlpm build:labextension:dev`，定义于 `package.json:31`
F-066: TypeScript 编译目标通过 `tsc` 命令执行，dev 模式加 `--sourceMap`，定义于 `package.json:35-36`
