---
type: Example
title: 编写自定义 Skill
description: 遵循 Anthropic Agent Skills 规范编写一个完整的自定义 Skill，包括 SKILL.md 的 YAML frontmatter 规范、body 指令编写、渐进式加载设计、脚本和参考资源组织，以及使用 package_skill.py 打包为 .skill 文件。
tags: [anthropics-skills, example, skill, skill-md, custom-skill, packaging]
generated: { by: "agent:okf-wiki-generator", at: "2026-08-22T22:45:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: facts
    resource: /.spec/facts.md
    title: anthropics-skills 源码事实清单
---

## 场景说明

你需要创建一个自定义的 Agent Skill。本示例将创建一个 "API 文档生成器" Skill（`api-doc-generator`），演示完整的 Skill 开发流程：
1. 规划 Skill 结构和资源
2. 编写合规的 SKILL.md（YAML frontmatter + 指令 body）
3. 添加辅助脚本和参考资源
4. 运行验证脚本检查格式
5. 打包为 `.skill` 文件分发

## Skill 规范核心原则

Skill 采用**三级渐进式加载**（Progressive Disclosure）架构：

| 层级 | 内容 | 加载时机 | 大小 |
|------|------|---------|------|
| L1 Metadata | name + description | 始终在上下文中 | ~100 词 |
| L2 SKILL.md body | 主体指令 | Skill 触发时加载 | <500 行 |
| L3 Bundled Resources | scripts/references/assets/examples | 按需加载 | 无限制 |

## 完整步骤

### 步骤 1：创建 Skill 目录结构

每个 Skill 是一个自包含文件夹：

```bash
# 创建 Skill 目录
mkdir -p skills/api-doc-generator/{scripts,references,examples,assets}

# 标准结构：
# api-doc-generator/
# ├── SKILL.md              # 必需：Skill 定义文件
# ├── scripts/              # 可选：确定性/重复性任务的可执行脚本
# │   ├── generate_openapi.py
# │   └── validate_schema.py
# ├── references/           # 可选：按需加载的参考文档
# │   ├── openapi-patterns.md
# │   └── http-status-codes.md
# ├── examples/             # 可选：使用示例
# │   └── sample-output.md
# ├── assets/               # 可选：模板、图标等输出用文件
# │   └── template.yaml
# └── LICENSE.txt           # 可选：许可证
```

### 步骤 2：编写 SKILL.md（最小模板）

最小可用的 SKILL.md 仅需 6 行：

```markdown
---
name: api-doc-generator
description: Replace with description of the skill and when Claude should use it.
---

# Insert instructions below
```

但生产级 Skill 需要更完整的 frontmatter 和 body。

### 步骤 3：编写完整 SKILL.md

创建 `skills/api-doc-generator/SKILL.md`：

```markdown
---
name: api-doc-generator
description: >
  Generate OpenAPI 3.1 documentation for REST APIs from code or natural language descriptions.
  Use this skill when asked to create API documentation, generate OpenAPI/Swagger specs,
  document HTTP endpoints, create API reference docs, or design REST API schemas.
  Triggers on: "document this API", "generate OpenAPI", "create swagger", "API docs".
license: Complete terms in LICENSE.txt
---

# API Doc Generator

Generate production-ready OpenAPI 3.1 specifications for REST APIs.

## When to Use This Skill

Activate this skill when the user:
- Asks to document an existing API
- Requests an OpenAPI/Swagger specification
- Wants to design a new REST API
- Needs API reference documentation
- Mentions "endpoint docs", "API schema", or "REST specification"

Do NOT activate this skill for:
- GraphQL APIs (use a different approach)
- gRPC/Protobuf documentation
- Simple one-off endpoint questions

## Core Workflow

Follow this process when generating API documentation:

### Step 1: Gather Requirements

Before writing any spec, determine:

1. **API purpose** — What does this API do? Who are its consumers?
2. **Authentication** — What auth method? (API key, OAuth2, Bearer token, none)
3. **Base URL** — Production and staging URLs
4. **Content type** — JSON (default), form-data, or multipart
5. **Existing code** — If code exists, extract endpoint patterns from it

Ask clarifying questions if any of these are unclear. For internal APIs,
default to JSON content type and Bearer token auth unless told otherwise.

### Step 2: Generate the OpenAPI Document

Use the script to bootstrap the spec, then refine:

```bash
python scripts/generate_openapi.py \
  --title "API Title" \
  --version "1.0.0" \
  --auth bearer \
  --base-url "https://api.example.com/v1" \
  --output openapi.yaml
```

If the script is not available or the task is simple enough, write the YAML directly.
Always use OpenAPI 3.1 format (not Swagger 2.0).

### Step 3: Define Paths and Operations

For each endpoint, document:

- **Path and method** (GET/POST/PUT/PATCH/DELETE)
- **Summary** — One-line description (imperative mood: "List users", not "Returns a list")
- **Operation ID** — camelCase, unique: `listUsers`, `getUserById`, `createUser`
- **Parameters** — Path, query, header params with types and descriptions
- **Request body** — Schema reference and example
- **Responses** — At minimum: 200 (success), 400 (validation), 401 (auth), 404 (not found)
- **Tags** — Group related endpoints (e.g., "Users", "Orders")

### Step 4: Define Reusable Schemas

Extract common objects into `components/schemas`:

- Use `$ref` to reference schemas from paths
- Define error response schema once and reference it
- Use `allOf` for inheritance/polymorphism
- Include `example` values for every property

Load `references/openapi-patterns.md` for schema design patterns:
- Pagination (cursor-based and offset-based)
- Error response envelopes
- Soft delete patterns
- Rate limit headers

### Step 5: Validate the Output

Always validate the generated spec before delivering:

```bash
python scripts/validate_schema.py openapi.yaml
```

If the script reports errors, fix them and re-validate. The script checks:
- Valid YAML/JSON syntax
- Required OpenAPI 3.1 fields
- Reference integrity (no broken $ref)
- Schema type consistency

### Step 6: Deliver

Provide the user with:
1. The complete OpenAPI YAML file (in a code block or written to disk)
2. A brief summary of the endpoints documented
3. Any assumptions made (e.g., "assumed Bearer auth since not specified")
4. Instructions for next steps (e.g., "You can paste this into https://editor.swagger.io to preview")

## Quality Standards

- Every endpoint must have at least one example response
- Error responses use the shared Error schema
- Date fields use `format: date-time` (RFC 3339)
- Paginated lists use the Pagination envelope pattern (see references)
- Boolean flags don't use `is_` prefix in schema properties (use `active` not `isActive`)
- IDs use `format: uuid` or `type: integer` consistently within an API

## Common Patterns

For reference documentation on common OpenAPI patterns:
- Pagination: Read `references/openapi-patterns.md` section "Pagination"
- File uploads: Use `multipart/form-data` with `format: binary`
- Webhooks: Define in `components/webhooks` (OpenAPI 3.1)
- Versioning: Use URL path versioning (`/v1/`, `/v2/`) unless told otherwise

## Writing Style for Descriptions

- Use imperative mood for operation summaries
- Parameter descriptions start with a capital letter and end without a period
- Describe what the parameter does, not what it is
- Good: "Filter results by creation date (ISO 8601)"
- Bad: "This is the date filter parameter"

## Scripts

Scripts in the `scripts/` directory are black-box tools. Run them with `--help`
first to understand their options:

```bash
python scripts/generate_openapi.py --help
python scripts/validate_schema.py --help
```

Script paths below are relative to this skill's directory.
```

### 步骤 4：YAML Frontmatter 字段详解

`quick_validate.py` 只允许 6 个 frontmatter 属性：

```python
ALLOWED_PROPERTIES = {'name', 'description', 'license', 'allowed-tools', 'metadata', 'compatibility'}
```

| 字段 | 必需 | 约束 | 说明 |
|------|------|------|------|
| `name` | ✅ | kebab-case (`^[a-z0-9-]+$`)，不以连字符开头/结尾，无连续连字符，≤64 字符 | Skill 唯一标识符 |
| `description` | ✅ | ≤1024 字符，禁止包含 `<` `>`，支持 YAML 多行语法（`>`, `\|`, `>-`, `\|-`） | **触发 Skill 的主要机制**，必须同时包含"做什么"和"何时使用" |
| `license` | ❌ | 字符串 | 许可证声明 |
| `allowed-tools` | ❌ | 列表 | 允许的工具列表 |
| `metadata` | ❌ | 对象 | 元数据（如 hermes 标签、分类） |
| `compatibility` | ❌ | ≤500 字符 | 兼容性要求 |

**description 是最关键的字段**：

```yaml
# ❌ 太简单，无法可靠触发
description: "Generate API documentation"

# ✅ 包含功能+触发场景+触发词
description: >
  Generate OpenAPI 3.1 documentation for REST APIs from code or natural language descriptions.
  Use this skill when asked to create API documentation, generate OpenAPI/Swagger specs,
  document HTTP endpoints, create API reference docs, or design REST API schemas.
  Triggers on: "document this API", "generate OpenAPI", "create swagger", "API docs".
```

建议写得主动/明确（"pushy"），解决触发不足（undertrigger）问题。简单单步查询可能不会触发 Skill，复杂多步任务才能可靠触发。

### 步骤 5：编写辅助脚本（scripts/）

创建 `skills/api-doc-generator/scripts/generate_openapi.py`：

```python
#!/usr/bin/env python3
"""Bootstrap an OpenAPI 3.1 YAML specification."""

import argparse
import sys
import yaml
from pathlib import Path


def generate_spec(title: str, version: str, auth: str, base_url: str) -> dict:
    """Generate a minimal OpenAPI 3.1 spec skeleton."""
    spec = {
        "openapi": "3.1.0",
        "info": {
            "title": title,
            "version": version,
            "description": f"{title} API Documentation"
        },
        "servers": [{"url": base_url}],
        "paths": {},
        "components": {
            "schemas": {
                "Error": {
                    "type": "object",
                    "required": ["error", "message"],
                    "properties": {
                        "error": {"type": "string", "description": "Error code"},
                        "message": {"type": "string", "description": "Human-readable error message"},
                        "details": {"type": "object", "description": "Additional error context"}
                    }
                }
            },
            "responses": {
                "BadRequest": {
                    "description": "Invalid request parameters",
                    "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}}
                },
                "Unauthorized": {
                    "description": "Authentication required or failed",
                    "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}}
                },
                "NotFound": {
                    "description": "Resource not found",
                    "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}}
                }
            }
        }
    }

    # Add security schemes based on auth type
    if auth == "bearer":
        spec["components"]["securitySchemes"] = {
            "BearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT"
            }
        }
        spec["security"] = [{"BearerAuth": []}]
    elif auth == "apikey":
        spec["components"]["securitySchemes"] = {
            "ApiKeyAuth": {
                "type": "apiKey",
                "in": "header",
                "name": "X-API-Key"
            }
        }
        spec["security"] = [{"ApiKeyAuth": []}]

    return spec


def main():
    parser = argparse.ArgumentParser(description="Generate OpenAPI 3.1 spec skeleton")
    parser.add_argument("--title", required=True, help="API title")
    parser.add_argument("--version", default="1.0.0", help="API version")
    parser.add_argument("--auth", choices=["bearer", "apikey", "none"], default="bearer", help="Auth type")
    parser.add_argument("--base-url", required=True, help="API base URL")
    parser.add_argument("--output", default="openapi.yaml", help="Output file path")
    args = parser.parse_args()

    spec = generate_spec(args.title, args.version, args.auth, args.base_url)
    output_path = Path(args.output)
    output_path.write_text(yaml.dump(spec, sort_keys=False, allow_unicode=True, default_flow_style=False))
    print(f"Generated OpenAPI spec: {output_path}")


if __name__ == "__main__":
    main()
```

创建 `skills/api-doc-generator/scripts/validate_schema.py`：

```python
#!/usr/bin/env python3
"""Validate an OpenAPI 3.1 YAML/JSON specification."""

import argparse
import sys
import yaml
import json
from pathlib import Path
from urllib.parse import urlparse


def collect_refs(obj, refs=None, path="$"):
    """Recursively collect all $ref values from a dict/list."""
    if refs is None:
        refs = []
    if isinstance(obj, dict):
        for key, value in obj.items():
            if key == "$ref" and isinstance(value, str):
                refs.append((value, f"{path}.{key}"))
            else:
                collect_refs(value, refs, f"{path}.{key}")
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            collect_refs(item, refs, f"{path}[{i}]")
    return refs


def resolve_ref(ref: str, spec: dict) -> bool:
    """Check if a local $ref can be resolved."""
    if not ref.startswith("#/"):
        return True  # External refs not validated
    parts = ref[2:].split("/")
    current = spec
    for part in parts:
        part = part.replace("~1", "/").replace("~0", "~")
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            return False
    return True


def validate(filepath: Path) -> list[str]:
    """Validate an OpenAPI spec file, returning list of errors."""
    errors = []
    try:
        content = filepath.read_text()
        if filepath.suffix in ('.yaml', '.yml'):
            spec = yaml.safe_load(content)
        else:
            spec = json.loads(content)
    except (yaml.YAMLError, json.JSONDecodeError) as e:
        return [f"Parse error: {e}"]

    # Check required fields
    if not spec.get("openapi"):
        errors.append("Missing required field: openapi")
    elif not str(spec["openapi"]).startswith("3.1"):
        errors.append(f"Expected OpenAPI 3.1.x, got: {spec['openapi']}")
    if not spec.get("info"):
        errors.append("Missing required field: info")
    elif not spec["info"].get("title"):
        errors.append("Missing required field: info.title")
    if "paths" not in spec:
        errors.append("Missing required field: paths")

    # Validate $ref integrity
    for ref, location in collect_refs(spec):
        if not resolve_ref(ref, spec):
            errors.append(f"Broken $ref: {ref} at {location}")

    return errors


def main():
    parser = argparse.ArgumentParser(description="Validate OpenAPI 3.1 spec")
    parser.add_argument("file", help="Path to OpenAPI YAML/JSON file")
    args = parser.parse_args()

    filepath = Path(args.file)
    if not filepath.exists():
        print(f"Error: File not found: {filepath}", file=sys.stderr)
        sys.exit(1)

    errors = validate(filepath)
    if errors:
        print(f"Validation failed with {len(errors)} error(s):")
        for err in errors:
            print(f"  ✗ {err}")
        sys.exit(1)
    else:
        print("✓ Validation passed")
        sys.exit(0)


if __name__ == "__main__":
    main()
```

脚本设计原则：
- **黑盒调用**：脚本是确定性工具，Claude 直接调用而非读取源码理解
- 运行 `python scripts/xxx.py --help` 先了解参数
- 有明确的输入输出和错误处理
- 不依赖网络或外部服务（或明确声明依赖）

### 步骤 6：编写参考资源（references/）

创建 `skills/api-doc-generator/references/openapi-patterns.md`：

```markdown
# OpenAPI Pattern Reference

Load this file when designing schema structures for common API patterns.

## Pagination

### Offset-based Pagination

```yaml
parameters:
  - name: page
    in: query
    schema: { type: integer, minimum: 1, default: 1 }
  - name: per_page
    in: query
    schema: { type: integer, minimum: 1, maximum: 100, default: 20 }
```

Response envelope:
```yaml
PaginatedResponse:
  type: object
  properties:
    data:
      type: array
      items: { $ref: "#/components/schemas/Item" }
    pagination:
      type: object
      properties:
        page: { type: integer }
        per_page: { type: integer }
        total: { type: integer }
        total_pages: { type: integer }
```

### Cursor-based Pagination

```yaml
parameters:
  - name: cursor
    in: query
    schema: { type: string }
    description: "Opaque cursor from previous response. Omit for first page."
  - name: limit
    in: query
    schema: { type: integer, minimum: 1, maximum: 100, default: 20 }
```

## Error Response Envelope

Use a consistent error format across all endpoints:

```yaml
Error:
  type: object
  required: [error, message]
  properties:
    error:
      type: string
      description: Machine-readable error code
      example: "VALIDATION_ERROR"
    message:
      type: string
      description: Human-readable error message
      example: "Email field is required"
    details:
      type: object
      additionalProperties: true
    request_id:
      type: string
      description: "Request ID for debugging"
```
```

参考资源规则：
- 大文件（>300 行）包含目录
- 在 SKILL.md 中明确标注何时加载（如 "Load during Step 4"）
- 按变体组织（如支持多云则分别 aws.md, gcp.md, azure.md）

### 步骤 7：添加 LICENSE.txt（可选）

```text
MIT License

Copyright (c) 2026

Permission is hereby granted, free of charge, to any person obtaining a copy...
```

### 步骤 8：运行验证脚本

在 anthropics-skills 仓库中使用 skill-creator 的验证工具：

```bash
# 使用 skill-creator 的 quick_validate.py 验证
cd /path/to/anthropics-skills
python skills/skill-creator/scripts/quick_validate.py ../api-doc-generator

# 或使用本项目内的验证（如果复制了脚本）
python skills/api-doc-generator/scripts/validate_schema.py --help
```

`validate_skill()` 执行以下检查：

```python
# 验证流程（quick_validate.py）
1. 检查 SKILL.md 文件是否存在
2. 检查文件是否以 --- 开头
3. 用正则 ^---\n(.*?)\n---（DOTALL）提取 frontmatter
4. 用 yaml.safe_load() 解析
5. 验证结果是字典类型
6. 检查非预期字段（不在 ALLOWED_PROPERTIES 中的字段报错）
7. 检查 name/description 必填字段
8. 校验 name 格式：kebab-case，^[a-z0-9-]+$，≤64 字符
9. 校验 description ≤1024 字符，不含 < >
10. 校验 compatibility ≤500 字符（如存在）
```

### 步骤 9：打包为 .skill 文件

`.skill` 文件本质是 ZIP 压缩包：

```bash
# 使用 skill-creator 的打包脚本
cd /path/to/anthropics-skills
python skills/skill-creator/scripts/package_skill.py \
  ../api-doc-generator \
  ./output
```

打包脚本执行：

```python
# package_skill.py 关键逻辑
# 1. 先运行 validate_skill() 验证
# 2. 使用 zipfile.ZIP_DEFLATED 压缩
# 3. 输出文件名：<directory-name>.skill（用目录名，非 frontmatter name）
# 4. 自动排除：
#    - 目录：__pycache__, node_modules
#    - 根目录专属：evals/（测试用例不打包）
#    - 文件：.DS_Store
#    - Glob：*.pyc
```

打包后生成 `api-doc-generator.skill`，可以分发给其他用户安装到 Claude Code 中。

```bash
# 验证打包结果
unzip -l output/api-doc-generator.skill
```

### 步骤 10：SKILL.md Body 写作风格

遵循以下指令写作原则（来自 skill-creator SKILL.md）：

| 原则 | 说明 |
|------|------|
| **使用祈使句** | "Run the script"，不是 "You should run the script" |
| **解释"为什么"** | 不生硬写 MUST，而是解释原因 |
| **避免过度约束** | 发现写 ALWAYS/NEVER 全大写时，考虑重构为解释原因 |
| **利用 Theory of Mind** | 让 Skill 通用，不绑定到特定示例 |
| **明确定义输出模板** | 使用 "ALWAYS use this exact template:" 模式 |

SKILL.md 长度指南：
- 推荐 ≤500 行
- 超过 500 行时分层，引用 references/ 中的额外文件
- 最重要的内容前置

### 步骤 11：安全原则

Skill 不得包含：
- 恶意软件、漏洞利用代码
- API 密钥、令牌或凭证
- 意图让用户感到意外的内容（"Lack of Surprise" 原则）
- Prompt 注入攻击字符串（打包前运行安全扫描）

如果使用了 `allowed-tools`，不要声明比需要更多的权限。

## 本地测试 Skill

在 Claude Code 中测试本地 Skill：

```bash
# 将 Skill 目录链接到 Claude Code skills 目录
ln -s $(pwd)/skills/api-doc-generator ~/.claude/skills/api-doc-generator

# 或复制
cp -r skills/api-doc-generator ~/.claude/skills/

# 重启 Claude Code 后，用触发词测试
# 例如说："帮我为用户管理API生成 OpenAPI 文档"
```

## 相关概念

- [SKILL.md 格式规范](../concepts/skill-md-format-spec.md)
- [渐进式加载机制](../concepts/progressive-loading.md)
- [Skill 打包格式](../concepts/skill-packaging.md)
- [评估与基准框架](../concepts/eval-benchmark-framework.md)
