---
okf_version: "0.2"
type: concept
title: "注意力战术与作者开源产物"
description: "文章点名的三条 Make Time 战术（Caffeine Nap / Be Stuck / Random Question List）及其机制，以及作者开源仓库 LearnPrompt/qbs 的三个内置 skill、安装命令与官方口径对照"
tags: [make-time, tactics, caffeine-nap, be-stuck, qbs, agent-skills, open-source]
sources:
  - id: blog-article
    url: https://mp.weixin.qq.com/s/cyiP8goJJrB5-Fi_F96GKA
  - id: official-qbs-repo
    url: https://github.com/LearnPrompt/qbs
---

# 注意力战术与作者开源产物

## 一、Caffeine Nap（咖啡小睡）

| 项 | 内容 | F 编号 |
|---|------|--------|
| 做法 | 喝完咖啡**立刻睡 15 分钟** | F-028 |
| 机制 | 咖啡因需要约 **20 分钟**才生效；醒来时"自然清醒"与"咖啡因起效"同时到位 | F-028 |

**核验结论**（P0-4，✅ 通过）：咖啡因经小肠吸收至入脑约 20 分钟，短睡 15–20 分钟为通行区间，与书中战术一致（见 [verification.md](../references/verification.md)）。

> 这是一条**剂量与时机有生理学依据**的战术：把"起效延迟"当作可利用的窗口，而不是等待成本。

## 二、Be Stuck（卡住时别逃）

| 项 | 内容 | F 编号 |
|---|------|--------|
| 做法 | 卡住的时候不要逃——**不要切到别的窗口**，盯着屏幕或起来走两步都行 | F-029 |
| 理由 | 切走看似在休息，实际是给大脑**灌新上下文**；回来要重新加载刚才的思路，**又是一个 Time Crater** | F-030 |

**机制解读**：这条战术直接建立在 Time Craters 与切换成本之上（见 [01-make-time-framework.md](01-make-time-framework.md) 第五节）——切走一次的成本不是切换的那几秒，而是重新加载思路的二十余分钟。因此"留在原地发呆"在成本上优于"切走 30 秒"。

## 三、Random Question List（随机问题清单）

| 项 | 内容 | F 编号 |
|---|------|--------|
| 做法 | 脑子里突然冒出的问题**不要立刻搜**，写在纸上攒着一起查 | F-031 |
| 理由 | 搜一个配置问题会顺手看到娱乐短视频和科技热点，**半小时就没了**；且新内容越多反而更焦虑 | F-032 |

**机制解读**：这条战术针对的是 Infinity Pools（无底洞）——"搜一下"的真实成本不是查询本身，而是搜索入口带来的无限内容流（F-023）。

## 四、作者的开源产物：LearnPrompt/qbs

### 仓库身份

| 属性 | 值 | F 编号 |
|------|-----|--------|
| 地址 | `github.com/LearnPrompt/qbs` | F-033 → F-049 |
| 定位 | Agent Skills 项目（MIT 许可） | F-049 |
| README 标语 | "QBS = Question → Book → Skill" | F-049 |
| 构成 | QBS 方法本体 + 由书籍提炼出的 skill 集 | F-033 |

> 文章中的地址写作 `github. com/LearnPrompt/qbs`（含空格），系排版处理；仓库本身已核实存在（F-049）。

### 内置三个 skill

文章称"除时间管理外还包含两个 skill"（F-034）；仓库 README 给出了三个的精确名称与适用场景（F-050）：

| skill | 对应问题 | F 编号 |
|-------|---------|--------|
| `make-time` | 一天被 AI 任务打成碎片 | F-050 |
| `the-debugging-book` | AI 修 bug 反复猜 | F-050 |
| `shape-up` | AI 把小需求越做越大 | F-050 |

> **数量与博文一致（时间管理 + 2 个），名称更精确**——博文的"修 bug""越做越大"分别对应 `the-debugging-book` 与 `shape-up`（见 [verification.md](../references/verification.md) §四）。

### 安装方式

```bash
npx skills@latest add LearnPrompt/qbs --skill qbs
```

依赖 Node.js / npm / npx 与 Git（F-051）。

> 这条路径说明：QBS 产出的 skill 通过**通用 Agent Skills 分发方式**交付，而非绑定某一平台。可对照 [mattpocock-skills](../../mattpocock-skills/index.md) 中描述的 Skills 生态与分发渠道。

### 官方口径与博文自述的对照

| 维度 | 博文（作者自述） | 仓库 README（官方口径） |
|------|-----------------|------------------------|
| 时间损耗 | 推算约 5 小时/天（F-039，取决于已勘误的 F-026） | 明确声明"目前没有完整计时数据，**暂不承诺'几分钟做完'**"（F-052） |

> **口径对照价值**：README 的"不承诺耗时"与博文的个人推算形成互补——**方法论可复用，耗时数据不可外推**。

## 五、作者的读书闭环（QBS 的附带效应）

| 事实 | 内容 | F 编号 |
|------|------|--------|
| 阅读现状（自述） | book 里躺着十几本书，最近一次打开记录是**四个月前**，今年买了七八本一本都没读完 | F-042（作者自述） |
| 观点 | 带着**具体问题**读书、从**能解决问题的一页**开始，不知不觉整本书就看完了 | F-043（作者观点） |
| 观点 | QBS 的一个"副作用"是**重燃了读书热情** | F-044（作者观点） |

该意图在开源仓库中被产品化：**Skill 每次交付时，会说明刚才那个判断来自哪一章**（F-049 / 对照 F-009 的模板要求 ②）。

```text
具体问题 → 定向读书（可被要求"说出读了哪几章"）
        → 提炼 skill（带章节出处）
        → 新任务试跑
        → 读书行为被"有用性"反向驱动，形成闭环
```

## 主题关联

- [00-qbs-method.md](00-qbs-method.md)：本篇的 skill 产物由 QBS 方法生成
- [01-make-time-framework.md](01-make-time-framework.md)：三条战术共同依赖的 Time Craters 与切换成本机制
- [mattpocock-skills](../../mattpocock-skills/index.md)：Agent Skills 的安装与分发生态
- [codex-agent-workflow-practices](../../codex-agent-workflow-practices/index.md)：Codex 多任务并行的工作流实践（与作者 F-035 所述"后台挂着七八个任务"的处境同源）

## 已知边界

- **战术为节选**：文章只点名了三条战术，书中总计 87 条（F-027），本篇不代表全貌。
- **作者自述不可外推**：F-042 ~ F-044 为个人经验与观点。
- **时效性**：模型称呼（GPT-6、Fable 5.1，F-041）与仓库活跃度随时间变化；`npx skills@latest` 的用法以仓库 README 当前版本为准。