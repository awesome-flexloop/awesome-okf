---
bundle: pocketflow-core
phase: R (事实采集)
source: d:\spaces\SpecWeave\external\libs\ai\ThePocket\PocketFlow
facts_count: 50
---

# PocketFlow 核心框架 — 事实采集

## 模块与导入

1. PocketFlow 是单文件框架：所有核心代码在 `pocketflow/__init__.py` 中，约 200 行。
2. 导出 12 个公共类：`BaseNode`、`Node`、`BatchNode`、`Flow`、`BatchFlow`、`AsyncNode`、`AsyncBatchNode`、`AsyncParallelBatchNode`、`AsyncFlow`、`AsyncBatchFlow`、`AsyncParallelBatchFlow`、`_ConditionalTransition`（内部类，通过运算符重载间接使用）。
3. 同步类通过 `from pocketflow import Node, Flow, BatchNode, BatchFlow` 导入；异步类通过 `from pocketflow import AsyncNode, AsyncFlow, AsyncBatchNode, AsyncParallelBatchNode, AsyncBatchFlow, AsyncParallelBatchFlow` 导入。
4. 框架无任何第三方依赖，仅使用 Python 标准库：`copy`、`warnings`、`asyncio`。

## BaseNode 基类

5. `BaseNode.__init__(self)` 初始化两个空字典：`self.params = {}`（节点参数）、`self.successors = {}`（后继节点映射，key 为 action 字符串，value 为节点对象）。
6. `BaseNode.set_params(self, params)` 将传入的 params 字典合并更新到 `self.params`：`self.params.update(params)`。
7. `BaseNode.next(self, node, action="default")` 方法：设置后继节点——`self.successors[action] = node`，返回传入的 node 对象（支持链式调用）。
8. `BaseNode.prep(self, shared)` — 前处理步骤，默认返回 None；在同步节点中执行前读取/准备 shared 数据。
9. `BaseNode.exec(self, prep_res)` — 核心执行步骤，默认返回 None；接收 prep 的返回值作为输入。
10. `BaseNode.post(self, shared, prep_res, exec_res)` — 后处理步骤，默认返回 None；可修改 shared 存储，返回值决定下一个 action 分支。
11. `BaseNode._exec(self, prep_res)` — 内部执行方法，直接调用 `self.exec(prep_res)`，子类可重写以添加重试逻辑。
12. `BaseNode._run(self, shared)` — 内部运行方法：调用 `prep(shared)` → `_exec(prep_result)` → `post(shared, prep_result, exec_result)`，返回 post 的结果作为 action。
13. `BaseNode.run(self, shared)` — 公开同步运行接口：调用 `self._run(shared)`，返回 action 字符串（或 None）。
14. `BaseNode >> other_node` — 运算符重载：调用 `self.next(other_node, "default")`，即设置默认后继节点，返回 other_node。
15. `BaseNode - action_string` — 运算符重载：返回 `_ConditionalTransition(self, action_string)` 对象，用于条件分支。

## _ConditionalTransition 内部类

16. `_ConditionalTransition` 是一个过渡对象，持有 `node`（源节点）和 `action`（条件字符串）。
17. `_ConditionalTransition.__rshift__(self, other)` — 当执行 `node - "action" >> target_node` 时，调用 `self.node.next(other, self.action)`，即设置条件分支后继节点。

## Node 类（同步节点，带重试）

