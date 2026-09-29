# 完整事实登记

> 主信源：微信公众号"挖地兔"（Tushare官方），2026-08-25 06:28
> URL：https://mp.weixin.qq.com/s/OsEhhFtwrasx7Y9cw29Zug
> P0核验：3✅ 2⚠️ 1❌（核心声明F-006失败）

## 元信息

| 编号 | 事实 | 核验 |
|------|------|------|
| F-001 | 标题《WorkBuddy、千问办公、TraeWork三大平台同步上架》，"挖地兔"，2026-08-25 06:28 | — |

## 平台描述

| 编号 | 事实 | 核验 |
|------|------|------|
| F-002 | Tushare是Python财经数据接口平台，token认证，返回Pandas DataFrame，覆盖股票/基金/期货/债券/外汇/宏观等 | ✅ |
| F-003 | WorkBuddy是AI办公平台，Connector是外部服务桥梁，自然语言操作，无需手动下载上传复制粘贴 | ✅ 腾讯出品，MCP协议 |
| F-004 | 千问办公是千问团队开发的桌面智能办公助手，macOS/Windows，桌面版+网页版 | ⚠️ 钉钉业务线开发；还支持鸿蒙6.1+ |
| F-005 | TraeWork是TRAE品牌下AI原生工作台，网页/桌面/移动三端，Work/Code/Design三模式 | ✅ |

## 核心声明

| 编号 | 事实 | 核验 |
|------|------|------|
| F-006 | Tushare数据同步上架WorkBuddy/千问办公/TraeWork，成为官方预置连接器 | ❌ 未获证实，详见核验报告 |
| F-007 | 此前Tushare是"野生插件"，用户需通过自定义连接器手动添加Tushare MCP | ⚠️ 手动配置属实，但"变为预置"无证据 |
| F-008 | 📝 三个平台覆盖从企业协作、文档办公到开发者Agent的不同场景 | 📝 |

## WorkBuddy 配置

| 编号 | 事实 | 核验 |
|------|------|------|
| F-009 | 在WorkBuddy找到Tushare连接器→点"+"→输入token→保存并连接→去试试 | ⚠️ 有社区Skill非官方预置 |
| F-010 | 无Tushare账号可点"如何获取Token？"跳转注册页，注册后在个人中心找Token | ✅ |

## 千问办公配置

| 编号 | 事实 | 核验 |
|------|------|------|
| F-011 | 千问办公由千问团队开发，macOS/Windows，桌面版+网页版 | ⚠️ 同F-004 |
| F-012 | Tushare上架千问办公官方预置连接器，开箱即用 | ❌ 官方连接器列表无Tushare |
| F-013 | 点Tushare金融数据→安装→连接→授权应用→同意授权 | ❌ 基于F-012不成立 |
| F-014 | 未登录Tushare时跳转登录页，微信扫码完成授权 | ⚠️ Tushare支持微信登录，但预置流程不成立 |

## TraeWork配置

| 编号 | 事实 | 核验 |
|------|------|------|
| F-015 | TraeWork是TRAE品牌下AI原生工作台 | ✅ |
| F-016 | 网页版/桌面版/移动版三种形态 | ✅ |
| F-017 | Work/Code/Design三种模式，覆盖专业开发到日常办公 | ✅ Design模式2026-06-25发布 |
| F-018 | Tushare是TraeWork官方预置连接器，点"安装"→输入Token→保存并连接 | ❌ 官方文档列出"Trae"非"TraeWork" |
| F-019 | 连接成功后可在TraeWork对话框直接使用 | ❌ 基于F-018不成立 |

## 用途与效果

| 编号 | 事实 | 核验 |
|------|------|------|
| F-020 | 📝 三大平台对接Tushare用法基本一致，不再需要编程，会问问题/调试问题即可得结果 | 📝 |
| F-021 | 📝 示例："获取近5日涨幅最大的板块并分析资金流向"→图文并茂报告 | 📝 基于F-006不成立 |
| F-022 | 更多问题：指数走势对比/茅台日线/龙虎榜机构席位/两融余额/涨停板名单 | ✅ 这些是Tushare可提供的数据类型 |
| F-023 | 📝 三平台覆盖企业协作/文档办公/开发者Agent不同场景 | 📝 |
| F-024 | 📝 Tushare将持续优化，加快与更多AI平台对接，丰富数据维度，提升响应速度 | 📝 未来计划 |
| F-025 | 📝 "数据的价值，最终要落到使用上" | 📝 金句 |

## 核验补充

| 编号 | 事实 | 来源 |
|------|------|------|
| F-026 | 2026-08-25"多平台上架"新闻主体是启信慧眼（企业数据查询），非Tushare | 搜狐 |
| F-027 | Tushare官方MCP支持平台：OpenClaw系(OpenClaw/WorkBuddy/KimiClaw/MaxClaw/CoPaw/悟空)、Vibe Coding(CodeBuddy/ClaudeCode/Cursor/Trae/Cline/Lingma)；无千问办公，列出"Trae"非"TraeWork" | Tushare官方文档 |
| F-028 | Tushare MCP仍需手动配置：登录个人中心拷贝MCP key→手动添加到各平台MCP配置 | Tushare官方文档 |
| F-029 | WorkBuddy上有社区Skill tushare-finance（作者stanleychanh，非Tushare官方waditu-tushare） | ClawHub |
| F-030 | 千问办公由阿里钉钉业务线主导，整合QoderWork/悟空/MuleRun，支持macOS 14+/Windows 10+/HarmonyOS 6.1+ | qwenwork.cn, 阿里云 |
| F-031 | WorkBuddy是腾讯出品AI办公智能体，连接器基于MCP协议，内置80+连接器，Ask/Plan/Craft三模式 | 腾讯云/掘金 |
| F-032 | Tushare官方Skill tushare-data（GitHub: waditu-tushare/skills），clawhub install安装，仍需手动配Token | GitHub |

## 事实统计

| 类别 | 数量 |
|------|------|
| 元信息 | 1 |
| 平台描述 | 4 |
| 核心声明 | 3 |
| WorkBuddy配置 | 2 |
| 千问办公配置 | 4 |
| TraeWork配置 | 5 |
| 用途效果 | 6 |
| 核验补充 | 7 |
| **合计** | **32** |
