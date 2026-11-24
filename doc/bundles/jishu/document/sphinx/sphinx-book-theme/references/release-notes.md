---
type: Reference
title: "版本、兼容性与升级注记"
description: "sphinx-book-theme 的发布节奏、版本时间线、依赖兼容矩阵、已知废弃项与升级检查清单"
tags: [sphinx, theme, reference, changelog, version, compatibility]
generated: { by: "reference_agent/lobsterai-cn", at: "2026-11-24T03:02:35Z" }
verified: { by: "process:seven-concepts-v", at: "2026-11-24T03:02:35Z" }
status: stable
stale_after: 2027-11-24
sources:
  - id: sbt-changelog
    resource: https://github.com/executablebooks/sphinx-book-theme/blob/main/CHANGELOG.md
    title: sphinx-book-theme CHANGELOG
  - id: sbt-pyproject
    resource: external/libs/docs/sphinx-contrib/sphinx-book-theme/pyproject.toml
    title: pyproject.toml
---

# 版本、兼容性与升级注记

## 当前快照

| 项目 | 值 | 来源 |
|------|-----|------|
| 源码版本 | `1.5.0.dev` | `src/sphinx_book_theme/__init__.py` |
| 最近正式版 | `1.4.0`（2026-07-19） | `CHANGELOG.md` |
| 父主题 | `pydata-sphinx-theme==0.23.0` | `pyproject.toml` |
| Sphinx | `>=8.2` | `pyproject.toml` |
| Python | `>=3.11` | `pyproject.toml` |
| 构建后端 | `sphinx-theme-builder >= 0.2.0a7` | `pyproject.toml` |
| Node | `20.9.0` | `pyproject.toml` 的 `[tool.sphinx-theme-builder]` |
| 许可证 | BSD-3-Clause | `LICENSE` / classifiers |

> 注意：CHANGELOG 的 `v1.4.0` 条目写的是升级到 pydata 0.20，而当前开发分支已把依赖推到 `0.23.0`。这说明 `1.5.0.dev` 尚未发布，版本注记以 `pyproject.toml` 为准。

## 版本时间线

| 版本 | 日期 | 关键变化 |
|------|------|---------|
| `1.5.0.dev` | 未发布 | 依赖推进到 `pydata-sphinx-theme==0.23.0`、`sphinx>=8.2`；源码版本号领先 CHANGELOG |
| `1.4.0` | 2026-07-19 | 升级 pydata-sphinx-theme 0.20、Sphinx >=8.2 |
| `1.3.0` | 2026-07-19 | 默认分支改为 `main`；新增匈牙利语翻译；升级 pydata 0.17；CI 支持手动触发 |
| `1.2.0` | 2026-03-09 | JupyterLite 按钮修复；GitLab 源码文本显示；支持 Sphinx 9 / Python 3.14；最低 Sphinx 7、Python 3.11 |
| `1.1.2` | 2024-02-13 | 版本号修正；事件处理签名修正 |
| `1.1.1` | 2024-02-13 | 用 `config-inited` 事件注册配置，修复配置被覆盖 |
| `1.1.0` | 2023-12-19 | 搜索框回到侧栏；CSS 对象处理修复；Windows 构建修复；Sphinx 7 支持 |

更早版本见仓库 `CHANGELOG.md`。

## 兼容矩阵

| 主题版本 | Sphinx | Python | 父主题 |
|---------|--------|--------|--------|
| `1.5.0.dev` | `>=8.2` | `>=3.11` | `==0.23.0` |
| `1.4.0` | `>=8.2` | `>=3.11` | `0.20.x` |
| `1.2.0`–`1.3.0` | `>=7` | `>=3.11` | `0.17.x` / 更早 |
| `1.1.x` | `>=7` | `>=3.9` | 较早 |

实际安装时以 `pip` 解析结果为准；若项目同时锁定父主题，可能出现冲突。

## 已知废弃项

| 项 | 状态 | 替代 |
|----|------|------|
| `single_page` 主题选项 | 0.3.4 起废弃，加载时 warning | 无；移除配置 |
| `expand_toc_sections` | 保留但标为 DEPRECATE | 用 `show_navbar_depth` / `max_navbar_depth` |
| `extra_footer` | 文档站 `conf.py` 注释为 `DEPRECATED KEY`，`theme.conf` 仍保留 | 优先 `footer_content_items` + 自定义模板 |
| `html_sourcelink_suffix` 默认 `.txt` | 主题改为默认空字符串 | 需要 `.txt` 时显式配置 |

废弃项的 warning 类型为 `sphinxbooktheme`，便于过滤。

## 升级检查清单

### 1. 依赖

```bash
pip install -U sphinx-book-theme
python -c "import sphinx_book_theme; print(sphinx_book_theme.__version__)"
python -c "import pydata_sphinx_theme; print(pydata_sphinx_theme.__version__)"
```

确认 Sphinx、父主题、Python 三者都满足新版本要求。

### 2. 配置

- 检查 `html_theme_options` 是否有已废弃键。
- 布尔值是否仍是布尔（不是字符串 `"False"`）。
- `html_sidebars` 引用的模板是否仍存在。
- `footer_content_items` 引用的模板是否仍存在。
- `launch_buttons` 的键是否仍被支持。

### 3. 模板覆盖

如果你覆盖了 `sections/header.html`、`components/page-toc.html` 等模板：

- 对比新版本原模板，确认 block 名称与变量未变；
- 检查新增/删除的 class 是否影响你的 CSS；
- 检查 `header_buttons` 的数据结构是否变化。

### 4. 样式

- 自定义 CSS 是否依赖 `bd-*`、`pst-*` 深层结构；
- CSS 变量名是否仍存在；
- 打印样式是否仍可读；
- 移动端布局是否回归。

### 5. 测试

```bash
pytest
```

若失败：

1. 先看 diff，确认是预期变化；
2. 只对确认的文件 `--force-regen`；
3. 再跑全量测试；
4. 在 CHANGELOG 或项目升级记录中注明行为变化。

### 6. 构建产物

- `stb compile` 是否成功；
- `static/styles`、`static/scripts`、`static/locales` 是否生成；
- 页面是否 404 主题 CSS/JS；
- 下载按钮的 `.ipynb` 是否仍生成。

## 维护模式的影响

README 明确项目处于维护模式：

- 缺陷修复仍可能合入，但不保证时间；
- 新功能开发"不太可能"；
- 若你依赖新特性，考虑：
  - 在上游 issue 中提出并附 PR；
  - 做子主题/Fork，承担跟进成本；
  - 迁移到活跃维护的同类主题（需评估迁移成本）。

## 版本锁定建议

| 场景 | 建议 |
|------|------|
| 生产文档站 | `sphinx-book-theme==1.4.0` + 锁定父主题 |
| 跟随修复 | `sphinx-book-theme~=1.4` |
| 参与开发 | 源码安装 + `stb compile` + `pytest` |
| 子主题 | 在 `pyproject.toml` 写 `sphinx-book-theme>=1.4,<2` |

## 相关概念

- [主题选项速查](theme-options-reference.md)
- [源码路径映射](source-map.md)
- [定制、子主题与主题开发](../concepts/08-customization-and-development.md)
