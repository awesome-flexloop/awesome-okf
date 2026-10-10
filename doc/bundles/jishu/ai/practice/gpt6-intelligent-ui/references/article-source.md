---
okf_version: "0.2"
type: fact-registry
title: "事实编号清单：GPT-6 Intelligent UI（F-001 ~ F-034）"
sources:
  - id: "apso-gpt6-intelligent-ui"
    title: "全网首个可交互诺贝尔文学奖书单来了，这是GPT-6最好玩的新功能"
    url: "https://mp.weixin.qq.com/s/fmYnRRxXB1Ok3HIB53xSMA"
    publisher: "APPSO"
    date: "2026-10-09"
status: draft
stale_after: "2026-12-31"
generated:
  by: "wechat-public-okf:recreate"
  date: "2026-10-10"
---

# 事实编号清单

> 类型：**O**=客观（页面/可验证事实）；**V**=作者观点/价值判断；**S**=厂商自述（OpenAI）。
> A-G 段（F-001~F-027）出自 APPSO 博文正文；H 段（F-028~F-034）为 2026-10-10 公开信源核验补充。
> P0=需独立核验的高风险声明；存在"P0"标记者详见 [verification.md](verification.md)。

## A 段：引入与诺奖背景（F-001~F-006）

| F | claim | type | source_id | locator | status |
|---|-------|------|-----------|---------|--------|
| F-001 | 莫言 2012 年获诺贝尔文学奖，作者曾花一晚理清其作品阅读顺序 | V | apso-gpt6-intelligent-ui | 第 1 段 | 作者回忆，非本束核验范围 |
| F-002 | 中国作家残雪、日本作家村上春树被博文列为"陪跑" | V | apso-gpt6-intelligent-ui | 第 2 段 | 单源/flagged（无独立官方证据，见 verification） |
| F-003 | 加拿大诗人、作家安妮·卡森（Anne Carson）摘得 2026 年诺贝尔文学奖 | O | apso-gpt6-intelligent-ui | 第 2 段 | P0，nobelprize.org 核验 ✅ |
| F-004 | 作者向 ChatGPT 提出用卡片手账方式整理安妮·卡森作品阅读清单 | O | apso-gpt6-intelligent-ui | 第 2 段 | 单篇体验 |
| F-005 | 阅读清单支持翻页、判断每本书是否适合入门与阅读顺序、读完可勾选"完成阅读"、进度更新 | O | apso-gpt6-intelligent-ui | 第 2 段 | 单篇体验 |
| F-006 | 这些功能来自 OpenAI 2026-10-07 发布《GPT-6 and Intelligent UI for everyone》，向全量 ChatGPT 用户推送 GPT-6 与 Intelligent UI | O | apso-gpt6-intelligent-ui | 第 2 段末 | P0，OpenAI 发布页核验 ✅ |

## B 段：场景可视化（F-007~F-010）

| F | claim | type | source_id | locator | status |
|---|-------|------|-----------|---------|--------|
| F-007 | "所有的场景都能可视化"为小节标题 | V | apso-gpt6-intelligent-ui | B 段 | 博文表述 |
| F-008 | OpenAI 定义 Intelligent UI 为"智能界面"：ChatGPT 根据提问把文字、图片、按钮、表单、图表及可互动工具动态组合 | O | apso-gpt6-intelligent-ui | B 段 | P0，定义一致性 |
| F-009 | 以前 AI 只能输出文字；GPT-6 能按提问现场组装含排版/按钮/表单/图表的独立界面 | O | apso-gpt6-intelligent-ui | B 段 | 机制单源解读 |
| F-010 | 应用场景含知识学习、娱乐、日常生活；官方示例含周日烤肉（菜谱/购物清单/时间表同现）与自驾游路线（休息站标地图、标记绕行点） | O | apso-gpt6-intelligent-ui | B 段 | 官方示例转述 |

## C 段：知识学习场景（F-011）

| F | claim | type | source_id | locator | status |
|---|-------|------|-----------|---------|--------|
| F-011 | 对化学知识点问"请告诉我酒精灯怎么用"，约 52 秒后产生交互方案；酒精灯使用拆成六个关键步骤，每步配提示 | O | apso-gpt6-intelligent-ui | C 段 | P0 单篇体验（等时/步骤数不可复现） |

## D 段：游戏场景（F-012~F-013）

| F | claim | type | source_id | locator | status |
|---|-------|------|-----------|---------|--------|
| F-012 | 对 GPT 说"给我做一个贪吃蛇的小游戏"，得到可直接玩的画面而非规则说明书，有完整规则/计分（每块+10 分）/实时反馈 | O | apso-gpt6-intelligent-ui | D 段 | 单篇体验 |
| F-013 | 可继续定制（小熊形象、每块+20 分），模型修改角色/规则/计分/界面，二次修改耗时更长 | O | apso-gpt6-intelligent-ui | D 段 | 单篇体验 |

## E 段：生活场景（F-014~F-016）

| F | claim | type | source_id | locator | status |
|---|-------|------|-----------|---------|--------|
| F-014 | 上传宠物照片问"哪一套更符合我宠物的特点"，GPT 并排放置两件衣服并标注颜色/尺寸/材质/适用场合 | O | apso-gpt6-intelligent-ui | E 段 | 单篇体验 |
| F-015 | 用户可据使用场景和偏好选择 | V | apso-gpt6-intelligent-ui | E 段 | 博文表述 |
| F-016 | "并不是将图表、按钮以及文字堆积在一起，而是让答案具有了继续工作下去的能力" | V | apso-gpt6-intelligent-ui | E 段末 | 作者观点 |

