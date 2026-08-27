---
type: concept
title: 错误处理与 VFile 消息系统
description: MySTmd 使用 VFile 作为错误/警告/信息的收集容器，通过 fileError/fileWarn/fileInfo 上报问题，每个消息关联 RuleId 用于分类和严重级别覆盖。
tags: [mystmd, error-handling, vfile, ruleid, diagnostics]
generated: 2026-08-23
verified: true
status: stable
stale_after: 2027-12-31
sources:
  - path: "/references/myst-common-source.md"
    facts: [F-073, F-074]
  - path: "/references/myst-parser-source.md"
    facts: [F-005, F-018]
  - path: "/references/simple-validators-source.md"
    facts: [F-106, F-107, F-108]
---

## VFile 消息机制

MySTmd 使用 [VFile](https://github.com/vfile/vfile)（虚拟文件）作为文档处理过程中的消息收集容器。每个文档对应一个 VFile 实例，所有解析、转换、验证过程中的错误和警告都通过 VFile 的 messages 数组收集。

### VFile 核心结构

```ts
interface VFile {
  path: string;           // 文件路径
  value: string;          // 文件内容
  messages: VFileMessage[];  // 消息列表
  data: Record<string, any>;  // 附加数据
  result?: any;           // 处理结果
}
```

### VFileMessage

```ts
interface VFileMessage extends Error {
  source: string;         // 消息来源（如 'myst-parser'、'myst-transforms'）
  ruleId?: string;        // 规则 ID（对应 RuleId 枚举）
  fatal: boolean | null;  // true=error, false=warning, null=info
  line?: number;          // 行号
  column?: number;        // 列号
  position?: Position;    // 完整位置信息
  actual?: string;        // 实际值
  expected?: string[];    // 期望值
  url?: string;           // 帮助文档 URL
  note?: string;          // 附加说明
}
```

## 消息上报函数

myst-common 提供三个核心上报函数：

```ts
fileError(
  vfile: VFile,
  message: string,
  node: GenericNode,
  source: string,
  ruleId: RuleId,
  opts?: { note?: string; url?: string; fatal?: boolean }
): VFileMessage

fileWarn(vfile, message, node, source, ruleId, opts?): VFileMessage
fileInfo(vfile, message, node, source, ruleId, opts?): VFileMessage
```

### 参数说明

| 参数 | 说明 |
|------|------|
| `vfile` | 目标 VFile 实例 |
| `message` | 人类可读的错误消息 |
| `node` | 触发错误的 AST 节点（用于提取 position） |
| `source` | 错误来源包名（如 'myst:directive'、'myst-transforms:links'） |
| `ruleId` | RuleId 枚举值，用于分类和级别覆盖 |
| `opts.note` | 附加说明（如何修复） |
| `opts.url` | 帮助文档链接 |
| `opts.fatal` | 覆盖默认严重级别 |

### 使用示例

```ts
// 在 applyDirectives 中报告未知指令
if (!spec) {
  fileError(
    vfile,
    `Unknown directive: {${node.name}}`,
    node,
    'myst:directive',
    RuleId.unknownDirective,
    { note: `Available directives: ${Object.keys(directives).join(', ')}` }
  );
  return;
}
```

## RuleId 分类体系

RuleId 枚举包含 80+ 个规则 ID，覆盖文档处理的各个阶段：

### 解析阶段规则

| RuleId | 严重级别 | 说明 |
|--------|---------|------|
| `unknownDirective` | error | 使用了未注册的指令名 |
| `unknownRole` | error | 使用了未注册的角色名 |
| `unknownJumpable` | error | 未知的跳转目标 |
| `directiveArgs` | error | 指令参数格式错误 |
| `directiveOptions` | error | 指令选项格式错误 |
| `directiveBody` | error | 指令体格式错误 |
| `mystParseError` | error | 通用解析错误 |
| `mathMetadata` | warn | 数学公式元数据问题 |
| `mathLabel` | warn | 数学公式标签问题 |
| `mathAlignment` | warn | 数学公式对齐问题 |

### 引用与链接规则

| RuleId | 严重级别 | 说明 |
|--------|---------|------|
| `refNotFound` | error | 交叉引用目标不存在 |
| `citeNotFound` | error | 引用 key 在参考文献中找不到 |
| `xrefLoop` | error | 交叉引用形成循环 |
| `duplicateIdentifier` | error | 重复的 identifier |
| `linkNotFound` | warn | 内部链接目标不存在 |
| `externalLinkNotFound` | info | 外部链接不可访问 |
| `imageNotFound` | warn | 图片文件不存在 |
| `imageAltText` | info | 图片缺少 alt 文本 |

### 配置与 Frontmatter 规则

| RuleId | 严重级别 | 说明 |
|--------|---------|------|
| `projectConfig` | error | 项目配置错误 |
| `siteConfig` | error | 站点配置错误 |
| `frontmatter` | warn | Frontmatter 字段问题 |
| `invalidYaml` | error | YAML 解析错误 |

### 代码与执行规则

| RuleId | 严重级别 | 说明 |
|--------|---------|------|
| `codeMetadata` | warn | 代码块元数据问题 |
| `executable` | warn | 代码执行问题 |
| `kernel` | error | Jupyter 内核问题 |
| `notebookRun` | warn | Notebook 未运行 |

### 转换阶段规则

| RuleId | 严重级别 | 说明 |
|--------|---------|------|
| `missingTOC` | warn | 目录缺失 |
| `transformError` | error | Transform 执行错误 |
| `exportNotFound` | error | 导出目标不存在 |
| `exportNoFormat` | warn | 导出格式未指定 |

## ErrorRule 严重级别覆盖

用户可以通过 myst.yml 的 `project.error_rules` 配置覆盖默认严重级别：

```yaml
project:
  error_rules:
    - id: unknownDirective
      severity: ignore     # 忽略未知指令警告
    - id: imageAltText
      severity: error      # 将图片缺少alt升级为错误
    - id: externalLinkNotFound
      severity: ignore     # 忽略外部链接检查
```

ErrorRule 结构：
```ts
type ErrorRule = {
  id: string;                          // RuleId 值
  severity: 'ignore' | 'warn' | 'error';  // 覆盖后的级别
  key?: string;                        // 可选的键匹配
} & Record<string, any>;
```

严重级别语义：
- **error**：处理失败，构建中止
- **warn**：警告，构建继续但标记问题
- **info**：信息，仅日志记录
- **ignore**：完全抑制，不记录

## simple-validators 的消息收集

simple-validators 包使用相同的消息模式，但提供更通用的验证错误/警告机制：

```ts
type ValidationOptions = {
  property: string;                     // 当前验证的属性名
  messages?: { errors: ValidationMessage[]; warnings: ValidationMessage[] };
  suppressErrors?: boolean;
  suppressWarnings?: boolean;
  errorLogFn?: (msg: string) => void;
  warningLogFn?: (msg: string) => void;
  location?: string;                    // 位置路径
  source?: string;                      // 错误来源
  file?: string;                        // 文件路径
  // ...
};

validationError(message: string, opts: ValidationOptions): undefined;
validationWarning(message: string, opts: ValidationOptions): undefined;
```

与 fileError/fileWarn 的区别：
- simple-validators 的 validationError 返回 undefined（表示验证失败），而不是 VFileMessage
- 消息结构是 `{property, message}` 而非 VFileMessage
- 支持 suppressErrors/suppressWarnings 标志
- 支持 incrementOptions 嵌套路径追踪

## 消息流

```
mystParse(content, opts)
     │
     ├─ 创建 VFile（如果 opts.vfile 未提供）
     │
     ├─ 分词阶段（markdown-it）
     │   └─ 错误 → console.error（分词阶段无法关联 VFile）
     │
     ├─ MDAST 构建阶段（tokensToMyst）
     │   └─ 错误通过 state.addError() 或 fileError 上报
     │
     ├─ 指令处理（applyDirectives）
     │   └─ fileError(fileWarn) → vfile.messages
     │
     ├─ 角色处理（applyRoles）
     │   └─ fileError(fileWarn) → vfile.messages
     │
     └─ 返回 MDAST tree
              │
              ▼
basicTransformations(tree, vfile, opts)
     │
     ├─ 每个 transform 处理节点
     │   └─ fileError/fileWarn/fileInfo → vfile.messages
     │
     └─ 处理完成
              │
              ▼
项目级 transforms
     │
     └─ resolveReferences/buildToc 等
         └─ fileError/fileWarn → vfile.messages
              │
              ▼
构建输出
     └─ 检查 vfile.messages 中 fatal===true 的消息
         → 有则构建失败，展示错误摘要
         → 无则构建成功，展示警告/信息摘要
```

## 位置信息

错误消息自动从 AST 节点的 position 字段提取行号和列号。position 由解析器在 openNode 时设置：

```ts
position = {
  start: { line: number; column: number; offset: number },
  end: { line: number; column: number; offset: number },
};
```

MarkdownParseState 在 openPosition 时从 Token 的 map 属性计算位置。

## 相关概念

- [MyST 解析器](02-myst-parser.md)
- [MDAST 转换管线](03-myst-transforms.md)
- [公共类型系统](04-myst-common-types.md)
- [配置系统](10-configuration-system.md)
