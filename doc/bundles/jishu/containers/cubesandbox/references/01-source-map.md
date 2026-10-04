---
type: Reference
title: CubeSandbox 源码信源地图
description: CubeSandbox v0.7.2 信源登记——版本 pin（tag/commit/remote）、仓库目录与组件地图、已知信源瑕疵与读取规则
tags: [CubeSandbox, source-map, v0.7.2, 信源登记]
generated: { by: "process:source-code-to-okf-wiki", at: "2026-10-04" }
verified: { by: "process:seven-concepts-v", at: "2026-10-04" }
status: stable
stale_after: 2027-10-04
sources:
  - id: S1
    resource: https://github.com/TencentCloud/CubeSandbox
    title: TencentCloud/CubeSandbox 官方仓库
---

# CubeSandbox 源码信源地图

> 本知识包全部事实来自腾讯官方开源仓库 **TencentCloud/CubeSandbox** 的 release tag **v0.7.2**。本文登记版本 pin、仓库结构与已知瑕疵，是全束 `sources` 字段的指向目标。

## 一、版本 pin（G0 信源稳定性门产出）

| 项 | 值 |
|---|---|
| 远程仓库 | `git@github.com:TencentCloud/CubeSandbox.git` |
| release tag | **v0.7.2** |
| tag commit | `f1aaa737fb3862202b1731e0e0d844c28779f930` |
| tag 日期 | 2026-09-24 |
| 本地工作树 | v0.7.2 + 11 commits（HEAD `e02976ae`） |
| 读取规则 | post-release 变更文件一律以 `git show v0.7.2:<path>` 的 blob 为准 |
| 本地路径（只读） | `external/dao/runtime/tencent/CubeSandbox` |

tag 选型判据：文档引用集合 ∩ 版本变更集合 = ∅——引用的接口、配置、文件在 v0.7.2 中全部存在。

## 二、仓库顶层结构与组件地图

| 顶层目录 | 组件 | 语言/形态 | 角色 |
|---|---|---|---|
| `CubeAPI/` | CubeAPI | Rust（axum），:3000 | E2B 兼容 REST API 网关 |
| `CubeMaster/` | CubeMaster、cubemastercli | Go（gin），:8089/gRPC :9999 | 编排调度、模板/卷元数据 |
| `Cubelet/` | Cubelet、cubecli | Go，:9998/:9999/debug :9966 | 节点代理（root `/data/cubelet`） |
| `CubeShim/` | CubeShim（shim + protoc） | Rust，containerd-shim 0.9.0 | Shim v2 运行时接入 |
| `hypervisor/` | cube-hypervisor | Rust workspace（Cargo.toml 登记 29 members），crate v28.0.0 | cloud-hypervisor fork，KVM VMM |
| `guest-init/` | cube-init | Rust，guest 内 PID 1 | guest 环境初始化、挂 pmem、拉起 cube-agent |
| `agent/` | cube-agent（rustjail、cube） | Rust，ttrpc vsock :1024 / passfd :1027 | guest 内容器与进程管理 |
| `CubeNet/` | cubevs | Go + eBPF C（cilium/ebpf） | eBPF 网络数据面 |
| `CubeEgress/` | CubeEgress | OpenResty + Lua，:8080/:8443/:9091 | L7 出向策略透明网关 |
| `CubeProxy/` | CubeProxy | OpenResty + Lua，:8080/:8081/:9090 | 沙箱域名路由与 gRPC 桥接 |
| `cubecow/` | cubecow（+ cubecow-cli） | Rust，lib/cdylib/staticlib | CoW 卷快照引擎（reflink/s3 双后端） |
| `CubeS3lvol/` | s3lvol_tgt | C（SPDK/DPDK）+ 脚本 | NVMe/TCP target，对接对象存储 |
| `CubeOps/` | CubeOps、cubeopscli | Go（gin），:3010 | 运维面（认证/集群/节点/仓库） |
| `cube-lifecycle-manager/` | CLM | Go，Redis Stream + 选主 | 自动暂停/恢复控制循环 |
| `CubeTemplateCenter/` | CubeTemplateCenter | Go（gin） | 模板构建服务 |
| `sdk/` | sdk/python、sdk/go、sdk/node | Python / Go / TypeScript | 三端 SDK |
| `pkgs/` | CubeLog、blobstore、cubedb、proto | Go | 共享库 |
| `web/` | WebUI | React + TSX（`web/src/pages/` 19 个组件、main.tsx 18 路由，主导航 15 页面），:12088 | 管理控制台 |
| `deploy/` | one-click、kubernetes（Helm chart `cube` v0.7.2）、pvm、release-assets.yaml | Shell/YAML | 部署资产 |
| `configs/` | 内核 config、single-node 配置 | config/YAML | 配置样例 |
| `docs/zh/` | 官方中文文档（guide/architecture/changelog） | Markdown | 文档事实源 |
| `openapi.yml` | CubeAPI OpenAPI 3.1.0 | YAML（2458 行、26 paths） | 接口契约 |

## 三、已知信源瑕疵（引用时须附带说明）

1. **openapi.yml 版本号错位**：v0.7.2 tag 的 `openapi.yml` 中 `info.version` 仍为 "0.1.0"，但文件描述为 "E2B-compatible sandbox API server."、server 前缀 `/cubeapi/v1`。文档引用以"v0.7.2 tag 中的契约快照"口径表述，不称其为 0.1.0 版接口。
2. **changelog 日期偏差**：v0.7.2 changelog 标题写 2026-09-23，tag 实际打于 2026-09-24。以 tag commit 日期为准。
3. **hypervisor workspace members 与目录实存不一致**：v0.7.2 tag blob 的 `hypervisor/Cargo.toml` [workspace] 枚举 **29** 个成员（工作树随后续提交增至更多）；磁盘实存目录还含 docs/fuzz 等非成员目录。表述统一为"Cargo.toml 登记 29 个 workspace 成员"，不写"目录中存在 29 个组件目录"。（V 阶段勘误：R 阶段 F-098 曾误记为 28，名单漏 block_util，已按 tag blob 更正为 29。）
4. **post-release 变更**：CubeAPI handlers/services、sdk/go/envd.go、openapi.yml、CubeS3lvol C 源、deploy/one-click（工作树中 online-install.sh 已删除）在 tag 之后有变更；hypervisor/block_util 已存在于 tag 中（工作树仅修改其 `lib.rs`、`raw_sync.rs`）。所有此类引用以 `git show v0.7.2:<path>` 为准。
5. **性能数字前提**：60ms 基于裸金属环境；<5MB 内存开销基于 ≤32GB 规格沙箱实测。引用时必须附带前提，不外推到任意环境。

## 四、锚点与链接约定

- 源码锚点格式：`<相对路径>:<行号>`，相对路径自仓库根起算，如 `Cubelet/config/config.toml:78`。
- 全束事实编号 F-001 ~ F-244，锚点逐条索引见 [02-anchor-index.md](02-anchor-index.md)。
- 束内交叉链接使用相对路径；外部引用使用官方 URL，不引用本地绝对路径。
