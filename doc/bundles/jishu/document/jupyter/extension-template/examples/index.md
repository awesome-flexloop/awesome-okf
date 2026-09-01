# 实战示例（Examples）

按扩展类型组织的实操示例，提供完整可运行的代码。建议在阅读对应概念文档后动手实践。

## 示例列表

| 编号 | 示例 | 对应类型 | 涉及概念 |
|------|------|---------|---------|
| 01 | [你的第一个前端扩展（Hello World）](01-hello-world.md) | frontend | 命令注册、Widget 创建、命令面板 |
| 02 | [全栈扩展：前后端通信](02-full-stack-server.md) | frontend-and-server | APIHandler、requestAPI、GET/POST 请求 |
| 03 | [自定义 MIME 渲染器](03-mime-renderer.md) | mimerenderer | IRenderMime、自定义数据渲染、文件类型注册 |
| 04 | [创建自定义暗色主题](04-custom-dark-theme.md) | theme | CSS 变量覆盖、暗色主题适配、滚动条样式 |

## 前置准备

所有示例都需要：
- Python 3.10+
- Node.js LTS
- JupyterLab 4.0.0+
- Copier 9.2+

安装方法参考 [快速开始](../concepts/01-getting-started.md)。

## 运行示例的通用步骤

1. 使用 Copier 生成项目（选择对应的扩展类型）
2. `pip install -e ".[dev]"` 安装 Python 包
3. `jupyter-builder develop . --overwrite` 链接扩展
4. `jlpm install` 安装 JS 依赖
5. `jlpm build` 或 `jlpm run watch` 构建
6. `jupyter lab` 启动 JupyterLab

```{toctree}
:hidden:
:maxdepth: 7

01-hello-world
02-full-stack-server
03-mime-renderer
04-custom-dark-theme
```
