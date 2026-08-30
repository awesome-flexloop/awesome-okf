---
type: OKF
title: 交叉引用
description: 与儒家四书知识包关联的其他知识资源：帛书老子阅读教程（think/laozi/boshu-reading）、laozi-lineage 老子传本谱系（SpecWeave 主仓库）、psi 理论体系，及 confucian 组未来增量规划（five-classics/xunzi/chuanxilu）
tags: [reference, cross-reference, confucian, four-books, laozi, psi]
generated: { by: "agent:create-confucian-okf-wiki", at: "2026-08-30T00:00:00+08:00" }
status: stable
stale_after: 2027-08-30
---

# 交叉引用

本文件登记与"儒家四书"知识包关联的其他知识资源，供读者深入学习时跳转参考。本包与 think/laozi/ 既有 bundle 构成经典阅读方法论的互补对：laozi 讲"版本怎么流传"，four-books 讲"注疏怎么分层使用"（见[四书知识包架构洞察](../insights.md)洞察5），两域 bundle 经本文件互联而不重复。

## 同仓库关联知识包

### 帛书《老子》阅读教程（think/laozi/boshu-reading）

**链接**：[帛书老子阅读教程](../../../laozi/boshu-reading/index.md)

**与本包的关系**：出土文献阅读方法的互补——本包以传世定本为底本、出土文献（定州汉简《论语》）作异文参照（F-055~F-062）；boshu-reading 以出土文本（马王堆帛书甲乙本）为底本展开阅读。两包共享"双源核对""异文并列登记"方法论，应用于不同问题域（洞察5）。

| 维度 | four-books（本包） | boshu-reading |
|------|-------------------|---------------|
| 底本 | 通行定本（朱熹《四书章句集注》所定系统之今通行本） | 马王堆帛书甲乙本 |
| 出土文献角色 | 定州汉简《论语》作异文参照（F-055~F-062） | 帛书即阅读底本 |
| 核心问题 | 注疏怎么分层使用（经文层/注疏层/现代解读层） | 版本差异怎么读（德经在前、避讳字、通假字） |
| 注家谱系 | 何晏→朱熹→刘宝楠/焦循→现代译注 | 王弼、河上公等传世注与帛书校读 |

### psi 理论体系（think/psi）

**链接**：[Ψhē 理论体系](../../../psi/index.md)

**与本包的关系**：同属 think 域的对照性理论资源。psi 分组收录 ψ=ψ(ψ) 自指递归理论体系（哲学、数学形式化、宇宙本论、意识研究四束）；本包的儒家心性论传统（性善论、慎独、修齐治平）可作为与之并置阅读的古典理论化样本——两者对"心性/意识"问题给出进路不同的理论化，读者可自行对观，本包不作比附。

## 跨仓库资源

### laozi-lineage（老子传本谱系）

**位置**：SpecWeave 主仓库 `bundles/laozi-lineage/`（不在 awesome-okf-xs 子模块内，故不作相对路径链接，此为 SpecWeave 主仓库说明）

**定位**：学术性的《老子》传本源流研究，侧重版本学、文献学、考古学。

**与本包的关系**：本包定州汉简《论语》部分（F-055~F-062）涉及的"出土文献与传世本对读"方法，在 laozi-lineage 中有系统的版本学展开（研究者侧）；儒家经典目前无对应的传本谱系 bundle，如未来需要可按同一模式在 confucian 组内扩展。

## 本组增量规划

confucian 分组当前只有 four-books 一个 bundle。规划中的增量 bundle：

| 规划 bundle | 覆盖范围 | 状态 |
|------------|---------|------|
| five-classics | 五经（《诗》《书》《礼》《易》《春秋》）深读 | 规划中，目录未创建 |
| xunzi | 《荀子》深读（性恶论、礼论，与孟子性善论对照） | 规划中，目录未创建 |
| chuanxilu | 《传习录》深读（心学系统的专门展开） | 规划中，目录未创建 |

> 以上为 spec 登记的增量规划条目，目录尚未创建，不作链接；儒家全 corpus（五经、十三经、《荀子》《传习录》及注疏传统）在本包[儒家经典体系总览](../concepts/00-classics-system.md)中作总览覆盖。

## 相关文档

- [儒家经典体系总览](../concepts/00-classics-system.md)——十三经体系与四书位置
- [原文权威信源](canonical-sources.md)——定州汉简《论语》登记
- [四书知识包架构洞察](../insights.md)——与 laozi bundle 的方法论互补（洞察5）
