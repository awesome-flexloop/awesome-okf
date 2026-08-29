# 示例 00：安装配置完整步骤

> 对应事实：F-018~F-023
> 环境：Claude Code + DeepSeek V4 Pro + 阿里云百炼

## 步骤 1：克隆仓库到用户级 skills 目录

```bash
git clone https://github.com/asuojun/claude-vision-skill.git ~/.claude/skills/claude-vision-skill
```

Windows PowerShell 对应路径为 `C:\Users\<用户名>\.claude\skills\claude-vision-skill`。

> 仓库地址：https://github.com/asuojun/claude-vision-skill

## 步骤 2：替换硬编码路径（必做）

仓库原始 SKILL.md 写死了作者同事的机器路径，共 **3 处**：

```
/Users/wwu/.codex/skills/claude-vision-skill/vision.js
```

分别出现在三种场景（本地路径 / `--url` / `--clipboard`）的命令中。需全部替换为本机绝对路径，例如：

- macOS/Linux：`/Users/<你>/.claude/skills/claude-vision-skill/vision.js`
- Windows：`C:/Users/<你>/.claude/skills/claude-vision-skill/vision.js`

> ⚠️ 不替换会导致 Skill 触发后找不到脚本。注意原路径是 `.codex` 目录而非 `.claude`，直接照抄必然失败。

## 步骤 3：创建 .env 配置

在 skill 目录（vision.js 旁边）创建 `.env`：

```bash
# 阿里云百炼 API Key（必填，百炼控制台申请）
DASHSCOPE_API_KEY=sk-你的Key

# 视觉模型名
VISION_MODEL=qwen-vl-max

# 阿里云百炼 OpenAI 兼容接口地址（一般不用改）
DASHSCOPE_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
```

配置项说明：

| 变量 | 必填 | 说明 |
|------|------|------|
| DASHSCOPE_API_KEY | ✅ | 百炼控制台申请；新用户每模型 100 万 Token 免费（180 天内有效） |
| VISION_MODEL | 否 | `qwen-vl-max`（性价比推荐）或 `qwen3.5-omni-plus`（全模态，成本约4倍） |
| DASHSCOPE_BASE_URL | 否 | OpenAI 兼容端点，默认即可 |

## 步骤 4：安装 dotenv（最关键的坑）

```bash
cd ~/.claude/skills/claude-vision-skill
npm install dotenv
```

> **⚠️ 为什么必须装？** vision.js 中加载 .env 的代码是：
>
> ```js
> try { require("dotenv").config(); } catch {}
> ```
>
> 不装 dotenv 时：**没有任何报错**，但 .env 完全不生效，Key 静默退回默认值 `sk-xxx`，请求失败时现象诡异。这是本项目最容易踩的坑。

## 步骤 5：验证安装

在 skill 目录下手动测试：

```bash
node vision.js "图片路径" "请描述这张图片"
```

能输出图片的详细文字描述即安装成功。

## 安装检查清单

- [ ] 仓库已 clone 到 `~/.claude/skills/claude-vision-skill/`
- [ ] SKILL.md 中 3 处硬编码路径已替换为本机绝对路径
- [ ] `.env` 已创建，DASHSCOPE_API_KEY 已填入真实 Key
- [ ] 已在 skill 目录执行 `npm install dotenv`
- [ ] `node vision.js <测试图> "请描述"` 能返回图片描述

完成后进入 [示例 01：三场景实战](01-usage-scenarios.md)。
