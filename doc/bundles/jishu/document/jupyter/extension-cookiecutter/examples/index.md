# 示例文档

可运行的代码示例，从基础到进阶，每个示例包含完整代码和逐行解析。

## 基础示例

- [01 基础 Ping 扩展示例](01-basic-ping-extension.md) — 逐行解析模板生成的 Ping 扩展全部代码（__init__.py、extension.py、handlers.py、配置、测试），理解模板最小可运行示例

## 进阶示例

- [02 添加自定义 API 端点](02-custom-endpoint.md) — 添加 CRUD REST API 端点（GET/POST/PUT/DELETE）、路径参数、请求体验证、错误处理、状态码规范
- [03 添加可配置参数](03-configurable-extension.md) — 使用 traitlets 添加多种类型配置（Unicode/Integer/Bool/List/Dict/Float）、参数验证器、settings 传递、测试配置覆盖

```{toctree}
:hidden:
:maxdepth: 7

01-basic-ping-extension
02-custom-endpoint
03-configurable-extension
```
