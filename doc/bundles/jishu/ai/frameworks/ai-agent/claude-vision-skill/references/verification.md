# 核验报告

> 核验日期：2026-08-29
> 核验方式：WebSearch + 官方文档/仓库交叉验证
> 核验人：OKF Wiki Bot

## 总结

| 项 | 结果 |
|----|------|
| P0 声明数 | 6 |
| ✅ 通过 | **6** |
| ⚠️ 部分通过 | 0 |
| ❌ 失败 | 0 |
| 时效性补充 | 3 |

**结论**：博文涉及的仓库、模型、机制、作者身份全部真实可查，未发现虚构。3 项补充均为时效性/完整性提示，不影响博文操作步骤的正确性。

## 逐项核验

### 1. claude-vision-skill GitHub 仓库 — ✅ 通过

- 仓库 https://github.com/asuojun/claude-vision-skill **真实存在且 Public**，所有者 asuojun（14 次提交）
- 文件列表确认包含 `vision.js`、`SKILL.md`、`CLAUDE.md`、`AGENTS.md`、`clipboard.ps1`、`clipboard.swift`
- README 描述与博文一致："让没有识图能力的模型获得识图能力——把图片发给有 vision 的模型，用文字描述回来"
- SKILL.md 含规范 YAML frontmatter（name + description）

**补充差异**：
- README 主推"场景A"（vision.js 拷项目根目录 + 合并 CLAUDE.md），博文采用 `~/.claude/skills/` 全局安装——两者均可行
- SKILL.md 硬编码 `~/.codex/skills/...`（最近提交者 waynewu411，Codex 路径），需替换

### 2. DeepSeek V4 Pro 纯文本无视觉 — ✅ 通过

- DeepSeek 官方 API 文档（Vision 指南）明确：仅 `deepseek-v4-flash-vision-exp` 接受图片，其他模型返回 400 错误 "This model does not support image"
- V4 Pro 正式版 DeepSeek-V4-Pro-0813 于 2026-08-13 发布
- Claude Code 对不支持图片的端点显示占位提示，与 [Unsupported Image] 现象吻合

**⏰ 时效性补充**：`deepseek-v4-flash-vision-exp` 于 **2026-08-21（博文发布当天）** 上线，基于 V4-Flash，实验性。用户现在可评估直连方案，但 V4 Pro 仍无视觉 API。
- 注：CSDN 有第三方博客称"V4 Pro 正式版首次原生支持图像推理"，与官方文档矛盾，不采信

### 3. 阿里云百炼 qwen-vl-max + compatible-mode — ✅ 通过

- qwen-vl-max 官方模型页确认：输入 Text/Image/Video，输出 Text，快照 qwen-vl-max-2025-08-13，北京/新加坡可用
- 官方视觉指南示例使用 `DASHSCOPE_API_KEY` 环境变量，与博文一致
- `https://dashscope.aliyuncs.com/compatible-mode/v1` 为百炼官方 OpenAI 兼容端点
- 补充：免费额度为每模型 100 万 Token、开通后 180 天内有效

### 4. Claude Code Skill 机制 — ✅ 通过

- 与 Anthropic 官方 Agent Skills 标准（2025-10-16 工程博客）完全一致
- 个人 Skill 路径 `~/.claude/skills/<skill-name>/SKILL.md`；model-invoked；启动预加载 name/description；按上下文自动加载
- SKILL.md 须以 YAML frontmatter 开头，name ≤64 字符、description ≤1024 字符

### 5. qwen3.5-omni-plus 模型 — ✅ 通过

- 官方模型页确认存在：Qwen3.5-Omni 旗舰全模态，输入 Text/Image/Video/Audio，输出 Text/Audio，快照 qwen3.5-omni-plus-2026-03-15，支持 OpenAI 兼容调用

**成本补充**：omni 输入 7 元/百万 token，qwen-vl-max 输入 1.6 元/百万 token，纯看图场景 omni 成本约 4 倍，博文未提示。

### 6. macrozheng 身份与 mall-swarm — ✅ 通过

- macrozheng 为真实知名技术博主（macrozheng.com，掘金认证）
- mall 单体电商 60k+ star；mall-swarm（https://github.com/macrozheng/mall-swarm）11k+ star，Spring Cloud Alibaba / Spring Boot 3 / JDK 17 / Kubernetes，教程站 cloud.macrozheng.com

## 风险与建议

1. **时效性**：DeepSeek 官方视觉模型已上线，本 Skill 的定位从"唯一方案"变为"解耦方案"（推理模型可自由选择），价值仍在但建议读者知悉
2. **安装可靠性**：SKILL.md 硬编码路径 + dotenv 静默失败是两个真实存在的坑，已在概念与实战文档中显著标注
3. **成本感知**：默认 qwen-vl-max 成本极低；若读者改 omni 需知 4 倍差价
4. **stale_after**：设为 2026-11-29（视觉模型生态变化快，3 个月后复核模型名称与价格）
