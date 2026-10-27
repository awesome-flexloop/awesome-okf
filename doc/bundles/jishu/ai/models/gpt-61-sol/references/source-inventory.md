---
type: Reference
title: Sol 信源与编号事实台账
source: https://developers.openai.com/api/docs/models/gpt-6.1-sol
sources:
  - id: model
    resource: https://developers.openai.com/api/docs/models/gpt-6.1-sol
  - id: cache
    resource: https://developers.openai.com/api/docs/guides/prompt-caching
  - id: migration
    resource: https://developers.openai.com/api/docs/guides/latest-model?model=gpt-6-astra
  - id: responses
    resource: https://developers.openai.com/api/docs/guides/migrate-to-responses
  - id: computer
    resource: https://developers.openai.com/api/docs/guides/tools-computer-use
  - id: safety
    resource: https://deploymentsafety.openai.com/gpt-6-1-sol
  - id: launch
    resource: https://openai.com/zh-Hans-CN/index/introducing-gpt-6-1-sol/
  - id: asana
    resource: https://asana.com/inside-asana/cut-browsers-agent-cost
  - id: asana-openai
    resource: https://openai.com/zh-Hans-CN/index/asana-browser-agent/
  - id: deepswe
    resource: https://deepswe.datacurve.ai/
status: draft
---

# Sol 信源与编号事实台账

采集日为 2026-10-27。F 编号只在本页登记，概念页引用编号，不复制另一份台账。下表中的“确认”只表示来源确实如此声明，不表示第三方复测成立。

## 信源分工

