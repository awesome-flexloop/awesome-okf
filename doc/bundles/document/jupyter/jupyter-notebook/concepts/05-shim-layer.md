---
title: 配置兼容层（notebook_shim）
type: concept
bundle: jupyter-notebook
chapter: "05"
difficulty: advanced
tags: ["backend", "shim", "compatibility", "configuration", "migration"]
prerequisites: ["02-backend-app"]
sources: ["F-014"]
next: ["11-migration-guide"]
related: ["references/00-source-registry"]
---

# 05 | 配置兼容层：notebook_shim

Notebook v7 通过外部包 `notebook_shim` 提供v6配置兼容层，使得大量现有的 `jupyter_notebook_config.py` 文件在v7下仍能工作。

## 为什么需要Shim层

Notebook 6.x是独立的Tornado应用，所有配置都在 `c.NotebookApp.*` 下。Notebook 7.x基于Jupyter Server和JupyterLab，配置被拆分到了不同的应用类：

| v6配置 | v7配置 | 说明 |
|--------|--------|------|
| `c.NotebookApp.port` | `c.ServerApp.port` | 服务器端口 |
| `c.NotebookApp.notebook_dir` | `c.ServerApp.root_dir` | 工作目录 |
| `c.NotebookApp.open_browser` | `c.LabServerApp.open_browser` | 是否自动打开浏览器 |
| `c.NotebookApp.ip` | `c.ServerApp.ip` | 监听IP |
| `c.NotebookApp.token` | `c.ServerApp.token` | 认证token |
| `c.NotebookApp.password` | `c.ServerApp.password` | 密码哈希 |
| `c.NotebookApp.allow_origin` | `c.ServerApp.allow_origin` | CORS允许源 |
| `c.NotebookApp.disable_check_xsrf` | `c.ServerApp.disable_check_xsrf` | 禁用XSRF检查 |
| `c.NotebookApp.base_url` | `c.ServerApp.base_url` | 基础URL前缀 |

如果用户直接升级到v7，所有旧配置都会失效。Shim层的作用就是**透明地将旧配置映射到新配置**。

## ShimMixin 的位置

```python
# notebook/app.py
from notebook_shim.shim import NotebookConfigShimMixin

class JupyterNotebookApp(NotebookConfigShimMixin, LabServerApp):
```

