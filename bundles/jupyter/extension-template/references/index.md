# 参考文档（References）

从源码中提取的信源文档，提供配置参数、模板字段和代码结构的精确参考。

## 参考列表

| 文档 | 内容 |
|------|------|
| [Copier 配置参数全参考](copier-config.md) | copier.yml 中所有参数的类型、默认值、条件和验证规则 |
| [package.json 模板字段解析](package-json-source.md) | package.json.jinja 的条件依赖、构建脚本、JupyterLab 扩展元数据 |
| [pyproject.toml 模板字段解析](pyproject-source.md) | pyproject.toml.jinja 的构建配置、hatchling、jupyter-builder 集成 |
| [前端入口模板解析](frontend-entry-source.md) | src/index.ts.jinja 四种扩展类型的插件定义差异 |
| [Python 服务端模板解析](server-routes-source.md) | routes.py.jinja 的 APIHandler 模式、路由注册、认证装饰器 |
| [CI/CD 工作流源码解析](ci-workflows-source.md) | GitHub Actions 工作流的 job 结构、测试步骤、发布流程 |

## 源码信源

所有参考文档基于以下源文件分析生成：

```
external/libs/jupyter/extension-template/
├── copier.yml                          # Copier 参数配置
└── template/
    ├── package.json.jinja              # NPM 包配置模板
    ├── pyproject.toml.jinja            # Python 包配置模板
    ├── src/index.ts.jinja              # 前端入口模板
    ├── src/request.ts.jinja            # API 请求封装（frontend-and-server）
    ├── {{python_name}}/__init__.py.jinja    # Python 包入口
    ├── {{python_name}}/routes.py.jinja      # 路由处理器（frontend-and-server）
    ├── schema/plugin.json.jinja        # 设置 Schema（has_settings）
    ├── style/variables.css             # CSS 变量（theme）
    └── .github/workflows/              # CI/CD 工作流
```
