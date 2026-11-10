# 变更日志

## 2026-11-10

- 依据 Thoughtworks Technology Radar Vol 35（2026-11-04，Trial）的 blip《Coding harness for general-purpose agents》生成知识包。
- 采用七概念 R→I→E→V→C 链路：R 采集 47 条事实 → I 拆六层知识 → E 信源先行生成 → V 四视角审查与机械门禁 → C 原子提交。
- 以四家官方文档核验编程入口与运行时能力：Claude Agent SDK overview/hosting、Codex SDK README/app-server README、OpenCode SDK/server/permissions、Pi SDK/CLI Integration/README。
- 以 Radar Vol 35 首页与同簇 blip 核验评级与主题关系：Agent sandboxing（Adopt）、Managed agents runtime（Trial）、Enterprise harness（Assess）、Harness quality evaluation（Assess）、Agent plugin marketplace（Trial）、Agent Skills（Trial，2026-04）。
- 按操作可复现性两问判定不设 `examples/`：源文为观点型雷达条目，无可照做的安装/配置/代码/实测流程；官方最小调用形状放在概念文档中，仅作形态说明。
- 勘误 E-1：Claude Agent SDK 的“沙箱”属托管/运行时层，“审批”属 permissions 层，正文分层呈现。
- 勘误 E-2：Pi “刻意”把护栏留给扩展是作者措辞；官方可核验的是“minimal, extensible”，默认功能克制。
- 勘误 E-3：Codex SDK 与 app-server 是两条不同入口（stdio JSONL vs JSON-RPC），正文分栏。
- 勘误 E-4：OpenCode 核验时文档为 V1，并给出 V2 入口；正文标注版本边界。
- 事实登记双份比对：`F-001` 至 `F-047` 集合一致、连续无跳号。
- 结构：6 篇概念 + 2 篇 references + index + log；无 examples。
- 索引接入：practice/index.md、jishu/ai/index.md、jishu/index.md、bundles/index.md、doc/index.md 计数同步。
- 机械门禁：check-utf8.py、check-toctrees.py、check-bundles-index.py、check-frontmatter（如可用）逐项执行，结果见 spec review.md。

## CMD-LOG

```text
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=S0 | event=CMD_START | session=sc-20261110-coding-harness | msg=方法论编排开始：Thoughtworks Coding Harness 全面学习并生成 OKF wiki | ctx={"scenario":"knowledge","topic":"coding-harness-general-purpose-agents","depth":"standard"}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=S1 | event=SCENARIO_DETECTED | session=sc-20261110-coding-harness | msg=场景4 知识沉淀（R→I→E→V→C） | ctx={"confidence":"high"}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=S2 | event=CHAIN_SELECTED | session=sc-20261110-coding-harness | msg=链路：R 事实采集 → I 三层拆分 → E 信源先行 → V 对抗审查 → C 原子提交
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=S3 | event=CONCEPT_COMPLETED | session=sc-20261110-coding-harness | msg=R 完成：47 条事实；P0 覆盖发布信息/四入口/运行时/护栏/相关 blip
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=S4 | event=GATE_PASSED | session=sc-20261110-coding-harness | msg=G1 事实无因果推断词；G2 六篇概念均含现象/机制/边界；G3 结构可迁移；G4 索引与计数收尾
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=S5 | event=CHAIN_COMPLETED | session=sc-20261110-coding-harness | msg=知识包生成完成，待原子提交
```
