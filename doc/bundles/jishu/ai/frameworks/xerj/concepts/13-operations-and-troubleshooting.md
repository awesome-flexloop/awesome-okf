---
type: Concept
title: 生产运维与排障
description: XERJ 的生产部署形态——systemd 加固单元、存活与就绪双探针、SIGHUP 热加载边界、容量三数字与三文件 fd、备份四式、升级流程与六类生产症状的「症状→指标→日志→配置键」排障法
tags: [xerj, 运维, 备份, 升级, 排障, 容量]
generated: { by: source-code-to-okf-wiki/E, at: 2026-10-20T00:00:00Z }
verified: { by: source-code-to-okf-wiki/V, at: 2026-10-20T00:00:00Z }
status: stable
stale_after: 2027-04-20
sources:
  - id: xerj-docs-facts
    resource: /references/facts-docs.md
    title: 官方文档站事实清单
  - id: xerj-docs-source
    resource: /references/docs-source.md
    title: 官方文档站信源登记
---

# 生产运维与排障

## 部署心智模型

**一个二进制、一个配置文件、一个数据目录**（F-293）。剩下的都是调优。

### systemd 单元

以非 root 用户运行，配置与数据目录分开：

```sh
sudo useradd --system --home /var/lib/xerj --shell /usr/sbin/nologin xerj
sudo install -d -o xerj -g xerj -m 0750 /var/lib/xerj /etc/xerj
sudo install -m 0640 -o xerj -g xerj xerj.toml /etc/xerj/xerj.toml
```

```ini
[Service]
Type=simple
User=xerj
Group=xerj
ExecStart=/usr/local/bin/xerj --config /etc/xerj/xerj.toml
Restart=on-failure
RestartSec=5
LimitNOFILE=1048576
LimitMEMLOCK=infinity

# Hardening
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/var/lib/xerj
ProtectKernelTunables=true
ProtectKernelModules=true
ProtectControlGroups=true
SystemCallArchitectures=native
LockPersonality=true
```

加固项与 `LimitNOFILE` 的取值都来自官方单元（F-294）。`LimitNOFILE=1048576` 不是随手写的——见下面的「文件描述符」。

## 存活与就绪：两个探针

编排器不该在节点恢复途中把一个健康的节点杀掉，所以两者分开（F-295）：

| 探针 | 端点 | 返回 200 的条件 | 用作 |
|---|---|---|---|
| 存活 | `GET /v1/health` | 进程绑定监听器之后即可 | Kubernetes `livenessProbe` |
| 就绪 | `GET /v1/health/ready` | **WAL 完整重放且最后一次 flush 检查点已落盘**之后 | `readinessProbe`，避免流量打到重启中的节点 |

```sh
$ curl -sf http://127.0.0.1:8080/v1/health/ready && echo OK
{"status":"ready","wal_replayed":true,"indices":4,"uptime_s":17}
OK
```

## 配置热加载的边界

多数可调项通过 **SIGHUP** 热加载；**四个例外需要完整重启**（F-296）：端口、TLS 证书、`data_dir`、`cluster.enabled`。热加载它们会被拒绝，并在日志里给出明确错误。

```sh
sudo systemctl reload xerj        # 发 SIGHUP
journalctl -u xerj -n 10 --no-pager
# ... config reloaded: merge.max_merge_count 16 → 24
# ... config reloaded: limits.max_concurrent_searches 64 → 128
```

## 日志级别

日志走 stdout，结构化格式（**生产为 JSON，TTY 下为 pretty**），由 `RUST_LOG` 控制（F-297）：

```sh
RUST_LOG="info,xerj_vector=debug" xerj --config /etc/xerj/xerj.toml
RUST_LOG="warn" xerj --config /etc/xerj/xerj.toml

# 不重启临时提升运行中服务的级别
sudo systemctl set-environment RUST_LOG="info,xerj_query=debug"
sudo systemctl reload xerj
```

级别从低到高：`error → warn → info → debug → trace`，`info` 是生产默认。`XERJ_LOG` 优先于 `RUST_LOG`（`RUST_LOG` 仅在前者未设时被检查）。

## 容量规划：三个数字

取最大的那个来规划（F-298）：

