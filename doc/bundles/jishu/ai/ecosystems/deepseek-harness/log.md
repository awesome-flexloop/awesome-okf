# DeepSeek Harness 知识包变更日志

## 2026-11-04

### 创造模式增量

- 学习公开文章《DeepSeek 再放大招，上线 Creator Mode。》（沉默王二，2026-11-03），读到结尾并拆分五个案例；配图未逐图核读。
- 增补官方主页、Web UI 入门、插件基础、打包安装、HMR 与模型公告的核验。
- 新增事实 F-017 至 F-065 共 49 条；旧 F-001 至 F-016 保留不重排。事实、覆盖索引和核验表编号集合一致性由机械检查验收。
- 新增创造模式、五案例、权限与生命周期、知识地图四篇概念，以及一篇待复现练习；新增四篇信源文档和三篇目录索引。
- 根入口改为 Harness 与创造模式，明确“2.0”为旧文章标题口径；修正工作模式页错指的 F-010/F-013/F-014。
- 不增加知识包束数，不修改其他在途知识包。旧定价及旧示例不在本次全面重新核验范围。

### 阶段与限制

- R：浏览器原文采集、事实登记及官方页面核验完成。
- I：三条四元组分析假设完成，事实、机制与迁移分层。
- E：原创教程与“察验再装”单案例待验证方法完成。
- V：四视角独立审查、文本修正及另一次独立回归完成；机械检查范围与剩余边界见下节，不宣称作者插件实测通过。
- C：用户未授权提交，未提交、未推送。
- status 保持 draft，stale_after 为 2026-12-04；精确工具契约、权限要求、其他入口与案例独立运行仍未验证。
- 全库导航变更前基线返回三项他方在途问题，均在 `jishu/ai/products/pagekin/`，与本次包体改动分开验收。

### 审查修正与验收

- 补齐首轮模型预算、数据外发、确定版本与安装脚本审批；官方安装文档提示脚本执行可能位于 Agent 沙箱外，保留关键短摘录。
- 倒计时练习新增日期绑定、自然归零、后台活动证据和配置基线比较；安全页新增逐项配置恢复及并发更新保护。
- 删除作者使用 ctx.effect 的无源码归因，分开需求与结果证据；补模式成熟度和七概念释义。
- 修正存量价格页引用，撤回旧 facts 的独立 verified 标签，给旧价格和概念页加历史边界并更新修订时间；未重读旧文章，不算旧事实全面复验。
- 49 编号三表集合一致、19 篇 Markdown / 14 篇正文计数一致、YAML/sources/UTF-8/无 BOM 均通过；包内导航清单和从全站入口可达通过。
- 最终显式扫描 19 篇文件，本地引用 95 个与 frontmatter 路径零断链。首个目录扫描量为零的结果已作废；16 个外部 URL 未批量验收。
- 全库导航复验先后出现 19、6、30 项外部在途问题；未修改他方目录，不宣称全库门禁通过。
- 全量 Sphinx dummy 构建主动停止、不计通过；同一项目配置保留日期钩子，限制本包并只启用 myst_parser 的严格 dummy 解析完成，退出码 0。不等同于生产 HTML、全部扩展或全库构建通过。
- 完整外部逐字回验、版本快照、图片独有信息及作者插件独立运行仍缺失；保持 draft。待验证模式的风险推导不能冒充实测 G3 成熟性。

```text
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=V1 | event=CONCEPT_COMPLETED | session=sc-20261104-wechat-okf | msg=四视角审查与独立修正回归完成 | ctx={"runtime_test":false,"source_verbatim_complete":false}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=V2 | event=GATE_PASSED | session=sc-20261104-wechat-okf | msg=包内静态验收通过；全库与实测不在通过范围 | ctx={"facts":49,"md":19,"content":14,"local_links":95,"sphinx_target_exit":0}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=S99 | event=CHAIN_COMPLETED | session=sc-20261104-wechat-okf | msg=R→I→E→V文档交付；模式仍待实测，C未授权 | ctx={"status":"draft","new_bundles":0,"commit":false}
```

```text
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=S0 | event=CMD_START | session=sc-20261104-wechat-okf | msg=公开文章知识沉淀 | ctx={"scenario":"knowledge","depth":"deep"}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=S2 | event=CHAIN_SELECTED | session=sc-20261104-wechat-okf | msg=R→I→E→V；C需另行授权 | ctx={"mode":"increment","new_bundles":0}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=R1 | event=CONCEPT_COMPLETED | session=sc-20261104-wechat-okf | msg=原文与官方页面核读；新增49条事实 | ctx={"range":"F-017..F-065","runtime_test":false}
```

## 2026-10-10

### 新增

- **bundle 初始化**：`deepseek-harness` 知识包（单源公众号公开文章教程）
  - 概念 3 篇：Harness 核心概念（执行壳）、四种工作模式、开源免费 + 模型单独计费
  - 示例 1 篇：假商店项目修复与生成演示（977→662）
  - 事实登记 1 篇：F-001~F-016（页面事实 + 作者主张分层，标注单源/推断）
- 来源：公众号《DeepSeek Harness 2.0 来了，Codex 该退休》（有限进步Seven，2026-10-05）

### 状态与限制

- **status: draft**——单源公开文章，未经官方文档独立交叉验证
- **stale_after: 2026-12-05**——定价/模式信息可能随官方发布过期
- 待办：获取 DeepSeek 官方 GitHub/文档后补充独立源，移除单源标注
