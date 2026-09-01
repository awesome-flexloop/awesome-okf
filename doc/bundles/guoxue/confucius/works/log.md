# 更新日志

## 2026-08-31

### 创建
- 初始化 works bundle（孔子相关著作权威阅读教程），依据 Web 双信源（zh.wikipedia.org + ctext.org + 中国孔子网 chinakongzi.org + 出土文献研究论文）核对采集整理
- 创建 9 篇概念文档、3 篇示例文档、3 篇信源文档
- 建立与 think/laozi/boshu-reading、think/huangdi-neijing、think/confucian/four-books 的交叉引用

### 结构
- concepts/：00-shu-er-bu-zuo, 01-chunqiu, 02-shijing, 03-shangshu, 04-li-yue, 05-zhouyi-yizhuan, 06-lunyu, 07-banben-yuanliu, 08-guishu-bianwei
- examples/：01-chunqiu-bifa（春秋笔法三传对照）, 02-lunyu-xuandu（论语代表章句精读）, 03-shishu-xuandu（诗书选读）
- references/：01-authoritative-editions, 02-commentaries-graded, 03-sources-cross-ref
- facts.md：63 条零推测事实（F-001~F-063，每条含信源 URL）
- insights.md：4 条四元组洞察 + 3 个可复用阅读模式（归属辨析法、版本对照阅读法、注家分层选用法）

### 方法论
- 遵循 seven-concepts 场景4（知识沉淀）链路：R（信源采集与事实登记）→ I（洞察四元组）→ E（模式沉淀）→ V（对抗审查）→ C（原子提交与质量门）

### 对抗审查（V）
- 修正 F-016 信源 URL 篇名子路径（teng-wen-gong-shang → xia，与「滕文公下」篇名一致），并同步 references/01-authoritative-editions.md
- 精确化 references/02-commentaries-graded.md 注本登记口径：明确「有事实依据」与「通行经学传统」两类注本边界，避免用经文事实编号伪装注本事实
- 质量门通过：gates.bundles（14 域 58 组 321 束五面一致）、gates.toctrees（confucius scoped 断链 0）、gates.utf8（23 文件有效 UTF-8）