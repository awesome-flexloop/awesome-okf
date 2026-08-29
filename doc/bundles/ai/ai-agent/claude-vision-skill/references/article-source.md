# 信源与事实登记

## 博文信息

| 项 | 内容 |
|----|------|
| 标题 | 《DeepSeek V4 Pro 也能看图了！》 |
| 作者 | macrozheng（公众号） |
| 发布时间 | 2026-08-21 14:10 |
| URL | https://mp.weixin.qq.com/s/3AZbLPVwg45PrQSuvcJDHQ |
| 内容类型 | 开源工具技术教程 |
| 开源项目 | https://github.com/asuojun/claude-vision-skill |

**作者身份（F-035）**：macrozheng 为知名技术博主，mall 单体电商 60k+ star，mall-swarm 微服务商城（Spring Cloud Alibaba / Spring Boot 3 / JDK 17 / Kubernetes）11k+ star，教程站 cloud.macrozheng.com。✅ 已核验

## 事实登记（F-001~F-035）

### 元信息

| 编号 | 事实 |
|------|------|
| F-001 | 标题《DeepSeek V4 Pro 也能看图了！》，公众号macrozheng，2026-08-21 14:10 |

### 问题背景

| 编号 | 事实 | 核验 |
|------|------|------|
| F-002 | Claude Code 接纯文本模型时发图片返回 [Unsupported Image] | ✅ |
| F-003 | DeepSeek V4 Pro 本身不带视觉能力 | ✅ 官方文档：仅 flash-vision-exp 接受图片 |
| F-004 | V4 Pro 正式版（DeepSeek-V4-Pro-0813）2026-08-13 发布 | ✅ |
| F-005 | 补充：deepseek-v4-flash-vision-exp 于 2026-08-21（博文当天）上线，实验性；V4 Pro 截至 08-29 仍无视觉 API | ✅ 补充核验 |

### 解决方案

| 编号 | 事实 | 核验 |
|------|------|------|
| F-006 | 思路：图片先发视觉模型转录成文字，再交回文本模型推理 | ✅ README 一致 |
| F-007 | 对文本模型只是多一段上下文，效果等于"看图" | — |
| F-008 | claude-vision-skill：标准 Claude Code Skill，配置好后直接发图自动识图 | ✅ |
| F-009 | 仓库 github.com/asuojun/claude-vision-skill，公开，含 vision.js/SKILL.md/clipboard.ps1/clipboard.swift | ✅ |
| F-010 | 识图准确度/速度/成本取决于视觉模型；博文用 qwen-vl-max | ✅ |

### 工作原理

| 编号 | 事实 | 核验 |
|------|------|------|
| F-011 | 链路：发图→description自动触发→vision.js→dotenv注入→base64→POST视觉模型API（OpenAI兼容）→文字描述→DeepSeek推理 | ✅ |
| F-012 | 真正看图的是视觉模型，DeepSeek 拿文字转录结果 | ✅ |
| F-013 | Skill 放 ~/.claude/skills/，model-invoked，启动时预加载 name/description，按上下文自动加载，无需斜杠命令 | ✅ Anthropic 官方 |
| F-014 | SKILL.md 以 YAML frontmatter 开头，含 name（≤64）+ description（≤1024，做什么+何时用） | ✅ |
| F-015 | SKILL.md 硬编码他人路径 /Users/wwu/.codex/skills/claude-vision-skill/vision.js 共3处（本地/--url/--clipboard），提交者 waynewu411，需替换 | ✅ |
| F-016 | README 主推"场景A"：vision.js 拷项目根目录 + 合并 CLAUDE.md；博文采用 ~/.claude/skills/ 全局安装 | ✅ 补充 |
| F-017 | vision.js 的 require("dotenv") 在 try{}catch{} 中，不装则静默失败、Key 退回 sk-xxx 且无报错；必须 npm install dotenv | ✅ 最易踩坑 |

### 安装配置

| 编号 | 事实 | 核验 |
|------|------|------|
| F-018 | git clone 到 ~/.claude/skills/claude-vision-skill/（用户级全局安装） | ✅ |
| F-019 | skill 目录创建 .env：DASHSCOPE_API_KEY（必填）、VISION_MODEL、DASHSCOPE_BASE_URL | ✅ |
| F-020 | DASHSCOPE_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1 | ✅ 官方端点 |
| F-021 | API Key 在阿里云百炼控制台申请 | ✅ |
| F-022 | 安装：cd ~/.claude/skills/claude-vision-skill && npm install dotenv | ✅ |
| F-023 | 验证：node vision.js "图片路径" "请描述这张图片"，输出描述即装好 | — |

### 视觉模型

| 编号 | 事实 | 核验 |
|------|------|------|
| F-024 | qwen-vl-max 存在：百炼，Text/Image/Video→Text，快照 qwen-vl-max-2025-08-13，北京/新加坡可用 | ✅ |
| F-025 | qwen3.5-omni-plus 存在：全模态 Text/Image/Video/Audio→Text/Audio，快照 qwen3.5-omni-plus-2026-03-15 | ✅ |
| F-026 | 成本：omni 输入 7 元/百万 token，vl-max 1.6 元/百万，看图约 4 倍差价，博文未提示 | ✅ 补充 |
| F-027 | 百炼新用户每模型 100 万 Token 免费、开通后 180 天有效 | ✅ 补充 |

### 使用方式

| 编号 | 事实 | 核验 |
|------|------|------|
| F-028 | 自动触发：会话中直接发图片（本地路径/粘贴截图/URL），description 自动匹配 | ✅ |
| F-029 | 案例：mall-swarm 架构图粘贴后问"这张图片里有什么"，DeepSeek V4 Pro 借 Skill 认出 | — |
| F-030 | 手动-本地：node vision.js "C:/path/to/image.png" "请描述..." | ✅ |
| F-031 | 手动-网络：vision.js --url "https://example.com/image.png" "请描述..." | ✅ |
| F-032 | 手动-剪贴板：vision.js --clipboard "请描述..."（Windows 用 clipboard.ps1） | ✅ |
| F-033 | 回退：本地路径文件不存在→自动回退剪贴板；无路径无URL→自动尝试剪贴板 | ✅ |
| F-034 | --no-fallback 关闭回退直接报错 | ✅ |

### 作者身份

| 编号 | 事实 | 核验 |
|------|------|------|
| F-035 | macrozheng：mall 60k+ star、mall-swarm 11k+ star（Spring Cloud Alibaba/Boot3/JDK17/K8s）、cloud.macrozheng.com | ✅ |

## 事实统计

- 事实总数：**35 条**
- 核验状态：6 项 P0 声明全部 ✅ 通过
- 时效性/成本补充：5 条（F-005、F-015、F-016、F-026、F-027）
- 作者观点（📝）：F-007 为作者对方案效果的判断，其余为可核验事实或操作步骤
