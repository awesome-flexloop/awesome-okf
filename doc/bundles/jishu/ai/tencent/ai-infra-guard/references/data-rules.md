---
type: Reference
title: 数据文件与规则格式信源
description: 记录 fingerprints、vuln、mcp、eval 四类数据文件的目录结构、YAML 格式和规模统计。
tags: [ai-infra-guard, data, yaml, fingerprint, vulnerability, mcp, eval]
generated: { by: "reference_agent/trae-solo", at: "2026-08-23T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T00:00:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: src-data
    resource: /references/data-rules.md
    title: 数据文件与规则格式信源
---

## 源码/数据路径

- `data/fingerprints/` — 142 个 .yaml 文件
- `data/vuln/` — 2014 个 .yaml 文件（中文，按组件分目录）
- `data/vuln_en/` — 英文漏洞库（部分组件）
- `data/mcp/` — 15 个 .yaml 文件
- `data/eval/` — 17 个 .json 文件

## 指纹文件格式

每个 .yaml 文件对应一个组件指纹：

```yaml
info:
  name: dify
  author: author_name
  example:
    - https://example.com
  desc: 组件描述
  severity: high
  metadata:
    key: value
  recommendation: 1
http:
  - method: GET
    path: /
    matchers:
      - 'body="dify"'
      - 'header="x-powered-by" && body="~=dify"'
    extractor:
      part: body
      group: version
      regex: 'dify/v(\d+\.\d+\.\d+)'
version:
  - method: GET
    path: /api/version
    matchers:
      - 'body="version"'
    versionrange: '*'
```

### Matchers DSL

匹配源关键字：
- `body` — HTTP 响应体
- `header` — HTTP 响应头
- `icon` — favicon hash（mmh3）
- `hash` — 响应体 hash

操作符：
- `=` — 包含（contains）
- `==` — 完全相等
- `!=` — 不包含
- `~=` — 正则匹配

逻辑：
- `&&` — 与
- `||` — 或
- `(...)` — 括号分组

注意：`hash` matcher 不能与其他类型 matcher 共存。

### 组件列表（部分）

涵盖 142 个 AI 基础设施组件，包括：
- LLM 推理：vllm, ollama, llama-cpp, sglang, tensorrt-llm, lmdeploy, xinference, localai
- AI 框架：langflow, flowise, dify, fastgpt, maxkb, anythingllm, openwebui, librechat
- Agent 框架：crewai, autogpt, superagi, praisonai, langroid
- 向量库：milvus, qdrant, weaviate, chroma
- 工作流：n8n.io, ray, dask_http, kubeflow, mlflow
- MCP：mcp, mcp-server, n8n-mcp
- 开发工具：jupyter-lab, gradio, marimo, bentoml

## 漏洞文件格式

`data/vuln/<component>/CVE-XXXX-XXXX.yaml`：

```yaml
info:
  name: vllm
  cve: CVE-2024-XXXX
  summary: 漏洞简述
  details: |
    详细描述，可多行
  cvss: "7.5"
  severity: HIGH
  security_advise: 升级到 x.y.z 或更高版本
  references:
    - https://nvd.nist.gov/vuln/detail/CVE-2024-XXXX
    - https://github.com/vllm-project/vllm/security/advisories/...
  author: researcher_name
rule: version < "0.5.0"
references:
  - https://nvd.nist.gov/vuln/detail/CVE-2024-XXXX
```

### rule 表达式

- `version > "1.0.0"` — 大于
- `version >= "1.0.0"` — 大于等于
- `version < "1.0.0"` — 小于
- `version <= "1.0.0"` — 小于等于
- `version == "1.0.0"` — 等于
- `version != "1.0.0"` — 不等于
- `is_internal` — 内网环境标识
- 逻辑组合：`(version > "1.0" && version < "2.0") || is_internal`

### 组件目录

- `dask/` — 2 个 CVE
- `dify/` — 26 个 CVE
- `jan/` — 2 个 CVE
- `mcp/` — 2 个 CVE
- `n8n/` — 65+ 个 CVE
- `ray/` — 11 个 CVE + 部署安全提示
- `vllm/` — 45+ 个 CVE + 部署安全提示
- `ollama/` — 部署安全提示

## MCP 插件规则格式

`data/mcp/<rule_name>.yaml`：

```yaml
info:
  id: mcp_ssrf
  name: MCP SSRF Detection
  description: 检测 MCP 工具中的 SSRF 漏洞
  author: researcher
  categories:
    - ssrf
    - network
rules:
  - name: 直接URL请求
    pattern: 'requests\.(get|post|put|delete)\s*\('
    description: 工具直接发起 HTTP 请求，可能存在 SSRF
prompt_template: |
  你是一个安全审计专家，请分析以下 MCP 工具代码...
```

### 规则文件列表

- `cors.yaml` — CORS 配置检测
- `mcp_path_traversal.yaml` — 路径遍历
- `mcp_sql_injection.yaml` — SQL 注入
- `mcp_ssrf.yaml` — SSRF
- `mcp_tool_rug_pull.yaml` — 工具恶意行为
- `tool_poisoning.yaml` — 工具投毒
- 以及其他 9 个规则文件（共 15 个）

### internal/mcp 中的结构对应

```go
type PluginConfig struct {
    Info struct {
        ID          string   `yaml:"id"`
        Name        string   `yaml:"name"`
        Description string   `yaml:"description"`
        Author      string   `yaml:"author"`
        Category    []string `yaml:"categories"`
    } `yaml:"info"`
    Rules          []Rule `yaml:"rules,omitempty"`
    PromptTemplate string `yaml:"prompt_template"`
}

type Rule struct {
    Name        string `yaml:"name"`
    Pattern     string `yaml:"pattern"`
    Description string `yaml:"description"`
}
```

## 评测集格式

`data/eval/<name>.json`，JSON 数组格式，每条记录包含 prompt 及相关元数据。

### 评测集列表（17个）

| 文件名 | 主题 |
|--------|------|
| advbench.json | 通用对抗性提示 |
| cnsafe.json | 中文安全评测 |
| safebench.json | 安全基准 |
| JailBench-Tiny.json | 越狱小型集 |
| CBRN-weapon.json | CBRN 武器相关 |
| violent.json | 暴力内容 |
| misinformation.json | 虚假信息 |
| privacy-leakage.json | 隐私泄露 |
| unethical-behavior.json | 不道德行为 |
| cyberattack.json | 网络攻击 |
| JADE-db-v3.0.json | JADE 数据库 |
| 以及其他 6 个文件 | |

评测集通过 `/api/v1/knowledge/evaluations` API 管理，在 ModelRedteamReport 任务中通过 `MultiDataset:dataset_file=<path>` scenario 引用。

## 数据加载机制

### 指纹加载

`Runner.initFingerprints()`：
1. 若 `LoadRemote` 为 true，调用 `utils.LoadRemoteFingerPrints`
2. 否则读取 `--fps` 指定路径（文件或目录）
3. 目录模式下扫描所有 `.yaml` 文件
4. 对每个文件调用 `parser.InitFingerPrintFromData(data)`
5. 创建 `preload.New(hp, fps)` 指纹引擎

### 漏洞加载

`Runner.initVulnerabilityDB()`：
1. 若 `LoadRemote`，调用 `engine.LoadFromHost`
2. 否则调用 `engine.LoadFromDirectory(vulDir)`
3. Language 为 "en" 时自动追加 `_en` 后缀（`data/vuln_en`）
4. 加载时编译所有 rule 表达式为 AST

### MCP 插件加载

`Scanner.RegisterPlugin(plugins)`：
1. 定位可执行文件同目录的 `data/mcp/`，不存在则回退工作目录
2. 扫描所有 `.yaml` 文件
3. 调用 `NewYAMLPlugin(configPath)` 解析
4. 若 plugins 列表非空，仅加载 ID 在列表中的插件

## 相关概念

- [指纹规则 DSL](../concepts/02-fingerprint-dsl.md)
- [CVE 漏洞匹配](../concepts/03-vuln-matching.md)
- [MCP 安全扫描](../concepts/06-mcp-scan.md)
- [自定义指纹示例](../examples/custom-fingerprint.md)
