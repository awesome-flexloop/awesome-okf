---
type: Example
title: "演练 00：本地复现一次构建并验证幂等"
description: "按 build.sh 的四步在本地跑一次合并，核对三节计数、验证第二次运行零差异，并处理常见的四类失败"
---

# 演练 00：本地复现一次构建并验证幂等

> **边界声明**：以下命令**未在本次研读中执行**，依据为 `scripts/build.sh`（F-025 ~ F-031）与 `scripts/merge.py`（F-032 ~ F-044）。执行会**就地覆写**目标文件（F-043），请先备份。

## 1. 前置条件

| 依赖 | 检查命令 | 说明 |
|------|---------|------|
| bash | `bash --version` | 脚本使用 `set -euo pipefail` 与 `trap` |
| curl | `curl --version` | 需要 `-f`（失败即退）与 `-L`（跟随重定向） |
| base64 | `base64 --version` | GNU coreutils 或 busybox 均可 |
| python3 | `python3 --version` | 脚本调用 `python3`，不是 `python` |
| 网络 | 可访问 `raw.githubusercontent.com` | 上游 gfwlist 的默认地址 |

Windows 用户请在 WSL 或 Git Bash 中执行；PowerShell 没有 `base64 -d` 的同义开关。

## 2. 操作步骤

```bash
# ① 进入仓库并备份（就地覆写，务必先备份）
cd skylinevpn-proxylist
cp proxy.list proxy.list.bak

# ② 跑构建：默认拉 gfwlist，写回仓库根的 proxy.list
./scripts/build.sh

# ③ 看三节计数（脚本会把计数打到 stdout）
#    预期形如：domain_suffix=26447, exact=84, regex=167

# ④ 看差异规模
git diff --stat proxy.list

# ⑤ 再跑一次，验证幂等
./scripts/build.sh
git diff --stat proxy.list        # 预期：无输出（第二次不再产生差异）
```

第 ⑤ 步是重点：如果第二次仍有差异，说明归约不幂等，或上游在两次运行之间发生了变化（周一 00:00 UTC 前后尤其容易遇到）。

## 3. 预期结果与判读

| 观察项 | 正常 | 异常与含义 |
|--------|------|-----------|
| stdout 计数 | 三节均有值，后缀约 2.6 万 | 后缀为 0 或个位数 → 上游未抓到或解码失败（D-2） |
| 文件头 | 两行固定注释 | 头部有额外注释 → 说明上一次是人工编辑，本次已被清除（F-042） |
| `git diff --stat` | 首次若干行新增，第二次无输出 | 第二次大量删除 → 上游收缩或归约异常 |
| 文件大小 | 约 389 KB | 明显偏小（如 < 50 KB）→ 立即回滚备份 |

## 4. 常见失败与处置

**（1）`curl: (22) The requested URL returned error: 404`**

上游路径变更。`build.sh` 的 `SRC_URL` 可覆盖（F-026）：

```bash
SRC_URL="https://example.com/gfwlist.txt" ./scripts/build.sh
```

**（2）`base64: invalid input`**

上游返回的不是 base64（可能是 HTML 错误页或被中间层改写）。`set -euo pipefail` 会让脚本中止，此时 `proxy.list` **尚未被写入**，原文件安全。

**（3）`entry outside known section: xxx`**

`merge.py` 在读取现有 `proxy.list` 时遇到不认识的节（F-038）。说明有人手工加了第四节的标题，或文件被其他工具改写过。处置：从备份恢复，或用 `git checkout -- proxy.list`。

**（4）计数正常但匹配结果不对**

不是构建问题，而是消费端语义问题（D-5）。检查消费端是否把 `domain_suffix` 实现成「严格相等」而不是「含子域」。

## 5. 收尾

```bash
# 确认无误后再删除备份
rm proxy.list.bak

# 若要提交，注意工作流会在 push 后自动发版（F-046）
git add proxy.list
git commit -m "Update proxy.list $(date -u +%Y-%m-%d)"
```

若只是本地验证、不想触发发布，**不要 push 到 `main`**；工作流的 `push` 触发器会在 `proxy.list` 变更时立刻发 Release（F-046）。

## 6. 这次演练验证了什么

- ✅ 构建脚本可以在本地独立运行，不依赖 Actions；
- ✅ 归约对同一输入是确定性的（排序 + 集合，F-042）；
- ✅ 无变化时 `git diff` 为空，这是「静默提交」（F-052）的前提；
- ❌ 不验证上游内容正确性——脚本本身不做内容判断。

## 关联

- 原理：[02 上游消化](../concepts/02-upstream-digestion-pipeline.md)、[03 归约算法](../concepts/03-reduction-algorithm.md)
- 风险：[05 风险与边界](../concepts/05-boundaries-and-risk-model.md) 第 2 节
- 事实：F-025 ~ F-031、F-042 ~ F-044、F-052
