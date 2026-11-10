---
type: Reference
title: "仓库信源事实清单（F-035 ~ F-090）"
description: "基于 mini-swe-agent v2.4.6（commit 04d809ce）源码、官方文档与 GitHub API 的逐条事实登记，含实现与 README 的差异"
tags: [信源, 源码, mini-swe-agent, v2.4.6, F编号]
generated: { by: "seven-concepts-cmd/R", at: "2026-11-10T16:40:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-11-10T17:05:00+08:00" }
status: stable
stale_after: 2027-03-31
sources:
  - id: github-mini-swe-agent
    resource: https://github.com/SWE-agent/mini-swe-agent
    title: "SWE-agent/mini-swe-agent 官方仓库"
  - id: repo-commit
    resource: https://github.com/SWE-agent/mini-swe-agent/commit/04d809ceab9df28f9adaed044884180159172930
    title: "本知识包锁定的源码版本（2026-09-03，v2.4.6）"
  - id: github-api
    resource: https://api.github.com/repos/SWE-agent/mini-swe-agent
    title: "GitHub API 仓库元数据快照（2026-11-10）"
---

# 仓库信源事实清单（F-035 ~ F-090）

> 源码路径均相对于 `external/dao/SWE-agent/mini-swe-agent/`（本地浅克隆，不纳入版本控制）。数字均来自 2026-11-10 的实测或时点快照。

