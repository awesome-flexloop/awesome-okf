# 信源登记簿（References）

本目录收录 mobilepa-bench 知识包的事实台账与信源登记，是全部 concepts 文档的事实依据层。

## 信源清单

| 编号 | 信源 | 类型 | 覆盖事实 |
|------|------|------|---------|
| R1 | [事实台账](facts.md) | 两份 R 阶段事实清单的适配合并 | A 部分：MobilePA-Bench F-001 ~ F-032（沿用原编号）；B 部分：Qwen-UI-Agent 网站仓 WEB-A-01 ~ WEB-A-24（改编号，每条标注 facts-websites.md 原编号） |
| R2 | [信源登记](source-registry.md) | 仓库内文件与外部 URL 逐项登记 | 两个信源根的文件清单、相对路径、覆盖事实范围与未覆盖项 |

## 事实编号索引说明

| 编号段 | 含义 | 信源根 |
|--------|------|--------|
| F-001 ~ F-032 | MobilePA-Bench 仓库与站点事实（编号沿用 facts-mobilepa-bench.md） | `external/libs/tools/Tongyi-MAI/MobilePA-Bench` |
| WEB-A-01 ~ WEB-A-24 | Qwen-UI-Agent 网站仓事实（改用 WEB-A 前缀避免与 A 部分冲突，每条标注 facts-websites.md A 部分原编号） | `external/libs/tools/Tongyi-MAI/Qwen-UI-Agent` |

## 性质声明

本束登记的两个仓库**均为网站/论文资产，非实现代码仓**：

- MobilePA-Bench：仅含 README/LICENSE/静态项目页/CI 配置，基准本体在 arXiv:2608.23035（F-001）；
- Qwen-UI-Agent：README 原文 "Website source only — this is not the Qwen-UI-Agent implementation repository."，实现代码指向 Tongyi-MAI/MAI-UI（WEB-A-01、WEB-A-02）。

依据此性质，本束不设 examples/ 目录（理由记录于本束根目录 `log.md`）。

```{toctree}
:hidden:
:maxdepth: 7

facts
source-registry
```
