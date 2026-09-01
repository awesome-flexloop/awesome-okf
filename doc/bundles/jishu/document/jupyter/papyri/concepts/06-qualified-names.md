---
type: Concept
title: 限定名与交叉引用
description: "Papyri 的限定名（Qualified Names）系统——使用 : 分隔符消除模块/属性歧义，以及 CrossRef/RefInfo/LocalRef 的引用机制"
tags: [papyri, qualified-names, cross-reference, refinfo, linking]
generated: { by: reference_agent/trae-soLO, at: "2026-08-22T00:00:00Z" }
verified: { by: "process:grep-api-check", at: "2026-08-22T00:00:00Z" }
status: stable
stale_after: 2027-02-22
sources:
  - id: papyri-src
    resource: /references/papyri-source.md
    title: Papyri Python 核心包源码信源
  - id: nodes-src
    resource: /references/ir-nodes-source.md
    title: Papyri IR 节点类型源码信源
---

## 为什么需要限定名

Python 中使用点号（`.`）同时表示模块路径分隔和属性访问。这导致歧义：`numpy.linalg.norm` 中的 `.` 既可以理解为"numpy 模块的 linalg 子模块的 norm 函数"，也可以理解为"numpy 模块的 linalg 属性的 norm 属性"。当包从子模块重新导出名称时（如 `from .sub import foo` 后在包级别可以 `import pkg; pkg.foo`），点号分隔无法消除"这个点是模块路径还是属性"的歧义。

Papyri 使用冒号（`:`）作为模块路径与属性路径的分隔符来解决这个问题。

## 限定名格式

Papyri 的限定名（Qualified Name, QA）格式为：

```
<module-path>:<attribute-path>
```

- **模块路径**：`importlib.import_module()` 可以直接导入的模块名（不含点号歧义）
- **属性路径**：模块内的属性/类/方法/函数访问链，使用点号分隔

示例：

| 限定名 | 模块 | 属性 | 说明 |
|--------|------|------|------|
| `numpy:einsum` | `numpy` | `einsum` | numpy 顶层函数 |
| `numpy.linalg:norm` | `numpy.linalg` | `norm` | numpy.linalg 子模块的 norm 函数 |
| `numpy:ndarray.reshape` | `numpy` | `ndarray.reshape` | numpy.ndarray 类的 reshape 方法 |
| `numpy:zeros_like` | `numpy` | `zeros_like` | numpy.zeros_like 函数 |
| `package.sub:attribute` | `package.sub` | `attribute` | 子模块的属性 |

> [!IMPORTANT]
> Papyri 命令行使用限定名（`numpy:einsum`），而非 Python 点号表示法（`numpy.einsum`）。`--only` 选项也接受限定名。

## 引用节点类型

Papyri IR 中有三种核心引用类型：

### RefInfo：跨包引用（tag 4000）

`RefInfo` 是一个 frozen dataclass，指向（可能在另一个 bundle 中的）文档对象：

```python
@register(4000)
@dataclass(frozen=True)
class RefInfo(Node):
    module: str | None   # 模块名（不含点号），None 表示当前模块
    version: str | None  # 版本号，None 表示当前版本
    kind: str            # 文档类型："api"/"module"/"example"/"docs"/"to-resolve"/"missing" 等
    path: str            # 完整路径
```

`kind` 字段携带解析状态：

- `"to-resolve"`：gen 输出的占位符，表示无法在本地解析，需要 ingest 的 relink pass 处理
- `"missing"`：ingest 尝试解析但找不到目标，渲染时应显示为纯文本
- 其他值（`"module"`, `"local"`, `"api"` 等）：已解析

`RefInfo.from_untrusted(module, version, kind, path)` 是安全的工厂方法，断言 module 中不包含冒号。

`__post_init__` 中断言 `module` 不含点号（模块名必须是顶层的，不含 `.`）。

### LocalRef：同包引用（tag 4022）

`LocalRef` 是 frozen dataclass，指向同一 bundle 内的文档：

