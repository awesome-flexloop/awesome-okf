---
okf_version: "0.2"
---
# Git 学习与团队协作知识库

本知识包是简书连载《开源的世界》（nb/40234132）中 Git 相关文章的**中文教程束**，基于 2020 年前后教程整理，覆盖 Git 学习路线、Git Flow 分支模型与团队协作、下载加速技巧三大主题。所有内容均溯源至 3 篇简书原文（编号事实 F-213~F-219、F-238~F-247、F-256~F-259），遵循 [OKF v0.2 规范](https://github.com/awesome-flexloop/awesome-okf)。

## 内容概览（concepts/）

* [Git 学习路线与 Git Flow 分支模型导论](concepts/00-learning-path.md) — Git 学习资源路线、gitk 中文乱码处理、中心版本库 master/develop 双主分支与 feature/release/hotfix 辅助分支模型导论。
* [Git Flow 分支模型与团队协作](concepts/01-branch-model.md) — 项目配置管理 PCM、Git Flow 规则表、feature/release/hotfix 三场景实战命令、裸库共享、版本号 x.y.z 与局域网协作。
* [Git 下载代码加速与容量限制解除](concepts/02-download-acceleration.md) — http.postBuffer 增大缓存、低速阈值调整、浅层克隆加 `git fetch --unshallow` 解除克隆容量与速度问题。

## 信源登记簿（references/）

* [《2.1 Git 学习笔记》](references/source-1.md) — F-213 ~ F-219。
* [《2.2 使用 Git 管理配置团队项目》](references/source-2.md) — F-238 ~ F-247。
* [《Git 下载代码加速，解除容量限制》](references/source-3.md) — F-256 ~ F-259。

## 学习路径建议

1. **入门**：00-learning-path（学习资源 + 分支模型导论）→ 01-branch-model（团队实战）
2. **排障**：02-download-acceleration（克隆容量/速度问题处理）
3. **延伸**：配合 [github 束](../github/index.md) 的 Gist 与 GitHub Actions、[opensource 束](../opensource/index.md) 的开源实践阅读

## 信任与生命周期说明

* **status 判定依据**：全部非 index/log 文档均 `status: stable`。内容基于简书连载《开源的世界》原文事实登记（facts.md）生成，不虚构原文没有的事实或资源。
* **stale_after 解释**：统一设置为 `2026-12-31`。文中 Git 配置项、分支模型方法论长期有效；具体命令细节与平台行为以当前官方文档为准（各概念文档已含「现状」说明）。
* **核验链路**：`generated.at` 记录原始生成时刻（2026-09-02）；`verified.at` 记录过程核验事件（2026-09-02），事实编号与 `facts.md` 双份登记一致。
* **时点边界**：本束全部内容基于 2020 年前后教程，部分资源链接与平台行为可能已变化，详见各文档「现状」小节。

```{toctree}
:hidden:
:maxdepth: 7

concepts/index
references/index
log
```
