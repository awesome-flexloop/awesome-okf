# 更新日志

## 2026-09-02

### 新增
- 意象配图 1 张（水墨意象类，存 doc/_static/bundles/yixue/tcm/classics/nanjing/images/）：束封面 `nanjing-cover.jpg`（束根 index.md 首屏）
- Mermaid 结构图 3 张：concepts/01-structure-81「81 难六部结构」、concepts/02-relation-to-neijing「与内经关系」、concepts/04-commentators「注家谱」

### 合规
- 纯视觉增量，知识内容零改动：正文、frontmatter、表格、链接、references 均未增删改；V 阶段独立对抗审查 A/B/C 全通过——3 张 Mermaid 图六规则机检合规、图中事实逐字核验通过、Sphinx 构建本束零错误零告警、单页配图 ≤2 配额达标

## 2026-08-30

### 创建
- 初始化 nanjing bundle：《难经》（黄帝八十一难经）阅读教程，落位 tcm/classics/（中医经典域第 2 束）
- 概念文档 6 篇、精读示例 2 篇、信源文档 2 篇，共 10 个内容文档；另含束根与三个子目录索引及本日志

### 方法
- seven-concepts-cmd 场景 4（知识沉淀）链路 R→I→E：R 阶段双信源核对（维基文库本为底本附校勘记 19 条，国学导航本六部分类本为主对校，古诗文网为第三参证；ctext.org 访问受限未采用）
- 事实登记 89 条（NJ-001~NJ-089），81 难题名/主题全录一条不少；精读 20 难全文，实质异文 26 处（沿用 facts 登记 15 处、精读新发现 11 处）
- 托名与成书五说并列登记不裁决；义理级两读"故知肾有一也/二也"（维基文库本/国学导航本）全文并列标注

### 结构
- concepts/：00-what-is-nanjing, 01-structure-81, 02-relation-to-neijing, 03-core-concepts, 04-commentators, 05-legacy
- examples/：first-nan-cunkou, nanjing-neijing-parallel
- references/：sources-editions, commentary-grades

### 合规
- 束根首屏医学免责声明（精确文本）；全部内容文档尾注免责提醒
- 引用规范：一律"《难经》第 N 难作某"，禁用"秦越人说"；原文标注底本信源；异文显式标注"维基文库本作某/国学导航本作某"
- 注家对照：登记谱系立场（吕广/杨玄操/滑寿 + 维基文库校勘记/中医宝典认证词条），不转录受版权保护注文；徐大椿《难经经释》作补位登记并标注无登记信源
- 交叉引用全部为束内相对路径（带 .md 后缀），无指向 bundles/ 树外的本地链接，无 file:/// 链接

### 遗留项
- 徐大椿《难经经释》及《难经疏证》《古本难经阐注》作者信息未纳入本次事实采集，待补源后升级 commentary-grades 条目
- 二十七难"霈"上字符维基文库页面显示不全（国学导航本作"留需"），存疑待核
- 命门学说后世发挥（注家具体论证）未采集，05-legacy 仅登记起点与框架
