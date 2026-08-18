# 文档元数据二分法规范

awesome-okf-xs 文档库采用 **YAML/TOML 内容-元数据二分法** 管理文档：
- **Markdown 文件**：只存放正文内容和极简 YAML frontmatter
- **TOML 文件**：存放所有结构化元数据，位于 `.meta/toml/` 镜像路径

> 本规范继承自 xuanspace 的文档元数据规范。当前 `.meta/toml/` 镜像目录尚未建立，后续任务统一处理。

## 1. YAML frontmatter 规范

Markdown 文件顶部的 YAML frontmatter 仅允许以下 4 个字段：

```yaml
---
id: "unique-document-id"
x-toml-ref: "path/to/metadata.toml"
source: "original-source-if-applicable"
version: "1.0.0"
---
```

### 允许字段说明

| 字段 | 必填 | 说明 |
|---|---|---|
| `id` | 是 | 文档唯一标识符，建议使用 kebab-case |
| `x-toml-ref` | 否（当前阶段） | 对应 TOML 元数据文件的相对路径（相对于 .meta/toml/） |
| `source` | 否 | 原始来源（如派生于 xuanspace 或其他项目） |
| `version` | 否 | 文档版本号，遵循 semver |

### 禁止字段列表

YAML frontmatter 中**禁止**出现以下字段（这些应放在 TOML 元数据中）：
- ❌ `title`（标题应作为 Markdown 正文的 H1）
- ❌ `description`、`summary`
- ❌ `tags`、`categories`、`keywords`
- ❌ `author`、`created_at`、`updated_at`
- ❌ `status`、`draft`

## 2. TOML 元数据规范

扩展元数据存放于 `.meta/toml/` 目录下，路径与原 Markdown 文件镜像对应（扩展名 `.md` → `.toml`，根目录文件直接放在 `.meta/toml/` 下）。

TOML 结构与 xuanspace 一致，包含 title、description、tags、categories、status、author、timestamps、extra 等字段。

## 3. 使用原则

1. **内容与元数据分离**：Markdown 专注于写作，TOML 专注于结构化数据
2. **极简 frontmatter**：YAML 部分只保留连接信息，不重复内容
3. **单一数据源**：每个元数据字段只在 TOML 中出现一次
4. **派生产物溯源**：源自外部的知识文档必须在 frontmatter 标注 `source` 字段