# 更新日志

## 2026-08-30

### 创建
- 初始化 suanjing-reading bundle（think/suanxue 分组），中国数学典籍阅读教程
- 创建 14 篇概念文档（concepts/）、8 篇实践示例（examples/）、4 篇信源文档（references/）
- facts.md：96 条零推测事实（F-001~F-096），覆盖算经十书、算筹记数、周髀、九章、刘徽、孙子、张丘建、祖氏父子、宋元四大家、明清会通、出土文献 11 个分类；附锚点核验表 A-1~A-10
- insights.md：5 条四元组洞察（算法化传统vs演绎传统、十书体系化与制度支撑、宋元高峰后的中断、古今转译边界、问题驱动读法）与 mermaid 知识地图

### 结构
- concepts/：00-why-read-suanjing、01-history-overview、02-chousuan-numeration、03-jiuzhang-structure、04-jiuzhang-key-methods、05-liuhui-commentary、06-zhoubi-suanjing、07-suanjing-shishu、08-zu-chongzhi、09-song-yuan-peak、10-dayan-tianyuan-siyuan、11-ming-qing-transition、12-chinese-math-characteristics、13-reading-path
- examples/：01-fangtian-fractions、02-yingbuzu-double-false、03-fangcheng-negative、04-gougu-pythagoras、05-wuwuzhishu-crt、06-baiji-weng、07-geyuan-pi、08-reading-plan
- references/：online-sources（s- 级原典 10 个）、core-editions（e- 级点校本 6 个）、modern-studies（r- 级研究文献 8 个）、cross-ref（库内关联 6 个）

### 信源
- 原文以 ctext.org（《周髀》《九章》《海岛》《孙子》全文，附《四部丛刊》等底本 res 编号）、汉典古籍、中华文库、国学大师为在线入口
- 点校本依据钱宝琮《算经十书》（中华书局 1963）、郭书春/刘钝《算经十书》（辽宁教育 1998）、白尚恕《〈九章算术〉注释》（科学 1983）、李继闵《九章算术校证》（1993）、《中国科学技术典籍通汇·数学卷》（1993）
- 现代研究依据钱宝琮《中国数学史》、Needham SCC Vol.3、Martzloff（1997）、Chemla & Guo（2004）、Katz 主编 Sourcebook（2007）、吴文俊《中国数学史大系》

### 方法
- 七概念方法论 R→I→E：R 信源先行+事实采集（G1 零因果词）、I 四元组洞察（G2）、E 三层文档萃取（G3）
- examples 01-07 严格四段式：原文引录（注明底本+信源 id）→ 白话译文 → 现代数学解读（LaTeX/算法步骤/定理对照）→ 延伸（传播与优先权，采用审慎表述）