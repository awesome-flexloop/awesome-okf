---
type: Concept
title: CVE 漏洞匹配
description: AIG 的漏洞引擎基于语义化版本比较，将指纹识别出的组件版本与 YAML 规则库中的 version 表达式匹配，当前内置 2014 条 CVE 规则并支持中英文双语。
tags: [ai-infra-guard, vulnerability, cve, version, semantic-version, advisory]
generated: { by: "reference_agent/trae-solo", at: "2026-08-23T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T00:00:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: vuln-struct
    resource: /references/vuln-struct.md
    title: 漏洞结构与 AdvisoryEngine 信源
  - id: scan-engine
    resource: /references/scan-engine.md
    title: 扫描引擎与指纹 DSL 信源
---

## 概述

漏洞匹配引擎（`AdvisoryEngine`）负责将指纹识别阶段发现的组件名称和版本号，与漏洞规则库进行比对，返回受影响的 CVE 列表。它与指纹 DSL 共享同一套表达式解析器，但使用版本比较语义而非字符串匹配。

## 数据结构

### Info（漏洞元信息）

```go
type Info struct {
    FingerPrintName string   `yaml:"name"`
    CVEName         string   `yaml:"cve"`
    Summary         string   `yaml:"summary"`
    Details         string   `yaml:"details"`
    CVSS            string   `yaml:"cvss"`
    Severity        string   `yaml:"severity"`
    SecurityAdvise  string   `yaml:"security_advise,omitempty"`
    References      []string `yaml:"references"`
    Author          string   `yaml:"author,omitempty"`
}
```

### VersionVul（版本漏洞规则）

```go
type VersionVul struct {
    Info        Info         `yaml:"info"`
    Rule        string       `yaml:"rule"`
    RuleCompile *parser.Rule `yaml:"-"`
    References  []string     `yaml:"references"`
}
```

`Rule` 字段是 DSL 表达式字符串，在文件加载时编译为 `*parser.Rule` AST，运行时通过 `AdvisoryEval` 求值。

## AdvisoryEngine

```go
type AdvisoryEngine struct {
    ads []VersionVul
}
```

核心方法：

| 方法 | 功能 |
|------|------|
| `NewAdvisoryEngine()` | 创建空引擎 |
| `LoadFromDirectory(dir)` | 从目录递归加载所有 .yaml 漏洞文件 |
| `LoadFromHost(host)` | 从远程 Server API 加载 |
| `GetAdvisories(pkgName, version, isInternal)` | 查询匹配的漏洞 |
| `GetCount()` | 返回已加载规则总数 |

### GetAdvisories 匹配逻辑

```go
func (ae *AdvisoryEngine) GetAdvisories(packageName, version string, isInternal bool) ([]VersionVul, error) {
    for _, ad := range ae.ads {
        if ad.Info.FingerPrintName != packageName {
            continue  // 组件名不匹配，跳过
        }
        if version != "" && ad.Rule != "" {
            // 有版本号且有规则：执行版本比较
            if ad.RuleCompile.AdvisoryEval(&parser.AdvisoryConfig{
                Version: version,
                IsInternal: isInternal,
            }) {
                ret = append(ret, ad)
            }
        } else {
            // 无版本号或无规则：无条件匹配
            ret = append(ret, ad)
        }
    }
}
```

关键点：
- 先按组件名（`FingerPrintName`）过滤
- 若检测到版本号且规则非空，执行语义化版本比较
- 若版本号为空（指纹未提取到版本）或规则为空字符串，漏洞无条件匹配（保守策略）

## 版本比较 DSL

### 关键字

- `version` — 表示检测到的版本号
- `is_internal` — 布尔值，表示是否内网环境

### 比较操作符

| 操作符 | 语义 | hashicorp/go-version 方法 |
|--------|------|--------------------------|
| `>` | 大于 | `GreaterThan` |
| `>=` | 大于等于 | `GreaterThanOrEqual` |
| `<` | 小于 | `LessThan` |
| `<=` | 小于等于 | `LessThanOrEqual` |
| `==` | 等于 | `Equal` |
| `=` | 等于（同 ==） | `Equal` |
| `!=` | 不等于 | `!Equal` |

### 逻辑组合

支持 `&&`、`||` 和括号：

```yaml
rule: version > "1.0.0" && version < "2.0.0"
rule: (version >= "3.0" && version < "4.0") || is_internal
```

### 版本号标准化

`versionCheck` 函数在比较前对版本号进行标准化：

1. 去除 `v` 前缀（`v1.2.3` → `1.2.3`）
2. `"latest"` 视为 `"999"`（始终大于普通版本）
3. 字母部分替换为 `.0`（`1.2.3-rc1` → `1.2.3.0.0`）
4. 空字符串视为 `"0"`
5. 无法解析的版本回退为 `0.0.0`

这意味着非标准版本号也不会导致程序崩溃，而是以保守方式处理。

## 规则文件示例

```yaml
info:
  name: vllm
  cve: CVE-2024-8768
  summary: vLLM 存在未授权访问漏洞
  details: |
    vLLM 在默认配置下未启用身份验证，攻击者可通过
    API 直接访问模型推理服务，导致计算资源滥用。
  cvss: "9.8"
  severity: CRITICAL
  security_advise: 升级到 v0.6.0 或更高版本，或配置网络访问控制
  references:
    - https://nvd.nist.gov/vuln/detail/CVE-2024-8768
  author: zhuque-lab
rule: version < "0.6.0"
references:
  - https://nvd.nist.gov/vuln/detail/CVE-2024-8768
```

## 双语支持

漏洞库提供中文和英文两个版本：
- `data/vuln/` — 中文漏洞描述（默认）
- `data/vuln_en/` — 英文漏洞描述

Runner 初始化时根据 `Options.Language` 选择：

```go
vulDir := strings.TrimRight(r.Options.AdvTemplates, "/")
if r.Options.Language == "en" {
    vulDir = vulDir + "_en"
}
err = engine.LoadFromDirectory(vulDir)
```

CLI 通过 `--lang en` 切换。

## 安全评分

扫描完成后，`Runner.CalcSecScore` 根据漏洞严重程度计算安全分数：

| 严重级别 | 扣分 |
|---------|------|
| HIGH / CRITICAL / 高危 / 严重 | 70 分/个 |
| MEDIUM / 中危 | 30 分/个 |
| LOW / 其他 | 10 分/个 |

- 基础分：100
- 最低分：0（扣到 0 为止）
- 无漏洞：100 分

该分数在 AI-Infra-Scan 任务最终结果中返回，用于前端展示安全评分仪表盘。

## 从扫描到漏洞匹配的完整链路

```
HTTP 响应
  │
  ├─► favicon hash 计算
  │
  ├─► fpEngine.RunFpReqs()
  │     ├─► 遍历 142 个指纹
  │     ├─► 对每个指纹执行 body/header/icon 匹配
  │     └─► 返回 []FpResult{Name, Version}
  │
  └─► advEngine.GetAdvisories(name, version, isInternal)
        ├─► 按组件名过滤 2014 条规则
        ├─► 执行 RuleCompile.AdvisoryEval()
        │     ├─► versionCheck() 标准化版本号
        │     ├─► hashicorp/go-version 比较
        │     └─► 逻辑运算求值
        └─► 返回 []VersionVul（命中的 CVE）
```

## 相关概念

- [指纹规则 DSL](/concepts/02-fingerprint-dsl.md)
- [分布式架构总览](/concepts/00-architecture.md)
- [漏洞结构信源](/references/vuln-struct.md)
- [CLI 扫描示例](/examples/cli-scan.md)
