# References - olot 信源索引

本目录包含 olot 项目文档的所有信源登记文件，所有 concepts 和 examples 文档中的事实均可追溯到此处的信源。

## 信源文件列表

| 文件 | 信源类型 | 说明 |
|------|---------|------|
| [readme-source.md](readme-source.md) | 官方文档 | 项目 README，包含项目介绍、CLI 和 Python API 使用示例 |
| [oci-source.md](oci-source.md) | 源码 | OCI 层操作核心逻辑、层注解常量、MediaType 定义 |
| [backend-source.md](backend-source.md) | 源码 | 三种后端（skopeo/oras-py/oras-cp）实现与函数签名 |

## 信源使用说明

- 每个 concepts/examples 文档的 frontmatter 中 `sources` 字段指向此处的文件
- 信源文件仅记录可验证的事实，不包含推断性内容
- 文档内容与信源不一致时，以信源为准
