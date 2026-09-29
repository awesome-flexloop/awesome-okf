---
title: 工具调用模式
type: concept
bundle: pocketflow-patterns
source: cookbook/pocketflow-code-generator
related:
  - /pocketflow/pocketflow-patterns/concepts/agent-loop
---

# 工具调用模式

工具调用模式在Agent循环基础上，将具体操作封装为独立"工具节点"，决策节点根据LLM输出选择调用哪个工具。

## 结构图

```
┌──────────────┐
│ ToolDecision  │  LLM决定调用哪个工具
│ (返回工具名)  │
└──────┬───────┘
       │
  ┌────┼────┬─────────┐
  │    │    │         │
"search" "code" "calc" ...
  │    │    │
  ▼    ▼    ▼
┌────┐┌────┐┌────┐
│搜索││代码││计算│ ...
└─┬──┘└─┬──┘└─┬──┘
  └─────┼─────┘
        │ "decide"
        └────────→ ToolDecision（循环）
```

## 实现方式

决策节点返回工具名称，每个工具是独立节点，执行完后都回到决策节点：

```python
decide - "search" >> search
decide - "execute_code" >> execute
decide - "calendar" >> calendar
decide - "answer" >> answer

search - "decide" >> decide
execute - "decide" >> decide
calendar - "decide" >> decide
```

## MCP 工具集成

`pocketflow-mcp` 示例展示了如何通过 MCP（Model Context Protocol）协议接入外部工具服务：

```python
# 工具节点动态发现MCP工具
class MCPToolNode(Node):
    def exec(self, prep_res):
        tool_name = self.params["tool"]
        args = self.params["args"]
        return call_mcp_tool(tool_name, args)
```

## Cookbook 对应示例

- `pocketflow-code-generator` — 代码生成+执行工具
- `pocketflow-google-calendar` — Google Calendar API工具
- `pocketflow-mcp` — MCP协议工具集成
- `pocketflow-coding-agent` — 编码Agent（多工具）
- `pocketflow-text2sql` — Text-to-SQL工具
- `pocketflow-invoice` — 发票生成工具
