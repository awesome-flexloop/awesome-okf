# ROS 2 Bundle 变更日志

## 2026-09-02 — 初始版本

- ✅ 基于 **blog-article-to-okf-wiki** 方法论链路 **R→I→E→V** 生成（历史教程类，无 examples/）
- ✅ 完成 R 阶段（事实采集）：从简书连载《☠️无人驾驶(停止维护)》（nb/47487870，作者"水之心"）的《ROS2 概念》一文采集 9 条事实（F-324~F-332），事实基准为 `.trae/specs/jianshu-blogs-to-okf-wiki/facts.md`（唯一合法事实集）
- ✅ 完成 I 阶段（洞察提炼）：确定单篇 concepts 总览结构（ros2 束承载 ROS 2 层概念，通信底座下沉到 dds 束）
- ✅ 完成 E 阶段（信源先行成文）：references/（1篇 + index）→ concepts/（1篇 + index）→ 根 index → log

### 信源

| 信源ID | 原文 URL | 内容时点 |
|--------|---------|---------|
| jianshu-86377a66ecef | https://www.jianshu.com/p/86377a66ecef（ROS2 概念） | 2020 年前后 |

### 文件清单（共 6 个文件）

| 文件路径 | 说明 |
|---------|------|
| `index.md` | Bundle 根索引（性质声明、结构总览、分层导航、信任与生命周期、已知边界、toctree） |
| `concepts/index.md` | 概念文档子目录索引（学习路径 + toctree） |
| `concepts/00-ros2-overview.md` | ROS 2 概念总览（中间件/节点/发现/DDS 底座/QoS/统计） |
| `references/index.md` | 信源登记簿子目录索引（信源清单 + 事实编号段索引 + 可信度说明） |
| `references/source-01.md` | ROS2 概念（F-324~F-332） |
| `log.md` | 本文件 |

### 质量门记录

- **事实溯源门**：所有具体声明均带 F 编号引用，无 facts.md 之外编造的内容 — **通过**
- **过时内容门**：concepts/00 设「现状」小节，仅做"已过时、以官方当前文档为准"式一般性说明，未虚构当代行为 — **通过**
- **交叉引用门**：束内用 `/concepts/00-ros2-overview.md` 根相对引用、`../references/xx.md` 相对引用；兄弟束用 `../../dds/index.md`、`../../autoware/index.md` 相对路径；无 `file:///` 绝对路径 — **通过**
- **frontmatter 门**：bundle 根带 `okf_version: "0.2"` + 单信源 sources；子文档带 type/title/description/tags/generated/verified/status/stale_after/sources — **通过**
- **性质声明门**：index.md 顶部显著位置标注"历史教程类知识包，非当前官方技术文档"，已知边界两条（ROS 2 早期版本/Topic Statistics 范围）齐全 — **通过**
- **toctree 门**：根 toctree 覆盖 concepts/index、references/index、log；concepts/index toctree 覆盖 1 篇；references/index toctree 覆盖 1 篇；组索引 `autonomous/index.md` 已含 ros2/index 条目 — **通过**

### 备注

- 本 bundle 为 `jishu/autonomous/` 新分组第二束，组索引由本任务创建；`jishu/index.md` 接入由主任务（Task7）统一负责，本任务不修改；
- 与 dds、autoware 两束交叉链接已建立：ros2/index.md 引 dds 与 autoware 两束。