| 维度 | 数字 | 备注 |
|---|---|---|
| **磁盘** | 约为 ES 的 **1/1.6**（实测 1.61× vs ES 8.13.4，随数据形状变化） | **另留 30% 余量给合并**——合并两个 5 GiB 的段需要临时 10 GiB 空闲 |
| **RAM** | 空闲基线约 **400 MB** | 向量字段按 `dims × 4` 字节叠加（**即便 scalar8 量化也不减常驻**，只改打分精度，#392）；memtable 按索引受 `flush_size_mb` 约束 |
| **CPU** | 每次 turbo-ingest 通道**每个 `turbo_parallel` worker 钉住一个核** | 繁忙节点至少留 **2 核**给查询路径 |

### 文件描述符

**每个打开的 segment 占 3 个文件描述符**（data / sidx / ids）——1000 段的索引约需 **3000 个 fd**（F-299）。systemd 单元里的 `LimitNOFILE=1048576` 绰绰有余；不用 systemd 就自己设 `ulimit -n 1048576`。

> 这条约束直接来自 [11 存储](/concepts/11-storage-compression-clustering.md) 的三文件结构——**架构决策会以运维约束的形式回来找你**。

## 备份与恢复

备份是**纯文件系统操作**：段写后不变、WAL 只追加，所以可以在服务运行时复制数据目录，恢复就是把目录复制回去（F-302）。

### 四种备份方式

**① 热备份（rsync）**

```sh
curl -sXPOST -H "Authorization: ApiKey $XERJ_API_KEY" \
  http://127.0.0.1:8080/v1/admin/flush
{"flushed_indices":4,"segments_written":4,"wal_checkpoint":12847}

rsync -aH --delete /var/lib/xerj/ backup.internal:/srv/backups/xerj/$(date +%F)/
```

先 flush 再 rsync（F-303）。因为段是内容寻址的，后续 rsync **只传新段**。这与 ZFS 快照、LVM 快照兼容；用 ZFS 时，flush 之后的快照本身就是真正的时间点一致的，不需要 rsync 这一步。

**② S3 / 对象存储**

```sh
curl -sXPOST -H "Authorization: ApiKey $XERJ_API_KEY" \
  -H "Content-Type: application/json" \
  http://127.0.0.1:8080/v1/admin/backup \
  -d '{
    "destination": "s3://my-backups/xerj/nightly",
    "credentials": {
      "endpoint": "https://s3.us-east-1.amazonaws.com",
      "access_key": "AKIA...",
      "secret_key": "..."
    },
    "flush_first": true
  }'
{"backup_id":"bk-2026-04-15T03-00-00Z","bytes":142857600,"duration_ms":8421}
```

`POST /v1/admin/backup` 把数据目录的完整副本**流式**传到任意 S3 兼容端点；**默认可增量**——只上传目标端还没有的段（F-304）。

**③ 单索引**

```sh
curl -sXPOST -H "Authorization: ApiKey $XERJ_API_KEY" \
  http://127.0.0.1:8080/v1/indices/events/flush
sudo tar czf events-$(date +%F).tar.gz -C /var/lib/xerj events
```

**④ 集群**

索引数据当前是节点本地的，所以集群备份就是**把单节点流程在每个节点上跑一遍**（F-307）。每个节点持有它所服务索引的完整副本，没有分片子集、没有 drain API 需要排序。

### 恢复

```sh
sudo systemctl stop xerj
sudo rm -rf /var/lib/xerj/*
sudo rsync -aH backup.internal:/srv/backups/xerj/2026-04-15/ /var/lib/xerj/
sudo chown -R xerj:xerj /var/lib/xerj
sudo systemctl start xerj
curl -sf http://127.0.0.1:8080/v1/health/ready
```

**无导入步骤**——启动时的 WAL 重放从磁盘上的文件重建 memtable 状态（F-305）。

## 升级

XERJ 遵循 SemVer（F-308）：补丁版本是可直接替换的；次版本可能引入向后兼容的 schema 字段；主版本可能改变磁盘格式，此时二进制随附一次性迁移工具。

### 单节点：四步

```sh
# 1. 备份
curl -sXPOST -H "Authorization: ApiKey $XERJ_API_KEY" \
  http://127.0.0.1:8080/v1/admin/backup \
  -d '{"destination":"s3://my-backups/xerj/pre-upgrade"}'

# 2. 取新版本并校验（解压与校验和链式绑定）
#    校验失败的包不会被解到运行节点上
curl -fsSLO "$base/$asset"; curl -fsSLO "$base/$asset.sha256"
want=$( { sha256sum "$asset" 2>/dev/null || shasum -a 256 "$asset"; } | cut -d ' ' -f 1 )
printf %s "$want" | LC_ALL=C grep -qE '^[0-9a-f]{64}$' \
  || { echo "no working SHA-256 tool — refusing to install an unverified $asset" >&2; exit 1; }
tr -d '\r' < "$asset.sha256" | LC_ALL=C grep -qxF -e "$want $asset" -e "$want *$asset" \
  || { echo "CHECKSUM MISMATCH for $asset — do not install it" >&2; exit 1; }
tar xzf "$asset"

# 3. 原地替换二进制
sudo systemctl stop xerj
sudo install -m 0755 "xerj-$ver-$target/xerj" /usr/local/bin/xerj
sudo systemctl start xerj

# 4. 确认版本
curl -s http://127.0.0.1:8080/v1/health | jq .version
```

