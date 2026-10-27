---
type: Concept
title: RTX Spark 平台定位与上市口径
description: 区分超级芯片、OEM 整机、本地 AI 平台以及地区发布与供应时间
tags: [RTX Spark, Windows on Arm, 产品发布]
source: ../references/article-source.md
sources:
  - id: facts
    resource: ../references/article-source.md
  - id: cn
    resource: https://blogs.nvidia.cn/blog/nvidia-rtx-spark-pcs-available-today-a-new-beginning-for-windows-pcs/
  - id: en
    resource: https://nvidianews.nvidia.com/news/nvidia-rtx-spark-pcs-available-today-a-new-beginning-for-windows-pcs/
  - id: specs
    resource: https://www.nvidia.com/en-us/products/rtx-spark/
status: stable
stale_after: 2026-12-31
---

# RTX Spark 平台定位与上市口径

NVIDIA 中文稿页头为2026-10-15，正文以2026-10-16电头宣布RTX Spark笔记本上市，定位覆盖本地AI、创作与游戏（[F-001、F-019、F-029、F-053](../references/article-source.md)）。两个日期字段不合并，也不猜测时区原因。理解它时需要分开三个对象：CPU/GPU集成的超级芯片、采用该芯片的品牌整机，以及驱动、推理框架和应用组成的软件平台。

## 三个对象

| 对象 | 文章中的对应内容 | 不能直接推出的结论 |
|---|---|---|
| 超级芯片 | Grace CPU、Blackwell RTX GPU、统一内存、FP4 指标 | 每台整机都有最高配置 |
| OEM 整机 | 不同品牌、尺寸、内存及市场报价 | 各地区同名型号配置相同 |
| 软件平台 | CUDA、TensorRT、智能体、创作应用、游戏集成 | 所有 x86 软件与插件无需移植 |

第一行依据 F-006~F-014，第二行依据 F-002~F-005、F-059~F-061，第三行依据 F-019~F-025、F-031、F-043~F-051。表中右列是阅读边界，不是额外性能结论。

RTX Spark 与 DGX Spark 不应因名称相近而合并。PAIR 官方页面将两者分别列为设备类型（F-027）；本包只处理 RTX Spark Windows PC，不拿另一产品的操作系统、内存带宽或安装命令填补本产品资料。

## 上市与支持的时间轴

| 时间 | 事件 | 证据范围 |
|---|---|---|
| 2025-04-23 | 微软公布 Windows Arm64 原生 PyTorch 2.7，示例走 CPU | F-044，历史背景 |
| 2026-10-15 | 中文稿页头日期；Adobe发布RTX Spark应用优化合作公告 | F-001、F-033，来源日期字段分开 |
| 2026-10-16 | NVIDIA 中文稿宣布笔记本上市 | F-001 |
| 2026-10 月底 | 中文稿预告万兴喵影支持 | F-036，计划而非已验收 |
| 2026-11 | NVIDIA 开发稿预告紧凑桌面 | F-012，未来计划 |

“今日”“本月底”“随后”均需锚定原文时点，不能在转载日或读取日自动重置。未补读新 release notes 前，本包不会把预计上市或测试版自动升级成正式可用。

## 中国与全球资料

中文稿列华硕、戴尔、联想、微软、微星五个品牌；英文稿另列 HP。这是发布范围差异，不能据中文列表断言全球没有 HP（F-002~F-003）。两稿还分别采用 YOGA Pro 15 RTX Spark 与 Yoga Pro 9n 等命名，不足以建立一一对应的 SKU 映射（F-059~F-060）。

人民币 18,999 元与美元 2,599 元均是各自稿件的起价，Surface OEM 页面则显示 2,599.99 美元（F-004~F-005）。币种、含税规则、配置和销售时点不同，本包不换汇生成“价差”，也不把起价与 128 GB 顶配绑定。

## 学习方向

先读[统一内存与算力](01-memory-and-compute.md)，判断模型能否容纳、指标采用何种精度；再读[智能体与权限](02-agents-and-routing.md)和[原生开发栈](03-windows-arm-development.md)，区分本地模型、工具执行与软件移植。创作者与玩家可分别进入[创作支持状态](04-creation-and-media.md)与[游戏性能口径](05-gaming-and-measurement.md)。
