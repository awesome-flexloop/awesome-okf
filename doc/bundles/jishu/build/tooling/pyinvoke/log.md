# Bundle Update Log

## 2026-09-02

**Merge**: 从 SpecWeave docs/knowledge/learning/04-docs-markup-tooling/pyinvoke-wiki/ 合并独有内容

* **Add**: concepts/12-tool-comparison-and-selection.md — 工具对比与选型：与 Make/Shell Script/Fabric/Nox/Tox/Poetry Scripts 的差异矩阵与各自结论、选型决策树、适用/不适用场景边界（源自 learning 侧 overview/comparison.md 与 overview/intro.md）
* **Update**: concepts/index.md、根 index.md 导航与 toctree（12→13 概念）
* **重复确认**：learning 侧 overview/intro（定位与设计哲学）与既有 00-introduction 重叠、overview/quickstart/installation 与 01-getting-started 重叠、overview/architecture 与 07/08 执行模型重叠、core-concepts/ 十篇（task/context/collection/config/parser/program/executor/runner/loader）与既有 02-08、11 概念文档逐一对应重叠，均未重复迁入

## 2026-08-21

* **Creation**: 建立 PyInvoke 知识包脚手架（concepts/examples/references 三目录）与信源登记（PyInvoke 源码路径与核心模块清单）。
* **Add**: R阶段完成——深度阅读 PyInvoke v3.0.3 源码 18 个核心模块（tasks.py, collection.py, context.py, config.py, executor.py, program.py, main.py, __main__.py, runners.py, loader.py, exceptions.py, parser/, watchers.py, terminals.py, util.py, env.py, completion/, vendor/），提取 70+ 源码事实（F-001 ~ F-073），覆盖类定义、方法签名、参数、数据流、配置层级、异常体系、Watcher机制、CLI入口点等。
* **Add**: I阶段完成——提炼 3 个核心架构洞察（I-01 Config隐形中枢/I-02 四层管道模型/I-03 Runner三线程IO模型），设计知识地图（入门5篇→配置执行4篇→高级3篇，共12概念+5示例）。
* **Add**: E阶段完成——concepts/ 下 12 个概念文档（00-introduction ~ 11-advanced-patterns），examples/ 下 5 个实战示例（basic-task/namespace-organization/custom-cli/file-watcher-automation/testing-tasks），references/ 下 1 个信源登记，加上 4 个 index.md 导航文件，共 23 个文件。
* **Add**: C阶段完成——萃取通用提示词模板与 R→I→E→V→C 五阶段 Workflow，沉淀为可复用模式。
* **Verify**: V阶段对抗审查完成——发现并修复 1 处虚构 API（`concepts/11-advanced-patterns.md` 中不存在的 `Response` 类，已替换为 MockContext 真实支持的正则字典键用法）；补充信源登记中的版本号（v3.0.3）、CLI入口点说明、遗漏模块（main.py/__main__.py/completion//vendor/）；修正信源登记的 sources 字段指向外部权威信源（GitHub + 官方文档）。
* **Fix**: 全 bundle 23 个文件最终验证通过——bundle 结构符合 OKF v0.2 规范、frontmatter 字段完整（type/title/description/tags/generated/verified/status/stale_after/sources）、81 条交叉链接全部有效、代码示例基于真实源码 API、事实声明可溯源。全部文档 `status: stable`，`stale_after: 2027-12-31`。
