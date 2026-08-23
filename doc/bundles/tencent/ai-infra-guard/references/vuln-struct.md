---
type: Reference
title: 漏洞结构与 AdvisoryEngine 信源
description: 记录 pkg/vulstruct 中 Info、VersionVul、AdvisoryEngine 的字段和方法签名。
tags: [ai-infra-guard, go, vulnerability, cve, advisory]
generated: { by: "reference_agent/trae-solo", at: "2026-08-23T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T00:00:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: src-vuln-struct
    resource: /references/vuln-struct.md
    title: 漏洞结构与 AdvisoryEngine 信源
---

## 源码路径

- `pkg/vulstruct/advisory.go`
- `pkg/vulstruct/scanner.go`

## Info 结构

```go
type Info struct {
    FingerPrintName string   `yaml:"name" json:"name"`
    CVEName         string   `yaml:"cve" json:"cve"`
    Summary         string   `yaml:"summary" json:"summary"`
    Details         string   `yaml:"details" json:"details"`
    CVSS            string   `yaml:"cvss" json:"cvss"`
    Severity        string   `yaml:"severity" json:"severity"`
    SecurityAdvise  string   `yaml:"security_advise,omitempty" json:"security_advise"`
    References      []string `yaml:"references" json:"references"`
    Author          string   `yaml:"author,omitempty" json:"author,omitempty"`
}
```

字段说明：
- `FingerPrintName`（yaml: name）— 关联的指纹组件名称
- `CVEName`（yaml: cve）— CVE 编号
- `Summary` — 漏洞简述
- `Details` — 详细描述
- `CVSS` — CVSS 评分
- `Severity` — 严重级别（high/critical/medium/low 或中文）
- `SecurityAdvise` — 安全修复建议
- `References` — 参考链接列表

## VersionVul 结构

```go
type VersionVul struct {
    Info        Info         `yaml:"info" json:"info"`
    Rule        string       `yaml:"rule" json:"rule"`
    RuleCompile *parser.Rule `yaml:"-" json:"-"`
    References  []string     `yaml:"references" json:"references"`
}
```

自定义 `UnmarshalYAML`：
- `rule` 字段必填，缺失返回错误
- Rule 字段即使为空字符串也允许
- 反序列化后 `Info.References` 被设置为顶层 References

## ReadVersionVul 函数

```go
func ReadVersionVul(body []byte) (*VersionVul, error)
```

处理流程：
1. `yaml.Unmarshal` 到 `VersionVul`
2. TrimSpace 处理 `Info.Details`
3. 复制 `References` 到 `Info.References`
4. 若 Rule 为空，RuleCompile 设为 nil
5. 调用 `parser.ParseAdvisorTokens(advisory.Rule)` 词法分析
6. 调用 `parser.CheckBalance(tokens)` 检查括号
7. 调用 `parser.TransFormExp(tokens)` 构建 AST
8. 赋值给 `RuleCompile`

## AdvisoryEngine

```go
type AdvisoryEngine struct {
    ads []VersionVul
}
```

方法：

```go
func NewAdvisoryEngine() *AdvisoryEngine
func (ae *AdvisoryEngine) LoadFromDirectory(dir string) error
func (ae *AdvisoryEngine) LoadFromHost(host string) error
func (ae *AdvisoryEngine) GetAdvisories(packageName, version string, isInternal bool) ([]VersionVul, error)
func (ae *AdvisoryEngine) GetCount() int
func (ae *AdvisoryEngine) GetAll() []VersionVul
```

### LoadFromDirectory

- 若 dir 是目录，递归扫描所有文件
- 仅处理 `.yaml` 后缀文件
- 对每个文件调用 `ReadVersionVul` 解析
- 任一文件解析失败则整体返回错误
- 结果存入 `ae.ads`

### LoadFromHost

- 请求 `http://{host}/api/v1/knowledge/vulnerabilities?page=1&size=9999`
- 调用 `utils.LoadRemoteVulStruct` 获取数据
- 对每条原始数据调用 `ReadVersionVul`

### GetAdvisories

匹配逻辑：
1. 遍历所有已加载的 `VersionVul`
2. `ad.Info.FingerPrintName != packageName` 跳过
3. 若 version 非空且 Rule 非空：调用 `ad.RuleCompile.AdvisoryEval(&parser.AdvisoryConfig{Version: version, IsInternal: isInternal})`
4. 否则（version 为空或 Rule 为空）：直接加入结果（无条件匹配）

## YAML 规则文件格式示例

```yaml
info:
  name: vllm
  cve: CVE-2024-XXXX
  summary: 漏洞简述
  details: |
    详细描述
  cvss: "7.5"
  severity: HIGH
  security_advise: 升级到 xxx 版本或更高版本
  references:
    - https://example.com/advisory
rule: version < "0.5.0"
references:
  - https://example.com/advisory
```

规则表达式支持：
- `version > "x.y.z"`
- `version >= "x.y.z"`
- `version < "x.y.z"`
- `version <= "x.y.z"`
- `version == "x.y.z"`
- `version != "x.y.z"`
- `is_internal`
- 逻辑组合：`&&`、`||`、括号

## 相关概念

- [CVE 漏洞匹配](/concepts/03-vuln-matching.md)
- [指纹规则 DSL](/concepts/02-fingerprint-dsl.md)
- [扫描引擎信源](/references/scan-engine.md)
