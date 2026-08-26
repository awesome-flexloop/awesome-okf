# 核心概念索引

| 序号 | 文档 | 一句话简介 |
|------|------|-----------|
| 00 | [简介](00-introduction.md) | jupyterlab-github 在 JupyterLab 生态中的定位、只读设计理念、双组件架构概览 |
| 01 | [安装与快速上手](01-getting-started.md) | pip 安装、Access Token 获取与配置、启动浏览、默认仓库设置、速率限制说明 |
| 02 | [架构总览](02-architecture-overview.md) | 双组件架构、Contents.IDrive 虚拟文件系统模式、请求路由、四层结构与数据流 |
| 03 | [GitHubDrive 虚拟文件系统](03-github-drive.md) | GitHubDrive 类详解、路径解析、四级导航、大文件 Blob 降级、仓库列表三级降级、格式转换、base64 解码 |
| 04 | [浏览器 UI 组件与交互](04-browser-ui.md) | GitHubFileBrowser、GitHubUserInput、GitHubErrorPanel 三个控件、工具栏按钮、MyBinder 集成、事件循环防循环机制 |
| 05 | [服务端代理与认证](05-server-proxy.md) | GitHubHandler Tornado 代理、Token 安全机制、Link 头分页自动聚合、扩展注册与自动启用 |
| 06 | [配置与设置系统](06-configuration.md) | 前端设置 Schema（baseUrl/accessToken/defaultRepo）、服务端 traitlets 配置、Token 优先级、GitHub Enterprise 支持 |

```{toctree}
:maxdepth: 7

00-introduction
01-getting-started
02-architecture-overview
03-github-drive
04-browser-ui
05-server-proxy
06-configuration
```
