# 实战示例

本目录包含 5 个完整的可运行示例，每个示例对应一个或多个核心概念，提供从简单到复杂的渐进式学习路径。

* [基础使用：在自己项目中引入 Invocations](basic-usage.md) — 从零开始配置 tasks.py，包含测试、格式化、文档构建、打包发布的完整项目模板。对应概念：[快速上手](../concepts/01-getting-started.md)、[组合模式](../concepts/10-composition-patterns.md)。
* [自定义发布流程](custom-release-flow.md) — 基于 packaging.release 添加前置检查、Docker 构建、发布后通知的自定义发布工作流。对应概念：[包发布生命周期](../concepts/05-packaging-release.md)、[组合模式](../concepts/10-composition-patterns.md)。
* [多站点文档构建配置](multi-site-docs.md) — 配置 docs 模块管理多个 Sphinx 站点（API + WWW），含双站构建和 watch_docs 监控。对应概念：[Sphinx 文档管理](../concepts/04-docs-sphinx.md)、[文件监控](../concepts/07-utilities-watchers.md)。
* [文件监控自动测试](file-watch-auto-test.md) — 使用 watch 模块实现代码变化时自动运行测试/覆盖率，打造 TDD 反馈循环，含多任务监控模式。对应概念：[工具函数与文件监控](../concepts/07-utilities-watchers.md)、[测试与覆盖率](../concepts/03-testing-pytest.md)。
* [打包安装验证模式](test-install-verification.md) — 使用 release.test_install 在临时 venv 中验证包安装、导入、类型检查，自定义增强验证流程。对应概念：[包发布生命周期](../concepts/05-packaging-release.md)、[工具函数](../concepts/07-utilities-watchers.md)。

```{toctree}
:hidden:

basic-usage
custom-release-flow
file-watch-auto-test
multi-site-docs
test-install-verification
```
