# 更新历史

## 2026-11-16

- 用户给出企业域飞书 docx，要求"全面学习并生成 OKF wiki 教程"。按 `lark-doc-to-okf-wiki` 流程执行：敏感度预检 → 采集 → 事实台账 → 七件套 → 门禁。
- 采集：`lark-cli docs +fetch --doc-format markdown`，document_id `HkvNdjRwIoK4DcxHThicjQS3nig`、revision_id 3367、正文 73,231 字符 / 362 行；另取两级标题大纲。
- 该文档无画板（0 个 whiteboard 块）、无评论（reference_map 无 comments），故跳过画板判读与评论 sidecar 环节；信息全部来自正文文字与示例图的 alt/caption。
- 图片未入库：正文 197 张示例图一张未复制，理由与代价记录在信源登记（授权未明、体量超预算、教程需要的是提示词写法而非图本身）。
- 事实台账建 40 条（F-001—F-040），全部 ✅ 或 ⚠️，无 📐/💬 条目；计数核对表由正则与字面匹配机械得出，标题 14、图 197、提示词 44、表格 35、grid 80。
- 口径处理：95% 小字准确率与词条无定义两项标 ⚠️，保留原文数字不做替换；三条洞察写进根索引，均给证据与反常识面。
- 落位判定：与既有 `doubao-work*` 家族同处 `jishu/ai/frameworks/ai-agent/`，便于从豆包工作族横向跳转；未放入 `models`（该组面向模型技术分析，非使用教程）。
- 本包含 17 个 Markdown（根 2 + concepts 7 + examples 4 + references 4），无二进制素材。

```text
[CMD-LOG] | level=INFO | cmd=lark-doc-to-okf-wiki | step=S0 | event=SCENARIO_DETECTED | session=sc-20261116-seedream55-wiki | msg=私域信源 + 结构兼内容双形态 | ctx={"sensitivity":"private","variant":"content+structure","target":"user-specified"}
[CMD-LOG] | level=INFO | cmd=lark-doc-to-okf-wiki | step=S1 | event=CONCEPT_COMPLETED | session=sc-20261116-seedream55-wiki | msg=正文与评论采集完成 | ctx={"chars":73231,"lines":362,"comments":0}
[CMD-LOG] | level=INFO | cmd=lark-doc-to-okf-wiki | step=S2 | event=CONCEPT_COMPLETED | session=sc-20261116-seedream55-wiki | msg=画板为 0，跳过双源导出 | ctx={"whiteboards":0}
[CMD-LOG] | level=INFO | cmd=lark-doc-to-okf-wiki | step=S4 | event=GATE_PASSED | session=sc-20261116-seedream55-wiki | msg=事实台账 40 条无因果词且可追溯 | ctx={"facts":40,"verified":"40 ✅/⚠️","causal_word":"none"}
[CMD-LOG] | level=INFO | cmd=lark-doc-to-okf-wiki | step=S5 | event=CONCEPT_COMPLETED | session=sc-20261116-seedream55-wiki | msg=七件套落盘 | ctx={"md":17,"concepts":6,"examples":3,"references":3,"assets":0}
```
