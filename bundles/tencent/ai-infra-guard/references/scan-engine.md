---
type: Reference
title: 扫描引擎与指纹 DSL 信源
description: 记录 common/runner 和 common/fingerprints/parser 中 Runner、指纹解析器、AST 求值器的结构体与方法。
tags: [ai-infra-guard, go, scanner, fingerprint, dsl, parser]
generated: { by: "reference_agent/trae-solo", at: "2026-08-23T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T00:00:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: src-scan-engine
    resource: /references/scan-engine.md
    title: 扫描引擎与指纹 DSL 信源
---

## 源码路径

- `common/runner/runner.go`
- `common/runner/types.go`
- `common/runner/ai.go`
- `common/runner/result.go`
- `common/runner/ipnet.go`
- `common/fingerprints/parser/parser.go`
- `common/fingerprints/parser/token.go`
- `common/fingerprints/parser/synax.go`
- `common/fingerprints/parser/stack.go`
- `common/fingerprints/parser/tokenstrem.go`
- `common/fingerprints/preload/preload.go`
- `common/fingerprints/preload/version_range.go`

## Runner 结构

```go
type Runner struct {
    Options     *options.Options
    hp          *httpx.HTTPX
    hm          *hybrid.HybridMap
    rateLimiter ratelimit.Limiter
    result      chan HttpResult
    fpEngine    *preload.Runner
    advEngine   *vulstruct.AdvisoryEngine
    total       int
    done        chan struct{}
    callback    func(interface{})
}
```

### 初始化流程

`New(options2 *options.Options) (*Runner, error)` 依次调用：

1. `initStorage()` — 创建 `hybrid.DefaultDiskOptions` 混合存储
2. `processTargets()` — 处理 `--target`、`--file`、`--localscan`，支持 CIDR 展开
3. `initComponents()` — ratelimit、fastdialer、httpx 客户端
4. `initFingerprints()` — 加载 YAML 指纹，调用 `parser.InitFingerPrintFromData`
5. `initVulnerabilityDB()` — 加载漏洞库，中文 `data/vuln/` 或英文 `data/vuln_en/`

### 扫描流程

`RunEnumeration()`：
1. 启动 `handleOutput` goroutine 消费结果通道
2. 使用 `sizedwaitgroup.New(rateLimit)` 控制并发
3. 遍历 hybrid map 中所有目标
4. 无 http 前缀 → `runHostRequest`（http 失败重试 https）
5. 有 http 前缀 → `runDomainRequest`
6. `extractContent` 提取状态码、标题、favicon hash、指纹、漏洞

### 安全评分

```go
func (r *Runner) CalcSecScore(advisories []vulstruct.Info) CallbackReportInfo
```

扣分规则：
- high/critical/高危/严重：每个 -70
- medium/中危：每个 -30
- low/其他：每个 -10
- 基础分 100，最低 0

### 回调类型

```go
type CallbackScanResult struct {
    TargetURL       string
    StatusCode      int
    Title           string
    Fingerprint     string
    Vulnerabilities []vulstruct.Info
    Resp            string
    ScreenShot      string
    Reason          string
    Summary         string
}

type CallbackProcessInfo struct {
    Current int
    Total   int
}

type CallbackReportInfo struct {
    SecScore   int
    HighRisk   int
    MediumRisk int
    LowRisk    int
}
```

## 指纹数据结构

```go
type FingerPrint struct {
    Info    FingerPrintInfo `yaml:"info"`
    Http    []HttpRule      `yaml:"http"`
    Version []HttpRule      `yaml:"version,omitempty"`
}

type FingerPrintInfo struct {
    Name           string            `yaml:"name"`
    Author         string            `yaml:"author"`
    Example        []string          `yaml:"example,omitempty"`
    Desc           string            `yaml:"desc,omitempty"`
    Severity       string            `yaml:"severity"`
    Metadata       map[string]string `yaml:"metadata"`
    Recommendation int               `yaml:"recommendation,omitempty"`
}

type HttpRule struct {
    Method       string    `yaml:"method"`
    Path         string    `yaml:"path"`
    Matchers     []string  `yaml:"matchers"`
    Data         string    `yaml:"data,omitempty"`
    dsl          []*Rule   `yaml:"-"`
    VersionRange string    `yaml:"versionrange,omitempty"`
    Extractor    Extractor `yaml:"extractor,omitempty"`
}

type Config struct {
    Body   string
    Header string
    Icon   int32
    Hash   string
}
```

## DSL Token 类型

```go
const (
    tokenBody   = "body"
    tokenHeader = "header"
    tokenIcon   = "icon"
    tokenHash   = "hash"
    tokenText   = "text"

    tokenContains   = "="
    tokenFullEqual  = "=="
    tokenNotEqual   = "!="
    tokenRegexEqual = "~="

    tokenAnd = "&&"
    tokenOr  = "||"

    tokenLeftBracket  = "("
    tokenRightBracket = ")"
)

const (
    tokenVersion    = "version"
    tokenIsInternal = "is_internal"
    tokenGt         = ">"
    tokenGte        = ">="
    tokenLt         = "<"
    tokenLte        = "<="
)
```

## AST 节点与求值

```go
type Exp interface {
    Name() string
}

type Rule struct {
    root Exp
}

type dslExp struct {
    op        string
    left      string
    right     string
    cacheRegx *regexp.Regexp
}

type logicExp struct {
    op    string
    left  Exp
    right Exp
}

type bracketExp struct {
    inner Exp
}
```

关键函数：
- `ParseTokens(s string) ([]Token, error)` — 指纹表达式词法分析
- `ParseAdvisorTokens(s string) ([]Token, error)` — 漏洞版本表达式词法分析
- `CheckBalance(tokens []Token) error` — 括号匹配检查
- `TransFormExp(tokens []Token) (*Rule, error)` — 构建 AST
- `(*Rule).Eval(config *Config) bool` — 指纹匹配求值
- `(*Rule).AdvisoryEval(config *AdvisoryConfig) bool` — 版本漏洞求值
- `(*Rule).hashUsage() (usesHash bool, hashOnly bool)` — hash 互斥检查
- `InitFingerPrintFromData(data []byte) (*FingerPrint, error)` — 从 YAML 初始化指纹

### Eval 操作符语义

| 操作符 | 语义 |
|--------|------|
| `=` | strings.Contains |
| `==` | 完全相等 |
| `!=` | 不包含 |
| `~=` | 正则匹配 |
| `&&` | 逻辑与（短路） |
| `\|\|` | 逻辑或（短路） |

### AdvisoryEval 版本比较

使用 `github.com/hashicorp/go-version` 库：
- `version > "1.2.3"` — GreaterThan
- `version >= "1.2.3"` — GreaterThanOrEqual
- `version < "1.2.3"` — LessThan
- `version <= "1.2.3"` — LessThanOrEqual
- `version == "1.2.3"` — Equal
- `is_internal` — 布尔值匹配

`versionCheck` 函数：去除 `v` 前缀，字母替换为 `.0`，`"latest"` → `"999"`。

## AI 分析

```go
func ScreenShot(url string) ([]byte, error)
func Analysis(url string, resp string, language string, model *models.OpenAI) ([]byte, *vulstruct.Info, string, error)
func LoadSensitivePrompt(language string) string
func LoadWebPageScreenShotSummary(language string) string
```

`Analysis` 流程：截图 → 多模态 LLM 描述截图 → 注入敏感信息分析 prompt → 流式返回结果 → 提取 `<title>/<details>/<severity>/<summary>` 标签。

## 相关概念

- [指纹规则 DSL](/concepts/02-fingerprint-dsl.md)
- [CVE 漏洞匹配](/concepts/03-vuln-matching.md)
- [分布式架构总览](/concepts/00-architecture.md)
