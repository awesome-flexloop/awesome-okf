---
type: Concept
title: 配置加载管线：插值、归一化与深合并
description: 源码视角解析 compose 文件发现、环境变量分层、bash 风格插值引擎、短语法归一化、!override/!reset 深合并及 extends/include/profiles 语义
tags: [podman, compose, source-code, config, yaml, interpolation, merge]
generated: { by: "source-code-to-okf-wiki", at: "2026-09-10T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-09-10T00:00:00Z" }
status: stable
stale_after: "2027-09-10"
sources:
  - id: source-code
    resource: /references/source-code-map.md
    title: podman_compose.py 源码信源登记（v1.6.0 / commit e3df104）
---

# 配置加载管线：插值、归一化与深合并

`podman-compose up` 做的第一件事不是碰容器，而是把一组 YAML 文件加工成内存中规范的 service dict。这个加工管线集中在 `PodmanCompose._parse_compose_file()`（L2652-3056），由五个阶段串成：**文件发现 → 环境装配 → 逐文件加载（归一化 → 插值 → 合并）→ 全局后处理 → 服务展开**。

## 文件发现：14 个候选名与递归向上查找

compose 文件的定位按以下优先级：

1. `-f/--file` 显式指定（可多次；`-` 表示从 stdin 读取）；
2. 环境变量 `COMPOSE_FILE`（多个文件用 `COMPOSE_PATH_SEPARATOR` 分隔，Windows 上是分号）；
3. 项目 `.env` 中的 `COMPOSE_FILE`（.env 被提前加载以支持此项）；
4. 都没有时，`find_compose_files_recursively()`（L2392）从当前目录**逐级向上**查找（最多 10 层），命中任一候选文件即停止，并把工作目录切换到文件所在目录。

候选文件名常量 `COMPOSE_DEFAULT_LS`（L2374）共 14 个，覆盖三类命名：`compose.{yaml,yml}` 及其 override、`podman-compose.{yaml,yml}`、`docker-compose.{yml,yaml}` 及其 override、`container-compose.{yml,yaml}` 及其 override。

## 环境变量分层

管线中 `self.environ` 的合并顺序（后者覆盖前者）：

```text
.env 文件 dotenv 值  →  当前进程 os.environ  →  COMPOSE_PROJECT_DIR / COMPOSE_FILE / COMPOSE_PATH_SEPARATOR  →  命令行 -e
```

两个特殊处理：

- `.env` 中以 `PODMAN_` 开头的变量会被注入 `os.environ`（L2739），使后续 podman 子进程继承（例如代理设置）；
- `--env-file` 指定的文件相对当前工作目录解析，而默认 `.env` 取 compose 文件所在目录。

Profile 来自 `--profile` 与 `COMPOSE_PROFILES` 的并集；此外，命令行显式指定的目标服务，其自身声明的 profiles 会被自动启用（`_resolve_profiles`，L3058）。

## 插值引擎：bash 参数扩展的本地实现

Compose 文件中的 `$VAR` 替换**不依赖外部命令**，而是 `var_interpolate()`（L275）内一个完整的 tokenizer：

1. `tokenize()` 把字符串切成 `LiteralToken` 与 `VarToken` 两种记号；
2. `VarToken.resolve(env)` 按操作符求值。

支持 6 种 bash 风格操作符：

| 语法 | 语义 |
|------|------|
| `${VAR:-default}` | VAR 未设置**或为空**时用 default |
| `${VAR-default}` | VAR 未设置时用 default（空值不用） |
| `${VAR:?err}` | VAR 未设置或为空时**报错终止**，err 经插值后作为消息 |
| `${VAR?err}` | VAR 未设置时报错终止 |
| `${VAR:+alt}` | VAR 非空时展开为 alt，否则为空 |
| `${VAR+alt}` | VAR 已设置时展开为 alt |

转义与边界规则：`$$` 输出字面 `$`；`$` 后跟非变量名字符（如 `$5`）视为普通文本；花括号支持嵌套计数（`advance_to_closing_brace` 维护 brace 层级）；操作数自身会递归插值（默认值里可以再引用别的变量）。

递归应用由 `rec_subs()`（L473）完成：遍历 dict/list/str 全部字符串节点。一个关键特例：当 dict 含 `environment` 键时，服务自身的环境变量会被并入替换字典——因此**同一服务内环境变量可以互相引用**；短格式环境变量（值为 null，表示从宿主继承）在此处被解析为宿主实际值。

## 归一化：短语法到长语法

`normalize_service()`（L2078）在合并前逐文件执行，把 Compose Spec 允许的各种简写统一为内部规范形态：

