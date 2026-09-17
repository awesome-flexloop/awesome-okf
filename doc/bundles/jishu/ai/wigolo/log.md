# wigolo 知识包变更日志

## 2026-09-16 · 初版生成（博文→OKF Bundle）

- **来源**：微信公众号「GHub开源甄选」《零API Key、零费用！这个GitHub开源神器让AI Agent彻底告别"搜索付费焦虑"》（作者小涛，2026-09-15 07:01，3246 字）
- **方法论**：七概念场景 4 知识沉淀链路 R→I→E→V→C，由 blog-article-to-okf-wiki 七阶段执行
- **规模**：13 文件（3 concepts + 3 examples + 2 references + 3 目录 index + 根 index + 本日志）；F 编号事实 55 条（博文 33 + 官方核验 22）

### R（事实采集与核验）

- 微信反爬确定，经 browser_use 子代理在页面跳转前提取 `#js_content` innerText（3246 字，结尾完整）
- 信源距离预判：第三方开源推介号；Benchmark 段识别为厂商自述材料
- P0/P1 核验 18 项（GitHub REST API + main 分支 README/docs/installation/cli）：**14✅ / 4⚠️ / 0❌**
- 4 项 ⚠️：Star 动态时点（博文"三千多" vs 2026-09-16 实测 5,268）、Benchmark 厂商自述性质、`:full` 仅为构建目标、`--limit` vs `--max-results` 参数口径；另将"GitHub Trending"订正为可证实的 Trendshift #79424
- 补正博文两处不完整口径：需 LLM 的是 research/agent/`search format=answer` 三处（非"两个"）；`--agents` 官方 9 目标（博文列 7）

### I（骨架与归属）

- 操作可复现性两问皆"是" → 技术教程类骨架，设 examples/
- 归属：直挂 `jishu/ai/`（单工具博文转化束先例：free-llm-api-roundup/mattpocock-skills/browseract 等），不入 ai-agent 子组、不新建分组

### E（bundle 生成）

- 信源先行：article-source.md → verification.md → concepts → examples → 各级 index
- 全部数字/命令/版本携带 F 编号；curl/docker/环境变量与官方文档逐字一致

### V（对抗审查与机械门禁）

四视角审查采纳并修复：

1. 🔴 魔鬼代言人 → 补充 **AGPL-3.0 采用边界**（修改源码对外提供 SaaS 触发网络开源义务），新增 concepts/02 §5 与 index 采用提示
2. 🟠 老板视角 → 补充**单人维护 Beta 项目供应风险**（owner=User、参数快速迭代，建议锁版本）
3. 🔵 未来视角 → 强化时效与复核安排（stale_after=2026-12-31，复核 Star/Beta→GA/:full/CLI 参数）
4. 链接自检 → 修复 3 处 concepts→examples 相对链接多跳一级（`../../examples/` → `../examples/`）

机械门禁（2026-09-16）：

| 检查项 | 结果 |
|--------|------|
| 双份 F 编号正则核对（facts.md ↔ article-source.md） | ✅ 各 55、F-001~F-055 连续无跳号、集合相等 |
| UTF-8 严格编码 | ✅ `check-utf8.py`：全库 10309 文件有效（含本 bundle） |
| 总索引三角对账 | ✅ 本束计入后按目录树地面真值更新（543→544、jishu 410→411、ai 191→192），`check-bundles-index.py` 复跑通过 |
| toctree 三级完整 | ✅ 本束 4 个 index.md 指令块齐备；建 log.md 后本束唯一断链（log 未建）已消除 |
| 相对链接可达 | ✅ 本束内/跨束链接逐一核对（跨束仅引用已存在的 todesk-ai/browseract/open-code-review/context-optimization） |
| frontmatter 完整 | ✅ okf_version/type/title/description/tags/generated/status/stale_after/sources 齐备，双信源以上 |
| 敏感信息 | ✅ 无家目录绝对路径（Windows 路径以 %USERPROFILE% 表述）、无密钥 |
| 勘误落实 | ✅ 4 项 ⚠️ 正文均呈现官方值并标注博文口径；Benchmark 标"官方自述演示" |

### 并行会话冲突与在途状态登记（重要）

- 生成期间有并行会话在同一 `jishu/ai/index.md` 接入 **loopx、uumit-a2a-marketplace** 等束，发生一次竞争写入（表格行与 `{toctree}` 标记拼接异常、表格中空行），本会话已修复该结构损伤并保留全部并行束条目。
- 同期并行会话将总索引从 538 更新至 543；本会话按 `check-bundles-index.py` 目录树地面真值校正为 **544**（其计数时点漏计本束）。
- `check-toctrees.py` 另报 3 个**非本会话**在途束未完成 toctree 接线（`ai-agent/ai-agent-book/`、`gpt6-astra-usage-guide/`、`llama-cpp-local-inference/`，含 2 个缺失根 index.md）。这些束文件由并行会话创建，本会话遵循最小变更不代接，留待各会话收尾；本束自身 toctree 无遗留问题。
- 既有漂移登记（非本次引入）：`jishu/index.md` 域导航页导语"111 个一级束"与 ai 行"45 束"为历史过期值（实际 411/192），全页计数失真，建议另起任务对账，本会话不扩大变更范围；总索引 mermaid 节点束数已同步为 411。

### C（提交）

- 待原子提交：子模块 awesome-okf-xs（本 bundle 13 文件 + ai/index.md + bundles/index.md）→ 主仓库 spec（wigolo-blog-okf-wiki/）→ 主仓库 gitlink；用户未要求不 push
