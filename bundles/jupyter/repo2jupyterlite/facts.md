# repo2jupyterlite 源码事实清单

&gt; R阶段产出：零推测事实，每条事实指向具体源码位置。禁止出现"用于"/"目的是"/"设计为"等推断词。

## 项目元数据

- F-001: 包名 `repo2jupyterlite`，版本 `0.2`，描述 "Build JupyterLite bundles from code repositories"
- F-002: `setup.py` 中 `python_requires="&gt;=3.10"`
- F-003: `setup.py` 中 `install_requires` 列表包含：`jupyterlite-core[all]`、`jupyterlite-xeus-python`、`jupyter-repo2docker`、`yarl`
- F-004: `setup.py` 中 console_scripts 入口点：`repo2jupyterlite = repo2jupyterlite.app:main`
- F-005: `setup.py` 中 `setup()` 函数调用前执行 `subprocess.check_call(["npm", "i"])` 和 `subprocess.check_call(["npm", "run", "build"])`
- F-006: 作者为 Yuvi Panda，邮箱 yuvipanda@gmail.com，License 为 3-BSD
- F-007: 仓库地址 `https://github.com/jupyterlite/repo2jupyterlite/`
- F-008: `environment.yml` 指定 conda-forge channel，依赖：mamba、fastapi、uvicorn、nodejs、pip
- F-009: `package.json` 中 name 为 `binderlite`，version 为 `1.0.0`
- F-010: `package.json` dependencies：`bootstrap: "^5.2.3"`、`react: "^18.2.0"`、`react-dom: "^18.2.0"`
- F-011: `package.json` devDependencies：`@babel/core: "^7.22.1"`、`@babel/preset-env: "^7.22.2"`、`@babel/preset-react: "^78.22.3"`、`babel-loader: "^8.2.1"`、`css-loader: "^6.7.3"`、`html-webpack-plugin: "^5.5.1"`、`style-loader: "^3.3.2"`、`webpack: "^5.6.0"`、`webpack-cli: "^4.10.0"`、`webpack-dev-server: "^4.9.3"`
- F-012: `package.json` scripts：`build: "webpack"`、`watch: "webpack --watch"`
- F-013: `package.json` babel 配置：presets 为 `@babel/preset-env` 和 `["@babel/preset-react", {"runtime": "automatic"}]`

## CLI 入口 `repo2jupyterlite/app.py`

- F-014: `app.py` 第12-21行定义 `content_providers` 列表，包含：`contentproviders.Local`、`contentproviders.Zenodo`、`contentproviders.Figshare`、`contentproviders.Dataverse`、`contentproviders.Hydroshare`、`contentproviders.Swhid`、`contentproviders.Mercurial`、`contentproviders.Git`（均来自 `repo2docker.contentproviders`）
- F-015: `fetch(url, ref, checkout_path)` 函数定义在第27行
- F-016: `fetch` 遍历 `content_providers` 列表，对每个 ContentProvider 实例化并调用 `cp.detect(url, ref=ref)`，返回非 None 时记录日志并 break
- F-017: `fetch` 中所有 ContentProvider 都返回 None 时，调用 `log.error(...)` 后 return（无异常抛出）
- F-018: `fetch` 调用 `picked_content_provider.fetch(spec, checkout_path, yield_output=True)`，逐行 log.info 输出
- F-019: `build(repo_dir, output_dir)` 函数定义在第58行
- F-020: `build` 构造命令列表 `["jupyter", "lite", "build", ".", "--output-dir", abs_output_path, "--contents", "."]`
- F-021: `build` 检查 `os.path.join(repo_dir, "jupyterlite_config.json")` 是否存在，存在则追加 `["--config", "jupyterlite_config.json"]`
- F-022: `build` 调用 `subprocess.check_call(cmd, cwd=repo_dir)`
- F-023: `main()` 函数定义在第82行
- F-024: `main()` 使用 argparse，接受位置参数 `url` 和 `output_dir`，可选参数 `--ref`（默认None）
- F-025: `main()` 中如果 `args.output_dir` 路径已存在，打印错误信息并 `sys.exit(1)`
- F-026: `main()` 中如果 `os.path.exists(args.url)` 为 True（本地路径），则 `checkout_dir = args.url`，`temp_dir = nullcontext()`
- F-027: `main()` 中如果 `args.url` 不是本地路径，则 `temp_dir = TemporaryDirectory()`，`checkout_dir = temp_dir.name`，调用 `fetch(args.url, args.ref, checkout_dir)`
- F-028: `main()` 在 `with temp_dir:` 上下文中调用 `build(checkout_dir, args.output_dir)`，然后打印 `f"Go to http://localhost:8000/{args.output_dir}"`

## 仓库提供者 `repoproviders/github.py`

