# 信源清单

## 信源列表

| 编号 | 类型 | 来源 | URL | 可信度 | 用于核实 |
|------|------|------|-----|--------|----------|
| R1 | 主信源 | 微信公众号"AI产品阿颖" | https://mp.weixin.qq.com/s/ho00Y5QXxGLqqYkFoocNOw | 中（个人公众号，观点为主） | F-001~F-039 |
| R2 | 官方 | Anthropic — Introducing Claude Tag | https://www.anthropic.com/news/introducing-claude-tag | 高 | F-007~F-009 |
| R3 | 官方 | Slack Help — Use Claude in Slack | https://slack.com/intl/en-au/help/articles/53532192117267 | 高 | F-007~F-008 |
| R4 | 媒体 | Ars Technica — Cat Wu专访 | https://arstechnica.com/ai/2026/05/claude-codes-product-lead-talks-usage-limits-transparency-and-the-lean-harness/ | 高 | F-010~F-012 |
| R5 | 媒体 | Lenny's Podcast（YouTube） | https://www.youtube.com/watch?v=PplmzlgE0kg | 高 | F-011~F-012 |
| R6 | 媒体 | 36氪/爱范儿 — 豆包工作实测 | https://36kr.com/p/3954390879222917 | 高 | F-003~F-004 |
| R7 | 媒体 | 网易新闻/赛博禅心 — 豆包工作 | https://c.m.163.com/news/a/L56HHQUU0556C3J2.html | 中高 | F-003 |
| R8 | 官方 | OpenClaw 文档 — Agent Channels | https://learnopenclaw.org/agentchannels.html | 中 | F-039 |
| R9 | 开源 | Open Claude Tag对比表 | https://github.com/Anil-matcha/open-claude-tag/blob/main/README.md | 中 | F-039 |
| R10 | 媒体 | 腾讯云 — AI研发效率数据 | https://developer.cloud.tencent.com/article/2677538 | 高 | F-013~F-014 |

## F 编号索引

| 编号 | 简述 | 信源 | 核验 |
|------|------|------|------|
| F-001 | 元信息 | R1 | — |
| F-002 | 豆包工作发布 | R6/R7 | ✅ |
| F-003 | 三个入口 | R6/R7 | ✅ |
| F-004 | 30天免费 | R6 | ✅ |
| F-005 | 飞书原生Agent | R6/R7 | ✅ |
| F-006 | 移动端语音 | R1 | ✅ |
| F-007 | Claude Tag发布 | R2 | ✅ |
| F-008 | Claude Tag功能 | R2/R3 | ✅ |
| F-009 | 两者逻辑一致 | R1 | 📝 |
| F-010 | Cat Wu身份 | R4/R5 | ✅ |
| F-011 | Cat Wu引语 | R4/R5 | ⚠️ |
| F-012 | 数据源偏差 | R5 | ⚠️ |
| F-013 | 10倍/30%数据 | — | ❌ |
| F-014 | 实际数据 | R10 | 补充 |
| F-015~F-020 | 使用案例 | R1 | 📝 |
| F-021~F-035 | 核心论点 | R1 | 📝 |
| F-036~F-038 | 作者背景 | R1 | 📝 |
| F-039 | OpenClaw | R8/R9 | ⚠️ |

## 可信度说明

- **客观事实**：20条（产品事实、Claude Tag、Cat Wu身份等，已通过权威来源核验）
- **作者观点（📝）**：19条（核心论点、使用体验、趋势判断，标注为博文作者观点）
- **核验补充**：1条（F-014实际行业数据，用于勘误F-013）
- **❌ 失败**：1项（F-013效率数据归因失实）
- **⚠️ 部分通过**：2项（F-011引语细节偏差、F-039 OpenClaw定位说明）

```{toctree}
:hidden:

article-source
verification
```
