# 参考与信源

本目录存放博文溯源材料与官方核验报告（E 阶段「信源先行」最先生成的两篇）：

- [article-source.md](article-source.md) — 原文事实清单（F-001~F-107 双份登记的 bundle 侧副本；含信源距离预判、图片缺口登记、七段事实表）
- [verification.md](verification.md) — P0 权威核验报告（18 项：14✅ / 4⚠️ / 0❌）+ 勘误四张清单（日期版本 / 成效溯源 / 口径对照 / 引文命令逐字）

**信源结构**：

| 层级 | 信源 | 用途 |
|------|------|------|
| 二手推介 | 微信公众号「虾说AI实验室 / 虾哥」《微信聊天记录只能烂在手机里？开源 WeChatBridge 一键转给 AI 和 Obsidian》（2026-09-24） | 被转化的原文，全部事实登记为 F-001~F-063 |
| 一手官方 | GitHub `freestylefly/WeChatBridge` 默认分支 README（抓取 2026-11-06） | P0 核验与口径订正，补充事实登记为 F-064~F-107 |
| 官方引用但未抓取 | `USAGE.zh-CN.md`、`PRODUCT_CAPABILITIES.zh-CN.md` | 仅登记引用关系（F-101），不作事实来源 |

> F 编号双份登记：spec 侧正本位于主仓库 `.trae/specs/okf-wiki-ecosystem/wechatbridge-okf-wiki/facts.md`，
> 与本目录 `article-source.md` 正文机械同步，编号集合相等且连续无跳号（校验记录见 [../log.md](../log.md)）。

```{toctree}
:maxdepth: 1
:caption: 参考文档

article-source
verification
```