## F 段：黑盒随机性（F-017~F-020）

| F | claim | type | source_id | locator | status |
|---|-------|------|-----------|---------|--------|
| F-017 | OpenAI 演示麻将交互；APSO 按同法复现麻将桌难题，结果无麻将桌/按钮，而是普通礼貌文本 | O | apso-gpt6-intelligent-ui | F 段 | P0 单篇体验（复现失败） |
| F-018 | Intelligent UI 不是模型临时"画网页"，而是一套原生组件库加配套界面编译器 | O | apso-gpt6-intelligent-ui | F 段 | 机制单源解读 |
| F-019 | 模型可调用文字/图表/按钮/表单/交互区域，编译器边接收输出边逐步展现 | O | apso-gpt6-intelligent-ui | F 段 | 机制单源解读 |
| F-020 | OpenAI 产品经理 Aarush Selvan：设计团队研究何时加图表/按钮有用、何时混乱 | O | apso-gpt6-intelligent-ui | F 段 | 厂商自述 |

## F 段补充：调度规律（F-021~F-023）

| F | claim | type | source_id | locator | status |
|---|-------|------|-----------|---------|--------|
| F-021 | 若无特别提示，ChatGPT 按任务决定是否以互动方式交流 | V | apso-gpt6-intelligent-ui | F 段 | 博文归纳 |
| F-022 | 比较类问题可采用并排排列 | V | apso-gpt6-intelligent-ui | F 段 | 博文归纳 |
| F-023 | 复杂概念可用交互式图表，简单题目优先文字 | V | apso-gpt6-intelligent-ui | F 段 | 博文归纳 |

## G 段：局限、演进与结论（F-024~F-027）

| F | claim | type | source_id | locator | status |
|---|-------|------|-----------|---------|--------|
| F-024 | Intelligent UI 动态图表/交互组件更像一次性体验，缺少稳定代码沙盒与独立资产入口，轻量任务流畅、高精准/专业场景"显得小儿科" | V | apso-gpt6-intelligent-ui | G 段 | 作者观点 |
| F-025 | Intelligent UI 目前不支持 Pro effort；Pro effort 用 GPT-6 Astra | O | apso-gpt6-intelligent-ui | G 段 | P0，OpenAI 分层核验 ✅ |
| F-026 | 不支持 Pro effort 意味着"新界面与最强推理不能同现"，复杂长思考任务可能回到文字形式 | V | apso-gpt6-intelligent-ui | G 段 | 作者观点 |
| F-027 | 底层逻辑：多模态融合改变人机交互方式；自然语言宜表达复杂目标、图形界面宜观察状态/比较/调参 | V | apso-gpt6-intelligent-ui | G 段 | 作者观点 |

## G 段末：达尔文与转型（F-028~F-030 并入 H 段核验前）

| F | claim | type | source_id | locator | status |
|---|-------|------|-----------|---------|--------|
| F-028 | 2007 年第一代 iPhone 用点按/滑动/双指缩放重新定义手机操作（作者类比） | V | apso-gpt6-intelligent-ui | G 段 | 类比 |
| F-029 | 智慧如"豆包手机助手技术预览版把对话连到系统操作层"、"荣耀 MagicOS 9.0 YOYO"。用户说"帮我点一杯热拿铁"自动调用外卖应用下单并在结算前确认 | S | apso-gpt6-intelligent-ui | G 段 | 厂商演示转述 |
| F-030 | OpenAI："过去的几十年里，人们一直在学习用为具体任务设计好的固定程序，未来软件要适应人的各种工作" | S | apso-gpt6-intelligent-ui | G 段 | 厂商自述 |
| F-031 | 安妮·卡森《红的自传》引文"How does distance look? ... It depends on light"（"距离看起来是什么样？它取决于光"） | O | apso-gpt6-intelligent-ui | G 段末 | 文学引用，作者以此收束全文 |

## H 段：2026-10-10 公开信源核验补充（F-032~F-034）

| F | claim | type | source_id | locator | status |
|---|-------|------|-----------|---------|--------|
| F-032 | GPT-6 于 2026-10-07 发布，Intelligent UI 随《GPT-6 and Intelligent UI for everyone》向全量用户推送 | O | openai-gpt6-intelligent-ui | OpenAI 发布页 | P0，独立第三方（gihyo.jp）交叉验证 ✅ |
| F-033 | 安妮·卡森为 2026 年诺贝尔文学奖得主（诗人、作家） | O | nobelprize-literature-2026 | nobelprize.org | P0 ✅ |
| F-034 | GPT-6 存在 Astra / 探索模式（Pro effort）分层能力，Intelligent UI 暂不与 Astra 最强推理同现 | O | gihyo-gpt6 | 独立第三方媒体 | P0 交叉验证：与博文 F-025 口径一致 ✅ |

> **编号连续性校验**：本清单 F-001 ~ F-034 连续无跳号。A-G 段（F-001~F-031）出自博文正文；H 段（F-032~F-034）为 2026-10-10 公开信源核验补充。历史修订：无效编号 `F-026'` 已于首次产出更正为 `F-031`（《红的自传》引文），H 段编号顺延。