18. `Node` 继承自 `BaseNode`，在 `__init__(self, max_retries=1)` 中接收 `max_retries` 参数（默认 1，即不重试）。
19. `Node._exec(self, prep_res)` 重写：实现重试循环——`for _ in range(self.max_retries)`，每次调用 `self.exec(prep_res)`；若成功返回结果；若抛出异常且还有重试次数则继续重试。
20. 重试耗尽后：如果节点定义了 `exec_fallback(self, prep_res, exc)` 方法，则调用它返回降级结果；否则重新抛出最后一个异常。
21. `exec_fallback` 方法是可选的降级处理，签名为 `exec_fallback(self, prep_res, exc)`，当 max_retries 次重试全部失败后被调用。
22. Node 节点的三个核心方法签名：`prep(self, shared)`、`exec(self, prep_res)`、`post(self, shared, prep_res, exec_res)`。
23. Node 节点的 post 方法返回值语义：返回 None 表示走 default 分支；返回字符串表示走对应 action 分支；返回其他值（如信号字符串）作为 Flow 的最终返回值。

## BatchNode 类（同步批量节点）

24. `BatchNode` 继承自 `Node`，重写了 `_exec(self, items)` 方法。
25. `BatchNode._exec` 遍历 prep 返回的可迭代对象 items，对每个 item 调用 `self.exec(item)`，收集所有结果组成列表返回。
26. BatchNode 的典型用法：`prep` 返回待处理项列表，`exec` 处理单个项，`post` 接收结果列表进行汇总。
27. BatchNode 的 exec 方法签名为 `exec(self, item)`，每次处理一个元素。

## Flow 类（同步流程）

28. `Flow` 继承自 `Node`，构造函数 `Flow(start=None)` 可选接收起始节点；也可通过 `flow.start(node)` 方法后续设置。
29. `Flow.start(self, start=None)` 方法：设置 `self.start_node`，返回 self 以支持链式调用（如 `flow.start(n1).next(n2)`）。
30. `Flow._orch(self, shared, params=None)` 是核心编排方法：
    - 从 `copy.copy(self.start_node)` 开始（使用浅拷贝避免状态污染）
    - 将 params（或 self.params）合并为参数集 p
    - 循环：curr.set_params(p) → last_action = curr._run(shared) → curr = copy.copy(self.get_next_node(curr, last_action))
    - 当 curr 为 None 时退出循环，返回 last_action
31. `Flow.get_next_node(self, curr, action)` 方法：从 `curr.successors` 中查找 key 为 action 的后继节点；若找不到，查找 key 为 str(action) 的后继节点；若都找不到，查找 key 为 "default" 的后继节点。若 "default" 也找不到，发出 UserWarning 并返回 None。
32. Flow 作为 Node 使用：Flow 继承自 Node，因此 Flow 可以嵌套在另一个 Flow 中作为节点运行。Flow 的 `_run` 方法实际上调用 `self._orch(shared)`。
33. Flow 运行时对每个节点使用 `copy.copy()` 浅拷贝：这意味着节点的实例属性（如 self.number）会被复制，但节点间共享的类属性不会重复创建。
34. Flow 的 `run(self, shared)` 方法：公开入口，调用 `self._orch(shared)`，返回最后一个节点 post 的返回值（即 last_action）。

## BatchFlow 类（同步批量流程）

35. `BatchFlow` 继承自 `Flow`，重写了 `_orch(self, shared, params=None)`。
36. BatchFlow._orch 首先调用 `self.prep(shared)` 获取参数列表（每个元素是一个 params 字典），然后对每个 params 字典，调用父类 `Flow._orch(shared, params)` 执行子流程。
37. BatchFlow 的 `prep(self, shared)` 方法（继承自 BaseNode，需子类重写）应返回一个列表，列表中每个元素是传给子流程节点的 params 字典。
38. 每个参数集会通过 `set_params` 注入到子流程的节点中，节点通过 `self.params.get(key)` 访问。
39. BatchFlow 支持嵌套：内层 BatchFlow 的 prep 可通过 `self.params` 获取外层 BatchFlow 传入的参数。

## AsyncNode 类（异步节点）

