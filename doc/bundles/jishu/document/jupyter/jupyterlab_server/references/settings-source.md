---
okf_version: "0.2"
type: reference
title: "设置系统源码（settings_handler.py + settings_utils.py）"
description: "jupyterlab_server 设置系统的完整 API：SettingsHandler REST端点、SchemaHandler基类、JSON Schema验证、三层配置覆盖与设置持久化"
tags: [settings, json-schema, schema-handler, settings-handler, overrides, validation, json5, draft7]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T12:30:00Z" }
verified: { by: "process:source-code-to-okf-wiki-v", at: "2026-08-22T12:30:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: settings-handler-py
    resource: "../../../../../external/libs/jupyter/jupyterlab_server/jupyterlab_server/settings_handler.py"
    title: "jupyterlab_server/settings_handler.py"
  - id: settings-utils-py
    resource: "../../../../../external/libs/jupyter/jupyterlab_server/jupyterlab_server/settings_utils.py"
    title: "jupyterlab_server/settings_utils.py"
---

# 设置系统源码

本信源登记设置系统两个核心文件的API：
- `settings_handler.py`（约110行）：Tornado REST处理器
- `settings_utils.py`（约509行）：设置读写核心逻辑、SchemaHandler基类

## 常量

```python
SETTINGS_EXTENSION = ".jupyterlab-settings"
```

用户设置文件的扩展名。

## SettingsHandler 类

```python
class SettingsHandler(ExtensionHandlerMixin, ExtensionHandlerJinjaMixin, SchemaHandler):
```

设置REST API处理器。

### initialize()

```python
def initialize(
    self,
    name: str,
    app_settings_dir: str,
    schemas_dir: str,
    settings_dir: str,
    labextensions_path: list[str],
    overrides: dict[str, Any] | None = None,
    **kwargs: Any,
) -> None:
```

初始化handler，调用 `SchemaHandler.initialize()` 和 `ExtensionHandlerMixin.initialize()`。

### GET /lab/api/settings/ 或 /lab/api/settings/{schema_name}

```python
@web.authenticated
def get(self, schema_name: str = "") -> Any:
```

获取设置：

1. 获取当前locale，设置translator
2. 解析 `ids_only` 查询参数（`?ids_only=true` 仅返回schema ID列表）
3. 调用 `get_settings()` 获取结果
4. 记录所有warnings到日志
5. 返回JSON响应

当 `schema_name` 为空时返回所有设置列表（`{"settings": [...]}`），否则返回单个schema的设置。

### PUT /lab/api/settings/{schema_name}

```python
@web.authenticated
def put(self, schema_name: str) -> None:
```

更新设置：

1. 验证 settings_dir 存在（否则500）
2. 解析请求body为JSON，提取 `raw` 字段
3. 调用 `save_settings()` 保存
4. 错误处理：
   - JSONDecodeError → 400
   - KeyError/TypeError（缺少raw字段）→ 400
   - ValidationError（schema验证失败）→ 400
5. 成功返回 204 No Content

请求body格式：`{"raw": "{\"key\": \"value\", ...}"}` （raw是JSON字符串，支持json5注释）

## SchemaHandler 类

```python
class SchemaHandler(APIHandler):
```

需要访问设置的handler基类，被 SettingsHandler 和 TranslationsHandler 继承。

### initialize()

```python
def initialize(
    self,
    app_settings_dir: str,
    schemas_dir: str,
    settings_dir: str,
    labextensions_path: list[str] | None,
    overrides: dict[str, Any] | None = None,
    **kwargs: Any,
) -> None:
```

初始化：
- 若未提供overrides，从app_settings_dir加载
- 存储所有目录路径到实例属性
- overrides加载失败时记录warning但不中断

### get_current_locale()

```python
def get_current_locale(self) -> str:
```

获取当前locale：
1. 查询translation-extension设置中的locale值
2. "default"映射到SYS_LOCALE
3. 无效locale回退到DEFAULT_LOCALE（"en"）
4. 支持PSEUDO_LANGUAGE（"ach_UG"）伪翻译语言
5. 设置schema缺失时记录warning，返回SYS_LOCALE

## 核心函数（settings_utils.py）

### get_settings()

```python
def get_settings(
    app_settings_dir: str,
    schemas_dir: str,
    settings_dir: str,
    schema_name: str = "",
    overrides: dict[str, Any] | None = None,
    labextensions_path: list[str] | None = None,
    translator: Any = None,
    ids_only: bool = False,
) -> tuple[dict[str, Any], list[Any]]:
```

公共API，获取设置数据。

- 无schema_name：返回 `({"settings": [settings_list]}, warnings)`
- 有schema_name：返回 `({"id": ..., "schema": ..., "version": ..., "raw": ..., "settings": ..., "last_modified": ..., "created": ...}, warnings)`
- 若未提供overrides，自动从app_settings_dir加载
- 支持translator回调翻译schema中的可翻译字符串
- ids_only模式仅返回schema ID列表

### save_settings()

```python
def save_settings(
    schemas_dir: str,
    settings_dir: str,
    schema_name: str,
    raw_settings: str,
    overrides: dict[str, Any],
    labextensions_path: list[str] | None = None,
) -> None:
```

保存用户设置：

1. 用json5解析raw_settings字符串
2. 获取对应schema并验证payload（Draft7Validator）
3. 将原始字符串（保留注释）写入 `.jupyterlab-settings` 文件
4. 验证失败抛出 ValidationError

### 内部函数

#### _get_schema()

```python
def _get_schema(
    schemas_dir: str,
    schema_name: str,
    overrides: dict[str, Any],
    labextensions_path: list[str] | None,
) -> tuple[dict[str, Any], str]:
```

查找、解析和验证单个JSON Schema：
1. 先在labextensions_path中查找联邦扩展的schema（路径：`{ext_path}/{ext_name}/schemas/{ext_name}/{plugin_name}.json`）
2. 回退到默认schemas_dir
3. 加载并JSON解析
4. 应用 `_override()` 覆盖默认值
5. 使用 `Draft7Validator.check_schema()` 验证schema本身有效性
6. 调用 `_get_version()` 获取版本号
7. 返回 `(schema_dict, version_string)`

#### _get_user_settings()

```python
def _get_user_settings(
    settings_dir: str,
    schema_name: str,
    schema: Any,
) -> dict[str, Any]:
```

读取用户设置文件：
1. 路径为 `{settings_dir}/{package_dir}/{plugin}.jupyterlab-settings`
2. 使用json5解析（支持注释、尾随逗号等）
3. 使用Draft7Validator验证用户设置
4. 验证失败时返回空设置和warning
5. 返回 `{raw, settings, warning, last_modified, created}`，其中时间为UTC ISO格式

#### _list_settings()

```python
def _list_settings(
    schemas_dir: str,
    settings_dir: str,
    overrides: dict[str, Any],
    extension: str = ".json",
    labextensions_path: list[str] | None = None,
    translator: Any = None,
    ids_only: bool = False,
) -> tuple[list[Any], list[Any]]:
```

列出所有设置：
1. 递归glob schemas_dir下所有.json文件
2. 递归glob labextensions_path下所有 `**/schemas/**/*.json` 文件
3. 从相对路径生成schema_name（`@scope/package:plugin` 格式）
4. 联邦扩展schema去重（先发现的优先）
5. ids_only模式仅返回 `{id: ...}`
6. 完整模式返回每个schema的完整数据（含schema/version/raw/settings/last_modified/created）
7. 返回按ID倒序排列

#### _override()

```python
def _override(
    schema_name: str,
    schema: dict[str, Any],
    overrides: dict[str, Any],
) -> dict[str, Any]:
```

应用overrides到schema默认值：
- 对于dict类型默认值，使用recursive_update深度合并
- 对于标量默认值，直接替换
- overrides中存在但schema properties中不存在的key，添加到properties

#### _path()

```python
def _path(
    root_dir: str,
    schema_name: str,
    make_dirs: bool = False,
    extension: str = ".json",
) -> str:
```

将schema_name（`@scope/package:plugin`格式）转换为文件系统路径。schema_name按`:`分割为包目录和插件名。make_dirs=True时自动创建父目录。

#### _get_overrides()

```python
def _get_overrides(app_settings_dir: str) -> tuple[dict[str, Any], str]:
```

加载overrides配置，按优先级顺序：
1. `{app_settings_dir}/overrides.d/*.json`（按文件名排序）
2. `{app_settings_dir}/overrides.d/*.json5`（按文件名排序）
3. `{app_settings_dir}/overrides.json`
4. `{app_settings_dir}/overrides.json5`
5. ConfigManager中 `labconfig/default_setting_overrides`（通过ConfigManager读取）

使用json5解析.json5文件，json解析.json文件，recursive_update合并所有来源。

#### _get_version()

```python
def _get_version(schemas_dir: str, schema_name: str) -> str:
```

从schema所在目录的 `package.json.orig` 文件读取版本号，不存在则返回"N/A"。

[F-203]
