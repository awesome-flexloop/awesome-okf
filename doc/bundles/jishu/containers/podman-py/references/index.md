# 信源登记簿

本目录登记 podman-py 知识包所有内容据以派生的源码信源。所有概念文档和示例文档的 `sources` 字段均指向此目录下的信源条目。信源基于 `external/dao/action/Containers/podman-py/` 源码核心文件。

* [README.md 项目概览与快速入门](readme-source.md) — `README.md`：项目基本信息、安装命令、运行时与可选依赖、基础使用示例、官方文档与源码仓库链接。
* [PodmanClient 核心客户端](client-source.md) — `podman/__init__.py`、`podman/client.py`、`podman/version.py`：模块导出、Docker 兼容性别名、PodmanClient 类定义、构造参数、from_env 环境变量配置、默认连接逻辑、9 个资源管理器属性、直接方法、不支持的 Swarm 操作。
* [HTTP 传输层实现](api-source.md) — `podman/api/` 目录：APIClient 继承 requests.Session、APIResponse 错误映射、6 种支持的 URL Scheme、UDSAdapter/SSHAdapter/HTTPAdapter 传输适配器选择、DEFAULT_CHUNK_SIZE=2MB、工具函数导出、异常体系。

```{toctree}
:hidden:
:maxdepth: 7

api-source
client-source
readme-source
```
