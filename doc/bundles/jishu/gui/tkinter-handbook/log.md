# tkinter-handbook Bundle 变更日志

## 2026-09-02 — 初始版本

- 基于简书博客集《tkinter 手册》（作者简书 uid 1114626 / xinetzone，共 21 篇，2020-04 至 2021-02 发布；文集 /nb/ 链接未随抓取获得）整理生成
- 采用 blog-article-to-okf-wiki 七阶段工作流（敏感度预检→骨架判定→F 编号事实采集→P0 权威核验→三层知识拆分→信源先行生成→对抗审查）
- 覆盖 12 个概念文档 + 3 个示例文档 + 1 个信源登记文档（共 16 个内容文档），另含 concepts/examples/references 三个子目录 index.md、根 index.md 与本日志
- 知识聚类：F-THB-01/18/19/20 拆入入门与基础概念；F-THB-02/03 各自独立成篇；F-THB-04/13/20 的对话框/变量追踪/调度剪贴板合并为一篇；F-THB-05/06/07/12/16/17 拆为 Canvas 核心、画图函数、图片、交互四篇；F-THB-10/11/14/15 合并为多窗口篇；F-THB-21 独立 ttk 篇；F-THB-08/09 分别并入示例与画布交互篇
- 信源：F-THB-01 至 F-THB-21 逐篇登记（标题、/p/ 永久链接、抓取日期、字数/截图数/待更备注）；外部核验信源含 Python 官方文档 tkinter/tkinter.ttk、effbot Tkinterbook、TkDocs、标准库 tkinter/dnd.py 源码
- 30 张运行截图已本地化至 `_static/bundles/jishu/gui/tkinter-handbook/images/`（命名规则：<文章 slug>-1114626-<图床哈希>.webp）；21 个 math.jianshu.com 公式渲染图全部转写为行内文本/代码（F-01×1、F-02×3、F-05×7、F-06×7、F-16×3）
- 已知残缺与边界声明：
  - F-THB-12《Python 设置 Canvas 背景图片且支持全屏显示》为付费文章（1000 简书币），仅获免费试读；图片随窗口缩放重绘的实现代码不在试读范围，已在 concepts/09 与信源登记中显式标注，未臆造
  - F-THB-08（进度条，全文仅代码+效果图）、F-THB-18（资源篇，仅 8 个资源名称无链接）为作者待更状态；资源链接由知识包按名称核对官方入口给出并在信源登记中说明
  - F-THB-09 为标准库 tkinter/dnd.py 源码转载，用法提炼自模块 docstring
