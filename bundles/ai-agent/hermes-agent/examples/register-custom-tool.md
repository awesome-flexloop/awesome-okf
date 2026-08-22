---
okf_version: "0.2"
type: example
title: 注册自定义工具
description: 使用 ToolRegistry 单例注册自定义工具，定义 OpenAI Function Schema，编写 handler 函数，通过 check_fn 控制可用性，让 Agent 能够调用自定义业务逻辑
tags: [hermes-agent, example, tool-registry, custom-tool, function-calling, schema]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-23T00:00:00+08:00" }
status: stable
stale_after: 2027-08-23
related:
  - /concepts/tool-registry.md
  - /concepts/agent-core-loop.md
sources:
  - id: hermes-agent-self
    resource: /references/hermes-agent-sources.md
    title: hermes-agent 源码参考
---

# 注册自定义工具

## 场景说明

本示例演示如何向 hermes-agent 的 `ToolRegistry` 单例注册自定义工具。通过定义符合 OpenAI Function Calling 规范的 JSON Schema、编写 handler 处理函数、设置 `check_fn` 可用性检查，Agent 即可在对话中自动发现并调用你的自定义业务逻辑。这是扩展 Agent 能力边界的核心方式。

**前置条件**：
- Python ≥ 3.11 且 < 3.14
- 已安装 hermes-agent（`pip install hermes-agent`）
- 拥有一个兼容 OpenAI Chat Completions API 的模型服务
- 理解 [工具注册表概念](/concepts/tool-registry.md)

## 完整代码示例

