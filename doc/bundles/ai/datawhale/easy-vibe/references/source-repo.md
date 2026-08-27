# 信源：Easy-Vibe 官方仓库

## 基本信息

| 项目 | 内容 |
|------|------|
| 仓库 | https://github.com/datawhalechina/easy-vibe |
| 组织 | Datawhale（datawhalechina） |
| 在线文档 | https://datawhalechina.github.io/easy-vibe/ |
| 许可证 | CC BY-NC-SA 4.0 |
| 项目性质 | VitePress（Vue 3）文档站，AI Vibe Coding 教程 |
| Node 要求 | >= 18.0.0 |
| VitePress 版本 | ^2.0.0-alpha.16 |

## 关键文件索引

| 文件 | 作用 |
|------|------|
| `README.md` | 项目介绍、学习路径、新闻、贡献者 |
| `AGENTS.md` | 通用 AI Agent 仓库指南 |
| `CLAUDE.md` | Claude Code 专用详细指南 |
| `llms.txt` | AI Agent 导航地图（决策树+文章索引） |
| `package.json` | 依赖与脚本定义 |
| `docs/.vitepress/config.mjs` | 站点主配置（10 语言、导航、侧边栏、SEO、base 路径） |
| `docs/.vitepress/theme/index.js` | 主题入口与 200+ 交互组件注册 |
| `docs/.vitepress/theme/components/WelcomeScreen.vue` | 欢迎页 SVG 描边动画 |
| `docs/index.md` | 首页语言自动重定向逻辑 |
| `docs/welcome.md` | 欢迎页入口 |
| `docs/zh-cn/index.md` | 中文首页 hero |
| `docs/zh-cn/guide/introduction.md` | 项目介绍与三阶段路径 |
| `docs/DEPLOYMENT.md` | 部署说明与故障排查 |
| `scripts/build-locales.mjs` | 多语言顺序构建脚本（含文件锁） |
| `scripts/generate-sitemap.mjs` | sitemap.xml 与 robots.txt 生成 |
| `scripts/build-latex-book.mjs` | PDF（XeLaTeX）电子书构建 |
| `scripts/build-epub.mjs` | EPUB 电子书构建 |
| `scripts/build-books.mjs` | 多语言电子书编排 |
| `tools/translation/check-localization.mjs` | 附录组件 i18n 翻译缺失扫描 |
| `vercel.json` | Vercel 部署与缓存/安全头配置 |
| `Dockerfile` | 魔搭创空间镜像（Node 构建 + Nginx，端口 7860） |
| `nginx.conf` | Nginx 配置 |
| `.github/workflows/deploy.yml` | GitHub Pages 部署工作流 |
| `.github/workflows/release-books.yml` | tag 触发 PDF/EPUB Release 工作流 |
| `examples/` | 4 个练习项目（均含 prompt.txt） |

## 目录速览

```
easy-vibe/
├── docs/
│   ├── .vitepress/        # 配置、主题、组件、侧边栏
│   ├── public/            # 静态资源（llms.txt、favicon、sitemap）
│   ├── index.md           # 语言重定向
│   ├── welcome.md         # 欢迎页
│   ├── zh-cn/  en/  zh-tw/  ja-jp/  ko-kr/
│   ├── es-es/  fr-fr/  de-de/  ar-sa/  vi-vn/
│   └── DEPLOYMENT.md
├── assets/                # 仓库级图片
├── scripts/               # 构建与维护脚本
├── tools/translation/     # i18n 检查工具
├── examples/              # 练习项目
├── docs-readme/           # 10 语言 README
├── package.json
├── vercel.json
├── Dockerfile
├── nginx.conf
├── llms.txt
├── AGENTS.md
└── CLAUDE.md
```

## 采集说明

- 本信源于 2026-08-23 基于 `main` 分支工作区副本采集。
- 事实清单见 [/datawhale/easy-vibe/spec/facts.md](../spec/facts.md)。
- 架构洞察见 [/datawhale/easy-vibe/spec/insights.md](../spec/insights.md)。
