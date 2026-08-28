---
type: Concept
title: "docker、checkout、bash 基础动作与 internal 基建"
description: "非 Bazel 构建路径的执行底座：bash 与 docker 动作的 staleness 检查与 DOCKER_RUN_FLAGS 拼接、checkout 的 submodule 三连重试，以及 docker-run、gcloud-auth、setup-runner 三个 internal 基建机制。"
tags: [protobuf-ci, github-actions, ci-infrastructure]
generated: { by: agent/trae-glm, at: 2026-08-28T00:00:00Z }
verified: { by: process:source-code-to-okf-wiki-v, at: 2026-08-28T00:00:00Z }
status: stable
stale_after: 2027-06-30
sources:
  - id: protobuf-ci-actions
    resource: /references/protobuf-ci-actions.md
    title: "protobuf-ci 仓库 CI 动作信源"
---

非 Bazel 构建路径（CMake 等体系）的 CI 执行由三个顶层动作支撑：bash（直接运行 bash 脚本）、docker（在指定镜像内运行命令）、checkout（仓库检出）。它们的下层是 internal/ 基建：docker-run（统一的 docker 运行封装）、gcloud-auth（GCP 凭据链）与 setup-runner（runner 环境修复）。三者的共同特征是：即便走非 Bazel 路径，"陈旧文件再生成"检查仍借助 Bazel 完成。字段级细节见 [/references/protobuf-ci-actions.md](/references/protobuf-ci-actions.md)。

## bash 动作与 staleness 检查

bash（name 'Non-Bazel Bash Run'，description 'Run a bash script for Protobuf CI testing with a non-Bazel build system'）的 inputs：credentials（required: true，"The GCP credentials to use for reading the docker image"）、command（required: true，"A command to run in the docker image"）、bazel-version（default "8.7.0"）、bazel-flags（"Bazel flags to use for staleness regen"）。

步骤序列：①"Symlink current Actions repo"（`ln -fs $GH_ACTION_DIR $GH_ACTION_CLONE`，建立 `../../_actions/current` 符号链接，使 composite action 能以相对路径互相引用）→ ②uses `./../../_actions/current/internal/setup-runner` → ③"Update stale files using Bazel"（uses `./../../_actions/current/bazel`，bazel-cache: regenerate-stale-files，bash: `./regenerate_stale_files.sh $BAZEL_FLAGS`）→ ④"Run"（`shell: bash, run: ${{ inputs.command }}`）。

## docker 动作与 DOCKER_RUN_FLAGS

docker（name 'Docker Non-Bazel Run'，description 'Run a docker image for Protobuf CI testing with a non-Bazel build system'）的 inputs：credentials、command、image（均 required: true）、platform、skip-staleness-check（type: boolean）、entrypoint、extra-flags，以及 staleness-image（default "us-docker.pkg.dev/protobuf-build/containers/common/linux/bazel:8.7.0-4d8e80ef93b0219fb907af9dd4596b92946995d8"）。

步骤：Symlink → uses internal/setup-runner → 未跳过 staleness 时 uses `./../../_actions/current/bazel-docker`（image 取 inputs.staleness-image，bazel-cache: regenerate-stale-files，bash: `./regenerate_stale_files.sh $BAZEL_FLAGS`）；skip-staleness-check 为真时跳过该步，仅 uses internal/gcloud-auth。

DOCKER_RUN_FLAGS 按需拼接：platform 给出时追加 `--platform ${{inputs.platform}}`；entrypoint 给出时追加 `--entrypoint ${{inputs.entrypoint}}`；最终 uses internal/docker-run，run-flags 为 `${{ env.DOCKER_RUN_FLAGS }} ${{ inputs.extra-flags }}`。

## checkout 动作与 submodule 三连

checkout（name 'Github Checkout'，description 'Check out a Github repository'）的 inputs：ref（required: true，"The branch, tag or SHA to checkout"）、submodules（"Whether or not to checkout submodules"）。

