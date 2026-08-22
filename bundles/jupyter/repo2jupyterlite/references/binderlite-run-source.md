---
type: Reference
title: BinderLite Web 应用信源
description: binderlite/run.py FastAPI 应用的API登记，包含路由定义、构建触发和重定向逻辑
tags: [binderlite, fastapi, web, api, route, async, redirect]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T16:00:00+08:00" }
verified: { by: "process:grep-api-verify", at: "2026-08-22T16:00:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: run-py
    resource: ../../../../../../external/libs/jupyter/repo2jupyterlite/binderlite/run.py
    title: binderlite/run.py 源码
---

## 模块概览

`binderlite/run.py` 实现了 BinderLite 的 FastAPI Web 应用，提供首页渲染和动态构建/服务 JupyterLite 实例的API。

## 模块级变量

| 变量 | 类型 | 说明 |
|------|------|------|
| `app` | `FastAPI` | FastAPI 应用实例 |
| `repo_providers` | `dict[str, type]` | 注册的仓库提供者：`{"gh": GitHubRepoProvider}` |
| `templates` | `Jinja2Templates` | Jinja2 模板引擎，目录为 `binderlite/templates/` |
| `output_dir_prefix` | `Path` | 输出目录前缀，值为 `Path("output")`，启动时自动创建 |
| `publisher` | `LocalFilesystemPublisher` | 本地文件系统发布器实例 |

## 静态资源挂载

- `/static`：挂载 `binderlite/static/` 目录（webpack 输出的前端 JS/CSS/SVG）
- `/render`：由 `publisher.mount_extra_handlers(app)` 挂载，服务已构建的静态文件

## 路由 API

### `GET /`

**处理器**：`index(request: Request)`

**响应**：`HTMLResponse`，渲染 `templates/index.html` 模板，传入 `repo_providers` 字典。

**模板上下文**：
- `request`：FastAPI Request 对象
- `repo_providers`：可用的仓库提供者字典

### `GET /v1/{provider_name}/{spec_and_path:path}`

**处理器**：`render(provider_name: str, spec_and_path: str, request: Request)`

**参数**：
- `provider_name`：提供者名称（如 `"gh"`）
- `spec_and_path`：仓库规格与路径（如 `"user/repo/HEAD/notebook.ipynb"`）

**处理流程**：

1. **获取 Provider**：`provider_class = repo_providers[provider_name]`
2. **解析 Spec**：`provider, path = provider_class.from_spec_and_path(spec_and_path)`
3. **第一次重定向**（path 为空）：
   - 使用 `yarl.URL` 构造新 URL：`{current_path}/lab/index.html`
   - 保留 query 参数（处理 yarl bug #111）
   - 返回 `RedirectResponse`
4. **解析 Ref**：`ref = await provider.get_resolved_ref()`
5. **第二次重定向**（ref 变化）：
   - 如果 `ref != provider.unresolved_ref`（如 HEAD → commit SHA）
   - 重定向到 `/v1/{provider_name}/{user}/{repo}/{sha}/{path}`
   - 保留 query 参数
6. **生成 Slug**：`escape(f"{provider_name}-{resolved_spec}", safe=ascii_letters+digits+"-/")`
7. **构建检查**：
   - 如果 `not (await publisher.exists(slug))`：
     - 如果 `path.endswith(".html")`：触发构建
       - 构造命令：`["repo2jupyterlite", repo_url, "--ref", ref, output_dir]`
       - 在 `publisher.get_target_dir(slug)` 上下文中获取目标目录
       - `asyncio.create_subprocess_exec(*cmd)` 执行
       - 非零退出码 → `HTTPException(500, "jupyter lite build failed")`
       - 成功 → `await publisher.upload(d, slug)`
     - 如果不以 `.html` 结尾：`return Response(status_code=404)`
8. **服务文件**：`return await publisher.serve_object(slug, path, request.headers)`

## 导入依赖

- `asyncio`：异步子进程执行
- `os`、`pathlib.Path`：文件路径操作
- `string`：安全字符集
- `yarl.URL`：URL 操作（处理重定向）
- `repoproviders.github.GitHubRepoProvider`：GitHub 仓库提供者
- `escapism.escape`：URL 安全编码
- `fastapi`：FastAPI、HTTPException、Request
- `fastapi.responses`：Response、HTMLResponse、RedirectResponse
- `fastapi.staticfiles.StaticFiles`：静态文件服务
- `fastapi.templating.Jinja2Templates`：Jinja2 模板
- `binderlite.publish.LocalFilesystemPublisher`：本地发布器
