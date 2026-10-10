---
type: Concept
title: image-blaster 技术架构——动态/静态拆分、Hunyuan 参数、图片双模型、Hooks 自动化
description: 端到端技术栈、物体识别判据、3D 参数可调面、音频三形态与自动化钩子
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

# 技术架构——拆分判据、参数与自动化

## 1. 端到端技术栈

```
用户输入 → Claude Code（终端）
    ↓
image-blast-project（初始化）
    ↓
image-blast-uncover（AI 视觉分析）→ 用户确认物体列表
    ↓
image-blast-plate（背景擦除）→ FAL: nano-banana / gpt-image-2
    ↓
image-blast-world（环境重建）→ World Labs: marble-1.1
    ↓
image-blast-3d（物体建模）→ FAL: hunyuan-3d
    ↓
image-blast-sfx（音效生成）→ ElevenLabs: elevenlabs-sfx
    ↓
输出资产包（worlds/<任务名>/）
```

[F-007][F-008][F-017][F-015]

## 2. 动态/静态物体的判断标准

image-blaster 在分析图像时把物体分成两类 [F-031]：

| 类型 | 判据 | 处理 |
|---|---|---|
| **动态物体** | "人类能搬动"的东西——桌上的杯子、街角的自动贩卖机、墙边的梯子 | 拆出来单独生成 3D 模型（Hunyuan 3D） |
| **静态环境** | "人类搬不动"的东西——地面涂鸦、墙上壁纸、地板地毯 | 留在背景里，由 Marble 整体重建 |

这个判断标准**朴素但有效**：它保证了拆出的物体都是"可交互"的（可拿起来、可移动位置），同时静态部分由 Marble 整体重建，维持空间关系一致性。

## 3. Hunyuan 3D 参数可调面

对 3D 模型生成环节，image-blaster 暴露了若干关键参数（默认值已够用，高级玩家可调）[F-018][F-019][F-020][F-021]：

| 参数 | 选项/默认 | 用途 |
|---|---|---|
| `--face-count` | 40,000~1,500,000，**默认 50,000** | 面数；实时游戏用低面数，电影级资产拉高到几十万面 |
| `--enable-pbr` | **默认开启** | 生成带金属度/粗糙度贴图的 PBR 物理渲染材质 |
| `--generate-type` | Normal（带贴图）/ LowPoly（低多边形简化）/ Geometry（纯几何白模） | 生成类型 |
| `--polygon-type` | triangle / quadrilateral | 三角面或四边面（LowPoly 模式下可选） |

## 4. 图片编辑的"双保险"

默认用 FAL 的 **Nano Banana Pro** 做图片擦除和清理；不满意时对 Claude 说 `Use gpt-image-2 for edits` 即切换到 OpenAI 的 **GPT-Image-2** [F-017]。作者观点：Nano Banana 对风格化图像更好，GPT-Image-2 对写实照片更精准 [F-022]。

## 5. 三种音效输出

`image-blast-sfx` 生成三类音效 [F-023]：

1. **环境循环音（Ambient Loops）**：整个场景背景音（咖啡馆喧闹、森林鸟叫风声），自动拼接成无缝循环。
2. **物体交互音（Physics SFX）**：每个动态物体专属交互音（拿起杯子的"咔哒"、贩卖机出货的"叮咚"）。
3. **自定义音效（Custom Prompt-based）**：可对 Claude 说"给这把椅子加个摇晃的吱呀声"，用 ElevenLabs 生成。

## 6. Hooks 机制：自动化细节

image-blaster 利用 Claude Code 的 Hooks 系统做了两类贴心自动化 [F-026]：

- **SessionStart Hook**：每次启动 Claude 时自动跑 `setup-check.sh`，检查依赖与 API Key 是否配置好。
- **UserPromptSubmit Hook**：监控 `input/` 目录，一旦发现新图片就自动进入待处理状态。

## 7. 设计评价（作者观点）

作者在文末指出：image-blaster 本质是 World Labs 设计师业余时间写的 TypeScript 代码，开源后爆火。其示范意义在于——**AI 3D 创作的土壤已经成熟，缺的是把各个模型串起来的那根线**；"多个专业模型 + 一个靠谱编排层"可能成为下一阶段 AI 创作工具的主流范式 [F-032]。（该段为博文作者推断，属观点层 P2 单源。）

---

### 引用的关键事实

[F-007]：[F-008]：环境/物体对应的模型与格式<br>
[F-015]：8 个 skills 流水线<br>
[F-017]：图片编辑双模型（nano-banana 默认 / gpt-image-2 备选）<br>
[F-018]：[F-019]：[F-020]：[F-021]：Hunyuan 3D 参数<br>
[F-022]：Nano Banana vs GPT-Image-2 风格偏好的观点<br>
[F-023]：三种音效输出<br>
[F-026]：Hooks 自动化（SessionStart / UserPromptSubmit）<br>
[F-031]：动态/静态物体判断标准<br>
[F-032]：文末"多模型编排是主流范式"的观点