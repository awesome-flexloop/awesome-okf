# 变更日志

## v1.1.0 (2026-09-08)

### 更新

- 补充版本号 1.6.0（来源：`pyproject.toml`）
- 补充全局参数表（`--in-pod`、`--pod-args`、`--parallel`、`--skip-missing-url`、`--skip-directory-validation` 等）
- 新增 Pod 支持章节（`--in-pod` 用法）
- 新增 systemd 集成章节（`compose_systemd` 命令：register/unregister/create-unit/list）
- 新增 config 命令章节（输出合并后的 YAML 配置）
- 补充 `links` 配置模式说明（服务间旧式显式依赖声明）
- 更新项目信息：标注构建后端为 setuptools（vendor 豁免）

### 事实来源

- 源码：`external/dao/action/Containers/podman-compose/podman_compose.py`（v1.6.0）
- 示例：`examples/hello-python/`、`examples/nodeproj/`

---

## v1.0.0 (2026-08-26)

### 新增

- 初始 OKF Wiki Bundle 生成
- 信源文档：`references/readme-source.md`（官方 README 信源登记）
- 概念文档（4个）：
  - `concepts/00-introduction.md`：快速上手与 Compose Spec 兼容
  - `concepts/01-daemonless-arch.md`：daemon-less 架构（直接调用 podman CLI）
  - `concepts/02-rootless.md`：rootless 模式下的网络与卷
  - `concepts/03-compose-patterns.md`：Compose 文件常见模式
- 示例文档（2个）：
  - `examples/01-wordpress.md`：WordPress + MariaDB 部署示例
  - `examples/02-multi-container.md`：Web + Redis 集群多容器编排
- 索引文件：各级 index.md 导航
- Bundle 根索引：`index.md`（含 okf_version frontmatter）

### 生成信息

- **生成者**：source-code-to-okf-wiki skill
- **事实来源**：`.trae/specs/containers-okf-wiki/facts-podman-compose.md`
- **代码版本**：podman-compose main 分支
- **OKF 规范版本**：v0.2
