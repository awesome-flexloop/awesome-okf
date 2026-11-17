# References 索引

本目录登记本束的信源与外部约定，作为概念文档的溯源依据。

## 信源文件

| 文件 | 内容 |
|---|---|
| [source-code.md](/references/source-code.md) | 仓库/commit 固定、12 文件清单与 SHA256、模块结构、测试基线 |
| [api-and-conventions.md](/references/api-and-conventions.md) | MetaWeblog 端点、9 个方法、Post/FileData、博客园四个约定、审核与 OpenAPI 边界 |
| [security-design.md](/references/security-design.md) | 四种凭据后端、配置边界、输入/输出控制、威胁对照、平台注意事项 |

## 信任级别

| 级别 | 含义 | 本束使用 |
|---|---|---|
| high | 直接来自源码或仓库自带参考文档 | 全部 |

本束没有 medium/low 信源；未使用外部二手资料。

```{toctree}
:hidden:
:maxdepth: 2

api-and-conventions
security-design
source-code
```
