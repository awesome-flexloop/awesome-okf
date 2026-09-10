---
type: Concept
title: 查询执行与多语句支持
description: "Driver v2 的查询执行路径：串行查询（beginQuery/endQuery）、Transaction 模型、多语句 QuerySplitter（RuneStack 嵌套感知）、rows/result 实现。F-013~F-015、F-017~F-021。"
tags: [driver, dolt, query, transaction, multi-statement]
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

# 查询执行与多语句支持

> **对应 F 编号**：F-013 ~ F-015、F-017 ~ F-021

## 串行查询模型（F-013、F-014）

[con](file:///d:/spaces/SpecWeave/external/dao/action/DoltHub/driver/conn.go#L41-L51) 维护一个 `activeQueryCtx` 字段，强制串行执行：

```go
func (d *DoltConn) beginQuery(ctx context.Context, query string) (*gms.Context, error) {
    res := d.gmsCtx.WithContext(ctx)
    gms.WithPid(globalQueryPid.Add(1))(res)

    // 如果已有活跃查询，先杀掉它
    if d.activeQueryCtx != nil {
        if res.ProcessList != nil {
            res.ProcessList.EndQuery(d.activeQueryCtx)
        }
        d.activeQueryCtx = nil
    }

    // 注册新查询
    res, err = res.ProcessList.BeginQuery(res, query)
    d.activeQueryCtx = res
    return res, err
}
```

所有操作（Prepare、ExecContext、QueryContext）统一经过 `queryWithBindings()`（[que](file:///d:/spaces/SpecWeave/external/dao/action/DoltHub/driver/conn.go#L251-L268)）：

```go
func (d *DoltConn) queryWithBindings(ctx context.Context, query string, bindings map[string]sqlparser.Expr) (*gms.Context, gms.Schema, gms.RowIter, error) {
    queryCtx, err := d.beginQuery(ctx, query)
    if err != nil { return nil, nil, nil, err }

    queryCtx.SetQueryTime(time.Now())
    sch, itr, _, err := d.se.QueryWithBindings(queryCtx, query, nil, bindings, nil)
    if err != nil {
        d.endQuery(queryCtx)
        return nil, nil, nil, translateError(err)
    }

    // 用 callbackOnCloseIter 包装，确保 Close 时结束查询
    return queryCtx, sch, &callbackOnCloseIter{iter: itr, callback: d.endQuery}, nil
}
```

## Transaction 支持（F-015）

[b](file:///d:/spaces/SpecWeave/external/dao/action/DoltHub/driver/conn.go#L167-L191) 仅支持 `LevelSerializable` 和 `LevelDefault` 两种隔离级别：

```go
func (d *DoltConn) BeginTx(ctx context.Context, opts driver.TxOptions) (driver.Tx, error) {
    if opts.Isolation != driver.IsolationLevel(sql.LevelSerializable) &&
       opts.Isolation != driver.IsolationLevel(sql.LevelDefault) {
        return nil, fmt.Errorf("isolation level not supported '%d'", opts.Isolation)
    }

    queryCtx, _, iter, err := d.queryWithBindings(ctx, "begin", nil)
    if err != nil { return nil, err }
    iter.Close(queryCtx)

    return &doltTx{ctx: d.gmsCtx.Context, conn: d}, nil
}
```

[dol](file:///d:/spaces/SpecWeave/external/dao/action/DoltHub/driver/transaction.go) 仅包装 `context.Context` + `*DoltConn`，Commit/Rollback 通过执行 SQL 语句实现：

```go
type doltTx struct {
    ctx  context.Context
    conn *DoltConn
}

func (t *doltTx) Commit() error {
    _, _, iter, err := t.conn.queryWithBindings(t.ctx, "commit", nil)
    iter.Close(nil)
    return err
}

func (t *doltTx) Rollback() error {
    _, _, iter, err := t.conn.queryWithBindings(t.ctx, "rollback", nil)
    iter.Close(nil)
    return err
}
```

**重要**：doltTx 继承的是连接的原始 Context（`d.gmsCtx.Context`），而非 BeginTx 传入的 ctx——这样用户取消 BeginTx 的 ctx 不会影响后续的 Commit/Rollback。

## 多语句支持：QuerySplitter（F-021）

[d](file:///d:/spaces/SpecWeave/external/dao/action/DoltHub/driver/query_splitter.go) 使用 `RuneStack` 追踪括号/引号/反引号的嵌套深度，只在最外层按 `;` 拆分：

```go
var openRunes = map[rune]bool{'(': true, '"': true, '\'': true, '`': true}

func parseNext(queries string) (int, error) {
    openStack := NewRuneStack()
    var prevCh rune
    for pos, ch := range queries {
        lastOpen := openStack.Peek()
        switch lastOpen {
        case 0:
            if openRunes[ch] {
                openStack.Push(ch)
            } else if ch == ';' {
                return pos + 1, nil  // 找到拆分点
            }
        case '"', '\'', '`':
            if ch == lastOpen && prevCh != '\\' {
                openStack.Pop()  // 匹配的引号，退出嵌套
            }
        case '(':
            if ch == ')' {
                openStack.Pop()
            } else if openRunes[ch] {
                openStack.Push(ch)
            }
        }
        prevCh = ch
    }
    return len(queries), nil
}
```

示例：`SELECT * FROM t WHERE name = 'a;b'; SELECT * FROM u` → 正确拆分为两条语句，中间的 `;` 在引号内不被拆分。

**注意**：`multistatements=true` 时，`Prepare()` 返回 `doltMultiStmt`，由 GMS 的 `NewMysqlParser()` 在解析阶段拆分（[pre](file:///d:/spaces/SpecWeave/external/dao/action/DoltHub/driver/conn.go#L77-L100)），而非 QuerySplitter——QuerySplitter 作为备用拆分器存在于代码中。

## Rows 与 Result 实现（F-018、F-019）

[dol](file:///d:/spaces/SpecWeave/external/dao/action/DoltHub/driver/rows.go) 是 GMS RowIter 的适配器：

```go
type doltRows struct {
    sch     gms.Schema
    rowIter gms.RowIter
    drained bool
}
```

`Next()` 处理多种 Go 类型：`types.Value`、`driver.Valuer`、`types.GeometryValue`、`EnumType`、`SetType`。`Close()` 会 drain 剩余行以确保 DML 结果集被完全消费。

[dol](file:///d:/spaces/SpecWeave/external/dao/action/DoltHub/driver/result.go) 通过遍历 RowIter 累加影响行数：

```go
type doltResult struct {
    affected int64
    last     int64
}

func newResult(queryCtx *gms.Context, sch gms.Schema, rowIter gms.RowIter) (driver.Result, error) {
    // 遍历所有行，累加 RowsAffected 和 InsertID
}
```

## 完整查询流程

```
db.QueryContext(ctx, "SELECT * FROM t")
    → DoltConn.QueryContext()
        → DoltConn.Prepare("SELECT * FROM t")
            → doltStmt{conn: d, query: "SELECT * FROM t"}
        → stmt.QueryContext(ctx, args)
            → queryWithBindings(ctx, "SELECT * FROM t", nil)
                → beginQuery(ctx, "SELECT * FROM t")
                → se.QueryWithBindings(gmsCtx, query, nil, nil, nil)
                → callbackOnCloseIter{iter: rowIter, callback: endQuery}
            → doltRows{sch, rowIter}
    用户调用 rows.Next() 逐行读取
    用户调用 rows.Close() → callbackOnCloseIter.Close() → endQuery()
```
