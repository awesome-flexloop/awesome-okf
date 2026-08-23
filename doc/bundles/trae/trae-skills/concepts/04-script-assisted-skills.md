---
type: Concept
title: 脚本辅助型技能
description: 脚本辅助型技能在 SKILL.md 指令基础上集成 Python/JS 脚本执行具体操作，适用于外部数据获取、复杂计算、二进制处理等场景。社区中 daily-hot-news（四层数据源热榜抓取）、daily-trend-writer（报告生成）、video-to-keyframes（视频抽帧与关键帧选择）是典型代表。
tags: [trae-skills, script-assisted, python, fetch_news, video-to-keyframes, daily-hot-news]
generated: { by: "reference_agent/trae-cn", at: 2026-04-22T00:00:00+08:00 }
verified: { by: "process:seven-concepts-v", at: 2026-04-22T00:00:00+08:00 }
status: stable
stale_after: 2026-10-22
sources:
  - id: src
    resource: /references/skills-source.md
    title: Trae Skills 源码信源
---

## 脚本辅助型的设计哲学

脚本辅助型技能的核心分工是：**SKILL.md 负责"指挥"，脚本负责"执行"**。

- SKILL.md 决定何时调用脚本、传入什么参数、如何处理输出
- Python/JS 脚本负责完成 Agent 无法仅靠自然语言推理完成的操作：外部数据获取、复杂算法计算、二进制数据处理

关键原则：**脚本应尽可能极简**。能通过 Agent 内置能力（文件读写、Shell 执行、WebFetch）完成的就不要写脚本。脚本的引入是为了弥补 Agent 能力的不足，而非替代 Agent 的推理能力。

## daily-hot-news：四层数据源降级架构

daily-hot-news 是脚本辅助型技能的入门范例，展示了如何优雅地集成 Python 脚本完成外部数据获取任务。

### 技能工作流

```
用户触发（"今日热搜"等关键词）
    ↓
确认需求（平台选择/数量）
    ↓
执行 fetch_news.py 获取数据
    ↓
格式化输出（Markdown 热榜报告）
```

### fetch_news.py 四层数据源设计

fetch_news.py 配置了 4 层数据源优先级，实现高可用的热榜数据抓取：

| 优先级 | 数据源 | API 地址 | 特点 |
|--------|--------|----------|------|
| ①首选 | 韩小韩 API | `api.vvhan.com` | 数据全面、响应快 |
| ②备选 | 60s API | `60s.viki.moe` | 备用数据源 |
| ③备选 | 小众独行 API | `xzdx.top` | 第二备用 |
| ④自建 | DailyHotApi | 环境变量 `DAILY_HOT_API_BASE` | 用户自建实例 |

当高层数据源请求失败时，自动降级到下一层，确保至少有一个数据源可用。

### PLATFORM_CONFIG 配置

脚本通过 `PLATFORM_CONFIG` 字典统一管理 6 个平台的配置：

```python
PLATFORM_CONFIG = {
    "weibo":   {"vvhan_type": "wb", "sixty_s_path": "weibo", ...},
    "baidu":   {"vvhan_type": "bd", "sixty_s_path": "baidu", ...},
    "zhihu":   {"vvhan_type": "zhihu", "sixty_s_path": "zhihu", ...},
    "toutiao": {"vvhan_type": "toutiao", "sixty_s_path": "toutiao", ...},
    "bilibili":{"vvhan_type": "bili", "sixty_s_path": "bilibili", ...},
    "douyin":  {"vvhan_type": "douyin", "sixty_s_path": "douyin", ...},
}
```

每个平台配置包含各数据源的类型标识、平台名称和 emoji 图标。

### 命令行接口

```bash
python fetch_news.py --platforms weibo,baidu,zhihu --top 10 --format json --output result.json
```

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--platforms` | 逗号分隔平台列表 | 全部 6 个平台 |
| `--top` | 每平台条目数 | 10 |
| `--format` | 输出格式（json/markdown） | json |
| `--output` | 输出文件路径 | stdout |

### 热度值格式化

`format_hot_value` 函数将原始热度数值格式化为人类可读形式：
- ≥1 亿：显示"X.X亿"
- ≥1 万：显示"X.X万"
- 其他：显示原始数字

### generate_report.py 报告生成

generate_report.py 将 fetch_news.py 输出的 JSON 数据转换为三种格式：
- **markdown**：标准 Markdown 表格格式
- **text**：纯文本格式
- **html**：渐变背景（#667eea→#764ba2）、圆角卡片、排名圆形色块（金/银/铜色）的精美 HTML 报告

```bash
python generate_report.py --data result.json --format markdown --output report.md
```

### SKILL.md 输出格式约定

SKILL.md 定义了标准的 Markdown 输出格式：
- 标题：`# 🔥 今日全网热榜 | {日期} {时间}`
- 每个平台一个二级标题 + 表格（排名/热搜话题/热度）
- 排名前 3 名使用 🥇🥈🥉 emoji
- 末尾附时间戳和免责声明

