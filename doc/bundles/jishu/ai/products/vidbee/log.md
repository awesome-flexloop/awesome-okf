# VidBee 变更日志

## 2026-10-10

- 按 seven-concepts-cmd 的知识沉淀场景执行 R→I→E→V；未授权 Git 提交，C 不执行。
- 公开读取芋道源码文章，核对账号、作者及时间；不保存正文镜像和推广材料。
- 以 v2.1.0 README、release API、固定 main SHA 和官方转录/AI 指南补核验；登记 F-001～F-038。
- 创建四篇教程、信源清单、事实表、核验报告和知识地图；不设未经实测的 examples。
- 基线 `conda run -n py314 invoke gates.all`：UTF-8 与 UTF-8 自检通过，toctree 检查发现 34 项其他在途问题并退出；不修改其他包来消除问题。
- 用户批准共享索引增量接入，接入前须重新读取并保留其他会话改动。
- G1/G2 通过；G3 保留单案例 L1 待验证，不能宣称跨案例实证完成。生成阶段状态为 draft。
- 四个独立视角完成首轮审查，修正来源 ID、Bilibili 归因、正文事实覆盖、Experimental/新桥接与 v2.1.0 区别、旧数据库延用条件；补充保留删除责任、组织部署准入、授权和成本边界。
- 独立复验未发现剩余 P0/P1，提出三项 P2：F-009/F-026 登记缺口、官方章节 locator 不精确、日志未承载修补记录。已补登记、同步核验表、修正 locator 并追加本日志；学习指南范围与未运行边界保留。
- 增量加入产品导航行和 toctree，产品目录 29 束；AI/技术域/总索引已由并行会话更新至实时值，本会话复核一致后不重复覆盖。`conda run -n py314 invoke gates.bundles` 通过：9 域、61 组、611 束。
- `conda run -n py314 invoke gates.all` 本轮：11212 文件 UTF-8 与自检通过，toctree 在其他在途包 `deepseek-harness/concepts` 缺 index.md 处退出；不声称全库全部通过。
- 标准链接 CLI 即使显式文件列表也扫描 0，未采信其通过提示。改用既有 `parse_links`/`check_local_link` 接口显式检查本包 12 文件、58 本地引用，零断链；包内完整 toctree BFS、YAML/type/resource、F-001～F-038 连续集合与核验表一致、7 个事实来源 ID 解析均通过。
- 最后一次独立定向复验确认三类修补闭环，无剩余分级发现；9 份带元数据文档统一标记 stable。此状态仅表示文档已审查，不是软件运行或多案例实证验收。
- Sphinx 构建验证未完成：技术域 dummy、本包 HTML 与核心扩展隔离 HTML 三次尝试均未在 120 秒内完成初始化，已停止，未产出可确认的构建成功结果。保留此环境验证缺口，不把解析门禁替代完整构建通过。
- 最终机械复验通过：12 文件、9 份 stable 元数据、38 条事实与核验集合、58 本地引用、包内导航及总索引计数；共享父索引增量内容通过 `git diff --check`。未暂存、提交或推送。

```text
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=V | event=CONCEPT_COMPLETED | session=sc-20261010-vidbee | ctx={"four_views":true,"revision_recheck":"passed","runtime_test":false,"sphinx_build":"not-completed"}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=S99 | event=CHAIN_COMPLETED | session=sc-20261010-vidbee | ctx={"documents":12,"facts":38,"insights":3,"pattern_maturity":"L1","C":"未授权，不执行","global_gate":"其他在途问题未通过"}
```
