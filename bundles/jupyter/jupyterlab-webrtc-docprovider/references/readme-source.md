---
type: Reference
title: README与用户文档源码
description: README.md中的安装说明、使用指南、配置说明，CONTRIBUTING.md中的开发流程
tags: [readme, install, user-guide, configuration, development]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T07:06:00Z" }
verified: { by: "process:grep-verify", at: "2026-08-22T07:10:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: readme-md
    resource: https://github.com/jupyterlite/jupyterlab-webrtc-docprovider/blob/main/README.md
    title: README.md - User documentation
  - id: contributing-md
    resource: https://github.com/jupyterlite/jupyterlab-webrtc-docprovider/blob/main/CONTRIBUTING.md
    title: CONTRIBUTING.md - Development guide
---

## README.md 用户文档要点

### 工作原理

不同于 JupyterLab 内置的纯 WebSocket 协作方案，jupyterlab-webrtc-docprovider 依赖：
1. **信令服务器**（Signaling Server）：用于定位 peer
2. **WebRTC 协议**：协调实际的数据交换

### 服务器配置

```json
{
  "LabServerApp": {
    "collaborative": true
  }
}
```

JupyterLite 中在 `jupyter-lite.json` 的 `jupyter-config-data` 中配置。

### 客户端配置

通过 `overrides.json` 预配置用户设置：

```json
{
  "@jupyterlite/webrtc-docprovider:plugin": {
    "disabled": false,
    "room": "a pre-shared room name",
    "roomPrefix": "a-very-unique-name",
    "signalingUrls": [
      "wss://y-webrtc-signaling-eu.herokuapp.com",
      "wss://y-webrtc-signaling-us.herokuapp.com",
      "wss://signaling.yjs.dev"
    ],
    "usercolor": "f57c00",
    "username": "Jo V. Un"
  }
}
```

### 使用步骤

1. 安装扩展
2. 配置服务器启用 collaborative
3. 启动 JupyterLab/Lumino 客户端
4. 使用 `?room=` URL 参数打开
5. 可选：`?username=` 和 `?usercolor=`
6. 打开共享编辑活动（Notebook 或 Editor）

### 安全注意

README 特别提醒：信令服务器仅知晓高层元数据，受 SSL 保护；但生产部署不应依赖免费托管服务。

## CONTRIBUTING.md 开发指南要点

### 开发安装

```bash
python -m pip install -e .
jupyter labextension develop . --overwrite
jlpm build
```

### Watch 模式

```bash
# 终端1
jlpm watch
# 终端2
jupyter lab --no-browser --debug --expose-app-in-browser
```

`--expose-app-in-browser` 将 app 实例暴露到全局 `window.jupyterapp`，方便浏览器调试。

### 开发卸载

```bash
pip uninstall jupyterlab-webrtc-docprovider
# 还需移除 labextension develop 创建的符号链接
jupyter labextension list  # 查找链接位置
```

## 相关概念

- [安装与快速开始](/concepts/01-getting-started.md)
- [配置三级优先级系统](/concepts/09-configuration.md)
- [构建与打包系统](/concepts/10-build-and-packaging.md)
