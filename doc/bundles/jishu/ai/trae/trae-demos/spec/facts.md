# TRAE Demos 源码事实清单

## 项目基本信息

- F-001: 项目为社区驱动的 TRAE 构建项目展示平台，采用 MIT License，提交项目版权归原作者所有。来源：README.md
- F-002: 项目横幅图片为 `./assets/image/Demos.gif`。来源：README.md
- F-003: 提供中英文双语切换：English 链接 ./README.md，中文链接 ./README.zh-CN.md。来源：README.md
- F-004: 根目录包含 README.md（英文）、README.zh-CN.md（中文）、CONTRIBUTING.md、CONTRIBUTING.zh-CN.md、LICENSE 文件，以及 demos/、assets/image/、.github/ISSUE_TEMPLATE/ 目录。来源：目录结构 `d:\spaces\SpecWeave\external\libs\ai\trae-community\trae-demos\`

## 投稿与审核机制

- F-005: 投稿 4 项 Must Have 标准：使用 TRAE 作为核心技术、可访问（开源仓库或在线演示）、代码质量良好且有基本文档、完成度较高（polished）。来源：README.md
- F-006: 投稿流程为：检查要求 → 通过 Issue 模板提交（英文 submit_demo_en.yml / 中文 submit_demo_zh.yml）→ 24 小时内确认 → 3-5 个工作日审核 → 通过后展示。来源：README.md
- F-007: CONTRIBUTING.md 定义了 5 个项目分类：Web Applications、Tools & Utilities、Games、AI Applications、Other。来源：CONTRIBUTING.md
- F-008: 审核评分权重：TRAE Usage(40%)、Code Quality(25%)、Completeness(20%)、Documentation(15%)。来源：CONTRIBUTING.md
- F-009: Issue 模板配置 `blank_issues_enabled: false`，提供 1 个联系链接指向 `https://github.com/orgs/trae-community-org/discussions` 讨论区。来源：config.yml
- F-010: ISSUE_TEMPLATE 目录包含 7 个 YAML 文件：config.yml、report_demo.yml、report_demo_en.yml、submit_demo_en.yml、submit_demo_zh.yml、update_demo.yml、want_demo.yml。来源：目录结构 `d:\spaces\SpecWeave\external\libs\ai\trae-community\trae-demos\.github\ISSUE_TEMPLATE\`

## Demo 内容组织

- F-011: Demo 文件存放在 `demos/period-N/` 目录下，按"期"（period）组织，当前仅有 `period-1/` 目录。来源：目录结构 `d:\spaces\SpecWeave\external\libs\ai\trae-community\trae-demos\demos\`
- F-012: 每个 Demo 文件命名为 `demo-N.md`（英文）和 `demo-N.zh-CN.md`（中文），当前 period-1 下有 demo-1 和 demo-2 共 4 个文件。来源：目录结构 `d:\spaces\SpecWeave\external\libs\ai\trae-community\trae-demos\demos\period-1\`
- F-013: 英文 README 的"Past Issues"表格标注 Issue #1 包含 2 个项目，发布时间 2026.03。来源：README.md
- F-014: 中文 README 的"往期内容"表格标注第 1 期包含 2 个项目，发布时间 2026.03。来源：README.zh-CN.md

## Demo #1: Minecraft Guilin City Walk

- F-015: Demo #1 为 "Minecraft Guilin City Walk | 桂林像素漫步"，作者 @MU-ty，类型 Web App，技术栈 JavaScript/TypeScript。来源：demo-1.md
- F-016: Demo #1 文件头标注"Issue: #1 | March 2026"，中文版标注"收录于：第 1 期 | 2026年3月"。来源：demo-1.md / demo-1.zh-CN.md
- F-017: Demo #1 GitHub 仓库为 `https://github.com/MU-ty/Minecraft-Guilin-City-Walk-TRAE`，在线演示为 `https://mu-ty.github.io/Minecraft-Guilin-City-Walk-TRAE/`。来源：demo-1.md
- F-018: Demo #1 核心亮点 4 项：PixelMap 像素地图（SVG 交互式放射状路径图）、TRAE 在桂林（记录社区活动+资料下载+地图标记）、MC 风格 UI（Press Start 2P 像素字体+方块按钮）、管理员系统（Coffee Chat 预约+GitHub 互动）。来源：demo-1.md
- F-019: Demo #1 本地运行命令：`git clone` → `npm install` → `npm run dev`。来源：demo-1.md
- F-020: Demo #1 预览图片使用 GitHub user-attachments 资源链接（2 张截图）。来源：demo-1.md

## Demo #2: TraeClaw

- F-021: Demo #2 为 "TraeClaw"，作者 @firerlAGI，类型 Plugin/Extension，技术栈 JavaScript/TypeScript。来源：demo-2.md
- F-022: Demo #2 英文文件头标注"Issue: #2 | April 2026"，中文文件头标注"收录于：第 2 期 | 2026年4月"，与 README 中"Issue #1"标注存在不一致。来源：demo-2.md / demo-2.zh-CN.md
- F-023: Demo #2 GitHub 仓库为 `https://github.com/firerlAGI/TraeClaw`，无在线演示（标记为 _No response_）。来源：demo-2.md
- F-024: Demo #2 核心亮点 3 项：打通本地调用链路（OpenClaw→trae_delegate→TraeClaw→Trae Desktop）、npm 分发（traeclaw npm 包）、完善排障体系（health/ready/chat 排障入口+文档）。来源：demo-2.md
- F-025: Demo #2 安装方式非传统命令行，而是向 OpenClaw 发送一段自然语言指令（让 OpenClaw 阅读 AGENTS.md 和 AI_INSTALL.zh-CN.md 后通过 npm 安装并验证）。来源：demo-2.md
- F-026: Demo #2 附微信公众号文章链接：`https://mp.weixin.qq.com/s/WYOO8WOxX8i-r9lG6hLtAA`。来源：demo-2.md
