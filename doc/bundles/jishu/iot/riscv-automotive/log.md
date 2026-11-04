# 生成日志（Log）

> 本日志记录《ARM败在哪？RISC-V上车》OKF 知识包的生成过程、质量门与决策依据，供后续维护者审计与复核。方法论链路：**seven-concepts-cmd 七概念元编排（场景 4 知识沉淀，R→I→E→V→C）→ blog-article-to-okf-wiki 七阶段工作流**。CMD-LOG session：`sc-20261104-riscv-automotive`。

## 2026-11-04：初始版本（R→I→E→V）

### R 阶段：信源先行与事实采集

- **内容敏感度预检（阶段 0）**：公开内容（`mp.weixin.qq.com/s/q0R4yQBlq2dv1ajIqHT6lg` 公开推文，无登录/验证码/邀请码/付费墙）→ 标准工作流，bundle 入 `jishu/iot/`。
- **对象**：公众号「SoC芯片」《ARM败在哪？RISC-V上车》（作者署名「芯格芯格」，2026-11-02 00:00）。
- **信源定性**：**芯片垂直自媒体的产业战略评论/观点分析**（信源距离第三类"第三方综述/评论转述"）。非厂商自宣、非官方发布、非作者一手实测。
- **提取方式**：WebFetch 首次即成功返回全文（五节 + 结语）。注：Skill 文档记载 `mp.weixin.qq.com` 常被 WebFetch 反爬（13/13 拦截、建议改用 browser_use），本次属**例外**，如实记录。
- **事实登记**：F-001 ~ F-041 连续编号（无跳号）。A~F 为博文（28 条，F-001~F-028），G 为权威源核验补充（13 条，F-029~F-041）。分类约定：O=客观事实（博文叙述）｜V=作者观点/判断｜S=厂商/媒体口径。
- **P0 权威核验**：三轮 WebSearch + 权威源交叉核验（RISC-V International 官方站、RISC-V 官方 ISA 规范库、Gasgoo/Hengsen/EEWorld/EET-China/EDN China 行业媒体、ISO 26262 技术资料、AUTOSAR 适配厂商公告），形成 V1~V10 十项声明簇。
  - 结论：**✅ 7 / ⚠️ 3 / ❌ 0**。
  - ⚠️ 三项：① F-005"2026 量产元年"为**媒体概括框架**（紫荆 M100 实为 2025-12-18 上车，精确起点早于 2026）；② F-011/F-018"换供应商不重写软件"为**理想上限**（作者自陈非现状，需 AUTOSAR 层抽象配合）；③ F-024/F-025"ARM 短期仍主流/双轨并行"为**定性能见**（无量化权威源）。
  - 关键 ✅：基础 ISA 冻结（V2）、先外设后核心（V4）、生态胜负手（V5）、PLIC 实现差异与自定义扩展不可移植（V6）、AUTOSAR 适配（V7）、ASIL-D 全链路约 2 年 / 编译器属 TCL1（V8）、开源≠无风险（V10）。
  - **本文无量化数字与具体产品名可勘误**，故核验目标为"产业事实框架是否成立"，核验方以 DF30/M100/CCR4001 等量产案例为框架补锚点。

### I 阶段：骨架判定

