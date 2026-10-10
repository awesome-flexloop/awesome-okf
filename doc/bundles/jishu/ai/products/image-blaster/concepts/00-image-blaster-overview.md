---
type: Concept
title: image-blaster 概述——定位、多模型编排与 8 技能流水线
description: 项目本质、为何选择"专业模型编排"而非大一统模型、流水线结构
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

# 概述——定位、多模型编排与 8 技能流水线

## 1. 它是"什么"与"不是什么"

image-blaster **不是**一个独立的桌面软件或 Web 应用，而是一套**运行在 Claude Code 上的「图像到世界」技能集（skillset）**[F-005]。它由 World Labs 设计团队成员 `neilsonnn`（显示名 Neilson K-S）开发，MIT 开源，语言以 TypeScript 为主（71.5%）、JavaScript 27.5% [F-030][F-004]。

用户需要自己在终端里跑 Claude（`claude` 命令），通过自然语言驱动整个流程。这种"终端 + Agent 技能"的形态带来两个特点：

- **环境无关**：可在任何支持 Claude Code 的环境中使用，也能嵌进自己的开发流水线 [F-005]。
- **编排即产品**：整个项目的"贡献"不在某个模型，而在于**把多个专业模型按正确顺序串起来**的编排逻辑。

## 2. 核心设计理念：多模型编排 vs 大一统模型

市面上很多 AI 3D 工具标榜"全能模型"能搞定一切；image-blaster 的取向**完全相反**——每个环节交给该领域最专业的模型，即"术业有专攻" [F-013]。文章作者认为，这种编排思路比"一个勉强能做但什么都做不好"的大一统模型更靠谱，因为最终得到的资产包**每个输出环节都不拖后腿**。

| 环节 | 对应模型 | 用途 |
|---|---|---|
| 3D 环境重建 | World Labs **Marble 1.1** | 单图可探索环境 |
| 物体 3D 建模 | 腾讯 **Hunyuan 3D**（via FAL） | PBR 材质稳定的可编辑模型 |
| 背景擦除/图片编辑 | **Nano Banana Pro**（默认）/ **GPT-Image-2**（备选） | FAL 生态成熟图像编辑 |
| 音效生成 | **ElevenLabs SFX** | 环境循环音 + 物体交互音 |

[F-007][F-008][F-009][F-017]

> 🧠 **执行者注（机制层，单源假设）**：这是"编排层"范式在创意工具链的落地——AI 图像生成已高度内卷，真正的瓶颈是"图像之后那一步"（把静态图变成可交互、可进引擎的 3D 资产）。image-blaster 用编排层把领域专业模型的"工人"协调起来分步干活（来源：博文作者观点 P2，F-032）。

## 3. 8 个 Skill 串起的流水线

image-blaster 的核心是 8 个 Claude Code skills，按严格顺序串联 [F-014][F-015]：

| 序号 | skill | 作用 |
|---:|---|---|
| 1 | `image-blast-project` | 创建项目目录、初始化状态 |
| 2 | `image-blast-uncover` | AI 视觉分析图像、列出可拆分物体、等待确认 |
| 3 | `image-blast-plate` | 把确认要拆的物体从原图擦除，得到干净背景 |
| 4 | `image-blast-world` | 调用 World Labs API 生成 3D 环境 |
| 5 | `image-blast-3d` | 对每个拆分物体调用 Hunyuan 3D 生成模型 |
| 6 | `image-blast-sfx` | 生成环境音和物体音效 |
| 7 | `image-blast-image-edit` | 通用图像编辑（擦除、裁剪等） |
| 8 | `image-blast-wildcard` | 万能扩展口，可调 FAL 上任何模型 |

（skill 目录实测于仓库 `.claude/skills/`，与博文清单一致 [F-033]）

## 4. 人类始终在回路里

每生成完一个环节，Claude 会停下来询问"要不要继续"，用户可以调整参数、换模型、甚至只跑其中某一步 [F-016]。相比"点一下就等半天然后给你一坨不可编辑内容"的全自动工具，这种**逐步确认**让整个过程可控、可插入人为判断。

## 5. 一次调用示例

把图片放进 `input/` 目录，进入 `claude` 后说一句：

```
blast it and confirm each step with me
```

Claude 会按 8 技能顺序执行，每步停下等待确认 [F-011][F-030]。

---

### 引用的关键事实

[F-004]：World Labs 团队成员开发（人名三源不一致，见 [verification.md](../references/verification.md#勘误表) E-2）<br>
[F-005]：运行在 Claude Code 上的图像到世界技能集<br>
[F-007]：[F-008]：[F-009]：三类输出资产与对应模型<br>
[F-011]：[F-030]：blast 触发指令与流程<br>
[F-013]：多模型编排优于大一统模型的观点<br>
[F-014]：[F-015]：8 个 skills 及清单<br>
[F-016]：人类在环逐步确认机制<br>
[F-017]：图片编辑双模型<br>
[F-033]：仓库结构实测含 .claude/skills 八个技能目录