# 核心概念索引

本目录包含 pytest-jupyter 的核心概念文档，按学习路径顺序排列。

## 文档列表

### 入门篇

| 文档 | 内容 |
|------|------|
| [简介](00-introduction.md) | pytest-jupyter 定位、三层插件架构、核心能力一览、项目信息 |
| [5分钟快速上手](01-getting-started.md) | 安装、conftest配置、第一个测试、常见问题 |

### 架构篇

| 文档 | 内容 |
|------|------|
| [架构总览](02-architecture-overview.md) | 模块结构、插件加载机制、fixture依赖DAG、异步测试架构、设计哲学 |
| [Fixture工厂模式](08-fixture-factories.md) | 工厂fixture设计模式、闭包机制、资源追踪、自定义工厂模板 |

### 插件详解篇

| 文档 | 内容 |
|------|------|
| [Core插件详解](03-core-plugin.md) | 环境隔离(jp_environ)、asyncio事件循环、异步测试pytest钩子、临时目录fixtures |
| [Client插件详解](04-client-plugin.md) | 内核启动工厂(jp_start_kernel)、ZMQ上下文管理、资源自动清理 |
| [Server插件详解](05-server-plugin.md) | ServerApp生命周期、jp_fetch/jp_ws_fetch HTTP客户端、认证测试、自动清理 |
| [Tornado异步测试支持](06-tornasync-plugin.md) | 内嵌pytest-tornasync、IOLoop桥接、HTTP服务器/客户端、端口管理 |

### 深度专题

| 文档 | 内容 |
|------|------|
| [Echo测试内核](07-echo-kernel.md) | EchoKernel实现原理、do_execute方法、stdin处理、kernelspec、扩展方式 |

## 学习路径推荐

### 路径1：测试Jupyter Server扩展（最常见）

简介 → 快速上手 → 架构总览 → Core插件 → Server插件 → Fixture工厂模式 → [Server API测试示例](/examples/03-server-api-test.md)

### 路径2：测试Jupyter内核

简介 → 快速上手 → 架构总览 → Core插件 → Client插件 → Echo内核 → [内核测试示例](/examples/02-kernel-testing.md)

### 路径3：测试Jupyter基础工具（不涉及网络）

简介 → 快速上手 → Core插件 → [基础测试示例](/examples/01-basic-core-test.md)
