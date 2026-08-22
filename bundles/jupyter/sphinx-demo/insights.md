---
type: Insights
okf_version: "0.2"
title: "sphinx-demo 架构洞察"
generated: "2026-08-22"
tags: [jupyter, sphinx, jupyterlite, demo, documentation]
sources:
  - facts.md
  - ../../../../../external/libs/jupyter/sphinx-demo/pyodide-kernel-example/docs/source/conf.py
  - ../../../../../external/libs/jupyter/sphinx-demo/index.html
  - ../../../../../external/libs/jupyter/sphinx-demo/.github/workflows/pages.yml
---
# sphinx-demo 架构洞察

## I-001：jupyterlite-sphinx 的"构建期耦合 + 分层配置"集成模型

**类型**：架构模式

**关联事实**：F-020, F-021, F-022, F-023, F-024, F-025, F-026, F-027, F-030, F-032

**洞察**：sphinx-demo 示范了 jupyterlite-sphinx 如何把 JupyterLite 的构建与 Sphinx 的文档构建在**构建期**耦合，而不是运行时耦合——JupyterLite 部署产物最终落在 Sphinx 构建输出的 `lite/` 子目录（F-007）。

耦合通过 conf.py 中的一组 `jupyterlite_*` 配置项完成（F-020~F-027），每个配置项对应一个明确的控制维度：
- **内容范围**：`jupyterlite_contents = ["custom_contents/*"]` 用 glob 声明哪些源文件进入内嵌 JupyterLite 站点（F-022）；
- **构建噪声**：`jupyterlite_silence` 控制构建日志详细度（F-023）；
- **输出裁剪**：`strip_tagged_cells` 让带 `jupyterlite_sphinx_strip` 标签的单元格从文档 HTML 中剥离、但仍保留在 JupyterLite 部署中（F-024）——这是"文档视图"与"可执行视图"内容分离的关键机制；
- **交互注入**：`global_enable_try_examples`（F-025）、`try_examples_global_button_text`（F-026）、`try_examples_global_warning_text`（F-027）三件套控制 docstring Examples 段自动转交互按钮的行为。

在上述构建期配置之外，项目把 JupyterLite 自身的配置拆成**四层 JSON**（F-032~F-036），构成"构建期（conf.py + jupyter_lite_config.json）→ 运行时（jupyter-lite.json）→ 插件（overrides.json）→ 交互（try_examples.json）"的完整分层，每层只改自己关心的面。

```
        Sphinx 文档构建（conf.py）
  jupyterlite_contents / strip_tagged_cells / try_examples_*   (F-020~F-027)
        │ 构建期钩子：jupyterlite-sphinx 在 make html 中启动 JupyterLite build
        ▼
   Sphinx build/html ──► lite/ 子目录（内嵌 JupyterLite 部署, F-007）
         │
         └─ 四层 JSON 配置
            jupyter_lite_config.json（构建时, F-032）
            jupyter-lite.json      （运行时, F-033/034）
            overrides.json         （插件/工具栏, F-035）
            try_examples.json      （交互/热更新, F-036）
```

**复用价值**：给文档站加交互示例时，优先采用"conf.py 声明内容 glob + strip_tagged_cells 做双视图分离 + 四层 JSON 分面配置"的模板；`try_examples.json` 支持按页面正则 ignore（F-036），适合控制哪些示例不进入交互。

## I-002：双内核双站点的"对称复制"架构与最小差异面

**类型**：设计决策

**关联事实**：F-004, F-005, F-006, F-015, F-016, F-017, F-018, F-019, F-030, F-031, F-033, F-034, F-039

**洞察**：项目没有为"Pyodide vs Xeus"设计抽象层，而是用两个**近乎对称的目录**（`pyodide-kernel-example/` 与 `xeus-kernel-example/`）分别承载两种内核的完整配置（F-004/F-005），以此作为对比教学。

