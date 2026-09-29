---
type: Concept
title: "God's Eye View：公开信号与 3D 地球"
description: "把航班、船舶、卫星、地震和公共摄像头等公开信号放入可探索的浏览器 3D 地球"
tags: [Gods-Eye-View, OSINT, Cesium, 空间数据]
generated: { by: "process:seven-concepts-e", at: "2026-09-20" }
verified: { by: "process:seven-concepts-v", at: "2026-09-20" }
status: flagged
stale_after: 2026-11-30
sources:
  - { id: article, resource: "/references/article-source.md" }
  - { id: github, resource: "https://github.com/bilawalsidhu/gods-eye-view" }
---

# God's Eye View：公开信号与 3D 地球

God's Eye View 把航班、船舶、卫星、地震、摄像头、火点和基础设施等公开信号放入一张浏览器 3D 地球，重点是统一探索界面，而非提供私有卫星或秘密情报。[F-007][F-010]

## 读图时先看状态

同一张地图上的对象不共享一个真实性等级：

- 航班、船舶和地震来自公开数据源，存在刷新间隔和覆盖缺口。
- 卫星位置是基于轨道要素计算的当前位置。
- 交通可能沿真实道路模拟，摄像头位姿可能需要校准。
- 发射回放可能标记为 `RECONSTRUCTED ESTIMATE`。[F-009]

基础图层可免密钥运行，但照片级地图、语音和部分数据服务仍可能需要 key、配额或计费。[F-008] 因此它替代的是“把多个公开源拼成一个工作台”的软件成本，不是消除地图与数据服务成本。

## 风险边界

不要把延迟、估计或模拟图层写成实时观测，也不要仅凭视觉效果推断隐私、军情或现实事件。重要结论必须回到原始数据提供方核查。
