---
type: Concept
title: "MAI-UI 评估管线：双通道推理、判分与五视图聚合"
description: "evaluation/grounding 的完整链路：CustomQwen3_VL_VLLM_Model 离线批量、eval_local/eval_server 双通道、正负样本判分、5 类指标视图、6 基准统一 ScreenSpot-Pro 格式与 extract_metrics 汇总。"
tags: [MAI-UI, 评估管线, vLLM, ScreenSpot-Pro, 基准测试]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-29T14:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-29T14:00:00+08:00" }
status: stable
stale_after: 2026-12-31
sources:
  - id: mai-ui-facts
    resource: /references/facts.md
    title: MAI-UI 源码事实台账
  - id: mai-ui-sources
    resource: /references/source-registry.md
    title: MAI-UI 信源登记
---

MAI-UI 的评估管线位于 `evaluation/grounding/`，是一条与 `src/` 客户端外壳**相互独立**的代码路径：它用 vLLM 离线批量或 OpenAI 兼容服务两条通道对 6 个 GUI grounding 基准打分。评估 README 声明训练范式沿用 UI-Ins（arXiv:2510.20286，代码 github.com/alibaba/UI-Ins），并针对 MAI-UI 做了适配（F-046）。本篇按"数据统一格式 → 模型封装 → 双通道执行 → 判分 → 五视图聚合 → 汇总导出"六段组织。

## 数据：6 基准统一重排为 ScreenSpot-Pro 格式

`evaluation/grounding/data/` 下有 6 个数据目录（F-048）：

| 目录 | 内容 |
|---|---|
| `ScreenSpot_Pro_data/` | 28 个 json（android_studio_macos、autocad_windows、blender_windows、photoshop_windows、word_macos 等） |
| `ScreenSpot_V2_data/` | desktop/mobile/web 3 个 convert json |
| `OS_G_data/` | OSWorld-G_sspro_format.json |
| `OS_G_Refine_data/` | OSWorld-G_refined_sspro_format.json |
| `MMbench_data/` | MMbench_GUI_sspro_format.json |
| `UI_Vision_data/` | element_grounding_basic/functional/spatial.json |

README 声明 OSWorld-G、MMBench 已重排为 ScreenSpot-Pro 格式（F-048）——所有基准进入同一判分管线的前提。

## 模型封装：CustomQwen3_VL_VLLM_Model

`evaluation/grounding/models/MAI_UI.py` 定义 `class CustomQwen3_VL_VLLM_Model():`（无基类）（F-035）：

- `load_model(self, model_name_or_path="Qwen/Qwen3-VL-30B-A3B-Instruct", max_pixels=99999999)`：用 `vllm.LLM` 加载，`tensor_parallel_size=torch.cuda.device_count()`、`gpu_memory_utilization=0.90`、`max_model_len=32768`、`limit_mm_per_prompt={"image": 1}`、mm_processor_kwargs 的 min_pixels=16*16*4；模块顶部设置 `mp.set_start_method('spawn', force=True)` 与 `os.environ["VLLM_WORKER_MULTIPROC_METHOD"] = "spawn"`（F-035）。
- `set_generation_config(self, **kwargs)` 为空实现（F-035）。

两个推理方法（F-036）：

| 方法 | 采样参数 | resize | point 归一化 |
|---|---|---|---|
| `ground_only_positive(self, instruction, image, use_guide_text=False)` | SamplingParams(temperature=0.0, max_tokens=256) | smart_resize factor=16*2 | `point_x / resized_width` |
| `batch_ground_only_positive(self, instructions, images, use_guide_text=False)` | SamplingParams(temperature=0.01, max_tokens=256) | smart_resize factor=14*2 / min_pixels=28*28 | 固定除以 1000 |