## video-to-keyframes：四脚本流水线架构

video-to-keyframes 是更复杂的脚本辅助型技能，通过 4 个 Python 脚本组成完整的视频处理流水线。

### 技能工作流

```
用户提供视频 + 触发词（"抽帧"/"关键帧"/"拆帧"等）
    ↓
检查依赖（Python 3.10+、numpy、opencv-python）
    ↓
一键运行 run_video_workflow.py
    ↓
查看 segments_gallery.html 确认分段合理性
    ↓
查看 gallery.html 挑选 6-12 张关键帧
    ↓
将 cand_id 写入 selected.txt
```

### 四脚本职责划分

| 脚本 | 职责 | 依赖 |
|------|------|------|
| `generate_daily_folder.py` | 生成以当前日期命名的输出文件夹（`%Y-%m-%d` 格式） | Python 标准库 |
| `extract_frames_and_describe.py` | 视频抽帧，计算每帧的清晰度（拉普拉斯方差）、亮度、对比度、饱和度、运动指标 | numpy, opencv-python |
| `select_keyframes.py` | dHash 转场检测、分段、候选帧评分、生成 HTML 画廊页 | numpy, opencv-python |
| `run_video_workflow.py` | 一键编排，依次调用上述脚本，最后生成汇总文件 | numpy, opencv-python |

### extract_frames_and_describe.py 帧分析

该脚本使用 `FrameInfo` dataclass 记录每帧的多维质量指标：

| 字段 | 类型 | 说明 |
|------|------|------|
| `index` | int | 帧序号 |
| `timestamp_s` | float | 时间戳（秒） |
| `file` | str | 帧图片文件名 |
| `width/height` | int | 帧尺寸 |
| `sharpness` | float | 清晰度（拉普拉斯方差） |
| `brightness` | float | 亮度 |
| `contrast` | float | 对比度 |
| `saturation` | float | 饱和度 |
| `motion` | float | 与前帧差均值（运动幅度） |
| `suggested_keep` | bool | 建议保留标记 |
| `description` | str | 中文质量描述 |

命令行参数支持精细控制抽帧行为：
- `--every-seconds`：抽帧间隔（默认 0.5 秒）
- `--max-frames`：最大帧数限制（默认 600）
- `--min-sharpness`：最低清晰度阈值（默认 80.0）
- `--brightness-min/max`：亮度范围过滤（默认 60-200）

输出文件包括：`meta.json`（视频元信息）、`frames.json/csv`（全部帧信息）、`top_keep.json`（按清晰度排序前 30 帧）、`f_*.jpg`（帧图片）。

### select_keyframes.py 关键帧选择算法

这是视频处理的核心脚本，实现了三个关键算法：

**1. dHash 转场检测**

使用差值哈希（dHash，64 位）计算相邻帧的汉明距离：
- 当相邻帧 dHash 汉明距离 ≥ `cut_thr`（默认 22-30）且前后 `stable_window` 窗口内最大距离 ≤ `stable_thr`（默认 10-31）时，判定为转场点
- 过短分段（< `min_seg_len`，默认 1.5-2.0 秒）会被合并

**2. 候选帧评分公式**

`_score` 函数使用加权评分：
```
总分 = 清晰度 × 0.45 + 亮度适中度 × 0.25 + 对比度 × 0.15 + 饱和度 × 0.05 + 低运动 × 0.10
```

清晰度权重最高（0.45），确保选出清晰的帧；低运动权重（0.10）偏好稳定画面。

**3. 输出文件体系**

| 文件 | 内容 |
|------|------|
| `cuts.json` | 转场点列表 |
| `segments.json` | 分段列表（seg_id/start_t/end_t/rep_t/rep_score） |
| `candidates.json/csv` | 候选帧信息 |
| `gallery.html` | 候选帧画廊页（供人工复筛） |
| `segments_gallery.html` | 分段代表帧画廊（先确认分段合理性） |
| `prompt_pack.html` | 复筛+提示词协作页（暗色模式、文件上传、一键复制） |
| `selected.txt` | 空文件，供人工填写选中的 cand_id |

