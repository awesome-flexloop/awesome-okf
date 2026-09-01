---
type: Concept
title: 重定向图模型
description: rediraffe的核心算法——将重定向关系建模为有向图，链式压缩到叶子节点，循环检测保证正确性
tags: [sphinxext-rediraffe, graph, algorithm, directed-acyclic-graph, cycle-detection]
generated: { by: "reference_agent/trae-glm", at: "2026-08-21T16:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T16:30:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: rediraffe-source
    resource: /references/rediraffe-source.md
    title: sphinxext-rediraffe 源码信源登记
---

# 重定向图模型

## 为什么需要图模型

最朴素的重定向实现是：对每个 `源→目标` 对，在源位置生成一个跳转到目标的HTML文件。但这种方式存在两个问题：

1. **链式跳转**：如果 A→B，B→C，C→D，用户访问 A 时会经历 A→B→C→D 三次HTTP重定向，体验差且可能被浏览器拦截
2. **循环风险**：如果配置了 A→B，B→A，用户会陷入无限重定向循环

rediraffe 通过**有向图模型**解决这两个问题。

## 图的基本概念

在 rediraffe 中：
- **顶点（Vertex）**：每个文档路径是图中的一个顶点
- **边（Edge）**：`源→目标` 重定向关系是图中的一条有向边，从源指向目标
- **叶子节点（Leaf）**：不作为任何边起点的顶点（即该页面没有被重定向走，是实际存在的最终页面）

```
    重定向配置            有向图表示

a.rst → b.rst           a ──→ b ──→ c ──→ d (叶子)
b.rst → c.rst
c.rst → d.rst           e ──→ f (叶子)
e.rst → f.rst
```

## create_graph：从文本到图

`create_graph(path)` 函数负责解析重定向文件（或直接使用dict），将其转换为 `dict[str, str]` 形式的邻接表。

### 文件格式解析

重定向文件的每一行是一条边：

```text
# 注释行以#开头
源路径 目标路径
"带空格的源" "带空格的目标"
'单引号也可以' 不带引号的目标
```

解析正则表达式：

```python
RE_OBJ = re.compile(r"(?:(\"|')(.*?)\1|(\S+))\s+(?:(\"|')(.*?)\4|(\S+))")
```

这个正则的含义：
- `(?:("|')(.*?)\1|(\S+))`：匹配源路径——要么是引号包裹的内容（捕获组2），要么是非空白字符序列（捕获组3）
- `\s+`：一个或多个空白字符分隔
- `(?:("|')(.*?)\4|(\S+))`：匹配目标路径——同理（捕获组5或6）

解析逻辑：
```python
edge_from = match.group(2) or match.group(3)  # 取引号内容或非空内容
edge_to = match.group(5) or match.group(6)
```

### 错误检测

`create_graph` 在解析过程中检测以下错误：

| 错误类型 | 检测方式 | 处理 |
|---------|---------|------|
| 格式无效行 | `RE_OBJ.fullmatch(line)` 返回 None | 记录行号错误，设置broken=True |
| 重复key | `edge_from in graph_edges` | 记录重复错误，设置broken=True |

任何解析错误最终会抛出 `ExtensionError`，导致构建失败（`app.statuscode = 1`）。

## create_simple_redirects：链式压缩与循环检测

`create_simple_redirects(graph_edges)` 是图模型的核心算法。它的目标是：将图中每个顶点直接连接到它的**叶子节点**。

### 算法流程

```python
def create_simple_redirects(graph_edges: dict) -> dict:
    redirects = {}
    broken_vertices = set()

    for vertex in graph_edges:
        if vertex in broken_vertices:
            continue

        visited = []
        while vertex in graph_edges:
            if vertex in visited:
                # 检测到循环！
                logger.error('A circular redirect exists. Links: ' + ' -> '.join(visited + [vertex]))
                broken_vertices.update(visited)
                break
            visited.append(vertex)
            vertex = graph_edges[vertex]

        # vertex 现在是叶子节点
        for visited_vertex in visited:
            redirects[visited_vertex] = vertex

    if broken_vertices:
        raise ExtensionError(...)

    return redirects
```

### 算法步骤说明

1. **遍历每个起始顶点**：对于图中的每个起点，沿着边的方向遍历
2. **路径追踪**：用 `visited` 列表记录当前遍历路径
3. **循环检测**：如果遍历中遇到已在 `visited` 中的顶点，说明存在环
4. **叶子节点绑定**：遍历到叶子节点后，将路径上所有顶点都直接指向该叶子节点

### 示例：链式压缩

输入：
```python
{'a': 'b', 'b': 'c', 'c': 'd'}
```

遍历过程：
- `a → b → c → d`（d是叶子，不在graph_edges的key中）
- visited = [a, b, c]，叶子 = d

输出：
```python
{'a': 'd', 'b': 'd', 'c': 'd'}
```

### 示例：多链混合

输入：
```python
{'a': 'b', 'b': 'c', 'c': 'd', 'e': 'f', 'g': 'h', 'h': 'i'}
```

输出：
```python
{'a': 'd', 'b': 'd', 'c': 'd', 'e': 'f', 'g': 'i', 'h': 'i'}
```

### 示例：循环检测

输入：
```python
{'a': 'b', 'b': 'a'}
```

遍历过程：
- `a → b → a`（a已在visited=[a,b]中，检测到循环）

结果：抛出 ExtensionError，构建失败。错误信息：
```
rediraffe: A circular redirect exists. Links involved: a -> b -> a
```

### 示例：多环检测

输入包含多个独立循环时，算法会检测所有循环：
```python
{'a': 'b', 'b': 'c', 'c': 'd', 'd': 'e', 'e': 'a',  # 环1
 'f': 'g', 'g': 'h', 'h': 'j', 'j': 'g'}             # 环2
```

结果：错误信息包含所有涉及的顶点。

## 图模型的关键性质

### 1. 每个顶点最多一条出边

由于 `create_graph` 禁止重复key（F-013: "duplicate keys not allowed"），每个顶点最多有一条出边。这意味着图的结构是若干条链组成的森林，而不是复杂的网状结构。

```
合法结构（链状森林）：         非法结构（多父节点）：
a → b → c → d               a → b
e → f                        a → c  ← 重复key a，被create_graph拒绝
g → h → i
```

这个约束大大简化了算法——从任意顶点出发的路径是唯一的，不会出现分叉。

### 2. 叶子节点不在key集合中

叶子节点是不作为重定向源的页面。在 `create_simple_redirects` 的 while 循环中，当 `vertex not in graph_edges` 时停止，此时的 vertex 就是叶子。

叶子节点可以是：
- 实际存在的文档页面（最常见）
- 不存在的页面（会在build_redirects中被检测为"目标不存在"错误）
- 外部URL（但rediraffe仅处理站内相对路径）

### 3. 压缩后无中间节点

`create_simple_redirects` 的输出保证：
- 所有 key 直接映射到叶子节点
- 输出dict的value一定不在key集合中（即value都是叶子）
- 不存在链式跳转

这个性质确保了用户最多经历一次重定向。

## dict 配置 vs 文件配置

无论使用dict还是文件配置，最终都进入相同的图处理流程：

```python
# 方式1：dict配置
rediraffe_redirects = {'a.rst': 'b.rst', 'b.rst': 'c.rst'}
# graph_edges = {'a.rst': 'b.rst', 'b.rst': 'c.rst'} 直接使用

# 方式2：文件配置
rediraffe_redirects = 'redirects.txt'
# graph_edges = create_graph(Path(srcdir) / 'redirects.txt') 解析后得到
```

两种方式在图处理阶段完全等价。

## 算法复杂度分析

设图中有 N 个顶点（重定向条目数）：

- **时间复杂度**：O(N)。每个顶点被访问恰好一次（已访问过的顶点通过 `if vertex in broken_vertices: continue` 跳过，或通过visited遍历后加入redirects）。
- **空间复杂度**：O(N)。存储redirects字典和visited列表。
- **循环检测**：使用列表的 `in` 操作检测循环，复杂度 O(P)（P为当前路径长度）。由于每个顶点最多在一条路径中，总体仍为 O(N)。

实际使用中，重定向条目数通常在几十到几百，性能完全不是问题。

## 相关概念

- [架构概览](02-architecture-overview.md)
- [配置项详解](04-configuration.md)
- [基础重定向示例](../examples/basic-redirects.md)
- [sphinxext-rediraffe 源码信源登记](../references/rediraffe-source.md)
