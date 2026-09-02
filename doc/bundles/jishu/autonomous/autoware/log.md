# Autoware Bundle 变更日志

## 2026-09-02 — 初始版本

- ✅ 基于 **blog-article-to-okf-wiki** 方法论链路 **R→I→E→V** 生成（历史教程类，无 examples/）
- ✅ 完成 R 阶段（事实采集）：从简书连载《☠️无人驾驶(停止维护)》（nb/47487870，作者"水之心"）4 篇实测教程采集 23 条事实（F-319~F-323、F-333~F-340、F-349~F-353、F-357~F-361），事实基准为 `.trae/specs/jianshu-blogs-to-okf-wiki/facts.md`（唯一合法事实集）
- ✅ 完成 I 阶段（洞察提炼）：确定"WSL2 环境 → ADE 环境 → Autoware.Auto 基础"的三篇 concepts 递进结构
- ✅ 完成 E 阶段（信源先行成文）：references/（4篇 + index）→ concepts/（3篇 + index）→ 根 index → log

### 信源

| 信源ID | 原文 URL | 内容时点 |
|--------|---------|---------|
| jianshu-7218542ae424 | https://www.jianshu.com/p/7218542ae424（Ubuntu 搭建 AutowareAuto） | 2020 年前后 |
| jianshu-8f97786e1631 | https://www.jianshu.com/p/8f97786e1631（AutowareAuto 基础） | 2020 年前后 |
| jianshu-a95f95276fec | https://www.jianshu.com/p/a95f95276fec（WSL2 之 autoware.auto） | 2020 年前后 |
| jianshu-dfc1df4eb6ee | https://www.jianshu.com/p/dfc1df4eb6ee（WSL2 安装和配置无人驾驶系统 autoware.auto） | 2020 年前后 |

### 文件清单（共 10 个文件）

| 文件路径 | 说明 |
|---------|------|
| `index.md` | Bundle 根索引（性质声明、结构总览、分层导航、信任与生命周期、已知边界、toctree） |
| `concepts/index.md` | 概念文档子目录索引（学习路径 + toctree） |
| `concepts/00-wsl2-environment.md` | WSL2 环境搭建（X 桌面路径 + Ubuntu 子系统路径 + VcXsrv 显示转发） |
| `concepts/01-ubuntu-ade-environment.md` | Ubuntu 与 ADE 开发环境（adehome/.aderc/克隆/构建测试） |
| `concepts/02-autoware-auto-basics.md` | Autoware.Auto 基础（三系/2020.5 能力/ADE 安装/演示命令链） |
| `references/index.md` | 信源登记簿子目录索引（信源清单 + 事实编号段索引 + 可信度说明） |
| `references/source-01.md` | Ubuntu 搭建 AutowareAuto（F-319~F-323） |
| `references/source-02.md` | AutowareAuto 基础（F-333~F-340） |
| `references/source-03.md` | WSL2 之 autoware.auto（F-349~F-353） |
| `references/source-04.md` | WSL2 安装和配置无人驾驶系统 autoware.auto（F-357~F-361） |
| `log.md` | 本文件 |

### 质量门记录

- **事实溯源门**：所有具体声明均带 F 编号引用，无 facts.md 之外编造的命令/数字/名称；命令仅转录原文，未增补 — **通过**
- **过时内容门**：三篇 concepts 均设「现状」小节，仅做"已过时、以官方当前文档为准"式一般性说明，未虚构当代行为 — **通过**
- **交叉引用门**：束内用 `/concepts/xx.md` 根相对引用、`../references/xx.md` 相对引用；兄弟束用 `../../dds/index.md`、`../../ros2/index.md` 相对路径；无 `file:///` 绝对路径 — **通过**
- **frontmatter 门**：bundle 根带 `okf_version: "0.2"` + 四信源 sources（resource 指向 /references/source-0N.md）；子文档带 type/title/description/tags/generated/verified/status/stale_after/sources — **通过**
- **性质声明门**：index.md 顶部显著位置标注"历史教程类知识包，非当前官方技术文档"，已知边界四条（Autoware.Auto 早期/ROS2 Dashing/WSL2 早期/旧式安装）齐全 — **通过**
- **toctree 门**：根 toctree 覆盖 concepts/index、references/index、log；concepts/index toctree 覆盖 3 篇；references/index toctree 覆盖 4 篇；组索引 `autonomous/index.md` 已含 autoware/index 条目 — **通过**

### 备注

- 本 bundle 为 `jishu/autonomous/` 新分组首束，组索引由本任务创建；`jishu/index.md` 接入由主任务（Task7）统一负责，本任务不修改；
- 兄弟束 DDS/ROS2 与本束交叉链接已建立：autoware/index.md 引 dds 与 ros2 两束。
