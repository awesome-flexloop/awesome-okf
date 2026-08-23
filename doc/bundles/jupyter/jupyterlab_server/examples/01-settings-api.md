---
okf_version: "0.2"
type: example
title: "设置系统API示例"
description: "通过REST API和Python API操作设置：查询设置、保存设置、使用overrides覆盖配置、验证Schema约束。"
tags: [settings, api, rest, schema, overrides, json-schema]
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

# 设置系统API示例

## REST API 示例

假设服务器运行在 http://localhost:8888，以下示例展示如何通过HTTP API操作设置。

### 查询所有设置

```bash
curl -s http://localhost:8888/lab/api/settings/ | python -m json.tool
```

响应示例（简化）：
```json
{
  "settings": [
    {
      "id": "@jupyterlab/apputils-extension:themes",
      "schema": {
        "title": "Theme",
        "description": "Theme settings.",
        "type": "object",
        "properties": {
          "theme": {
            "type": "string",
            "title": "Selected Theme",
            "default": "JupyterLab Light"
          },
          "theme-scrollbars": {
            "type": "boolean",
            "title": "Theme Scrollbars",
            "default": false
          }
        }
      },
      "version": "3.0.0",
      "raw": "{\"theme\": \"JupyterLab Dark\"}",
      "settings": {
        "theme": "JupyterLab Dark",
        "theme-scrollbars": false
      },
      "last_modified": "2024-01-15T10:30:00.000000Z",
      "created": "2024-01-10T08:00:00.000000Z"
    }
  ]
}
```

### 查询单个设置

```bash
curl -s http://localhost:8888/lab/api/settings/@jupyterlab/apputils-extension:themes | python -m json.tool
```

### 保存设置

```bash
# 切换到暗色主题
curl -X PUT http://localhost:8888/lab/api/settings/@jupyterlab/apputils-extension:themes \
  -H "Content-Type: application/json" \
  -d '{
    "raw": "{\"theme\": \"JupyterLab Dark\", \"theme-scrollbars\": true}"
  }'
```

### 重置设置（删除用户覆盖）

```bash
curl -X DELETE http://localhost:8888/lab/api/settings/@jupyterlab/apputils-extension:themes
```

### 多语言查询（返回翻译后的schema）

```bash
# 获取中文翻译的设置schema
curl -s "http://localhost:8888/lab/api/settings/@jupyterlab/apputils-extension:themes?locale=zh_CN"
```

## Python API 示例

### 使用 get_settings/save_settings 函数

```python
import tempfile
import os
import json
from jupyterlab_server.settings_utils import get_settings, save_settings

# 准备目录结构
with tempfile.TemporaryDirectory() as tmp:
    schemas_dir = os.path.join(tmp, "schemas")
    settings_dir = os.path.join(tmp, "user-settings")
    os.makedirs(os.path.join(schemas_dir, "@myorg", "myplugin"))
    os.makedirs(settings_dir)

    # 写入一个JSON Schema
    schema = {
        "title": "My Plugin Settings",
        "description": "Settings for my plugin",
        "type": "object",
        "properties": {
            "refreshInterval": {
                "type": "integer",
                "title": "Refresh Interval",
                "default": 30,
                "minimum": 5,
                "maximum": 300
            },
            "showNotifications": {
                "type": "boolean",
                "title": "Show Notifications",
                "default": True
            }
        }
    }
    schema_path = os.path.join(schemas_dir, "@myorg", "myplugin", "plugin.json")
    with open(schema_path, "w") as f:
        json.dump(schema, f)

    # 查询设置（返回schema + 用户设置 + 合并后的设置）
    warnings = []
    result = get_settings(
        schemas_dir=schemas_dir,
        settings_dir=settings_dir,
        schema_name="@myorg/myplugin:plugin",
        overrides={},
        warnings=warnings,
        translator=None,
        labextensions_path=[],
    )
    schema_out, raw, settings_data, version, warns = result

    print("默认设置:", settings_data)
    # 输出: {'refreshInterval': 30, 'showNotifications': True}

    # 保存用户设置
    save_settings(
        schemas_dir=schemas_dir,
        settings_dir=settings_dir,
        schema_name="@myorg/myplugin:plugin",
        overrides={},
        warnings=warnings,
        translator=None,
        labextensions_path=[],
        raw='{"refreshInterval": 60}',
    )

    # 再次查询，看到用户设置已生效
    result = get_settings(
        schemas_dir=schemas_dir,
        settings_dir=settings_dir,
        schema_name="@myorg/myplugin:plugin",
        overrides={},
        warnings=warnings,
        translator=None,
        labextensions_path=[],
    )
    _, _, settings_data, _, _ = result
    print("用户设置后:", settings_data)
    # 输出: {'refreshInterval': 60, 'showNotifications': True}
```

### 使用 overrides 强制配置

```python
# 系统级overrides（管理员设置，对所有用户生效）
overrides = {
    "@myorg/myplugin:plugin": {
        "refreshInterval": 120  # 管理员强制设置刷新间隔
    }
}

# 用户尝试设置refreshInterval=60，但overrides会覆盖
# 最终值为120（overrides优先级高于用户设置）
result = get_settings(
    schemas_dir=schemas_dir,
    settings_dir=settings_dir,
    schema_name="@myorg/myplugin:plugin",
    overrides=overrides,  # 传入overrides
    warnings=warnings,
    translator=None,
    labextensions_path=[],
)
```

## 用户设置文件位置

用户设置文件默认位于：

| 平台 | 路径 |
|------|------|
| Linux | `~/.jupyter/lab/user-settings/{plugin_name}.jupyterlab-settings` |
| macOS | `~/Library/Jupyter/lab/user-settings/...` |
| Windows | `%APPDATA%\jupyter\lab\user-settings\...` |

文件使用json5格式（支持注释和尾随逗号）：

```json5
// @myorg/myplugin:plugin settings
{
  // 刷新间隔（秒）
  "refreshInterval": 60,
  "showNotifications": true,  // 显示通知
}
```
