# 信源与核验（References）

信源先行：本目录先于 `concepts/` 生成，是全束 F 编号与勘误口径的唯一依据。分两轮——首轮两篇（微信博文 + GitHub API + README 快照），源码轮两篇（固定 commit `fb6a42c` 的本地源码）。

| 文档 | 内容 |
|------|------|
| [博文事实清单（F-001~F-057）](article-source.md) | 博文 40 条 + 2026-11-06 官方核验补充 17 条；与 spec `facts.md` 双份登记、编号集合一致 |
| [P0 权威核验报告](verification.md) | 22 项 P0/P1 核验（14✅/8⚠️/0❌）、勘误四张清单、核验方法与局限、复核安排 |
| [源码事实清单（F-058~F-101）](source-code-map.md) | 🔬 源码轮 44 条代码级事实：信源基线、仓库规模、模块分层、只读契约、双 CLI 口径、四视图规格、计数断言 |
| [源码级核验报告与首轮对账](source-code-verification.md) | 🔬 源码轮：G0 信源稳定性（固定 commit、tag 落后 13 提交）、首轮 8 项 ⚠️ 逐项对抗性对账、漂移分类 D1~D5、计数双口径复核、本轮局限 |

```{toctree}
:maxdepth: 1
:caption: 信源参考

article-source
verification
source-code-map
source-code-verification
```
