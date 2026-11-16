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
- 门禁实跑（工作区，2026-11-16）：`check-bundles-index.py` 通过（9 域 / 65 组 / 741 束，frontmatter、计数行、节标题、分组表、toctree 五面一致）；`check-toctrees.py` 通过（零断链、零孤立）；`check-utf8.py` 通过（13,387 个文件均有效 UTF-8）；`check-asset-baseline.py` 因 `git` 不在本机 PATH 而 SKIP（未验证 HEAD 锚定与三处规模数字，未把 SKIP 记成通过）。
- 落包前共用索引出现既存漂移：技术域节标题声明 542 束、目录树实为 543 束（先于本包存在）。接入本包后按目录树地面真值统一为 741 束 / 544 束（技术）/ 305 束（AI）/ 102 束（frameworks）/ 68 束（ai-agent），并同步 README 表与 doc/index.md。
- 包内自审：40 条事实编号连续无缺口、无未定义引用；17 页本地链接 0 断链；facts.md 无因果词（因为/导致/所以/错误）。
- 修正两处自审发现的口径错误：洞察一原写"提示词手册章节为 197 张图的图集"（197 是全文档图数），改为"40 张带词组的图集"；人像写真子项原按合并口径记 8 项，按 ▎ 小标题改为 10 项（护照/签证照、证件寸照、职业照分列），并在场景页补出 31 处 ▎、去重 30 个的口径。
- 包内 Sphinx 限定构建通过：以 `sphinx-build -b html -E -c doc <本包目录> _build/limited` 只摄入本包 17 页，exit 0、17 个页面 HTML 齐全、零 WARNING（跨包链接因限定摄入未参与解析，其正确性由包内自审的 0 断链承担）。
- 全站 Sphinx 构建（`.venv` + `invoke build`）同时启动：读取阶段本包 17 页全部载入且无 WARNING 指向本包路径；因"writing output"阶段耗时过长（4% 时采样），未等到全站写入完成即收尾，故不宣称全站构建通过。

```text
[CMD-LOG] | level=INFO | cmd=lark-doc-to-okf-wiki | step=S0 | event=SCENARIO_DETECTED | session=sc-20261116-seedream55-wiki | msg=私域信源 + 结构兼内容双形态 | ctx={"sensitivity":"private","variant":"content+structure","target":"user-specified"}
[CMD-LOG] | level=INFO | cmd=lark-doc-to-okf-wiki | step=S1 | event=CONCEPT_COMPLETED | session=sc-20261116-seedream55-wiki | msg=正文与评论采集完成 | ctx={"chars":73231,"lines":362,"comments":0}
[CMD-LOG] | level=INFO | cmd=lark-doc-to-okf-wiki | step=S2 | event=CONCEPT_COMPLETED | session=sc-20261116-seedream55-wiki | msg=画板为 0，跳过双源导出 | ctx={"whiteboards":0}
[CMD-LOG] | level=INFO | cmd=lark-doc-to-okf-wiki | step=S4 | event=GATE_PASSED | session=sc-20261116-seedream55-wiki | msg=事实台账 40 条无因果词且可追溯 | ctx={"facts":40,"verified":"40 ✅/⚠️","causal_word":"none"}
[CMD-LOG] | level=INFO | cmd=lark-doc-to-okf-wiki | step=S5 | event=CONCEPT_COMPLETED | session=sc-20261116-seedream55-wiki | msg=七件套落盘 | ctx={"md":17,"concepts":6,"examples":3,"references":3,"assets":0}
```
