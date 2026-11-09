# 实战示例

本目录的 3 篇示例都遵循同一结构：适用场景 → 前置条件 → 分步命令 → 预期结果 → 失败排查表。它们**均为基于源码阅读整理的用法演示，未在本机实跑**，所有输出只表示格式与字段形态，不构成运行结果承诺。

| 序号 | 示例 | 覆盖能力 | 前置概念 |
|---|---|---|---|
| 01 | [带前置检查的首次接入](01-quickstart-with-preflight.md) | 安装 Skill、版本门禁、扫码授权、身份确认、只读查询 | [01 前置检查与身份](../concepts/01-preflight-and-identity.md) |
| 02 | [从表格数据到在线 PPT](02-sheet-to-ppt-pipeline.md) | `collect.py` 采集、pptx 域建文档、写页、传图、交付链接 | [02 意图路由](../concepts/02-intent-routing.md) |
| 03 | [本地 PPT 预览与公式重算](03-pptx-preview-and-recalc.md) | `pptx2image.py` 生成预览、`recalc.py` 重算并保存 | [04 脚本工具链](../concepts/04-scripts-toolchain.md) |

建议顺序：先跑 01 建立可用环境，再按任务类型选择 02 或 03；三篇之间没有执行上的强依赖，但 02、03 都假定前置检查已通过。

```{toctree}
:hidden:
:maxdepth: 7

01-quickstart-with-preflight
02-sheet-to-ppt-pipeline
03-pptx-preview-and-recalc
```