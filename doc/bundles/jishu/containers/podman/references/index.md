# 信源登记簿

本目录按「一文档 = 一源码切片」原则为 Podman 知识包的每个核心事实提供可追溯源码锚点。每条 Reference 文档包含：事实编号表 + 原始文件路径 + 内容语义摘要；概念文档与示例文档中的每条断言均能通过 sources 字段关联到至少一条 Reference。

* [README.md 与 docs/README.md 文档工程](readme-source.md) — 项目定位与根 README 4 事实；Sphinx 文档工程目录结构（source/markdown、build、options、_static）6 事实；本地 man/HTML 构建流程 5 步；CODE_STRUCTURE.md 顶层目录 12 条；MANPAGE_SYNTAX 模板化手册页语法 3 条；REST API Swagger 注入与版本化 YAML 2 条。
* [CLI 层与 Domain 层架构源码](cli-domain-source.md) — cmd/podman Cobra 命令树（rootCmd、子命令包注册、RunE 三行模式、registry 单例）6 条；pkg/domain/entities 双接口（ContainerEngine/ImageEngine + Options 结构体 + Reports）4 条；pkg/domain/infra/abi 本地 libpod 直接调用 4 条；infra/tunnel 远程 HTTP bindings 转发 4 条；pkg/bindings 稳定 Go 客户端 ABI 承诺 + 错误码映射 3 条；pkg/specgen SpecGenerator 集中化 OCI 规格组装（CLI→Spec→OCI/Quadlet/Kube Play 复用）3 条；CLI→Domain 全链路执行流程图解。
* [libpod 核心与外部协同库](libpod-source.md) — Runtime/Container/Pod/Volume 四大实体（13 条，含 conmon 附加进程、Pod infra、持久化 SQLite/BoltDB 双模、cgroup v2 委托）；containers/storage GraphDriver+Layer/Image/Container 三级模型+ fuse-overlayfs 4 条；containers/image 5 传输协议 + Copy/Login 4 条；containers/buildah Builder+Containerfile 指令解析 3 条；containers/common/libnetwork Netavark/slirp4netns 网络栈 3 条；OCI crun/runc 调用链 2 条；`podman run` 下半球（specgen → storage→ net→ conmon→ crun→ cgroup→ DB）完整调用链图。

```{toctree}
:hidden:
:maxdepth: 7

readme-source
cli-domain-source
libpod-source
```
