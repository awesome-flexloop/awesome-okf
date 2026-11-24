---
type: Example
title: "演练 02：维护者发布 Runbook"
description: "手动触发、更换上游源、同日重发、回滚错误清单与发布后核对——一份按步骤执行、每步都带验收信号的维护者操作手册"
---

# 演练 02：维护者发布 Runbook

> **边界声明**：本演练的命令依据 `.github/workflows/release.yml`（F-045 ~ F-058）与 `README.md`（F-064）整理，**未在本次研读中执行**。所有写操作（推送、发版、删 tag）都应由有仓库写权限的人确认后执行。

## 1. 日常：什么都不用做

正常节拍是每周一 00:00 UTC 由 cron 触发（F-045），流程为：抓上游 → 合并 → 有变化才提交 → 发 Release。维护者的日常动作只有**每周扫一眼 Release 列表**，确认两件事：

1. 本周是否出现了新的日期 tag；
2. Release notes 里的 `Rules: N` 是否仍在合理区间（当前约 26,698，F-015）。

若某周没有新 tag，先看 Actions 是否失败，再看 `proxy.list` 是否本来就没有变化（可能只是上游无更新）。

## 2. 手动触发一次发布

```bash
# 触发工作流（默认分支上的 release.yml）
gh workflow run release.yml

# 查看运行状态
gh run list --workflow=release.yml --limit 5

# 跟踪最新一次运行
gh run watch
```

适用场景：刚合并了策展条目但没改 `proxy.list` 之外的触发条件、或定时任务漏跑。注意 `push` 触发只认 `proxy.list` 路径（F-046），改脚本不会自动发版。

**验收信号**：运行成功后，`gh release list --limit 3` 能看到当天的 `vYYYYMMDD`，且 `latest` 指向同一提交（F-058）。

## 3. 同日重发

工作流本身支持同日重跑（F-056）：`gh release delete "$TAG" --yes --cleanup-tag || true` 会先删掉当天 Release 与 tag，再重建。

因此**不需要手工删**，直接再触发一次即可。手工干预只在一种情况下需要：删除动作因权限失败（此时日志里会出现 `release delete` 的非零退出被 `|| true` 吞掉），需要人工确认旧 Release 是否残留。

```bash
gh release view "v$(date -u +%Y%m%d)"     # 确认是否残留/是否为新
gh release delete "v$(date -u +%Y%m%d)" --yes --cleanup-tag
```

## 4. 更换上游源

`build.sh` 的 `SRC_URL` 可由环境变量覆盖（F-026）。两种改法：

**（1）临时换源（本地验证）**

```bash
SRC_URL="https://example.com/other-gfwlist.txt" ./scripts/build.sh /tmp/proxy.test.list
```

**（2）永久换源（改工作流）**

在 `release.yml` 的 merge 步骤上加 `env`：

```yaml
      - name: Merge upstream into proxy.list
        env:
          SRC_URL: https://example.com/other-gfwlist.txt
        run: ./scripts/build.sh proxy.list
```

**验收信号**：新源首次运行后，`git diff --stat` 的变化规模应与源切换的预期一致；若出现数万行删除，立即回滚（见第 5 节）。

## 5. 回滚一次错误发布

规则表的回滚分两层，不要混用：

| 层 | 目标 | 做法 |
|----|------|------|
| 数据回滚 | 让 `proxy.list` 回到上一版 | `git revert <bad-commit>` 后推送，工作流会自动发新 Release |
| 发版撤回 | 让某个 Release 不再对外 | `gh release delete vYYYYMMDD --yes --cleanup-tag` |

推荐先做数据回滚：`git revert` 产生的新提交会被 `push` 触发器接手，自动走一遍完整流程，产物与历史都可追溯。直接删 Release 而不回滚数据，会导致「下次 cron 又把错误内容发出来」。

```bash
git log --oneline -5 proxy.list        # 找到要回滚的提交
git revert --no-edit <bad-commit>
git push
```

**验收信号**：新 Release 的 notes 里 `Rules: N` 回到预期区间；`proxy.list` 的三节计数与回滚前一致（对比 F-015 的口径）。

## 6. 发布后核对清单

每次人工介入后，按此表逐项确认：

| # | 检查 | 命令 / 位置 | 通过标准 |
|---|------|-----------|---------|
| 1 | 工作流成功 | `gh run list --workflow=release.yml` | 最近一次为 success |
| 2 | 当天 tag 存在 | `gh release list --limit 3` | 有 `vYYYYMMDD` |
| 3 | latest 对齐 | `git rev-list -n1 latest` 与 `git rev-parse HEAD` | 两者相同 |
| 4 | 资产存在 | `gh release view vYYYYMMDD` | 列表含 `proxy.list` |
| 5 | 条目数合理 | Release notes 的 `Rules: N` | 与上一版差异在合理区间 |
| 6 | 三节完整 | 下载后 `grep -c "^## "` | 输出 3 |

第 5 项是唯一能发现「上游异常」的人工检查点——因为流程本身不设下界（D-2）。

## 7. 紧急处置：停掉自动发布

若确认上游被污染且短期无法修复，最小干预是**禁用工作流**（而不是删仓库或改 tag）：

```bash
gh workflow disable release.yml     # 停止 cron 与 push 触发
gh workflow enable release.yml      # 修复后恢复
```

禁用后，已发布的 Release 仍在，消费端继续拿到旧表——这通常比拿到污染表更安全（见 [演练 01](01-consumer-integration.md) 第 5 节）。

## 8. 这次演练验证了什么

- ✅ 手动触发与定时触发走同一条代码路径，不存在「只有 CI 能跑」的隐藏依赖；
- ✅ 同日重发是幂等的，不需要人工清理；
- ✅ 回滚应优先在数据层做（`git revert`），而不是只在发布层删 Release；
- ❌ 不提供「上游内容是否正确」的判断方法——那需要人工抽样。

## 关联

- 发布原理：[04 发布通道](../concepts/04-release-channel-and-fixed-url.md)
- 风险清单：[05 风险与边界](../concepts/05-boundaries-and-risk-model.md)
- 事实：F-045 ~ F-058、F-026、F-064
