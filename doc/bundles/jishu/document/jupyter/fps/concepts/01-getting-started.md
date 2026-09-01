---
type: Concept
title: 安装与快速开始
description: FPS的安装方法、CLI命令用法，以及创建和运行第一个FPS应用的完整指南。
tags: [getting-started, installation, cli, first-app]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T14:52:00+08:00" }
verified: { by: "process:grep-api-verify", at: "2026-08-22T14:52:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: fps-cli-py
    resource: /references/cli-source.md
    title: src/fps/cli/_cli.py
  - id: fps-module-py
    resource: /references/module-source.md
    title: src/fps/_module.py
---

## 安装

FPS 发布在 PyPI 和 conda-forge 上，可以通过 pip 或 conda/mamba 安装。

### 使用 pip 安装

```bash
pip install fps
```

安装含Web支持（FastAPI + anycorn）：

```bash
pip install "fps[fastapi,anycorn]"
```

开发模式安装（含测试和文档依赖）：

```bash
git clone https://github.com/jupyter-server/fps.git
cd fps
pip install -e ".[fastapi,anycorn,test,docs]"
```

### 使用 conda/mamba 安装

```bash
micromamba install fps
```

## CLI 命令

安装后可使用 `fps` 命令启动应用。

### 基本用法

```bash
fps <module_path> [options]
```

`<module_path>` 指定要运行的根模块，支持两种格式：
- Python路径格式：`文件名:类名`（如 `simple:Main`）
- entry-point名称：在 `fps.modules` 组中注册的名称（如 `fps_module`）

### CLI 选项

| 选项 | 说明 |
|------|------|
| `--config <file>` | 指定JSON配置文件路径 |
| `--set key=value` | 设置模块参数（可多次使用），key支持点分路径如 `module.param` |
| `--show-config` | 显示实际配置参数后启动 |
| `--help-all` | 显示所有配置参数的描述信息（基于Pydantic字段元数据） |
| `--backend asyncio\|trio` | 选择事件循环后端，默认 `asyncio` |
| `--timeout <seconds>` | 设置prepare+start阶段总超时 |
| `--stop-timeout <seconds>` | 设置stop阶段超时，默认1秒 |

## 第一个 FPS 应用

创建一个最简单的FPS应用，体验模块的生命周期。

### 步骤1：创建应用文件

创建 `simple.py`：

```python
from fps import Module

class Main(Module):
    def __init__(self, name, **kwargs):
        super().__init__(name)
        self.greeting = kwargs.get("greeting", "Hello!")
        self.farewell = kwargs.get("farewell", "Goodbye!")

    async def start(self):
        print(self.greeting)

    async def stop(self):
        print(self.farewell)
```

### 步骤2：运行应用

```bash
fps simple:Main --set greeting="Hello, World!" --set farewell="See you later!"
```

输出：
```
Hello, World!
```

应用会持续运行，按 `Ctrl+C` 停止：
```
See you later!
```

### 发生了什么

1. `fps simple:Main` 告诉FPS加载 `simple.py` 中的 `Main` 类作为根模块
2. `--set greeting="Hello, World!"` 将 `greeting` 参数传递给 `Main.__init__`
3. 框架执行 `prepare` 阶段（Main未覆盖，使用空实现）
4. 框架执行 `start` 阶段，调用 `Main.start()` 打印问候语
5. 应用进入运行状态，等待退出信号
6. 按Ctrl+C触发 `stop` 阶段，调用 `Main.stop()` 打印告别语

## 使用JSON配置文件

对于复杂的模块树，可以使用JSON配置文件替代CLI参数。

创建 `config.json`：

```json
{
  "main": {
    "type": "simple:Main",
    "config": {
      "greeting": "Hello from config!",
      "farewell": "Goodbye from config!"
    }
  }
}
```

运行：

```bash
fps --config config.json
```

### 选择子模块作为根

如果配置文件包含多个顶层模块，可以指定模块名选择其中一个作为根：

```bash
fps --config config.json main
```

## 查看配置帮助

使用 `--help-all` 可以自动生成配置参数文档（需要模块使用Pydantic model定义config）：

```bash
fps simple:Main --help-all
```

## 事件循环后端

FPS支持asyncio（默认）和trio两种后端：

```bash
fps simple:Main --backend trio
```

## 相关概念

- [FPS简介](00-introduction.md)
- [模块系统](02-module-system.md)
- [配置系统](05-configuration-system.md)
- [可插拔Web服务器](07-web-modules.md)
- [第一个Web应用](../examples/03-web-server.md)
