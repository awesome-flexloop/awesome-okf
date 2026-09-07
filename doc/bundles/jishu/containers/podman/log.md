# 更新日志

## 2026-09-07

* **初始生成（OKF 知识包 v1.0 基准）**：首次创建 `podman/` 知识包，基于对 Podman v6.x 源码仓库（`external/dao/action/podman-container-tools/podman/`）中 cmd/podman/、pkg/domain/、libpod/、pkg/api/、pkg/bindings/、pkg/specgen/、README.md、docs/README.md、docs/CODE_STRUCTURE.md 共 37 条架构与命令事实的逐文件 Grep 核验，经 seven-concepts 方法论 **R（复盘）→ I（洞察）→ E（萃取）→ V（对抗审查）** 四阶段流程生成。
  * **Concepts 6 篇**：00-introduction daemonless 架构四层代码 + 9 命令域；01-commands 容器状态机 + 查询四件套 + 镜像传输协议 + Pod infra；02-rootless user namespace 映射 + fuse-overlayfs + slirp4netns + cgroup v2 delegation + 禁用 privileged；03-docker-compat CLI 别名双兼容 + 双环境变量 + REST 双端点 + podman-compose + 迁移五步灰度；04-quadlet-kube 四类单元文件 + 启动依赖图 + auto-update+healthcheck 自愈闭环 + kube play/apply/down 幂等；05-remote-machine UDS/SSH/TCP 三协议 + 命名连接 + macOS 后端对比 + Windows WSL2 原生推荐路径。
  * **Examples 2 篇**：01-rootless-production 九步 EL9 生产部署（含 cgroup v2 + linger + firewalld + auto-update timer + 8 项验收）；02-quadlet-stack 三服务生产级 Quadlet 栈（Network+Volume×1 + Container×3、Secret 注入、健康检查 SQL/PING/HTTP、资源上限、ReadOnly 加固、7 项验收矩阵）。
  * **References 3 篇**：readme-source 文档工程与顶层目录 18 条锚点；cli-domain-source CLI+Domain+SpecGenerator 六段 24 条源码锚点+执行路径图；libpod-source 四大实体+四协同库+OCI runtime 共 34 条底层锚点+下半球调用链图。
* **溯源声明（sources 字段）**：全部 11 篇内容文档（6 Concept + 2 Example + 3 Reference）均携带 YAML frontmatter `sources` 字段，指向对应 Reference；每条 Reference 内每条事实带「事实编号 + 原始文件/路径锚点」，供后续 V 阶段对抗性核验逐点追溯。
* **生命周期字段**：全部内容文档统一 `status: stable`、`stale_after: 2027-09-07`（一年后针对 v7.x 破坏性 API 变更的保守重新评估节点）；`generated.at` / `verified.at` 分别记录本次生成时刻与本次 Grep 对抗验证时刻，两者分离可追溯。
* **域级注册**：本知识包注册于 `doc/bundles/jishu/containers/index.md` 容器生态域，为该域第 12 个项目（补全原有 podman-py、podman-compose 之外的 Podman 引擎本体知识覆盖空缺），对应 toctree 项已新增、项目列表表格已新增一行。
