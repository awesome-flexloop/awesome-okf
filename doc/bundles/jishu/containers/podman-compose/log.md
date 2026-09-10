# 变更日志

## v1.4.0 (2026-09-10)

### 新增

- 基于官方 `examples/` 目录 12 个示例应用精读，新增 1 篇示例文档：
  - `examples/03-official-examples-gallery.md`：官方示例图鉴——按三级梯度拆解 12 个用例（单服务最小用例 echo/hello-app/docker-inline/nvidia-smi；双服务编排 azure-vote/wordpress/busybox/hello-python；多服务与高级模式 hello-app-redis/nodeproj/awx3/awx17），覆盖插值参数化、命名卷、links 别名、extends 继承、read_only+tmpfs、build+image 双轨、GPU 预留、dockerfile_inline、`run --rm` 一次性任务容器等模式，附横向模式对照表
- 新增信源文档 `references/examples-source.md`：12 个示例的服务规模、核心演示特性与关键文件索引、事实注记（命名混用、插值惯例、短格式 env、extends 唯一用例等）

### 更新

- `examples/index.md`：示例清单补充 03，原「更多官方示例」简表替换为图鉴指引，toctree 同步
- `references/index.md`：信源清单与 toctree 补充 examples-source
- 根 `index.md`：Bundle 结构树、实战示例导航、信源表、frontmatter sources 补充示例信源

### 事实来源

- 官方示例：`external/dao/action/Containers/podman-compose/examples/`（12 个应用目录，v1.6.0 快照 commit e3df104）
- 源码交叉印证：字段翻译与归一化逻辑（`rec_subs`、`container_to_build_args`、`is_local`、`resolve_extends`）

---

## v1.3.0 (2026-09-10)

### 新增

- 基于官方 `docs/`（7 份 Changelog、Extensions、Mappings）与 `completion/bash` 补全脚本精读，新增 2 篇概念文档：
  - `concepts/08-x-podman-extensions.md`：x-podman 扩展字段全解——容器级（uidmaps/gidmaps/rootfs/no_hosts/passwd）、密钥级（relabel）、网络级（disable_dns/dns/routes）、服务网络扩展（mac_address/interface_name）、podman 特有网络模式（slirp4netns/pasta/ns/private）与挂载类型（glob/image）、Docker Compose 兼容开关（docker_compose_compat 元开关与 3 个分项）、自定义 Pod 管理（in_pod/pod_args）
  - `concepts/09-version-evolution.md`：版本演进与能力矩阵——0.1.x 六种网络映射模式与 1.x 架构断点、1.1.0→1.6.0 能力引入时间线、三条演进主线（方言退场/可靠性加固/双语标签）、podman 4.6.0/5.6.0 与 Python 版本门槛、1.6.0 后未发布的 newsfragments 变更、bash 补全脚本机制与已知漂移
- 新增信源文档 `references/docs-source.md`：docs/ 9 文件与 completion/ 脚本内容索引、版本固定、补全脚本与代码漂移注记

### 更新

- `concepts/index.md`：概念清单、架构路径与生产路径补充 08-09，toctree 同步
- `references/index.md`：信源清单与 toctree 补充 docs-source
- 根 `index.md`：Bundle 结构树、源码精读导航、信源表、frontmatter sources 补充官方文档信源

### 事实来源

- 官方文档：`external/dao/action/Containers/podman-compose/docs/`（Changelog-1.1.0~1.6.0、Extensions.md、Mappings.md）
- 补全脚本：`external/dao/action/Containers/podman-compose/completion/bash/podman-compose`（411 行）
- 源码交叉印证：`podman_compose.py`（v1.6.0，commit e3df104）

---

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