- F-029: `GitHubRepoProvider(LoggingConfigurable)` 类定义在第11行，继承自 `traitlets.config.LoggingConfigurable`
- F-030: `GitHubRepoProvider.name` = `Unicode("GitHub")`
- F-031: `GitHubRepoProvider.cache` = `Cache(1024)`（类级别属性）
- F-032: `GitHubRepoProvider.cache_404` = `Cache(1024, max_age=300)`（类级别属性）
- F-033: `GitHubRepoProvider.hostname` = `Unicode("github.com", config=True)`
- F-034: `GitHubRepoProvider.api_base_path` = `Unicode("https://api.{hostname}", config=True)`
- F-035: `GitHubRepoProvider.client_id` = `Unicode(config=True)`，默认值从环境变量 `GITHUB_CLIENT_ID` 读取（`@default("client_id")`）
- F-036: `GitHubRepoProvider.client_secret` = `Unicode(config=True)`，默认值从环境变量 `GITHUB_CLIENT_SECRET` 读取
- F-037: `GitHubRepoProvider.access_token` = `Unicode(config=True)`，默认值从环境变量 `GITHUB_ACCESS_TOKEN` 读取
- F-038: `_default_git_credentials` 方法：如果 `access_token` 存在且 `client_id` 存在，返回 `r"username={client_id}\npassword={token}"`；如果 `access_token` 存在但 `client_id` 不存在，返回 `rf"username={self.access_token}\npassword=x-oauth-basic"`；否则返回空字符串
- F-039: `from_spec_and_path(cls, spec_and_path: str)` 类方法定义在第98行
- F-040: `from_spec_and_path` 中 `len(spec_and_path.split("/")) == 3` 时，split("/", 3) 后追加空字符串作为path；否则 split("/", 3)
- F-041: `from_spec_and_path` 返回 `(cls(parts[0], parts[1], parts[2]), path)`，其中 `path = parts[3]`
- F-042: `GitHubRepoProvider.__init__(self, user, repo, unresolved_ref)` 设置实例属性 `self.user`、`self.repo`、`self.unresolved_ref`
- F-043: `_github_api_request(self, api_url, etag=None)` 异步方法定义在第120行
- F-044: `_github_api_request` 创建 `AsyncHTTPClient()` 实例
- F-045: `_github_api_request` 中如果 `client_id` 和 `client_secret` 都存在，设置 `auth_username` 和 `auth_password`
- F-046: `_github_api_request` 中如果 `access_token` 存在，设置 `headers["Authorization"] = f"token {self.access_token}"`
- F-047: `_github_api_request` 中如果传入 `etag`，设置 `headers["If-None-Match"] = etag`
- F-048: `_github_api_request` 构造 `HTTPRequest(api_url, headers=headers, user_agent="BinderHub", ...)`
- F-049: `_github_api_request` 中 HTTP 304 返回 `e.response`；403 且 `x-ratelimit-remaining == "0"` 时抛出 ValueError；404/422 返回 None；其他异常 raise
- F-050: `_github_api_request` 中响应头包含 `x-ratelimit-remaining` 时，根据 remaining/rate_limit 比例分级别（warning/info/debug）记录日志
- F-051: `get_resolved_ref(self)` 异步方法定义在第203行
- F-052: `get_resolved_ref` 检查实例属性 `resolved_ref`，存在则直接返回
- F-053: `get_resolved_ref` 构造 API URL：`{api_base_path}/repos/{user}/{repo}/commits/{ref}`
- F-054: `get_resolved_ref` 先查 `self.cache.get(api_url)`，命中则使用缓存的 etag；否则查 `self.cache_404.get(api_url)`，命中则返回 None
- F-055: `get_resolved_ref` 调用 `_github_api_request(api_url, etag=etag)`
- F-056: `get_resolved_ref` 中 resp 为 None（404/422）时，缓存到 `cache_404` 并返回 None
- F-057: `get_resolved_ref` 中 resp.code == 304 时，使用缓存的 sha，调用 `self.cache.move_to_end(api_url)` 刷新 LRU
- F-058: `get_resolved_ref` 正常响应时，解析 JSON 取 `ref_info["sha"]`，存入 `self.resolved_ref`，缓存 `{"etag": resp.headers.get("ETag"), "sha": ...}` 到 `self.cache`
- F-059: `get_resolved_spec(self)` 异步方法：先 `await self.get_resolved_ref()`，返回 `f"{self.user}/{self.repo}/{resolved_ref}"`
- F-060: `get_resolved_repo(self)` 方法：返回 `f"https://{self.hostname}/{self.user}/{self.repo}"`

## 工具类 `repoproviders/utils.py`

