---
type: bundle
title: Skopeo 镜像仓库操作工具
okf_version: "0.2"
---

# Skopeo 知识库

本知识包是 [Skopeo](https://github.com/containers/skopeo)（Apache-2.0 许可证）——无守护进程的远程 OCI/Docker 镜像仓库操作工具的系统化中文源码教程，基于 skopeo v1.x 源码（`external/dao/action/podman-container-tools/skopeo/` 目录）与官方 README 深度阅读生成。覆盖 6 种传输协议架构、copy 命令共享标志组设计、sync 批量同步配置驱动机制，以及多架构 manifest list 处理等核心知识。所有内容均溯源至 Go 源码（cmd/skopeo/copy.go、delete.go、inspect.go、sync.go、login.go、main.go）与官方 README，遵循 [OKF v0.2 规范](concepts/00-introduction.md)。

## 架构总览篇（concepts/）

* [skopeo 概述与传输协议架构](concepts/00-introduction.md) —— 无守护进程设计哲学、6 种传输协议（containers-storage/dir/docker/docker-archive/docker-daemon/oci）详解、Cobra CLI 框架结构、共享标志组 design、9 个命令家族职责边界。
* [copy 命令与 sharedCopyOptions 标志组](concepts/01-copy-architecture.md) —— copy.Image() 核心调用链、copyOptions 结构体全字段解析、multi-arch 处理策略（all/most-permissive/specific）、GPG 签名与层加密控制、sharedCopyOptions 安全/认证/压缩标志组。
* [sync 批量同步命令与 YAML 配置驱动](concepts/02-sync-architecture.md) —— 三种源传输（docker/dir/yaml）分发机制、regexp 标签过滤与 semver 约束过滤（Masterminds/semver/v3）、dry-run 预演、scoped 命名空间映射、目标传输限制。

## 实战示例（examples/）

* [镜像跨仓库迁移与格式转换](examples/00-migration-format-conversion.md) —— Docker v2s2↔OCI 格式转换、跨注册表迁移（含认证重定向）、多架构 manifest list 处理、docker-daemon 导入、digest 文件输出、常见错误排查。

## 信源登记簿（references/）

* [skopeo 源码与文档信源登记](references/source.md) —— README.md 命令表格、6 种传输协议、copy/delete/inspect/sync/login/main 六个 Go 源码文件的 Grep 级事实登记。

## 信任与生命周期说明

* **status 判定依据**：全部 5 个内容文档（3 个概念 + 1 个示例 + 1 个信源登记）均 `status: stable`。内容基于对 skopeo 源码（cmd/skopeo/copy.go、delete.go、inspect.go、sync.go、login.go、main.go）与 README.md 的逐文件阅读与事实提取，经 seven-concepts 方法论 R→I→E→V 四阶段流程生成。
* **stale_after 解释**：统一设置为 `2027-09-08`。skopeo 核心传输协议架构（6 种 transport）与 copy/sync 命令接口自 v1.0 确立以来保持稳定；该日期作为针对未来大版本引入破坏性变更（如传输协议重写或 CLI 标志重构）的保守重新评估节点。
* **核验链路**：`generated.at` 记录各文档原始生成时刻；`verified.at` 记录 V 阶段 Grep 对抗验证事件（copyOptions 结构体字段、syncOptions 结构体字段、Output struct 字段、registrySyncConfig 字段逐一比对源码），两者分离、可追溯。

本知识包共收录 6 个内容文档（3 个概念 + 1 个示例 + 1 个信源登记 + 1 个 log），另含 3 个子目录 index.md 与根 index.md。

```{toctree}
:hidden:
:maxdepth: 7

concepts/index
examples/index
references/index
log
```
