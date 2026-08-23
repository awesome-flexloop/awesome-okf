---
type: reference
title: scikit-build-core 源码信源
description: scikit-build-core 核心模块源码路径索引、版本信息与数据来源说明
tags:
  - scikit-build
  - build
  - source
  - reference
generated: true
verified: true
status: stable
sources:
  - https://github.com/scikit-build/scikit-build-core
  - "external/libs/tools/scikit-build/scikit-build-core/src/scikit_build_core/"
---

# scikit-build-core 源码信源

## 项目基本信息

| 项目 | 值 |
|------|-----|
| 包名 | `scikit_build_core` |
| 构建后端 | `hatchling.build`（自身使用 Hatch 构建） |
| 许可证 | Apache-2.0 |
| 作者 | Henry Schreiner |
| 支持 Python | 3.9 ~ 3.15 |
| 运行时依赖 | `packaging >=23.2`, `pathspec >=0.12.0` |
| 可选依赖(wheels) | `cmake`, `ninja` |

## 源码目录结构

源码根目录位于 `scikit-build-core/src/scikit_build_core/`，核心模块如下：

```
scikit_build_core/
├── __init__.py          # 包入口，定义 __version__
├── __main__.py          # CLI 入口（scikit-build/scikit-build-core 命令）
├── cmake.py             # CMake 类与 CMaker 类，CMake 集成核心
├── errors.py            # 异常类定义（CMakeConfigError 等）
├── program_search.py    # CMake/Ninja/Make 程序搜索与版本检测
├── format.py            # 输出格式化工具
├── _check_extra.py      # extra 依赖检查
├── _logging.py          # rich 日志工具
├── _reproducible.py     # 可重现构建工具
├── _shutil.py           # shutil 扩展工具
├── _variants.py         # 变体构建支持
├── _compat/             # Python 版本兼容层
│   ├── tomllib.py
│   ├── typing.py
│   └── importlib/
├── _vendor/             # Vendored pyproject_metadata
├── build/               # PEP 517 构建入口
│   ├── __init__.py      # build_wheel/build_sdist/build_editable
│   ├── _editable.py     # Editable 安装实现
│   ├── _fileapi.py      # CMake File API 集成
│   ├── _wheel.py        # Wheel 构建实现
│   ├── metadata.py      # 元数据处理
│   └── sdist.py         # SDist 构建实现
├── builder/             # 构建编排层
│   ├── builder.py       # Builder 类，CMake 参数与架构处理
│   ├── generator.py     # CMake 生成器选择
│   ├── get_requires.py  # 构建依赖计算
│   └── sysconfig.py     # Python sysconfig 查询
├── file_api/            # CMake File API 类型化模型
│   ├── model/           # CodeModel/Cache/Index 等 dataclass
│   ├── query.py         # File API stateless query
│   └── reply.py         # File API reply 解析
├── settings/            # 配置系统
│   ├── skbuild_model.py # ScikitBuildSettings 及子配置 dataclass
│   ├── sources.py       # EnvSource/ConfSource/TOMLSource/SourceChain
│   └── skbuild_read_settings.py  # SettingsReader 配置加载
├── metadata/            # 动态元数据插件
│   ├── __init__.py
│   ├── regex.py
│   ├── template.py
│   └── fancy_pypi_readme.py
├── hatch/               # Hatch 构建插件
├── init/                # scikit-build-core init 命令（项目模板生成）
├── setuptools/          # setuptools 兼容层
├── ast/                 # Python AST 分析（用于跨模块导出检测）
└── resources/           # 静态资源
    ├── _editable_redirect.py   # Editable redirect 模板
    ├── known_wheels.toml       # 已知 wheel 列表
    ├── scikit-build.schema.json  # JSON Schema
    ├── cmake/            # CMake FindPython 模块
    └── templates/        # 项目模板（c/cython/fortran/nanobind/pybind11/swig）
```

## CLI 入口点

| 命令 | 入口 |
|------|------|
| `scikit-build` | `scikit_build_core.__main__:main` |
| `scikit-build-core` | `scikit_build_core.__main__:main` |

## Entry Points 清单

| group | name | 目标 |
|-------|------|------|
| `build_backend` | — | `scikit_build_core.build` |
| `console_scripts` | `scikit-build` | `scikit_build_core.__main__:main` |
| `console_scripts` | `scikit-build-core` | `scikit_build_core.__main__:main` |
| `hatch` | `scikit-build` | `scikit_build_core.hatch.hooks` |
| `scikit-build-core.cmake` | `ninja` | `scikit_build_core.builder.get_requires:GetNinja` |
| `scikit-build-core.cmake` | `cmake` | `scikit_build_core.builder.get_requires:GetCMake` |
| `scikit-build-core.metadata` | `regex` | `scikit_build_core.metadata.regex:regex_metadata` |
| `scikit-build-core.metadata` | `template` | `scikit_build_core.metadata.template:template_metadata` |
| `scikit-build-core.metadata` | `setuptools_scm` | `scikit_build_core.metadata.setuptools_scm` |
| `scikit-build-core.metadata` | `fancy-pypi-readme` | `scikit_build_core.metadata.fancy_pypi_readme` |
| `validate_pyproject.tool_schema` | `scikit-build` | `scikit_build_core.settings.skbuild_schema:get_skbuild_schema` |
| `distutils.commands` | `build_cmake` | `scikit_build_core.setuptools.command:CMakeBuild` |
| `distutils.setup_keywords` | `cmake_args` 等 | setuptools 兼容参数 |

## 数据来源说明

本文档事实采集自 scikit-build-core 源码仓库 `d:\spaces\SpecWeave\external\libs\tools\scikit-build\scikit-build-core\`，对应 GitHub 仓库 `scikit-build/scikit-build-core`。所有模块路径、类名、方法签名、字段默认值均通过直接读取源码验证。
