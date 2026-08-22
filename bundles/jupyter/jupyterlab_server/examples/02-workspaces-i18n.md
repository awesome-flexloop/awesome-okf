---
okf_version: "0.2"
type: example
title: "工作区与国际化示例"
description: "工作区CRUD操作、slugify文件名转换、工作区CLI使用、TranslationBundle翻译、语言包查询、Schema翻译等实战示例。"
tags: [workspaces, i18n, translation, cli, slugify, language-pack]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T12:30:00Z" }
verified: { by: "process:source-code-to-okf-wiki-v", at: "2026-08-22T12:30:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: workspaces-handler-py
    resource: "../../../../../external/libs/jupyter/jupyterlab_server/jupyterlab_server/workspaces_handler.py"
    title: "jupyterlab_server/workspaces_handler.py"
  - id: translation-utils-py
    resource: "../../../../../external/libs/jupyter/jupyterlab_server/jupyterlab_server/translation_utils.py"
    title: "jupyterlab_server/translation_utils.py"
---

# 工作区与国际化示例

## 工作区管理示例

### REST API 操作工作区

```bash
# 列出所有工作区
curl -s http://localhost:8888/lab/api/workspaces/ | python -m json.tool

# 获取默认工作区
curl -s http://localhost:8888/lab/api/workspaces/default | python -m json.tool

# 保存工作区
curl -X PUT http://localhost:8888/lab/api/workspaces/my-project \
  -H "Content-Type: application/json" \
  -d '{
    "data": {
      "layout-restorer": {
        "main": {"dock": {"type": "split-area", "children": []}},
        "left": {"collapsed": false, "widgets": ["filebrowser"]}
      }
    },
    "metadata": {
      "id": "/lab/workspaces/my-project"
    }
  }'

# 删除工作区
curl -X DELETE http://localhost:8888/lab/api/workspaces/my-project
```

### Python API 使用 WorkspacesManager

```python
import tempfile
import os
import json
from jupyterlab_server.workspaces_handler import WorkspacesManager, slugify, WORKSPACE_EXTENSION

with tempfile.TemporaryDirectory() as tmp:
    # 创建manager
    manager = WorkspacesManager(workspaces_dir=tmp)

    # slugify 测试
    print(slugify("My Project"))           # "my-project"
    print(slugify("数据科学"))              # "shu-ju-ke-xue" (unidecode)
    print(slugify("a" * 50))               # 长名称截断+hash
    print(slugify("default"))              # "default"
    print(slugify("workspace", base="/path/to"))  # "/path/to/workspace"

    # 工作区文件名
    path = manager.workspace_path("my-project")
    print(path)  # /tmp/.../my-project.jupyterlab-workspace

    # 保存工作区
    data = {
        "data": {"layout-restorer": {}},
        "metadata": {"id": "/lab/workspaces/my-project"}
    }
    manager.save("my-project", data)

    # 获取工作区
    ws = manager.get("my-project")
    print(ws["metadata"]["id"])  # "/lab/workspaces/my-project"
    print("last_modified" in ws["metadata"])  # True
    print("created" in ws["metadata"])        # True

    # 列出工作区
    workspaces, error = manager.list_workspaces()
    print(f"工作区数量: {len(workspaces)}")  # 2 (default + my-project)

    # 删除工作区
    manager.delete("my-project")

    # 验证已删除
    try:
        manager.get("my-project")
    except Exception as e:
        print(f"获取已删除工作区: {e}")  # HTTPError 404
```

### 工作区CLI使用

```bash
# 列出所有工作区
python -m jupyterlab_server.workspaces list
# 输出: {"workspaces": [...], "ids": ["/", "/workspace1"]}

# 导出默认工作区到stdout
python -m jupyterlab_server.workspaces export

# 导出指定工作区到文件
python -m jupyterlab_server.workspaces export my-project --output-dir ./backups
# 生成文件: ./backups/my-project.jupyterlab-workspace

# 从文件导入工作区
python -m jupyterlab_server.workspaces import ./backups/my-project.jupyterlab-workspace

# 导入并重命名
python -m jupyterlab_server.workspaces import workspace.json --name new-name

# 指定工作区目录
python -m jupyterlab_server.workspaces list --workspaces-dir /custom/workspaces
```

## 国际化示例

### 查询语言包

```bash
# 列出所有可用语言包
curl -s http://localhost:8888/lab/api/translations/ | python -m json.tool
```

响应示例：
```json
{
  "data": {
    "en": {
      "displayName": "English",
      "nativeName": "English"
    },
    "zh_CN": {
      "displayName": "Chinese (Simplified)",
      "nativeName": "中文（简体）"
    },
    "ja": {
      "displayName": "Japanese",
      "nativeName": "日本語"
    }
  },
  "message": ""
}
```

### 切换语言

```bash
# 获取中文翻译数据
curl -s http://localhost:8888/lab/api/translations/zh_CN | python -m json.tool | head -20
```

### Python API 使用 TranslationBundle

```python
from jupyterlab_server.translation_utils import TranslationBundle, translator

# 切换全局语言
translator.set_locale("en")  # 默认英语，返回原文

# 加载默认domain的翻译bundle
bundle = translator.load("jupyterlab")

# 基本翻译（英语返回原文）
print(bundle.gettext("Run"))          # "Run"
print(bundle.__("Run"))               # 简写

# 复数翻译
print(bundle.ngettext("cell", "cells", 1))   # "cell"
print(bundle.ngettext("cell", "cells", 5))   # "cells"
print(bundle._n("cell", "cells", 5))         # 简写

# 带上下文的翻译
print(bundle.pgettext("verb", "Open"))       # "Open" (动词)
print(bundle.pgettext("adjective", "Open"))  # "Open" (形容词)
print(bundle._p("verb", "Open"))             # 简写
```

### 验证locale有效性

```python
from jupyterlab_server.translation_utils import is_valid_locale, get_display_name

print(is_valid_locale("en"))        # True
print(is_valid_locale("zh_CN"))     # True
print(is_valid_locale("invalid"))   # False
print(is_valid_locale("no_NO"))     # True (特殊处理)

# 获取语言的本地化显示名
print(get_display_name("zh_CN", "en"))   # "Chinese (Simplified China)"
print(get_display_name("zh_CN", "zh_CN")) # "中文（简体中文）"
```

### 翻译JSON Schema

```python
import json
from jupyterlab_server.translation_utils import translator

# 一个示例schema（包含用户可见字符串）
schema = {
    "title": "Notebook Settings",
    "description": "Settings for the notebook extension.",
    "type": "object",
    "properties": {
        "lineNumbers": {
            "type": "boolean",
            "title": "Line Numbers",
            "description": "Whether to show line numbers in code cells.",
            "default": False
        }
    }
}

# 切换到中文
translator.set_locale("zh_CN")

# 翻译schema（自动翻译title/description等用户可见字段）
translated = translator.translate_schema(schema)
print(translated["title"])  # "笔记本设置"（如果语言包已安装）
print(translated["properties"]["lineNumbers"]["title"])  # "行号"

# 切回英语
translator.set_locale("en")
translated_en = translator.translate_schema(schema)
print(translated_en["title"])  # "Notebook Settings"（原文）
```

### 创建自定义翻译Bundle

```python
from jupyterlab_server.translation_utils import TranslationBundle

# 为自定义domain创建翻译bundle
bundle = TranslationBundle(domain="my-extension", locale_="en")

# 后续如果安装了对应语言包，update_locale会加载翻译
bundle.update_locale("zh_CN")
```