40. `AsyncNode` 继承自 `Node`，提供三个异步核心方法：`prep_async(self, shared)`、`exec_async(self, prep_res)`、`post_async(self, shared, prep_res, exec_res)`。
41. AsyncNode 重写了 `_run` 为异步方法 `_run_async(self, shared)`：await prep_async → await _exec_async → await post_async。
42. AsyncNode 的 `_exec_async(self, prep_res)` 实现异步重试循环：与同步版类似，但每次重试 await `self.exec_async(prep_res)`。
43. 异步降级方法为 `exec_fallback_async(self, prep_res, exc)`，重试耗尽后调用。
44. AsyncNode 的 `run(self, shared)` 方法是同步入口，内部使用 `asyncio.run(self.run_async(shared))` 执行。
45. `run_async(self, shared)` 是异步入口，await `self._run_async(shared)`。
46. AsyncNode 的 `exec` 方法默认为同步空操作（pass），但子类若同时定义了同步和异步方法，异步方法优先。

## AsyncBatchNode 类（异步串行批量节点）

47. `AsyncBatchNode` 继承自 `AsyncNode`，`_exec_async` 依次 await 每个 item 的 exec_async（串行执行），返回结果列表。

## AsyncParallelBatchNode 类（异步并行批量节点）

48. `AsyncParallelBatchNode` 继承自 `AsyncNode`，`_exec_async` 使用 `asyncio.gather(*[self.exec_async(item) for item in items])` 并行执行所有 item。
49. 并行执行时所有 item 同时启动，结果按输入顺序排列，总耗时约等于单个最慢 item 的耗时。

## AsyncFlow / AsyncBatchFlow / AsyncParallelBatchFlow

50. `AsyncFlow` 继承自 `AsyncNode`，`_orch_async` 使用 await 驱动节点流转；节点可以是 AsyncNode 或普通 Node（同步节点在异步流程中通过 `asyncio.to_thread` 或直接调用运行——具体取决于实现）。
51. `AsyncBatchFlow` 继承自 `AsyncFlow`，与 BatchFlow 类似，但 prep_async 返回参数列表后串行 await 每个子流程。
52. `AsyncParallelBatchFlow` 继承自 `AsyncFlow`，使用 `asyncio.gather` 并行运行多个子流程实例。

## 测试验证的行为特性

53. 线性管道使用 `>>` 连接：`n1 >> n2 >> n3`，所有节点 post 返回 None（default 分支）。
54. 条件分支使用 `- "action" >>`：`check - "positive" >> add_pos; check - "negative" >> add_neg`，check 的 post 必须返回对应的字符串。
55. 自环实现循环：`check - 'positive' >> subtract3; subtract3 >> check`，直到 check 返回 'negative' 退出。
56. Flow 结束时若找不到匹配 action 的后继且无 default，发出 UserWarning："Flow ends: '<action>' not found in [<keys>]"。
57. Flow 可以嵌套 Flow：内层 Flow 作为外层 Flow 的一个节点，内层 Flow 最后一个节点的 post 返回值作为外层 Flow 的 action 分支依据。
58. Flow 支持 `Flow(start=node)` 构造函数直接指定起始节点。
59. Node 的 max_retries 参数控制 exec 重试次数：max_retries=2 表示最多尝试 2 次（1次初始 + 1次重试）；重试失败后若有 exec_fallback 则调用它，否则抛出异常。
60. AsyncNode 可混合使用同步 exec 和异步 exec_async：AsyncNode 优先使用 exec_async。
61. AsyncParallelBatchNode 的并行执行：items 同时启动，结果顺序与输入顺序一致；通过执行时间验证了并行性（5个0.1s延迟任务总耗时 < 0.2s）。
62. BatchFlow 的 params 传递：prep 返回 `[{'key': 'a'}, {'key': 'b'}]`，节点内通过 `self.params.get('key')` 获取当前参数。
63. BatchFlow 支持自定义参数：prep 可返回包含多个键值对的 params 字典，节点可同时访问多个参数。
64. BatchFlow 嵌套：外层 BatchFlow 的 prep 返回 group 参数，内层 BatchFlow 的 prep 根据 group 返回 item 参数。
