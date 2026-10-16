# 信源登记簿（References）

本目录收录 Cua Computer-Use 开源全栈知识包的信源事实清单和核验报告。

## 信源清单

| 编号 | 信源 | 类型 | 覆盖事实 |
|------|------|------|---------|
| R1 | [博文原文](article-source.md) | 微信公众号"FinOps实战"（2026-09-26） | F-001 ~ F-053（博文全部事实与观点）+ F-054 ~ F-065（核验补充与时点勘误） |
| R2 | [核验报告](verification.md) | GitHub API + newreleases.io + piwheels + 官方文档页 + 第三方报道 | 18 项 P0/P1 声明核验结论（12✅ + 6⚠️ + 0❌）+ 第二轮第二篇 20 项（14✅ + 6⚠️ + 0❌）与跨信源对账 4 条 |
| R3 | [第二篇文章事实清单](second-article-facts.md) | 微信公众号"极限编程驿站"（2026-10-08） | F-066 ~ F-139（第二篇文章事实/观点/厂商自述）+ F-140 ~ F-154（官方源核验补充与未核验项） |

## 事实编号索引

| 事实编号 | 简述 | 信源 | 文档 |
|---------|------|------|------|
| F-001~F-003 | 博文元信息 | R1 | 00-project-overview |
| F-004~F-009 | 项目身份、Computer-Use 2.0 理念、三大难题、三类人群 | R1+R2 | 00-project-overview |
| F-010~F-014 | 五大核心模块 | R1+R2 | 01-five-core-modules |
| F-015 | 许可证透明度 | R1+R2 | 02-ecosystem-and-licensing |
| F-016~F-026 | Stars 趋势、社区活跃度、发布节奏、语言构成 | R1+R2 | 03-stars-and-momentum |
| F-027~F-040 | 快速上手路径（安装命令、三步骤、Fleets、建议顺序） | R1+R2 | 04-getting-started |
| F-041~F-053 | 评价、适用场景、局限与展望 | R1 | 05-scenarios-and-limitations |
| F-054~F-057 | 官方核验：仓库身份/MIT/README 引语/stars 时点/语言时点 | R2 | 00-project-overview, 03 |
| F-058~F-060 | 官方核验：sandbox 版本日期/nightly 节奏 | R2 | 03-stars-and-momentum |
| F-061~F-063 | 官方核验：6×7 教程/安装命令/CUA-S1 | R2 | 01, 04 |
| F-064~F-065 | 官方核验：第三方许可证/快照后演进 | R2 | 02 |
| F-066~F-069 | 第二篇文章元信息（标题/公众号/发布时间/跨四类系统） | R3 | second-article-facts |
| F-070~F-076 | 项目身份与动量（仓库/Star/Fork/Rust 占比/MIT/建仓/贡献者） | R3 | second-article-facts |
| F-077~F-086 | 六组件构成（Driver/Spaces/Lume/SDK 与 CLI/CUA-S1/Bench） | R3 | second-article-facts |
| F-087~F-096 | Cua Driver 机制与权限三档（standard/bounded/unrestricted） | R3 | second-article-facts |
| F-097~F-111 | Cua Bench 榜单 v1（25 个 KiCad 任务/200 步/netlist 判分/名次） | R3 | second-article-facts |
| F-112~F-120 | 命令族（安装/`cua sb` gVisor 沙箱/Lume/Driver） | R3 | second-article-facts |
| F-121~F-125 | 许可分层（MIT/FSL-1.1-MIT/AGPL 系 cua-perception） | R3 | second-article-facts |
| F-126~F-127 | 废弃包与 cuabot 安全警告 | R3 | second-article-facts |
| F-128~F-130 | 「何时不需要它」作者判断 | R3 | second-article-facts |
| F-131~F-133 | 采用者与成本（Fleets 单价、Spaces 免费） | R3 | second-article-facts |
| F-134~F-139 | 结语观点与文章元信息（项目地址/许可标注） | R3 | second-article-facts |
| F-140~F-154 | 官方源核验补充与未核验项（GitHub API/README/榜单/官网，2026-10-16） | R3 | second-article-facts |

## 可信度说明

| 等级 | 事实编号 | 说明 |
|------|---------|------|
| ✅ 已核验 | F-003、F-005~F-015、F-019、F-023~F-025、F-027~F-038、F-040、F-049、F-054~F-056、F-058~F-064 | 经 GitHub API/官方文档/版本库/多方报道交叉验证 |
| ⚠️ 时点/口径差异 | F-004（主体名称）、F-016~F-018、F-020、F-026、F-057 | 核心事实正确，但为时点快照或口径差异，引用须带时点 |
| 📝 作者观点 | F-021~F-022、F-039、F-041~F-053 | 博文作者分析判断，非客观事实 |

```{toctree}
:hidden:
:maxdepth: 7

article-source
verification
second-article-facts
```