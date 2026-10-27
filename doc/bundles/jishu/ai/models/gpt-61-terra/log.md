# 变更日志

## 2026-10-27

- 来源：Tibo Day 22 原帖，补充 OpenAI 发布文和 API 模型参考。公开内容按子项目自治规范存入 `doc/bundles/`。
- 归属：`jishu/ai/models/gpt-61-terra/`。主体是基础模型能力与选型，沿用已有 models 分组；不新增厂商分组。
- R：先生成信源台账，登记 F-001 至 F-045 共 45 条，官方自述与访问观测分层。未读取的系统卡不作为实质证据。
- I：按定位、能力、费用、评估分篇，洞察以现象 / 解释假设 / 影响 / 建议四元组记录。
- E：形成 5 篇内容文档、2 篇信源文档、3 篇索引和本日志，共 11 个 Markdown 文件；候选模式保持 L1，未执行迁移实验。
- 骨架判定：源文没有具备输入输出与实际复现记录的操作流程，不设 `examples/`。所列任务评估方案均待实测。
- 流程适配：按子项目轻量自治规范，只维护一份 F 台账；不创建主仓 spec、不复制临时草稿入公共目录。C 未获明确提交授权，不提交、不推送。

### V 与机械验收

- 四个独立视角完成审查；已修订官网任务例归因、Cost 统计缺口、effort 缺口、执行器说明、非实测验收样例及人工成本口径。限定这些修订点的独立回归未发现剩余 P0-P3 问题；回归不包含外部网站复测。
- 直接使用 py314 解释器从标准输入执行机械核验：11 个 Markdown 文件严格 UTF-8 解码、无 BOM；含 frontmatter 的文件 YAML 可解析、type 非空、sources 条目均有 resource；F-001 至 F-045 连续唯一，全部 F 引用落在台账集合内。
- 从本束根 index 沿 toctree 实际遍历，11/11 文件可达，全部导航目标存在。这是本束完整遍历，不以指定目录断链检查冒充全站可达检查。
- 链接检查使用显式逐文件 `--paths` 与 `--check-frontmatter-paths`：实际扫描 11 文件，23 个本地引用及元数据路径通过；5 个外链未执行网络可达性检查。早先目录扫描返回 0 文件的结果不计入验收。
- `git diff --check` 通过；`invoke gates.redline` 为 11 passed。未新增或修改 Python 源码。
- 全库门禁未通过：此前 toctree 被并行写入的 `kanzan` 目录缺失索引与不可达内容拦截；资产基线门发现 README 与文档首页仍写 679，而总索引已为 682。开工时总索引为 681，因此 679 属既有漂移，未在本任务中扩大修订范围。
- 总索引计数门曾通过 682 束 / 63 组 / 9 域；恢复后的复跑发现目录树已为 683 束，技术域为 504，而声明仍为 682 / 503。并行目录变化使先前通过结果失效，不能宣称当前全库计数通过；未修改或接管 `kanzan`。
- Sphinx dummy 构建已启动；收尾读取原任务状态仍为 Running，exit_code 为空。未重复启动，未宣称构建成功；构建终态待确认。
- 交付状态：本束内容与局部门禁完成，保持 draft；系统卡、精确额度规则、独立性能实验与全库门禁仍未完成。不提交、不推送。

## 编排记录

```text
[CMD-LOG] | cmd=seven-concepts | step=S0 | event=CMD_START | session=sc-20261027-gpt-61-terra | scenario=knowledge | depth=deep
[CMD-LOG] | cmd=seven-concepts | step=S2 | event=CHAIN_SELECTED | session=sc-20261027-gpt-61-terra | chain=R>I>E>V | C=await-explicit-authorization
[CMD-LOG] | cmd=seven-concepts | step=R1 | event=CONCEPT_COMPLETED | session=sc-20261027-gpt-61-terra | facts=45 | system-card=unread
[CMD-LOG] | cmd=seven-concepts | step=G1 | event=GATE_PASSED | session=sc-20261027-gpt-61-terra | numbered-statements=45 | vendor-claims=attributed
[CMD-LOG] | cmd=seven-concepts | step=G2 | event=GATE_PASSED | session=sc-20261027-gpt-61-terra | insight-tuples=3
[CMD-LOG] | cmd=seven-concepts | step=E1 | event=CONCEPT_COMPLETED | session=sc-20261027-gpt-61-terra | pattern=L1-candidate | migration=not-executed
```

G3 只确认候选模式结构，不能宣称经验验证通过；V 与机械门禁结果见上方实际执行记录。

```text
[CMD-LOG] | cmd=seven-concepts | step=V1 | event=CONCEPT_COMPLETED | session=sc-20261027-gpt-61-terra | perspectives=4 | targeted-regression=no-remaining-findings
[CMD-LOG] | cmd=seven-concepts | step=V2 | event=GATE_PASSED | session=sc-20261027-gpt-61-terra | scope=bundle | files=11 | facts=45 | toctree-reachable=11/11 | local-links=23
[CMD-LOG] | cmd=seven-concepts | step=V3 | event=GATE_FAILED | session=sc-20261027-gpt-61-terra | scope=repository | blockers=parallel-navigation-and-count-drift,existing-homepage-count-drift | sphinx=pending
```
