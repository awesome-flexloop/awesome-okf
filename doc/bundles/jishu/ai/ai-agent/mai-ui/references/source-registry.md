---
type: Reference
title: "MAI-UI 信源登记"
description: "mai-ui 束全部信源文件清单：伞仓与内层仓库的 README/LICENSE/NOTICE/requirements、src 六文件、evaluation、cookbook、tests 及博客站 stub，逐项登记路径与覆盖事实范围。"
tags: [MAI-UI, 信源登记, 源码]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-29T14:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-29T14:00:00+08:00" }
status: stable
stale_after: 2026-12-31
sources:
  - id: mai-ui-facts
    resource: /references/facts.md
    title: MAI-UI 源码事实台账
---

# MAI-UI 信源登记

本文件登记 mai-ui 束引用的全部信源文件。信源根为本地源码目录 `external/libs/tools/Tongyi-MAI/MAI-UI/MAI-UI`（下表"路径"均相对此根；伞仓 README 位于其上一级）。所有事实编号见 [/references/facts.md](/references/facts.md)。仓库对应的开源地址为 GitHub `Tongyi-MAI/MAI-UI`（技术报告 arXiv:2512.22047，见 F-001）。

## 伞仓层

| 路径 | 性质 | 覆盖事实 | 说明 |
|---|---|---|---|
| `../README.md`（伞仓根，即 `Tongyi-MAI/MAI-UI/README.md`） | Markdown | F-053 | 标题 "MAI-UI × Qwen-UI-Agent"；Projects 章节声明 Qwen-UI-Agent 为 "continuation work of MAI-UI"（arXiv:2607.28227），并列出 `MAI-UI 1.0/` 目录 |

## 内层仓库根文件（MAI-UI/MAI-UI）

| 路径 | 性质 | 覆盖事实 | 说明 |
|---|---|---|---|
| `README.md` | Markdown（已读全文） | F-001、F-004、F-005 | 仓库定位（2B/8B/32B/235B-A22B 家族、HuggingFace 权重、arXiv:2512.22047）；vLLM 0.11.0 部署命令；两个 Agent 的初始化示例 |
| `LICENSE` | Apache-2.0 全文 | F-002 | Apache License Version 2.0 |
| `NOTICE` | 声明文件 | F-002 | 版权 "Alibaba Cloud and its affiliates"；第三方组件 Jinja2/NumPy/OpenAI Python Client/Pillow 及各自许可证 |
| `requirements.txt` | 依赖清单（已读全文） | F-003 | 仅 Jinja2==3.1.6、numpy==2.3.5、openai==2.13.0、Pillow==12.0.0 四包 |
| `.github/workflows/deploy-pages.yml` | CI workflow | F-054 | 仅确认存在，内容未展开 |

## src/ 核心实现（6 文件）

| 路径 | 行数 | 覆盖事实 | 说明 |
|---|---|---|---|
| `src/unified_memory.py` | 69 | F-007、F-008 | `TrajStep` 与 `TrajMemory` 两个 dataclass 的字段定义 |
| `src/base.py` | 137 | F-009、F-010、F-011 | `BaseAgent(ABC)` 抽象契约：predict 签名、6 个只读 property、reset/load_traj/save_traj |
| `src/utils.py` | 66 | F-012 | 5 个图像/坐标工具函数（safe_pil_to_bytes、pil_to_base64、save_screenshot、extract_click_coordinates、draw_clicks_on_image） |
| `src/prompt.py` | 148 | F-013、F-014、F-015、F-016 | 4 个 prompt 模板、10/12 种动作定义、`<thinking>/<tool_call>` 输出协议、21/14 两套 App 列表 |
| `src/mai_grounding_agent.py` | 265 | F-017、F-018、F-019、F-020、F-021、F-022 | 无基类的 MAIGroundingAgent：SCALE_FACTOR=999、parse_grounding_response、predict 签名与 3 次重试、seed=42、双消息结构 |
| `src/mai_naivigation_agent.py` | 593 | F-023~F-034 | 继承 BaseAgent 的 MAIUINaivigationAgent：3 个模块级解析函数、坐标 2/4 值格式、system_prompt 模板切换、history_responses 再合成、_prepare_images 图像窗口、_build_messages 全文本回放、predict 生命周期、reset 覆写 |

## evaluation/ 评估管线

