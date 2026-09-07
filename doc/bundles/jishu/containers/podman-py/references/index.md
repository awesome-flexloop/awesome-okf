# 信源登记簿

本目录登记 podman-py 知识包 v2.0 所有内容据以派生的源码+AGENTS信源。所有 12 篇内容文档（6 概念+3 示例+3 信源登记）的 frontmatter `sources` 字段均锚定本目录的条目。本目录合计 3 篇，覆盖 20+20+30=**70 条编号锚点 + 1 调用链图**，保证"每一个技术结论 → 一条可 grep 的源码锚点 → 一段可读原文"一一对应，可对抗审查（V 阶段）。

* [README.md + AGENTS.md 合成 20 锚点](readme-source.md) — README 4 组事实（RM-1 PyPI 名 podman / RM-2 4 extras / RM-3 Python 3.9+ / RM-4 7 行基础示例）+ AGENTS 18 条（Persona+Mental 3条 / Build-Test-Quality AG4~AG11 8项 / Quick start SSH 预断言 AG12 / 质量双轨+pylint+DCO+tox recreate AG13~AG16 / R1~R7 七陷阱 AG17 / 文档优先级 AG18）。
* [PodmanClient + APIClient 20 锚点](client-source.md) — PodmanClient 薄门面 13 条（CL-1 组合不是继承 / CL-2 DockerClient 别名 / CL-3 四级连接优先级伪代码 / CL-4 from_env 6双前缀表 / CL-5 9管理器字母序 / CL-6 7直方法 / CL-7~CL-10 Swarm 4 NotImplementedError / CL-11 version 返回字段 / CL-12 containers.conf 读取路径 / CL-13 close 语义）+ APIClient 传输层 7 条（API-1 继承 requests.Session / API-2 6 scheme 路由表 / API-3 404→NotFound/ImageNotFound 精确映射 / API-4 chunk 2MB / API-5 双前缀端点 / API-6 连接池 / API-7 timeout 两级语义）。
* [Manager + Mixin + 异常 + SSH + Quadlets 30+ 锚点 + 1 调用链图](api-source.md) — 8 大模块编号：Manager 基类 M-1~M-7（7条）+ Mixin 横切 MX-1~MX-3 + MRO 左端顺序 / RunMixin.run R-1~R-4 4 返回分支伪代码 / ImagesManager Rich I-1~I-6（优雅降级+progress_bar强制compat+policy 4选1+platform token+BuildError增量消费）/ Quadlet Q-1~Q-11（6属性+3方法+install A/B/C三形态）/ 8 类异常继承链 E-1~E-8 图 / SSHSocket S-1~S-8（本地mktemp+ssh命令拼接+StrictHostKeyChecking生产注意+身份文件权限+DEVNULL+100ms轮询+close SIGTERM→SIGKILL+SSH前置预断言）/ PodmanConfig.is_machine PM-1~PM-3 / images.pull(progress_bar=True) 端到端 7 步骤调用链 ASCII 图。

```{toctree}
:hidden:
:maxdepth: 7

readme-source
client-source
api-source
```
