---
type: Reference
title: image-blaster 事实清单（facts）
description: F-001~F-035 事实登记——页事实、作者论断与官方核验补充三析分层，逐条可溯源
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

# 事实清单（facts）

> 编号规则：`F-###` 连续编号。`type` 语义：`page_fact`=页面/官方可验证事实；`author_claim`=文章作者的主张/评价/推断；`exec_verified`=本包制作时经官方仓库核验后补充的一手事实。F-001~F-032 来自博文；F-033~F-035 为官方核验补充。

## A. 页事实与作者论断（来源 `wechat`）

| F | claim | type | source_id | 状态 |
|---|---|---|---|---|
| F-001 | 文章标题「6.9K Star！这个开源项目把图像变3D世界的门槛砸得稀碎！」 | page_fact | wechat | verified |
| F-002 | 文章发布时间的 Unix 时间戳 `1791159720`（换算 2026-10-05 08:22 +08:00） | page_fact | wechat | verified |
| F-003 | 副标题/摘要"从一张照片到一个可漫游的3D空间，中间隔了多少行业壁垒？" | page_fact | wechat | verified |
| F-004 | image-blaster 由 World Labs 设计团队成员 Neilson Koerner-Safrata 开发 | author_claim | wechat | partial（GitHub 显示 neilsonnn/Neilson K-S，marble3dai 称 Nicholas Neilson） |
| F-005 | 是运行在 Claude Code 上的「图像到世界」技能集，而非独立桌面/Web 应用 | author_claim | wechat | verified（README 自称 image-to-world skillset） |
| F-006 | 给出图片后可产出一整套可直接进游戏引擎的 3D 资产包 | author_claim | wechat | verified（README "fully meshed 3D environment"） |
| F-007 | 静态环境用 World Labs Marble 生成 3D 高斯泼溅场景（.spz） | author_claim | wechat | verified（README marble-1.1 + .spz） |
| F-008 | 动态物体用腾讯 Hunyuan 3D 生成带 PBR 材质的可编辑 3D 模型（.glb/.obj） | author_claim | wechat | verified（README hunyuan-3d 经 FAL） |
| F-009 | 环境/物体音效用 ElevenLabs SFX 生成（.mp3） | author_claim | wechat | partial（elevenlabs-sfx 在 README，必需性未确认） |
| F-010 | 文章称开源以来 Star 冲到 6.9K+ | author_claim | wechat | ⚠️ 差异（核验时实测 2.7k） |
| F-011 | 开发者只对 Claude 说一句 "blast it and confirm each step with me" | author_claim | wechat | verified（README 同名指令） |
| F-012 | 声称约 5 分钟把一张照片变成可漫游 3D 环境 | author_claim | wechat | verified（README "< 5 minutes"） |
| F-013 | "术业有专攻"的多模型编排思路优于"无所不能的大一统模型" | author_claim | wechat | 观点（P2 单源） |
| F-014 | 8 个 Claude Code skills 严格顺序串联 | author_claim | wechat | verified（仓库 8 个 skill 目录） |
| F-015 | 8 个 skill：project/uncover/plate/world/3d/sfx/image-edit/wildcard | author_claim | wechat | verified（.claude/skills/ 目录实测） |
| F-016 | 人类始终在回路里，每生成完一环节 Claude 停下询问是否继续 | author_claim | wechat | 未独立验证（由命令语义推断） |
| F-017 | 背景擦除/图片编辑默认 FAL Nano Banana Pro；可切 GPT-Image-2 | author_claim | wechat | verified（README 默认 nano-banana、备选 gpt-image-2） |
| F-018 | Hunyuan 参数 --face-count 默认 50000（范围 40000~1500000） | author_claim | wechat | verified（README 一致） |
| F-019 | --enable-pbr 默认开启 | author_claim | wechat | verified（README 一致） |
| F-020 | --generate-type 含 Normal/LowPoly/Geometry | author_claim | wechat | verified（README 一致） |
| F-021 | --polygon-type，LowPoly 模式下可选手三角面或四边面 | author_claim | wechat | verified（README 一致） |
| F-022 | Nano Banana 擅长风格化，GPT-Image-2 对写实更精准 | author_claim | wechat | 观点（P2 单源） |
| F-023 | 三种音效：环境循环音、物体交互音、自定义 Prompt 音效 | author_claim | wechat | 部分核验（README 确认 ambient + object physics） |
| F-024 | 输出目录 worlds/<任务名>/{source, plate, environments/spz, objects/{glb,obj}, sfx/{ambient,physics}} | author_claim | wechat | 部分（仓库有 worlds/ 目录，细部未逐一比对） |
| F-025 | 默认附带隐藏的 React Viewer（需改 .claudeignore 解锁）用于浏览器预览 | author_claim | wechat | 部分（仓库含 .claudeignore，未逐一确认） |
| F-026 | Hooks：SessionStart 自动跑 setup-check.sh；UserPromptSubmit 监控 input/ 目录 | author_claim | wechat | 未逐一核验（仓库含 .claude 配置） |
| F-027 | 环境要求：Node.js >= 18、pnpm/npm、最新版 Claude Code 免费 CLI | author_claim | wechat | partial（README 确认需 claude CLI，Node 要求未显） |
| F-028 | 安装四步：git clone / cd / curl -fsSL claude.ai/install.sh / 配 API Key | author_claim | wechat | verified（README Quickstart 一致） |
| F-029 | 需要 World Labs / FAL / ElevenLabs 三个服务 API Key | author_claim | wechat | partial（README 只提 World+FAL，ElevenLabs 未列必需） |
| F-030 | 把图片放进 input/ 目录、claude 中执行 blast 指令驱动全流程 | author_claim | wechat | verified（README 一致） |
| F-031 | 动态/静态物体判断：动态=人类能搬动（拆出建模），静态=搬不动（留背景 Marble 重建） | author_claim | wechat | 观点（作者机制归纳，P2 单源） |
| F-032 | 文末观点：AI 3D 创作土壤已成熟，缺"把模型串起来那根线"，多模型编排或成主流范式 | author_claim | wechat | 观点（P2 单源） |

## B. 官方核验补充（来源 `github`，exec_verified）

| F | claim | type | source_id | 状态 |
|---|---|---|---|---|
| F-033 | 仓库公开存在，主 `neilsonnn`，显示名 Neilson K-S，MIT，1 contributor；TypeScript 71.5% / JavaScript 27.5%；含 .claude/skills、worlds、input、app 等目录 | exec_verified | github | verified |
| F-034 | 最新提交约 2026-05-15，共 72 commits，无 Releases、无 packages | exec_verified | github | verified |
| F-035 | 核验时（2026-10-10）Star 约 2.7k、watching 29、forks 249 | exec_verified | github | verified |

## 统计

- **博文（wechat）**：F-001 ~ F-032 共 32 条
- **官方核验补充（github）**：F-033 ~ F-035 共 3 条
- **合计 35 条**；状态细分见 [verification.md](verification.md)