两者均返回 `{"result": "positive", "format": "x1y1x2y2", "raw_response", "bbox": None, "point": None-or-[x,y]}`；`use_guide_text=True` 时在 prompt 后追加 guide_text `"<tool_call>\n{\"name\": \"grounding\", \"arguments\": {\"action\": \"click\", \"coordinate\": ["`（F-036）。

注意评估 prompt 与 `src/prompt.py` 的 `MAI_MOBILE_SYS_PROMPT_GROUNDING` 文本一致，但**末尾追加一行 `## Input instruction`**（F-037）——训练/推理用的 prompt 与评测用的 prompt 并非逐字节相同。

## 双通道执行

**通道一：eval_local.py（vLLM 离线批量）。** 命令行参数（F-038）：`--model_type`（required，build_model 仅支持 "MAI_UI"）、`--model_name_or_path`、`--screenspot_imgs`（required）、`--screenspot_test`（required）、`--task`（默认 "all"）、`--inst_style`（choices: instruction/action/description/all，默认 "instruction"）、`--language`（choices: en/cn/all，默认 "en"）、`--gt_type`（choices: positive/negative/all，默认 "positive"）、`--log_path`（required）、`--use_guide_text`（str_to_bool，默认 True）、`--max_pixels`（默认 2116800）；模块常量 `GT_TYPES = ['positive', 'negative']`、`INSTRUCTION_STYLES = ['instruction', 'action', 'description']`、`LANGUAGES = ['en', 'cn']`、`torch.manual_seed(114514)`（F-038）。

中文指令限制：`lang == "cn"` 时要求 `inst_style == 'instruction'` 且 `gt_type == 'positive'`，否则 raise AttributeError；中文 prompt 取 `task_instance["instruction_cn"]`，英文取 `task_instance["instruction"]`（F-039）。批量推理 batch_size=100，批量失败降级单样本循环，仍失败则填入 `{"result": "positive", "format": "x1y1x2y2", "raw_response": "ERROR", "bbox": None, "point": None}`（F-039）。

**通道二：eval_server.py（OpenAI 兼容服务 + 多线程）。** 参数 `--dataset_dir`(required)、`--image_root`(required)、`--output_file`（默认 ./results.jsonl）、`--server_ip`（默认 localhost）、`--server_port`（默认 8001）、`--model_name`（默认 "MAI-UI-8B"）、`--api_key`（默认 "EMPTY"）、`--num_workers`（默认 16）；用 `ThreadPoolExecutor(max_workers=num_workers)` 并发调用 `client.chat.completions.create`，逐条 JSONL 追加写入（`file_write_lock = threading.Lock()` 保护）；smart_resize max_pixels=6553600、factor=16*2；跑完按 `dataset_source` 聚合打印 accuracy（F-043）。

## 判分逻辑：bbox 归一化点包含（F-040）

- **正样本** `eval_sample_positive_gt`：bbox 除以 `sample["img_size"]` 归一化为 [x1,y1,x2,y2]；`response["point"]` 为 None 记 "wrong_format"；点落在 bbox 矩形内记 "correct"，否则 "wrong"。
- **负样本** `eval_sample_negative_gt`：`response["result"] == "negative"` 记 "correct"，"positive" 记 "wrong"，其余 "wrong_format"——负样本把模型"回答有目标元素"判为 wrong，而非仅统计正样本命中率。
- eval_server.py 同逻辑但错误标签写作 'incorrect'（bbox 用 `case.get('img_size', [ori_width, ori_height])`），坐标按 `related / 1000.0` 归一化再乘原图宽高得到绝对 pred（F-040）。

## 五视图聚合与结果结构

`evaluate(results)` 返回 `{"details": results, "metrics": {"fine_grained", "seeclick_style", "leaderboard_simple_style", "leaderboard_detailed_style", "overall"}}`（F-041）：

| 视图 | 分组键 |
|---|---|
| fine_grained | platform × application × instruction_style × gt_type |
| seeclick_style | platform × instruction_style × gt_type |
| leaderboard_simple_style | group |
| leaderboard_detailed_style | application |
| overall | 全局 |