**三个核心 dataclass**：
- `Cand`：候选帧（group_id/cand_id/timestamp_s/src_file/out_file/score/各质量指标/description）
- `Cut`：转场点（index_left/index_right/t_left/t_right/cut_t/dhash_dist）
- `Segment`：分段（seg_id/start_t/end_t/rep_t/rep_file/rep_score/frame_count）

### 一键运行命令

```bash
python .\skills\video-to-keyframes\resources\scripts\run_video_workflow.py "<视频路径>" --day-folder "<当天文件夹>" --every-seconds 0.5 --max-frames 600
```

输出目录结构：
```
<当天文件夹>/
├── _frames_<视频名>_<间隔>/
│   ├── f_*.jpg                    # 候选帧池
│   ├── frames.csv/json            # 全部帧信息
│   ├── top_keep.json              # 清晰度前30帧
│   ├── meta.json                  # 视频元信息
│   └── _keyframe_candidates/
│       ├── cuts.json              # 转场点
│       ├── segments.json          # 分段
│       ├── segments_gallery.html  # 分段画廊（先看）
│       ├── gallery.html           # 候选帧画廊（复筛）
│       ├── candidates.csv/json    # 候选帧数据
│       ├── selected.txt           # 人工选择结果
│       └── prompt_pack.html       # 提示词协作页
└── <视频名>_拆分.txt              # 汇总文件
```

## zopia_ai_skills：API 集成模式

zopia_ai_skills（name: `zopia-api`）展示了另一种脚本辅助模式——不提供本地脚本，而是在 SKILL.md 中详细定义 API 端点和认证流程，指导 Agent 直接通过 HTTP 请求与外部服务交互。

### 认证流程
1. 引导用户访问 `https://zopia.ai/settings/api-tokens` 生成 token
2. Token 格式为 `zopia-xxxxxxxxxxxx`，有效期 30 天
3. 每次请求 header 携带 `Authorization: Bearer <TOKEN>`

### 推荐工作流
Create Project → Save Settings → Multi-turn Agent Chat → View Results

### 核心 API 端点

| 方法 | 路径 | 功能 |
|------|------|------|
| POST | `/api/base/create` | 创建项目（返回 baseId） |
| POST | `/api/base/settings` | 保存设置（locale/style/aspect_ratio 必填） |
| POST | `/api/v1/agent/chat` | Agent 对话（自动调用 screenplay_writer/character_designer/storyboard_artist/video_producer） |
| GET | `/api/base/settings` | 查询设置 |
| GET | `/api/base/list` | 项目列表 |
| GET | `/api/base/{id}` | 项目详情 |
| GET | `/api/billing/getBalance` | 查询积分余额 |

### 会话管理
- 首次调用不传 `session_id`，响应返回 session_id
- 后续调用传入 session_id 继续同一会话
- 同一 session_id 同一时间只能一个请求（409 表示另一个仍在运行）

### 错误码处理
| 码 | 含义 |
|----|------|
| 400 | 参数错误 |
| 401 | 未认证/token 过期 |
| 402 | 积分不足 |
| 403 | 无权限 |
| 404 | 资源不存在 |
| 409 | 会话运行中 |

## 脚本辅助型技能的设计原则

从社区实例总结的设计原则：

1. **标准库优先**：`fetch_news.py` 仅使用 Python 标准库，无需 pip install，降低使用门槛
2. **一键命令**：提供类似 `run_video_workflow.py` 的编排脚本，Agent 只需一条命令即可完成全流程
3. **结构化输出**：脚本输出 JSON/CSV 等结构化数据，由 SKILL.md 指导 Agent 格式化为最终产出
4. **参数有默认值**：所有命令行参数都提供合理默认值，减少 Agent 的决策负担
5. **降级容错**：多数据源设计（如 fetch_news.py 的四层降级）确保脚本健壮
6. **HTML 可视化**：对于需要人工参与复筛的场景（如视频关键帧选择），生成 HTML 画廊页提供可视化界面
7. **SKILL.md 主导**：脚本是工具，SKILL.md 始终是"指挥官"，定义何时调用脚本、如何解释结果

## 相关概念

- [技能分类与模板模式](/concepts/02-skill-categories.md)
- [纯 Prompt 型技能](/concepts/03-prompt-only-skills.md)
- [Workflow 编排型技能](/concepts/05-workflow-skills.md)
- [社区积分机制](/concepts/06-community-points.md)
- [编写自定义 Skill](/concepts/07-write-skill.md)

## 相关内容

- [源码信源索引](/references/skills-source.md)
- [带 Python 脚本的 Skill 示例](/examples/skill-with-python-script.md)
- [社区积分贡献示例](/examples/points-contribution.md)
