# 信源清单

## 信源列表

| 编号 | 类型 | 来源 | URL | 可信度 | 用于核实 |
|------|------|------|-----|--------|----------|
| R1 | 主信源 | 36氪/陈曦 | https://mp.weixin.qq.com/s/yib0hxacgpIvxD4yoD17-A | 高（专业媒体） | F-001~F-040 |
| R2 | 官方 | OpenAI — Agents SDK演进 | https://openai.com/index/the-next-evolution-of-the-agents-sdk/ | 高 | F-005 |
| R3 | 官方 | LangChain — Agents文档 | https://docs.langchain.com/oss/python/langchain/agents | 高 | F-006 |
| R4 | 官方 | LangChain博客 — Agent Harness解析 | https://langchain-blog.ghost.io/the-anatomy-of-an-agent-harness/ | 高 | F-006 |
| R5 | 官方 | Deloitte — State of AI in the Enterprise 2026 | https://www.deloitte.com/content/dam/assets-zone2/nl/en/docs/services/consulting/2026/PoV_State-of-AI-2026_Deloitte.pdf | 高 | F-009 |
| R6 | 官方 | BCG — AI at Work 2026 | https://www.bcg.com/publications/2026/ai-at-work-why-strategy-matters-more-than-tools | 高 | F-027 |
| R7 | 官方 | BCG幻灯片PDF | https://web-assets.bcg.com/e7/c7/00d913744cccb1e4f65bbf54fe86/ai-at-work-slideshow-june-2026.pdf | 高 | F-027~F-028 |
| R8 | 官方 | 飞书帮助中心 — 在飞书中使用豆包工作 | https://www.feishu.cn/hc/zh-CN/articles/282796994123 | 高 | F-015~F-016, F-032 |
| R9 | 媒体 | 网易科技 — 千问办公首个通过信通院评估 | https://www.163.com/tech/article/L3L5TMN100098IEO.html | 中高 | F-034~F-035 |
| R10 | 媒体 | 华为云 — 云上Agent基准度量模型首批 | https://huaweicloud.csdn.net/6a745b95662f9a54cb9918a0.html | 中高 | F-035 |

## F 编号索引

| 编号范围 | 类别 | 信源 | 核验 |
|----------|------|------|------|
| F-001 | 元信息 | R1 | — |
| F-002~F-008 | Agent上半场 | R1,R2,R3,R4 | 2✅/4📝 |
| F-009~F-014 | Context瓶颈 | R1,R5 | 1✅/4📝/1✅ |
| F-015~F-022 | 飞书集成 | R1,R8 | 3✅/4📝/1✅ |
| F-023~F-026 | 组织闭环 | R1 | 1✅/3📝 |
| F-027~F-031 | ROI | R1,R6,R7 | 2✅/3📝 |
| F-032~F-037 | 权限安全 | R1,R8,R9,R10 | 2✅/1⚠️/2📝/1补充 |
| F-038~F-040 | 下半场竞争 | R1 | 3📝 |

## 可信度说明

- **客观事实**：17条（产品事实、OpenAI/LangChain/Deloitte/BCG官方数据、飞书官方文档）
- **作者观点（📝）**：20条（分析框架、趋势判断、金句）
- **核验补充**：3条（Deloitte中间档30%、BCG样本量11749人、信通院认证时间线）
- **✅ P0通过**：5项
- **⚠️ P0部分通过**：1项（信通院双项认证）
- **❌ P0失败**：0项

```{toctree}
:hidden:

article-source
verification
```
