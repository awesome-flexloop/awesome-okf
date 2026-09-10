# 变更日志

## v1.6.0 (2026-09-10)

### 新增

- 跨束对比文档 `concepts/10-compose-vs-podman-py.md`：podman-compose（声明式 CLI 编排器，GPL-2.0）与 podman-py（命令式 Python SDK，Apache-2.0，v5.8.0）全面对比——控制路径对照（asyncio 子进程 vs requests/REST）、十维差异表（范式/执行机制/抽象边界/状态模型/配置能力/远程/错误处理/可测试性等）、Docker 兼容路径差异、选型决策表（9 个场景）、组合使用模式（compose 写标签 / SDK 按标签读），以及 compose 不依赖 podman-py 的事实核验

### 更新

- `concepts/index.md`：概念清单与架构学习路径补充 10，toctree 同步
- 根 `index.md`：Bundle 结构树与源码精读导航补充对比文档
- 跨束互链：podman-py 束根索引新增指向本文档的对比入口（反向链接）

### 事实来源

- podman-compose 束：本束 04-09 源码精读文档（v1.6.0，commit e3df104）
- podman-py 束：`doc/bundles/jishu/containers/podman-py/`（v5.8.0，6 概念/3 示例/3 信源）

---

## v1.5.0 (2026-09-10)

### 新增

- 官方 examples/ 12 个示例由图鉴（03）进一步逐例详细展开，新增 8 篇示例教程（按 §6.5 多轮增量扩展规范编号续接）：
  - `examples/04-echo-hello-app.md`：echo/hello-app 单服务最小用例——端口参数化三种用法、curl 回显探针、最小生命周期
  - `examples/05-docker-inline-gpu.md`：dockerfile_inline 内联构建机制（临时 .containerfile 生命周期）与 GPU 预留（deploy.resources → --device CDI 翻译）
  - `examples/06-azure-vote.md`：前端+Redis 双服务标准形态——服务名零配置发现、dict/list 两种 env 语法对照、项目级 .env 角色
  - `examples/07-busybox-syntax.md`：配置语法参考卡——links 别名隐含依赖、空值 env 透传、labels、注释形式的 12 个可选字段目录（13 行注释计数已经脚本核实）
  - `examples/08-hello-python.md`：aiohttp+aioredis 计数器——build/image 双轨与 is_local、read_only+命名卷写路径设计
  - `examples/09-redis-cluster.md`：7 服务 6 节点 Bitnami Redis 集群——creator 初始化角色、REDIS_NODES 服务名发现、两层 depends_on 与 service_started 条件边界
  - `examples/10-nodeproj.md`：Node 开发环境——extends 基服务合并、两层 env 分工、rootless UID 传递与 HOME 设计、read_only+tmpfs+bind mount、run --rm --no-deps 初始化
  - `examples/11-awx-large-app.md`：awx3 五服务 links 组网与 awx17 Ansible Jinja2 模板生成（绝对路径 sed 改写 + run --rm --service-ports migrate）

### 更新

- `examples/index.md`：示例清单补 04-11（共 11 篇），学习路径改为入门/语法速查/进阶/高级/图鉴五级，toctree 同步
- 根 `index.md`：Bundle 结构树展开 11 篇示例、实战示例导航增加逐例详解入口

### 事实来源

- 官方示例：`external/dao/action/Containers/podman-compose/examples/`（12 目录，commit e3df104）
- 本轮补读应用代码：hello-python/app/web.py+requirements.txt、nodeproj Dockerfile+package.json+index.js、awx17 docker-compose.yml.j2

---

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
