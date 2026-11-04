# 示例 00：安装与三步实操

> 对应事实：F-023、F-024、F-029~F-032、F-039
> 前置：已选定宿主并确认 Python 3.10+ 可用

## 安装

### 方式 A：包管理器下载 ZIP（推荐，官方分发方式）

1. 下载 `learn-from-materials-1.1.0.zip`
2. 解压得到 `learn-from-materials/` 文件夹
3. 把**整个文件夹**放入宿主的 Skill 搜索目录（见下表）

| 宿主 | 用户级 Skill 目录 |
|------|-------------------|
| WorkBuddy | `~/.workbuddy/skills/` |
| Codex | `~/.agents/skills/` |
| Claude Code | `~/.claude/skills/` |
| GitHub Copilot CLI | `~/.copilot/skills/` 或 `~/.agents/skills/` |

安装后的目录形态（**顶层须直接含四项**，避免多套一层）：

```
~/.claude/skills/learn-from-materials/
├── SKILL.md
├── scripts/
├── references/
└── templates/
```

> ⚠️ **最常见的安装失败**：解压后多套了一层目录（如 `learn-from-materials/learn-from-materials/SKILL.md`），宿主扫不到 `SKILL.md`。

### 方式 B：git clone

```bash
git clone https://github.com/dmoshehun-prog/learn-from-materials.git
```

然后同样把目录放到上述 Skill 目录下（或直接 clone 到该目录内）。

### 方式 C：一句话让 Agent 自己装（原文用法）

原文作者采用的正是这种方式——在宿主任务里发一句话，由 Agent 完成安装（F-023）。

## 三步实操（原文流程，逐字提示词）

> 以下三步为原文作者在**豆包工作**中的一手操作记录（F-023/025/026/027 为单源登记）。宿主不同则界面路径不同，但**交互范式一致**。

### 第一步：装技能

打开宿主，新建一个工作任务，**选好存放材料的本地文件夹**，然后发一句话（**原文逐字**）：

```
帮我安装 GitHub 上 dmoshehun-prog 的 learn-from-materials 技能，装好之后用大白话告诉我它能做什么、怎么用。
```

装完后宿主会给出安装结果，并解释这个技能的用法。

### 第二步：把材料变成学习网页

先把 PDF 放进**任务对应的本地文件夹**，让它用这个技能做一次快速概览。提示词参考（**原文逐字**，F-024）：

```
请用 learn-from-materials 对这份 PDF 做一次快速概览，生成中文学习网页。整理核心观点和术语解释，保留原文页码，区分报告内容与模型补充。
```

任务完成后得到一个 **HTML 文件**，直接点开即可在宿主的内置浏览器里预览。

### 第三步：生成链接分享

在内置浏览器里点击右上角**「分享」→「生成链接」**，得到可访问的网页链接（F-027）；复制链接发给同事或朋友，对方打开即可查看。

## 手动 CLI 链（排查 / 复现用）

在 Skill 根目录运行（F-039）：

```bash
python extract.py                 # 提取材料 + 能力检查
python methods.py bind            # 绑定方法候选
python methodology.py bind        # 绑定方法论候选
python prepare_quick.py           # 快速了解路径预备
python pipeline.py assemble       # 组装页面数据
python render_page.py             # 渲染单文件 HTML
python finalize.py                # 绑定 + 核验 + 打包交付
```

## 常见问题

| 现象 | 排查方向 |
|------|----------|
| 宿主说找不到技能 | 检查 Skill 目录层级，`SKILL.md` 是否在**顶层** |
| 提取阶段报缺依赖 | 该格式需要可选依赖（如 MOBI 需 Calibre `ebook-convert`，**无内置回退**） |
| 扫描 PDF 内容缺失 | 需 OCR/视觉能力；缺失时对应范围被标记为**未核验** |
| 长书生成质量不稳 | 换用长上下文、高推理能力模型（F-038） |

## 下一步

阅读 [示例 01：产出与分享](01-output-and-sharing.md)，了解六板块怎么读、如何分享。
