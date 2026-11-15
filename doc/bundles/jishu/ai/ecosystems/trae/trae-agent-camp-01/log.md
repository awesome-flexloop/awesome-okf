# 更新日志

## 2026-11-15

- **创建知识包**：以 TRAE 训练营第二期 01 课课程文档（采集于 2026-11-15，revision_id 1236）为唯一主信源，按 R→I→E→V→C 链路生成 8 篇概念、3 篇示例、2 篇信源参考与 5 条洞察、5 个模式。
- **事实登记**：F-001~F-091 共 91 条，其中课程原文 80 条（含 F-090、F-091）、核验补充 9 条（F-079~F-087）、元信息 2 条（F-088、F-089）。
- **P0 核验**：10 项 → 5 ✅ / 5 ⚠️ / 0 ❌。通过项为 Base URL、模型存在性与视觉/GUI 能力、豆包手机助手 2026 年 9 月发布、APK 大小、ReAct 定义；部分通过项集中于免费额度口径、仓库归属、设备边界、费用估算与 App 内部行为。
- **敏感度处理**：课程文档托管于企业内部飞书域，本包按用户指定目录落盘；正文与信源层均不引用其 URL，不转载课堂体验额度的领取流程、令牌与个人登记信息（该项已于 2026-11-13 21:00 过期），课程文档直接引用的附件令牌与视频令牌不收录。
- **V 审查**：四视角共 7 条意见，采纳 5 条、部分采纳 2 条、不采纳 0 条；采纳项已回归到 01、02、03、05、07 与 index 正文。
- **索引接入**：新增 `jishu/ai/ecosystems/trae/trae-agent-camp-01/`，并同步 trae 分组、ecosystems 分类、ai 域与 bundles 总索引四层计数。
- **门禁**：`check-toctrees.py`、`check-bundles-index.py`、`check-utf8.py`、链接检查四项结果见下方记录。

### 门禁记录

| 门禁 | 命令 | 结果 |
|------|------|------|
| toctree 完整性 | `python scripts/check-toctrees.py` | 通过：全部 index.md 引用有效，所有内容文档可达 |
| 总索引计数对账 | `python scripts/check-bundles-index.py` | 通过：9 域 / 65 组 / 738 束，五面一致 |
| UTF-8 编码 | `python scripts/check-utf8.py` | 通过：13336 个文件均为有效 UTF-8 |
| Markdown 链接 | `.agents/scripts/check-links.py --path <bundle>` | 通过：20 文件 / 75 条本地引用零断链（过程中修复 3 处跨组相对路径） |
| 库规模基线 | `python scripts/check-asset-baseline.py` | 规模数字通过（README 与 doc/index.md 已同步 738）；字节残差为工作区未提交变更（含并行会话改动），按脚本要求提交后复跑 |
| Sphinx dummy 构建 | `sphinx-build -b dummy -E doc _build/dummy` | 通过：构建成功，全库 364 条既有警告（集中在其他既有束）；本束 0 告警 |

### CMD-LOG

```text
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=S0 | event=CMD_START | session=sc-20261115-trae-agent-camp-01 | msg=方法论编排开始：TRAE 训练营第二期 01 课学习与洞察 | ctx={"scenario":"knowledge","topic":"trae-agent-camp-01","depth":"standard"}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=S1 | event=SCENARIO_DETECTED | session=sc-20261115-trae-agent-camp-01 | msg=场景4知识沉淀 | ctx={"chain":"R-I-E-V-C"}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=S2 | event=CHAIN_SELECTED | session=sc-20261115-trae-agent-camp-01 | msg=链路R-I-E-V-C，含P0核验与四视角审查 | ctx={"gates":["G1","G2","G3","V","G4"]}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=S3 | event=GATE_PASSED | session=sc-20261115-trae-agent-camp-01 | msg=G1事实无因果词，91条编号事实 | ctx={"facts":91}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=S4 | event=GATE_PASSED | session=sc-20261115-trae-agent-camp-01 | msg=G2洞察四元组完整，5条 | ctx={"insights":5}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=S5 | event=GATE_PASSED | session=sc-20261115-trae-agent-camp-01 | msg=G3模式要素完整，5个L1-draft | ctx={"patterns":5}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=S6 | event=GATE_PASSED | session=sc-20261115-trae-agent-camp-01 | msg=V四视角7条意见，采纳5条部分采纳2条 | ctx={"adopted":7}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=S99 | event=CHAIN_COMPLETED | session=sc-20261115-trae-agent-camp-01 | msg=知识包落盘完成 | ctx={"files":20}
```
