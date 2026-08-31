# 信源参考索引

本目录登记“算经阅读教程”所依据的全部文献信源，供概念文档与算题实战溯源引用。

| 信源文件 | 内容 | 对应文献级别 |
|---------|------|------------|
| [online-sources.md](online-sources.md) | 在线原典全文与影印底本：ctext.org（周髀/九章/海岛/孙子）、汉典古籍、中华文库、国学大师、维基文库 | 一级文献（原典） |
| [core-editions.md](core-editions.md) | 现代点校本与权威整理本：钱宝琮《算经十书》（中华书局1963）、郭书春/刘钝点校本、《九章算术》各注本、《中国科学技术典籍通汇·数学卷》、出土算数文献 | 二级文献（点校整理） |
| [modern-studies.md](modern-studies.md) | 现代学术研究：李俨/钱宝琮、李约瑟 SCC 卷3、吴文俊《中国数学史大系》、Martzloff、Chemla、Katz 资料集 | 三级文献（学术研究） |
| [cross-ref.md](cross-ref.md) | 库内交叉引用：katex、sympy、manim、boshu-reading、psi-math、okf-spec | 元数据/导航 |

## 信源分级原则

本知识包采用三级信源体系：

1. **一级（原典）**：在线全文与影印底本，原文引录的唯一依据；引录处标注信源 ID（如 `s-ctext-haidao`）与底本。
2. **二级（点校整理）**：现代权威点校本，校勘、断代、注释争议的裁决依据；标注信源 ID（如 `e-qian-1963`）。
3. **三级（学术研究）**：现代通史与专著，历史评价与世界数学史定位的依据；标注信源 ID（如 `r-martzloff-1997`）。

## 信源使用说明

- 概念文档通过 frontmatter 的 `sources` 字段引用信源，resource 使用 bundle 内绝对路径（`/references/xxx.md`）。
- 正文行文中的信源标注采用“据 <信源ID>”形式，例如“据 s-ctext-jiuzhang，《九章算术》收 246 题”。
- 古籍原文均为公共领域；现代研究著作仅登记书目与观点出处，不作大段摘录。
- 在线信源 URL 于 2026-08-30 实测可达（维基系站点浏览器访问正常，自动化抓取受限）。

```{toctree}
:hidden:
:maxdepth: 7

online-sources
core-editions
modern-studies
cross-ref
```