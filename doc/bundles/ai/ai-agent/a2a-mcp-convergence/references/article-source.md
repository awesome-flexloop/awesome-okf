---
type: Reference
title: 博文信源事实清单
description: 微信公众号"AI干活我偷懒"博文《A2A与MCP：Agent互操作协议栈的合流时刻》F-001~F-053完整事实登记，含汇合事件、协议分工、A2A架构、治理缺口、核验补充与勘误
tags: [事实清单, 信源, 微信公众号, AI干活我偷懒, A2A, MCP, AAIF]
generated: { by: "blog-article-to-okf-bundle", at: "2026-08-28T23:50:00+08:00" }
status: stable
stale_after: 2026-12-31
sources:
  - id: wechat-article-aiganhuo
    resource: https://mp.weixin.qq.com/s/rhw4xEncNH-t7xcwrj_Hfw
    title: 《A2A 与 MCP》（AI干活我偷懒，2026-08-26）
---

# 博文信源事实清单

> 主信源：微信公众号"AI干活我偷懒"，2026-08-26 07:00 发布，无作者bio，无免责声明。
> URL：https://mp.weixin.qq.com/s/rhw4xEncNH-t7xcwrj_Hfw
>
> F-001~F-048 为博文原文事实/观点，F-049~F-053 为核验过程中补充的事实与勘误。

## 元信息

| 编号 | 事实 | 分类 | 核验 |
|------|------|------|------|
| F-001 | 文章标题《A2A 与 MCP：Agent 互操作协议栈的合流时刻》，公众号"AI干活我偷懒"，2026-08-26 07:00 | 元信息 | — |

## 汇合事件（F-002 ~ F-010）

| 编号 | 事实 | 分类 | 核验 |
|------|------|------|------|
| F-002 | 2026-08-20 Google将A2A协议捐赠给Linux Foundation旗下AAIF，与MCP同属一个中立治理机构 | 事件 | ⚠️ 时间线不精确，见F-049 |
| F-003 | A2A官方文档首页写明"MCP和A2A不是竞品"，A2A让独立Agent互相发现、委派任务、共享结果 | 官方定位 | ⚠️ 引文为意译，见F-053 |
| F-004 | AAIF 2025年12月成立，Linux Foundation托管，白金成员8家：AWS/Anthropic/Block/Bloomberg/Cloudflare/Google/Microsoft/OpenAI | 治理 | ✅ |
| F-005 | AAIF成员从不到40家涨到250家以上（2026年8月） | 治理 | ✅ |
| F-006 | AAIF已托管MCP（Anthropic）、goose（Block）、AGENTS.md（OpenAI），A2A并列其中 | 治理 | ✅ |
| F-007 | AAIF执行总监Mazin Gilbert："Companies don't want just one protocol; they want the whole stack to be open." | 引语 | ⚠️ Axios原文无法直接验证 |
| F-008 | lmunck博客：OpenAI/Google/Anthropic/Microsoft标准化Agent栈是为了在更上层竞争，标准正从竞争武器变成公共基础设施 | 作者观点 | 📝 |
| F-009 | 博文核心问题：A2A与MCP什么关系？合流后竞争移到哪里？ | 作者观点 | 📝 |
| F-010 | 直接竞争对手共治同一套标准在行业治理里极其罕见 | 作者观点 | 📝 |

## MCP与A2A分工（F-011 ~ F-019）

