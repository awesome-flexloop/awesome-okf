---
type: Reference
title: "贡献者表格生成脚本信源"
description: "docs/scripts/gen_contributors.py 与 docs/_static/custom.css 的核心逻辑摘录，包含YAML→HTML表格自动生成机制。"
tags: [reference, contributors, automation, python, yaml, html]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T12:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T12:00:00Z" }
status: stable
stale_after: "2027-08-22"
sources:
  - id: gen-script
    resource: https://github.com/jupyter-server/team-compass/blob/main/docs/scripts/gen_contributors.py
    title: "docs/scripts/gen_contributors.py"
  - id: custom-css
    resource: https://github.com/jupyter-server/team-compass/blob/main/docs/_static/custom.css
    title: "docs/_static/custom.css"
---

## gen_contributors.py 核心逻辑

### 依赖

- `pandas`：数据处理
- `ruamel.yaml`：YAML 解析
- `pathlib`, `os.path`：路径处理

### 工作流程

1. 读取 `docs/team/contributors-jupyter-server.yaml`
2. 用 ruamel.yaml 解析为 DataFrame
3. 按 `team` 字段筛选 active/inactive 成员
4. 对每个分组调用 `_generate_contributors()` 生成 HTML 表格
5. 识别 SSC 代表（有 `ssc` 字段的成员），判断现任（最新任期无结束日期）和历任
6. 将生成的 HTML 写入 `active.txt`、`inactive.txt`、`ssc-current.txt`、`ssc-past.txt`

### HTML 生成逻辑

- 每行4人（N_PER_ROW = 4）
- 头像URL：`https://github.com/{handle}.png?size=200`（去掉 @ 前缀）
- 个人主页URL：`https://github.com/{handle}`
- 输出格式为 reStructuredText `.. raw:: html` 指令，嵌入 HTML 表格
- 表格模板包含头像（120px）、姓名（粗体）、机构信息

### SSC 代表判定

```python
latest_term = rep.ssc[-1]           # 取最后一个任期
is_current = latest_term.split("-")[-1] == ""  # 任期以"-"结尾且无结束日期=现任
```

## custom.css 样式

- 贡献者条目：宽度100px、高度200px、内边距1em、垂直顶部对齐
- 头像：最大宽度120px，居中
- 姓名：居中、粗体、2px边距
- 机构信息：0.7em字号、粗体
- 贡献者表格：自动居中