两个示例的 conf.py 逐行一致（F-020~F-029 共用一个描述），差异被刻意收敛到最小、可枚举的 5 处：
1. **kernel 依赖包**：requirements.txt 分别用 `jupyterlite-pyodide-kernel==0.5.2`（固定版本，F-018）与 `jupyterlite-xeus`（F-019）；
2. **WASM 环境文件**：仅 xeus 需要 `environment.yml`（F-016），其 channels 依赖 emscripten-forge（F-038）、deps 含 pandas/matplotlib/xeus-python（F-039）；
3. **运行时默认内核**：`defaultKernelName` 为 `"python"` vs `"XPython"`（F-033/F-034）；
4. **版本切换器匹配**：`version_match` 为 `"pyodide"` vs `"xeus"`（F-030）；
5. **编辑链接路径**：`html_context.doc_path` 指向各自示例目录（F-031）。

这个"对称复制"策略把两种内核的差异暴露为**显式 diff**，读者可直接对比任意两个文件。CI 侧用 GitHub Actions 的 matrix 并行构建这两个站点，最终把 `/pyodide/` 与 `/xeus/` 两个独立站点聚合部署。

```
   GitHub Actions matrix: [[pyodide-kernel-example, pyodide],
                            [xeus-kernel-example, xeus]]
        │ uv install requirements.txt → make html（每站点独立构建）
        ▼
   pyodide/ 站点            xeus/ 站点
   conf.py × 相同           conf.py × 相同
   jupyter-lite.json        jupyter-lite.json
     defaultKernel=python     defaultKernel=XPython   (F-033/034)
   requirements: pyodide==0.5.2   requirements: jupyterlite-xeus (F-018/019)
   （无 environment.yml）    environment.yml (emscripten-forge) (F-016/037/038/039)
```

**复用价值**：对比型演示项目可优先选"对称复制 + 显式差异清单"而非过早抽象；差异点应集中在依赖文件、运行时默认值、切换器标识等可枚举字段上，便于文档化与自动化校验。

## I-003：落地页 + 版本切换器驱动的双站点聚合导航

**类型**：架构约束

**关联事实**：F-009, F-010, F-011, F-012, F-013, F-014, F-030, F-031

**洞察**：由于双内核被部署为两个独立站点（`/pyodide/` 与 `/xeus/`），项目在根目录放了两类"聚合导航"资产：静态落地页 `index.html` 与版本切换器数据 `switcher.json`。

- **index.html** 是纯静态 HTML 落地页（F-009~F-013）：用一张内核表格把两个站点的 JupyterLite badge 链接并列（F-011/F-012/F-013），favicon 复用 pyodide 站点的资源（F-010），零 JS 依赖即可作为仓库主页；
- **switcher.json**（F-014）是 PyData Sphinx Theme 版本切换器（navbar 的 `version-switcher`）的数据源，conf.py 通过 `switcher.json_url` 指向它（F-030）；两站点的 `version_match` 分别设为 `"pyodide"`/`"xeus"`（F-030），使浏览器在站内导航栏下拉即可跳转到另一内核站点。

部署时由 pages.yml 将这两个根级文件 `mv` 进聚合目录（`mv index.html dist/index.html`、`mv switcher.json dist/switcher.json`），形成"双站点 + 根导航"的扁平结构，与 F-011 的表格入口和 F-014 的切换器构成三重互通的导航闭环。

```
                GitHub Pages 根（gh-pages）
   ┌────────────────────────┬────────────────────────┐
 index.html (F-011/012/013) │ switcher.json (F-014)
   ▼ 表格 badge 链接          ▼ version-switcher 数据
 /pyodide/ 站点  ◄────────►  /xeus/ 站点
   version_match="pyodide"     version_match="xeus"   (F-030)
   navbar 下拉跳转另一站点（conf.py switcher.json_url, F-030）
```

**复用价值**：多独立站点的聚合部署可参考"根落地页 + switcher 数据 + 站点内下拉跳转"的三层导航；落地页保持无 JS 静态化，switcher 数据与各站点 conf.py 的 `version_match` 约定一致的标识符，避免导航脱节。