- **操作可复现性两问**：① 有读者可照做的安装/配置/代码/调用流程？→ **否**；② 流程经作者实测、具备可复现性？→ **否** → 商业/战略分析类，**不设 examples/**（与 embedded-weekly-03 / threeui / a2a-mcp 正例同型）。
- **归属**：`jishu/iot/riscv-automotive/`（jishu/iot 已有「📰 端侧 AI 资讯（博文核验）」板块与 embedded-weekly-03/xingchen-300-edge-ai/rtx-spark 同品类先例；单篇博文不新建分组）。
- **三层拆分**：现象/事实层（00）、机制/路径层（01）、工程判断/边界层（02）。
- **status 裁决**：0 ❌、核心框架全部成立，但内容以定性与趋势判断为主、可核性有限 → **draft**（保守档，与 embedded-weekly-03 同型），**不置 flagged**；`stale_after: 2027-05-31`。

### E 阶段：bundle 生成（信源先行顺序）

references/article-source → references/verification → references/index → concepts/00 → concepts/01 → concepts/02 → concepts/index → index.md → log.md，共 9 个文件。所有具体声明挂 F 编号；⚠️ 项在正文保留"上限/定性/媒体框架"限定，不当事实转引；核验方补充的产业案例（F-030~F-034）与作者主张清晰区分。

### V 阶段：机械门禁与索引接入

- **gates 环境说明**：`invoke gates.all` 依赖 invocations 环境；本会话以**手动等效核验**逐项执行正则/脚本比对，未谎报 gates 通过。

| # | 门禁项 | 方法 | 结果 |
|---|--------|------|------|
| 1 | 双份 F 编号集合 | spec `facts.md` ↔ `references/article-source.md` 正则 `^\|\s*F-(\d{3})\s*\|` 集合比对 | ✅ 各 41、集合相等、F-001~F-041 连续 |
| 2 | 每级 index 含 toctree | 检查根 index / concepts/index / references/index 三个 ` ```{toctree} ` 块 | ✅ |
| 3 | toctree 条目文件存在 | `check-toctrees.py` | ✅ 本包 3 级全可达（4 处报告缺口均为他人在途 WIP，与本包无关） |
| 4 | 相对链接可达 | 正则提取 + 路径存在性（9 文件 / 30 链接） | ✅ 0 断链 |
| 5 | UTF-8 strict | `check-utf8.py` | ✅ 12769 文件通过 |
| 6 | frontmatter YAML 可解析 + 必需字段 | PyYAML safe_load 全部 9 文件 | ✅ |
| 7 | 敏感信息零残留 | grep 检索 `file:///` 与 `C:\Users`/家目录前缀 | ✅ 0 命中 |
| 8 | 计数与索引接入 | jishu/iot/index.md 导航+toctree；`check-bundles-index.py` 五面计数对账 | ✅ 9 域/64 组/705 束 五面一致 |

- **四视角对抗审查**：
  - 事实溯源视角：具体声明均可回溯 F 编号与 references；⚠️ 项保留口径限定；核验方补充事实与作者主张分离标注。✅
  - 结构规范视角：frontmatter 字段（type/title/sources/status/stale_after/generated）、kebab-case 文件名、MyST toctree、无 examples 骨架与判定一致。✅
  - 读者可用视角：性质声明与口径勘误置顶；概念地图三条路径与"读法提示"清晰。✅
  - 时效边界视角：stale_after + 提前复核触发条件明示。✅

### 索引接入与计数

- `jishu/iot/index.md`：新增 `riscv-automotive` 至"📰 端侧 AI 资讯（博文核验）"板块表行与 toctree。
- `bundles/index.md`：`total_bundles` 与相关域/组计数按目录树真值 +1（**并发会话已先将其余会话新增 1 束写入 704/514，本包仅补 +1 → 705/515，未回滚他人变更**）。
- **并发提示**：`check-toctrees.py` 报告的 4 处缺口（`jishu/ai/products/pagekin/`、`jishu/ai/ecosystems/deepseek/super-agent-architecture/`）为其他会话在途未完成产物，按纪律只报告不擅改。

## 文件清单

| 文件 | 说明 |
|------|------|
| index.md | 包入口（okf_version 0.2，性质声明 + 分层导航 + 信任与生命周期 + 已知边界） |
| log.md | 本文件 |
| concepts/index.md | 概念地图与学习路径三条 |
| concepts/00-supply-chain-autonomy.md | 供应链自主权（F-005~F-012、F-041） |
| concepts/01-adoption-path-and-ecosystem.md | 上车路径与生态胜负手（F-013~F-017） |
| concepts/02-four-industry-realities.md | 四个产业现实与结语（F-018~F-028） |
| references/index.md | 参考资料索引 |
| references/article-source.md | 主信源元信息 + F-001~F-041 全部事实 |
| references/verification.md | V1~V10 十项 P0 核验 + 口径四清单 + 残余不确定性 |

## 已知遗留

1. **非一手实测教程**：全文为产业观点分析，无安装/代码/实测流程，不可照做复现。
2. **无量化声明可核**：作者未给出产品名、数字、公司名；核验的是"产业事实框架是否成立"，非逐字数字勘误。
3. **定性判断占比高**："短期 ARM 仍主流""双轨并行是主流策略"等维持作者判断口径，未升级为量化事实。
4. **量产元年为媒体框架**：M100 实为 2025-12 上车；本包并列呈现两口径。
5. **gates 未以 invoke 运行**（环境依赖缺失），以手动等效核验代偿，待子模块 CI 环境复跑。
6. **子模块提交待执行**：当前为未提交工作区状态，按约定拆分为子模块与主仓两次原子提交（主仓提交含 submodule 指针变更）。