停机时间等于 WAL 重放时间——低百万级活文档负载下通常是数秒（F-310）。

### 集群：必须全停全起

**线协议没有版本协商**：新线版本的节点与旧线版本的节点双向都无法通信（F-250）。因此集群升级是同一维护窗口内所有节点**全停全起**，不是滚动重启——没有 drain/activate API，也没有分片迁移需要排序。

因为索引数据是节点本地的，**每个节点的数据目录也是该节点自己的升级责任**——动二进制之前先按备份指南给每台机器做快照。

### 磁盘格式与回退

格式标记在 `<data_dir>/<index>/xerj_meta.json`（见 [11 存储](/concepts/11-storage-compression-clustering.md)）。回退就是重装上一个二进制（F-255）：对标记版本仍可被旧二进制读取的索引有效；标记已越过的索引在旧二进制下打不开，回退意味着**恢复升级前的备份**。

## 排障：症状 → 指标 → 日志 → 配置键

官方排障页给出 6 类症状，每类都给出这四件套（F-311）。这个结构本身就是最值得学的东西。

### ① 摄入吞吐在几小时后掉下来

**根因**：合并压力。段堆积得比合并器消化得快，memtable 正在 flush 出小段。

```sh
curl -s http://127.0.0.1:8080/v1/metrics | grep -E 'segment_count|merge_duration'
xerj_segment_count{index="logs"} 2847
xerj_merge_duration_seconds_count{index="logs"} 183
xerj_merge_duration_seconds_sum{index="logs"} 1847.2
```

**处置**：调大 `[storage] flush_size_mb`（让 flush 产出更大的起始段），调大 `[merge] max_merge_count`（让每轮消费更多段）——**盯 RSS**，合并峰值内存随它涨。快速 NVMe 上可用 `XERJ_MERGE_PARALLELISM` 提高并发。

> ⚠️ `[merge] max_concurrent` 与 `io_rate_mb_per_sec` **在这个场景下不会改变任何事**——它们被接受但未接线。

### ② 负载下查询超时

**根因**：并发查询太多，或单个查询太大。

```sh
journalctl -u xerj --since "10 min ago" | grep -E 'cancel|timeout|rejected'
# "query cancelled: max_query_memory_mb exceeded"    ← 内存超限
```

看 `active_searches` 是否顶到 `max_concurrent_searches`（F-316）。

**处置**：内存型 → 调大 `[limits] max_query_memory_mb`（512 → 1024，聚合密集负载可到 2048）；并发型 → 调大 `max_concurrent_searches`，**但先确认宿主机确实有余量**。

### ③ 节点 RAM 无限上涨

**根因**：大向量字段，或太多索引配着大的 `flush_size_mb`。

```sh
curl -s http://127.0.0.1:8080/v1/metrics | grep memory_usage
xerj_memory_usage_bytes 14200000000   # 14 GB 且在涨
```

**处置**：调小 `flush_size_mb`；若自动上限不适合本机，显式设 `[limits] max_process_memory_mb`。

> **量化今天不是内存解法**：`scalar8`（按字段用 `index_options` 打开）缩小的是 **kNN 打分工作集**，不是常驻内存（#392）；且节点级 `[vector] default_quantization` 键未接线。

### ④ 崩溃重启后出现 WAL 警告

**根因**：服务在写入中途被杀（断电、OOM kill、磁盘满），留下撕裂或损坏的 WAL 文件。

XERJ **自行修复 WAL，且从不因它拒绝启动**（F-312）：

| 情形 | 行为 | 日志 |
|---|---|---|
| 尾部撕裂 | 截断 | `WAL open: healed torn tail (crash/ENOSPC leftover) by truncation` |
| 文件中段损坏 | 冻结该文件，追加转到新分代 | `WAL open: mid-file corruption detected` |
| 帧不可读 | 重放时跳过 | `skipping corrupt WAL entry during replay` |

