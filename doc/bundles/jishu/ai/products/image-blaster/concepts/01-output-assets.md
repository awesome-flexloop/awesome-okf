---
type: Concept
title: image-blaster 输出资产——三类"生产就绪"可进引擎的交付物
description: .spz 静态环境 / .glb/.obj 动态物体 / .mp3 音效，以及输出目录结构与结构化设计
sources:
  - id: wechat
    resource: https://mp.weixin.qq.com/s/uANTnBjmirCavBJb9pNytA
    access_time: "2026-10-10"
  - id: github
    resource: https://github.com/neilsonnn/image-blaster
    access_time: "2026-10-10"
generated:
  by: trae-solo-agent
  at: "2026-10-10T12:00:00+08:00"
status: stable
stale_after: "2026-12-10"
---

# 输出资产——三类"生产就绪"的交付物

## 1. 三类输出资产

默认情况下，image-blaster 会把一张输入图片转换为一套 **三类资产** [F-006][F-007][F-008][F-009]：

| 类型 | 内容 | 格式 | 生产用途 |
|---|---|---|---|
| 静态环境 | World Labs Marble 生成的 3D 高斯泼溅（Gaussian Splatting）场景 | `.spz` | 可在其中自由漫游 |
| 动态物体模型 | 场景中"人类能搬动"的物体，Hunyuan 3D 生成带 PBR 材质的可编辑模型 | `.glb` / `.obj` | 可在 Blender 继续雕刻，或拖进游戏引擎当可交互道具 |
| 音效 | 环境循环音效 + 每个物体的交互音效，ElevenLabs SFX 生成 | `.mp3` | 环境循环音 + 物体交互音，命名规范 |

## 2. "生产就绪"的结构化设计

很多 AI 工具的问题是"生成了但没法直接用在工程里"。image-blaster 一开始就瞄准**可进引擎**的目标 [F-006]：

- **环境 `.spz`**：高斯泼溅，可直接在 Unity / Unreal / Three.js 里加载与漫游 [F-007]。
- **物体 `.glb` / `.obj`**：标准格式 + PBR 材质，能进 Blender 二次雕刻，也能直接当引擎内可交互对象 [F-008]。
- **音效 `.mp3`**：环境循环音 + 物体交互音，按规范命名，可直接挂在游戏逻辑上 [F-009][F-023]。
- **扩展面**：官方声明其资产可嵌入 Unity、Unreal、Godot 等游戏引擎，Blender/3DS Max/Maya 等 DCC，以及 Three.js / Electron 的 Web/桌面应用 [F-006]。默认还附带一个隐藏的 React Viewer（需改 `.claudeignore` 解锁）用于浏览器预览最终效果 [F-025]。

## 3. 输出目录结构

每次 blast 完成后，资产按以下结构整理 [F-024]（仓库含 `worlds/` 目录 [F-033]）：

```
worlds/
└── <任务名>/
    ├── source/          # 原始图片与分析 JSON
    ├── plate/           # 擦除物体后的干净背景图
    ├── environments/
    │   └── spz/         # World Labs 输出的高斯泼溅
    ├── objects/
    │   ├── glb/         # 3D 模型（标准格式）
    │   └── obj/         # 3D 模型（兼容格式）
    └── sfx/
        ├── ambient/     # 环境循环音
        └── physics/     # 物体交互音
```

这种目录设计的目标是**整洁、可预测、好管理** [F-024]，让下游管线能稳定消费。

---

### 引用的关键事实

[F-006]：产出一整套可进游戏引擎的 3D 资产包（含引擎/DCC/Web 嵌入能力）<br>
[F-007]：[F-008]：[F-009]：三类资产与对应模型/格式<br>
[F-023]：三音效输出（环境循环/物体交互/自定义）<br>
[F-024]：输出目录结构<br>
[F-025]：React Viewer（默认隐藏，改 .claudeignore 解锁）<br>
[F-033]：仓库目录实测含 worlds/