| 编号 | 事实 | 分类 | 核验 |
|------|------|------|------|
| F-011 | MCP是开源标准，把AI应用连到数据源/工具/工作流，官方类比USB-C | 协议定位 | ✅ |
| F-012 | A2A是Agent间开放标准，官方定位"互操作的通用语言" | 协议定位 | ✅ |
| F-013 | 两者不是上下级，是两根轴线：MCP垂直（应用到资源），A2A水平（Agent到Agent） | 协议关系 | ✅ |
| F-014 | MCP交互对象是数据源/工具/工作流；A2A是其他独立Agent | 协议分工 | ✅ |
| F-015 | MCP请求-响应；A2A多轮协商/长时程任务 | 协议分工 | ✅ |
| F-016 | MCP典型场景查数据库/调API/读文件；A2A跨组织协作/任务委派 | 协议分工 | ✅ |
| F-017 | MCP解决资源侧标准化（写一次server任何客户端连），A2A解决Agent侧标准化（任何框架Agent都能对话） | 协议分工 | ✅ |
| F-018 | 官方推荐栈：ADK构建+MCP装备工具+A2A通信——一个管"手"一个管"对话" | 最佳实践 | ✅ |
| F-019 | 博文引用A2A官方："A2A is for agent-to-agent communication... including those using MCP... discover, delegate, share results"以及"A2A不是MCP替代品" | 官方引文 | ⚠️ 意译非逐字，见F-053 |

## 为什么不能用一个协议（F-020 ~ F-024）

| 编号 | 事实 | 分类 | 核验 |
|------|------|------|------|
| F-020 | 工具无状态/预定义/一次调用一结果；Agent有状态/会推理/能多轮协商 | 概念区分 | ✅ |
| F-021 | 把Agent包装成工具会砍掉协商能力，Agent天生应直接对话 | 设计论证 | ✅ |
| F-022 | 没有A2A的连锁反应：点对点写死→定制→难扩展→互操作低→安全措施不一致 | 问题分析 | 📝 |
| F-023 | A2A不做：Agent开发框架/子Agent工具调用协议/即时消息应用 | 边界定义 | ✅ |
| F-024 | 简单调用用函数/API即可（上协议过度设计）；工具调用表达不了"谈判与澄清"是A2A存在原因 | 决策框架 | ✅ |

## A2A技术架构（F-025 ~ F-033）

| 编号 | 事实 | 分类 | 核验 |
|------|------|------|------|
| F-025 | 三角色：User发起/A2A Client代表用户/A2A Server暴露HTTP端点远程Agent | 技术架构 | ✅ |
| F-026 | Server为黑盒，内部记忆/工具不暴露——对方只需知道交付什么 | 技术架构 | ✅ |
| F-027 | Agent Card：JSON数字名片，声明身份/端点/能力/认证/技能 | 技术架构 | ✅ |
| F-028 | Task：有状态工单，唯一ID+定义生命周期 | 技术架构 | ✅ |
| F-029 | Message+Part：Part支持text/raw/url/data四种类型 | 技术架构 | ✅ |
| F-030 | Context：contextId把多个相关Task逻辑分组 | 技术架构 | ✅ |
| F-031 | 传输HTTP(S)+JSON-RPC 2.0，认证在Agent Card声明，凭证走HTTP头 | 技术架构 | ✅ |
| F-032 | Agent Response两种形态：新Task（长时程）或即时Message | 技术架构 | ✅ |
| F-033 | 三种交互：短任务请求-响应轮询/长任务SSE流/断连webhook推送 | 技术架构 | ✅ |

## 协同案例（F-034 ~ F-037）

| 编号 | 事实 | 分类 | 核验 |
|------|------|------|------|
| F-034 | 汽车修理店：Manager用A2A多轮追问异响细节再委派Mechanic | 官方案例 | ✅ |
| F-035 | Mechanic用MCP调诊断扫描仪/维修手册/升降机 | 官方案例 | ✅ |
| F-036 | Mechanic用A2A跨组织查Parts Supplier库存 | 官方案例 | ✅ |
| F-037 | 四步：诊断(A2A)→委派(A2A)→工具调用(MCP)→跨组织(A2A)；A2A仅在Agent间，设备走MCP | 官方案例 | ✅ |

## 共享治理与采纳（F-038 ~ F-043）

