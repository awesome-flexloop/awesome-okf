# Log：WorkBuddy 沙箱公网端点

## 2026-09-16

- 建立 `workbuddy-sandbox-public-endpoint` 知识包。
- 提取微信公众号「AI工具实测派」博文全文，登记 F-001~F-027 博文事实。
- 使用腾讯云 WorkBuddy Enterprise 产品概述、WMA 产品介绍、CodeBuddy Remote Control 文档、CodeBuddy IDE 更新记录完成官方交叉核验。
- 实时请求 3 个公开 `*.agentos-app.net` 案例与 1 个 `app.workbuddy.host` 示例，补充 F-028~F-039。
- 核验结论：12 项 P0/P1 声明中 7✅、5⚠️、0❌；核心公网 HTTPS 能力成立，内部 CLB/sandbox-proxy 链路未官方证实。
- 按操作可复现性两问判定不设 `examples/`，生成 3 篇概念文档与 2 篇信源文档。
- V 阶段独立对抗审查：P0=0、P1=2、P2=7；已补 5 个内容文件的 `verified` 字段、3 个实时实证 URL、CLB 术语说明、证据快照与安全提示。
- 机械门禁：本束专项检查通过（9 文件、8 toctree 条目、39 对 F 编号、无断链/敏感绝对路径）；`python scripts/check-utf8.py` 通过（10412 个文件）。
- 全库计数与 toctree 在并行会话工作树短暂收敛时曾通过（9 域 / 59 组 / 555 束；全部 index.md 引用有效）；最终复跑受其他会话未接入新增束影响再次失败，失败清单不含本束路径，需并行工作收敛后复跑全库门禁。
- `invoke gates.*` 在当前 Anaconda 环境因 `invocations` 分发包元数据缺失无法导入，未声称 invoke 门禁通过；已直接运行任务底层脚本与本束专项脚本完成等效验证。

## 2026-09-16：横向对标增强

- 按用户要求对标 TraeCode、TraeWork、豆包工作，新增 F-040~F-052 共 13 条事实。
- 新增 `concepts/03-platform-comparison.md`，区分 WorkBuddy/CloudStudio、TraeCode/Vercel、TRAE CN/IGA Pages、TraeWork/BytePlus Pages、豆包工作云电脑五种公网化路径。
- 官方确认：TraeCode 国际版 SOLO 经 Vercel 部署；TRAE CN 当前未内置一键部署，需接 IGA Pages；TraeWork 经 BytePlus Pages Skill 发布且临时预览约 3 小时重置；豆包工作云电脑支持隔离后台执行。
- 豆包工作“公网 IP / EdgeOne 部署”仅获得第三方实测支持，官方任务须知未直接确认，正文标记为 ⚠️。
- 独立 V 审查结果 P0=0、P1=2；已补第三方实测 URL，并将全部导航中的事实范围同步为 F-001~F-052。
- 增强后本束共 10 个 Markdown 文件；专项 toctree、链接、frontmatter 与 F-001~F-052 双份编号检查通过。
