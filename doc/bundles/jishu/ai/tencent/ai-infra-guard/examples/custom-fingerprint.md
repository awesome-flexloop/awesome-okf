---
type: Example
title: 自定义指纹规则
description: 通过编写 YAML 指纹文件扩展 AIG 的组件识别能力，包含 info 元信息、http 匹配规则、version 版本探测和 extractor 正则提取的完整示例。
tags: [ai-infra-guard, fingerprint, custom, yaml, dsl, example]
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

## 指纹文件结构

自定义指纹是一个 YAML 文件，放在 `data/fingerprints/` 目录下（或通过 `--fps` 指定的自定义目录）。基本结构：

```yaml
info:
  name: my-app
  author: your-name
  desc: 我的自定义应用
  severity: high
  example:
    - https://my-app.example.com
http:
  - method: GET
    path: /
    matchers:
      - 'body="my-app"'
```

## 完整示例

以下是一个虚构的 AI 平台 "MyAIPlatform" 的指纹规则：

```yaml
info:
  name: myaiplatform
  author: security-team
  example:
    - https://ai.internal.company.com
  desc: MyAIPlatform 企业级 AI 推理平台
  severity: high
  metadata:
    vendor: MyCompany
    category: ai-platform
  recommendation: 1

http:
  - method: GET
    path: /
    matchers:
      - 'body="MyAIPlatform"'
      - 'header="x-powered-by: myai"'

  - method: GET
    path: /api/health
    matchers:
      - 'body="\\"service\\":\\"myai-inference\\""'

version:
  - method: GET
    path: /api/version
    matchers:
      - 'body="version"'
    extractor:
      part: body
      group: version
      regex: '"version"\s*:\s*"v?(\d+\.\d+\.\d+)"'
```

## 字段说明

### info 段

| 字段 | 必填 | 说明 |
|------|------|------|
| `name` | 是 | 组件唯一标识，必须与漏洞文件中的 `info.name` 对应 |
| `author` | 否 | 规则作者 |
| `desc` | 否 | 组件描述 |
| `severity` | 否 | 组件暴露风险级别（high/medium/low） |
| `example` | 否 | 示例 URL 列表 |
| `metadata` | 否 | 自定义键值对 |
| `recommendation` | 否 | 推荐级别（整数） |

### http 段

定义用于识别组件的 HTTP 请求和匹配规则。每个规则项包含：

- `method` — HTTP 方法（通常为 GET）
- `path` — 请求路径
- `matchers` — DSL 表达式数组（所有 matcher 必须同时匹配）
- `data` — 请求体（POST 请求时使用）

### version 段

可选，定义版本探测规则。结构与 http 相同，但通常配合 `extractor` 使用。

### extractor

从响应中提取版本号：

| 字段 | 说明 |
|------|------|
| `part` | 提取来源：`body` 或 `header` |
| `group` | 捕获组名称（通常为 `version`） |
| `regex` | 正则表达式，必须包含一个捕获组 |

## DSL 匹配器写法

### 简单包含匹配

```yaml
matchers:
  - 'body="dify"'
```

body 中包含字符串 "dify" 即匹配（大小写不敏感）。

### 多条件 AND

```yaml
matchers:
  - 'body="dify"'
  - 'header="application/json"'
```

matcher 数组内多个条件默认 AND 关系，必须全部匹配。

### OR 逻辑

```yaml
matchers:
  - 'body="dify" || body="langgenius/dify"'
```

在单个表达式中使用 `||`。

### 括号分组

```yaml
matchers:
  - '(body="vllm" || header="x-vllm") && body="api"'
```

### 正则匹配

```yaml
matchers:
  - 'body~="vllm/v\\d+\\.\\d+"'
```

使用 `~=` 操作符进行正则匹配。正则在规则加载时预编译。

### 不包含

```yaml
matchers:
  - 'body!="error"'
  - 'header!="x-frame-options: deny"'
```

### 完全匹配

```yaml
matchers:
  - 'icon=123456789'
```

`==` 表示完全相等（注意 `=` 是 contains，`==` 是 exact match）。

### Header 匹配

```yaml
matchers:
  - 'header="server: gunicorn"'
  - 'header="set-cookie: myai_session"'
```

所有响应 header 被拼接为一个字符串后进行匹配。

### Favicon hash 匹配

```yaml
matchers:
  - 'icon=-123456789'
```

favicon 的 mmh3 hash 值。注意：`icon` 和 `hash` matcher 不能与其他类型 matcher 共存于同一条规则中。

## 编写技巧

### 减少误报

建议使用至少 2 个独立特征：

```yaml
http:
  - method: GET
    path: /
    matchers:
      - 'body="unique-product-name"'
      - 'header="x-custom-header: specific-value"'
```

避免使用过于通用的字符串（如 "login"、"dashboard"）作为唯一匹配条件。

### 版本提取

版本号正则应尽可能精确：

```yaml
extractor:
  part: body
  group: version
  regex: 'app[/-]v?(\d+\.\d+\.\d+)'
```

提取的版本号会传递给漏洞引擎进行版本区间匹配。

### 测试规则

使用 CLI 测试：

```bash
ai-infra-guard scan -t https://target.com --fps ./my-fingerprint.yaml
```

确认指纹被正确识别并出现在输出表格中。

也可以使用 `--check-vul` 验证规则语法：

```bash
ai-infra-guard scan --check-vul --fps ./my-fingerprint.yaml
```

## 添加关联漏洞

创建指纹后，可以在漏洞库中添加对应的 CVE 规则。在 `data/vuln/<component-name>/` 下创建 YAML：

```yaml
info:
  name: myaiplatform
  cve: CVE-2025-XXXXX
  summary: MyAIPlatform 未授权 API 访问
  details: |
    MyAIPlatform 1.2.0 之前版本的 /api/admin 接口
    未进行身份验证，攻击者可获取模型配置。
  cvss: "8.6"
  severity: HIGH
  security_advise: 升级到 1.2.0 或更高版本
  references:
    - https://example.com/advisory
rule: version < "1.2.0"
references:
  - https://example.com/advisory
```

`info.name` 必须与指纹文件的 `info.name` 完全一致。

## 相关概念

- [指纹规则 DSL](../concepts/02-fingerprint-dsl.md)
- [CVE 漏洞匹配](../concepts/03-vuln-matching.md)
- [CLI 扫描示例](cli-scan.md)
- [数据文件格式](../references/data-rules.md)
