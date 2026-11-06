# 实战示例（Examples）

> ⚠️ **本目录整体声明**：源文未提供任何可照做步骤（F-039）。三篇 examples 全部整理自
> **官方 GitHub README 的文档化流程**（三步上手、开发者章节、场景/分批段落），
> **非源文作者实测、非本知识包 macOS 实机验证**。命令逐字引用，UI 细节因截图不可补全一律不写。
> 执行前请以官方 [使用指南](https://github.com/freestylefly/WeChatBridge/blob/main/USAGE.zh-CN.md) 为准。

| 文档 | 内容 |
|------|------|
| [00-install-and-first-forward.md](00-install-and-first-forward.md) | 版本前置（macOS 14+ / 微信 4.1.13+）、安装、启用入口、首次合并转发四个检查点、失败兜底接手 |
| [01-build-from-source.md](01-build-from-source.md) | Xcode 16 / Swift 6 前置、四行构建命令逐字、产物路径、安装注册脚本、开发验证命令与项目结构 |
| [02-scenes-skills-and-batch-workflow.md](02-scenes-skills-and-batch-workflow.md) | 场景/技能配置顺序、超过 100 条时的分批收集七步、投递失败后的五类接手动作 |

**骨架判定依据**：操作可复现性两问皆「是」——官方 README 给出了带版本、带顺序、带产物路径的操作流程
（F-077、F-088、F-089、F-090、F-092）。完整判据见主仓库 spec
`.trae/specs/okf-wiki-ecosystem/wechatbridge-okf-wiki/spec.md` 的「骨架判定」段，
以及本束 [log.md](../log.md) 的 I 阶段记录（跨仓库路径仅作文字说明，不作相对链接）。

```{toctree}
:maxdepth: 1
:caption: 实战示例

00-install-and-first-forward
01-build-from-source
02-scenes-skills-and-batch-workflow
```
