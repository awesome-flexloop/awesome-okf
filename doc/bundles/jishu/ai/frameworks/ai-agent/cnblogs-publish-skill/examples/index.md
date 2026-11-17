# Examples 索引

本目录是可直接照做的操作示例，命令均使用占位值，不包含真实凭据。

## 示例清单

| 示例 | 场景 |
|---|---|
| [01 发布非公开草稿](/examples/01-publish-draft.md) | 默认安全路径；frontmatter、输出字段、验证与常见偏差 |
| [02 公开发布与首页推荐](/examples/02-publish-public-homepage.md) | `--publish`、首页分类、审核等待与误判对照 |
| [03 维护文章与图片](/examples/03-manage-posts-and-images.md) | list/get/update/delete/upload/render 与 update 风险 |

## 前置条件

- 已完成 [首次配置](/concepts/03-credentials-setup.md)。
- 文章为 UTF-8 Markdown，可带 frontmatter。
- 命令在 skill 根目录执行；Windows 用 `python` 或 `py -3`。

```{toctree}
:hidden:
:maxdepth: 2

01-publish-draft
02-publish-public-homepage
03-manage-posts-and-images
```
