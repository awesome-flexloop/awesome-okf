# SOP 标准作业程序示例库

本目录收录可直接参考或适配的 SOP 模板与对照案例，均基于 [facts.md](../facts.md) 所引行业实证提炼。

## 示例一览

```{toctree}
:maxdepth: 1
:hidden:

01-sop-template
02-runbook-vs-playbook-example
```

| 示例 | 说明 | 对应洞察 |
|------|------|---------|
| [通用 SOP 模板（可复制）](01-sop-template.md) | 一页式 SOP 骨架 + 填写说明，含字段对齐 ALCOA+ 与四层体系 | 洞察 3 / 洞察 5 |
| [runbook vs playbook 对照示例](02-runbook-vs-playbook-example.md) | 同一故障场景（如数据库宕机）的两种写法对照 | 概念 04（辨析）|

## 使用建议

- **模板**：直接复制为组织内 SOP 骨架，按自身场景删减字段；重点对齐"谁、何时、做了什么、结果如何"四要素。
- **对照示例**：用于培训 SRE / 运维团队理解 runbook 与 playbook 的职责边界。
- **所有示例均不可直接用于合规审计**——必须经组织质量 / 法规部门审核后替换为真实业务内容。