> **信源**: [app.py:L32,L242](../references/00-source-registry.md#S-004)（F-014）

关键观察：
1. `NotebookConfigShimMixin` **不在notebook包内**，而是来自独立的 `notebook_shim` 包
2. 这意味着shim层可以独立发布、独立更新，不受Notebook版本约束
3. Mixin通过Python MRO在类继承链中插入配置映射逻辑

## notebook_shim 包结构

虽然notebook_shim是外部依赖，但从其在app.py中的使用方式可以推断其核心功能：

```python
# notebook_shim 包提供的核心内容（基于import推断）
notebook_shim/
└── shim.py
    └── class NotebookConfigShimMixin:
            # 定义v6 traitlets别名
            # 将c.NotebookApp.*映射到c.ServerApp.* / c.LabServerApp.*
            # 提供配置迁移警告
```

版本要求：`notebook_shim>=0.2.4`（来自pyproject.toml F-003）。

## Mixin工作原理

`traitlets` 配置系统支持**别名（aliases）**和**特性转发**。NotebookConfigShimMixin大致做以下事情：

### 1. 定义v6风格的trait别名

```python
# notebook_shim/shim.py 的概念性实现
from traitlets import Unicode, Int, Bool, observe
from jupyter_server.serverapp import ServerApp

class NotebookConfigShimMixin:
    """A mixin for shimming Notebook 6.x config to Jupyter Server."""

    # 将旧配置名映射为新配置名
    port = Int(None, allow_none=True).tag(config=True)
    notebook_dir = Unicode(None, allow_none=True).tag(config=True)
    # ... 更多v6配置项

    @observe('port')
    def _port_changed(self, change):
        if change['new'] is not None:
            self.serverapp.port = change['new']
            self.log.warning(
                "NotebookApp.port is deprecated in Notebook 7, use ServerApp.port"
            )
```

这是一个概念性示例——实际实现可能使用traitlets的 `aliases` 机制或属性描述符。

### 2. 配置文件兼容

Shim层使得以下配置文件仍能被识别：
- `jupyter_notebook_config.py` → 自动映射到ServerApp/LabServerApp配置
- 命令行 `--NotebookApp.port=8888` → 转发到ServerApp.port

### 3. 弃用警告

当用户使用旧配置名时，Shim层会输出弃用警告，引导用户迁移到新配置名。

## 相关的Shim：nbclassic

除了 `notebook_shim` 提供配置兼容外，还有一个相关项目 `nbclassic`：

```python
nbclassic_enabled = self.server_extension_is_enabled("nbclassic")
page_config["nbclassic_enabled"] = nbclassic_enabled
```

> **信源**: [app.py:L330-331](../references/00-source-registry.md#S-004)

nbclassic提供了Notebook 6.x的**完整UI复刻**，在v7的JupyterLab基座上运行经典界面。前端通过 `nbclassic_enabled` 标志检测是否安装了nbclassic，并可能显示切换提示。

## 配置迁移策略

### 新项目（推荐）

直接使用v7原生配置，不依赖shim层：

```python
# jupyter_server_config.py 或 jupyter_notebook_config.py
c.ServerApp.port = 8888
c.ServerApp.root_dir = "/home/user/notebooks"
c.ServerApp.token = ""
c.ServerApp.password = ""
c.LabServerApp.open_browser = True
```

### 现有项目（渐进迁移）

1. 短期：旧配置继续工作（通过shim层），注意观察弃用警告
2. 中期：将 `c.NotebookApp.*` 逐项替换为 `c.ServerApp.*` 或 `c.LabServerApp.*`
3. 长期：完全移除对notebook_shim的依赖（虽然它会一直存在以保证向后兼容）

### 配置文件选择

v7会读取以下配置文件（优先级从高到低）：

1. `~/.jupyter/jupyter_server_config.py`（推荐，v7原生）
2. `~/.jupyter/jupyter_notebook_config.py`（兼容，通过shim层）
3. 系统级配置（如 `/etc/jupyter/`）

建议新配置写入 `jupyter_server_config.py`，旧配置可以保留在 `jupyter_notebook_config.py` 中直到完全迁移。

## CLI命令兼容

v7保留了 `jupyter notebook` 命令作为入口，但底层实际启动的是Jupyter Server + Notebook扩展：

```bash
# v6和v7都支持的命令
jupyter notebook                          # 启动Notebook
jupyter notebook --port=9999              # 指定端口（v6/v7都支持）
jupyter notebook --no-browser             # 不打开浏览器
jupyter notebook --NotebookApp.port=9999  # v6风格（v7通过shim兼容）
```

v7推荐的新方式：
```bash
jupyter server --ServerApp.jpserver_extensions="{'notebook': True}"
```

但 `jupyter notebook` 命令会一直保留作为便捷入口。

## 扩展开发者注意事项

如果你在开发Notebook/JupyterLab扩展，需要注意：

1. **不要依赖 `c.NotebookApp.*` 配置名**：始终使用扩展自己的配置节，或使用 `c.ServerApp.*`
2. **不要假设Notebook是唯一前端**：JupyterLab、Retrolab、nbclassic都可以作为Jupyter Server的前端
3. **配置名检查**：如果你的扩展读取配置，应同时检查新旧配置名，并给出迁移提示

```python
# 扩展配置兼容示例
@property
def my_setting(self):
    # 优先新配置名
    value = self.config.get("MyExtension", {}).get("my_setting")
    if value is not None:
        return value
    # 回退旧配置名（v6兼容）
    old_value = self.config.get("NotebookApp", {}).get("my_old_setting")
    if old_value is not None:
        self.log.warning("NotebookApp.my_old_setting is deprecated, use MyExtension.my_setting")
        return old_value
    return default_value
```

## 为什么Shim层是独立包

将shim层独立为 `notebook_shim` 包有几个好处：

1. **独立迭代**：shim的bug修复和配置映射更新不需要发布Notebook新版本
2. **多前端共享**：nbclassic等其他基于Jupyter Server的前端也可以复用notebook_shim
3. **可选依赖**：理论上，不需要v6兼容的用户可以不安装notebook_shim（但当前它是硬依赖）
4. **职责清晰**：Notebook核心代码专注于v7原生功能，兼容代码分离维护

## 下一步

- → [v6到v7迁移指南](11-migration-guide.md) 完整的迁移检查清单和常见问题
- → [JupyterHub集成](07-jupyterhub-integration.md) 多用户环境配置
