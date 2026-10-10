---
okf_version: "0.2"
type: concept
title: "安装、使用与风格对比页"
description: "两种安装法、六条可直接复制的提示、风格对比页的决策交互"
sources:
  - id: github-repo
    resource: https://github.com/oil-oil/oil-ui
  - id: blog
    resource: https://mp.weixin.qq.com/s/JqY_1JW1FSMQU3XAQyTRPA
generated:
  by: seven-concepts-cmd+wechat-public-okf
  at: "2026-10-10T00:00:00+08:00"
status: stable
stale_after: 2027-03-31
---

# 安装、使用与风格对比页

## 两种安装方式（F-019 / F-025✅）

**方式一：一行命令**

```bash
npx skills add oil-oil/oil-ui
```

需要 Node.js 18+。此命令从 GitHub 官方仓库拉取 Skill 定义到本地 Agent 环境。

**方式二：自然语言**

不发命令，直接把需求描述给 Agent（Claude Code / Cursor / Codex 等），让它自行发现并应用 oil-ui 方法论。

> 首次使用会触发**版本检查**：Agent 每 10 分钟检查一次是否更新；网络超时 2 秒即跳过；**不会把对话内容上传**；若本机无 Python 只提醒一次不再打扰（F-020 / 见 [03 边界](03-pro-legacy-and-update.md)）。

## 六条可直接复制的提示（examples/ 展开）

以下是经核验可复制的起始提示（完整可执行版见 [examples/00-quickstart-prompts.md](../examples/00-quickstart-prompts.md)）：

1. "先用八步设计法，先认品类，然后给我 3 个拉开差别的设计方向。"
2. "定调性：能量高、完成度高、密度疏松、分量轻、严肃度中等——告诉我每刻度你打算怎么落地。"
3. "从具体的东西出发：用'深空星云 + 玻璃拟态 + 太空站指挥舱'做第一版素材。"
4. "先问首屏给谁看：这是内容页不是说服页，首屏放第一排内容。"
5. "任意两个方向的骨架/字体/色彩/主视觉最多一项相同，先自查再开画。"
6. "做完把 3 个方向全部放同一个对比页里，按电脑和手机两种尺寸截图给我挑。"

## 风格对比页（F-018 / F-006✅）

oil-ui **自带**一个风格对比页（ProfileComparer），把多个设计方向**并排**放进同一页面：

- 每个方向独立成卡，突出"一项差异化"（骨架/字体/色彩/主视觉）。
- 以 **HTML / 图片 / 可运行页**三种形态呈现，方便你在真实尺寸下对比。
- 你的任务是"挑"而不是"从头猜"——对比页让高低立判，决策成本降低。

## 使用流程速览

```
需求 → 认品类/定调性 → 从具体出发 → 首屏定性 → 拉开方向(≥2)
     → 进对比页 → 你挑方向 → 说喜欢/不喜欢哪里 → 以实际画面为准迭代
```

---
**本概念支撑事实**：F-006、F-018、F-019、F-020、F-025。