| 路径 | 行数 | 覆盖事实 | 说明 |
|---|---|---|---|
| `evaluation/grounding/models/MAI_UI.py` | 240 | F-035、F-036、F-037 | CustomQwen3_VL_VLLM_Model：vLLM 离线加载、单样本/批量推理方法、guide_text 追加、评估 prompt 尾行 |
| `evaluation/grounding/eval_local.py` | 466 | F-038、F-039、F-040、F-041 | 命令行参数清单、中文指令限制、判分逻辑（正/负样本、wrong_format）、5 类指标视图聚合 |
| `evaluation/grounding/eval_server.py` | 268 | F-037、F-040、F-043 | OpenAI 兼容客户端 + ThreadPoolExecutor 16 线程通道、SYSTEM_PROMPT、`related / 1000.0` 归一化 |
| `evaluation/grounding/extract_metrics.py` | 354 | F-044 | metrics.overall.action_acc 提取、多 checkpoint 对比表输出 |
| `evaluation/grounding/requirements.txt` | — | F-045 | vllm 0.11.0 / transformers 4.57.0 / torch 2.8.0 等 11 包，与根 4 包依赖版本不一致 |
| `evaluation/grounding/README.md` | — | F-046、F-047 | UI-Ins 训练范式声明（arXiv:2510.20286）、`--use_guide_text False` 约定、MAI-UI-8B 三种评测方式结果表 |
| `evaluation/grounding/output_local/OS_G.json`、`SSV2.json`（同目录另 4 个 json） | — | F-042 | 结果 JSON 顶层结构：details + metrics 五子键 |
| `evaluation/grounding/data/`（6 个数据目录） | — | F-048 | ScreenSpot_Pro_data（28 json）/ScreenSpot_V2_data/OS_G_data/OS_G_Refine_data/MMbench_data/UI_Vision_data，统一 ScreenSpot-Pro 格式 |

## cookbook/ 与 tests/

| 路径 | 覆盖事实 | 说明 |
|---|---|---|
| `cookbook/grounding.ipynb`（6 cell） | F-049 | grounding 单图复现：加载示例图 → 建 Agent → predict → extract_click_coordinates → draw_clicks_on_image |
| `cookbook/run_agent.ipynb`（7 cell） | F-050 | navigation 5 张连续截图循环预测、同一实例轨迹累积 |
| `tests/test_mai_navigation_agent.py`（577 行） | F-051、F-052 | _build_messages 10 个用例；mock OpenAI + JSON 基线（output_messages/ 8 个文件） |
| `tests/output_messages/*.json`（8 个） | F-052 | 与用例对应的消息结构基线文件 |
| `resources/example_img/figure1~5.png` | F-006、F-049、F-050 | 两个 notebook 的示例输入图（仅登记，图像内容未解析） |

## 外部博客站（MAI-UI-blog，登记性信源）

> ⚠️ 该站点为项目主页型静态站（对应 facts-websites.md B 部分 F-025~F-040）。其中两篇博客页面为 Notion 重定向 stub（F-036/F-037），**仅登记存在性与 URL 字面标题，正文零引用**；站点 HTML 的模型家族声明、亮点卡与基准表（F-025~F-035）及 leaderboard.json（F-038/F-039）、轨迹视频资产（F-040）按台账登记引用，引用处均注明出处为博客站 HTML 页面。

| 路径/对象 | 覆盖事实 | 说明 |
|---|---|---|
| `site/index.html`（英文主站）与 `site/index_zh_cn.html`（中文版） | F-025、F-026、F-027、F-028、F-029、F-030 | 站点标题 "MAI-UI: Real-World Centric Foundation GUI Agents"、作者/机构署名、资源链接矩阵（Paper/Code/HuggingFace/ModelScope/MobileWorld/Cite）、模型家族声明（2B~235B）、四大 Technical Highlights 卡、七个 section 结构 |
| `site/index.html` 基准表 | F-033、F-034、F-035 | AndroidWorld 成功率表（MAI-UI-235B-A22B 76.7 全表最高）、MobileWorld 表（235B-A22B overall 41.7）、ScreenSpot-Pro 定位表（部分行） |
| `site/Grounding-Blog/index.html` | F-036 | **Notion 重定向 stub**，仅登记：URL 字面标题 "Why your AI Agent keeps misclicking: A Practical Grounding Guide for Frontier Models"；正文未采集、不引用 |
| `site/MobileWorld-Blog-Post/index.html` | F-037 | **Notion 重定向 stub**，仅登记：URL 字面标题 "MobileWorld Update: Can Frontier Models Really Control Your Phone? Evaluating End-to-End Mobile Use"；正文未采集、不引用 |
| `site/leaderboard.json`（118 行） | F-038、F-039 | columns/task_counts/results 13 条；json 无 MAI-UI 条目而 HTML 表含 Ours 组，两信源收录范围不一致，引用须注明出处文件 |
| `site/MobileWorld/trajs/`（17 个 mp4）与 `site/asset/` 配图 | F-040、F-030 | 轨迹视频资产（文件名即模型标识）与 grounding/navigation pipeline 等配图（仅登记存在性） |

## 相关概念

- [/references/facts.md](/references/facts.md)：上述信源对应的 F-001~F-054 事实台账
- [/concepts/00-project-overview.md](/concepts/00-project-overview.md)：仓库定位（引用伞仓与根文件信源）
- [/concepts/06-evaluation-pipeline.md](/concepts/06-evaluation-pipeline.md)：评估管线（引用 evaluation/ 信源）
