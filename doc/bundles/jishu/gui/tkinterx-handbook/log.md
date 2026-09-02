# tkinterx-handbook Bundle 变更日志

## 2026-09-02 — 初始版本

- 基于简书博客集《tkinterx 手册》（简书文集 nb/45403586，作者 xinetzone，共 5 篇）整理生成
- 采用 blog-article-to-okf-wiki 七阶段工作流（敏感度预检→骨架判定→F 编号事实采集→P0 外部核验→知识拆分→信源先行生成→对抗审查）
- 覆盖 6 个概念文档 + 3 个示例文档 + 1 个信源登记文档
- 信源：F-TXH-01 至 F-TXH-05 逐篇登记；外部核验信源含 PyPI（tkinterx 0.0.9，2020-05-30，维护者 xinetzone，MPL 2.0）与 GitHub（xinetzone/pychaos）
- 15 张运行截图本地化至 images/ 目录（命名规则：<文章 slug>-1114626-<图床哈希>.webp）；3 个数学公式转写为行内文本
- 已知残缺：F-TXH-04《tkinterx 之抠图工具》为作者待更状态，仅 1 张效果图与 `python draw_graph.py` 运行说明，未提供源码与 API，已在概念文档 06 与信源登记中显式标注，未臆造内容
## 待办（资产落地）

- `images/` 目录下 15 张截图二进制文件需从 `raw/images/` 复制落地：源文件名为 `1114626-<哈希>.webp`，目标文件名按 `<文章 slug>-1114626-<哈希>.webp` 规则重命名（示例：`raw/images/1114626-8975fb2c9834b284.webp` → `images/1a08da0a098f-1114626-8975fb2c9834b284.webp`）；15 组哈希与文章归属见 references/sources.md「图片本地化说明」与 concepts/examples 各文档的图片引用。