`calc_metric_for_result_list` 输出 `num_correct_action / num_total / wrong_format_num / action_acc / text_acc / icon_acc`（text/icon 按 ui_type=="text"/"icon" 分桶）（F-041）。output_local 落盘的 JSON 即此结构，details 每条含 id、img_path、group、platform、application、lang、instruction_style、prompt_to_evaluate、gt_type、ui_type、task_filename、pred、raw_response、bbox、correctness 字段；同目录现存 OS_G.json、SSV2.json、MMBench.json、OS_G_Refine.json、SSPro.json、UI_Vision.json 六个结果文件（F-042）。

## 汇总导出与复现口径

`extract_metrics.py` 的 `extract_action_acc_from_json(json_file_path)` 读取 `data['metrics']['overall']` 下的 `action_acc`、`num_correct_action`、`num_total`、`wrong_format_num`；目录中存在 "checkpoint" 开头的文件夹时输出多 checkpoint 对比表 metrics_comparison.xlsx（openpyxl 给每行最高分加红色填充），否则输出 metrics_summary.csv；参数含位置参数 input_directory、`--input -i`、`--output -o`、`--format -f`（xlsx/csv/auto）、`--verbose -v`，无参数时进入交互模式（F-044）。

**评估环境独立**：`evaluation/grounding/requirements.txt` 锁定 `vllm==0.11.0`、`transformers==4.57.0`、`accelerate==1.3.0`、`qwen-vl-utils==0.0.14`、`dashscope==1.23.6`、`openai==2.2.0`、`torch==2.8.0`、`torchvision==0.23.0`、`pillow==10.4.0`、`numpy==1.26.4`、`pandas==2.2.2`，并指定 `--extra-index-url https://pypi.nvidia.com` 与 `https://download.pytorch.org/whl/cu12`——与根 requirements.txt（4 包、openai==2.13.0、Pillow==12.0.0）版本不一致，须单独建环境（F-045）。

**MAI-UI 的必要参数**：README 显式 `--use_guide_text False`（guide text 特性对 MAI-UI 禁用以对齐标准推理模式），环境要求 conda python=3.12、VLLM==0.11.0，示例命令 `--model_name_or_path Tongyi-MAI/MAI-UI-8B --max_pixels 6553600`（F-046）。

**三种评测方式互相印证**：README 附 MAI-UI-8B 结果表（UI-Vision / MMBench-GUI L2 / ScreenSpot-Pro / ScreenSpot-V2 / OSWorld-G / OSWorld-G Refine）——Tech Report 40.7/88.8/65.8/95.2/60.1/68.6、eval locally 40.9/88.9/66.1/95.1/60.9/68.7、eval by vllm api 40.3/88.7/67.0/94.9/61.7/69.5，六个数据集三行差距均 ≤1 点（F-047）。复现分数异常时，先查归一化口径（见 [/concepts/05-prompt-action-space.md](/concepts/05-prompt-action-space.md) 对照表）与 `--use_guide_text False` 是否就位。

## 相关概念

- [/concepts/01-quickstart-installation.md](/concepts/01-quickstart-installation.md)：根依赖与评估依赖两套环境的区分
- [/concepts/03-grounding-agent.md](/concepts/03-grounding-agent.md)：评估 prompt 的同源模板（F-037）
- [/concepts/05-prompt-action-space.md](/concepts/05-prompt-action-space.md)：999/1000 双口径对照表
- [/references/source-registry.md](/references/source-registry.md)：evaluation/ 全部信源文件
- [MobileWorld 评测环境束](../mobile-world/index.md)：端到端导航评测环境（MAI-UI 分数 41.7 的出处环境）
- [MobilePA-Bench 规划基准束](../mobilepa-bench/index.md)：GUI 之外的工具规划维度基准（互补层级）
