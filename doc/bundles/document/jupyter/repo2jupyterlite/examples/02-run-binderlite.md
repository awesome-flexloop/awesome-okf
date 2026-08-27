---
type: Example
title: 运行 BinderLite 服务示例
description: 安装依赖、配置GitHub认证、启动BinderLite Web服务并在浏览器中使用的完整步骤
tags: [binderlite, web, server, fastapi, uvicorn, deployment]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T16:00:00+08:00" }
verified: { by: "process:grep-api-verify", at: "2026-08-22T16:00:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: metasource
    resource: /references/metasource.md
    title: 项目元数据信源
  - id: run-source
    resource: /references/binderlite-run-source.md
    title: BinderLite Web应用信源
---

本示例演示如何从源码安装和运行 BinderLite Web 应用，实现类似 mybinder.org 的按需构建 JupyterLite 服务。

## 步骤1：准备 Conda 环境

BinderLite 需要 FastAPI、uvicorn、Node.js 等依赖。使用项目提供的 `environment.yml`：

```bash
# 进入项目目录
cd /path/to/repo2jupyterlite

# 创建并激活 conda 环境
mamba env create -n binderlite -f environment.yml
conda activate binderlite
```

`environment.yml` 包含的依赖（F-008）：

| 包 | 用途 |
|---|---|
| mamba | 快速包管理器 |
| fastapi | Web 框架 |
| uvicorn | ASGI 服务器 |
| nodejs | 前端构建运行时 |
| pip | Python 包管理器 |

## 步骤2：安装额外 Python 依赖

environment.yml 只列出了 conda 依赖，还需要通过 pip 安装：

```bash
pip install -e .
```

这会以开发模式安装 repo2jupyterlite 及其 pip 依赖（F-003）：
- jupyterlite-core[all]
- jupyterlite-xeus-python
- jupyter-repo2docker
- yarl

另外 BinderLite 还需要：
```bash
pip install escapism jinja2 python-multipart aiofiles tornado traitlets
```

## 步骤3：构建前端资源

```bash
npm install
npm run build
```

这会：
1. 安装 React、Bootstrap 等前端依赖
2. 使用 Webpack 打包 React 应用
3. 输出 JS 到 `binderlite/static/index.js`
4. 输出 HTML 模板到 `binderlite/templates/index.html`

> **注意**：`pip install -e .` 时 setup.py 会自动执行 `npm i &amp;&amp; npm run build`（F-005），但如果修改了前端源码，需要手动重新执行 `npm run build`。

## 步骤4：配置 GitHub 认证（可选但推荐）

匿名访问 GitHub API 有 60 次/小时的 rate limit。配置认证可以提高到 5000 次/小时。

### 方式A：Personal Access Token

```bash
export GITHUB_ACCESS_TOKEN=ghp_your_token_here
```

### 方式B：OAuth App

```bash
export GITHUB_CLIENT_ID=your_client_id
export GITHUB_CLIENT_SECRET=your_client_secret
```

这些环境变量会被 GitHubRepoProvider 的 `@default` 方法自动读取（F-056, F-069, F-082）。

## 步骤5：启动 BinderLite

```bash
uvicorn binderlite.run:app --host 0.0.0.0 --port 8000
```

参数说明：
- `binderlite.run:app`：FastAPI 应用实例的模块路径
- `--host 0.0.0.0`：监听所有网络接口（默认 127.0.0.1）
- `--port 8000`：监听端口（默认 8000）

开发模式（自动重载）：
```bash
uvicorn binderlite.run:app --reload
```

## 步骤6：在浏览器中使用

1. 打开浏览器访问 `http://localhost:8000`
2. 在输入框中粘贴 GitHub URL，例如：
   - `https://github.com/username/repo`（默认分支）
   - `https://github.com/username/repo/blob/main/notebook.ipynb`（指定文件）
   - `https://github.com/username/repo/tree/dev`（指定分支）
3. 实时解析结果会显示在输入框下方
4. 点击 "Launch" 按钮
5. 等待构建完成（首次构建可能需要数十秒到数分钟）
6. 自动进入 JupyterLab 界面

### URL 格式

BinderLite 直接访问 URL 格式：

```
http://localhost:8000/v1/gh/{user}/{repo}/{ref}/{path}
```

示例：
- `http://localhost:8000/v1/gh/username/repo/HEAD/lab/index.html`
- `http://localhost:8000/v1/gh/username/repo/main/lab/index.html?path=notebook.ipynb`

## 步骤7：了解构建产物

构建成功后，`output/` 目录下会生成按 slug 组织的构建产物：

```
output/
└── gh-username/
    └── repo/
        └── abc1234def5678.../     # commit SHA作为目录名
            ├── .completed-sentinel # 构建完成标记
            ├── lab/
            │   └── index.html
            ├── pyodide/           # 或 xeus/
            ├── kernels/
            ├── content/
            ├── index.html
            └── ...
```

已构建的站点可以直接通过 `/render/` 路径访问，不经过动态构建逻辑：

```
http://localhost:8000/render/gh-username/repo/abc1234.../lab/index.html
```

## 开发模式工作流

如果需要修改代码：

1. **后端修改**：使用 `uvicorn --reload`，修改Python文件后自动重载
2. **前端修改**：运行 `npm run watch` 监听文件变更自动重新打包
3. **清理构建缓存**：删除 `output/` 目录可强制重新构建
   ```bash
   rm -rf output/
   ```

## 生产部署注意事项

1. **使用 Gunicorn + Uvicorn workers**：
   ```bash
   gunicorn binderlite.run:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
   ```

2. **配置反向代理**：使用 Nginx 作为前端代理，处理 SSL、静态文件缓存和请求缓冲

3. **构建产物存储**：本地文件系统适合单实例部署；多实例部署需要使用共享存储或实现 S3 Publisher

4. **磁盘空间管理**：构建产物会持续累积，需要定期清理 `output/` 目录中旧的构建

5. **Rate Limit**：配置 `GITHUB_ACCESS_TOKEN` 以提高 API 配额，避免用户遇到 rate limit 错误

## 相关概念

- [03-BinderLite Web应用](../concepts/03-binderlite-web.md)
- [05-Publisher存储系统](../concepts/05-publisher-system.md)
- [06-构建流程与缓存策略](../concepts/06-build-process.md)
- [08-整体架构总结](../concepts/08-architecture-summary.md)