```python
"""
register-custom-tool.py
演示：向 ToolRegistry 注册自定义工具并在 Agent 对话中使用
"""
import os
import json
import hashlib
import datetime
from typing import Optional, List, Dict, Any

# ── 步骤 1：从 tools.registry 导入单例 registry 和 tool_error ──
from tools.registry import registry, tool_error


# ── 步骤 2：定义工具的业务逻辑 ──

def calculate_checksum(file_path: str, algorithm: str = "sha256") -> str:
    """计算文件校验和（示例业务逻辑）。"""
    if not os.path.isfile(file_path):
        return tool_error(
            f"文件不存在: {file_path}",
            error_type="file_not_found",
            tool="calculate_checksum",
        )
    try:
        h = hashlib.new(algorithm)
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        return json.dumps({
            "file": file_path,
            "algorithm": algorithm,
            "checksum": h.hexdigest(),
            "size_bytes": os.path.getsize(file_path),
        }, ensure_ascii=False)
    except Exception as e:
        return tool_error(
            f"计算校验和失败: {str(e)}",
            error_type="checksum_error",
            tool="calculate_checksum",
        )


def get_current_time(timezone: str = "Asia/Shanghai") -> str:
    """获取当前时间（示例业务逻辑）。"""
    try:
        now = datetime.datetime.now(datetime.timezone.utc)
        # 简化版时区处理（实际项目可用 zoneinfo）
        tz_offsets = {
            "Asia/Shanghai": 8,
            "UTC": 0,
            "America/New_York": -5,
            "Europe/London": 0,
            "Asia/Tokyo": 9,
        }
        offset_hours = tz_offsets.get(timezone, 8)
        local = now + datetime.timedelta(hours=offset_hours)
        return json.dumps({
            "timezone": timezone,
            "datetime": local.strftime("%Y-%m-%d %H:%M:%S"),
            "utc_datetime": now.strftime("%Y-%m-%d %H:%M:%S"),
            "unix_timestamp": int(now.timestamp()),
            "weekday": local.strftime("%A"),
        }, ensure_ascii=False)
    except Exception as e:
        return tool_error(
            f"获取时间失败: {str(e)}",
            error_type="time_error",
            tool="get_current_time",
        )


def list_directory(path: str, pattern: Optional[str] = None) -> str:
    """列出目录内容（示例业务逻辑）。"""
    import fnmatch
    if not os.path.isdir(path):
        return tool_error(
            f"目录不存在: {path}",
            error_type="directory_not_found",
            tool="list_directory",
        )
    try:
        entries = []
        for name in sorted(os.listdir(path)):
            if pattern and not fnmatch.fnmatch(name, pattern):
                continue
            full_path = os.path.join(path, name)
            entries.append({
                "name": name,
                "type": "directory" if os.path.isdir(full_path) else "file",
                "size": os.path.getsize(full_path) if os.path.isfile(full_path) else None,
            })
        return json.dumps({
            "path": path,
            "pattern": pattern,
            "entries": entries,
            "total": len(entries),
        }, ensure_ascii=False)
    except PermissionError:
        return tool_error(
            f"权限不足，无法访问目录: {path}",
            error_type="permission_denied",
            tool="list_directory",
        )
    except Exception as e:
        return tool_error(
            f"列出目录失败: {str(e)}",
            error_type="list_error",
            tool="list_directory",
        )


# ── 步骤 3：定义 check_fn（可选，用于运行时可用性检查） ──

def check_checksum_requirements() -> bool:
    """checksum 工具无外部依赖，始终可用。"""
    return True


def check_time_requirements() -> bool:
    """时间工具无外部依赖，始终可用。"""
    return True


def check_directory_requirements() -> bool:
    """目录工具需要文件系统访问权限（模拟检查）。"""
    return os.access(os.getcwd(), os.R_OK)


# ── 步骤 4：定义 OpenAI Function Schema ──

CHECKSUM_SCHEMA = {
    "name": "calculate_checksum",
    "description": (
        "计算指定文件的哈希校验和。支持 md5、sha1、sha256、sha512 算法。"
        "用于验证文件完整性或检测文件变更。"
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "要计算校验和的文件的绝对路径",
            },
            "algorithm": {
                "type": "string",
                "description": "哈希算法名称",
                "enum": ["md5", "sha1", "sha256", "sha512"],
                "default": "sha256",
            },
        },
        "required": ["file_path"],
    },
}

TIME_SCHEMA = {
    "name": "get_current_time",
    "description": (
        "获取当前日期和时间。支持多时区，返回本地时间、UTC时间、Unix时间戳和星期几。"
        "当用户询问'现在几点'、'今天几号'等时间相关问题时使用。"
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "timezone": {
                "type": "string",
                "description": "目标时区名称（IANA时区格式）",
                "enum": ["Asia/Shanghai", "UTC", "America/New_York", "Europe/London", "Asia/Tokyo"],
                "default": "Asia/Shanghai",
            },
        },
        "required": [],
    },
}

LIST_DIR_SCHEMA = {
    "name": "list_directory",
    "description": (
        "列出指定目录下的文件和子目录。支持通配符过滤（如 *.py、*.md）。"
        "当用户需要查看目录内容、查找特定类型文件时使用。"
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "要列出的目录的绝对路径",
            },
            "pattern": {
                "type": "string",
                "description": "可选的通配符过滤模式，如 *.py、*.md",
            },
        },
        "required": ["path"],
    },
}


# ── 步骤 5：向 registry 注册工具 ──

registry.register(
    name="calculate_checksum",
    toolset="file_utils",          # 工具集分组名
    schema=CHECKSUM_SCHEMA,         # OpenAI Function Schema
    handler=lambda args, **kw: calculate_checksum(
        file_path=args.get("file_path", ""),
        algorithm=args.get("algorithm", "sha256"),
    ),
    check_fn=check_checksum_requirements,  # 可用性检查
    emoji="🔐",                     # 工具图标（用于 UI 显示）
    description="计算文件哈希校验和",  # 简短描述（覆盖 schema 中的 description）
)

registry.register(
    name="get_current_time",
    toolset="time_utils",
    schema=TIME_SCHEMA,
    handler=lambda args, **kw: get_current_time(
        timezone=args.get("timezone", "Asia/Shanghai"),
    ),
    check_fn=check_time_requirements,
    emoji="🕐",
)

registry.register(
    name="list_directory",
    toolset="file_utils",
    schema=LIST_DIR_SCHEMA,
    handler=lambda args, **kw: list_directory(
        path=args.get("path", ""),
        pattern=args.get("pattern"),
    ),
    check_fn=check_directory_requirements,
    emoji="📁",
)


# ── 步骤 6：验证注册结果并使用 Agent ──

def main():
    # 验证工具已注册
    print("=== 已注册的工具 ===")
    for toolset in registry.get_registered_toolset_names():
        tools = registry.get_tool_names_for_toolset(toolset)
        print(f"  [{toolset}]: {', '.join(tools)}")

    # 获取工具定义（传入工具名集合）
    our_tools = {"calculate_checksum", "get_current_time", "list_directory"}
    definitions = registry.get_definitions(our_tools)
    print(f"\n=== 工具定义数量: {len(definitions)} ===")
    for d in definitions:
        fn = d["function"]
        print(f"  - {fn['name']}: {fn['description'][:60]}...")

    # 手动调用工具（模拟 Agent 调用）
    print("\n=== 手动测试工具调用 ===")

    # 测试 get_current_time
    entry = registry.get_entry("get_current_time")
    if entry:
        result = entry.handler({"timezone": "Asia/Shanghai"})
        print(f"get_current_time 结果: {result}")

    # 测试 list_directory
    entry = registry.get_entry("list_directory")
    if entry:
        result = entry.handler({"path": os.getcwd(), "pattern": "*.py"})
        data = json.loads(result)
        print(f"list_directory 结果: 共 {data['total']} 个 .py 文件")

    # 初始化 Agent 并对话（工具会自动被 Agent 使用）
    from run_agent import AIAgent

    agent = AIAgent(
        provider="openai",
        model="gpt-4o-mini",
        base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
        api_key=os.getenv("OPENAI_API_KEY", ""),
        toolsets=["file_utils", "time_utils"],  # 启用自定义工具集
        tools=list(our_tools),                  # 显式启用我们的工具
    )

    print("\n=== Agent 对话 ===")
    response = agent.chat("现在几点钟？帮我看看当前目录下有什么文件？")
    print(f"Agent: {response}")


if __name__ == "__main__":
    main()
```

