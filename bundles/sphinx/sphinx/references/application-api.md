---
type: "reference"
title: Sphinx 应用类 API 参考
description: Sphinx主类的完整API参考，包括初始化参数、属性、扩展注册方法和构建方法。
tags: [sphinx, api, application, core]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T15:30:00+08:00" }
verified: { by: "process:grep-verification", at: "2026-08-22T15:30:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: application-py
    resource: /references/application-api.md
    title: sphinx/application.py 源码
---
# Sphinx 应用类 API 参考

`Sphinx`类是Sphinx文档生成器的主入口，定义在`sphinx/application.py`。

## 类签名

```python
class Sphinx:
    def __init__(
        self,
        srcdir: str | os.PathLike[str],
        confdir: str | os.PathLike[str] | None,
        outdir: str | os.PathLike[str],
        doctreedir: str | os.PathLike[str],
        buildername: str,
        confoverrides: dict[str, Any] | None = None,
        status: IO[str] | None = sys.stdout,
        warning: IO[str] | None = sys.stderr,
        freshenv: bool = False,
        warningiserror: bool = False,
        tags: Sequence[str] = (),
        verbosity: int = 0,
        parallel: int = 0,
        keep_going: bool = False,
        pdb: bool = False,
        exception_on_warning: bool = False,
    ) -> None: ...
```

## 核心属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `srcdir` | `_StrPath` | 源文件目录 |
| `confdir` | `_StrPath` | conf.py配置目录（默认同srcdir） |
| `outdir` | `_StrPath` | 输出目录 |
| `doctreedir` | `_StrPath` | pickled doctrees缓存目录 |
| `config` | `Config` | 配置对象 |
| `env` | `BuildEnvironment` | 构建环境 |
| `builder` | `Builder` | 当前构建器实例 |
| `events` | `EventManager` | 事件管理器 |
| `registry` | `SphinxComponentRegistry` | 组件注册表 |
| `extensions` | `dict[str, Extension]` | 已加载扩展字典 |
| `project` | `Project` | 项目对象 |
| `tags` | `Tags` | 标签集合 |
| `parallel` | `int` | 并行任务数 |
| `verbosity` | `int` | 日志详细级别 |
| `statuscode` | `int` | 构建状态码（0=成功） |
| `phase` | `BuildPhase` | 当前构建阶段 |

## 扩展注册方法

| 方法 | 说明 |
|------|------|
| `setup_extension(extname: str)` | 导入并设置扩展模块（幂等） |
| `require_sphinx(version: tuple[int,int] | str)` | 检查Sphinx版本要求 |
| `connect(event, callback, priority=500) -> int` | 连接事件回调，返回listener_id |
| `add_builder(builder, override=False)` | 注册构建器 |
| `add_config_value(name, default, rebuild, types=(), description='')` | 注册配置值 |
| `add_event(name)` | 注册自定义事件 |
| `set_translator(name, translator_class, override=False)` | 注册/覆盖Translator |
| `add_node(node, override=False, **kwargs)` | 注册Docutils节点及各builder的visit/depart处理器 |
| `add_enumerable_node(node, figtype, title_getter=None, override=False, **kwargs)` | 注册可编号节点 |
| `add_directive(name, cls, override=False)` | 注册指令 |
| `add_role(name, role, override=False)` | 注册角色 |
| `add_domain(domain, override=False)` | 注册领域 |
| `add_directive_to_domain(domain, name, cls, override=False)` | 向领域添加指令 |
| `add_role_to_domain(domain, name, role, override=False)` | 向领域添加角色 |
| `add_crossref_type(directivename, rolename, indextemplate='', objtype=None, override=False)` | 注册交叉引用类型 |
| `add_transform(transform)` | 添加文档转换器 |
| `add_post_transform(transform)` | 添加后转换器 |
| `add_js_file(filename, priority=500, **kwargs)` | 注册JS文件 |
| `add_css_file(filename, priority=500, **kwargs)` | 注册CSS文件 |
| `add_lexer(alias, lexer)` | 注册Pygments词法分析器 |
| `add_autodocumenter(cls, override=False)` | 注册autodoc文档生成器 |
| `add_source_suffix(suffix, filetype)` | 注册源文件后缀 |
| `add_source_parser(parser, override=False)` | 注册源解析器 |

## 构建方法

| 方法 | 说明 |
|------|------|
| `build(force_all=False, filenames=())` | 执行构建。force_all=True全量构建，filenames指定构建特定文件 |
| `create_builder(name) -> Builder` | 通过registry创建构建器实例 |

## 构建流程简述

1. `__init__`中完成初始化→加载扩展→创建环境→创建构建器
2. `build()`根据参数调用builder的build_all/build_specific/build_update
3. 构建完成emit('build-finished', exception)，调用builder.cleanup()