- F-061: `Cache(OrderedDict)` 类定义在第5行
- F-062: `Cache.__init__(self, max_size=1024, max_age=0)` 设置 `self.max_size`、`self.max_age`、`self._ages = {}`
- F-063: `Cache._now(self)` 返回 `time.perf_counter()`
- F-064: `Cache._check_expired(self, key)`：如果 `self.max_age` 非0且 `self._ages[key] + self.max_age &lt; self._now()`，则 `self.pop(key)` 并返回 True；否则返回 False
- F-065: `Cache.get(self, key, default=None)`：key 存在且未过期时调用 `self.move_to_end(key)`，然后调用 `super().get(key, default)`
- F-066: `Cache.set(self, key, value)`：设置 `self[key] = value`、`self._ages[key] = self._now()`、`self.move_to_end(key)`；如果 `len(self) &gt; self.max_size`，弹出 `next(iter(self))`（最旧项）
- F-067: `Cache.pop(self, key)`：调用 `super().pop(key)` 并 `self._ages.pop(key)`

## BinderLite Web 应用 `binderlite/run.py`

- F-068: `app = FastAPI()` 实例定义在第22行
- F-069: `repo_providers = {"gh": GitHubRepoProvider}` 字典定义在第24行
- F-070: `templates = Jinja2Templates(directory=HERE / "templates")`，其中 `HERE = Path(__file__).parent`
- F-071: `output_dir_prefix = Path("output")`，调用 `os.makedirs(output_dir_prefix, exist_ok=True)`
- F-072: `app.mount("/static", StaticFiles(directory=HERE / "static"), name="static")`
- F-073: `publisher = LocalFilesystemPublisher()`，调用 `publisher.mount_extra_handlers(app)`
- F-074: `@app.get("/", response_class=HTMLResponse)` 路由：`index(request: Request)` 返回 `templates.TemplateResponse("index.html", {"request": request, "repo_providers": repo_providers})`
- F-075: `@app.get("/v1/{provider_name:str}/{spec_and_path:path}")` 路由：`render(provider_name, spec_and_path, request)` 定义在第49行
- F-076: `render` 中通过 `provider_class = repo_providers[provider_name]` 获取 provider 类
- F-077: `render` 调用 `provider_class.from_spec_and_path(spec_and_path)` 返回 `(provider, path)`
- F-078: `render` 中 `path.strip() == ""` 时，使用 `yarl.URL` 构造重定向 URL 到 `{path}/lab/index.html`，保留 query 参数，返回 `RedirectResponse`
- F-079: `render` 调用 `await provider.get_resolved_ref()` 获取 ref
- F-080: `render` 中如果 `ref != provider.unresolved_ref`，重定向到解析后的 spec URL，保留 query 参数
- F-081: `render` 调用 `await provider.get_resolved_spec()` 获取 resolved_spec
- F-082: `render` 中 `slug = escape(f"{provider_name}-{resolved_spec}", safe=string.ascii_letters + string.digits + "-" + "/")`，使用 `escapism.escape`
- F-083: `render` 中 `if not (await publisher.exists(slug))`：
  - 如果 `path.endswith(".html")`：构造 `["repo2jupyterlite", provider.get_resolved_repo(), "--ref", ref, str(d)]` 命令
  - 在 `publisher.get_target_dir(slug)` 上下文管理器中获取目标目录 d
  - `asyncio.create_subprocess_exec(*cmd)` 执行构建
  - `retcode != 0` 时抛出 `HTTPException(status_code=500, detail="jupyter lite build failed")`
  - 构建成功后 `await publisher.upload(d, slug)`
  - 如果 path 不以 .html 结尾，返回 `Response(status_code=404)`
- F-084: `render` 最后 `return await publisher.serve_object(slug, path, request.headers)`

## 发布抽象 `binderlite/publish.py`

- F-085: `output_dir_prefix = Path("output")`，调用 `os.makedirs(output_dir_prefix, exist_ok=True)`
- F-086: `Publisher` 类定义在第15行
- F-087: `Publisher.get_target_dir(self, slug)` 是 `@contextmanager`：`tempfile.mktemp()` 创建临时目录路径，yield 后在 finally 中 `shutil.rmtree(tmpdirname)`
- F-088: `Publisher.exists(self, slug)` 异步方法：`raise NotImplementedError()`
- F-089: `Publisher.upload(self, slug, source_dir)` 异步方法：`raise NotImplementedError()`
- F-090: `Publisher.get_redirect_url(self, slug)` 异步方法：`raise NotImplementedError()`
- F-091: `Publisher.mount_extra_handlers(self, app)` 方法：`pass`
- F-092: `LocalFilesystemPublisher(Publisher)` 类定义在第63行
- F-093: `LocalFilesystemPublisher.get_target_dir(self, slug)` 是 `@contextmanager`：`output_dir = output_dir_prefix / slug`，如果存在则 `shutil.rmtree(output_dir)`，yield output_dir
- F-094: `LocalFilesystemPublisher.upload(self, source_dir, slug)` 异步方法：写入空文件 `output_dir_prefix / slug / ".completed-sentinel"`
- F-095: `LocalFilesystemPublisher.exists(self, slug)` 异步方法：返回 `(output_dir_prefix / slug / ".completed-sentinel").exists()`
- F-096: `LocalFilesystemPublisher.get_redirect_url(self, slug)` 方法：返回 `f"/render/{slug}/index.html"`
- F-097: `LocalFilesystemPublisher.is_not_modified(self, response_headers, request_headers)` 方法：检查 `if-none-match`/`etag` 和 `if-modified-since`/`last-modified`，返回 bool
- F-098: `LocalFilesystemPublisher.serve_object(self, slug, path, request_headers)` 异步方法：
  - 构造 `file_path = output_dir_prefix / slug / path`
  - 如果 `file_path.is_dir()`，设置 `file_path = file_path / "index.html"`
  - 返回 `FileResponse(file_path, headers={"Cache-Control": "public, max-age=86400"})`
  - 如果 `is_not_modified` 返回 True，包装为 `NotModifiedResponse(resp.headers)`
