---
type: Concept
title: "04 · 官方命令路径与全虚构 Demo 的差距"
description: "clone/install/demo/profile-init/Codex 五步官方命令逐字登记，并说明为何本束不设 examples/、全虚构 Demo 不能证明真实数据可用性"
tags: [wechat-intelligence-hub, install, demo, profile-init, reproducibility, 骨架判定]
---

# 04 · 官方命令路径与全虚构 Demo 的差距

> ⚠️ **本篇是路径说明，不是实操教程。** 以下命令来自官方 main 分支 README 的**文档级逐字核验**（F-048~F-052）；本知识包**未 clone 仓库、未执行任何命令、未做实机验证**。官方自己亦标注 macOS 新机器路径未实测（F-035、F-056）。

## 1. 为什么这里没有 `examples/`

`blog-article-to-okf-wiki` 的骨架判定靠「操作可复现性两问」：

| 问题 | 本博文 | 判定 |
|------|--------|------|
| 是否有读者可照做的流程？ | 全文无一条命令、无版本号、无步骤顺序，只写「去 GitHub 把仓库 clone 下来」（F-003、F-040） | **否**（博文层） |
| 是否经作者实测且具备版本 / 输入 / 输出 / 步骤顺序？ | 明确「全虚构 Demo」「macOS 新机器的获取路径官方还没实测」，产出为截图图注（F-032、F-035） | **否** |

任一为否 → **概念骨架，不设 `examples/`**。官方 README 虽提供了命令，但那是**第二信源补充**，不能反过来把博文包装成实测教程。因此本束只用概念文档登记命令路径，并逐条标注未验证。

## 2. 官方五步路径（逐字登记，未实机验证）

**① 安装**（F-048）

```bash
git clone https://github.com/Rion-Wu-tech/wechat-intelligence-hub.git
cd wechat-intelligence-hub
./scripts/install.sh --with-sqlcipher --with-html
```

`--with-sqlcipher` 指向本地数据库读取依赖，`--with-html` 对应 HTML 报告产物（F-052）。

**② 先跑全虚构 Demo**（F-049）

```bash
bash projects/wechat-intelligence-hub/scripts/run_demo.sh
```

README 要求样例数据必须为虚构（F-053）。博主也建议「先用虚构 Demo 跑一遍，再决定要不要接自己的微信」（F-040）。

**③ 初始化个人 Profile**（F-050）

```bash
cd projects/wechat-intelligence-hub
python3 wechat_intelligence_hub.py profile-init \
  --owner-alias "你的微信昵称" \
  --personal-doc "/path/to/个人说明.md" \
  --plan-doc "/path/to/本月计划.md" \
  --priority-label "你的重点联系人标签"
```

这四个参数对应博文说的「把你在做的事、个人背景、关系标签变成日报的排序依据」（F-029）。**路径为占位符，不是真实路径**；本束不提供任何本机绝对路径。

**④ 用 Codex 自然语言调用**（F-051）

```text
$wechat-intelligence-hub 生成过去 24 小时的完整微信情报日报，分析群聊、重点联系人、待回复事项和商业机会。
$wechat-intelligence-hub 总结我和「联系人名字」最近聊到哪里，还有什么承诺没有完成。
$wechat-intelligence-hub 搜索过去 7 天所有微信聊天里关于「AI 培训」的讨论。
```

**⑤ 查看产物**（F-052）

```text
wechat_daily_full.md          # Markdown 全文报告
wechat-report/                # 报告目录
wechat_daily_report.html      # HTML 交互式报告
```

## 3. 全虚构 Demo 能证明什么、不能证明什么

| 能证明 | 不能证明 |
|--------|---------|
| 索引 → 判断 → 报告这条**链路**在虚构数据上跑得通（F-032、F-049） | 你的本机微信数据库可被正确读取 |
| 报告产物格式（md / html / report 目录）存在（F-052） | 真实聊天数据下的抽取质量、信号准确率 |
| 无需真实数据即可评估界面与信息架构 | 任意微信版本兼容、零封控（F-054 明确不保证） |

官方对「真实首次接入」的态度相当保守（F-056）：macOS 候选接入工具可能重启微信、重签名副本并有独立授权边界；Windows 首次获取路径**尚未合入**；这条路径需要单独验收。这正是 [01-local-first-readonly-architecture.md](01-local-first-readonly-architecture.md) 第 4 节「不重签名」范围勘误的来由。

## 4. 接入前的数据纪律（官方 + 博文一致）

- 接入须由**本人**完成登录与系统授权，密码与密钥不交给任何人（F-031、F-053）。
- 真实聊天、联系人、Profile、数据库、报告**不得提交 Git**；样例一律虚构（F-028、F-053）。
- 聊天记录、密钥、数据库**不要发到 Issue 或社群**（F-036、F-053）。
- 完整历史需要本人授权的本地数据库，且**只覆盖已同步到本机、当前可读**的数据（F-034、F-054）。

## 5. 复核提示

`stale_after: 2027-03-06` 之前复核：`v0.9.2-preview.2` 是否转正、`install.sh` 参数是否变化、macOS/Windows 首次获取路径是否合入、Profile 命令签名是否调整。版本漂移时以官方 README 为准，本页命令视为**2026-11-06 文档快照**。

下一站：[05-insights-and-adoption-boundaries.md](05-insights-and-adoption-boundaries.md)。
