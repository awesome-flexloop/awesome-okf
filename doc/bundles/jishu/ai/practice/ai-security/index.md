---
okf_version: "0.2"
type: group
title: "🛡️ AI 安全与红队研究"
description: "elder-plinius 三仓库——系统提示词透明档案·越狱攻击面研究库·拒绝行为消除研究工具包，覆盖 AI 安全对抗的守方机制、攻方入口与权重级干预三层"
total_bundles: 3
---

# 🛡️ AI 安全与红队研究

本分组沉淀 GitHub 红队研究者 elder-plinius（Pliny the Prompter）三个公开开源仓库的源码级中文教程。同一作者、同一红队研究视角，三个仓库恰好构成一条完整的“AI 安全对抗研究”知识线，分别对应攻防博弈的三个层次：

- 📜 **守方机制层——[CL4R1T4S 系统提示词透明档案](cl4r1t4s/index.md)**：收录 26 个厂商目录、73 个档案文件，涵盖 OpenAI/Anthropic/Google/xAI/Cursor/Devin/Manus 等主流 AI 产品的完整提取系统提示词。其核心主张是 AI 系统透明性——“shadow-puppet”（皮影戏）隐喻：用户在对话窗口看到的只是皮影，真正操纵其行为的系统提示词藏在幕后；该仓库把操纵者拉到台前，让守方防御设计变得可审计、可研究。
- ⚔️ **攻方入口层——[L1B3RT4S 越狱提示词研究库](l1b3rt4s/index.md)**：34 个厂商 .mkd 档案系统梳理各产品的越狱攻击面，配套 glitch token 编目数据库（*SPECIAL_TOKENS.json，7895 条）与 Unicode 隐写载体文件群，从攻击者视角回答“对齐防线在哪里、以何种方式失守”。AGPL-3.0 许可。
- 🔬 **模型层——[OBLITERATUS 拒绝行为消除研究工具包](obliteratus/index.md)**：abliteration 权重级干预研究工具，提供六阶段流水线（SUMMON→PROBE→DISTILL→EXCISE→VERIFY→REBIRTH）、7 方法预设（CLI 实际 10 个 choices）、15 分析模块、informed 闭环流水线、130 模型预设（5 层级，README 称 116 为勘误项），支持多 GPU、量化与远程执行，并内置社区遥测研究平台。AGPL-3.0+商业双许可。

三层之间是递进的因果链：提示词里写了什么防御（cl4r1t4s）→ 这些防御如何被提示词级攻击绕过（l1b3rt4s）→ 防御如何刻进模型权重、又如何被权重级干预研究性地移除（obliteratus）。攻防对抗从来不是单点问题：读懂守方设计才能理解攻方为何绕行，读懂攻方路径才能理解权重级对齐的必要性，也才能反过来评估每一层防御的真实强度。

> ⚠️ **用途限定声明**：三个仓库的全部内容仅用于 AI 安全研究与防御评估。本分组所有教程均为**研究性中性转述**——聚焦机制解剖、技术分类学与工程实现原理，不提供、也不复现任何可操作的攻击载荷。请勿将本组内容用于生成对抗性提示词，或绕过任何在役系统的安全策略。

## 推荐学习路径

```
🛡️ AI 安全对抗三层地图：守方机制 → 攻方入口 → 模型层干预

入口二选一，按兴趣深入：
  🔬 obliteratus  权重级对齐干预 —— 技术原理最扎实、学术引用最全，适合从机理入手
  📜 cl4r1t4s     系统提示词透明档案 —— 工程视角，适合从提示词设计与安全审计入手
        ↓
📜 cl4r1t4s      守方机制层：逐层解剖 26 家厂商系统提示词，
                 看清对齐在提示词里布置了哪些身份、约束与防注入指令
        ↓
⚔️ l1b3rt4s      攻方入口层：越狱技术分类学与攻击面测绘，
                 看清对齐防线的薄弱位置与失守方式
        ↓
🔬 obliteratus   模型层：refusal direction 定位与 abliteration 六阶段干预，
                 理解对齐如何刻进权重、又如何被研究性地移除与验证
```

两条入场路线各有侧重：**obliteratus** 路线适合机器学习背景读者，其研究文档（RESEARCH_SURVEY、mechanistic_interpretability_research、executive_research_summary 等）学术引用最全、原理推导最扎实，从残差流几何一路讲到干预效果的验证与复现；**cl4r1t4s** 路线适合提示词工程与安全审计读者，直接面对真实在役产品的提示词原件，学习成本最低、获得感最快。l1b3rt4s 建议在前两者之后阅读——此时你已理解守方设计与权重级机制，再看攻方分类学与 glitch token、Unicode 载体等入口研究，会有事半功倍的对照感。

