# 信源参考（References）

| 文档 | 说明 |
|------|------|
| [source-code-map.md](source-code-map.md) | v0.9.2 源码结构地图：目录构成、命令文件归属、27 个 internal 包、四个服务客户端、配置目录解析顺序 |
| [exit-code-contract.md](exit-code-contract.md) | 退出码契约全表：0~8 语义边界、后端码映射、5 个失败类型常量、9 条命令行解析失败前缀、exit 6 三态表 |
| [flag-inventory.md](flag-inventory.md) | 旗标清单与统计口径：104 处注册调用的逐文件分布、72 个全局去重旗标名、`vk create` 23 个自有旗标、`cmd/video` 44 个旗标对 |
| [backend-endpoints.md](backend-endpoints.md) | 后端端点全表：39 个去重端点、HTTP 方法与用途、引擎↔端点对应、端点提取的统计口径 |
| [source-facts.md](source-facts.md) | 编号事实清单 F-001~F-104：每条带仓库内相对路径与行号，含四轮计数勘误的审计轨迹 |

```{toctree}
:hidden:
:maxdepth: 1

source-code-map
exit-code-contract
flag-inventory
backend-endpoints
source-facts
```
