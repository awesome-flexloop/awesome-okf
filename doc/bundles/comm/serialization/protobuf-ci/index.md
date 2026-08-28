---
okf_version: "0.2"
---

# protobuf-ci 知识库

本知识包是 Google [protobuf-ci](https://github.com/protocolbuffers/protobuf-ci) 仓库（@v6）的系统化中文教程，基于源码深度阅读生成。protobuf-ci 是 protobuf 家族仓库共享的 GitHub Actions composite action 集合：9 个顶层动作 + 7 个 internal 动作，为主仓 14 个 workflow 提供 Bazel/CMake 构建执行、五层缓存（bazel 远程缓存 / ccache / sccache / repository cache / bazelisk cache）与跨平台容器底座。所有内容均溯源至 protobuf-ci 源码，遵循 [OKF v0.2 规范](../../../meta/okf-spec/index.md)。

## 概念文档（concepts/）

* [仓库定位与结构：可复用 CI 动作集合](concepts/01-repo-positioning-and-structure.md) — 9 个顶层与 7 个 internal action 清单、@v6 固定 tag 的 release 纪律与主仓引用计数矩阵。
* [bazel 与 bazel-docker 构建动作及远程缓存](concepts/02-bazel-build-actions.md) — 宿主机/容器两条 Bazel 执行路径、BAZEL_FLAGS 拼装、bazelisk 缓存与 GCS 远程缓存。
* [ccache 与 sccache 编译缓存动作](concepts/03-ccache-sccache-actions.md) — ccache 三级 restore-keys 回退链、Windows 专属配置与 sccache GCS 桶配置。
* [docker、checkout、bash 基础动作与 internal 基建](concepts/04-docker-checkout-bash-actions.md) — 非 Bazel 构建路径执行底座、submodule 三连重试与 docker-run/gcloud-auth/setup-runner 基建。
* [composer-setup 与 cross-compile-protoc 专项动作](concepts/05-composer-cross-compile-actions.md) — PHP 依赖缓存与复用 bazel-docker 构建 protoc_static 的交叉编译动作。

## 信源登记簿（references/）

* [protobuf-ci CI 动作信源登记](references/protobuf-ci-actions.md) — 顶层/internal action 与主仓 workflow 交叉验证信源，支撑 F-CI-001~056 共 56 条事实。

## 信任与生命周期说明

* **status 判定依据**：全部 6 个内容文档（5 个概念 + 1 个信源登记）均 `status: stable`。内容基于对 protobuf-ci @v6 源码（`external/libs/protocolbuffers/protobuf-ci/`）的逐动作阅读与事实提取（56 条事实），经 R→I→E→V→C 五阶段流程生成。
* **stale_after 解释**：统一设置为 `2027-06-30`。protobuf-ci 经由 release 机制向家族仓库供动作（任何变更须发布新 tag 才能生效），该日期作为针对 v7 大版本重新评估的保守节点。
* **核验链路**：`generated.at` 记录各文档原始生成时刻（2026-08-28）；`verified.at` 记录 V 阶段 Grep 验证事件（2026-08-28），两者分离、可追溯。
* **关联知识包**：主仓语言/编译器/运行时知识见姊妹束 [protobuf](../protobuf/index.md)。

本知识包共收录 6 个内容文档（5 个概念 + 1 个信源登记），另含 2 个子目录 index.md 与根 index.md、log.md。

```{toctree}
:hidden:
:maxdepth: 7

concepts/index
references/index
log
```
