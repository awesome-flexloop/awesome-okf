# 变更日志

## 2026-09-02 — 初始生成（v1）

- 来源：简书文集《Qt for Python》（nb/46707335，作者水之心/xinetzone，2020 年），33 篇公开博文
- 按 blog-article-to-okf-wiki 七阶段流程生成（技术教程完整骨架，含 examples/）
- R 阶段：Kimi WebBridge 浏览器自动化枚举章节 + shakespeare/v2 API 全文抓取；F-001 ~ F-111 事实登记（99 篇内事实 + 12 条跨篇 P0 事实）；10 项 P0 核验 9 ✅ + 1 勘误（WebKit 弃用版本 Qt 5.5，非 5.6）
- I 阶段：两问判定含可复现操作 → 完整骨架；归属 jishu 域新建 gui 分组
- E 阶段：
  - index.md
  - concepts/index.md + 8 篇概念文档（GUI 术语、Qt 架构、双绑定差异、元对象信号槽事件、绘图系统、图像类、Graphics View、资源与 QML）
  - examples/index.md + 33 篇原文完整转换（代码块/截图/链接保留）
  - references/index.md + article-source.md + verification.md
  - log.md
- 视觉资产：103 张原文截图本地化至 _static/bundles/jishu/gui/qt-for-python/images/；Mermaid 知识地图
- status: verified；stale_after: 2027-09-02（Qt 核心机制稳定期，按年度复核 PySide6 迁移信息）
