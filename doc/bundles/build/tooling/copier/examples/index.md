# 示例文档

本目录包含 4 个可直接运行的 Copier 使用示例，从基础到高级覆盖常见场景。

## 示例列表

* [基础模板创建与使用](basic-template.md) — 从零创建 Python 项目模板，配置 copier.yml、编写 Jinja2 模板文件、使用 `copier copy` 生成项目。入门必读。
* [条件渲染与动态文件](conditional-rendering.md) — 使用 `when` 条件问题、Jinja2 控制流、动态默认值、yield 标签从一个模板生成多个文件。
* [任务与自动化钩子](tasks-and-hooks.md) — `_tasks` 任务执行（shell/argv 两种格式、条件任务、工作目录）、`_migrations` 版本迁移脚本、前后消息配置。
* [项目更新工作流](update-workflow.md) — `copier update` 智能更新、冲突解决（inline/rej 模式）、迁移脚本编写、recopy 对比、CI/CD 更新最佳实践。
* [Python API 使用](python-api-usage.md) — `run_copy()`/`run_update()`/`run_recopy()` 便捷函数、Worker 类精细控制、错误处理、自定义 CLI 工具构建、批量生成项目。

```{toctree}
:hidden:

basic-template
conditional-rendering
python-api-usage
tasks-and-hooks
update-workflow
```
