---
okf_version: "0.2"
type: reference
title: "配置系统源码（config.py）"
description: "jupyterlab_server/config.py 中 LabConfig 配置类、页面配置构建、联邦扩展发现和 ConfigManager 多级配置的完整 API"
tags: [config, labconfig, traitlets, page-config, federated-extensions, config-manager]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T12:30:00Z" }
verified: { by: "process:source-code-to-okf-wiki-v", at: "2026-08-22T12:30:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: config-py
    resource: "../../../../../external/libs/jupyter/jupyterlab_server/jupyterlab_server/config.py"
    title: "jupyterlab_server/config.py"
---

# 配置系统源码（config.py）

本信源登记 `jupyterlab_server/config.py`（约403行）的核心类、函数和常量。config.py 提供 jupyterlab_server 的配置基础设施，包括 `LabConfig` 配置类、页面配置构建和联邦扩展发现机制。

## 模块常量

```python
DEFAULT_TEMPLATE_PATH = osp.join(osp.dirname(__file__), "templates")
```

包内 templates 目录的绝对路径，作为 `templates_dir` 的默认值。

## LabConfig 类

```python
class LabConfig(HasTraits):
```

配置混入类（Mixin），定义所有 Lab 应用相关的配置 traitlets。被 `LabServerApp`、`ProcessApp`、`WorkspaceListApp` 等继承。

### 目录配置 Traitlets

| Trait | 类型 | 默认值来源 | 说明 |
|-------|------|-----------|------|
| `app_settings_dir` | Unicode | `""` | 应用设置目录（page_config.json、overrides.json等） |
| `templates_dir` | Unicode | `DEFAULT_TEMPLATE_PATH` | Jinja2模板目录 |
| `static_dir` | Unicode | `""` | 静态文件目录（JS/CSS等） |
| `user_settings_dir` | Unicode | `""` | 用户设置覆盖目录 |
| `schemas_dir` | Unicode | `""` | JSON Schema目录 |
| `workspaces_dir` | Unicode | `""` | 工作区保存目录 |
| `themes_dir` | Unicode | `""` | 主题文件目录 |
| `labextensions_path` | List(Unicode) | `jupyter_path("labextensions")` | 联邦扩展搜索路径列表 |
| `extra_labextensions_path` | List(Unicode) | `[]` | 额外联邦扩展路径 |

### URL 配置 Traitlets

| Trait | 类型 | 默认值 | 说明 |
|-------|------|--------|------|
| `app_url` | Unicode | `"/lab"` | 应用根URL |
| `labextensions_url` | Unicode | `"{app_url}/extensions/"` | 联邦扩展静态资源URL |
| `settings_url` | Unicode | `"{app_url}/api/settings/"` | 设置API URL |
| `workspaces_api_url` | Unicode | `"{app_url}/api/workspaces/"` | 工作区API URL |
| `listings_url` | Unicode | `"{app_url}/api/listings/"` | 扩展列表API URL |
| `themes_url` | Unicode | `"{app_url}/api/themes/"` | 主题API URL |
| `licenses_url` | Unicode | `"{app_url}/api/licenses/"` | 许可证API URL |
| `translations_api_url` | Unicode | `"{app_url}/api/translations/"` | 翻译API URL |
| `tree_url` | Unicode | `"{app_url}/tree/"` | 文件树URL |

### 其他配置 Traitlets

| Trait | 类型 | 默认值 | 说明 |
|-------|------|--------|------|
| `app_name` | Unicode | `""` | 应用名称 |
| `app_version` | Unicode | `""` | 应用版本 |
| `app_namespace` | Unicode | `""` | 应用命名空间 |
| `cache_files` | Bool | `True` | 是否缓存文件（开发模式下设False） |
| `notebook_starts_kernel` | Bool | `True` | 打开Notebook时是否自动启动内核 |
| `copy_absolute_path` | Bool | `False` | 复制路径时使用绝对路径还是相对路径 |

### 默认值方法

所有URL traitlets 通过 `@default` 装饰器提供默认值，模式统一为：

```python
@default("xxx_url")
def _default_xxx_url(self) -> str:
    return ujoin(self.app_url, "api/xxx/")
```

## 核心函数

### get_federated_extensions(labextensions_path)

```python
def get_federated_extensions(labextensions_path: list[str]) -> dict[str, Any]:
```

发现所有联邦（预构建）扩展：

1. 遍历每个 `labextensions_path` 目录
2. 使用 glob 匹配两种目录结构：
   - 一级包：`{ext_dir}/[!@]*/package.json`（如 `@jupyterlab/apputils-extension` 外的包）
   - 二级包：`{ext_dir}/@*/*/package.json`（如 `@jupyterlab/apputils-extension`）
3. 读取 package.json，提取 name/version/description/homepage/repository/dependencies/jupyterlab 字段
4. 如果存在 `install.json`，一并读取
5. 返回 `{extension_name: ext_metadata}` 字典

扩展元数据字段：
- `name`: 包名
- `version`: 版本
- `description`: 描述
- `url`: 主页URL（优先homepage，其次repository.url）
- `ext_dir`: 扩展所在的根目录
- `ext_path`: 扩展的完整路径
- `is_local`: 是否本地扩展（默认False）
- `dependencies`: npm依赖
- `jupyterlab`: JupyterLab配置（含`_build`字段）
- `install`: install.json内容（可选）
- `repository`: 仓库URL（可选）

### get_page_config(labextensions_path, app_settings_dir, logger)

```python
def get_page_config(
    labextensions_path: list[str],
    app_settings_dir: str | None = None,
    logger: Logger | None = None
) -> dict[str, Any]:
```

构建传递给前端的页面配置字典，合并多层配置源：

1. **app_settings_dir层**（最低优先级）：读取 `page_config.json5` 或 `page_config.json`
   - 将 `disabledExtensions` 和 `deferredExtensions` 列表转为字典（`{name: True}`）
2. **静态配置层**：调用 `get_static_page_config()` 从 ConfigManager 读取
3. **联邦扩展层**：
   - 扫描所有联邦扩展，提取 `_build` 信息构建扩展列表
   - 处理扩展间的禁用关系（`disabledExtensions` 元数据）
4. **应用内建扩展层**：读取 `{app_dir}/static/package.json` 中的 `extensionMetadata`
5. **格式转换**：将字典转回列表（前端消费格式），仅保留值为True的键

### get_static_page_config(app_settings_dir, logger, level, include_higher_levels)

```python
def get_static_page_config(
    app_settings_dir: str | None = None,
    logger: Logger | None = None,
    level: str = "all",
    include_higher_levels: bool = False,
) -> dict[str, Any]:
```

通过 ConfigManager 读取 labconfig 配置目录下的 `page_config`。

### write_page_config(page_config, level)

```python
def write_page_config(page_config: dict[str, Any], level: str = "all") -> None:
```

将 page_config 写入指定级别的配置目录。

### load_config(path)

```python
def load_config(path: str) -> Any:
```

加载 JSON 或 JSON5 配置文件（根据扩展名自动判断）。

### get_package_url(data)

```python
def get_package_url(data: dict[str, Any]) -> str:
```

从 package.json 数据提取URL：优先 `homepage`，其次 `repository.url`，否则返回空字符串。

### get_allowed_levels()

```python
def get_allowed_levels() -> list[str]:
```

返回合法的配置级别列表：`["all", "user", "sys_prefix", "system", "app", "extension"]`。

### _get_config_manager(level, include_higher_levels)

```python
def _get_config_manager(level: str, include_higher_levels: bool = False) -> ConfigManager:
```

创建 ConfigManager 实例，映射级别到具体路径：

| 级别 | 读路径 | 写路径 |
|------|--------|--------|
| `all` | 所有级别 | 用户目录 |
| `user` | `jupyter_config_dir()/labconfig` | 同左 |
| `sys_prefix` | `ENV_CONFIG_PATH[0]/labconfig` | 同左 |
| `system` | `SYSTEM_CONFIG_PATH/labconfig` | 同左 |
| `app` | 空列表 | None |
| `extension` | 空列表 | None |

`include_higher_levels=True` 时，读取指定级别及以上的所有配置。

### recursive_update

```python
from jupyter_server.services.config.manager import ConfigManager, recursive_update
```

从 jupyter_server 导入的递归字典更新函数，用于深度合并配置。

[F-201]
