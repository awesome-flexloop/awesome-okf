# P0 核验报告

> 核验日期：2026-08-28
> 核验方法：WebSearch 权威来源交叉验证
> 核验结果：**3✅ 2⚠️ 1❌**
> ⚠️ 本报告包含一个 ❌ 失败项（核心声明），bundle status 标记为 `flagged`

## 核验结论总表

| 序号 | 声明项 | 结论 | 关键差异 |
|------|--------|------|----------|
| 1 | Tushare 平台描述 | ✅ 通过 | 无 |
| 2 | WorkBuddy 平台描述 | ✅ 通过 | 补充：腾讯出品，MCP协议，80+连接器 |
| 3 | 千问办公描述 | ⚠️ 部分通过 | 开发主体为钉钉业务线；遗漏鸿蒙平台 |
| 4 | TraeWork 描述 | ✅ 通过 | 无 |
| 5 | Tushare 三平台官方预置 | ❌ **失败** | 核心声明未获证实，详见下方 |
| 6 | Tushare MCP 从手动变预置 | ⚠️ 部分通过 | 手动配置属实，"变预置"无证据 |

## ❌ 失败项详情（第5项）

### 博文声称

> "Tushare数据已同步上架到国内三大主流AI办公平台……从众多三方发布的野生插件，走向了平台认可的官方预置连接器。"

### 核验发现

#### 发现1：日期张冠李戴

2026-08-25 确实有一篇"多平台上架"新闻，但主体是**启信慧眼**（企业数据查询服务），而非 Tushare：

> "启信慧眼MCP已上架TraeWork、千问办公、MiniMax Agent、ima等多个主流平台"
> ——搜狐，2026-08-25，https://m.sohu.com/a/1066960913_122850697/

博文可能将启信慧眼的上架新闻误归为 Tushare，或在同一日期发布了类似但未获证实的公告。

#### 发现2：官方支持平台列表不匹配

Tushare 官方 MCP 文档（https://tushare.pro/document/1?doc_id=463 ）列出的支持平台：

| 类别 | 平台 |
|------|------|
| OpenClaw 龙虾系 | OpenClaw、WorkBuddy、KimiClaw、MaxClaw、CoPaw、悟空 |
| Vibe Coding | CodeBuddy、ClaudeCode、Cursor、**Trae**、Cline、Lingma |

关键差异：
- 列出的是 **"Trae"**（编程 IDE），而非博文声称的 **"TraeWork"**（办公工作台）
- **完全没有提到千问办公/QwenWork**

#### 发现3：仍为手动配置

Tushare 官方 MCP 文档显示，用户仍需：
1. 登录 Tushare 个人中心
2. 拷贝 MCP key
3. 手动添加到各平台的 MCP 配置中（如编辑 `~/.openclaw/openclaw.json`）

这属于"自定义连接器"范畴，并非"官方预置、开箱即用"。

#### 发现4：WorkBuddy 上为社区 Skill

WorkBuddy 技能市场中存在 `tushare-finance` 技能，但：
- 作者为 stanleychanh（社区贡献者），非 Tushare 官方账号 waditu-tushare
- 需用户手动搜索、安装、配置 Token
- 不等同于"官方预置连接器"

Tushare 官方另有 Skill `tushare-data`（GitHub: waditu-tushare/skills），可通过 `clawhub install` 安装，但同样需手动配置。

### 可能的解释

1. **预告/计划**：博文可能宣布的是计划中或正在进行的对接，尚未正式上线
2. **混淆产品**：将 Trae（IDE）的 MCP 支持混淆为 TraeWork（工作台）的预置连接器
3. **社区贡献误述**：将社区 Skill 描述为官方预置
4. **营销表述**：使用"官方预置"等措辞提升产品形象，但实际仍需手动配置

### 处理方式

- bundle `status` 标记为 `flagged`
- index.md 顶部添加 ⚠️ 重要核验提示
- concepts/02-integration-status.md 逐条对照博文声称与核验事实
- 所有基于 F-006 的用例描述标注为"设想效果"

## 逐项详情

### 1. Tushare 平台 ✅

- 官方文档确认 token 认证、Pandas DataFrame 返回格式
- 覆盖股票/基金/期货/债券/外汇/宏观等全品类
- "免费"有积分门槛：注册送100积分，高级接口需2000+积分
- 来源：tushare.pro/document/1?doc_id=40

### 2. WorkBuddy 平台 ✅

- 腾讯出品的 AI 办公智能体
- 连接器基于 MCP 协议，内置 80+ 连接器
- 支持 Ask/Plan/Craft 三种工作模式
- 支持自定义 MCP 连接器
- 来源：腾讯云开发者社区、掘金

### 3. 千问办公 ⚠️

- 产品存在，桌面+网页+钉钉端
- **开发主体**：阿里钉钉业务线主导（非"千问团队"），整合 QoderWork/悟空/MuleRun
- **平台支持**：macOS 14+、Windows 10+、**HarmonyOS 6.1+**（博文遗漏鸿蒙）
- 连接器机制属实
- 来源：qwenwork.cn/download、help.aliyun.com/zh/qwenwork

### 4. TraeWork ✅

- 字节跳动 TRAE 品牌 AI 原生工作台
- 三端：网页版(work.trae.ai)/桌面版/移动版
- 三模式：Work/Code/Design
- Design 模式于 2026-06-25 发布
- 来源：docs.trae.ai、trae.ai

### 6. Tushare MCP ⚠️

- MCP 确实存在，手动配置流程属实
- 官方 Skill `tushare-data` 存在
- 但"从野生插件变为官方预置连接器"无证据支持
- 官方文档仍展示手动配置流程
- 来源：tushare.pro/document/1?doc_id=463、github.com/waditu-tushare/skills

## 权威来源汇总

| 来源 | URL | 用途 |
|------|-----|------|
| Tushare MCP 文档 | tushare.pro/document/1?doc_id=463 | 支持平台、配置流程 |
| Tushare AI 适配指南 | tushare.pro/document/1?doc_id=473 | 三层架构 |
| Tushare Skills GitHub | github.com/waditu-tushare/skills | 官方 Skill |
| TraeWork 官方文档 | docs.trae.ai/solo/what-is-trae-solo | 产品信息 |
| 千问办公下载 | qwenwork.cn/download | 平台支持 |
| 阿里云文档 | help.aliyun.com/zh/qwenwork | 开发主体 |
| 腾讯云 WorkBuddy | cloud.tencent.cn/developer/article/2722703 | WorkBuddy 信息 |
| 启信慧眼新闻 | m.sohu.com/a/1066960913 | 日期张冠李戴 |
| ClawHub | clawhub-skills.com/skills/tushare-finance | 社区 Skill |

## 核验结论

博文平台描述部分准确（WorkBuddy/千问办公/TraeWork 产品信息基本正确），但**核心声明"Tushare 成为三平台官方预置连接器"未获证实**。这是本系列8篇博文中首次出现 ❌ 失败项。

可能原因包括预告性质、产品混淆（Trae vs TraeWork）、社区贡献误述或营销性表述。读者应以各平台实际可用状态为准，Tushare MCP 当前仍需手动配置。