```python
@register(4022)
@dataclass(frozen=True)
class LocalRef(Node):
    kind: str  # 文档类型："docs"/"module"/"examples" 等
    path: str  # bundle 内路径
```

与 RefInfo 不同，LocalRef 省略 module 和 version，因为它们总是从 bundle 上下文中继承。Gen 在写入前验证目标存在，因此 LocalRef 保证链接有效。

### CrossRef：交叉引用（tag 4002）

`CrossRef` 是最终的交叉引用节点，出现在 IR 树的行内内容中：

```python
@register(4002)
class CrossRef(Node):
    value: str                    # 显示文本
    reference: RefInfo | LocalRef # 引用目标
    kind: str                     # 分类提示（如 "module"/"func"/"api"）
```

`exists` 属性是派生属性，基于 `reference.kind` 判断引用是否已解析：
- `reference` 为 LocalRef → 总是存在
- `reference.kind` 在 `("to-resolve", "missing")` → 不存在
- 其他 → 存在

注意：`kind` 字段不是 `reference.kind` 的冗余副本——两者可能不同（如 toctree 处理器中的场景）。

### InlineRole：未解析的角色（@debug 4003）

`InlineRole` 表示 RST 解释文本角色（如 ``:func:`numpy.linspace```），在 gen 阶段大多被替换为 `CrossRef`。包含字段：

- `value`：角色内容文本
- `domain`：Sphinx 域（如 `"py"`），None 为默认域
- `role`：角色名（如 `"func"`），None 为默认角色
- `inventory`：intersphinx 外部库存名（`:external+<inv>:…:` 前缀），None 为同项目引用

`prefix` 属性重建完整的 RST 前缀（如 `:external+inv:py:func:`）。

## 引用解析流程

### Gen 阶段（尽力而为）

1. 解析 docstring 中的 ``:func:`name``` 等角色 → 生成 `InlineRole`
2. 在同模块内查找匹配的对象 → 转换为 `CrossRef`（LocalRef 或 RefInfo）
3. 无法解析的 → `RefInfo(kind="to-resolve")` 占位符
4. "See Also" 条目初始化为 `RefInfo(kind="to-resolve", module="current-module", version="current-version")`

### Ingest 阶段（relink pass）

TypeScript ingest 引擎在接收到 bundle 后执行 relink：

1. 遍历所有 IR 节点，收集 `CrossRef` 中 kind="to-resolve" 的引用
2. 在已摄取的所有 bundle 中查找匹配目标
3. 找到目标 → 更新 RefInfo 的 module/version/kind/path
4. 找不到 → kind 设为 "missing"
5. 同时建立后向引用链接（backreferences）

### Viewer 阶段（渲染时）

1. 读取 CrossRef → 判断 exists 属性
2. 存在 → 渲染为超链接
3. 不存在（"to-resolve"/"missing"）→ 渲染为纯文本

## Key 四元组

在 GraphStore 和 ingest 中，文档通过四元组 Key 寻址：

```python
class Key(NamedTuple):
    module: str   # 包/模块名
    version: str  # 版本号
    kind: str     # 文档类型
    path: str     # 文档路径
```

这个四元组对应 SQLite `nodes` 表的 UNIQUE 约束：`(package, version, category, identifier)`。

## 工具函数

`utils.py` 提供限定名相关的工具：

- `full_qual(obj)`：获取 Python 对象的完全限定名
- `obj_from_qualname(qualname)`：从限定名字符串导入并返回对象（使用 `get_object()`，逐步尝试最长模块前缀）
- `Canonical`：规范名处理类
- `FullQual`：完全限定名处理类

`get_object(qual)` 函数（nodes.py）实现了智能模块解析：从最长的点号前缀开始尝试 `__import__`，找到可导入的最深模块路径后，再用 `getattr` 逐级获取属性。

## 相关概念

- [IR 节点类型体系](04-ir-node-types.md)
- [gen 管线](05-gen-pipeline.md)
- [GraphStore 与交叉链接](09-graphstore-and-crosslinks.md)
- [TypeScript 摄取与渲染器](12-ingest-and-viewer.md)
