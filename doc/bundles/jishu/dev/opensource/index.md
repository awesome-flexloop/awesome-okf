---
okf_version: "0.2"
---
# 开源项目实践知识库

本知识包是简书连载《开源的世界》（nb/40234132）中开源实践相关文章的**中文教程束**，基于 2020 年前后教程整理，覆盖为开源做贡献、开启开源项目、README 模板、无版权图库与程序员常用网站五大主题。所有内容均溯源至 5 篇简书原文（编号事实 F-220~F-224、F-230~F-237、F-248~F-255、F-260~F-265），遵循 [OKF v0.2 规范](https://github.com/awesome-flexloop/awesome-okf)。

## 内容概览（concepts/）

* [开源参与指南](concepts/00-participation-guide.md) — 为开源做贡献的原因、非编码贡献形态（文档/测试/翻译/答疑等）、分析开源项目、找项目资源、贡献前检查表与有效沟通。
* [开启一个开源项目](concepts/01-start-a-project.md) — 开源含义与原因、免费≠开源、项目必备文档、许可证选择、README 五问、贡献指南、行为规范、命名品牌与 pre-launch 清单。
* [项目的 README 模板要素](concepts/02-readme-template.md) — 翻译自 @PurpleBooth 的 README 模板：项目标题/获得开始/运行测试/部署/内置/投稿/版本/作者/许可证/致谢。
* [无版权图库使用指引](concepts/03-no-copyright-images.md) — 原文仅列出 3 篇参考资料，未直接列出图库名称；如实转述信源边界。
* [程序员常用网站](concepts/04-programmer-websites.md) — W3Schools 等六个重点网站及资讯、在线学习、社区工具、竞赛四类网站盘点（2020 年前后资源盘点，非操作教程）。

## 信源登记簿（references/）

* [《1.1 开源项目指南》（部分抓取）](references/source-1.md) — F-260 ~ F-265。
* [《1.2 开启一个开源项目》](references/source-2.md) — F-248 ~ F-255。
* [《项目的自述文档（README）模板》](references/source-3.md) — F-220 ~ F-222。
* [《4 无版权图库》](references/source-4.md) — F-223 ~ F-224。
* [《程序员需要了解的网站》](references/source-5.md) — F-230 ~ F-237。

## 学习路径建议

1. **入门**：00-participation-guide（贡献视角）→ 01-start-a-project（发起视角）
2. **写作**：02-readme-template（README 模板，可直接套用）
3. **资源**：03-no-copyright-images（图库信源边界）→ 04-programmer-websites（网站盘点）
4. **延伸**：配合 [git 束](../git/index.md) 的分支模型与 [github 束](../github/index.md) 的 Gist/Actions 阅读

## 信任与生命周期说明

* **status 判定依据**：全部非 index/log 文档均 `status: stable`。内容基于简书连载《开源的世界》原文事实登记（facts.md）生成，不虚构原文没有的事实或资源。
* **stale_after 解释**：统一设置为 `2026-12-31`。开源协作方法论与 README 模板结构长期有效；具体平台行为（GitHub 探索、各网站现状）随时间变化，文中已过时内容在「现状」小节说明并以当前官方文档为准。
* **核验链路**：`generated.at` 记录原始生成时刻（2026-09-02）；`verified.at` 记录过程核验事件（2026-09-02），事实编号与 `facts.md` 双份登记一致。
* **时点边界**：本束全部内容基于 2020 年前后教程，《1.1 开源项目指南》为部分抓取（正文在「没有人响应你」章节处截断），部分资源链接与平台行为可能已变化，详见各文档「现状」小节。

```{toctree}
:hidden:
:maxdepth: 7

concepts/index
references/index
log
```
