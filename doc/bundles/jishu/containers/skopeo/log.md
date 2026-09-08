# 更新日志

## 2026-09-08

* **初始生成（OKF 知识包 v0.2 基准）**：首次创建 `skopeo/` 知识包，基于对 Skopeo v1.x 源码仓库（`external/dao/action/podman-container-tools/skopeo/`）中 cmd/skopeo/copy.go、delete.go、inspect.go、sync.go、login.go、main.go 与 README.md 共 7 条源码文件的 Grep 级事实登记，经 seven-concepts 方法论 **R（复盘）→ I（洞察）→ E（萃取）→ V（对抗审查）** 四阶段流程生成。
  * **Concepts 3 篇**：00-introduction 无守护进程设计哲学与 6 种传输协议架构 + Cobra CLI 框架 + 共享标志组设计 + 9 命令家族职责边界；01-copy-architecture copy.Image() 核心调用链 + copyOptions 结构体全字段 + multi-arch 策略（all/most-permissive/specific）+ sharedCopyOptions 安全/认证/压缩标志组；02-sync-architecture 三种源传输（docker/dir/yaml）分发机制 + regexp/semver 标签过滤 + dry-run 预演。
  * **Examples 1 篇**：00-migration-format-conversion Docker v2s2↔OCI 格式转换 + 跨注册表迁移 + 多架构 manifest list 处理 + docker-daemon 导入 + digest 文件输出 + 常见错误排查。
  * **References 1 篇**：source 信源登记（README.md + 6 个 Go 源码文件 Grep 级事实）。
* **溯源声明（sources 字段）**：全部 5 篇内容文档（3 Concept + 1 Example + 1 Reference）均携带 YAML frontmatter `sources` 字段，指向 references/source.md；每条事实带「事实编号 + 原始文件/路径锚点」，供 V 阶段对抗性核验逐点追溯。
* **生命周期字段**：全部内容文档统一 `status: stable`、`stale_after: 2027-09-08`（一年后针对 v2.x 破坏性 API 变更的保守重新评估节点）；`generated.at` / `verified.at` 分别记录本次生成时刻与本次 Grep 对抗验证时刻，两者分离可追溯。
* **域级注册**：本知识包注册于 `doc/bundles/jishu/containers/index.md` 容器生态域，与 podman、buildah 同属 Podman Container Tools 三件套，对应 toctree 项已新增、项目列表表格已新增一行。
