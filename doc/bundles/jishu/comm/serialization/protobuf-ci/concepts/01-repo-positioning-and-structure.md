---
type: Concept
title: "仓库定位与结构：可复用 CI 动作集合"
description: "protobuf-ci 仓库的定位与结构全景：9 个顶层与 7 个 internal composite action 清单、@v6 固定 tag 的 release 版本纪律，以及主仓 14 个 workflow 的引用计数矩阵。"
tags: [protobuf-ci, github-actions, composite-action]
generated: { by: agent/trae-glm, at: 2026-08-28T00:00:00Z }
verified: { by: process:source-code-to-okf-wiki-v, at: 2026-08-28T00:00:00Z }
status: stable
stale_after: 2027-06-30
sources:
  - id: protobuf-ci-actions
    resource: /references/protobuf-ci-actions.md
    title: "protobuf-ci 仓库 CI 动作信源"
---

protobuf-ci 是 protocolbuffers 组织下的独立 CI（持续集成，Continuous Integration）基础设施仓库。顶层 README 对其定位的原句是 "A collection of actions and reusable workflows for CI testing in Protobuf repositories."——一组服务于 Protobuf 系列仓库 CI 测试的可复用动作（action）与工作流（workflow）集合。它与 protobuf 主仓（双构建系统总览见 [../../protobuf/concepts/00-repo-overview-and-build-systems.md](../../protobuf/concepts/00-repo-overview-and-build-systems.md)）解耦维护：主仓不内嵌这些步骤，而是以固定 tag 引用本仓库的 composite action（复合动作——将多步骤流程打包为单个可复用单元的 GitHub Actions 形态）。各 action 的源码路径与字段细节登记于 [/references/protobuf-ci-actions.md](/references/protobuf-ci-actions.md)。

## 仓库定位与复用边界

README 明确划定了变更边界："Actions and workflows here are expected to be reusable and changes here should apply to multiple test files/languages. If you want to make a change to a single test or language please make the change directly in the main protobuf repository."。换言之：本仓库只承接跨测试文件、跨语言的通用变更；只想改某个测试或某种语言，应直接修改主仓。

与这条边界配套的是版本纪律。README Releases 小节原句："Any change in this repository that you wish to see reflected in other Protobuf repositories requires a release."，发布流程指向内部 playbook "Making and Releasing Changes to protobuf-ci"。主仓侧的实际引用方式与此印证：全部引用形式均为 `uses: protocolbuffers/protobuf-ci/<action>@v6`——固定 tag（而非分支追踪），因此 protobuf-ci 的任何变更必须先打 release 才会生效到其他仓库。

## 目录结构全景

仓库根目录仅含十个目录与三个顶层文件（CONTRIBUTING.md、LICENSE、README.md）。九个顶层 action 各占一个目录、各含一个 action.yml：

| 顶层 action | action.yml 的 name | 职责 |
|---|---|---|
| bash/ | 'Non-Bazel Bash Run' | 非 Bazel 构建体系的 bash 脚本执行 |
| bazel/ | 'Docker Bazel Run' | 宿主机上的 Bazel 构建运行 |
| bazel-docker/ | 'Docker Bazel Run' | docker 容器内的 Bazel 构建运行 |
| ccache/ | 'CCache Setup' | ccache 编译缓存配置 |
| checkout/ | 'Github Checkout' | 仓库检出（含 submodule） |
| composer-setup/ | 'Composer Setup' | PHP composer 依赖安装与缓存 |
| cross-compile-protoc/ | 'Cross-compile protoc' | protoc 二进制交叉编译 |
| docker/ | 'Docker Non-Bazel Run' | 非 Bazel 构建体系的 docker 执行 |
| sccache/ | 'Setup sccache' | sccache 编译缓存配置 |

internal/ 目录下另有 7 个子 action（各含一个 action.yml）：bazel-setup、ccache-setup-windows、docker-run、gcloud-auth、repository-cache-restore、repository-cache-save、setup-runner。它们不面向使用方直接暴露，而是由顶层 action 在内部装配调用——例如 bazel 与 bazel-docker 都经由 internal/bazel-setup 完成 BAZEL_FLAGS 与远程缓存装配。

## 主仓引用矩阵

protobuf 主仓 .github/workflows/ 目录共含 24 个 yaml 文件（另有 README.md、release_prep.sh、release_prep_test.sh），其中 14 个引用 protocolbuffers/protobuf-ci。按 grep 行数统计的引用计数：

| 主仓 workflow | 引用数 | 备注 |
|---|---|---|
| test_cpp.yml | 28 | 含 3 处 bash、8 处 docker、6 处 sccache、3 处 bazel-docker、1 处 cross-compile-protoc |
| test_ruby.yml | 12 | |
| test_upb.yml | 8 | |
| test_php.yml | 8 | |
| test_csharp.yml | 8 | |
| test_bazel.yml | 6 | |
| test_objectivec.yml | 6 | |
| test_python.yml | 4 | |
| test_java.yml | 4 | 另有 2 处注释掉的引用 |
| test_rust.yml | 4 | |
| test_php_ext.yml | 3 | |
| staleness_check.yml | 2 | |
| test_hpb.yml | 2 | |
| test_yaml.yml | 1 | |

典型组合：staleness_check.yml 仅组合 checkout@v6 + bazel@v6；test_cpp.yml 组合 checkout、bazel-docker、cross-compile-protoc、sccache、docker、bash、bazel 全家桶，是引用面最广的 workflow；test_yaml.yml 仅用 checkout@v6。9 个顶层 action 全部被主仓以 @v6 引用——checkout@v6、bazel@v6、bazel-docker@v6、bash@v6、ccache@v6、composer-setup@v6、cross-compile-protoc@v6、docker@v6、sccache@v6——无一闲置。

## 治理与许可

LICENSE 为 Apache License Version 2.0, January 2004。CONTRIBUTING.md 的治理要点：贡献须签署 Google CLA（贡献者许可协议，Contributor License Agreement，https://cla.developers.google.com/）；遵循 Google's Open Source Community Guidelines；所有提交须经 GitHub pull request 评审。

## 相关概念

- [/concepts/02-bazel-build-actions.md](/concepts/02-bazel-build-actions.md) — bazel 与 bazel-docker 构建动作及远程缓存
- [/concepts/03-ccache-sccache-actions.md](/concepts/03-ccache-sccache-actions.md) — ccache 与 sccache 编译缓存动作
- [/concepts/04-docker-checkout-bash-actions.md](/concepts/04-docker-checkout-bash-actions.md) — docker、checkout、bash 基础动作与 internal 基建