第一步 uses `actions/checkout@08c6903cd8c0fde910a37f88322edcfb5dd907a8`（注释 # v5.0.0 (Node 24)），参数 ref。submodules 为真时再 uses `nick-fields/retry@ad984534de44a9489a53aefd81eb77f87c70dc60`（注释 # v4.0.0，timeout_seconds: 30、retry_wait_seconds: 30、max_attempts: 5）执行 submodule 三连命令：

```yaml
git submodule deinit --all -f
git submodule sync
git submodule update --force --init
```

（submodules=='recursive' 时第三条追加 `--recursive`。）三连的语义：deinit 清理旧状态 → sync 校正远端 URL → update 强制重新初始化拉取；配合 5 次重试对抗 submodule 拉取的网络抖动。

## internal/docker-run 与 fork PR 安全拦截

docker-run（name 'Run Docker'）的 inputs：image、command（required: true，"A raw docker command to run"）、run-flags、docker-cache（注释 "WARNING: loading from cache appears to be slower than pull!"）。

安全步骤：pull_request_target 事件且 image 含 `us-docker.pkg.dev/protobuf-build/release-containers/` 时，经 actions/github-script#v8.0.0 执行 `core.setFailed('Pull requests from forks cannot use release Docker images.')`——fork PR 禁用 release 镜像，防止不可信代码以受信入口运行（与 [02 篇](/concepts/02-bazel-build-actions.md)的远程缓存禁写同属一套 fork PR 安全策略）。随后执行 `gcloud auth configure-docker -q us-docker.pkg.dev`。

其余步骤：uses `docker/setup-qemu-action@96fe6ef7f33517b61c61be40b68a1882f3264fb8`（注释 # v4.2.0，continue-on-error: true，镜像 us-docker.pkg.dev/protobuf-build/containers/test/binfmt@sha256:10d6...）准备多架构模拟；docker-cache 给出时用 actions/cache（key: `${{ inputs.image }}`，path: ci/docker/）保存/加载 `docker image save --output ./ci/docker/{image}.tar`；否则经 nick-fields/retry#v4.0.0（timeout_minutes: 5、retry_wait_seconds: 60、max_attempts: 5）执行 `docker pull -q`。docker-cache 的注释表明镜像缓存加载反而比直接 pull 慢，故默认走 pull 路径。

## internal/gcloud-auth 与 setup-runner

gcloud-auth（name 'Authenticate for GCP'）输入 credentials、输出 credentials-file：uses `google-github-actions/auth@7c6bc770dae815cd3e89ee6cdf493a5fab2cc093`（注释 # v3.0.0，credentials_json 参数，仅当 env.CREDENTIALS_FILE 为空——支持上游已注入凭据时跳过）与 `google-github-actions/setup-gcloud@26f734c2779b00b7dda794207734c511110a4368`（注释 # v3.0.0，version: ">= 446.0.0"）；执行 `gcloud info` 验证；输出 CREDENTIALS_FILE 到 GITHUB_ENV/GITHUB_OUTPUT。bazel 远程缓存与 sccache GCS 桶的凭据均来源于此。

setup-runner（name 'Setup CI Runner'，无 inputs）唯一步骤 "Fix Windows line breaks"：runner.os == 'Windows' 时执行 `find . -type f -print0 | xargs -0 d2u 2>/dev/null || echo "Ignoring failure"`——用 d2u（dos2unix，CRLF→LF 行尾转换工具）修复全仓库行尾，失败则静默忽略；头部注释含 TODO(b/267357823)。

## 相关概念

- [/concepts/01-repo-positioning-and-structure.md](/concepts/01-repo-positioning-and-structure.md) — 仓库定位与结构：可复用 CI 动作集合
- [/concepts/02-bazel-build-actions.md](/concepts/02-bazel-build-actions.md) — bazel 与 bazel-docker 构建动作及远程缓存
- [/concepts/03-ccache-sccache-actions.md](/concepts/03-ccache-sccache-actions.md) — ccache 与 sccache 编译缓存动作
