# QAnything 知识束变更日志

## 2026-09-09 — V 验证修复回合（E1-E4 + 传播面修复 + draft→stable 升级）

**背景**：seven-concepts 方法论 V 阶段 Grep 对抗验证发现 4 处硬错误（E1-E4）及多处传播面，本回合先经 QAnything 源码逐一复核（复核结论：E1-E4 全部属实），再完成修复与升级。

**事实修复（references/facts.md，F 编号不变）**：

| 编号 | 错误 | 原值 | 修正值 | 源码证据 |
|---|---|---|---|---|
| E1 / F-qa-044 | `scripts/` 目录计数 | 共 13 个条目：10 个 Python 脚本 | 共 12 个条目：9 个 Python 脚本、2 个 Shell 脚本、1 个 jpg | `scripts/` 目录实读（entrypoint.sh、memory_usage.sh、weixiaobao.jpg + 9 个 .py） |
| E2 / F-qa-050 | 上传扩展名白名单数量 | 共 12 种 | 共 11 种（`.md/.txt/.pptx/.jpg/.jpeg/.png/.docx/.xlsx/.eml/.csv/.pdf`） | `scripts/multi_upload_files.py:10` |
| E3 / F-qa-010 | chunk_overlap 归属 | chunk_overlap 为 parent 尺寸的 1/4 | parent 块 chunk_overlap=0、child 块 chunk_overlap 为 child 尺寸的 1/4（默认 100） | `qanything_kernel/core/retriever/parent_retriever.py` L167/L194（parent=0）、L174/L200（child=int(child/4)） |
| E4 / F-qa-046 | 软链接组数 | 为 4 组模型目录创建软链接 | 以 `ln -s` 为 5 处模型/数据目录创建软链接（新增 nltk_data→仓库根） | `scripts/entrypoint.sh` L38/L42/L46/L50/L54 |

**传播面修复**：concepts/01-quick-start.md（L29/L37/L40）、concepts/03-retrieval.md（L31/L33/L64）、concepts/05-dependent-servers.md（L68）、examples/kb-upload-and-retrieval.md（L33/L63/L80）、references/insights.md（L35/L39/L41）。修复后全束 Grep 复查（`13 个条目|10 个 Python|共 12 种|overlap 200|overlap=parent|parent 尺寸的 1/4|parent/4|4 组模型目录`）零残留。

**升级动作**：

1. 11 篇内容文档（concepts 8 + examples 3）frontmatter `status: draft` → `status: stable`；
2. 上述文档及 references/ 三篇（facts/insights/sources）`verified` 更新为 2026-09-09、`stale_after` 顺延为 2027-09-09；
3. 束根 `index.md`「status 判定依据」条目改写为 stable 措辞（含本修复回合说明）；
4. 本日志条目补记。

**备注**：任务书所给信源路径 `d:\AI\.chaos\libs\netease-youdao\QAnything\` 不存在，实际信源为 vendor 子模块 `d:\AI\vendor\netease-youdao\QAnything\`（基线一致：v2.0.0 后 HEAD @ 615417a）；`multi_upload_files.py` 实际位于 `scripts/` 而非 `qanything_kernel/utils/`。此外按「以实际磁盘内容为准」原则，超额修复了任务书未列出的 3 处同源错误（03-retrieval L33/L64、insights L39、kb-upload L80）。
