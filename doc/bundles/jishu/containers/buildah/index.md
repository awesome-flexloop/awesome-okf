---
type: bundle
title: Buildah 镜像构建工具
okf_version: "0.2"
---

# Buildah 知识库

本知识包是 [Buildah](https://github.com/containers/buildah)（Apache-2.0 许可证）——无守护进程的 OCI 镜像构建工具的系统化中文源码教程，基于 buildah v1.x 源码（`external/dao/action/podman-container-tools/buildah/` 目录）与官方 README 深度阅读生成。覆盖 working container 生命周期、from/run/commit 核心流水线、22 个命令的四分组架构、Go API 可被 vendored 的设计特点等核心知识。所有内容均溯源至 Go 源码（cmd/buildah/main.go、build.go、from.go、commit.go、run.go、images.go、push.go）与官方 README，遵循 [OKF v0.2 规范](concepts/00-introduction.md)。

## 架构总览篇（concepts/）

* [buildah 概述与 working container 概念](concepts/00-introduction.md) —— 与 Podman/Skopeo 的定位差异、working container 生命周期（from→run→commit→push）、与 Podman container 的存储隔离、22 个命令的 4 组分组、Go API 可被 vendored 的设计。
* [构建流水线：from → run → commit](concepts/01-build-flow.md) —— from 命令的 NewBuilder() 调用链与 ONBUILD 指令处理、run 命令的 volumes/mounts/isolation 选项解析、commit 命令的 CommitOptions 全字段（压缩/签名/加密/SBOM/配置覆盖）、镜像列表与推送。

## 实战示例（examples/）

* [从 Containerfile 构建并推送 OCI 镜像](examples/00-dockerfile-build.md) —— 多阶段 Go 应用构建（Containerfile）、手工逐步构建等价操作（from→copy→run→config→commit）、GPG 签名与 SBOM 扫描、多架构 manifest list 构建与推送、常用标志速查。

## 信源登记簿（references/）

* [buildah 源码与文档信源登记](references/source.md) —— README.md 命令分组表格、22 个命令列表、main.go/build.go/from.go/commit.go/run.go/images.go/push.go 七个 Go 源码文件的 Grep 级事实登记。

## 信任与生命周期说明

* **status 判定依据**：全部 5 个内容文档（2 个概念 + 1 个示例 + 1 个信源登记）均 `status: stable`。内容基于对 buildah 源码（cmd/buildah/main.go、build.go、from.go、commit.go、run.go、images.go、push.go）与 README.md 的逐文件阅读与事实提取，经 seven-concepts 方法论 R→I→E→V 四阶段流程生成。
* **stale_after 解释**：统一设置为 `2027-09-08`。Buildah 核心构建流水线（from/run/commit）与 4 组命令架构自 v1.0 确立以来保持稳定；该日期作为针对未来大版本引入破坏性变更（如 BuilderOptions 接口重构或命令分组调整）的保守重新评估节点。
* **核验链路**：`generated.at` 记录各文档原始生成时刻；`verified.at` 记录 V 阶段 Grep 对抗验证事件（BuilderOptions/CommitOptions/RunOptions 结构体字段、groupImages/groupContainers/groupRegistries/groupSystem 常量逐一比对源码），两者分离、可追溯。

本知识包共收录 6 个内容文档（2 个概念 + 1 个示例 + 1 个信源登记 + 1 个 log），另含 3 个子目录 index.md 与根 index.md。

```{toctree}
:hidden:
:maxdepth: 7

concepts/index
examples/index
references/index
log
```
