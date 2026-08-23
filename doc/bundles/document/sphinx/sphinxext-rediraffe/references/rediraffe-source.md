---
type: Reference
title: sphinxext-rediraffe 源码信源登记
description: sphinxext-rediraffe 源码路径、版本、核心模块清单与公开 API 导出列表
tags: [sphinxext-rediraffe, source, reference, sphinx-extension]
generated: { by: "reference_agent/trae-glm", at: "2026-08-21T16:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T16:30:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: rediraffe-repo
    resource: https://github.com/sphinx-doc/sphinxext-rediraffe
    title: sphinxext-rediraffe GitHub Repository
---

# sphinxext-rediraffe 源码信源登记

## 源码位置

- **本地路径**：`external/libs/docs/sphinxext-rediraffe/`
- **上游仓库**：https://github.com/sphinx-doc/sphinxext-rediraffe
- **文档**：https://sphinxext-rediraffe.readthedocs.io/
- **PyPI**：https://pypi.org/project/sphinxext-rediraffe/
- **版本**：0.3.0（`__version__ = '0.3.0'`，`version_info = (0, 3, 0)`）

## 版本与依赖

| 项 | 值 |
|---|---|
| 包名 | `sphinxext-rediraffe` |
| 导入名 | `sphinxext.rediraffe` |
| 版本 | `0.3.0` |
| Python 要求 | `>=3.9` |
| 构建系统 | `flit_core>=3.12` |
| 许可证 | MIT |
| 作者 | Vasista Vovveti |

### 运行时依赖

| 包名 | 最低版本 | 用途 |
|------|---------|------|
| `Sphinx` | >=6.0 | 文档构建引擎（扩展宿主） |
| `jinja2` | （无显式下限） | 自定义重定向页面模板渲染 |

### 开发/测试依赖

| 包名 | 用途 |
|------|------|
| `pytest` | 单元测试框架 |
| `seleniumbase` | 浏览器端到端测试（验证重定向跳转） |
| `ruff` | 代码 lint |
| `furo` | 文档主题 |

## 核心模块清单

sphinxext-rediraffe 包结构极为精简，仅一个 Python 源文件：

```
sphinxext/
└── rediraffe.py     # 全部核心逻辑（485行）
```

### 模块详细 API 清单

#### 常量

| 符号 | 类型 | 值/说明 |
|------|------|---------|
| `__version__` | `str` | `'0.3.0'` |
| `version_info` | `tuple[int, int, int]` | `(0, 3, 0)` |
| `DEFAULT_REDIRAFFE_TEMPLATE` | `jinja2.Template` | 默认HTML重定向页面模板（含noscript降级+JS跳转+URL参数保留） |
| `REDIRECT_JSON_NAME` | `str` | `'_rediraffe_redirected.json'`，增量构建记录文件名 |
| `RE_OBJ` | `re.Pattern` | 重定向文件行解析正则：`(?:("|\')(.*?)\1|(\S+))\s+(?:("|\')(.*?)\4|(\S+))` |
| `READTHEDOCS_BUILDERS` | `list[str]` | `['readthedocs', 'readthedocsdirhtml']`，ReadTheDocs构建器名称 |

#### 公开函数

| 符号 | 签名 | 说明 |
|------|------|------|
| `create_graph` | `(path: Path) -> dict[str, str]` | 解析空白分隔的重定向边列表文件为dict映射；重复key或格式错误抛ExtensionError |
| `create_simple_redirects` | `(graph_edges: dict) -> dict` | 链式重定向压缩（DAG遍历至叶子节点）；检测循环重定向并抛ExtensionError |
| `build_redirects` | `(app: Sphinx, exception: Exception \| None) -> None` | Sphinx build-finished事件钩子；执行重定向HTML文件生成 |
| `setup` | `(app: Sphinx) -> ExtensionMetadata` | Sphinx扩展入口；注册配置值、Builder、事件钩子 |

#### 内部函数

| 符号 | 签名 | 说明 |
|------|------|------|
| `remove_suffix` | `(docname: str, suffixes: list[str]) -> str` | 移除已知源文件后缀（.rst/.md等） |

#### 公开类（Builder）

| 符号 | 基类 | builder name | 说明 |
|------|------|-------------|------|
| `CheckRedirectsDiffBuilder` | `sphinx.builders.Builder` | `'rediraffecheckdiff'` | Git diff检查器：检测删除/重命名文件是否有对应重定向 |
| `WriteRedirectsDiffBuilder` | `CheckRedirectsDiffBuilder` | `'rediraffewritediff'` | 自动重定向写入器：在checkdiff基础上自动将高相似度重命名追加到redirects文件 |

#### CheckRedirectsDiffBuilder 方法

| 方法 | 说明 |
|------|------|
| `init()` | 解析重定向配置，执行git diff检测删除/重命名文件，校验重定向覆盖 |
| `get_outdated_docs()` | 返回空列表（不触发文档重建） |
| `prepare_writing(docnames)` | 空实现（pass） |
| `write_doc(docname, doctree)` | 空实现（pass） |
| `get_target_uri(docname, typ)` | 返回空字符串 |
| `read()` | 返回空列表 |

#### WriteRedirectsDiffBuilder 方法

| 方法 | 说明 |
|------|------|
| `init()` | 先验证rediraffe_redirects为文件路径（str），再调用父类init()；对相似度≥阈值的重命名自动追加到redirects文件 |

#### setup() 注册内容

| 类型 | 名称 | 默认值 | 说明 |
|------|------|--------|------|
| 配置值 | `rediraffe_redirects` | `None` | 重定向配置（dict或文件路径字符串） |
| 配置值 | `rediraffe_branch` | `''` | Git diff基准分支/提交（diff检查器必需） |
| 配置值 | `rediraffe_template` | `None` | 自定义Jinja2模板文件路径 |
| 配置值 | `rediraffe_auto_redirect_perc` | `100` | 自动重定向相似度阈值（0-100） |
| Builder | `CheckRedirectsDiffBuilder` | — | 注册 `rediraffecheckdiff` 构建器 |
| Builder | `WriteRedirectsDiffBuilder` | — | 注册 `rediraffewritediff` 构建器 |
| 事件钩子 | `build-finished` → `build_redirects` | — | 构建完成后生成重定向HTML |

setup() 返回值：
```python
{
    'version': '0.3.0',
    'env_version': 1,
    'parallel_read_safe': True,
    'parallel_write_safe': True,
}
```

## 测试文件

| 文件 | 覆盖范围 |
|------|---------|
| `tests/test_create_graph.py` | create_graph解析：空格分隔、引号包裹、注释、重复key、复杂路径含引号 |
| `tests/test_create_simple_redirects.py` | create_simple_redirects：空图、单跳、链式压缩、循环检测、多链混合 |
| `tests/test_ext.py` | 端到端集成测试：html/dirhtml构建器下各种场景（简单、嵌套、链式、循环、不存在目标、已存在文件、Jinja模板、URL片段/查询参数保留） |
| `tests/test_builder.py` | Selenium浏览器测试：验证重定向页面实际跳转行为 |
| `tests/test_write_builder.py` | rediraffewritediff自动写入测试：重命名自动追加、相似度阈值过滤 |
| `tests/conftest.py` | pytest配置：Sphinx测试fixtures、git仓库初始化fixture、浏览器测试fixture |

### 测试根目录（tests/roots/ext/）

| 目录 | 测试场景 |
|------|---------|
| `test-simple` | 基础重定向 |
| `test-nested` | 嵌套目录重定向 |
| `test-complex` | 复杂链式重定向（多链汇聚） |
| `test-complex_dict` | dict配置方式的复杂链式重定向 |
| `test-cycle` | 循环重定向（应报错） |
| `test-no_cycle` | 无环但有重复目标 |
| `test-jinja` | 自定义Jinja模板 |
| `test-jinja_bad_path` | 模板路径不存在（回退默认） |
| `test-no_redirects` | 无重定向配置 |
| `test-no_rediraffe_file` | redirects文件不存在 |
| `test-bad_rediraffe_file` | 格式错误的redirects文件 |
| `test-backslashes` | Windows反斜杠路径 |
| `test-mixed_slashes` | 混合斜杠路径 |
| `test-dot_in_filename` | 文件名含点号 |
| `test-link_redirected_twice` | 同一源被重定向两次（应报错） |
| `test-link_redirected_to_nonexistant_file` | 重定向目标不存在 |
| `test-existing_link_redirected` | 源文件已存在（冲突警告） |
| `test-pass_url_fragments_queries` | URL片段(#hash)和查询(?query)参数保留 |
| `test-dirhtml_user_index_files` | dirhtml构建器下index文件处理 |
| `test-redirect_from_deleted_folder` | 从已删除目录重定向 |

## 公开 API 说明

sphinxext-rediraffe 的**主要使用方式是通过 Sphinx 配置和命令行**，而非 Python API 调用：

1. **Sphinx扩展方式**：在 `conf.py` 中添加 `'sphinxext.rediraffe'` 到 `extensions` 列表
2. **配置方式**：通过 `conf.py` 中的 `rediraffe_redirects` 等配置值控制行为
3. **CI检查方式**：通过 `sphinx-build -b rediraffecheckdiff` 或 `sphinx-build -b rediraffewritediff` 运行

`create_graph` 和 `create_simple_redirects` 虽然可以被 import，但属于内部实现函数，主要用于测试和调试。
