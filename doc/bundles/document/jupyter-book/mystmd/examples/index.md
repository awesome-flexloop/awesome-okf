# Examples

| 编号 | 示例 | 说明 | 相关概念 |
|------|------|------|---------|
| 00 | [使用 mystParse 解析 MyST Markdown](00-basic-parsing.md) | 基本解析、VFile 错误收集、自定义指令/角色注册、AST 遍历查询 | [MyST 解析器](/concepts/02-myst-parser.md) |
| 02 | [编写自定义 Transform 插件](02-custom-transform.md) | 函数式/Plugin 式 Transform、AST 遍历修改、MystPlugin 打包 | [MDAST 转换管线](/concepts/03-myst-transforms.md) |
| 03 | [参考文献引用处理](03-citations-example.md) | BibTeX 解析、引用渲染器、内联引用格式化、HTML 清理 | [参考文献处理](/concepts/12-citation-js-utils.md) |
| 04 | [编写自定义 Role](04-custom-role.md) | RoleSpec 定义、body/options 类型、验证逻辑、HTML 渲染属性 | [指令与角色系统](/concepts/06-directives-and-roles.md) |
| 05 | [编写自定义 Directive](05-custom-directive.md) | DirectiveSpec 定义、arg/options/body、ctx.parseMyst 递归解析、alias、MystPlugin 打包 | [指令与角色系统](/concepts/06-directives-and-roles.md) |

## 难度递进

```
入门级
 ├── 00-basic-parsing — 理解解析流程和 AST 结构
 │
进阶级
 ├── 04-custom-role — 行内扩展
 ├── 03-citations-example — 引用工具使用
 │
高级
 ├── 05-custom-directive — 块级扩展 + 递归解析
 └── 02-custom-transform — AST 后处理
```

```{toctree}
:hidden:
:maxdepth: 7

00-basic-parsing
02-custom-transform
03-citations-example
04-custom-role
05-custom-directive
```
