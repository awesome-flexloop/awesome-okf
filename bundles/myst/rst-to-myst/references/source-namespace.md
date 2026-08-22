---
type: Reference
title: rst-to-myst 命名空间 Mock 系统
description: namespace.py 实现 ApplicationNamespace Mock Sphinx 应用以收集指令和角色。
tags: [source-code, namespace, sphinx, mock, directive, role]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T02:55:00Z" }
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
  - id: src-namespace
    resource: /spec/facts.md
    title: rst-to-myst 事实清单
---

## 模块概览

`rst_to_myst/namespace.py` 实现 Sphinx 应用的 Mock 对象，用于在不运行完整 Sphinx 构建的情况下收集所有注册的指令和角色（263行）。

## 核心类

### `DomainMock`

模拟 Sphinx 域对象：
- `name: str` - 域名称
- `directives: dict` - 域内指令字典（浅拷贝）
- `roles: dict` - 域内角色字典（浅拷贝）

### `ApplicationNamespace`

模拟 `sphinx.application.Sphinx` 对象：

#### 属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `extensions` | `dict[str, Extension]` | 已加载扩展 |
| `directives` | `dict[str, Directive]` | 全局指令字典 |
| `roles` | `dict[str, Any]` | 全局角色字典 |
| `domains` | `dict[str, DomainMock]` | 域字典 |
| `default_domain` | `Optional[str]` | 默认域名称（默认"py"） |
| `language_module` | `Optional[ModuleType]` | 语言模块（用于翻译） |

#### Sphinx API 方法

| 方法 | 功能 |
|------|------|
| `add_directive(name, cls, override=False)` | 注册全局指令 |
| `add_role(name, role, override=False)` | 注册全局角色 |
| `add_domain(domain, override=False)` | 注册域（包装为 DomainMock） |
| `add_directive_to_domain(domain, name, cls, override=False)` | 向指定域注册指令 |
| `add_role_to_domain(domain, name, role, override=False)` | 向指定域注册角色 |

#### 元素查找方法

`get_element(attr, name)` 实现多级查找：
1. 名称规范化（转小写）
2. 语言模块翻译（如存在）
3. 含冒号时按 `domain:name` 查找指定域
4. 在默认域中查找
5. 在 `std` 域中查找
6. 在全局字典中查找

`get_directive(name)` 和 `get_role(name)` 是 `get_element` 的便捷封装。

#### 查询方法

- `list_directives() -> list[str]` - 列出所有指令名（含 `domain:name` 格式）
- `list_roles() -> list[str]` - 列出所有角色名
- `get_directive_data(name) -> dict` - 返回指令元数据（名称/描述/类/参数数量/选项等）
- `get_role_data(name) -> dict` - 返回角色元数据

#### Mock 机制

`__getattr__` 方法对未实现的属性返回 `Mock()` 对象，使得 Sphinx 扩展 setup 函数中调用的其他 Sphinx API 不会报错。

## 核心函数

### `compile_namespace(extensions, use_sphinx, default_domain, language_code) -> ApplicationNamespace`

编译完整的指令/角色命名空间：

1. 创建 ApplicationNamespace 实例
2. 从 `docutils.parsers.rst.directives._directive_registry` 加载 docutils 标准指令
3. 加载 docutils 标准角色（`_role_registry` 和 `_roles`）
4. 若 `use_sphinx=False`，直接返回
5. 若 `use_sphinx=True`：
   - 获取线程锁 `LOCK`
   - 临时替换全局 `directives._directives` 和 `roles._roles`
   - 加载 Sphinx 内置扩展和用户指定扩展
   - 调用每个扩展的 `setup(app)` 函数注册指令/角色
   - 恢复全局状态并释放锁

线程锁的作用是防止多线程环境下 docutils 全局状态被并发修改。

## 源码位置

- 文件路径：`rst_to_myst/namespace.py`
- 代码行数：263行

## 相关概念

- [ApplicationNamespace 与 Sphinx 扩展加载机制](/concepts/08-namespace-mocking.md)
