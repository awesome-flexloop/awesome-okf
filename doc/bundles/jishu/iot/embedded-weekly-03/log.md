# 生成日志（Log）

> 本日志记录《嵌入式周报·第三期》OKF 知识包的生成过程、质量门与决策依据，供后续维护者审计与复核。方法论链路：**seven-concepts-cmd 七概念元编排（场景 4 知识沉淀，R→I→E→V→C）→ wechat-public-okf 工作流**。CMD-LOG session：`sc-20261013-embedded-weekly-03`。

## 2026-10-13：初始版本（R→I→E→V）

### R 阶段：信源先行与事实采集

- **内容敏感度预检**：公开内容（mp.weixin.qq.com 公开访问，无登录/验证码/邀请码/付费墙）→ 标准工作流，bundle 入 `jishu/iot/`。
- **对象**：公众号「奔跑的码仔」《嵌入式周报·第三期｜AI设计的AI芯片，和一个只剩4天的RTOS版本》（2026-10-12 00:00，原创署名「奔跑的码仔」，覆盖 2026-10-05~11 一周）。
- **信源定性**：**自媒体技术综述（二手综述周报）**。客观骨架（项目存在、官方发布、公开数据）可靠；量化声明（openTPU 性能、TI 倍数）多为作者对原始项目/厂商自报口径的转述，无第三方实测。
- **事实登记**：F-001 ~ F-052 连续编号（无跳号），按周报六个板块组织（openTPU / 芯片与边缘 AI / Zephyr 生态 / CVE / Linux 与 RISC-V / 社区与硬件）。分类约定：`page_fact`（可核验客观陈述）、`author_claim`（作者观点/转述）、`verified/flagged`（独立核验后结论）。
- **P0 权威核验**：经 general_purpose_task 独立核验补齐第三方权威来源，识别 6 项需勘误/标记项（详见 [核验报告](references/verification.md) 与 [信源清单勘误摘要](references/source-manifest.md#重要勘误边界摘要详见核验报告)）：
  1. HN "250+ 分"最高观测约 144 → 降级（登首页属实）。
  2. Arduino Core for Zephyr v1.0.0 官方发布日 **2026-09-03** 非文章所述 10-04 → 勘误。
  3. Ambarella N1-665 规格疑与 N1-655 混淆 → flagged。
  4. LoRaWAN 原生后端"4.5 新增"版本归属 → single-source。
  5. Zephyr 4.5 精确 10-26（官方仅"2026-10"）→ single-source。
  6. openTPU 全量性能数字自报，无独立复现 → single-source。
  - Zephyr CVE-2026-19569 完整核验通过（8.8 分、userspace 整数溢出、影响 3.5.0~4.4.2、补丁 85c1c4c2、GHSA-fg8c-9fhq-q7hv）。

### I 阶段：骨架判定

- **两问判定**：周报为时效性综述，无可执行代码/配置产物 → **不设 examples/**；依数据性质设 concepts 五条路径（现象事实→机制原理→工程判断三层）。
- **归属**：`jishu/iot/`（对齐星辰300 的"端侧 AI 资讯核验"范例），新建 bundle `embedded-weekly-03`。
- **status 裁决**：客观骨架可信、量化声明含多处自报/勘误且无第三方实测 → **draft**（不谎报 sustainable）；stale_after 2027-04-30（受 2026-10 中下旬多个官方节点与 openTPU 独立复现触发提前复核）。

### E 阶段：bundle 生成（信源先行顺序）

references/source-manifest → references/verification → references/index → concepts×5 → concepts/index → index.md → log.md，共 10 个文件。所有具体声明挂 F 编号；勘误处采用权威值、不照搬周报；author_claim 类主张保持 **作者口径限定**、不升级为普遍事实。

### V 阶段：机械门禁与索引接入

- **gates 环境说明**：`invoke <bundle>.gates` 依赖 invocations 环境，本会话不可用，以下为**手动等效核验**（逐项执行正则/脚本比对），未谎报 gates 通过。

| # | 门禁项 | 方法 | 结果 |
|---|--------|------|------|
| 1 | F 编号连续性 | 正则提取 source-manifest 全部 `F-\d{3}` | ✅ F-001~F-052 连续无跳号 |
| 2 | 每级 index 含 toctree | 检查根 index / concepts/index / references/index 三个 ` ```{toctree} ` 块 | ✅ |
| 3 | toctree 条目文件存在 | 逐条对应文件系统检查 | ✅ |
| 4 | 无 file 协议绝对路径 | grep 检索 `file:` 前缀 URI | ✅ |
| 5 | 相对链接可达 | 链接逐条解析 | ✅ |
| 6 | 正文 F 引用越界 | 正文 `F-\d{3}` 引用 ⊆ F-001~F-052 | ✅ |
| 7 | 无用户主目录绝对路径泄露 | grep 检索系统用户目录前缀 | ✅ |
| 8 | frontmatter YAML 可解析 | PyYAML safe_load 全部 10 文件 | ✅ |
| 9 | 计数与索引接入 | jishu/iot/index.md 导航+toctree 新增条目；bundles/index.md 计数对账 | ✅ 见下节 |

- **四视角对抗审查**：
  - 事实溯源视角：每条具体声明可回溯 F 编号与 references；自报/营销数字均带来源与口径限定，author_claim 不冒充 page_fact。✅
  - 结构规范视角：frontmatter 字段（type/title/sources/status/stale_after/generated）、kebab-case 文件名、MyST toctree、无 examples 骨架与判定一致。✅
  - 读者可用视角：概念地图五条路径清晰；性质声明与勘误摘要置顶；P0 核验目录可读。✅
  - 时效边界视角：stale_after + 4 条提前复核触发条件明示。✅

### 索引接入与计数

- `jishu/iot/index.md`：新增 `embedded-weekly-03` 至"📰 端侧 AI 资讯（博文核验）"板块与 toctree。
- `bundles/index.md`：`total_bundles` 与相关域/组计数按实际口径 +1（修改前逐处读校，遵守项目记忆既有计数口径对账纪律）。

## 文件清单

| 文件 | 说明 |
|------|------|
| index.md | 包入口（okf_version 0.2，性质声明 + 导航 + 边界） |
| log.md | 本文件 |
| concepts/index.md | 概念地图与学习路径五条 |
| concepts/00-ai-designed-chip.md | openTPU 头条（F-001~F-011） |
| concepts/01-edge-ai-npu-trend.md | NPU 下沉 MCU（F-012~F-019） |
| concepts/02-zephyr-ecosystem.md | Zephyr 节奏/安全/产业/OEM（F-020~F-032） |
| concepts/03-riscv-software-stack.md | RVA23 与自动向量化（F-040~F-046） |
| concepts/04-community-maker-projects.md | 社区项目与打假（F-047~F-052） |
| references/index.md | 参考资料索引 |
| references/source-manifest.md | 主信源元信息 + F-001~F-052 全部事实 |
| references/verification.md | 17 项 P0 核验 + 勘误清单 + 残余不确定性 |

## 已知遗留

1. **无第三方实测**：openTPU 性能、TI 倍数等量化声明维持自报/营销口径，未升级。
2. **型号混淆嫌疑**：Ambarella N1-665 与 N1-655 规格疑混淆，以 flagged 标记，待官方 Datasheet 澄清。
3. **single-source 日期**：Zephyr 4.5 精确发布、Arduino 日期（已勘误）、LoRaWAN 版本归属等维持单源/勘误状态。
4. **gates 未以 invoke 运行**（环境依赖缺失），以手动等效核验代偿，待子模块 CI 环境复跑。
5. **子模块提交待执行**：当前为未提交工作区状态，按项目记忆约定拆分为子模块与主仓两次原子提交（主仓提交含 submodule 指针变更）。