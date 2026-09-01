---
type: Concept
title: 产品概览与核心能力
description: 豆包工作发布信息、产品定位、文档/PPT/网页生成能力、AI协同编辑、80+设计风格、带数据库网页、滚动额度模型
tags: [豆包工作, 产品发布, 文档生成, PPT, 网页生成, AI编辑, 额度模型, Doubao Work]
generated: { by: "blog-article-to-okf-bundle", at: "2026-08-28T23:55:00+08:00" }
status: stable
stale_after: 2026-12-31
sources:
  - id: appso-article
    resource: https://mp.weixin.qq.com/s/dqvRKQoH45cXL2F8z0ZHYw
    title: APPSO 豆包工作实测
  - id: 36kr-review
    resource: https://36kr.com/p/3954390879222917
    title: 36氪/爱范儿实测
---

# 产品概览与核心能力

> **事实基础**：本文所有具体数据与声明均带 F 编号，完整事实清单见 [references/article-source.md](../references/article-source.md)，核验报告见 [references/verification.md](../references/verification.md)。

## 1. 产品发布

2026年8月25日，字节跳动/豆包正式发布**豆包工作**（Doubao Work）——全新Logo、独立桌面客户端，定位为"面向生产力场景的全新Agent产品与品牌"（F-002）。

- **官网**：[doubao.com/work](https://www.doubao.com/work)（F-003）
- **可用平台**：豆包App内、飞书内、独立桌面客户端（F-003）
- **促销**：下载电脑版免费送30天订阅；已付费会员自动延期30天（F-004）

豆包过去两年是国内C端用户量最大的AI助手。近一两个月"工作任务"能力密集更新后，它已从聊天Bot转变为能干活的Agent（F-005）。

## 2. 基础能力矩阵

豆包工作覆盖当前办公Agent的主流能力（F-007）：

| 能力类别 | 具体功能 |
|---------|---------|
| 文档处理 | Word、Excel、PPT 原生可编辑文件生成 |
| 网页/应用 | 网页生成、小应用生成 |
| 多模态 | 图片生成、视频生成（见[01](01-multimodal-and-computer.md)） |
| 电脑操作 | 本地文件操作、远程控制（见[01](01-multimodal-and-computer.md)） |
| 协同 | 飞书云文档、AI协同编辑、@同事 |

### 实测：三份文件仅耗1%额度

APPSO 实测任务（F-009）：根据一份活动Brief、报名明细和供应商报价，生成三份原生可编辑文件：
- 活动执行方案 Word
- 报名与预算分析 Excel
- 内部提案 PPT（自动添加演讲者备注，F-010）

**5小时额度仅消耗1%**。博文评价完成度"非常高，生成结果可以直接拿来用"。

## 3. 交付即飞书云文档

使用飞书账号登录后，豆包工作交付的文档都是**飞书云文档**（F-011）：
- PPT/Word/Excel 均可直接在豆包工作内像飞书文档一样操作
- 可设置分享权限
- 可直接 @同事协同编辑

这意味着AI生成的文件不需要导出-上传-再分享的中间步骤，直接进入团队已有的文档协作流。

## 4. AI协同编辑

豆包工作支持对生成内容进行**局部修改**（F-012）：
- 直接选中要修改的区域
- 或通过对话进行定点/局部编辑
- 网页和应用几乎全方位支持

博文以工单表格为例：上传工单表格 → 要求整理为可视化网页 → 生成后直接修改内容、样式和布局，也可让AI定点编辑。

### 80+设计风格一键替换

网页生成内置**超过80种设计风格**（F-013），样式不满意一键替换，无需重新生成。

### 带数据库的网页

与多数办公Agent"HTML生成后数据不自动更新"不同，豆包工作的网页可以**直接带数据库**（F-014）：
- 生成完即为上线可用的服务
- 数据随源文档自动更新
- 省去Agent交付后的"返工成本"——以前AI生成PPT/表格/网页只是第一步，还要自己改格式、调布局、重新导出

## 5. 额度模型

豆包工作采用**滚动重置**机制，而非积分消耗完即止（F-032、F-033）：

| 维度 | 说明 |
|------|------|
| 5小时滚动额度 | 短时间使用强度有上限，到期自动回满 |
| 周额度 | 按周自动恢复 |
| 会员有效期内 | 可天天用、一直用，不会因额度耗尽而停用 |

**免费用户**：可用 Turbo 模型体验，额度有限但适合入门和简单任务（F-034）。
**Pro版**：窗口额度可完成大量日常办公，加强套餐可连续跑更多复杂任务（F-008、F-034）。

---

## 参考

- 完整事实清单：[references/article-source.md](../references/article-source.md)
- 核验报告：[references/verification.md](../references/verification.md)
- 多模态与电脑操作：[01-multimodal-and-computer.md](01-multimodal-and-computer.md)