- `build: ./dir` 字符串 → `build: {context: ./dir}`；`build.args` dict → `k=v` 列表；`additional_contexts` dict → `k=v` 列表；
- `env_file/security_opt/volumes` 的字符串形式 → 单元素列表；
- `environment/labels` → dict（`norm_as_dict`，同时接受 `["K=V", "K"]` 列表与 dict）；
- `extends: 服务名` 字符串 → `{service: 服务名}`；
- `depends_on` 的字符串/列表形式 → dict，并为每项补默认条件 `condition: service_started`；
- `secrets` 必须是列表（给成 dict 直接报错）；
- `seccomp:unconfined` / `apparmor:unconfined` 中的冒号改写为等号（podman 用 `=`）；
- 经 `include` 引入的文件，其 `volumes/env_file/build.context` 相对路径按被引文件所在子目录重写（`sub_dir` 参数）。

最后的 `normalize_final()`（L2201）把 build context 解析为相对项目目录的绝对路径（git URL 形式除外，由 `is_context_git_url` 判定，该函数还特别排除了 Windows 盘符路径被误判为 URL 的情况）。

## 深合并与 !override / !reset

多个 compose 文件（基础 + override + include）通过 `rec_merge_one()`（L2225）递归合并，语义是**带方言的深合并**：

- dict 按键递归合并；source 独有键直接并入；
- list 默认**追加**（不是替换）；
- 两类例外整体替换：`command` 与 `entrypoint` 永远以后值为准；
- `volumes` 列表追加前先按挂载目标（target）去重，避免同一挂载点出现两条；
- 合并双方类型不一致（如 dict 对 list）直接报错；
- 自定义 YAML 标签改变合并语义：
  - `!reset`（`ResetTag`，L1793）：该键在合并结果中删除——用于"清空基文件中的列表"；
  - `!override`（`OverrideTag`，L1764）：该值整体替换而不深合并/追加——用于"用我的列表完全取代基列表"。

两个标签通过 PyYAML 的 `YAMLObject` 机制注册到 SafeLoader/SafeDumper，因此 `config` 命令输出 YAML 时也能正确序列化。

> 实践要点：override 文件里修改 `ports/volumes/environment` 这类列表字段时，直接写值会与基础文件**追加合并**（常见的"端口翻倍"现象即源于此）；要整体替换必须显式使用 `!override`，要清空则用 `!reset`。

## extends 与 include

- **extends**（`resolve_extends`，L2329）：服务级继承。目标可以是同文件另一服务，也可以是外部文件中的服务（`extends.file`）；外部文件先插值再归一化，然后以 `rec_merge({}, 基服务, 当前服务)` 合并——当前服务覆盖基类。处理顺序按依赖数排序，保证基服务先就绪。
- **include**（L2853-2887）：顶层组合。`include` 接受字符串列表或 `{path: ...}` 字典（path 可为列表），路径相对**发起 include 的文件**解析；被引文件追加到文件迭代队列中处理，处理完即从合并对象删除 `include` 键以防循环重复引入。

## 项目命名与 x-podman 兼容开关

- **项目名**优先级：`-p` → `COMPOSE_PROJECT_NAME` → 顶层 `name:` → 项目目录名小写；再用正则 `[^-_a-z0-9]` 剔除非法字符。
- **资源命名**：容器默认名 `<项目>_<服务>_<序号>`（`format_name`），第一个副本可用 `container_name`；卷 `<项目>_<卷名>`；网络默认名同理。分隔符默认下划线，开启兼容模式后用连字符。
- **x-podman 设置**（`_parse_x_podman_settings`，L2604）识别 6 个键：`docker_compose_compat`、`default_net_name_compat`、`default_net_behavior_compat`、`name_separator_compat`、`in_pod`、`pod_args`；来源为 YAML 的 `x-podman:` 段与 `PODMAN_COMPOSE_<键>` 环境变量。设置 `docker_compose_compat: true` 会连锁开启「默认网络行为兼容 Docker、连字符命名、默认不使用 pod」三项，未识别的键只告警不报错。

服务展开为容器时（L2978-3045），副本数（replicas）来源优先级为 `--scale` > 服务级 `scale` > `deploy.replicas`（且 `deploy.mode: replicated`）；未声明 image 的服务默认镜像名取 `<项目>_<服务>`。展开后的容器列表按依赖数量排序，形成天然的拓扑启动顺序。整个合并配置还会计算 `yaml_hash`（紧凑 JSON 的 sha256），每个服务计算 `config_hash`，供生命周期命令做变更检测。

## 相关概念

- [CLI 翻译层与标签状态](05-cli-translation-layer.md)：归一化产物如何被翻译成 argv
- [Compose 文件常见模式](03-compose-patterns.md)：用户视角的配置写法
- [依赖图与 up/down 生命周期](07-dependency-lifecycle.md)：depends_on 归一化后的图结构如何被消费
- [快速上手与 Compose Spec 兼容](00-introduction.md)：命令行参数与环境变量入口
- [源码信源登记](../references/source-code-map.md)：行号与符号索引
