# 可复用模式（Patterns）

从 extension-template 源码中提炼的可复用设计模式，可应用于其他项目脚手架和扩展开发。

## 模式列表

| 模式 | 问题 | 解决方案 | 适用场景 |
|------|------|---------|---------|
| [条件渲染模板模式](conditional-rendering.md) | 多种配置变体需要独立维护模板 | Jinja2 条件块在单一模板中生成变体代码 | 项目脚手架、代码生成器 |
| [双包分发模式](dual-package-distribution.md) | 前端+后端混合技术栈安装复杂 | 将编译前端打包进 Python wheel，pip install 一键安装 | Jupyter 扩展、含 UI 的 Python 库 |
| [认证 API Handler 模式](authenticated-api-handler.md) | Web API 端点可能缺少认证导致安全漏洞 | 所有 HTTP 方法加 `@tornado.web.authenticated`，CI 自动检查 | Jupyter Server 扩展、Tornado 应用 |

## 模式使用建议

1. **条件渲染模式**适用于任何基于模板的代码生成场景，不仅限于 Copier
2. **双包分发模式**是 Jupyter 生态的标准实践，但也适用于其他需要"pip install 就能用"的 Web UI 库
3. **认证 Handler 模式**是安全红线，任何在 Jupyter Server 中注册路由的扩展必须遵循

```{toctree}
:hidden:
:maxdepth: 7

authenticated-api-handler
conditional-rendering
dual-package-distribution
```
