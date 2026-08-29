# 生成日志：豆包工作组织生产力

## 元信息

| 字段 | 值 |
|------|-----|
| 博文标题 | 下一代生产力，就在豆包工作+飞书里 |
| 博文作者 | 36氪/陈曦 |
| 博文日期 | 2026-08-25 21:42 |
| 博文URL | https://mp.weixin.qq.com/s/yib0hxacgpIvxD4yoD17-A |
| Bundle路径 | ai/ai-agent/doubao-work-org-productivity/ |
| 内容性质 | 专业媒体战略分析（引用第三方研究数据） |
| 骨架类型 | 商业分析/战略资讯（index + concepts + references + log，无examples） |
| 事实数量 | 40条（F-001~F-040） |
| 作者观点 | 20条（📝标注） |
| 第三方数据 | Deloitte（3235人/24国）+ BCG（11749人/14市场） |
| P0核验 | 5✅ 1⚠️ 0❌（本系列通过率最高） |
| status | verified |
| stale_after | 2026-11-30 |
| 生成日期 | 2026-08-28 |

## R→I→E→V 链路

| 阶段 | 动作 | 结果 |
|------|------|------|
| **R（采集）** | browser_use提取博文全文+元信息 | 全文获取，标题/作者/日期确认 |
| **R（核验）** | general_purpose_task P0核验6项 | 5✅ 1⚠️ 0❌ |
| **I（洞察）** | 四层拆分：能力商品化→Context瓶颈→飞书集成→组织ROI+安全 | 4篇concepts |
| **E（生成）** | 10文件bundle写入 + 索引更新 | 10文件全部写入 |
| **V（验证）** | UTF-8 + toctree + 相对链接 + 无file:/// | 全部通过 |

## 文件清单（10文件）

| # | 文件 | 内容 |
|---|------|------|
| 1 | index.md | 根索引，核心论点表，三bundle关系对比，已知边界 |
| 2 | concepts/index.md | 4篇概念学习路径+mermaid+toctree |
| 3 | concepts/00-agent-half-time.md | Harness商品化、OpenAI SDK、LangChain公式、上下半场对比 |
| 4 | concepts/01-context-bottleneck.md | Deloitte 34%/37%、人替Agent准备工作、企业非线性工作流 |
| 5 | concepts/02-feishu-integration-loop.md | 账号级集成、飞书AI原生OS、理解→执行→协作→沉淀闭环 |
| 6 | concepts/03-org-productivity-security.md | BCG 42%/8h、任务间隐性成本、权限继承、信通院认证⚠️ |
| 7 | references/index.md | 10信源+F编号索引+可信度说明+toctree |
| 8 | references/article-source.md | F-001~F-040完整事实登记8类表+统计 |
| 9 | references/verification.md | 6项P0核验报告+10个权威来源 |
| 10 | log.md | 本文件 |

## G1-G4 质量门

| 质量门 | 检查项 | 结果 |
|--------|--------|------|
| G1 信源 | 主信源URL可达，10个权威来源（含OpenAI/LangChain/Deloitte/BCG/飞书官方） | ✅ |
| G2 事实 | 40条事实全部编号，20条作者观点📝标注，3条核验补充 | ✅ |
| G3 核验 | 6项P0核验，5✅1⚠️0❌，⚠️项已如实标注 | ✅ |
| G4 结构 | 10文件完整，toctree三级，UTF-8，无file:/// | ✅ |

## 勘误/注意事项

| # | 类型 | 说明 |
|---|------|------|
| N1 | ⚠️ 待佐证 | 信通院双项认证"首批通过"仅有企业自述，缺信通院官方名单 |
| N2 | 细微差异 | Deloitte数据34%和37%之间有30%中间档，博文将"核心流程"并入34% |
| N3 | 时间说明 | Deloitte调查执行于2025年8-9月、2026年1月发布，博文称"2026年调查"指发布年 |

## 与同组知识包的关系

| 知识包 | 作者 | 视角 | P0 |
|--------|------|------|-----|
| doubao-work | APPSO | 功能实测 | 8✅ |
| doubao-work-context-layer | AI产品阿颖 | 个人战略感悟 | 4✅1⚠️1❌ |
| **doubao-work-org-productivity** | **36氪/陈曦** | **行业数据+组织ROI** | **5✅1⚠️0❌** |

## 已知限制

1. 博文为36氪分析文章，虽引用第三方数据但仍有作者分析框架
2. 信通院认证待官方佐证，已标注⚠️
3. 博文发布于产品上线当天，功能和认证状态可能更新
4. 20条作者观点代表36氪/陈曦立场，不代表OKF知识库立场
5. "龙虾"为行业俚语（指AI Agent浪潮），非具体产品名
6. stale_after设为2026-11-30，3个月后复核
