---
type: Example
title: 费曼讲义章节读法
description: 以第2卷第18章（麦克斯韦方程组）为例，演示在版权讲义类教材的阅读与合规短引——物理图像优先、表格对照与官网在线版使用
tags: [example, 费曼, 费曼物理学讲义, 麦克斯韦方程, 章节读法]
generated: { by: "agent:seven-concepts-cmd", at: "2026-08-30T10:30:00+08:00" }
verified: { by: "process:seven-concepts-r", at: "2026-08-30T10:30:00+08:00" }
status: stable
stale_after: 2027-08-30
sources:
  - id: facts
    resource: /facts.md
    title: 事实清单
  - id: primary
    resource: /references/01-primary-sources.md
    title: 核心元典原文信源总表
  - id: copyright
    resource: /references/04-copyright-policy.md
    title: 版权分级与引用策略
---

# 费曼讲义章节读法

《费曼物理学讲义》（*The Feynman Lectures on Physics*，1964-1966）在版权保护期内（Caltech 提供官方免费在线版，feynmanlectures.caltech.edu）。本文以第 2 卷第 18 章（"The Maxwell Equations"）为例，演示讲义类经典的读法与合规引用方式。

## 一、文本定位与获取

- 三卷结构：V1 经典物理（含相对论入门）、V2 电磁学与物质、V3 量子力学。
- 官方在线版免费浏览全文（见 [信源总表](../references/01-primary-sources.md)）；中译本为上海科技社新千年版（李洪芳等译）。
- 引用规则：外文单段短引不超过 50 词，本示例外文引文总量在 200 词配额内；中译本不转述，只登记书目。

## 二、读法第一步：先看这一章在全书的位置

第 2 卷用近 20 章铺垫：静电场（V2 ch.4-7）、场的矢量语言（散度/旋度，ch.2-3）、磁场（ch.13-14）、感生电场（ch.17）。第 18 章是收束——把此前散见的规律写成完整方程组。读该章前应已读过 ch.2（矢量场微分）与 ch.17（感应定律）。

## 三、读法第二步：抓住费曼的组织方式

第 18 章开头给出麦克斯韦方程组的标准形式（∇·E = ρ/ε₀；∇·B = 0；∇×E = −∂B/∂t；c²∇×B = j/ε₀ + ∂E/∂t），随后用整章讨论"这些方程意味着什么"。费曼在第 2 卷第 1 章结尾对麦克斯韦工作有一句著名评价，可作为读第 18 章的动机（42 词短引，读者应在官网原文核对上下文）：

> "From a long view of the history of mankind—seen from, say, ten thousand years from now—there can be little doubt that the most significant event of the 19th century will be judged as Maxwell's discovery of the laws of electrodynamics."

讲义中这种把物理定律放进历史尺度、讨论"定律意味着什么"的段落，是读法重心——不要只抄方程。

## 四、读法第三步：与麦克斯韦原著对照

第 18 章是进入麦克斯韦《电磁通论》（1873，PD）的最佳跳板，对照点：

| 费曼 V2 ch.18（现代） | 麦克斯韦《电磁通论》（1873） |
|----------------------|---------------------------|
| 四个矢量方程（散度/旋度） | 20 个分量方程，无 ∇ 符号 |
| 直接从场论结构展开 | 含涡旋-惰轮等力学模型类比 |
| 位移电流作为方程组分 | 位移电流作为模型推论引入 |
| 第 20-21 章电磁波解 | 第 XX 章光的电磁理论 |

对照读法：先读费曼掌握矢量形式 → 回到《电磁通论》对应卷次认亲分量式（方法见 [几何风格与代数风格](../concepts/05-geometric-reading.md)）→ 标注"哪些物理图像被现代整理保留、哪些模型被放弃"。

## 五、讲义类著作的通用读法

1. **按章节顺序通读**，不要跳读——费曼与朗道都在前面章节为后面埋伏笔（朗道密度更高）。
2. **每章回答一个问题**：本章新引入的核心概念是什么？ch.18 的答案是"位移电流与场方程闭合"。
3. **图像优先于推导**：费曼讲义的独特价值是物理图像；推导细节可配合标准教材。
4. **中译本对照术语**：散度/旋度/位移电流等术语与中译核对后建立自己的术语表。
5. **引用合规**：短引 ≤50 词并指向官网；不复制整节内容。

## 六、检查清单

1. 第 18 章之前为什么必须先读散度/旋度章（ch.2-3）？
2. 四个方程各自的物理名称与实验来源是什么？
3. 位移电流为什么是方程组闭合的关键？
4. 费曼的矢量方程与麦克斯韦 1873 分量式之间，差别是符号还是物理内容？

## 相关文档

- [教材与原典配合](../concepts/07-textbooks-and-originals.md)
- [版权分级与引用策略](../references/04-copyright-policy.md)
- [核心元典原文信源总表](../references/01-primary-sources.md)