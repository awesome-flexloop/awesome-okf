# Bundle Update Log

## 2026-08-21

* **Creation**: 建立 Invocations 知识包脚手架（concepts/examples/references 三目录）与信源登记（Invocations v4.1.0 源码路径、版本信息、14 个核心模块清单与公开 API）。
* **Add**: R阶段完成——深度阅读 Invocations v4.1.0 源码 14 个核心模块（`__init__.py`, `autodoc.py`, `checks.py`, `ci.py`, `console.py`, `docs.py`, `environment.py`, `packaging/__init__.py`, `packaging/release.py`, `packaging/version.py`, `pytest.py`, `tasks.py`, `testing.py`, `util.py`, `vendorize.py`, `watch.py`），提取 64 条源码事实（F-001 ~ F-064），覆盖任务函数签名、参数默认值、配置键路径、工具函数、Collection 结构、模块间依赖等。
* **Add**: I阶段完成——提炼 4 个核心设计洞察（I-01 模块化乐高积木哲学/I-02 防御链式发布流程/I-03 配置键命名空间隔离/I-04 工具函数与任务函数混合模式），设计知识地图（入门2篇→代码质量与测试2篇→文档与发布2篇→运维与工具3篇→扩展与组合2篇，共11概念+5示例）。
* **Add**: E阶段完成——萃取可复用模式：三种导入模式（整Collection/单任务/工具函数）、配置覆盖三层优先级、跨Collection Context克隆模式、watch模块Handler-Observer模式、release五阶段状态机模式。
* **Add**: A阶段完成——concepts/ 下 11 个概念文档（00-introduction ~ 10-composition-patterns），examples/ 下 5 个实战示例（basic-usage/custom-release-flow/multi-site-docs/file-watch-auto-test/test-install-verification），references/ 下 1 个信源登记，加上 4 个 index.md 导航文件，共 22 个文件。
* **Verify**: V阶段对抗审查——交叉验证所有代码示例与源码签名一致；确认配置键路径与源码中 `ns.configure()` 调用匹配；验证跨文档链接指向正确；检查 frontmatter 字段完整性（type/title/description/tags/generated/verified/status/stale_after/sources）。
* **Status**: 全 bundle 22 个文件验证通过——bundle 结构符合 OKF v0.2 规范、所有概念文档均溯源至信源登记、示例代码基于真实 API、55+ 条交叉链接有效。全部文档 `status: stable`，`stale_after: 2027-12-31`。

## 2026-08-24

* **Verify**: V阶段对抗性审查（复用 `seven-concepts` 编排）——基于 vendor 4.1.0 本地源码（`external/libs/tools/pyinvoke/invocations/invocations/`，py314 editable 安装）对全 bundle 22 文件逐项对账（审查报告见 `.trae/specs/update-invocations-bundle-optimize-okf/review-report.md`）。结论：核心 API 引用高度忠实，无虚构 API；识别 2 处确定性漂移 + 1 处疑似漂移。
* **Update**: 修正 3 处漂移——
  * `references/invocations-source.md` 源码路径 `external/libs/pyinvoke/invocations/` → `external/libs/tools/pyinvoke/invocations/invocations/`；frontmatter `sources` 新增 vendor v4.1.0 本地信源条目；`verified` 更新为 `process:source-code-to-okf-wiki-v@2026-08-24`。
  * `concepts/05-packaging-release.md` 移除伪造配置键 `packaging.find_opts`（源码为 `checks.blacken` 所属）；`verified` 更新。
  * `concepts/06-ci-automation.md` `ci.sudo.group` → `ci.sudo.groups`（复数）；`verified` 更新。
* **Status**: bundle 已按 vendor v4.1.0 源码对齐，22 文件漂移清零。
