# 变更日志

## 2026-09-12

- 初版 bundle 上线：源自腾讯文档《ToDesk AI 入门文档》（官方产品文档，9184 字，23 页 canvas 渲染页 Playwright 逐页截图 + 多模态 OCR 逐字转录）。
- 结构：concepts 4 篇（产品定位与演进 / 三大核心能力 / Computer Use 机制与边界 / 智能体技能与模型体系）+ examples 3 篇（安装登录与首次会话 / 定时任务跨设备与文件流转 / 自定义模型与技能管理）+ references 2 篇（F-001~F-058 事实清单 / P0 核验报告）。
- 骨架判定：操作可复现性两问皆"是"（安装/登录/定时任务/自定义模型均为可照做流程），故设 examples/。
- 核验：7 类 P0 声明 ✅ 4 / ⚠️ 3 / ❌ 0（⚠️ 均为单源或时效项，无核心声明失败），status: stable。
- 信源距离：官方发布（第一方产品文档）；官网 todesk.com / toodeskai.com 可达性核验通过。
### 2026-09-12 更新（官网二次采集）

- 信源扩展：新增 todeskai.com 官网首页采集（WebFetch），补充 F-059~F-070 共 12 条新事实。
- 新增内容：
  - concepts/04-browser-extension.md：浏览器插件概念文档（Chrome 扩展，四大能力）
  - examples/03-browser-extension.md：浏览器插件安装与使用实操
- 更新内容：
  - concepts/00-intro.md：版本时间线新增 3.1.0.0 条目；信源说明补充公司主体（上海久尺网络科技有限公司）
  - concepts/01-core-capabilities.md：新增"官网口径对比"节（四大能力 vs 三大能力）
  - examples/00-install-and-first-run.md：下载区补充 3.1.0.0 直链；新增 Android APK 安装
  - references/article-source.md：新增 I 节（F-059~F-070 官网二次采集）；疑点登记新增版本跳跃条目
  - references/verification.md：新增勘误-4/5 + 官网二次采集核验表
- 核验：6 类新增声明全部 ✅（浏览器插件/版本号/Android/公司主体/口径差异/下载直链）