| 编号 | 事实或声明 | 来源层级 | 核验 |
|---|---|---|---|
| F-035 | 仓库为 `SWE-agent/mini-swe-agent`，GitHub repo id 1010318950，创建于 2025-06-28T20:18:15Z。 | 官方元数据 | 通过（GitHub API） |
| F-036 | 截至 2026-11-10 的快照：stars 9,496、forks 1,306、open issues 140。 | 官方元数据 | 通过（GitHub API，时点值） |
| F-037 | 仓库许可证为 MIT，主要语言为 Python。 | 官方元数据 | 通过（GitHub API + LICENSE.md） |
| F-038 | 本地浅克隆 HEAD 为 `04d809ceab9df28f9adaed044884180159172930`（2026-09-03），包版本 `2.4.6`。 | 源码 | 通过（`git log` + `__init__.py`） |
| F-039 | README 声明当前为 mini-swe-agent v2，并提供 v2 迁移指南与 v1 分支。 | 官方文档 | 通过（README:17） |
| F-040 | README 的动机句为 “What if our agent was 100x simpler, and still worked nearly as well?”。 | 官方文档 | 通过（README:21） |
| F-041 | README 称使用者包括 Meta、NVIDIA、Essential AI、IBM、Nebius、Anyscale、Princeton University、Stanford University 等。 | 官方文档 | 机构自述（P1 单源，见 F-082） |
| F-042 | README 称在 SWE-bench verified 上得分 >74%，且启动速度远快于 Claude Code。 | 官方文档 | ⚠️ 74% 有 docs 佐证；启动速度无量化基准（F-083） |
| F-043 | README 称支持 local、docker/podman、singularity/apptainer、bubblewrap、contree 等执行环境。 | 官方文档 | 通过（源码 environments/） |
| F-044 | README 称通过 litellm、openrouter、portkey 等支持各类模型，并支持 `/completion` 与 `/response` 端点、interleaved thinking。 | 官方文档 | 通过（模型注册表，见 F-058） |
| F-045 | `pyproject.toml` 作者为 Kilian Lieret、Carlos E. Jimenez；`requires-python = ">=3.10"`；许可证 `LICENSE.md`。 | 源码 | 通过（pyproject） |
| F-046 | 运行时依赖包含 pyyaml、requests、jinja2、pydantic>=2、litellm>=1.75.5、tenacity、rich、python-dotenv、typer、platformdirs、textual、prompt_toolkit、datasets、openai。 | 源码 | 通过（pyproject dependencies） |
| F-047 | 控制台入口为 `mini`、`mini-swe-agent`、`mini-extra`、`mini-e`；分别指向 `run.mini:app` 与 `run.utilities.mini_extra:main`。 | 源码 | 通过（pyproject `[project.scripts]`） |
| F-048 | `AgentConfig` 字段：`step_limit=0`、`cost_limit=3.0`、`wall_time_limit_seconds=0`、`max_consecutive_format_errors=3`、`output_path=None`。 | 源码 | 通过（default.py:19-36） |
| F-049 | `DefaultAgent.run` 初始化 system + user 消息，循环 `step()`，捕获 `FormatError` / `InterruptAgentFlow` / 其它异常，`finally` 每步 `save()`，遇 `role=exit` 退出。 | 源码 | 通过（default.py:88-124） |
| F-050 | `DefaultAgent.step()` 的实现为 `return self.execute_actions(self.query())`。 | 源码 | 通过（default.py:126-128） |
| F-051 | `query()` 在调用模型前检查 step/cost/wall-time 限制，递增 `n_calls`，累计 `cost`，并把模型消息追加进历史。 | 源码 | 通过（default.py:130-152） |
| F-052 | `execute_actions()` 对消息中的每个 action 调用 `env.execute`，再通过 `model.format_observation_messages` 生成观察消息并追加。 | 源码 | 通过（default.py:154-157） |
| F-053 | `FormatError` 发生后仍累计已计费成本；连续格式错误达到 `max_consecutive_format_errors` 时以 `RepeatedFormatError` 退出。 | 源码 | 通过（default.py:99-118） |
| F-054 | `LocalEnvironment.execute` 使用 `subprocess.Popen(shell=True)`，传入 `cwd` 与 `os.environ \| config.env`，默认 30 秒超时；POSIX 超时杀整个进程组。 | 源码 | 通过（local.py:26-80） |
| F-055 | 完成信号为输出首行等于 `COMPLETE_TASK_AND_SUBMIT_FINAL_OUTPUT` 且 returncode=0；其余行作为 submission，并抛出 `Submitted`。 | 源码 | 通过（local.py:45-62） |
| F-056 | `DockerEnvironment` 启动 `docker run -d --name minisweagent-<8hex> -w <cwd> --rm <image> sleep 2h`，通过 `docker exec` 执行命令，默认 30 秒超时、`bash -lc` 解释。 | 源码 | 通过（docker.py:13-90） |
| F-057 | 其他环境类包括 `SingularityEnvironment`、`BubblewrapEnvironment`（Linux、实验性）、`ContreeEnvironment`、`SwerexDockerEnvironment`、`SwerexModalEnvironment`。 | 源码 | 通过（environments/ 与 docs/advanced/environments.md） |
| F-058 | 模型类注册表包含 10 项：litellm、litellm_textbased、litellm_response、openrouter、openrouter_textbased、openrouter_response、portkey、portkey_response、requesty、deterministic。 | 源码 | 通过（models/__init__.py `_MODEL_CLASS_MAPPING`） |
| F-059 | 默认模型类为 `LitellmModel`；名称含 anthropic/sonnet/opus/claude 时默认设置 `set_cache_control="default_end"`。 | 源码 | 通过（models/__init__.py） |
| F-060 | v2 默认使用原生 tool calling：`BASH_TOOL` 定义函数 `bash`，参数对象仅含必填字符串 `command`；`litellm.completion` 调用带 `tools=[BASH_TOOL]`。 | 源码 | 通过（actions_toolcall.py:9-27、litellm_model.py:64-71） |
| F-061 | 文本解析模式仍保留；源码注释称其为 v1.0 与原始 SWE-agent 的方式，并“强烈建议”v2 使用 toolcalls。 | 源码 | 通过（actions_text.py:1-5） |
| F-062 | v2 文本模式默认代码块标记从 ` ```bash ` 改为 ` ```mswea_bash_command `；完成信号从 `MINI_SWE_AGENT_FINAL_OUTPUT` 改为 `COMPLETE_TASK_AND_SUBMIT_FINAL_OUTPUT`。 | 官方文档 | 通过（v2_migration.md） |
| F-063 | 默认 `mini.yaml`：`step_limit: 0`、`cost_limit: 3.`、`mode: confirm`；system prompt 仅一句“You are a helpful assistant that can interact with a computer.”。 | 源码 | 通过（config/mini.yaml） |
| F-064 | 观察模板对输出做截断：少于 10,000 字符全量返回；否则返回前 5,000 + 后 5,000 字符，并给出 `elided_chars`。 | 源码 | 通过（config/mini.yaml、default.yaml） |
| F-065 | `mini` CLI 支持 `-t/--task`、`-c/--config`、`-m/--model`、`-y/--yolo`；运行模式为 confirm、yolo、human，可在运行中用 `/c`、`/y`、`/u` 切换。 | 官方文档 | 通过（docs/usage/mini.md） |
| F-066 | `InteractiveAgentConfig` 提供 `mode`、`whitelist_actions`、`confirm_exit`；`InteractiveAgent` 在消息追加时打印 step 与累计成本。 | 源码 | 通过（interactive.py:20-60） |
| F-067 | Python 嵌入方式为 `DefaultAgent(get_model(input_model_name=...), LocalEnvironment())`，然后 `agent.run(task)`。 | 官方文档 | 通过（docs/usage/python_bindings.md） |
| F-068 | SWE-bench 批处理命令为 `mini-extra swebench --model <model> --subset verified --split test --workers 4`，输出预测文件（preds.json）。 | 官方文档 | 通过（docs/usage/swebench.md） |
| F-069 | SWE-bench 单实例调试命令为 `mini-extra swebench-single --subset verified --split test -i sympy__sympy-15599`。 | 官方文档 | 通过（docs/usage/swebench.md） |
| F-070 | 官方 docs 首页声明 “Scores >74% on the SWE-bench verified benchmark”，并在 News 中记录 “Nov 19: Gemini 3 Pro reaches 74% on SWE-bench verified with mini-swe-agent!”。 | 官方文档 | 通过（docs/index.md:35、:216） |
| F-071 | 官方 docs News 另记录 “Aug 19: Randomly switching between GPT-5 and Sonnet 4 boosts performance”。 | 官方文档 | 通过（docs/index.md） |
| F-072 | FAQ 列出的默认限制：bash 以外无工具；文本模式从三反引号块解析；动作由 `subprocess.run` 独立执行；不能持久 `cd` 或 `export`，但可按动作设置环境变量。 | 官方文档 | 通过（docs/faq.md:39-50） |
| F-073 | FAQ 解释“为何不用 shell session”的三条理由：命令终止难以判定、坏命令可能杀死会话、中断会污染后续输出。 | 官方文档 | 通过（docs/faq.md:103-121） |
| F-074 | 轨迹序列化格式为 `mini-swe-agent-1.1`，包含 `info.model_stats`、`info.config`、`info.mini_version`、`info.exit_status`、`info.submission` 与完整 `messages`。 | 源码 | 通过（default.py:159-180） |
| F-075 | 代码规模实测：`src/` 下 59 个 `.py`、共 4,531 行；`default.py` 172 行、`local.py` 80 行、`litellm_model.py` 147 行、`run/mini.py` 86 行。 | 源码 | 通过（本机计数） |
| F-076 | 测试规模：`tests/` 下 56 个文件，`def test_` 共 460 处。 | 源码 | 通过（本机计数） |
| F-077 | 文档站为 mkdocs，覆盖 quickstart、usage（mini/swebench/inspector/output_files/python_bindings）、advanced（control_flow/cookbook/environments/global_configuration/v2_migration/yaml_configuration）与 reference（agents/environments/models/run）。 | 官方文档 | 通过（docs/ 目录树） |
| F-078 | README 与 FAQ 仍称“不需要 tool-calling 接口”，但 v2 默认实现正是 tool calling，构成文档滞后/自相矛盾。 | 源码+官方文档 | 通过（README:42、faq.md:46 vs litellm_model.py:69） |
| F-079 | README 的“100 lines”为概数；`default.py` 实际 172 行（含注释、空行与序列化方法），核心 `run/step/query/execute_actions` 约 100 行。 | 源码 | 口径说明（非错误） |
| F-080 | 官方示例模型为 `anthropic/claude-sonnet-4-5-20250929`，通过 litellm 调用。 | 官方文档 | 通过（python_bindings.md、cookbook.md） |
| F-081 | `pyproject.toml` 显式排除 litellm 1.82.7/1.82.8（安全原因）与 openai 1.100.0/1.100.1（issue #446）。 | 源码 | 通过（pyproject） |
| F-082 | README 的采用者名单为机构自述，仓库内无对应案例或授权证明。 | 官方文档 | 单源（P1） |
| F-083 | README “starts much faster than Claude Code” 未给出启动时间、硬件、版本或测量方法。 | 官方文档 | 单源（P1） |
| F-084 | 博客“26k+ Stars”与 GitHub API 的 9,496 不符，差异 16,504，属硬错误。 | 核验 | ❌ E-1 |
| F-085 | 博客“2024 年发布 SWE-bench”与 arXiv 2310.06770 的提交日期 2023-10-10 不符；SWE-agent 论文为 arXiv 2405.15793（2024）。 | 核验 | ❌ E-2 |
| F-086 | 博客快速开始中的 `MiniSWEAgent` 类、`result.passed`、`result.patch` 在 v2.4.6 源码中不存在；真实入口为 `DefaultAgent`，`run()` 返回 `exit_status`/`submission` 等字典。 | 核验 | ❌ E-3 |
| F-087 | 博客“没有工具/不需要 tool-calling”只适用于 v1 与 v2 的 textbased 模式；v2 默认 `mini.yaml` 与 `LitellmModel` 使用 bash tool call。 | 核验 | ❌ E-4（版本边界） |
| F-088 | 74% 与官方 docs 一致，但官方未公开该成绩对应的完整评测配置（模型快照、成本上限、重试/步数、容器架构）。 | 核验 | ⚠️ 口径边界 |
| F-089 | 博客表中的 Claude 3.7 Sonnet 65%、GPT-4o 42%、SWE-agent 1.0 54% 未在官方 docs 页面逐项复核。 | 核验 | 单源 |
| F-090 | 知乎链接 `https://zhuanlan.zhihu.com/p/2011860096536314782` 在 2026-11-10 三次抓取均失败（zhuanlan 403、API 40362、www 404），未使用其内容。 | 核验 | 信源缺口 |

```{toctree}
:hidden:
:maxdepth: 3

../blog-source
../verification
```
