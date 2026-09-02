# Ecosystem Bundle 变更日志

## 2026-09-02 — 初始版本

- ✅ 基于 **blog-article-to-okf-wiki** 方法论链路 **R→I→E→V** 生成（历史教程类，无 examples/）
- ✅ 完成 R 阶段（事实采集）：从简书连载《☠️无人驾驶(停止维护)》（nb/47487870，作者"水之心"）4 篇文章采集 24 条事实（F-301~F-311、F-341~F-348、F-354~F-356、F-362~F-363），事实基准为 `.trae/specs/jianshu-blogs-to-okf-wiki/facts.md`（唯一合法事实集）
- ✅ 完成 I 阶段（洞察提炼）：确定"数据集 → 车载术语 → 学习资源 → WSL2 GPU 环境"的四篇 concepts 结构，覆盖无人驾驶生态外围知识
- ✅ 完成 E 阶段（信源先行成文）：references/（4篇 + index）→ concepts/（4篇 + index）→ 根 index → log

### 信源

| 信源ID | 原文 URL | 内容时点 |
|--------|---------|---------|
| jianshu-0066c78a2f43 | https://www.jianshu.com/p/0066c78a2f43（无人驾驶数据集） | 2020 年前后 |
| jianshu-e99b8cbb1825 | https://www.jianshu.com/p/e99b8cbb1825（汽车系统开发常见名称） | 2020 年前后 |
| jianshu-ca403b26e91b | https://www.jianshu.com/p/ca403b26e91b（Autonomous 资源） | 2020 年前后 |
| jianshu-98c8af1d2d33 | https://www.jianshu.com/p/98c8af1d2d33（wsl2 配置多环境的深度学习 GPU 环境） | 2020 年前后 |

### 文件清单（共 12 个文件）

| 文件路径 | 说明 |
|---------|------|
| `index.md` | Bundle 根索引（性质声明、结构总览、分层导航、信任与生命周期、已知边界、toctree） |
| `concepts/index.md` | 概念文档子目录索引（学习路径 + toctree） |
| `concepts/00-datasets.md` | 无人驾驶常用数据集盘点（10 数据集） |
| `concepts/01-vehicle-terms.md` | 车载术语：ECU 与 CAN |
| `concepts/02-resources.md` | 无人驾驶学习资源导航 |
| `concepts/03-wsl2-gpu-deep-learning.md` | WSL2 GPU 深度学习环境搭建 |
| `references/index.md` | 信源登记簿子目录索引（信源清单 + 事实编号段索引 + 可信度说明） |
| `references/source-01.md` | 无人驾驶数据集（F-301~F-311） |
| `references/source-02.md` | 汽车系统开发常见名称（F-362~F-363） |
| `references/source-03.md` | Autonomous 资源（F-354~F-356） |
| `references/source-04.md` | wsl2 配置多环境的深度学习 GPU 环境（F-341~F-348） |
| `log.md` | 本文件 |

### 质量门记录

- **事实溯源门**：所有具体声明均带 F 编号引用，无 facts.md 之外编造的命令/数字/名称；命令仅转录原文，未增补 — **通过**
- **过时内容门**：四篇 concepts 均设「现状」小节，仅做"已过时、以官方当前文档为准"式一般性说明，未虚构当代行为 — **通过**
- **交叉引用门**：束内用 `/concepts/xx.md` 根相对引用、`../references/xx.md` 相对引用；兄弟束用 `../../autoware/index.md`、`../../dds/index.md`、`../../ros2/index.md` 相对路径；无 `file:///` 绝对路径 — **通过**
- **frontmatter 门**：bundle 根带 `okf_version: "0.2"` + 四信源 sources（resource 指向 /references/source-0N.md）；子文档带 type/title/description/tags/generated/verified/status/stale_after/sources — **通过**
- **性质声明门**：index.md 顶部显著位置标注"历史教程类知识包，非当前官方技术文档"，已知边界四条（数据集规模/CUDA 老式安装/conda 版本/资源链接）齐全 — **通过**
- **toctree 门**：根 toctree 覆盖 concepts/index、references/index、log；concepts/index toctree 覆盖 4 篇；references/index toctree 覆盖 4 篇；组索引 `autonomous/index.md` 已含 ecosystem/index 条目 — **通过**

### 备注

- 本 bundle 为 `jishu/autonomous/` 新分组第四束，组索引由本任务创建；`jishu/index.md` 接入由主任务（Task7）统一负责，本任务不修改；
- 与 autoware、dds、ros2 三束交叉链接已建立：ecosystem/index.md 引 dds、ros2、autoware 三束；
- F 号使用与任务描述的差异：concepts/03 与 source-04 用 F-341~F-348（98c8af1d2d33），concepts/01 与 source-02 仅用 F-362~F-363（e99b8cbb1825）——详见任务报告"F 号笔误裁决"。
