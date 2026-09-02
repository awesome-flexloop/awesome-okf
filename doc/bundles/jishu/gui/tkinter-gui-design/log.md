# 变更日志

## 2026-09-02 — 初始生成（v1）

- 来源：简书文集《tkinter GUI 设计》（作者水之心/xinetzone，2019-12-30 ~ 2020-06-15），34 篇公开博文（F-TGD-01 ~ F-TGD-34），Python 标准库 tkinter（Tcl/Tk）系统化学习笔记
- 按 blog-article-to-okf-wiki 流程生成（技术教程完整骨架，含 examples/）
- 信源阶段：references/sources.md 登记 34 篇原文（标题/链接/抓取日期 2026-09-02/备注）；第 13 篇付费文章仅登记可见元信息，多篇作者自标注"更新中/待更"短文已如实备注
- 内容阶段：
  - index.md（知识地图 Mermaid + 目录 + 推荐学习路径）
  - concepts/index.md + 10 篇概念文档（基础概念、基础部件、几何管理器、高级部件、菜单/窗口/对话框、友好界面与 ToolTip、事件与变量、Text、Canvas、样式/MVC/资源）
  - examples/index.md + 12 篇实战/示例文档（登录窗口、画图工具、图形操作、标注模板、小例子 18 则、Canvas 例子 6 则、文本编辑器、颜色形状选择器、计算器、动画拖拽、Matplotlib 嵌入、透明度）
  - references/index.md + sources.md
  - log.md
- 视觉资产：142 张原文截图本地化至 `_static/bundles/jishu/gui/tkinter-gui-design/images/`（引用路径 `../../../../../_static/...`），文档引用 142/142 零缺失；50 张数学公式图（math.jianshu.com，无本地化映射）按姊妹束 tkinterx-handbook 惯例转写为行内文本
- 自检：文件清单齐全（concepts 10 + examples 12 + references 2 + index/log 2）；图片计数对账 142=142；concepts/examples 无 jianshu 图床 URL、无 file 协议绝对路径、无 images 相对目录引用；53 处畸形图片语法（叹号左括号后缺失左方括号）已全部修正为标准图片语法
- status: stable；stale_after: 2027-09-02（tkinter 为 Python 标准库，API 长期稳定，按年度复核）