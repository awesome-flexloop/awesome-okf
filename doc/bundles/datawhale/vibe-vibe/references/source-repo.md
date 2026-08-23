# 信源：Vibe Vibe 官方仓库

## 基本信息

| 项目 | 内容 |
|------|------|
| 仓库 | https://github.com/datawhalechina/vibe-vibe |
| 组织 | Datawhale（datawhalechina） |
| 在线站点 | https://www.vibevibe.cn |
| 包名 | vibe-vibe-tutorial |
| 版本 | 0.0.4（Alpha，内部预览版） |
| 许可证 | CC BY-NC-SA 4.0（README 声明） |
| 项目性质 | VitePress（Vue 3）静态文档站，AI Vibe Coding 系统化教程 |
| 包管理器 | pnpm 10.21.0 |
| VitePress 版本 | ^1.6.4（稳定版） |
| Vue 版本 | ^3.5.25 |
| 支持语言 | 简体中文、英语 |
| 维护状态 | 2026-01-25 恢复开发，持续更新中 |

## 关键文件索引

| 文件 | 作用 |
|------|------|
| `README.md` | 项目介绍、核心理念、四大板块目录、快速开始、私有化部署、贡献者 |
| `README.en.md` | 英文版 README |
| `package.json` | 依赖与脚本定义（vibe-vibe-tutorial@0.0.4） |
| `pnpm-lock.yaml` | pnpm 锁文件 |
| `Dockerfile` | 多阶段构建（node:24-alpine + nginx:alpine） |
| `docker-compose.yml` | Docker Compose 编排（端口 1024:80、健康检查） |
| `docs/index.md` | 首页（含浏览器语言自动重定向脚本） |
| `docs/zh/index.md` | 中文首页（hero + features + 学习路径） |
| `docs/en/index.md` | 英文首页（完整翻译） |
| `docs/public/llms.txt` | AI 助手导航文件（教学路由表，173 行） |
| `docs/public/logo.png` | 站点 Logo |
| `docs/deployment/index.md` | 私有化部署指南（四种方式 + 离线注意事项） |
| `docs/.vitepress/config.mts` | 站点主配置（locales、nav、SEO、head、markdown） |
| `docs/.vitepress/modules/utils.ts` | frontmatter 解析、阅读时间、JSON-LD 等工具 |
| `docs/.vitepress/modules/seo.ts` | 面包屑结构化数据 |
| `docs/.vitepress/modules/faq.ts` | FAQ Schema 构建 |
| `docs/.vitepress/modules/feed.ts` | RSS/robots.txt 生成 |
| `docs/.vitepress/modules/sitemap.ts` | 图片 sitemap |
| `docs/.vitepress/modules/defaults.ts` | 自动描述、难度推断、相关页推荐 |
| `docs/.vitepress/theme/index.ts` | 主题入口 |
| `docs/.vitepress/theme/components/` | 100+ 交互 Vue 组件（按章节编号前缀） |
| `docs/.vitepress/theme/components/LocaleSwitch.vue` | 语言切换组件 |
| `docs/.vitepress/theme/components/BasicEditionUpdateBox.vue` | 基础篇版本提示组件 |
| `docs/.vitepress/theme/composables/useAnimation.ts` | 动画复用逻辑 |
| `docs/Basic/index.md` | 基础篇 v2 首页（个人主页+数字分身案例说明） |
| `docs/Basic/00-preface/` ~ `06-launch/` | 基础篇 7 章内容 |
| `docs/Basic-old/` | 旧版基础篇（保留，5 章+附录） |
| `docs/Advanced/index.md` | 进阶篇首页（16 章序言可读） |
| `docs/Advanced/01-environment-setup/` ~ `16-user-feedback-iteration/` | 进阶篇 16 章 |
| `docs/Articles/index.md` | 优质文章篇首页 |
| `docs/Articles/01-core-concepts/` ~ `06-business-trends/` | 优质文章 6 大分类 |
| `docs/Practice/` | 实践案例篇 |
| `docs/en/Basic/`、`docs/en/Advanced/`、`docs/en/Articles/`、`docs/en/Practice/` | 英文版完整镜像 |

## 目录速览

```
vibe-vibe/
├── docs/
│   ├── .vitepress/
│   │   ├── config.mts               # 站点主配置
│   │   ├── modules/                 # SEO、feed、sitemap、faq、defaults 模块
│   │   └── theme/
│   │       ├── components/          # 100+ 交互组件（01-* ~ 16-* 编号前缀）
│   │       ├── composables/         # useAnimation
│   │       ├── styles/              # variables.css
│   │       ├── types/               # components.ts
│   │       ├── custom.css
│   │       └── index.ts
│   ├── public/
│   │   ├── logo.png
│   │   ├── favicon.ico
│   │   ├── llms.txt                 # AI 助教路由表
│   │   ├── giscus/                  # 评论主题 CSS
│   │   ├── images/                  # 教程截图（按板块分目录）
│   │   └── components/              # 静态 HTML 演示
│   ├── index.md                     # 首页（语言重定向）
│   ├── zh/index.md                  # 中文首页
│   ├── en/index.md                  # 英文首页
│   ├── Basic/                       # 基础篇 v2（中文，00-06 章 + 附录）
│   ├── Basic-old/                   # 旧版基础篇（保留）
│   ├── Advanced/                    # 进阶篇（中文，01-16 章）
│   ├── Articles/                    # 优质文章篇（中文，6 分类）
│   ├── Practice/                    # 实践案例篇（中文）
│   ├── en/                          # 英文版镜像
│   │   ├── Basic/  Advanced/  Articles/  Practice/
│   └── deployment/index.md          # 私有化部署指南
├── Dockerfile                       # 多阶段构建
├── docker-compose.yml               # 容器编排
├── package.json
├── pnpm-lock.yaml
├── README.md
└── README.en.md
```

## 核心贡献者

| 姓名 | 职责 |
|------|------|
| 符航康 | 项目负责人 & 核心贡献者 |
| 齐国皓 | 项目负责人 & 核心贡献者 |
| 刘磊 | 实践篇贡献者、图像贡献者 |
| 陈俊希 | 优质文章篇板块贡献者 |
| 金龙 | 实践篇板块贡献者 |
| 舒璐璐 | 实践篇板块贡献者 |

## 关联站点

- https://www.vibevibe.cn — 教程主页
- https://cclog.vibevibe.cn — Claude Code 全特性速览（220+ 版本、1000+ 更新）

## 采集说明

- 本信源于 2026-08-23 基于工作区副本采集（Alpha v0.0.4）。
- 事实清单见 [/datawhale/vibe-vibe/spec/facts.md](/datawhale/vibe-vibe/spec/facts.md)。
- 架构洞察见 [/datawhale/vibe-vibe/spec/insights.md](/datawhale/vibe-vibe/spec/insights.md)。