| 编号 | 事实 | 分类 | 核验 |
|------|------|------|------|
| F-038 | AAIF三层Agent栈：模型层推理规划/MCP层工具集成/A2A层Agent协调 | 治理架构 | ✅ |
| F-039 | 生产栈需两层：MCP连内部工单/CRM，A2A路由到外部专门Agent | 最佳实践 | 📝 |
| F-040 | 共享治理保护协议区别：一套安全审查/一条合规轨道/统一场所；分散治理风险是各自偏离 | 治理分析 | 📝 |
| F-041 | 采纳数据（neuralcoretech博客）：MCP月SDK下载超1.1亿/公共服务器超1万(2026-04)；A2A采纳组织超150家 | 数据 | ⚠️ 1.1亿无权威来源，1万+和150+已确认 |
| F-042 | AAIF四大工作流至2027：MCP v2(流式/认证)/A2A治理RFC(Q3 2026)/AGENTS.md v1.0/安全认证 | 路线图 | ⚠️ 框架来自第三方，见F-052 |
| F-043 | 企业端（neuralcoretech博客）：AWS Bedrock AgentCore 2026-08-21 GA；Google Cloud Next 2026 Gemini Enterprise Agent Platform用A2A | 产品动态 | ❌ AWS日期有误，见F-051；Google ✅ |

## 三个缺口与建议（F-044 ~ F-048）

| 编号 | 事实 | 分类 | 核验 |
|------|------|------|------|
| F-044 | 三个缺口：归因（多Agent链无作者）/授权（协议vs政策）/追索（合同性非技术性） | 作者分析 | 📝 |
| F-045 | 买家五问：无需人批能做什么/调用记录/错误合同承诺/版本测试/合作伙伴离线兜底 | 作者建议 | 📝 |
| F-046 | EU AI Act Digital Omnibus 2026-07-27生效，Annex III推迟至2027-12-02（momoadvisors博客） | 法规 | ✅ |
| F-047 | 三条判断：互操作变入场券/廉价互操作利好买家利空薄软件/持久优势是结果质量+问责+信任 | 作者观点 | 📝 |
| F-048 | 年底悬念：真正产出跨供应商Agent则共享栈为真，否则只是branding | 作者观点 | 📝 |

## 核验补充与勘误（F-049 ~ F-053）

| 编号 | 事实 | 分类 | 来源 |
|------|------|------|------|
| F-049 | A2A于2025-06-23首次捐赠给LF；2026-08是转入AAIF（非首次捐赠）。AAIF博客8/17，Google公告8/20 | 勘误 | LF/AAIF官方 |
| F-050 | MCP下载量官方数据点：9700万(2025底)/近5亿(2026-07)；1.1亿(2026-04)无官方直接来源但增长曲线合理 | 勘误 | MCP官方博客 |
| F-051 | AWS Bedrock AgentCore 2025-10-13已GA；2026年8月GA的是Payments(8/18)和Registry(8/6)子功能 | 勘误 | AWS官方What's New |
| F-052 | "四大工作流至2027"框架主要来自genee.tech第三方博客；AAIF官网未直接列出；MCP 2026-07-28已有重大更新 | 勘误 | AAIF官网/genee.tech |
| F-053 | A2A官方实际措辞："complement MCP"（非"not a replacement"）、"exchange work"（非"share results"）；博文为意译 | 勘误 | A2A官方文档 |

## 事实统计

| 类别 | 数量 | 编号范围 |
|------|------|---------|
| 博文元信息 | 1 | F-001 |
| 汇合事件 | 9 | F-002~F-010 |
| 协议分工 | 9 | F-011~F-019 |
| 为什么不能合一 | 5 | F-020~F-024 |
| A2A技术架构 | 9 | F-025~F-033 |
| 协同案例 | 4 | F-034~F-037 |
| 治理与采纳 | 6 | F-038~F-043 |
| 缺口与建议 | 5 | F-044~F-048 |
| 核验补充与勘误 | 5 | F-049~F-053 |
| **合计** | **53** | F-001~F-053 |