## 知识包导航

| 知识包 | 文档数 | 一句话简介 |
|--------|--------|-----------|
| [cl4r1t4s](cl4r1t4s/index.md) | 8 | 系统提示词透明档案——26 家厂商目录、73 份完整提取的系统提示词（OpenAI/Anthropic/Google/xAI/Cursor/Devin/Manus 等），逐层解剖守方布置的身份、任务、防注入与输出约束机制，理解对齐第一道防线的真实长相（5 概念+1 示例+1 参考+1 索引） |
| [l1b3rt4s](l1b3rt4s/index.md) | 7 | 越狱提示词研究库——34 个厂商档案梳理越狱攻击面，配套 7895 条 glitch token 编目数据库（*SPECIAL_TOKENS.json）与 Unicode 隐写载体研究，给出攻方视角的对齐失守地图（AGPL-3.0） |
| [obliteratus](obliteratus/index.md) | 11 | 拒绝行为消除研究工具包——abliteration 权重级干预：六阶段流水线（SUMMON→PROBE→DISTILL→EXCISE→VERIFY→REBIRTH）、7 方法预设、15 分析模块、informed 闭环、116 模型预设（5 层级）、多 GPU/量化/远程执行与社区遥测平台（AGPL-3.0+商业双许可） |

## 核心概念速查

| 概念 | 一句话定义 | 所属知识包 |
|------|-----------|-----------|
| 系统提示词解剖四层结构 | 主流 AI 产品系统提示词普遍可拆为身份层（我是谁）、任务层（做什么）、约束层（不能做什么）、输出格式层（怎么交付）四层 | cl4r1t4s |
| 防注入指令分布 | 守方将防提示注入/防越狱指令分散嵌入系统提示词的多个位置形成冗余防线；分布位置与措辞强度本身即是研究信号 | cl4r1t4s |
| shadow-puppet 隐喻 | 用户对话到的只是“皮影”，真实行为由幕后系统提示词操纵——透明档案的价值在于把操纵者拉到台前 | cl4r1t4s |
| 越狱技术分类学 | 将公开越狱手法按策略归类（角色扮演框架、编码混淆、假设嵌套、渐进升级等），形成可检索的攻击面地图 | l1b3rt4s |
| glitch token | 分词器词表中处于训练分布外的异常 token，可诱发模型输出失控行为，被系统编目为潜在攻击入口（*SPECIAL_TOKENS.json 收录 7895 条） | l1b3rt4s |
| Unicode 隐写载体 | 零宽字符等不可见 Unicode 可作为越狱载荷的载体或混淆介质，绕过基于明文特征的过滤 | l1b3rt4s |
| refusal direction | 模型残差流中编码“拒绝”行为的方向向量，对其消融即可系统性削弱对齐——abliteration 的作用靶点 | obliteratus |
| abliteration 六阶段 | SUMMON→PROBE→DISTILL→EXCISE→VERIFY→REBIRTH：从召唤模型、探测拒绝方向、蒸馏干预目标、执行切除、验证效果到产出可复现产物的完整权重级干预流水线 | obliteratus |
| steering vectors | 在激活层面注入引导向量以定向改变模型行为的轻量干预手段，与权重级消融互为对照实验 | obliteratus |
| informed 闭环 | informed pipeline 依据评估反馈自动搜索干预方法与参数的闭环流水线，以数据驱动替代人工盲调 | obliteratus |

---

> **信任声明**：本分组索引与下辖三个知识包均基于 elder-plinius 三仓库源码与档案逐文件分析生成：CL4R1T4S 的 26 个厂商目录/73 个档案文件、L1B3RT4S 的 34 个厂商档案与 *SPECIAL_TOKENS.json 数据库、OBLITERATUS 的 obliteratus/ 包源码（分析模块/策略注册/流水线）与研究文档；仓库结构、数量、流水线阶段与方法名均经源码级核验。
> 
> **源码位置**：d:\spaces\SpecWeave\external\dao\action\elder-plinius\（CL4R1T4S / L1B3RT4S / OBLITERATUS 三个子目录）
> 
> **生成时间**：2026-09-02 | **维护者**：OKF Wiki Bot

```{toctree}
:hidden:
:maxdepth: 7

cl4r1t4s/index
l1b3rt4s/index
obliteratus/index
```
