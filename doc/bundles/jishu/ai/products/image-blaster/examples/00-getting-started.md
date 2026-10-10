---
type: Tutorial
title: image-blaster 快速上手——从安装到首次 blast
description: 环境要求、四步安装（clone / Claude Code / API Key / blast）与目录组织实操
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

# 快速上手——从安装到首次 blast

> ⚠️ **可复现性门**：本示例步骤经官方 README 逐字比对整理 [F-028][F-030]；本包制作时未实际运行流水线，属于"编排复现"，不构成对输出效果与耗时的独立实测。真机跑通前，将依赖/API Key/模型结果视为需进一步验证项。

## 1. 环境要求

| 依赖 | 版本要求 | 说明 |
|---|---|---|
| Node.js | >= 18 | 运行 Claude Code 的前提 |
| 包管理器 | pnpm / npm | 推荐 pnpm |
| Claude Code | 最新版官方 CLI | 免费 |

[F-027]

## 2. 四步安装

**第一步：克隆仓库**

```bash
git clone https://github.com/neilsonnn/image-blaster
cd image-blaster
```

**第二步：安装 Claude Code**（如尚未安装）

```bash
curl -fsSL https://claude.ai/install.sh | bash
```

**第三步：准备 API Key**

| 服务 | 官网 | 用途 | 费用 |
|---|---|---|---|
| World Labs | https://platform.worldlabs.ai | 3D 环境生成 | Marble 有免费额度，超出按量计费 |
| FAL | https://fal.ai | Hunyuan 3D 建模 + 图片编辑 | 按分钟计费，首次有赠金 |
| ElevenLabs | https://elevenlabs.io | 音效生成 | 有免费 tier |

[F-029]

> ⚠️ **核验提示**：README Quickstart 明确要求的 Key 为 **World Labs + FAL 两个**；ElevenLabs 出现在模型表（`elevenlabs-sfx`）但未列入必备 Key 清单。运行到音效环节如报缺 Key，再单独补 ElevenLabs（见 [verification.md](../references/verification.md) E-3）。

**第四步：启动 Claude，喂它一张图**

把要处理的图片放进 `input/` 目录，然后在项目根目录执行：

```bash
claude
```

进入 Claude 后说：

```
blast it and confirm each step with me
```

按提示把 API Key 告诉 Claude，剩下的交给它 [F-011][F-030]。

## 3. 执行时序（人类在环）

触发后，Claude 将按 8 个 skill 顺序执行，每步停下询问是否继续 [F-015][F-016]：

1. 初始化项目（`image-blast-project`）
2. AI 视觉分析、列出可拆分物体并等待确认（`image-blast-uncover`）
3. 背景擦除（`image-blast-plate`）
4. 环境重建（`image-blast-world`）
5. 物体建模（`image-blast-3d`）—— 可按需调参 [F-018~21]
6. 音效生成（`image-blast-sfx`）
7.（需要时）通用图片编辑 / 扩展模型（`image-blast-image-edit` / `image-blast-wildcard`）

## 4. 产物定位

完成后资产落在 `worlds/<任务名>/`：环境 `.spz`、物体 `objects/{glb,obj}`、音效 `sfx/{ambient,physics}` [F-024][F-033]。

| 用途 | 引用资产 |
|---|---|
| Unity / Unreal / Godot | `.spz` 环境 + `.glb` 物体 + `.mp3` 音效 |
| Blender 二次雕刻 | `objects/glb|obj` |
| Three.js / Electron 预览 | `.spz` 环境（可解锁 React Viewer 预览）[F-025] |

## 5. 已知坑位（来源于核验限）

- **Star 数勿以博文为准**：博文称 6.9K+，核验时 2.7k（数据时效，E-1）。
- **API Key 三者口径**：README 只列 World+FAL，ElevenLabs 为可选环境（E-3）。
- **3D 参数默认值**：`--face-count` 默认 50000，Hunyuan API 默认是 500000，如需电影级资产手动调高 [F-018]。