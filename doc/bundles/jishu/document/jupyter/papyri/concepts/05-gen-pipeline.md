---
type: Concept
title: gen 管线与 IR 生成
description: papyri gen 命令的核心管线流程——从模块遍历、docstring 解析到 IR 输出的完整过程
tags: [papyri, gen, pipeline, docstring, doctest]
generated: { by: reference_agent/trae-soLO, at: "2026-08-22T00:00:00Z" }
verified: { by: "process:grep-api-check", at: "2026-08-22T00:00:00Z" }
status: stable
stale_after: 2027-02-22
sources:
  - id: papyri-src
    resource: /references/papyri-source.md
    title: Papyri Python 核心包源码信源
  - id: cli-src
    resource: /references/cli-source.md
    title: Papyri CLI 命令源码信源
---

## gen 管线概览

`papyri gen` 是 Papyri 的核心功能。它从 TOML 配置文件出发，遍历目标 Python 库的 API，解析 docstring，执行示例代码，最终输出一个结构化的 DocBundle 目录。

管线入口为 `gen.py` 中的 `gen_main()` 函数，由 CLI 命令 `cli/gen.py` 调用。

## 管线阶段

### 阶段 1：配置加载与环境准备

1. **加载 TOML 配置**：通过 `config_loader.load_configuration()` 读取 TOML 文件，构建 `Config` 对象
2. **创建临时工作目录**：使用 `IPython.utils.tempdir.TemporaryWorkingDirectory` 切换到临时目录（避免副作用）
3. **导入目标模块**：使用 `importlib.import_module` 导入配置中指定的 `module` 和 `submodules`
4. **初始化组件**：
   - `ErrorCollector`：收集生成过程中的错误
   - `BlockExecutor`：执行 doctest 代码块
   - 进度条（rich progress）

### 阶段 2：API 遍历

使用 Python 的 `inspect` 模块遍历目标模块的公开 API：

- **模块（module）**：遍历模块的公开成员
- **类（class）**：遍历类的方法、属性、嵌套类
- **函数/方法（function/method）**：提取签名和 docstring
- **排除项**：配置中的 `exclude` 列表指定的限定名跳过

遍历过程中使用 `FullQual` 和 `Canonical` 工具类（utils.py）处理完全限定名和规范名解析。

### 阶段 3：Docstring 解析

对每个 API 对象的 docstring 执行以下步骤：

1. **提取签名**：通过 `signature.py` 中的 `Signature` 类解析 Python 函数签名，生成 `SignatureNode`
2. **NumPy 风格解析**：使用 `numpydoc_compat.NumpyDocString` 解析 docstring 为各节（Parameters/Returns/Examples 等）
3. **RST 解析**：对每个节的文本内容，通过 `ts.parse()`（tree-sitter RST 解析器）和 `tree.GenVisitor` 转换为 IR 节点树
4. **See Also 规范化**：`_normalize_see_also()` 将 See Also 条目转换为 `SeeAlsoItem` 列表，每个包含 `CrossRef`（初始为 "to-resolve" 状态）

### 阶段 4：示例执行（可选）

当 `--exec` 启用或配置中 `execute_doctests = true` 时：

1. 使用 `doctest.DocTestParser` 解析 Examples 节中的代码示例
2. 通过 `BlockExecutor` 在隔离的命名空间中执行代码
3. 捕获 stdout/stderr 输出和 matplotlib 图形
4. 将执行结果记录到 `Code` 节点的 `execution_status` 和 `out` 字段
5. 注册第三方 doctest 选项标志（FLOAT_CMP/REMOTE_DATA 等）为 no-op 以避免解析错误

### 阶段 5：类型推断（可选）

当 `--infer`（默认启用）时：

- 对 Examples 节中的代码进行类型推断
- 将 token 与引用关联为 `(token, reference)` 对
- 渲染器可以据此将 `np.array` 等标识超链接到对应的文档页面

### 阶段 6：交叉引用解析（尽力而为）

在 gen 阶段，跨引用进行尽力而为的本地解析：

- 本地引用（同模块内）解析为 `LocalRef`
- 外部引用初始标记为 `RefInfo(kind="to-resolve")`——ingest 阶段的 relink pass 会进一步解析
- "See Also" 中的引用也初始为 "to-resolve" 状态

### 阶段 7：组装 GeneratedDoc

将所有解析结果组装为 `GeneratedDoc` 对象：

```python
doc = GeneratedDoc.new()
# 设置 _content 字典（按标准节顺序）
# 设置 signature, see_also, aliases, item_file, item_line, item_type
# 设置 example_section_data, references, arbitrary, local_refs
```

`_OrderedDictProxy` 确保节的顺序在序列化/反序列化后保持不变。

### 阶段 8：写入磁盘

将每个 GeneratedDoc 写入 DocBundle 目录：

1. **papyri.json**：Bundle 清单（元数据）
2. **module/<qa>.json**：每个 API 对象的 `GeneratedDoc.to_json()` 输出
3. **docs/<name>**：叙述性文档
4. **examples/<name>**：示例 Section
5. **assets/**：二进制资源原样复制
6. **toc.json**：目录树（TocTree 列表）

写入前调用 `node.validate()` 进行类型校验。未处理的 `Directive` 节点在此阶段被拦截（`_reject_at_validate = True`）。

## 错误处理

### ErrorCollector

`ErrorCollector` 累积生成过程中的错误，支持：

- 按错误类型分类
- `--fail`：遇到第一个错误即中断
- `--fail-early`：覆盖提前错误选项
- `--fail-unseen-error`：只在遇到新类型错误时失败

### ExecutionStatus 枚举

```python
class ExecutionStatus(Enum):
    success = "success"
    failure = "failure"
    unexpected_exception = "unexpected_exception"
    none = "none"
    compiled = "compiled"
    syntax_error = "syntax_error"
```

## 特殊处理

### Doctest 选项标志兼容

pytest-doctestplus 和多个科学计算包（astropy、scipy 等）注册了自定义 doctest 选项标志。gen 在解析 Examples 节之前，将已知的第三方标志注册为 no-op：

```python
for _doctest_optname in ("FLOAT_CMP", "REMOTE_DATA", "IGNORE_OUTPUT",
                         "IGNORE_WARNINGS", "IGNORE_EXCEPTION"):
    doctest.register_optionflag(_doctest_optname)
```

### matplotlib 图形内联

执行示例时，matplotlib 图形被捕获并保存为 assets，通过 `Figure` 节点引用。

### 隐含导入

`_get_implied_imports()` 函数推断示例代码可能需要的导入（如模块自身的命名空间、类名等），注入到执行命名空间中。

## gen 命令选项

完整选项参见 [CLI 参考](13-cli-reference.md)，常用组合：

```bash
# 快速测试（无类型推断、无执行）
papyri gen examples/papyri.toml --no-infer

# 只生成单个对象
papyri gen examples/numpy.toml --only numpy:einsum

# 生成后立即打包
papyri gen examples/papyri.toml --pack

# 生成后立即上传到本地 viewer
papyri gen examples/papyri.toml --upload

# 严格模式（任何错误都失败）
papyri gen examples/papyri.toml --fail --fail-unseen-error
```

## 相关概念

- [IR 与 DocBundle](03-ir-and-docbundle.md)
- [IR 节点类型体系](04-ir-node-types.md)
- [限定名与交叉引用](06-qualified-names.md)
- [RST 解析](10-rst-parsing.md)
- [配置系统](07-config-system.md)
