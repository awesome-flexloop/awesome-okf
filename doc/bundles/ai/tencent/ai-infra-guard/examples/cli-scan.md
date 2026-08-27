---
type: Example
title: CLI 命令行扫描
description: 使用 ai-infra-guard scan 子命令对目标进行指纹识别和 CVE 漏洞扫描，支持单目标、批量目标、CIDR、代理、自定义规则库等参数。
tags: [ai-infra-guard, cli, scan, command-line, example]
generated: { by: "reference_agent/trae-solo", at: "2026-08-23T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T00:00:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: scan-engine
    resource: /references/scan-engine.md
    title: 扫描引擎与指纹 DSL 信源
  - id: go-server
    resource: /references/go-server.md
    title: Go WebSocket 与 HTTP Server 信源
---

## 基本扫描

扫描单个目标：

```bash
ai-infra-guard scan -t https://192.168.1.100:8080
```

扫描多个目标：

```bash
ai-infra-guard scan -t https://target1.com -t https://target2.com -t 192.168.1.0/24
```

从文件读取目标列表：

```bash
ai-infra-guard scan -f targets.txt
```

`targets.txt` 每行一个目标，支持 URL、IP:Port、CIDR 格式。

## 常用参数

| 参数 | 缩写 | 默认值 | 说明 |
|------|------|--------|------|
| `--target` | `-t` | 无 | 目标 URL，可多次指定 |
| `--file` | `-f` | 无 | 目标列表文件路径 |
| `--output` | `-o` | 无 | 输出文件路径 |
| `--timeout` | 无 | 5 | 请求超时时间（秒） |
| `--proxy-url` | 无 | 无 | HTTP 代理服务器 URL |
| `--header` | 无 | 无 | 自定义 HTTP 头，可多次指定 |
| `--limit` | 无 | 200 | 每秒最大请求数 |
| `--fps` | 无 | `data/fingerprints` | 指纹模板目录或文件 |
| `--vul` | 无 | `data/vuln` | 漏洞库目录 |
| `--lang` | 无 | `zh` | 输出语言（zh/en） |
| `--localscan` | 无 | false | 一键本地扫描（自动探测本机端口） |

## 扫描输出示例

扫描完成后，终端输出两张表格：

```
Application Summary:
+---------------------------+------------+-----------------+-------------------+
| Target                    | StatusCode | Title           | FingerPrint       |
+---------------------------+------------+-----------------+-------------------+
| https://10.0.0.5:3000     | 200        | Dify            | dify:0.10.0       |
| https://10.0.0.6:8000     | 200        | vLLM API server | vllm:0.5.0        |
+---------------------------+------------+-----------------+-------------------+

Vulnerability Summary:
+----------------+----------+----------------------------+-----------------------+
| CVE            | Severity | VulName                    | Target                |
+----------------+----------+----------------------------+-----------------------+
| CVE-2024-10252 | HIGH     | Dify 未授权访问            | https://10.0.0.5:3000 |
| CVE-2024-8768  | CRITICAL | vLLM API 未授权访问        | https://10.0.0.6:8000 |
+----------------+----------+----------------------------+-----------------------+
```

## 自定义规则库

使用私有指纹和漏洞库：

```bash
ai-infra-guard scan \
  -t https://internal.target.com \
  --fps /path/to/custom/fingerprints/ \
  --vul /path/to/custom/vuln/
```

英文漏洞描述：

```bash
ai-infra-guard scan -t https://target.com --lang en
```

## 本地扫描

自动探测本机开放端口并扫描：

```bash
ai-infra-guard scan --localscan
```

该模式调用 `utils.GetLocalOpenPorts()` 获取本机监听端口，对每个端口自动构造目标进行扫描。

## 使用代理

```bash
ai-infra-guard scan \
  -t https://target.com \
  --proxy-url http://127.0.0.1:8080
```

## 自定义请求头

```bash
ai-infra-guard scan \
  -t https://target.com \
  --header "Authorization: Bearer token123" \
  --header "X-Forwarded-For: 127.0.0.1"
```

## 列出可用漏洞模板

```bash
ai-infra-guard scan --list-vul
```

输出所有指纹组件及其关联漏洞数量的表格。

## 启动 Web 服务器

除了 CLI 扫描，还可以启动带 Web UI 的服务器：

```bash
ai-infra-guard webserver --server 127.0.0.1:8088
```

环境变量配置 API Checker：

```bash
export AIG_API_CHECKER_URL=http://127.0.0.1:8000
ai-infra-guard webserver
```

启动后浏览器访问 `http://127.0.0.1:8088` 即可使用图形界面。

## 输出到文件

```bash
ai-infra-guard scan -t https://target.com -o result.txt
```

输出文件包含每个目标的指纹信息和漏洞详情。

## 工作原理

1. CLI 的 `scanCmd.Run` 构造 `options.Options` 结构体
2. 调用 `runner.New(options)` 初始化扫描引擎
3. Runner 依次初始化存储、目标处理、HTTP 客户端、指纹引擎、漏洞引擎
4. 调用 `r.RunEnumeration()` 并发扫描所有目标
5. 对每个目标：HTTP 请求 → favicon hash → 指纹匹配 → 漏洞匹配 → 结果输出
6. 安全评分通过 `CalcSecScore` 计算（高危 -70/中危 -30/低危 -10）

## 相关概念

- [指纹规则 DSL](../concepts/02-fingerprint-dsl.md)
- [CVE 漏洞匹配](../concepts/03-vuln-matching.md)
- [分布式架构总览](../concepts/00-architecture.md)
- [Docker 部署示例](docker-deploy.md)
