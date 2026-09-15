# 信源登记簿（References）

本目录是星辰300 端侧 AI 知识包的信源登记，所有 concepts 文档中引用的事实均可追溯到此处的原始信源与核验记录。

## 信源清单

| 信源ID | 文档 | 原始来源 | 覆盖事实范围 |
|--------|------|---------|-------------|
| blog-wechat | [article-source.md](article-source.md) | 微信公众号"硅基之声"博文（2026-09-14，安谋科技通稿二手改写，厂商自宣） | F-001 ~ F-015（博文全部事实与厂商叙事） |
| Arm 官方 + 厂商通稿链核验 | [verification.md](verification.md) | arm.com/newsroom.arm.com、安谋科技官网、EET-China、界面新闻、WAIC 现场报道、arXiv、GitHub | 12 项核验结论 + F-016 ~ F-029 核验补充与勘误 |

## 事实编号索引

| 编号段 | 主题 | 分类 | 登记位置 |
|-------|------|------|---------|
| F-001 ~ F-002 | 博文元信息、信源性质（厂商自宣/通稿改写） | 元信息 | [article-source.md](article-source.md) |
| F-003 ~ F-007 | 平台构成、四大用例、32MHz MPS3、U55 定位 | 博文事实（平台与硬件） | [article-source.md](article-source.md) |
| F-008 ~ F-010 | Helium 性能叙事（含 5×/15× 嫁接错误）、NPU 分工、能力宣称 | 博文/厂商口径 | [article-source.md](article-source.md) |
| F-011 ~ F-014 | 四大用例：YOLO-Fastest / wav2letter+Conformer / kws-micronet / ESR | 博文事实（含 2 处待勘误名称/表述） | [article-source.md](article-source.md) |
| F-015 | "算力功耗平衡艺术/本地觉醒"营销叙事 | 厂商叙事 | [article-source.md](article-source.md) |
| F-016 ~ F-018 | 安谋科技公司身份、STAR-MC2 合作开发与品牌名关系、发布时间错配 | 核验补充（口径补正/勘误） | [article-source.md](article-source.md) |
| F-019 | Helium 5×/15× 主体为 Cortex-M55、M52 仅 5.6×/2.7× | 核验补充（**重点勘误**） | [article-source.md](article-source.md) |
| F-020 ~ F-022 | Ethos-U55 规格、Transformer 不原生支持、MPS3/32MHz 与 Corstone 先例 | 核验补充（勘误/口径补正） | [article-source.md](article-source.md) |
| F-023 ~ F-024 | 五模型档案核验、ESR→SESR 名称勘误 | 核验补充 | [article-source.md](article-source.md) |
| F-025 ~ F-029 | Synaptics 商用旁证、英文语料边界、20-30× 外推、自述经营数据、WAIC 时间线 | 核验补充（边界/勘误） | [article-source.md](article-source.md) |

## 信源可信度说明

- **信源距离 = 厂商自宣**：博文非独立报道，是安谋科技官方通稿经"硅基之声""白话IC"等自媒体渠道投放的二手改写（界面新闻同稿标注"商讯"）；多平台同稿分发不构成独立多源（F-002）。
- **硬件骨架可靠、营销口径需校正**：平台、器件型号、板卡、时钟频率均能被 Arm 官方资料证实；5 项 ⚠️ 集中在成效数字嫁接（F-019）、能力表达夸大（F-021）、模型名漏字（F-024）、时间框架松动（F-018、F-029）。
- **无第三方实测**：四用例无数值化性能/精度/功耗数据，应用领域为厂商目标场景宣称；500MHz/1GHz 下"20-30 倍"为厂商线性外推（F-027）。

```{toctree}
:hidden:
:maxdepth: 7

article-source
verification
```
