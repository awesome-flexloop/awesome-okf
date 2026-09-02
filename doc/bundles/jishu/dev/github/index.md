---
okf_version: "0.2"
---
# GitHub 生态知识库

本知识包是简书连载《开源的世界》（nb/40234132）中 GitHub 平台相关文章的**中文教程束**，基于 2020 年前后教程整理，覆盖 Gist 代码片段分享与 GitHub Actions 工作流两大主题。所有内容均溯源至 2 篇简书原文（编号事实 F-201~F-212、F-225~F-229），遵循 [OKF v0.2 规范](https://github.com/awesome-flexloop/awesome-okf)。

## 内容概览（concepts/）

* [创建 Gist 与分享代码片段](concepts/00-gist.md) — 公开/机密 Gist 的区别与隐私边界、Gist 即 Git 仓库、创建步骤、嵌入文本字段与 GeoJSON 地图。
* [GitHub Actions 工作流](concepts/01-actions-workflow.md) — Actions 核心概念、`.github/workflows` 目录约定、触发事件 `on`、`runs-on`、构建矩阵、checkout 引用语法、`jobs`/`needs` 依赖与状态徽章。

## 信源登记簿（references/）

* [《3 创建 Gist》](references/source-1.md) — F-225 ~ F-229。
* [《5 GitHub Actions 手册》](references/source-2.md) — F-201 ~ F-212。

## 学习路径建议

1. **入门**：00-gist（轻量代码分享）→ 01-actions-workflow（自动化工作流）
2. **延伸**：配合 [git 束](../git/index.md) 的分支模型与 [opensource 束](../opensource/index.md) 的开源实践阅读

## 信任与生命周期说明

* **status 判定依据**：全部非 index/log 文档均 `status: stable`。内容基于简书连载《开源的世界》原文事实登记（facts.md）生成，不虚构原文没有的事实或资源。
* **stale_after 解释**：统一设置为 `2026-12-31`。Gist 机制与 Actions 心智模型长期稳定；但 Actions 的语法、运行器镜像与操作版本持续演进，文中已过时示例在「现状」小节说明并以官方文档为准。
* **核验链路**：`generated.at` 记录原始生成时刻（2026-09-02）；`verified.at` 记录过程核验事件（2026-09-02），事实编号与 `facts.md` 双份登记一致。
* **时点边界**：本束全部内容基于 2020 年前后教程，文中 Actions 示例（`ubuntu-18.04`、`actions/checkout@v1` 等）为当时版本，详见各文档「现状」小节。

```{toctree}
:hidden:
:maxdepth: 7

concepts/index
references/index
log
```
