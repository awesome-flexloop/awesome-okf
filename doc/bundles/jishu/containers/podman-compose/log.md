# 变更日志

## v1.2.0 (2026-09-10)

### 新增

- 基于 `podman_compose.py` 全量源码精读（约 5534 行）新增 4 篇源码级概念文档：
  - `concepts/04-source-architecture.md`：单文件逻辑分层、`cmd_run/cmd_parse` 装饰器命令注册、`Podman` 类三种子进程调用（output/run/exec）、asyncio 信号量并发模型、日志流增量 UTF-8 解码与着色
  - `concepts/05-cli-translation-layer.md`：`container_to_args` 翻译主函数（service dict → podman argv）、卷/网络/密钥/资源参数生成、标签即数据库的无状态设计、config-hash 变更检测
  - `concepts/06-config-pipeline.md`：14 候选文件发现与递归向上查找、环境变量分层、6 操作符 bash 风格插值引擎、短语法归一化、`!override`/`!reset` 深合并、extends/include/profiles 语义、x-podman 兼容开关
  - `concepts/07-dependency-lifecycle.md`：12 种依赖条件与 docker 条件映射、`_deps/_dependents` 依赖图、`podman wait --condition` 启动屏障、up 重建判定三条件、拉取策略优先级、pod 创建、down 清理顺序、systemd 集成
- 新增信源文档 `references/source-code-map.md`：版本固定（`__version__=1.6.0`、git `v1.6.0-97-ge3df104`、commit `e3df10472e194ab6d547b5ad25542c5c79e1a5fb`）、10 层结构地图、核心符号行号索引、podman 版本门槛表

### 更新

- `concepts/index.md`：概念清单与架构学习路径补充 04-07，toctree 同步
- `references/index.md`：信源清单与 toctree 补充 source-code-map
- 根 `index.md`：Bundle 结构树、新增「源码精读」导航分区、信源表、frontmatter sources 补充源码信源

### 事实来源

- 源码：`external/dao/action/Containers/podman-compose/podman_compose.py`（v1.6.0，commit e3df104，2026-08-11）
- 方法：source-code-to-okf-wiki 工作流 R→I→E→V→C（信源版本固定 + 逐行事实采集 + Grep 级符号核验）

---

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
