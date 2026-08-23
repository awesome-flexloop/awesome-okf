---
type: Concept
title: ApplicationNamespace 与 Sphinx 扩展加载机制
description: rst-to-myst 如何通过 Mock Sphinx 应用收集 docutils 和 Sphinx 的指令/角色注册表。
tags: [namespace, sphinx, mock, application, directive, role, domain]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T02:57:00Z" }
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
  - id: src-namespace
    resource: /references/source-namespace.md
    title: rst-to-myst 命名空间 Mock 系统
---

## 为什么需要 Mock Sphinx

Sphinx 扩展通过调用 `app.add_directive()`、`app.add_role()`、`app.add_domain()` 等方法向 Sphinx 应用注册指令和角色。要收集 Sphinx 及其扩展提供的所有指令和角色，通常需要初始化一个完整的 Sphinx 应用对象，这会带来大量的依赖加载和副作用。

rst-to-myst 的解决方案是创建一个 Mock 对象 `ApplicationNamespace`，它只实现了扩展注册所需的方法，其余方法通过 `__getattr__` 返回通用 Mock 对象，使得 Sphinx 扩展的 `setup(app)` 函数可以正常运行并注册指令/角色，而不需要完整的 Sphinx 环境。

## DomainMock 类

`DomainMock` 模拟 Sphinx 域对象：

```python
class DomainMock:
    def __init__(self, name, directives=None, roles=None):
        self.name = name
        self.directives = copy.copy(directives or {})
        self.roles = copy.copy(roles or {})
```

每个 Sphinx 域（如 `py`、`cpp`、`std`）包含自己的指令和角色字典。使用浅拷贝避免修改原始域定义。

## ApplicationNamespace 类

### 属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `extensions` | `dict[str, Extension]` | 已加载的扩展元数据 |
| `directives` | `dict[str, Directive]` | 全局指令字典 |
| `roles` | `dict[str, Any]` | 全局角色字典 |
| `domains` | `dict[str, DomainMock]` | 域字典 |
| `default_domain` | `Optional[str]` | 默认域名（默认 `"py"`） |
| `language_module` | `Optional[ModuleType]` | 语言翻译模块 |

### Sphinx API 方法

ApplicationNamespace 实现了 Sphinx 应用的核心注册方法：

| 方法 | 功能 |
|------|------|
| `add_directive(name, cls, override=False)` | 注册全局指令 |
| `add_role(name, role, override=False)` | 注册全局角色 |
| `add_domain(domain, override=False)` | 注册域（自动包装为 DomainMock） |
| `add_directive_to_domain(domain, name, cls, override=False)` | 向指定域注册指令 |
| `add_role_to_domain(domain, name, role, override=False)` | 向指定域注册角色 |

向不存在的域注册会抛出 KeyError。

### Mock 机制

未显式实现的属性访问通过 `__getattr__` 返回 `Mock()` 对象：

```python
def __getattr__(self, name):
    return Mock()
```

这使得 Sphinx 扩展在 setup 中调用的其他 Sphinx API（如 `add_config_value`、`add_node`、`connect` 等）不会抛出 AttributeError，而是静默返回 Mock 对象。这是一种"宽容 Mock"策略——只关注收集指令/角色，忽略不相关的 API 调用。

### 元素查找优先级

`get_element(attr, name)` 方法实现了多级别查找逻辑：

1. **名称规范化**：转为小写
2. **语言翻译**：如果 language_module 存在，尝试翻译名称
3. **指定域查找**：名称含冒号（`domain:name`）时，在对应域中查找
4. **默认域查找**：如果设置了 default_domain，在默认域中查找
5. **std 域查找**：在标准域 `std` 中查找
6. **全局查找**：在全局 directives/roles 字典中查找

这种查找顺序模拟了 Sphinx 的元素解析逻辑：默认域优先级高于全局，std 域是兜底。

### 查询方法

| 方法 | 返回值 |
|------|--------|
| `get_directive(name)` | 指令类或 None |
| `get_role(name)` | 角色函数或 None |
| `list_directives()` | 所有指令名列表（含 `domain:name` 格式） |
| `list_roles()` | 所有角色名列表（含 `domain:name` 格式） |
| `get_directive_data(name)` | 指令元数据字典 |
| `get_role_data(name)` | 角色元数据字典 |

`get_directive_data` 返回的元数据包含：name、description、class 路径、required_arguments、optional_arguments、has_content、options（选项名到类型名的映射）。

## compile_namespace 函数

`compile_namespace()` 是命名空间编译的入口函数，执行以下流程：

### 步骤 1：创建 ApplicationNamespace 实例

使用指定的 default_domain 和 language_code 创建。

### 步骤 2：加载 docutils 标准指令

从 `docutils.parsers.rst.directives._directive_registry` 动态导入标准指令模块和类：

```python
for key, (modulename, classname) in directives._directive_registry.items():
    if key not in app.directives:
        module = import_module(f"docutils.parsers.rst.directives.{modulename}")
        app.directives[key] = getattr(module, classname)
```

### 步骤 3：加载 docutils 标准角色

```python
app.roles.update(roles._role_registry)
app.roles.update(roles._roles)
```

### 步骤 4：（可选）加载 Sphinx 扩展

如果 `use_sphinx=True`：

1. **获取线程锁**：防止多线程并发修改 docutils 全局状态
2. **临时替换全局状态**：将 `directives._directives` 和 `roles._roles` 替换为 app 中的字典，使得 Sphinx 扩展在注册时写入 app 的字典
3. **加载扩展**：依次加载 Sphinx 内置扩展和用户指定扩展，调用每个扩展的 `setup(app)` 函数
4. **恢复全局状态**：在 finally 块中恢复原始的 docutils 全局字典，释放锁

线程锁的使用确保了即使在多线程环境中调用 `compile_namespace`，也不会并发修改 docutils 的全局指令/角色注册表。

### 扩展加载错误处理

- 扩展模块导入失败：抛出 ImportError
- 扩展没有 setup 函数：抛出 ExtensionError
- setup 返回值不是字典：使用空字典

## CLI 中的使用

CLI 的 `directives list/show` 和 `roles list/show` 子命令通过 `compile_namespace()` 获取命名空间，然后查询可用的指令和角色信息。

在转换过程中，`to_docutils_ast()` 也调用 `compile_namespace()` 创建命名空间（或使用传入的预编译 namespace），供 LosslessRSTParser 查找指令类。

## 相关概念

- [三阶段转换流水线架构](/concepts/03-conversion-pipeline.md)
- [LosslessRSTParser 与自定义 Transform](/concepts/04-lossless-parser.md)
- [Python API 使用指南](/concepts/02-python-api.md)