**处置**：**没有要跑的东西**——不存在人工 WAL 修复命令。撕裂或损坏区域的写入丢失，其前的全部重放。若在没有崩溃或断电的情况下出现这些警告，检查磁盘并提 issue。

### ⑤ 合并时磁盘满

**根因**：没有为合并暂存空间预留——合并两个 N 大小的段需要 2N 空闲直到合并完成（F-317）。

**处置**：调小 `[merge] max_segment_mb` 让单次合并保持更小，或腾磁盘。合并重试成功后旧段会被 unlink。

### ⑥ 集群 flapping（leader 每几秒换一次）

**根因**：节点间网络延迟高到心跳超时，Raft 于是发起新选举。

```sh
journalctl -u xerj --since "5 min ago" | grep xerj_cluster
INFO xerj_cluster::raft: Starting election node=10.0.0.12:9300 term=17
INFO xerj_cluster::raft: Higher term observed — stepping down to follower
```

**处置**：把 `[cluster] tick_ms` 从 50 提到 150 或 250，给心跳在慢网络上留余量。**永远不要把 tick 间隔降到最差节点对 RTT 以下**。抬完 tick 仍持续抖动是**缺陷而非调参问题**——带 `RUST_LOG=xerj_cluster=debug` 提 issue（leader 死亡抖动那一类是 #1168）（F-313）。

### 附：WAL tap 目标显示数据陈旧

tap 按 `[wal_tap] poll_interval_ms`（默认 500）轮询，每次最多发 `max_batch_docs` 条——**端到端延迟至少是一个轮询周期**，目标限流或短暂下线时更久（tap 会退避重试，绝不越过未投递的条目）。

```sh
curl -s -H "Authorization: ApiKey $XERJ_API_KEY" \
  http://127.0.0.1:8080/_xerj/wal_tap/_stats
```

看 gap 与重试退避，然后降 `poll_interval_ms` 或提 `max_batch_docs`（F-314）。

> **单节点上没有副本会陈旧**——搜索读活跃 memtable 加段，本地结果总是当前。

## 提 issue 前的诊断采集

没有单一的打包命令，五条命令读出报告需要的东西（F-315）：

```sh
mkdir xerj-report && cd xerj-report
export XERJ_API_KEY=$(sudo cat /var/lib/xerj/admin.key)
xerj --version > version.txt
curl -s http://127.0.0.1:8080/v1/health > health.json
curl -s -H "Authorization: ApiKey $XERJ_API_KEY" http://127.0.0.1:8080/v1/metrics > metrics.txt
curl -s -H "Authorization: ApiKey $XERJ_API_KEY" http://127.0.0.1:9200/_cluster/health > cluster-health.json
journalctl -u xerj --since "1 hour ago" --no-pager > xerj.log
```

> **把配置文件与 `admin.key` 排除在报告之外**——密钥是节点的管理员凭据。应**手工粘贴相关的 `[section]` 段**代替。

## 指标面

`GET /v1/metrics` 返回 Prometheus 文本格式（F-300）：

| 类别 | 指标 |
|---|---|
| 计数器 | `docs_indexed`、`queries_executed`、`bytes_written`、`bytes_read`、`rerank_requests`（按 applied / degraded / refused / failed 分）、`rerank_documents_judged`（**计费单位**）、`rerank_provider_tokens`（按 input / output 分） |
| 直方图 | `query_latency`、`index_latency`、`flush_duration`、`merge_duration`、`wal_write_latency` |
| 仪表 | `segment_count`、`doc_count`、`memory_usage`（RSS 字节）、`active_searches`、`wal_size_bytes` |

抓取配置：

```yaml
scrape_configs:
  - job_name: xerj
    metrics_path: /v1/metrics
    static_configs:
      - targets: ["xerj.internal:8080"]
    authorization:
      type: Bearer
      credentials: ${XERJ_API_KEY}
```

> 端点在 **8080**（原生端口），不是 9200。

## 相关概念

- [13 生产运维与排障](/concepts/13-operations-and-troubleshooting.md)：本文
- [11 存储、压缩与集群现状](/concepts/11-storage-compression-clustering.md)：三文件结构、集群现状、格式标记
- [12 配置与环境变量](/concepts/12-config-and-environment.md)：未接线键与热加载边界
- [07 ES 兼容与基准诚实性](/concepts/07-es-compat-and-benchmarks.md)：一致性与基准口径
- 事实来源：[第二轮事实清单](/references/facts-docs.md)
