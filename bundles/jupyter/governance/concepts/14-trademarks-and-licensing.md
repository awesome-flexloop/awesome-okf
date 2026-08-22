---
type: Concept
title: "商标政策与许可证"
description: "Jupyter商标由LF Charities持有，规定了命名使用、视觉品牌使用和软件许可规则，指代性使用无需批准，产品/商业使用需申请授权。"
tags: [trademarks, licensing, bsd, copyright, brand-guidelines, lf-charities]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T08:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T08:00:00Z" }
status: stable
stale_after: "2027-08-22"
sources:
  - id: trademarks
    resource: /references/trademarks-license-source.md
    title: "商标与许可证信源"
---

## 法律主体

- **商标持有方**：[LF Charities, Inc.](https://lfcharities.org/)（501(c)(3) 公益慈善组织）
- **代码许可**：3-Clause BSD License（Modified BSD License）
- **版权模型**：**共享版权模型**（shared copyright model）——Jupyter 项目不做版权转让（no copyright assignment），每个贡献者保留自己贡献的版权，但通过开源许可授权给所有人使用

## 商标政策适用范围

商标政策的目的是保护 Jupyter 品牌，确保 Jupyter 官方发布的质量，同时让社区能够以标准方式讨论 Jupyter 技术。

### 涵盖内容
- **文字商标**："Jupyter"、"JupyterLab"、"Jupyter Notebook"、"JupyterHub" 等
- **Logo**：Jupyter 各项目的 Logo 图像
- **品牌特征**：与 Jupyter 相关的独特视觉识别元素

### 适用场景
- Jupyter 官方发布的软件、文档和材料
- 社区使用 Jupyter 名称和品牌
- 衍生或基于 Jupyter 技术的产品/服务

## 命名使用规则

### ✅ 无需批准的使用

**指代性使用（Nominative Use）**：当你在讨论 Jupyter 官方项目或其组件时，使用 Jupyter 名称进行指代：

- "我的产品使用 JupyterHub 进行用户管理"
- "这个包扩展了 JupyterLab 的功能"
- "基于 Jupyter Notebook 的教学工具"

使用"Jupyter"、"JupyterLab"等作为名词、形容词（而非商标意义上）来指代官方软件时，属于合理使用，无需批准。

### ❌ 需要批准的使用

**产品/服务命名**：以下使用需要向 Jupyter 商标工作组申请授权：

1. **以 Jupyter 命名的衍生产品/发行版**：如"Jupyter for Education"、"Jupyter Enterprise Edition"等暗示官方关系的产品名称
2. **域名**：包含 "jupyter" 关键词的域名（如 `jupyter-example.com`）
3. **活动名称**：使用 Jupyter 名称的商业活动或会议
4. **商品销售**：销售印有 Jupyter 标志的商品
5. **服务商标使用**：在商业服务中使用 Jupyter 名称暗示官方背书

申请渠道：联系 Trademark and Branding 工作组。

## 视觉品牌使用规则

### ✅ 允许的使用
- 在网站、博客、演讲中使用 Jupyter Logo **标识**官方项目（指代性使用）
- 使用 Logo 链接到 jupyter.org
- 在演示中展示 Jupyter 界面截图

### ❌ 限制
- **不得修改 Logo**：不得改变 Logo 的颜色、比例、元素
- **不得使用衍生 Logo**：不得创建看起来像 Jupyter 官方 Logo 的变形版本
- **不得暗示官方背书**：不得将 Logo 放在可能被误解为官方产品/服务的位置

官方 Logo 和品牌指南见：[jupyter/design](https://github.com/jupyter/design) 仓库。

## 软件许可证：3-Clause BSD

Jupyter 所有官方代码采用 **3-Clause BSD License**（也称为 Modified BSD License 或 New BSD License）：

```
Copyright (c) [年份], Project Jupyter Contributors
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice,
   this list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.
3. Neither the name of the copyright holder nor the names of its contributors
   may be used to endorse or promote products derived from this software
   without specific prior written permission.
```

### 3-Clause BSD 的关键要点

| 条款 | 含义 |
|------|------|
| **条款1** | 再分发源码必须保留版权声明、条件列表和免责声明 |
| **条款2** | 再分发二进制形式必须在文档/材料中复制版权声明等 |
| **条款3（广告条款）** | 不得使用版权持有者或贡献者的名字为衍生产品背书（这是与2-Clause BSD的唯一区别） |

### 共享版权模型

Jupyter **不要求版权转让**（Copyright Assignment Agreement）。每个贡献者保留自己贡献的版权，但通过接受 BSD 许可证，所有贡献都在相同许可下对所有人可用。

这种模型的优势：
- 贡献者保留自己代码的版权
- 项目不需要法律实体持有版权
- 贡献门槛低，无需签署 CLA（Contributor License Agreement）
- 与 BSD 许可证的精神一致

## 新代码的许可证声明

每个源代码文件头部应包含适当的许可证声明。Jupyter 推荐使用简短形式：

```python
# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.
```

## 反常识要点

- **"Jupyter"不是"随便用"的**：虽然 Jupyter 是开源项目，但"Jupyter"这个名字和相关 Logo 是注册商标，有明确的使用规范。开源≠放弃商标权。
- **不使用 CLA**：与 Apache Foundation 等要求签署 CLA 的项目不同，Jupyter 采用共享版权模型，不要求贡献者转让版权或签署协议。
- **3-Clause BSD 的"第三条款"很关键**：它禁止利用贡献者名字为衍生产品背书，这保护了 Jupyter 品牌和贡献者的声誉。
- **商标持有方不是 Linux Foundation**：Jupyter 商标由 LF Charities（501(c)(3)）持有，而非 Linux Foundation（501(c)(6)）。Jupyter Foundation 是 LF 下的定向基金，但商标归属公益慈善实体。

## 相关概念

- [常设委员会与工作组](/concepts/07-committees-and-working-groups.md)
- [Jupyter 基金会](/concepts/05-jupyter-foundation.md)
- [软件子项目体系](/concepts/06-software-subprojects.md)
