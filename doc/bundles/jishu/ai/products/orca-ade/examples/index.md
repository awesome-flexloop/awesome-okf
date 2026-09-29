# 实操示例（Examples）

> 本目录是**基于官方文档与官方仓库逐字核验重组的实操指引，不是博文作者的实测记录**：博文只声明 macOS 侧跑过一行安装命令（F-043），未给版本号、未展示任何命令输出，Windows/Linux 步骤为转述（F-044~F-046）；核验日 2026-09-20，对应最新正式版 v1.4.205（F-067）。**本包制作中未在任何平台真机执行**，文中引号内容均为官方文档原文措辞（非实测输出），读者执行前请以官方最新文档为准。

| 文档 | 主题 |
|------|------|
| [00-install-and-first-session.md](00-install-and-first-session.md) | 前置认知（不含模型/用已有订阅）、三平台安装资产与命令、Homebrew 同名 cask 消歧、首启导入 `~/.claude` 与 `~/.codex`、首个 worktree 链路、可用性检查表与常见坑 |
| [01-parallel-worktrees-and-cli.md](01-parallel-worktrees-and-cli.md) | 并行 worktree 扇出与 diff 择一合并、终端/通知/Design Mode/Diff 批注配套交互、Orca CLI 命令表、SSH 远程 worktree、移动端配对（双账号口径）、用量面板与并行 token 成本提示 |

```{toctree}
:hidden:
:maxdepth: 1

00-install-and-first-session
01-parallel-worktrees-and-cli
```