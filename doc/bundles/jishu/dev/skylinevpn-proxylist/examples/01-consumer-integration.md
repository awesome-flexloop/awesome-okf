---
type: Example
title: "演练 01：消费方接入与更新策略"
description: "用固定 URL 拉取 proxy.list、按三节语义实现一次主机匹配、设计增量更新与失败回退，并在接入侧补上仓库缺失的完整性检查"
---

# 演练 01：消费方接入与更新策略

> **边界声明**：本演练给出的是**接入方实现建议**，不是仓库的官方接口。仓库只保证「有一个固定下载地址」（F-064），不保证格式文档、更新通知或内容正确性。

## 1. 拉取

最小可用命令就是 README 里那一行（F-064）：

```bash
curl -fsSL https://github.com/skyline-projext/skylinevpn-proxylist/releases/latest/download/proxy.list -o proxy.list
```

如果要走仓库快照通道（更新可能滞后于 Release，C-1）：

```bash
curl -fsSL https://raw.githubusercontent.com/skyline-projext/skylinevpn-proxylist/latest/proxy.list -o proxy.list
```

生产环境建议加三件事：超时、条件请求、落盘前校验。

```bash
curl -fsSL --connect-timeout 10 --max-time 60 \
     --retry 3 --retry-delay 2 \
     -o proxy.list.new \
     https://github.com/skyline-projext/skylinevpn-proxylist/releases/latest/download/proxy.list
```

先写 `.new` 再替换，避免拉取中断把本地旧表覆盖成半截。

## 2. 接入侧的三道自检

仓库没有校验和，接入方必须自己补（对应 [05](../concepts/05-boundaries-and-risk-model.md) 第 2 节）：

```bash
# ① 条目数下界：防止近空表
RULES=$(grep -vcE "^(#|$)" proxy.list.new)
[ "$RULES" -ge 20000 ] || { echo "too few rules: $RULES"; exit 1; }

# ② 三节齐全：防止结构被改
for s in domain_suffix exact regex; do
  grep -qx "## $s" proxy.list.new || { echo "missing section $s"; exit 1; }
done

# ③ 原子替换
mv proxy.list.new proxy.list
```

这三条能挡住上游异常（D-2）、结构变更（C-4）与半截文件三类问题，成本不到十行。

若要更强，可在首次接入时记录文件 SHA-256，之后只做**单调性检查**（条目数不在合理区间即告警），而不是逐次比对摘要——因为每周必然变化。

## 3. 解析三节

三节语义由 `merge.py` 的归约逻辑反推（F-040），最低实现如下：

```python
import re

def load(path):
    sections = {"domain_suffix": [], "exact": [], "regex": []}
    cur = None
    for line in open(path, encoding="utf-8"):
        line = line.rstrip("\n")
        if line.startswith("## "):
            cur = line[3:].strip()
        elif line and not line.startswith("#") and cur in sections:
            sections[cur].append(line)
    return sections

def matches(host, rule):
    host = host.lower().rstrip(".")
    if rule["domain_suffix"]:
        suf = rule["domain_suffix"]
        return any(host == s or host.endswith("." + s) for s in suf)
    if rule["exact"]:
        return host in rule["exact"]
    if rule["regex"]:
        return any(re.search(p, host) for p in rule["regex"])
    return False
```

关键点只有一条：**`domain_suffix` 必须实现为「等于或以 `.` + 后缀结尾」**。归约阶段已经删掉了被父后缀覆盖的子域条目（F-041），如果这里写成严格相等，那些被删掉的条目就真的失效了（D-5）。

性能提示：2.6 万条逐条 `endswith` 在单次请求上可接受（毫秒级）；若要高频调用，应把后缀集合反转成「按标签从右往左查表」，而不是线性扫描。

## 4. 更新节奏

上游与发布节拍是**每周一 00:00 UTC**（F-045），但内容不一定每周变化（F-006）。建议：

| 策略 | 做法 | 适用 |
|------|------|------|
| 懒更新 | 每次启动检查本地文件 mtime，超过 7 天则拉取 | 桌面客户端 |
| 定时更新 | 每周二拉取一次（避开周一发布窗口） | 服务端常驻 |
| 事件更新 | 用户手动点「更新规则」 | 低频使用 |

不要按 tag 名去「追版本」——`latest` 是会被强推的别名（F-058），日期 tag 也可能被同日重发删除重建（F-056）。

## 5. 失败回退

```text
拉取失败 → 保留本地旧表（不要清空）
自检失败 → 保留本地旧表 + 告警
连续 N 次失败 → 告警升级，但不自动降级到空表
```

最后一条很重要：**空表在语义上等于「全部直连」**，与「规则过期」是完全不同的行为。多数故障场景下，旧表比空表安全。

## 6. 这次演练验证了什么

- ✅ 固定 URL 足以支撑无人值守的定期拉取；
- ✅ 三节语义可以用 20 行代码复现，不依赖仓库提供库；
- ✅ 接入侧可以用极低成本补上仓库缺失的完整性检查；
- ❌ 不能验证「命中后是否真的可达」——那取决于客户端与网络，不在本仓范围内。

## 关联

- 格式：[01 规则文件格式](../concepts/01-rule-file-format.md)
- 发布通道：[04 日期 tag 与 latest](../concepts/04-release-channel-and-fixed-url.md)
- 风险：[05 风险与边界](../concepts/05-boundaries-and-risk-model.md)
- 事实：F-001、F-006、F-015、F-041、F-045、F-056、F-058、F-064