## 逐步解释

### 步骤 1：导入 registry 单例

`tools.registry` 模块导出全局单例 `registry` 和 `tool_error` 辅助函数：
- `registry` 是 `ToolRegistry` 的唯一实例，所有工具必须通过它注册
- `tool_error()` 用于构造标准化的错误返回，Agent 能正确识别和处理

### 步骤 2：编写业务逻辑函数

每个工具对应一个 Python 函数，遵循以下约定：
- 接收具体参数（而非一个大字典），便于直接测试
- 成功时返回 JSON 字符串（`json.dumps(...)`），结果结构化
- 失败时调用 `tool_error()` 返回错误信息，包含 `error_type` 和 `tool` 字段
- **禁止**返回非字符串值（dict/list/None 等），registry 会将其转为错误

### 步骤 3：定义 check_fn

`check_fn` 是无参函数，返回 `bool`，用于运行时检测工具是否可用：
- 返回 `True`：工具可用，会被暴露给模型
- 返回 `False`：工具不可用，会从本次 `get_definitions()` 结果中过滤掉
- 结果会被缓存约 30 秒，避免频繁探测外部资源（如 Docker 守护进程、数据库连接）
- 对于无外部依赖的工具，直接 `return True` 即可

### 步骤 4：编写 OpenAI Function Schema

Schema 是一个 dict，遵循 OpenAI Function Calling 格式：
- `name`：工具名称，必须与注册时的 `name` 参数一致
- `description`：给模型看的功能描述，决定模型何时调用此工具，**越清晰越好**
- `parameters`：JSON Schema 格式定义参数类型、描述、枚举值、默认值、必填项
- Schema 中的 `description` 是指导模型行为的关键，应当包含使用场景提示

