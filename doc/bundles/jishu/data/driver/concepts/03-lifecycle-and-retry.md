---
type: Concept
title: 连接生命周期与 BackOff 重试
description: "Driver v2 的连接生命周期：Connector 持有共享 SqlEngine、Lazy Open + 进程级 semaphore、BackOff 重试模型（nbs.ErrDatabaseLocked / os.ErrDeadlineExceeded）、IsValid=false 会话复用策略。F-009~F-011、F-016。"
tags: [driver, dolt, lifecycle, retry, backoff]
generated: { by: "process:source-code-to-okf-wiki", at: "2026-09-10" }
verified: { by: "process:seven-concepts-v", at: "2026-09-10" }
status: stable
stale_after: "2027-03-31"
sources:
  - id: driver-repo
    resource: https://github.com/dolthub/driver
    title: dolthub/driver（官方仓库）
  - id: driver-local
    resource: "本地克隆（tag v2.2.0-18，commit 61ccedb7035925b3e4a5f91be6bd68b100e3b1e7）"
    title: driver 源码逐文件精读
---

# 连接生命周期与 BackOff 重试

> **对应 F 编号**：F-009 ~ F-011、F-016

## 共享 SqlEngine 与 Lazy Open（F-009）

[con](file:///d:/spaces/SpecWeave/external/dao/action/DoltHub/driver/connector.go#L75-L83) 在第一次 `Connect()` 时打开引擎，此后所有连接共享同一实例：

```go
type Connector struct {
    cfg    Config
    driver *doltDriver

    mu     sync.Mutex
    se     *engine.SqlEngine   // 共享引擎，首次 Connect 时初始化
    openCh chan struct{}       // 等待引擎打开的 channel
    closed bool
}
```

`getOrOpenEngine()` 使用**双重检查锁定**模式（[get](file:///d:/spaces/SpecWeave/external/dao/action/DoltHub/driver/connector.go#L182-L230)）：

```
Connect() 被调用
    │
    ├─ se != nil → 直接返回已有引擎
    │
    └─ se == nil
            ├─ openCh != nil → 等待已有 open 完成（loop）
            └─ openCh == nil → 成为 opener，发起 openEngineWithRetry()
                               完成后关闭 openCh，通知等待者
```

进程级 semaphore `openSem`（[o](file:///d:/spaces/SpecWeave/external/dao/action/DoltHub/driver/driver.go#L60-L64)）确保同一进程中同时只有一个 `openSqlEngine` 在飞行：

```go
var openSem = make(chan struct{}, 1)  // 容量 1，进程级信号量
```

原因：GMS（go-mysql-server）在引擎初始化阶段使用全局可变状态（系统变量、状态变量），并发访问不安全。

## BackOff 重试模型（F-010）

[ope](file:///d:/spaces/SpecWeave/external/dao/action/DoltHub/driver/connector.go#L232-L301) 支持通过 `Config.BackOff` 启用引擎打开时的重试：

```go
func (c *Connector) openEngineWithRetry(ctx context.Context) (*engine.SqlEngine, error) {
    // ...
    if c.cfg.BackOff == nil {
        return open(ctx)           // 无重试，单次尝试
    }
    // BackOff 是 stateful 的，使用前必须 Reset
    c.cfg.BackOff.Reset()
    bo := backoff.WithContext(c.cfg.BackOff, ctx)

    var lastErr error
    var se *engine.SqlEngine
    op := func() error {
        s, err := open(ctx)
        if err == nil {
            se = s
            return nil
        }
        lastErr = err
        if isRetryableOpenErr(err) {
            return err       // 可重试：返回 err，backoff 会延迟后重试
        }
        return backoff.Permanent(err)  // 不可重试：立即终止
    }
    backoff.Retry(op, bo)
    return se, nil
}
```

**可重试错误**（[is](file:///d:/spaces/SpecWeave/external/dao/action/DoltHub/driver/retryable_open_err.go)）：

| 错误类型 | 说明 |
|---------|------|
| `nbs.ErrDatabaseLocked` | NBS（Noms Block Store）锁冲突，通常是其他进程正在写同一 Dolt repo |
| `os.ErrDeadlineExceeded` | journal lock timeout，同上 |

不可重试的错误（如路径不存在、权限错误）会通过 `backoff.Permanent()` 立即终止。

## 指标上报（F-011）

嵌入式驱动每 24 小时向 DoltHub 发送一次匿名指标：

```go
const metricsInterval = time.Hour * 24
const metricsDisabledEnvKey = "DOLT_METRICS_DISABLED"

func emitUsageEvent(ctx context.Context, mrEnv *env.MultiRepoEnv) {
    if metricsDisabled.Load() || !metricsSent.CompareAndSwap(false, true) {
        return  // 已发送过或环境变量禁用
    }
    // 通过 gRPC 发送：eventsapi.AppID_APP_DOLT_EMBEDDED
}
```

禁用方式：设置环境变量 `DOLT_METRICS_DISABLED=1`。

## IsValid=false 会话策略（F-016）

[d](file:///d:/spaces/SpecWeave/external/dao/action/DoltHub/driver/conn.go#L235-L249) 采用**不复用 session** 的策略：

```go
func (d *DoltConn) IsValid() bool {
    return false  // 永远返回 false
}

func (d *DoltConn) ResetSession(ctx context.Context) error {
    return driver.ErrBadConn  // 强制重新建立连接
}
```

原因（源码注释）：`dsess.DoltSession` 包含大量内存状态（不同数据库的工作集头、分支指针等），复用的复杂度和出错风险高于直接新建。

对 `sql.DB` 连接池的影响：每次从池中取出的连接都会触发 `ResetSession` → `ErrBadConn` → 丢弃重连，因此**连接池的 maxIdleTime 和 maxLifetime 设置对此 driver 无效**，建议按需控制池大小。
