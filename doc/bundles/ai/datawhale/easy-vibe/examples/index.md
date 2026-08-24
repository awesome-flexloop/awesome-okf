# 示例索引

本目录收录 Easy-Vibe 项目中可直接复用的实践案例，帮助理解 Vibe Coding 工作流与工具链的具体用法。

## 示例清单

### [本地运行与构建示例](/ai/datawhale/easy-vibe/examples/01-local-dev-quickstart.md)

从零开始在本地启动 Easy-Vibe 文档站，涵盖依赖安装、开发服务器、生产构建与预览，以及 AI IDE 一键运行方式。

## 源码中的练习项目

Easy-Vibe 仓库的 `examples/` 目录还附带 4 个 Vibe Coding 练习项目，每个都含 `prompt.txt`（可直接喂给 AI IDE 的提示词）与参考图：

| 项目 | 类型 | 关键文件 |
|------|------|---------|
| `trae-3d-block-game/` | Electron + Vite 3D 方块游戏 | `electron/main.js`、`src/`、`vite.config.js`、`prompt.txt` |
| `trae-block-game/` | 单页方块游戏 | `index.html`、`prompt.txt` |
| `trae-linear-dashboard/` | Linear 风格仪表盘 | `index.html`、`prompt.txt` |
| `trae-screenshot-demo/` | 截图演示应用 | `index.html`、`script.js`、`styles.css`、`prompt.txt` |

这些项目展示了"一份 prompt.txt + 参考图 → AI 生成完整应用"的 Vibe Coding 实践模式。

```{toctree}
:hidden:

01-local-dev-quickstart
```
