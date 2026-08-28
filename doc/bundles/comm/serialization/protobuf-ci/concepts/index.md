# protobuf-ci 概念文档

按"仓库全景 → 构建路径 → 缓存策略 → 基础动作 → 专项动作"五篇递进。

* [仓库定位与结构：可复用 CI 动作集合](01-repo-positioning-and-structure.md) — 9 个顶层与 7 个 internal composite action 清单、@v6 固定 tag 的 release 纪律与主仓引用计数矩阵。
* [bazel 与 bazel-docker 构建动作及远程缓存](02-bazel-build-actions.md) — 宿主机/容器两条 Bazel 执行路径对比、BAZEL_FLAGS 拼装、bazelisk 缓存与 GCS 远程缓存。
* [ccache 与 sccache 编译缓存动作](03-ccache-sccache-actions.md) — ccache 三级 restore-keys 回退链、Windows 专属配置与 sccache GCS 桶配置。
* [docker、checkout、bash 基础动作与 internal 基建](04-docker-checkout-bash-actions.md) — 非 Bazel 构建路径执行底座、submodule 三连重试与 docker-run/gcloud-auth/setup-runner 基建。
* [composer-setup 与 cross-compile-protoc 专项动作](05-composer-cross-compile-actions.md) — PHP 依赖缓存（pull_request_target 只读）与复用 bazel-docker 构建 protoc_static 的交叉编译动作。

```{toctree}
:hidden:
:maxdepth: 7

01-repo-positioning-and-structure
02-bazel-build-actions
03-ccache-sccache-actions
04-docker-checkout-bash-actions
05-composer-cross-compile-actions
```