- F-099: `LocalFilesystemPublisher.mount_extra_handlers(self, app)` 方法：`app.mount("/render", StaticFiles(directory=output_dir_prefix), name="render")`

## 前端源码 `src/`

- F-100: `src/App.jsx` 导入：`useState` from react、`createRoot` from react-dom/client、`"bootstrap/dist/css/bootstrap.min.css"`、`parseRepoURL` from `./detectors`、`./App.css`
- F-101: `ExplanatoryCards()` 函数组件返回包含两排卡片的 div：
  - 第一排 "How it works"：3张卡片（输入仓库信息、预装Python包、交互使用）
  - 第二排 "Current Limitations"：3张卡片（有限包支持、有限语言支持、有限网络支持）
  - 底部小字反馈链接和作者信息
- F-102: `App()` 函数组件：
  - 使用 `useState("")` 管理 `repoUrl`
  - 使用 `useState(false)` 管理 `isSubmitting`
  - 使用 `useState(null)` 管理 `parsedRepoURL`
  - 渲染容器 div，包含 logo img（src="/static/wordmark.svg"）、form 表单
  - input 元素 onChange 时调用 `parseRepoURL(e.target.value)` 并 setParsedRepoURL
  - 解析结果以列表显示 `parsedRepoURL.displayParts` 的 key-value
  - Launch 按钮在 `!Boolean(parsedRepoURL)` 时 disabled
  - Launch 按钮 onClick 时构造 `/v1/{parsedRepoURL.spec}` URL，如有 filePath 追加 `?path=`，setIsSubmitting(true)，`window.location.href = redirectUrl`
- F-103: `App.jsx` 末尾：`document.body.innerHTML = "&lt;div id='app'&gt;&lt;/div&gt;"`，`createRoot(document.getElementById("app")).render(&lt;App /&gt;)`
- F-104: `src/detectors.js` 定义 `ParsedRepoURL` 类，构造函数接受 `(provider, spec, filePath, displayParts)`，设置同名实例属性
- F-105: `parseRepoURL(url)` 导出函数：
  - `funcs = [github]` 检测器数组
  - try `new URL(url)`，catch 时 console.log 并 return null
  - 遍历 funcs，调用 `f(urlObj)`，返回第一个非 null 结果
- F-106: `github(url)` 函数（非导出）：
  - `url.hostname !== "github.com"` 时 return null
  - `url.pathname.split("/").filter(part =&gt; part.trim() !== "")` 获取 pathParts
  - `pathParts.length &lt; 2` 时 return null
  - 初始化 parts：`{user: pathParts[0], repo: pathParts[1], ref: "HEAD", filePath: ""}`
  - `pathParts.length &gt; 3` 且 `pathParts[2]` 在 `["blob", "tree", "commit"]` 中时，设置 `parts["ref"] = pathParts[3]`，`parts["filePath"] = pathParts.slice(4).join("/")`
  - 返回 `new ParsedRepoURL("gh", "gh/{user}/{repo}/{ref}", filePath, displayParts)`，其中 displayParts 包含 source、repository、ref、path to open

## Webpack 配置 `webpack.config.js`

- F-107: `entry` 为 `path.resolve(__dirname, "src", "App.jsx")`
- F-108: plugins 包含 `new HtmlWebpackPlugin({...})`：
  - `publicPath: "/static/"`
  - `filename` 输出到 `path.resolve(__dirname, "binderlite", "templates", "index.html")`
  - `hash: true`
  - title 为 "BinderLite: Run JupyterLab entirely in the browser, with your packages &amp; notebooks"
- F-109: `mode: "development"`
- F-110: module.rules 包含两条：
  - `/\.
[truncated by convert_data_to_sft: original content length=9125 chars for checker-safe SFT export]
