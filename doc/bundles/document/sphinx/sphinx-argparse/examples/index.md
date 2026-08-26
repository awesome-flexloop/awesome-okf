# 示例文档

按使用场景组织的完整可运行示例。

| 示例 | 场景 | 关键特性 |
|------|------|----------|
| [基础用法完整示例](basic-usage.md) | 简单项目单页文档化 | module+func指定、基本指令用法、前言内容 |
| [多页面子命令文档化](subcommand-docs.md) | 复杂CLI多页面拆分 | :path:导航、:nosubcommands:、:command:交叉引用、toctree组织 |
| [嵌套内容增强完整示例](content-enhancement.md) | 丰富自动生成的文档 | @before/@after/@replace/@skip四种注入、代码块、警告、交叉引用 |
| [Markdown 集成示例](markdown-integration.md) | Markdown格式帮助文本 | :markdown:/:markdownhelp:、CommonMark语法、代码块高亮、限制说明 |
| [Man Page 与命令索引完整示例](manpage-and-index.md) | 生成man page和命令索引 | :manpage:、man_pages配置、简单索引/分组索引、交叉引用 |

## 示例使用建议

- **首次使用**：从"基础用法完整示例"开始，了解最小配置
- **多子命令项目**：参考"多页面子命令文档化"的组织方案
- **文档质量提升**：使用"嵌套内容增强"为自动生成文档添加示例和注意事项
- **偏好Markdown**：参考"Markdown集成示例"配置Markdown支持
- **需要man page**：参考"Man Page与命令索引"配置man page输出和命令索引

```{toctree}
:hidden:
:maxdepth: 7

basic-usage
content-enhancement
manpage-and-index
markdown-integration
subcommand-docs
```
