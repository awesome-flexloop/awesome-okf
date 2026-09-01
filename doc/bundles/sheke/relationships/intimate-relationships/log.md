# 更新日志

## 2026-08-30

### 创建

- 知识包 `intimate-relationships` 创建，收录罗兰·米勒《亲密关系》（*Intimate Relationships*，McGraw-Hill）的中文转述知识体系
- 完成 R 阶段公开信源调研：作者身份、版次沿革（1985 第1版至第9版）、三个中译本、14章结构、八大理论脉络均经两个以上独立信源交叉核验
- 全知识包 16 个文件，正文为原创中文转述，不含原书版权材料的复制

### 结构

| 路径 | 类型 | 说明 |
|------|------|------|
| index.md | OKF | 知识包入口、快速导航、学习路径 |
| facts.md | Facts | 43 条零推测事实与 24 个合规信源编号对照 |
| insights.md | Insights | 4 条四元组洞察 + Mermaid 知识地图 |
| concepts/index.md | —— | 概念层索引（无 frontmatter） |
| concepts/00-book-and-science.md | Concept | 著作定位：亲密关系作为实证科学 |
| concepts/01-research-methods.md | Concept | 研究方法与证据标准 |
| concepts/02-attraction-cognition.md | Concept | 吸引力与社会认知 |
| concepts/03-communication-conflict.md | Concept | 沟通与冲突（含戈特曼四骑士） |
| concepts/04-interdependence-maintenance.md | Concept | 相互依赖与关系维持 |
| examples/index.md | —— | 实践层索引（无 frontmatter） |
| examples/01-relationship-reflection.md | Example | 关系自评与反思清单（原创编排） |
| examples/02-reading-path.md | Example | 阅读路径与实践建议 |
| references/index.md | —— | 信源层索引（无 frontmatter） |
| references/01-editions.md | Reference | 版本与译本信息 |
| references/02-further-reading.md | Reference | 学术脉络与一手文献 |
| log.md | —— | 本日志 |

### 核验与合规

- P0 事实（作者身份、版次、中译本、章节结构、理论归属）均通过出版社官网、高校馆藏/课程文件、正规图书目录或学术论文全文双信源核验
- 第7版信息经补充调研由合法书目源（Biblio、Alibris）核验后写入；调研阶段接触过的盗版/非法下载站点未出现在任何产出物中
- 全知识包无原书直引（0 处），无版权量表复制；自评清单为依据教材框架的原创设计
- 放弃的未核验事实见 [facts.md 末尾](facts.md)
- 收尾自检结果：16 个文件齐备；12 个内容文档 frontmatter type 全部正确；根/概念/实践/信源四层 toctree 全覆盖本层内容文档；盗版域名与 file 协议绝对路径链接正则复检零命中；概念文档行数 82–93 行，均在 80–150 行区间
- 自检中移除 facts.md 内一处调研期残留的不合规销售渠道书目信源，第8版事实仅以 McGraw-Hill 官方改版说明为据；concepts/00 补充两段方法论转述使行数达标
## 2026-08-31

### 评审打磨（独立评审 V 阶段闭环）

- index.md 的 toctree 补齐 `:hidden:` 选项并去除条目的 `.md` 后缀（docname 形式），与其余 5 束及 OKF 范式对齐。
