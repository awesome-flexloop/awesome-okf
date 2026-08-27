---
type: Concept
title: 指纹规则 DSL
description: AIG 使用自研声明式 DSL 描述 AI 组件指纹，支持 body/header/icon/hash 四种匹配源和 contains/exact/regex 三种匹配方式，通过 YAML 文件定义无需改代码即可扩展识别能力。
tags: [ai-infra-guard, fingerprint, dsl, yaml, parser, regex]
generated: { by: "reference_agent/trae-solo", at: "2026-08-23T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T00:00:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: scan-engine
    resource: /references/scan-engine.md
    title: 扫描引擎与指纹 DSL 信源
  - id: data-rules
    resource: /references/data-rules.md
    title: 数据文件与规则格式信源
---

## 概述

指纹 DSL（Domain-Specific Language）是 AIG 用于识别 AI 基础设施组件的声明式规则语言。规则以 YAML 文件存储在 `data/fingerprints/` 目录，程序启动时由 `parser.InitFingerPrintFromData` 编译为可执行的 AST（抽象语法树），扫描时对每个 HTTP 响应进行匹配求值。

当前内置 142 个指纹规则，覆盖 LLM 推理框架、AI 应用平台、向量数据库、工作流引擎等类别。

## YAML 结构

一个完整的指纹文件包含三部分：

```yaml
info:
  name: dify                    # 组件唯一标识名
  author: researcher            # 规则作者
  example:                      # 示例 URL
    - https://dify.example.com
  desc: Dify AI 应用开发平台    # 组件描述
  severity: high                # 严重级别
  metadata:
    category: ai-platform
  recommendation: 1             # 推荐级别
http:                           # HTTP 指纹匹配规则
  - method: GET
    path: /
    matchers:
      - 'body="dify"'
    extractor:
      part: body
      group: version
      regex: 'dify/v(\d+\.\d+\.\d+)'
version:                        # 版本探测规则（可选）
  - method: GET
    path: /api/version
    matchers:
      - 'body="version"'
```

### info 字段

| 字段 | 类型 | 说明 |
|------|------|------|
| name | string | 组件名称，与漏洞规则中的 name 对应 |
| author | string | 规则作者 |
| example | []string | 示例目标 URL |
| desc | string | 组件中文描述 |
| severity | string | 组件暴露的风险级别 |
| metadata | map | 自定义元数据 |
| recommendation | int | 推荐级别 |

### http/version 字段

每个规则项包含：
- `method` — HTTP 方法（GET/POST 等）
- `path` — 请求路径
- `matchers` — DSL 表达式字符串数组（AND 关系，全部匹配才算命中）
- `data` — 请求体（可选）
- `extractor` — 版本提取器（可选）
- `versionrange` — 版本范围约束（可选）

## DSL 语法

### 匹配源

| 关键字 | 含义 | 数据来源 |
|--------|------|---------|
| `body` | HTTP 响应体 | `resp.DataStr` |
| `header` | HTTP 响应头 | 所有 header 拼接为字符串 |
| `icon` | favicon 的 mmh3 hash | `utils.FaviconHash(iconData)` |
| `hash` | 响应体 hash | 自定义 hash |

### 操作符

| 操作符 | 含义 | 示例 |
|--------|------|------|
| `=` | 包含（contains） | `body="dify"` — body 包含 "dify" |
| `==` | 完全相等 | `header="200"` — header 完全等于 "200" |
| `!=` | 不包含 | `body!="error"` — body 不含 "error" |
| `~=` | 正则匹配 | `body~="dify/v\\d+"` — body 匹配正则 |

### 逻辑运算符

| 运算符 | 含义 |
|--------|------|
| `&&` | 逻辑与（短路求值） |
| `\|\|` | 逻辑或（短路求值） |

### 括号

使用 `(...)` 改变优先级：

```
(body="dify" || body="langgenius") && header="application/json"
```

### 字符串字面量

用双引号包裹，支持转义 `\"`：

```
body="Dify: \"AI\""
```

## 匹配规则约束

### hash 互斥规则

`hash` 类型的 matcher 不能与 `body`/`header`/`icon` matcher 在同一个规则中共存。这在 `compileMatchers` 中通过 `hashUsage()` 检查强制实施：

```go
hasHashMatcher := false
hasNonHashMatcher := false
// ... 遍历检查
if hasHashMatcher && hasNonHashMatcher {
    return fmt.Errorf("hash matcher cannot coexist with other matcher types")
}
```

### 大小写不敏感

`Eval` 方法在比较前将源字符串和目标字符串都转为小写：

```go
s1 = strings.ToLower(s1)
text := strings.ToLower(next.right)
```

因此 DSL 中的字符串匹配是大小写不敏感的。

### 正则预编译

使用 `~=` 的正则表达式在规则加载时编译一次（`regexp.Compile`），缓存到 `dslExp.cacheRegx`，避免每次扫描重复编译。

## 执行流程

### 编译阶段

1. YAML 反序列化为 `FingerPrint` 结构体
2. 对每个 HttpRule 的 Matchers 调用 `transfromRule`
3. `ParseTokens` 词法分析：将字符串拆分为 Token 序列
4. `CheckBalance` 检查括号匹配
5. `TransFormExp` 递归下降解析，构建 AST（dslExp/logicExp/bracketExp）
6. 编译后的 AST 存入 `HttpRule.dsl` 字段

### 匹配阶段

1. Runner 发送 HTTP 请求获取响应
2. 计算 favicon hash
3. 调用 `fpEngine.RunFpReqs(fullUrl, 10, faviconHash)` 遍历所有指纹
4. 对每个指纹的每条 HttpRule，用响应数据填充 `Config{Body, Header, Icon, Hash}`
5. 调用 `Rule.Eval(config)` 递归求值 AST
6. 所有 matcher 均匹配则指纹命中
7. 若配置了 extractor，用正则从响应中提取版本号

## AST 节点类型

```go
type dslExp struct {
    op        string         // =, ==, !=, ~=
    left      string         // body, header, icon, hash
    right     string         // 待匹配字符串或正则 pattern
    cacheRegx *regexp.Regexp // 预编译正则
}

type logicExp struct {
    op    string // &&, ||
    left  Exp
    right Exp
}

type bracketExp struct {
    inner Exp
}
```

求值采用递归下降：
- `dslExp` 节点直接执行字符串/正则比较
- `logicExp` 节点先求左值，根据短路规则决定是否求右值
- `bracketExp` 节点直接求内部表达式的值

## 版本提取

`Extractor` 结构支持从响应中提取版本号：

```go
type Extractor struct {
    Part  string `yaml:"part"`  // body/header
    Group string `yaml:"group"` // 捕获组名
    Regex string `yaml:"regex"` // 正则表达式
}
```

提取的版本号传递给漏洞引擎，用于 `AdvisoryEval` 版本比较。

## 编写自定义指纹

详见 [自定义指纹示例](../examples/custom-fingerprint.md)。基本步骤：
1. 在 `data/fingerprints/` 创建新的 .yaml 文件
2. 填写 info 基本信息
3. 编写 http matchers（建议至少 2 条独立特征以减少误报）
4. 可选配置 version 探测和 extractor
5. 重启服务或通过 API 热加载

## 相关概念

- [CVE 漏洞匹配](03-vuln-matching.md)
- [扫描引擎信源](../references/scan-engine.md)
- [数据文件格式](../references/data-rules.md)
- [自定义指纹示例](../examples/custom-fingerprint.md)
