# log.md — 变更日志

## 2026-09-16：初始创建与中断恢复（R→I→E→V 全链路）

- **阶段**：R → I → E → V（博文转化七阶段工作流 + 七概念场景 4 知识沉淀编排）。
- **来源**：微信公众号「开源君笔记」文章《121K星的开源神器，本地跑大模型不用显卡了》（2026-07-31 06:56，贵州；原文 https://mp.weixin.qq.com/s/Nml1WTOv-m_P5Hs8hf9CIg）。
- **公开性**：公开可访问，无 code/token/邀请码 → 标准工作流（spec 在主仓库 `.trae/specs/okf-wiki-ecosystem/llama-cpp-local-inference-okf-wiki/`，产出在本子模块）。
- **骨架判定**：不设 `examples/`。操作可复现性两问：Q1 弱是（仅有“下载二进制/server/localhost”口述线索）、Q2 否（无版本、命令、GGUF 文件名、硬件型号、输入输出、benchmark）。
- **事实登记**：47 条 F 编号（F-001 至 F-047），F-001 至 F-037 来自博文（含 11 类作者观点 V 标注），F-038 至 F-047 为权威核验补充；双份登记（spec facts.md ↔ references/article-source.md）编号集合一致。
  - F-047 为 V 阶段独立重抓官方 server 文档时补登（Anthropic Messages 兼容、Function Calling、Reranking、多模态、continuous batching、speculative decoding 与官方 Docker 镜像），已回转双份登记。
- **P0/P1 核验**：11 组声明，✅ 6 组 / ⚠️ 4 组 / ❌ 1 组。
  - ❌ 关键勘误：4GB RAM 常规运行 Q4 7B 且 20–30 tok/s 不能泛化——Q4_K_M 7B 仅权重约 4.3–4.5GB，官方硬件档把 7B–13B 放在 8–16GB RAM；该说法降级为作者单环境轶事（F-044）。
  - ⚠️ 121K Star 为博文发布时点口径，2026-09-16 GitHub API 现值 127,752（F-037/F-038）；“一行 localhost 迁移”需补 /v1 与六项核对（F-046）；质量对比无评测条件（F-045）；树莓派仅限小模型实验（F-043）。
  - V 阶段独立复核：重新请求 GitHub API 与官方 server 文档页，仓库元数据（127,752/MIT/2023-03-10/master/llama.app）与前轮 F-038 逐字一致，server 能力陈述获官方页面再次确认（新增 F-047）。
- **状态**：`stable`。被勘误项是博文的硬件轶事，不推翻“llama.cpp 支持 CPU/本地推理、llama-server 与 OpenAI 兼容接口”的主结论；四条勘误已在根 index 与概念篇落地。
- **归属**：`jishu/ai/llama-cpp-local-inference/`，AI 域独立直挂束，不新建分组。
- **文件**：9 个（root index/log + concepts 4 + references 3），无 examples/。
- **中断恢复说明**：前轮会话完成 spec.md/facts.md 与 references/ 三文件后中断（无根 index/concepts）；本次经幂等检查回读全部既有产物后恢复，未静默覆盖。

## V 阶段机械门禁（2026-09-16 复核完成）

> 直接运行子模块 `scripts/` stdlib 脚本，未经 invoke/invocations，故不声称 `invoke gates.*` 结论。

| 检查项 | 结果 |
|--------|------|
| `scripts/check-bundles-index.py`（束/组/域五面对账） | ✅ 通过：9 域 / 59 组 / 546 束；本束贡献 +1（ai 组导航表与 toctree 已同步，191→194 含并行会话他束，地面真值对账） |
| `scripts/check-utf8.py` | ✅ 通过：10330 个文件均为有效 UTF-8（本束无 BOM、strict roundtrip 无乱码） |
| `scripts/check-toctrees.py` | ✅ **本束 9 文件零问题**（无断链、无孤立、根 index 已接入 ai 组 toctree）；脚本当次报出 14 处问题全部属于他会话在途 WIP（ai-agent/ai-agent-book 缺 log、free-llm-api-hands-on、inurl-unified-token、tencent/workbuddy-sandbox-public-endpoint 缺根 index），按“谁添加谁对账”未代为修改 |
| 双份 F 编号集合 | ✅ 正则提取两边均 47 个编号（F-001~F-047），集合相等、连续无跳号 |
| 相对链接逐验 | ✅ 30 条 Markdown 相对链接全部 Test-Path 可达（含根 index 主题关联 3 条：echobird、tencent/ncnn、containers/ai-lab-recipes） |
| `file:///`/家目录绝对路径 | ✅ 零出现（log 检查表文本中的“file:///”字样为检查项名称，非链接） |
| frontmatter 完整性 | ✅ 根 index/3 概念篇/2 reference 均含 okf_version/type/title/description/tags/generated/status/stale_after/sources；子目录 index 无 frontmatter 且含 toctree（合规） |
| 勘误正文落实 | ✅ 4GB/7B ❌ 在根 index 勘误 1 与 concepts/01 呈现正确值（8–16GB 官方档、4.3–4.5GB 权重）；Star 双时点；观点条目保留 V 标注 |
| 全库 gates | 见上三行 stdlib 脚本结果；未运行 invoke gates.*（环境约定），无谎报 |

## 待办（C 阶段）

- 提交顺序（用户确认后执行）：① 子模块 awesome-okf-xs 内提交（本束 9 文件 + ai 组 index + 总 index）→ ② 主仓库提交 spec（spec.md/facts.md/review.md）→ ③ 主仓库更新子模块指针。
