# GitHub Bundle 变更日志

## 2026-09-02 — 初始版本

**Migration**: 合并 learning 08/github-cli-wiki（gh 安装/基础命令/PR 工作流/Actions/高级用法/FAQ/速查 8 章）；舍弃源侧 log.md 与 retrospective.md（隐私元数据）。

- 基于简书连载《开源的世界》（nb/40234132）中 2 篇 GitHub 相关博文（2020 年前后）转化生成
- 覆盖 2 个概念文档 + 2 个信源登记文档
- 提取编号事实：F-225~F-229（创建 Gist）、F-201~F-212（GitHub Actions 手册）
- 主题覆盖：公开/机密 Gist 的区别与隐私边界、Gist 即 Git 仓库、创建步骤、嵌入文本字段与 GeoJSON 地图；Actions 核心概念、`.github/workflows` 目录约定、触发事件 `on`、`runs-on`、构建矩阵、checkout 引用语法、`jobs`/`needs` 依赖与状态徽章
- 时点处理：全部文档标注"基于 2020 年前后教程"，对已漂移内容（`ubuntu-18.04`、`actions/checkout@v1` 等 Actions 运行器与操作版本）加「现状」说明，不虚构当代行为
