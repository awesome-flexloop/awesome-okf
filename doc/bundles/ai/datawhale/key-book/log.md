# log

## 2026-08-23 — 初始知识束生成

- **R 阶段**：阅读 README.md、docs/index.md、docs/catalog.md（序言）、chapter1.md–chapter8.md、appendix.md、notation.md、reference.md，在 [spec/facts.md](spec/facts.md) 记录 8 章 + 序言 + 附录 + 符号表 + 参考文献的完整结构。
- **I 阶段**：在 [spec/insights.md](spec/insights.md) 提炼 4 条洞察：
  1. 理论机器学习的七大支柱构成完整判据链
  2. 从有限到无限的三层分析框架递进
  3. PAC 学习与统计学习理论在稳定性处统一
  4. 离线 i.i.d. 到在线非平稳的范式转换
- **E 阶段**：创建知识束文件：
  - `index.md`：束索引，含七大支柱与章节导航
  - `concepts/`：7 个概念文件（可学性、计算复杂度、泛化界、稳定性、一致性、收敛率、遗憾界）
  - `references/`：9 个参考文件（第 1–8 章 + 附录）
  - `examples/`：3 个案例（3-DNF 不可学、线性分类器 VC 维、UCB 多臂赌博机）
- **V 阶段**：
  - 章节标题与 catalog（README 目录表 + VitePress `config.mjs` 导航）对齐。发现两处源项目自身不一致：第 1 章源文件 H1 为"预备定理"但 catalog 为"预备知识"；第 3 章源文件 H1 为"复杂性分析"但 catalog 为"复杂度"。知识束统一采用 catalog 标题，并在参考文件中标注源 H1 差异。
  - 其余 6 章（可学性、泛化界、稳定性、一致性、收敛率、遗憾界）标题完全一致。
  - 校验 90 个内部交叉链接（`/datawhale/key-book/...`），全部解析到存在的文件。
  - 校验 frontmatter：1 个 index、7 个 concept、9 个 reference、3 个 example，type/bundle/sources/related 字段均合规。
  - 文件统计：概念 7、参考 9、案例 3，符合预期。

## 来源

- 仓库：https://github.com/datawhalechina/key-book
- 伴读对象：周志华等《机器学习理论导引》（机械工业出版社，2020）
- 许可证：CC BY-NC-SA 4.0
