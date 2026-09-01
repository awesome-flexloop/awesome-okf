# 实战示例（Examples）

本目录包含 MobileWorld 的 3 篇实战示例，对应读者实际跑分的三类必经路径：官方脚本评测、快照定制、真机与社区提交。所有步骤均来自仓库文档化的操作序列（scripts/ 与 docs/）。

## 示例清单

| 序号 | 文档 | 覆盖事实 | 说明 |
|------|------|---------|------|
| 01 | [运行官方评测脚本](01-run-built-in-eval-scripts.md) | F-072、F-037（参数解读另引 F-019/F-020/F-022） | 四个 run_*.sh 的公共模式与差异，`env run --count 5` + `eval` 两段式 |
| 02 | [定制 AVD 快照](02-customize-avd-snapshot.md) | F-073、F-061、F-067 | dev 容器内改快照 → 定冻结日期 → snapshot save → docker cp → buildx 重建镜像八步 |
| 03 | [真机评测与 leaderboard 提交](03-real-device-and-leaderboard-submit.md) | F-074、F-075、F-030、F-079 | USB 真机 + 各模型坐标约定表；bundle_trajs.py 打包 → leaderboard.json 条目 → issue 提交 |

### 建议顺序

```
01（先跑通官方全量评测）
  ↓
02（需要自定义评测起点时）
  ↓
03（真机补充评测 + 结果对外提交）
```

```{toctree}
:hidden:
:maxdepth: 7

01-run-built-in-eval-scripts
02-customize-avd-snapshot
03-real-device-and-leaderboard-submit
```
