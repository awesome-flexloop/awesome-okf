# 信源参考索引

本目录包含 litegitpuller 各核心模块的源码信源登记文档，所有概念文档和示例文档的 `sources` 字段均指向此处。

## 信源文档列表

| 文档 | 源码文件 | 说明 |
|------|---------|------|
| [插件入口源码](index-ts-source.md) | `src/index.ts` | 扩展激活逻辑、URL参数解析、nbgitpuller冲突检测、Provider选择 |
| [Git拉取核心源码](gitpuller-ts-source.md) | `src/gitpuller.ts` | GitPuller抽象基类、GithubPuller/GitlabPuller实现、模板方法模式 |
| [Python包源码](python-package-source.md) | `litegitpuller/__init__.py`, `install.json` | Python包入口、labextension路径注册、安装配置 |
| [构建配置源码](build-config-source.md) | `pyproject.toml`, `package.json` | hatchling构建配置、npm依赖、打包规则、构建脚本 |

## 源码版本信息

- **npm包名**: `@jupyterlite/litegitpuller`
- **版本**: 0.3.0
- **Python包名**: `litegitpuller`
- **Python要求**: >=3.8
- **JupyterLab要求**: >=4.0.0
- **许可证**: BSD-3-Clause
- **仓库**: https://github.com/jupyterlite/litegitpuller
