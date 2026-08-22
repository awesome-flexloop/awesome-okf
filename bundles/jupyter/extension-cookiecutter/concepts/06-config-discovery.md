---
type: Concept
title: 配置发现机制
description: 理解 Jupyter Server 扩展的自动发现机制——jupyter-config 目录、shared-data 安装、JSON 配置文件，以及为什么 pip install 后扩展自动启用。
tags: [configuration, discovery, jupyter-config, shared-data, auto-enable]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T13:10:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T13:10:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: pyproject
    resource: /references/pyproject-source.md
    title: pyproject.toml 模板字段全解析
---

## 自动发现问题

传统 Python 包安装后，用户需要手动启用扩展：

```bash
# 没有自动发现时，每次安装都要手动启用
jupyter server extension enable my_extension
```

Jupyter 通过**配置发现机制**实现 pip install 后扩展自动启用，无需手动操作。理解这个机制是开发 Jupyter Server 扩展的关键。

## 核心原理：配置即发现

Jupyter Server 启动时会扫描标准目录下的配置文件，自动加载其中声明的扩展配置。关键配置目录是：

```
{sys.prefix}/etc/jupyter/jupyter_server_config.d/
```

安装在同一个 Python 环境（同一个 sys.prefix）中的扩展，如果将 JSON 配置文件放入此目录，Jupyter Server 启动时就会读取该配置并自动启用扩展。

## 模板中的实现

模板通过三部分协作实现自动发现：

### 1. jupyter-config 目录

项目源码中包含配置文件：

```
my_server_extension/
└── jupyter-config/
    └── jupyter_server_config.d/
        └── my_server_extension.json
```

JSON 配置内容：

```json
{
  "ServerApp": {
    "jpserver_extensions": {
      "my_server_extension": true
    }
  }
}
```

此 JSON 告诉 Jupyter Server：在 ServerApp 的 jpserver_extensions 配置中，将 `my_server_extension` 设为 `true`（启用）。

### 2. pyproject.toml 的 shared-data 配置

```toml
[tool.hatch.build.targets.wheel.shared-data]
"jupyter-config" = "etc/jupyter"
```

这是 hatchling 构建后端的配置，含义是：
- 将源目录 `jupyter-config/`（包含 `jupyter_server_config.d/` 子目录）
- 安装到 wheel 包的 `etc/jupyter/` 路径
- pip install 时，wheel 中的 `etc/jupyter/` 会被解压到 `{sys.prefix}/etc/jupyter/`

最终效果：`pip install my_server_extension` 后，文件被安装到：

```
{sys.prefix}/etc/jupyter/jupyter_server_config.d/my_server_extension.json
```

### 3. Jupyter Server 启动扫描

Jupyter Server 启动流程：

```
jupyter server 启动
  │
  ├─ 确定 sys.prefix（当前 Python 环境根目录）
  │
  ├─ 扫描 {sys.prefix}/etc/jupyter/jupyter_server_config.d/*.json
  │    └─ 找到 my_server_extension.json
  │
  ├─ 加载 JSON 配置
  │    └─ ServerApp.jpserver_extensions = {"my_server_extension": true}
  │
  ├─ 遍历 jpserver_extensions 中值为 true 的扩展
  │    ├─ 导入模块 import my_server_extension
  │    ├─ 调用 _jupyter_server_extension_points() 获取 ExtensionApp 类
  │    └─ 初始化并启动扩展
  │
  └─ 扩展已就绪，可以接收请求
```

## 为什么不需要手动 enable

理解了上面的流程，就明白为什么 `pip install` 后扩展自动启用：

1. **wheel 安装配置文件**：pip 将 `jupyter-config/` 下的 JSON 放到 `{sys.prefix}/etc/jupyter/`
2. **Jupyter Server 自动扫描**：启动时读取该目录下所有 JSON
3. **配置中声明启用**：JSON 中 `jpserver_extensions.{ext_name}: true` 告诉 Server 启用该扩展

## 手动启用与禁用

虽然配置文件自动启用了扩展，用户仍可以手动控制：

```bash
# 查看已安装扩展状态
jupyter server extension list

# 手动启用（如果自动发现失败或被禁用）
jupyter server extension enable my_server_extension

# 手动禁用
jupyter server extension disable my_server_extension
```

禁用后，即使配置文件存在，扩展也不会加载（用户配置优先级高于系统配置）。

## jupyter-config 目录结构规范

Jupyter 生态中不同项目使用不同的配置子目录：

| 目录 | 用途 |
|------|------|
| `jupyter-config/jupyter_server_config.d/` | Jupyter Server 扩展配置 |
| `jupyter-config/jupyter_notebook_config.d/` | Jupyter Notebook 扩展配置（经典 Notebook） |
| `jupyter-config/nbconfig/` | Notebook 前端配置（已弃用） |

对于 Jupyter Server 扩展（本模板生成的类型），只需要 `jupyter_server_config.d/`。

## 配置文件格式

JSON 配置文件的顶层键对应 Jupyter 可配置类的类名（去掉前缀 `c.`）：

```json
{
  "ServerApp": {
    "jpserver_extensions": {
      "my_extension": true
    }
  },
  "Extension": {
    "ping_response": "hello"
  }
}
```

等价于 Python 配置文件（`jupyter_server_config.py`）：

```python
c.ServerApp.jpserver_extensions = {"my_extension": True}
c.Extension.ping_response = "hello"
```

JSON 配置适用于包自动安装的默认配置；用户自定义配置通常使用 Python 格式（`jupyter_server_config.py`），支持更丰富的逻辑。

## 其他构建后端的 shared-data 配置

如果使用 setuptools 而非 hatchling，需要在 setup.cfg 或 setup.py 中配置 data_files：

```python
# setup.py (setuptools)
from setuptools import setup
import sys

setup(
    name="my_extension",
    data_files=[
        ("etc/jupyter/jupyter_server_config.d", ["jupyter-config/jupyter_server_config.d/my_extension.json"]),
    ],
)
```

但本模板使用 hatchling，配置更简洁。

## 开发模式下的自动发现

使用 `pip install -e .` 开发模式安装时，hatchling 会创建一个 `.pth` 文件或直接链接，确保 jupyter-config 文件也被正确安装到 `{sys.prefix}/etc/jupyter/`。这也是为什么开发安装后 `jupyter server extension list` 能看到扩展。

## 故障排查

如果扩展安装后未被发现，按以下步骤排查：

1. **检查配置文件位置**：
   ```bash
   ls {sys.prefix}/etc/jupyter/jupyter_server_config.d/
   # 在 conda 环境中，sys.prefix 通常是 ~/miniconda3/envs/<env_name>
   ```

2. **验证 JSON 格式**：
   ```bash
   python -c "import json; json.load(open('{sys.prefix}/etc/jupyter/jupyter_server_config.d/my_extension.json'))"
   ```

3. **检查扩展列表**：
   ```bash
   jupyter server extension list
   ```

4. **检查扩展能否正常导入**：
   ```bash
   python -c "import my_extension; print(my_extension._jupyter_server_extension_points())"
   ```

## 相关概念

- [项目结构详解](/concepts/03-project-structure.md)
- [构建系统详解](/concepts/08-build-system.md)
- [pyproject.toml 模板字段解析](/references/pyproject-source.md)
