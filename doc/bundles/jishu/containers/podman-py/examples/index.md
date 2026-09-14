# 使用示例

本目录提供 podman-py 的实战示例代码，覆盖 docker-py → podman-py 脚本级灰度迁移、三服务（Quadlet PG+Redis+Nginx）15步编排生命周期、CI 集成测试治理（skipif/pnext/覆盖率双轨/DCO）、多容器 Pod 网络拓扑（自定义子网/Secret/Volume/事件流监听）四大真实场景。**示例 4 篇**，每篇脚本均可复制到项目中作为脚手架启动。

* [01 - 从 docker-py 迁移到 podman-py 脚本级灰度](01-migration.md) — 迁移前 3 条检查清单、3 行别名导入（DockerClient/异常/模块三别名）、from_env 零改迁移、10 项高频 API 兼容对比表、base_url socket 路径 Rootless/Rootful 差异代码、sparse 默认陷阱两种修复方案、5 个高概率踩坑点总结、Nginx 部署迁移前后 40 行完整代码对比、CI 集成 3 步验证脚本（bash + assert）。
* [02 - 三服务编排生命周期（Quadlet + Postgres + Redis + Nginx）](02-container-ops.md) — 前置断言函数 3 条（socket/版本≥5.8/enable-linger）、端到端 15 步流水线：(1) info (2) 清理旧资源 (3) pull三张镜像(policy=newer, progress_bar 降级) (4) quadlets.install 内存 tuple (5) wait pg 健康 30×2s (6) report+get_contents 校验 (7) create redis (8) create nginx (9) start 依赖顺序 (10) exec_run 健康探测 (11) logs tail (12) label=prod dry-run (13) 优雅 stop 反顺序 (14) remove v=True (15) prune label=demo；8 类异常分层捕获模板；5 条常见报错速查。
* [03 - 集成测试治理：skipif/pnext/覆盖率双轨/DCO/pylint 不默认](03-testing-governance.md) — tox.ini 环境矩阵（py39-313-unit + py312-313-integration + coverage 80% + lint）、unit test requests-mock 纯 mock HTTP 结构三示例、integration real_client 2 条前置断言（PODMAN_BINARY+ssh localhost exit）、@pytest.mark.skipif 三元组（PODMAN_VERSION/OS_RELEASE Fedora42+/RootfulRootless）、@pytest.mark.pnext 前瞻用例、覆盖率双轨 mermaid 流程图 + core 模块 85% 自测脚本、pylint 2 种主动调用时机（Reviewer 要求/大重构前基准）、DCO Signed-off-by + make validate git-validation 安装、CI 门外守门 G1-G3 防线表。
* [04 - 多容器 Pod 网络拓扑（自定义子网 + Secret + Volume + 事件流）](04-pod-network-topology.md) — IPAMConfig/IPAMPool 创建 10.89.0.0/24 bridge 网络（IPRange→lease_range 换算）、Secret 裸字节上送与 dict 形态 target/mode、命名卷 volumes={name:{bind,mode}} 挂载、Pod 内容器组（app+sidecar 共享 localhost）+networks={name:{}}端点配置、后台线程消费 /events NDJSON 流（since/filters/decode）、pods.stats 流式 decode、finally 逆序幂等清理（Pod→Secret→Volume→Network）、API-端点-源码出处对照表、排障清单。

```{toctree}
:hidden:
:maxdepth: 7

01-migration
02-container-ops
03-testing-governance
04-pod-network-topology
```
