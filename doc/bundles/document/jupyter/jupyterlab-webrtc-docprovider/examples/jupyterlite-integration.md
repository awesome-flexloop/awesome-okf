---
type: Example
title: JupyterLite集成配置
description: 在JupyterLite静态部署中配置和使用jupyterlab-webrtc-docprovider实现无服务器P2P协作
tags: [jupyterlite, static-deployment, p2p, browser-only, configuration]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T07:06:00Z" }
verified: { by: "process:grep-verify", at: "2026-08-22T07:10:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: readme
    resource: /references/readme-source.md
    title: README.md - JupyterLite configuration notes
  - id: config
    resource: /concepts/09-configuration.md
    title: 配置三级优先级系统
---

## JupyterLite 集成配置

JupyterLite 是 JupyterLab 的浏览器端静态部署版本，不需要后端 Jupyter Server。jupyterlab-webrtc-docprovider 最初就是从 JupyterLite 项目中提取的，因此对 JupyterLite 有原生支持。

## JupyterLite 中的协作特点

- **无需服务器中转**：文档同步完全通过 WebRTC P2P 实现
- **静态托管**：可部署到 GitHub Pages、Netlify、S3 等静态托管服务
- **信令服务器仍然需要**：用于 peer 发现（但可使用公共服务器或部署私有服务器）

## 步骤1：安装扩展到 JupyterLite

使用 `jupyter-lite` CLI 添加扩展：

```bash
# 安装 jupyterlite
pip install jupyterlite

# 添加 webrtc-docprovider 扩展
pip install jupyterlab-webrtc-docprovider

# 构建 JupyterLite 站点
jupyter lite build
```

或者使用 `--piplite` 在运行时安装（如果支持）：

```python
# 在 JupyterLite 的 notebook 中
import piplite
await piplite.install('jupyterlab-webrtc-docprovider')
```

## 步骤2：配置 jupyter-lite.json

在 JupyterLite 构建目录中创建/编辑 `jupyter-lite.json`：

```json
{
  "jupyter-config-data": {
    "collaborative": true,
    "fullWebRtcSignalingUrls": [
      "wss://signaling.yjs.dev",
      "wss://y-webrtc-signaling-eu.herokuapp.com"
    ],
    "webRtcRoomPrefix": "my-jupyterlite-demo-2024"
  }
}
```

### 配置项说明

| 配置项 | 类型 | 说明 |
|--------|------|------|
| `collaborative` | boolean | 必须设为 `true` 启用协作 |
| `fullWebRtcSignalingUrls` | string[] | 信令服务器 URL 列表 |
| `webRtcRoomPrefix` | string | 房间前缀（建议设置唯一值） |

## 步骤3：配置 overrides.json（可选）

创建 `overrides.json` 预设用户设置：

```json
{
  "@jupyterlite/webrtc-docprovider:plugin": {
    "disabled": false,
    "room": "jupyterlite-default",
    "username": null,
    "usercolor": null
  }
}
```

放置在 JupyterLite 构建输出的 `lab/settings/overrides.json` 路径。

## 步骤4：构建和部署

```bash
# 构建（包含 webrtc-docprovider 扩展）
jupyter lite build --output-dir dist

# 部署到静态托管（示例：使用 Python 本地预览）
cd dist
python -m http.server 8000
```

访问 `http://localhost:8000/lab?room=demo` 测试协作。

## JupyterLite URL 参数使用

与标准 JupyterLab 相同，支持 URL 参数：

```
https://your-jupyterlite.github.io/lab?room=team-meeting&username=Alice&usercolor=4caf50
```

## GitHub Pages 部署示例

```bash
# .github/workflows/deploy.yml
name: Deploy JupyterLite
on:
  push:
    branches: [main]
jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install jupyterlite jupyterlab-webrtc-docprovider
      - run: jupyter lite build
      - uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./_output
```

## 注意事项

1. **HTTPS 要求**：WebRTC 在非 localhost 的 HTTP 环境下可能不工作。GitHub Pages 等平台默认提供 HTTPS。
2. **信令服务器可用性**：公共信令服务器（Heroku）可能不稳定，生产部署建议使用私有信令服务器。
3. **localhost 房间隔离**：在 localhost 上部署时，roomPrefix 自动使用随机 UUID，不同开发者不会意外连接。
4. **文件持久化**：JupyterLite 中的文件存储在浏览器 IndexedDB 中，不同 peer 的文档通过 CRDT 同步，但文件本身不会自动持久化到服务器。
5. **房间名共享**：由于静态部署 URL 固定，使用 `?room=` 参数是创建不同协作会话的主要方式。

## 与标准 JupyterLab 的差异

| 特性 | JupyterLab | JupyterLite |
|------|-----------|-------------|
| 后端 | Jupyter Server（Python） | 无后端（浏览器端） |
| 内核 | 本地/远程内核 | Pyodide（浏览器内 Python） |
| collaborative 配置 | jupyter_server_config.json | jupyter-lite.json |
| 文件存储 | 服务器文件系统 | IndexedDB（浏览器） |
| 扩展安装 | pip/conda | jupyter lite build |
| WebRTC 支持 | ✅ | ✅（原生支持，无后端依赖） |

## 相关概念

- [配置三级优先级系统](/concepts/09-configuration.md)
- [房间ID与信令机制](/concepts/05-room-and-signaling.md)
- [安装与快速开始](/concepts/01-getting-started.md)
- [自定义信令服务器部署](/examples/custom-signaling-server.md)
