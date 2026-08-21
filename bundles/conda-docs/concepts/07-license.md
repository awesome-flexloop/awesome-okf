---
okf_version: "0.2"
type: "concept"
title: "许可证与商业使用边界"
sources:
  - LICENSE
---

# 许可证与商业使用边界

conda-docs 仓库本身的许可证与 Conda 生态其他组件的许可证需要区分理解。

## conda-docs 仓库许可证

conda-docs 采用 **BSD 3-Clause License**（见源码仓库 LICENSE 文件），这是一种宽松开源许可证：

- ✅ 允许商业使用
- ✅ 允许修改
- ✅ 允许分发
- ✅ 允许私有使用
- ⚠️ 必须保留版权声明和许可证文本
- ⚠️ 不使用作者名字做推广背书

## 生态组件许可证差异

Conda 生态不同组件使用不同许可证，商业环境需特别注意：

| 组件 | 许可证 | 商业使用注意事项 |
|---|---|---|
| conda（核心） | BSD 3-Clause | 可自由使用 |
| conda-build | BSD 3-Clause | 可自由使用 |
| conda-docs（本仓库） | BSD 3-Clause | 可自由使用 |
| **defaults 频道包** | Anaconda EULA / commercial terms | ⚠️ 大规模商业使用可能需要 Anaconda 商业许可 |
| **conda-forge 频道包** | 各包独立许可证（多为 BSD/MIT/Apache） | 遵循各包自身许可证 |
| Miniconda 安装器 | BSD 3-Clause | 安装器本身宽松，但 defaults 频道包受 EULA 约束 |
| Miniforge 安装器 | BSD 3-Clause | 完全开源，默认 conda-forge 频道无商业限制 |

## 商业合规关键区分

```
conda（工具本身，BSD）    ✅ 自由使用
    ↓ 使用时
defaults 频道（Anaconda 仓库）  ⚠️ 商业使用需评估
conda-forge 频道（社区仓库）    ✅ 自由使用（遵循各包许可证）
```

> **关键点**：Conda 包管理器本身是自由开源的，但从 `repo.anaconda.com`（defaults 频道）下载的包集合受 Anaconda 商业服务条款约束。商业环境可选择：
> 1. 使用 Miniforge + conda-forge（完全开源）
> 2. 购买 Anaconda 商业许可
> 3. 自建内部包镜像频道

## 文档内容复用

conda-docs 中的文档内容（`.rst`/`.md` 文件）同样采用 BSD 3-Clause，可自由引用和翻译，但需注明来源为 Conda Documentation（https://docs.conda.io）。

> 📌 **免责声明**：本概念仅提供许可证信息概览，不构成法律建议。企业商业部署请咨询法务团队评估 Anaconda EULA 条款。
