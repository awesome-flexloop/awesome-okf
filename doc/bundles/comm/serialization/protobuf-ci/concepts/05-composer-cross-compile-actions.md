---
type: Concept
title: "composer-setup 与 cross-compile-protoc 专项动作"
description: "composer-setup 的 PHP 依赖缓存（pull_request_target 只读、COMPOSER_HOME、chmod 777 修复）与 cross-compile-protoc 复用 bazel-docker 构建 protoc_static 并输出 $PROTOC。"
tags: [protobuf-ci, github-actions, cross-compile]
generated: { by: agent/trae-glm, at: 2026-08-28T00:00:00Z }
verified: { by: process:source-code-to-okf-wiki-v, at: 2026-08-28T00:00:00Z }
status: stable
stale_after: 2027-06-30
sources:
  - id: protobuf-ci-actions
    resource: /references/protobuf-ci-actions.md
    title: "protobuf-ci 仓库 CI 动作信源"
---

除通用构建与缓存动作外，protobuf-ci 提供两个专项动作：composer-setup 服务 PHP 依赖管理，cross-compile-protoc（交叉编译 protoc——在一种环境下构建另一种目标架构产物）服务 protoc 二进制的多架构产出。二者在 [01 篇](/concepts/01-repo-positioning-and-structure.md)的全景之内，本篇展开各自的内部机制；字段级细节见 [/references/protobuf-ci-actions.md](/references/protobuf-ci-actions.md)。

## composer-setup：PHP 依赖缓存

inputs：cache-prefix（required: true）、directory（"The directory containing composer.json"）。

缓存按事件分路：非 pull_request_target 事件 uses actions/cache（注释 # v5.0.1），key 为：

```yaml
composer-${{ runner.os }}-${{ inputs.cache-prefix }}-${{ hashFiles(format('{0}/composer.json', inputs.directory)) }}
```

（restore-keys 两级回退。）pull_request_target 事件则改用 actions/cache/restore——注释原句 "will never upload a new cache (untrusted path)"：不可信路径永不写缓存，与 bazel 远程缓存（[02 篇](/concepts/02-bazel-build-actions.md)）的 fork PR 禁写策略一脉相承。无论哪种事件，都设置 `COMPOSER_HOME=${{ github.workspace }}/composer-cache`，把 composer 主目录（含其缓存）固定到工作区内以便被捕获。

执行步骤为 `composer install --ignore-platform-reqs --working-dir=${{ inputs.directory }}`（注释说明 php-actions/composer 在非 Linux 平台不可用，引用 php-actions/composer#95，故改为直接调用 composer）。随后执行权限修复：

```yaml
sudo chmod -R 777 ${{ inputs.directory }}/composer.lock ${{ inputs.directory }}/vendor
```

chmod 777（读/写/执行全开）用于解决容器内外 UID 不一致导致的产物权限问题。

## cross-compile-protoc：复用 bazel-docker 的交叉编译

name 'Cross-compile protoc'，description 'Produces a cross-compiled protoc binary for a target architecture'。inputs：credentials（required: true）、architecture（required: true，"The target architecture to build for"）、image（required: true）。outputs：protoc（"Cross-compiled protoc location. Also output to $PROTOC"，value 来自 steps.output.outputs.protoc）。

它不自带构建逻辑，而是复用 bazel-docker：uses `./../../_actions/current/bazel-docker`，bazel-cache 传 `xcompile-protoc/${{ inputs.architecture }}`（按目标架构隔离缓存），bash 传：

```yaml
bazel build //:protoc_static --config=${{ inputs.architecture }} $BAZEL_FLAGS
cp bazel-bin/protoc_static .
```

即以 Bazel 的 `--config={architecture}` 交叉编译配置构建 `//:protoc_static` 目标。构建完成后：

```yaml
echo "PROTOC=protoc-${{ inputs.architecture }}" >> $GITHUB_ENV
mv protoc_static $PROTOC
```

产物路径同时进入 $GITHUB_ENV 与 outputs.protoc——workflow 内的后续步骤与环境变量消费方都能拿到同一位置。主仓 test_cpp.yml 中有 1 处 cross-compile-protoc 引用，与 checkout、bazel-docker、sccache、docker、bash、bazel 组合覆盖 C++ 交叉验证矩阵。

## 相关概念

- [/concepts/01-repo-positioning-and-structure.md](/concepts/01-repo-positioning-and-structure.md) — 仓库定位与结构：可复用 CI 动作集合
- [/concepts/02-bazel-build-actions.md](/concepts/02-bazel-build-actions.md) — bazel 与 bazel-docker 构建动作及远程缓存
