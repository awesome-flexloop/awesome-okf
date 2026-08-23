# 参考文档

从 Jupyter Server Extension CookieCutter 模板源码提取的精确参考资料。

## 配置与参数

- [cookiecutter.json 参数全参考](cookiecutter-json.md) — 所有交互参数定义、默认值和 Jinja2 渲染规则

## 核心源码解析

- [ExtensionApp 类源码解析](extension-app-source.md) — Extension 类的继承、handlers 注册、traitlets 配置、settings 传递
- [PingHandler 请求处理器源码解析](handler-source.md) — ExtensionHandlerMixin、APIHandler、认证装饰器、请求响应流程
- [pyproject.toml 模板字段全解析](pyproject-source.md) — 构建系统、项目元数据、依赖声明、工具配置（hatch/pytest/mypy/black/ruff）
- [测试源码解析](test-source.md) — pytest-jupyter 基础设施、conftest.py 配置、jp_fetch fixture、异步 API 测试模式

## 钩子与 CI

- [post_gen_project.py 生成后钩子解析](post-gen-hook-source.md) — 条件文件删除机制、递归删除工具函数
- [CI/CD 工作流源码解析](ci-workflow-source.md) — 两套 CI 体系、矩阵构建、Jupyter Releaser、lint.sh 脚本