| 键 | 实际读取对象 | 读取方式与边界 |
|---|---|---|
| S1 | [模型参考](https://developers.openai.com/api/docs/models/gpt-6.1-sol) | Defuddle 正文、浏览器端点图标、恢复后 WebFetch；限速档位名称出现不同快照 |
| S2 | [缓存指南](https://developers.openai.com/api/docs/guides/prompt-caching) | 前轮正文与恢复后 WebFetch 不一致，TTL 与写入费处于冲突状态 |
| S3 | [模型迁移指南](https://developers.openai.com/api/docs/guides/latest-model?model=gpt-6-astra) | 前轮取得 Sol 迁移说明；恢复后返回 Astra 主章节，不把其全部能力继承给 Sol |
| S4 | [Responses 迁移](https://developers.openai.com/api/docs/guides/migrate-to-responses) | 已读 Items、工具回传、多轮状态；通用接口规则 |
| S5 | [Computer use](https://developers.openai.com/api/docs/guides/tools-computer-use) | 已读 driver、工具循环及安全建议；部分模型建议指向 Astra |
| S6 | [Sol 系统卡增补](https://deploymentsafety.openai.com/gpt-6-1-sol) | WebFetch 取得前半至 5.2 前；后半子路由未取得目标正文，浏览器连接失败 |
| S7 | [Sol 发布文](https://openai.com/zh-Hans-CN/index/introducing-gpt-6-1-sol/) | Defuddle 403 后浏览器读正文及 Vega 精确标签；发布文日期未取得 |
| S8 | [Asana 原文](https://asana.com/inside-asana/cut-browsers-agent-cost) | Defuddle 已读；案例作者自报，不是独立模型评测 |
| S9 | [OpenAI 转述 Asana](https://openai.com/zh-Hans-CN/index/asana-browser-agent/) | 浏览器已读；与 S8 是同一实验，不能算第二个独立样本 |
| S10 | [DeepSWE 官网](https://deepswe.datacurve.ai/) | WebFetch 已读方法与可见榜单；本次可见榜单没有取得 GPT-6.1 Sol 条目 |

S1–S7 是同厂商资料；S8–S9 是同一案例的原述与转述。S10 是独立基准组织的方法来源，但并未完成 Sol 分数的独立验证。API、价格、安全分级属于厂商声明；评测和降本成效均须带来源限定。

## API 与价格事实

| 编号 | 来源的客观声明或采集观察 | 来源与状态 |
|---|---|---|
| F-001 | 模型显示名 GPT-6.1 Sol，API 名 `gpt-6.1-sol`。 | S1，确认 |
| F-002 | 官方定位是复杂编码、computer use、专业工作，措辞为 near-Astra performance at a lower cost，并建议在用户任务上比较。 | S1、S7，厂商定位 |
| F-003 | 模型参考的 knowledge cutoff 为 2026-04-30。 | S1，确认；非发布日期 |
| F-004 | context window 为 1,050,000 tokens。 | S1，接口声明 |
| F-005 | max output 为 128,000 tokens。 | S1，接口声明 |
| F-006 | 文本和图像输入，文本输出；原生音频、视频不支持。 | S1，接口声明 |
| F-007 | effort 支持 low、medium、high、xhigh、max；默认 medium。 | S1，接口声明 |
| F-008 | none 和 minimal 不支持。 | S1，接口声明 |
| F-009 | Streaming、function calling、structured outputs 支持。 | S1，接口声明 |
| F-010 | Fine-tuning 不支持。 | S1，接口声明 |
| F-011 | Responses 工具栏列出 web search、file search、image generation、code interpreter、hosted shell、apply patch、skills、computer use、MCP、tool search 支持。 | S1，接口声明 |
| F-012 | Sol 工具调用要求 Responses API。 | S1，确认 |
| F-013 | Snapshots 栏只取得 gpt-6.1-sol，没有取得日期固定名称。 | S1，采集观察 |
| F-014 | 前轮浏览器显示 Build 5000 RPM/1M TPM、Launch 10000/4M、Grow 15000/40M；恢复后 WebFetch 显示 Tier 1 500/500000、Tier 2 5000/1M、Tier 3 5000/2M、Tier 4 10000/4M、Tier 5 15000/40M；两次均列 Free 不支持。 | S1，不同快照；账户映射未裁定 |
| F-015 | Standard 每百万 token 输入 2 美元、缓存读 0.10 美元、输出 10 美元。 | S1，两次取得 |
| F-016 | 模型参考称缓存输入费率为普通输入的 5%。 | S1，价格声明 |
| F-017 | 模型参考列 cache writes 每百万 2.50 美元，普通输入费率的 1.25 倍。 | S1，两次取得；与通用缓存页冲突 |
| F-018 | 输入超过 272K 时，完整请求输入和缓存费率 2 倍、输出 1.5 倍。 | S1，两次取得 |
| F-019 | Fast 价格为 Standard 2 倍，Batch 与 Flex 比 Standard 低 50%。 | S1，两次取得 |
| F-020 | 前轮记录了 Ultrafast 倍率，但原始来源位置没有保留，本束不能独立回验。 | 来源不可回验；不作为报价依据 |
| F-021 | 模型参考列 regional processing 可用时加价 10%。 | S1，两次取得 |
| F-022 | 前轮缓存说明列 30m 写入为普通输入 1.25 倍、12h 为 2.5 倍；恢复后 S2 只列 in_memory/24h，且称两种保留策略同价。 | S2，冲突，TTL 参数不可直接部署 |
| F-023 | 前轮缓存说明将写入作为替代输入计费类别；恢复后 S2 FAQ 称缓存写入无额外费。 | S2，冲突；账单口径未实测 |
| F-024 | 缓存要求完整前缀精确匹配，静态说明置前，变化内容置后；图像和工具也须匹配。 | S2，两次说明的共同机制 |
| F-025 | 前轮说明对 GPT-5.6 及以后要求 1024 可见输入 tokens，隐藏系统内容不计最低长度；恢复后 S2 通用说明最低 1024，但没有这个隐藏内容限定。 | S2，细则待复核 |
| F-026 | 缓存不跨组织共享；地区 processing/Regional Inference 是保留位置相关边界；会话不保证命中。 | S2，共同机制与边界 |
| F-027 | 前轮 Sol 迁移说明将 none/minimal 映射到 low，其余有效 effort 先保留；恢复后 Astra 迁移段也如此说明。 | S3，Sol 档位另由 S1 核对 |
| F-028 | Sol 支持无工具调用的 Chat Completions。 | S1，恢复后明确文字确认 |
| F-029 | 前轮 Sol 迁移段建议删除 temperature、top_p、top_logprobs，Chat 删除 logprobs，Responses include 删除 message.output_text.logprobs；恢复后取得 Astra 同名参数说明。 | S3，Sol 具体参数需真实请求验证 |
| F-030 | Responses 输入输出使用 typed Items，SDK 可读取 output_text。 | S4，通用接口规则 |
| F-031 | function_call_output 通过原 call_id 关联工具结果。 | S4，通用接口规则 |
| F-032 | previous_response_id 不继承上一请求的顶层 instructions。 | S4，通用接口规则 |
| F-033 | 多轮历史输入仍计费。 | S4，通用接口规则 |
| F-034 | ComputerToolset 需要应用实现 driver；BrowserToolset 暴露浏览器函数工具。 | S5，通用接入路径 |
| F-035 | 自管循环包含 computer 工具、computer_call/actions、computer_call_output 截图与 call_id 关联。 | S5，通用接口流程 |
| F-036 | API 对话 Items 与浏览器/登录/运行时状态分别由接口和应用环境维持。 | S4、S5，责任边界 |
| F-037 | Computer use 指南建议隔离环境与站点、动作白名单。 | S5，安全建议 |
| F-038 | Computer use 指南将页面内容视为不可信，对难逆操作保留用户确认。 | S5，安全建议 |
| F-039 | 指南要求运行限制与实际结果验证；应用负责执行与观察。 | S5，安全建议 |
| F-040 | store:false 不等于取消所有数据处理与保留。 | S4、S5，数据边界 |
| F-041 | Sol 系统卡增补页面标注 2026-09-29。 | S6，页面日期 |
| F-042 | 系统卡按网络安全 Critical、生化 High 管理，并称采用与 Astra 相同 safeguards stack。 | S6，厂商风险管理声明 |
| F-043 | 系统卡提示研究环境/API 与生产 ChatGPT 的提示、工具、effort 等可能不同。 | S6、S7，评测限制 |
| F-044 | 系统卡提示旧模型对照值可能取后续版本，而非发布值。 | S6，评测限制 |
| F-045 | Agentic Safe Completions 的 Sensitive personal data 行，Sol 0.744、GPT-6 Sol 0.854，higher is better。 | S6，官方特定评测，未复测 |
| F-046 | 指令层级攻击表 Sol defender success rate 为 99.99%。 | S6，官方特定评测，未复测 |

## 发布评测与案例事实

下述评测数字均为 S7 厂商自报；百分比与美元 cost per task 保留原图口径，非本束实测。按 low/medium/high/xhigh/max 排列的向量只表示图上各配置，不包含置信区间。

| 编号 | 来源的客观声明或采集观察 | 来源与状态 |
|---|---|---|
| F-047 | 浏览器图标显示支持 Chat Completions、Responses、Batch；Live、Realtime 及实时翻译/转写、Assistants、Fine-tuning、Embeddings、专门图像/视频/音频端点、Moderation、legacy Completions 不支持。 | S1，DOM 支持图标核对 |
| F-048 | 发布文称面向 Plus、Pro、Business、Enterprise、Edu 开放 ChatGPT 工作和 Codex，暂不在“聊天”提供。 | S7，发布时措辞；非账户验收 |
| F-049 | 发布文称未来几天开放 Sol Ultrafast、Codex token 生成最高 8 倍速度。 | S7，发布时预告；非当前保证 |
| F-050 | 发布图注明研究环境/API 评测，提示、工具、effort 与 ChatGPT 可能不同，竞争模型取公开报告。 | S7，方法限定 |
| F-051 | DeepSWE v1.1 Sol6.1 分数为 64.4/73.0/75.2/71.9/71.9%，每任务费用为 0.17/0.42/0.65/0.79/1.57 美元。 | S7，官方图精确标签 |
| F-052 | DeepSWE Astra high 73.2%/3.92 美元、xhigh 74.1%/4.43 美元、max 73.2%/7.50 美元。 | S7，官方图精确标签 |
| F-053 | GDP.pdf 覆盖金融、医疗、法律等 10 领域复杂 PDF；Sol6.1 分数 27/30/32/31.8/31%，费用 0.33/0.34/0.35/0.37/0.42 美元。 | S7，官方图 |
| F-054 | AutomationBench 1.0.6 使用 47 工具，覆盖销售、营销、运营、支持、财务、人力资源。 | S7，评测说明 |
| F-055 | AutomationBench Sol6.1 分数 24.7/31.7/33.2/35.5/36.1%，费用 0.16/0.19/0.23/0.25/0.30 美元。 | S7，官方图 |
| F-056 | AutomationBench Astra max 41.4%/1.73 美元；Opus5.5 含回退 max 42.5%/1.44 美元。 | S7，官方图，非同提供商实测 |
| F-057 | Fable5.1 约 40% 任务回退到 Opus5，图中未计回退费用；max 图值 31.4%/2.45 美元。 | S7，图注限制 |
| F-058 | OSWorld 2.0 使用 v2026.08.08 离线集、部分奖励；Sol6.1 59/66.8/69.6/69.4/71.4%，费用 0.42/0.77/0.96/1.05/1.27 美元。 | S7，官方图；非完整成功率 |
| F-059 | OSWorld Astra max 73.5%/9.44 美元。 | S7，官方图，同样部分奖励 |
| F-060 | Terminal-Bench Science0.1 涉及数据分析、模拟、拟合、定理证明；Sol6.1 43.7/47.6/51.1/53.7/57%，费用 1.79/2.34/2.76/2.89/5.47 美元。 | S7，官方图 |
| F-061 | Terminal-Bench Science Astra max 68.1%/23.80 美元；官方对最困难科研任务建议 Astra。 | S7，官方图及建议 |
| F-062 | Factuality 样本选自用户曾指出旧模型事实问题的脱敏对话；指标为回答至少含一处事实错误的比例，越低越好。 | S7，刻意易错样本；非典型生产流量 |
| F-063 | Factuality Sol6.1 比例 7.7/6.3/4.5/4.1/4.6%，费用 0.05/0.06/0.08/0.10/0.13 美元。 | S7，官方图 |
| F-064 | 搜索故障未告知用户测试 max：Sol6.1 2.1%、GPT-6 Sol 4.9%、Astra 1.5%、Luna 28.7%。 | S7，官方失败比例 |
| F-065 | 规避限制测试 max：Sol6.1 23.5%、GPT-6 Sol 64.4%、Astra 17.4%、Luna 42.4%。 | S7，官方失败比例 |
| F-066 | Computer 不对齐结果测试 xhigh：Sol6.1 4.3%、GPT-6 Sol 17.4%、Astra 2.4%、Luna 13.7%。 | S7，官方失败比例 |
| F-067 | 安全图包含压力或低风险诱发条件，部分未启用完整产品保护；不是典型失误率。 | S7，方法限定 |
| F-068 | OpenAI 的 Asana 案例页标注 2026-10-09。 | S9，页面日期 |
| F-069 | 案例为同一任务采集 32 本书、每本 6 字段，共 192 facts。 | S8、S9，案例自报；字段名未取得 |
| F-070 | 主实验组合为 2 历史预算、6 缓存/截图策略、4 模型、每条件 3 运行，共 144 运行；Asana 原文另列 12 次 follow-up。 | S8、S9，非 144 个独立任务 |
| F-071 | 最优策略累计 20 张截图后裁到最新 1 张、扩大历史预算、缓存累计历史。 | S8、S9，单任务实验 |
| F-072 | B 原生产配置费用至少 36.21 美元、耗时至少 22.5 分钟；B 优化 1.24 美元、C 优化 0.66 美元、Sol 优化 0.47 美元/约 4 分钟。 | S8、S9，案例自报；原基线含未完成运行 |
| F-073 | 76 倍比较同时更换模型和工作流；B 自身优化约 29 倍；Sol 优化对 B 优化约 2.6 倍。 | S8、S9，比较口径 |
| F-074 | Sol 大预算旧策略 1.97 美元、优化 0.47 美元；优化输入中 89% 命中缓存。 | S8、S9，案例自报 |
| F-075 | 案例记录 Sol 小预算 3/18、大预算 18/18 且正确；本束未确认 18 的统计单位，不能转为完整采集正确率；最优配置正确性为作者自报。 | S8、S9，分母单位待原报告回验 |
| F-076 | 模型 A/B/C 匿名；B 在阶段 1，C/Sol 在阶段 2；原基线的成本和时间为下限。 | S8、S9，实验边界 |
| F-077 | 原文按 provider token counters 计算费用，每个答案按独立准备的 reference 评分。 | S8，方法说明 |
| F-078 | follow-up 中不裁截图的 B/Sol 每调用成本比最优裁剪方案低约 1.2 倍，C 低约 5%；每条件 3 或 4 运行，作者不区分几个百分点差异。 | S8，per-call 指标 |
| F-079 | 原文说未运行到 480000 字符历史预算上限；该上限没有成为这些运行的约束。 | S8，方法限制 |
| F-080 | DeepSWE 页面显示 113 tasks、91 repos、5 languages、28 models；v1.1 可见更新时间为 2026-09-22，使用统一 mini-swe-agent harness 和手写行为验证器。 | S10，基准方法与时点 |
| F-081 | 本次取得的 DeepSWE 可见榜单没有 Sol6.1 条目；Astra xhigh 显示 74%±3%、4.43 美元，发布图对应 74.1%/4.43 美元。 | S10、S7，显示精度不同；Sol 未独立验证 |
| F-082 | 恢复后模型参考称 Sol 支持 US/EU data residency，EU data residency 下 Fast 不可用。 | S1，接口地域边界 |
| F-083 | 恢复后 Astra 迁移指南称 GPT-5.5 及以前的 prompt_cache_retention 改为 prompt_cache_options.ttl="30m"；通用缓存页却仍给旧参数与 24h。 | S3、S2，文档冲突；不是 Sol 参数已验收 |

## 冲突裁定与未取得项

### 可回验摘录与历史记录

以下短摘录保存恢复后实际 WebFetch 返回内容。采集日期为 2026-10-27，未记录精确采集时分秒；不补造时间或历史全文哈希。它们可证明本次返回内容，不能证明浏览器与提取器为什么不同。

| 证据 ID | 页面与通道 | 必要原文摘录 | 关联 |
|---|---|---|---|
| S1-W1 | 模型页，WebFetch | `Cache writes` / `\$2.50`；`Cache writes are billed at 1.25x the uncached input token rate.` | F-017；当前可回验模型价 |
| S1-W2 | 模型页，WebFetch | `Tier 1` / `500` / `500,000`；`Tier 5` / `15,000` / `40,000,000` | F-014；仅保存两个端点行，其余数值在台账 |
| S2-W1 | 缓存页，WebFetch | `Prompt cache pricing is the same for both retention policies.`；`Allowed values are in_memory and 24h.` | F-022 |
| S2-W2 | 缓存页，WebFetch FAQ | `Will I be expected to pay extra for writing to Prompt Caching?` / `No. Caching happens automatically, with no explicit action needed or extra cost paid to use the caching feature.` | F-023 |
| S3-W1 | Astra 迁移页，WebFetch | `replace prompt_cache_retention with prompt_cache_options.ttl set to "30m"` | F-083；Astra 段落，非 Sol 测试结果 |
| H1 | 前轮浏览器/正文记录 | 原始完整快照未入包；仅保留采集记录，不能逐字回验 | F-014 的命名、F-022/023 前轮细则、F-029；降低证据等级 |

H1 中的数值和参数不作为当前账户报价或已验证接入依据。冲突原因仍未知，不能擅自归为官网更新或旧缓存。没有历史原文证据时，审查关闭的是误用路径，不是事实冲突本身。

| 项目 | 本束裁定 | 后续证据要求 |
|---|---|---|
| 缓存写入费用与 TTL | S1 两次一致列写入费；S2 返回了相互矛盾的保留和写入说明。价格表作为模型参考快照，公式仅作条件推导，不给可直接部署的 TTL 请求 | 在同一真实 Sol 账户核对模型价格、最新参数文档、usage 与实际账单 |
| 限速档位名称 | 并列两次采集记录与恢复后必要摘录，未保存历史完整快照；不把 Build/Launch/Grow 等同某 Tier，也不推算本账户限额 | 账户 limits 页与实际请求节流 |
| 参数迁移 | Sol effort 与工具端点已由 S1 确认；其他删除项保留前轮来源限定，不宣称真实请求已通过 | 固定 SDK 版本，以测试请求验证 |
| 发布日期 | 发布文日期未取得；不能用继续阅读日期或 knowledge cutoff 替代 | 官方正文时间字段 |
| 当前产品权益与速度 | 发布预告不证明今日账户已开放或达到 8 倍 | 账户页面、服务模式与端到端计时 |
| 系统卡后半与训练细节 | 未取得目标章节；参数量、MoE/训练规模、权重许可不作推测 | 完整官方系统卡及架构资料 |
| 独立 Sol 评测 | S10 仅核对方法，不算独立确认 Sol 分数 | 对应版本原始结果或可复跑数据 |
| Asana 完整实验附件 | [研究 PDF](https://assets.asana.biz/asset/fb86cc8e-6611-4404-b7c6-172692a724bb/How-Asana-used-Codex-to-optimize-browser-agent-costs-and-runtime.pdf) 只取得链接，未读；图的运行点和标准差未完整取得 | 阅读完整报告及原始运行日志 |
| 真实使用 | 本束未调用 Sol API，未运行电脑环境，没有 SLA 或采购验收结论 | 脱敏任务、固定执行器、权限和真实账单对照 |

### 编号与更新规则

F 编号不可复用。新证据改变旧口径时新增编号，记录有效时点与 `supersedes: F-xxx`，旧项标历史/被替代并保留原来源；正文转引当前项，日志追加修改原因。需要新证据时记录原文短摘录、URL、精确采集时间、页面定位和抓取方式；只取得摘要时降级，不用推导补成原文。

返回[教程入口](../index.md)。
