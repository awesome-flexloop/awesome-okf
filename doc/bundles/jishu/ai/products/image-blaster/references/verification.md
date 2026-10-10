---
type: Reference
title: image-blaster P0 核验记录（verification）
description: 关键声明核验对账、勘误表、核验方法与未覆盖边界
sources:
  - id: github
    resource: https://github.com/neilsonnn/image-blaster
    access_time: "2026-10-10"
generated:
  by: trae-solo-agent
  at: "2026-10-10T12:00:00+08:00"
status: stable
stale_after: "2026-12-10"
---

# P0 核验记录（verification）

## 核验方法

对博文关键声明逐条比对一手来源（GitHub 官方仓库 README、`.claude/skills/` 目录实测、仓库统计）与多家第三方评测（imageblaster.net、marble3dai、traictory、tosea.ai、vp-land，仅作方向佐证，不作裁决源）。时间戳换算：`ct=1791159720` → 2026-10-05 08:22 +08:00（Asia/Shanghai）。

## P0 断言核验表

| # | 声明（来源） | 独立核验源 | 核验结果 | 状态 |
|---|---|---|---|---|
| 1 | 仓库存在：github.com/neilsonnn/image-blaster（F-030） | GitHub 官方页面 | 存在，公开，MIT，TypeScript 71.5% | ✅ |
| 2 | 作者为 World Labs 团队成员（F-004） | GitHub neilsonnn + marble3dai（Nicholas Neilson） | GitHub 显示 neilsonnn(Neilson K-S) 与 World Labs；marble3dai 称 Nicholas Neilson；博文称 Neilson Koerner-Safrata | ⚠️ 姓名三源不一致，Team 归属 Ze up |
| 3 | Star 数 6.9K+（F-010） | GitHub 统计（核验日 2026-10-10） | 实测 2.7k | ⚠️ 显著差异（未知博文时点/夸大） |
| 4 | 5 分钟内从图到可漫游环境（F-012） | README `< 5 minutes` | 一致 | ✅ |
| 5 | 三类输出：spz 环境 / glb,obj 动态物体 / mp3 音效（F-007/8/9） | README Description + Advanced | 一致 | ✅ |
| 6 | 8 个 skill 串联（F-014/15） | `.claude/skills/` 目录实测 | 恰 8 个：project/uncover/plate/world/3d/sfx/image-edit/wildcard | ✅ |
| 7 | 模型编排：marble-1.1 / nano-banana / gpt-image-2 / hunyuan-3d / elevenlabs-sfx（F-007/8/9/17） | README Advanced | 完全一致 | ✅ |
| 8 | Hunyuan 参数（face-count 默认 50000、enable-pbr、generate-type、polygon-type）（F-018~21） | README Advanced | 逐字一致 | ✅ |
| 9 | 安装指令：clone / claude / blast 命令（F-027/29） | README Quickstart | 逐字一致 | ✅ |
| 10 | 需 World Labs + FAL API Key（F-028） | README Quickstart | 一致（README 仅提这两个，ElevenLabs 未列入必需） | ✅（ElevenLabs 部分见勘误 E-1） |
| 11 | 支持 Unity/Unreal/Godot/Blender/Three.js 嵌入（F-006/7） | README Extensions | 一致 | ✅ |

**汇总**：关键断言 8 ✅ / 2 ⚠️ / 0 ❌（⚠️ 为 Star 数与作者姓名口径、ElevenLabs 必需性）。

## 勘误表

| 勘误号 | 博文表述 | 实测/核验 | 分级 |
|---|---|---|---|
| E-1 | Star 数"6.9K+" | 核验时（10-10）实测 **2.7k**。差异可能因博文写作更早或夸大；未形成"撰写时点即为 6.9K"判断 | 数据时效（⚠️） |
| E-2 | 作者全名 Neilson Koerner-Safrata | GitHub 显示 neilsonnn（Neilson K-S）；marble3dai 第三方称 Nicholas Neilson | 人名口径（⚠️） |
| E-3 | 需三服务（World/FAL/ElevenLabs）API Key | README Quickstart 仅列 World Labs + FAL；ElevenLabs 出现在 Advanced 模型表（elevenlabs-sfx）但未在必备 Key 清单中 | 必需性未确认（⚠️） |
| E-4 | Node.js >= 18 环境要求 | README 未在头部显式列 Node 版本；博文为作者整理口径 | 未独立确认（⚠️） |

## 未能独立核验的边界

- **真机复现**：未实际执行 `claude` 流水线，无法验证"5 分钟""生产就绪"在真实环境成立。
- **输出兼容性**：`.spz` 在 Unity/Unreal/Three.js 的可加载性、`--enable-pbr` 材质质量未真机评测，仅引作者论断（author_claim）。
- **Hooks 细节**：`SessionStart` 跑 setup-check.sh、`UserPromptSubmit` 监控 input/ 未在仓库逐行确认，按 README/CLAUDE/common 推断。
- **模型能力对比**："Nano Banana 擅长风格化 / gpt-image-2 擅长写实"（F-022）为作者主观评分，无第三方评测裁决，保持观点标注。