### 步骤 5：调用 registry.register()

`register()` 方法接受以下关键参数：

| 参数 | 类型 | 说明 |
|------|------|------|
| `name` | str | 工具唯一名称，不能与其他工具重名（跨工具集重名需 `override=True`） |
| `toolset` | str | 工具集分组名，用于批量启用/禁用 |
| `schema` | dict | OpenAI Function Schema 定义 |
| `handler` | Callable | 处理函数，签名为 `handler(args: dict, **kwargs) -> str` |
| `check_fn` | Callable | 可选，可用性检查函数 |
| `requires_env` | list | 可选，所需环境变量名列表 |
| `is_async` | bool | 是否异步处理函数（默认 False） |
| `emoji` | str | 可选，UI 显示用的图标 |
| `description` | str | 可选，简短描述（覆盖 schema 中的 description） |
| `override` | bool | 是否允许覆盖同名内置工具（插件专用，需配置授权） |

handler 的 `**kwargs` 会传入运行时上下文，如 `store`（TodoStore 实例）、`agent`（AIAgent 实例）等。

### 步骤 6：在 Agent 中使用

初始化 `AIAgent` 时：
- 通过 `toolsets` 参数批量启用工具集（如 `"file_utils"`）
- 或通过 `tools` 参数显式指定工具名
- Agent 在 Think-Act-Observe 循环中会自动发现工具定义，在需要时调用

## 输出结果

运行脚本后，预期输出类似：

```
=== 已注册的工具 ===
  [file_utils]: calculate_checksum, list_directory
  [time_utils]: get_current_time
  ... (其他内置工具集)

=== 工具定义数量: 3 ===
  - calculate_checksum: 计算指定文件的哈希校验和。支持 md5、sha1、sha256...
  - get_current_time: 获取当前日期和时间。支持多时区，返回本地时间、UTC时间...
  - list_directory: 列出指定目录下的文件和子目录。支持通配符过滤...

=== 手动测试工具调用 ===
get_current_time 结果: {"timezone": "Asia/Shanghai", "datetime": "2026-08-23 14:30:00", ...}
list_directory 结果: 共 5 个 .py 文件

=== Agent 对话 ===
Agent: 现在北京时间是 2026年8月23日 14:30。当前目录下我看到有5个Python文件，包括...
```

## 注意事项

1. **handler 返回值约束**：handler 必须返回字符串（JSON 格式）或 multimodal 信封。返回 dict/list/None 等会被 `_normalize_handler_result()` 转为错误，导致 Agent 看到工具调用失败。

2. **Schema description 至关重要**：模型通过 description 判断何时调用工具。描述要包含：工具做什么、什么时候用、参数含义、返回内容。模糊的描述会导致工具误用或不用。

3. **toolset 命名规范**：自定义工具使用独立的 toolset 名称，避免与内置工具集（`terminal`、`web`、`file` 等）冲突。跨工具集重名注册会被拒绝，除非显式传 `override=True`（需要插件授权）。

4. **check_fn 缓存**：`check_fn` 返回值有 30 秒 TTL 缓存，加上 60 秒瞬态故障宽限期。外部依赖检查（如数据库连接）偶尔超时时不会立即导致工具消失。配置变更后可调用 `invalidate_check_fn_cache()` 清除缓存。

5. **线程安全**：`ToolRegistry` 使用 `RLock` 保护注册/查询操作，支持多线程环境（如 Gateway 模式下多会话并发）。

6. **错误处理最佳实践**：始终使用 `tool_error()` 返回错误，而不是直接 `raise`。未捕获的异常会被调度层转为通用错误消息，丢失上下文信息。

7. **模块级注册**：内置工具在模块导入时自动调用 `registry.register()`。自定义工具也应放在独立模块中，在模块顶层调用 `register()`，然后通过 `importlib.import_module()` 或直接 import 触发注册。
