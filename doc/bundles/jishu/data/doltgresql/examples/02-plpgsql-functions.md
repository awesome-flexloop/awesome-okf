---
okf_version: "0.2"
type: example
id: "examples-plpgsql-functions"
title: "plpgsql 函数编写与调用"
x-toml-ref: "../../../../../../../../.meta/toml/projects/awesome-okf-xs/doc/bundles/jishu/data/doltgresql/examples/02-plpgsql-functions.toml"
description: "CREATE FUNCTION ... LANGUAGE plpgsql 语法示例，覆盖基本函数、条件分支、循环、异常处理与集合返回函数"
tags: [doltgresql, example]
generated:
  at: "2026-09-09"
verified:
  at: "2026-09-09"
  by: process:seven-concepts-v
  status: stable
stale_after: "2027-03-09"
sources:
  - path: "server/plpgsql/interpreter_operation.go"
    type: source-code
    title: "server/plpgsql/interpreter_operation.go"
    distance: 1
  - path: "server/plpgsql/interpreter_logic.go"
    type: source-code
    title: "server/plpgsql/interpreter_logic.go"
    distance: 1
  - path: "server/node/create_function.go"
    type: source-code
    title: "server/node/create_function.go"
    distance: 1
  - id: plpgsql-source
    resource: /references/source.md
    title: "DoltgreSQL 源码事实登记"
---
# plpgsql 函数编写与调用

> 本文档展示 DoltgreSQL 中 plpgsql 存储过程的编写、执行与 OpCode 运行机制，覆盖条件分支、循环、异常处理与集合返回函数。

---

## 示例 1：基本函数（简单返回值）

### 创建函数

```sql
-- 简单标量函数（F-118：RoutineParam 含 Mode/Name/Type/HasDefault/Default）
CREATE OR REPLACE FUNCTION public.add_numbers(a integer, b integer)
RETURNS integer
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN a + b;
END;
$$;

-- 调用函数
SELECT public.add_numbers(10, 20) AS result;
-- result: 30
```

### 源码锚点

| 步骤 | 源码位置 | 说明 |
|------|---------|------|
| 函数创建 | [server/node/create_function.go L1](../../../../../external/dao/action/DoltHub/doltgresql/server/node/create_function.go) | `CreateFunction` 十字段结构体（F-119） |
| RoutineParam | [server/node/create_function.go L30](../../../../../external/dao/action/DoltHub/doltgresql/server/node/create_function.go) | Mode/Name/Type/HasDefault/Default 五字段（F-118） |
| 函数注册 | [server/types/function_registry.go L1](../../../../../external/dao/action/DoltHub/doltgresql/server/types/function_registry.go) | `globalFunctionRegistry` 全局单例（F-116、F-117） |

---

## 示例 2：条件分支（IF/CASE）

### IF 分支

```sql
-- IF/ELSIF/ELSE 条件分支（F-106：If(8) 操作码）
CREATE OR REPLACE FUNCTION public.classify_grade(score integer)
RETURNS text
LANGUAGE plpgsql
AS $$
BEGIN
    IF score >= 90 THEN
        RETURN 'A';
    ELSIF score >= 80 THEN
        RETURN 'B';
    ELSIF score >= 70 THEN
        RETURN 'C';
    ELSIF score >= 60 THEN
        RETURN 'D';
    ELSE
        RETURN 'F';
    END IF;
END;
$$;

SELECT public.classify_grade(85) AS grade;
-- grade: B
```

### CASE 表达式

```sql
-- CASE 表达式（F-106：Case(2) 操作码）
CREATE OR REPLACE FUNCTION public.get_status_description(status_code integer)
RETURNS text
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN CASE status_code
        WHEN 0 THEN 'Inactive'
        WHEN 1 THEN 'Active'
        WHEN 2 THEN 'Pending'
        WHEN 3 THEN 'Suspended'
        ELSE 'Unknown'
    END;
END;
$$;

SELECT public.get_status_description(1) AS description;
-- description: Active
```

### 源码锚点

| 操作码 | 说明 | 源码 |
|--------|------|------|
| `If(8)` | 条件分支 | [interpreter_operation.go L10](../../../../../external/dao/action/DoltHub/doltgresql/server/plpgsql/interpreter_operation.go) |
| `Case(2)` | CASE 表达式 | [interpreter_operation.go L10](../../../../../external/dao/action/DoltHub/doltgresql/server/plpgsql/interpreter_operation.go) |
| `Goto(7)` | 跳转指令 | [interpreter_operation.go L10](../../../../../external/dao/action/DoltHub/doltgresql/server/plpgsql/interpreter_operation.go) |
| `ScopeBegin(13)` / `ScopeEnd(14)` | 作用域管理 | [interpreter_operation.go L10](../../../../../external/dao/action/DoltHub/doltgresql/server/plpgsql/interpreter_operation.go) |

---

## 示例 3：循环（FOR/WHILE）

### FOR 循环遍历

```sql
-- FOR 循环（F-109：ForQueryInit(18)/ForQueryNext(19) 操作码）
CREATE OR REPLACE FUNCTION public.sum_range(start_val integer, end_val integer)
RETURNS integer
LANGUAGE plpgsql
AS $$
DECLARE
    total integer := 0;
    i integer;
BEGIN
    FOR i IN start_val..end_val LOOP
        total := total + i;
    END LOOP;
    RETURN total;
END;
$$;

SELECT public.sum_range(1, 100) AS total;
-- total: 5050
```

### WHILE 循环

```sql
-- WHILE 循环
CREATE OR REPLACE FUNCTION public.factorial(n integer)
RETURNS integer
LANGUAGE plpgsql
AS $$
DECLARE
    result integer := 1;
    counter integer := 1;
BEGIN
    WHILE counter <= n LOOP
        result := result * counter;
        counter := counter + 1;
    END LOOP;
    RETURN result;
END;
$$;

SELECT public.factorial(5) AS factorial_result;
-- factorial_result: 120
```

### 源码锚点

| 操作码 | 说明 | 源码 |
|--------|------|------|
| `ForQueryInit(18)` | FOR 循环初始化 | [interpreter_operation.go L10](../../../../../external/dao/action/DoltHub/doltgresql/server/plpgsql/interpreter_operation.go) |
| `ForQueryNext(19)` | FOR 循环迭代 | [interpreter_operation.go L10](../../../../../external/dao/action/DoltHub/doltgresql/server/plpgsql/interpreter_operation.go) |
| `Assign(1)` | 变量赋值 | [interpreter_operation.go L10](../../../../../external/dao/action/DoltHub/doltgresql/server/plpgsql/interpreter_operation.go) |
| `Get(6)` | 变量读取 | [interpreter_operation.go L10](../../../../../external/dao/action/DoltHub/doltgresql/server/plpgsql/interpreter_operation.go) |

---

## 示例 4：游标与记录

### SELECT INTO 获取单行

```sql
-- SELECT INTO（F-107：SelectInto(15) 操作码）
CREATE OR REPLACE FUNCTION public.get_employee_name(emp_id integer)
RETURNS text
LANGUAGE plpgsql
AS $$
DECLARE
    emp_name text;
BEGIN
    SELECT name INTO emp_name
    FROM employees
    WHERE id = emp_id;

    IF emp_name IS NULL THEN
        RETURN 'Not found';
    END IF;
    RETURN emp_name;
END;
$$;

SELECT public.get_employee_name(1) AS employee_name;
```

### 游标遍历多行

```sql
-- 游标遍历
CREATE OR REPLACE FUNCTION public.sum_salaries()
RETURNS integer
LANGUAGE plpgsql
AS $$
DECLARE
    total integer := 0;
    emp RECORD;
    cur CURSOR FOR SELECT salary FROM employees;
BEGIN
    OPEN cur;
    LOOP
        FETCH cur INTO emp;
        EXIT WHEN NOT FOUND;
        total := total + emp.salary;
    END LOOP;
    CLOSE cur;
    RETURN total;
END;
$$;

SELECT public.sum_salaries() AS total_salaries;
```

---

## 示例 5：异常处理（EXCEPTION）

### 基本异常处理

```sql
-- 异常处理（F-111：Exception(4)/Raise(11) 操作码）
CREATE OR REPLACE FUNCTION public.safe_divide(a integer, b integer)
RETURNS numeric
LANGUAGE plpgsql
AS $$
DECLARE
    result numeric;
BEGIN
    result := a / b;
    RETURN result;
EXCEPTION
    WHEN division_by_zero THEN
        RAISE NOTICE 'Attempted to divide by zero!';
        RETURN NULL;
    WHEN others THEN
        RAISE NOTICE 'Unexpected error: %', SQLERRM;
        RETURN NULL;
END;
$$;

SELECT public.safe_divide(10, 0) AS result;
-- result: NULL
-- NOTICE: Attempted to divide by zero!
```

### 带错误信息的异常抛出

```sql
-- RAISE 抛出异常
CREATE OR REPLACE FUNCTION public.create_employee(emp_name text, dept text)
RETURNS integer
LANGUAGE plpgsql
AS $$
DECLARE
    new_id integer;
BEGIN
    IF emp_name IS NULL OR emp_name = '' THEN
        RAISE EXCEPTION 'Employee name cannot be empty';
    END IF;

    IF dept IS NULL OR dept = '' THEN
        RAISE EXCEPTION 'Department cannot be empty';
    END IF;

    INSERT INTO employees (name, department)
    VALUES (emp_name, dept)
    RETURNING id INTO new_id;

    RETURN new_id;
END;
$$;

-- 触发异常
SELECT public.create_employee('', 'Engineering');
-- ERROR: Employee name cannot be empty
```

---

## 示例 6：集合返回函数（SRF）

### 返回表

```sql
-- 集合返回函数（F-115：IsSRF() 标识 SRF）
CREATE OR REPLACE FUNCTION public.get_employees_by_dept(dept text)
RETURNS TABLE(
    id integer,
    name text,
    salary numeric
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT e.id, e.name, e.salary
    FROM employees e
    WHERE e.department = dept;
END;
$$;

SELECT * FROM public.get_employees_by_dept('Engineering');
```

### 返回多个结果集

```sql
-- 返回多个记录集
CREATE OR REPLACE FUNCTION public.get_department_stats()
RETURNS SETOF record
LANGUAGE plpgsql
AS $$
DECLARE
    dept_record RECORD;
BEGIN
    FOR dept_record IN
        SELECT department, COUNT(*) AS emp_count, AVG(salary) AS avg_salary
        FROM employees
        GROUP BY department
    LOOP
        RETURN NEXT dept_record;
    END LOOP;
END;
$$;

SELECT * FROM public.get_department_stats();
```

### 源码锚点

| 概念 | 源码位置 | 说明 |
|------|---------|------|
| InterpretedFunction 接口 | [server/plpgsql/interpreter_logic.go L1](../../../../../external/dao/action/DoltHub/doltgresql/server/plpgsql/interpreter_logic.go) | 10 个方法：ApplyBindings/GetAllNames/QueryMultiReturn 等（F-113） |
| IsSRF() | [server/plpgsql/interpreter_logic.go L30](../../../../../external/dao/action/DoltHub/doltgresql/server/plpgsql/interpreter_logic.go) | 标识函数是否为集合返回函数（F-115） |
| Call() | [server/plpgsql/interpreter_logic.go L50](../../../../../external/dao/action/DoltHub/doltgresql/server/plpgsql/interpreter_logic.go) | 处理普通函数调用（F-114） |
| TriggerCall() | [server/plpgsql/interpreter_logic.go L70](../../../../../external/dao/action/DoltHub/doltgresql/server/plpgsql/interpreter_logic.go) | 处理触发器调用（F-114） |

---

## 示例 7：触发器函数

```sql
-- 触发器函数（F-114：TriggerCall() 处理触发器调用）
CREATE OR REPLACE FUNCTION public.log_employee_change()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        INSERT INTO employee_audit (action, emp_id, old_name, new_name, change_time)
        VALUES ('INSERT', NEW.id, NULL, NEW.name, NOW());
        RETURN NEW;
    ELSIF TG_OP = 'UPDATE' THEN
        INSERT INTO employee_audit (action, emp_id, old_name, new_name, change_time)
        VALUES ('UPDATE', NEW.id, OLD.name, NEW.name, NOW());
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        INSERT INTO employee_audit (action, emp_id, old_name, new_name, change_time)
        VALUES ('DELETE', OLD.id, OLD.name, NULL, NOW());
        RETURN OLD;
    END IF;
END;
$$;

-- 绑定触发器
CREATE TRIGGER employee_audit_trigger
AFTER INSERT OR UPDATE OR DELETE ON employees
FOR EACH ROW EXECUTE FUNCTION public.log_employee_change();
```

---

## OpCode 操作码速查

DoltgreSQL plpgsql 解释器支持 **23 种操作码**（F-105），按功能分类：

| 类别 | 操作码 | 枚举值 | 说明 |
|------|--------|--------|------|
| 变量操作 | `Alias` | 0 | 变量别名 |
| 变量操作 | `Assign` | 1 | 变量赋值 |
| 控制流 | `Case` | 2 | CASE 表达式 |
| 数据操作 | `DeleteInto` | 3 | DELETE ... INTO |
| 异常 | `Exception` | 4 | 异常处理块 |
| 动态 SQL | `Execute` | 5 | EXECUTE 动态 SQL |
| 变量操作 | `Get` | 6 | 读取变量值 |
| 控制流 | `Goto` | 7 | 跳转到标签 |
| 控制流 | `If` | 8 | IF 条件分支 |
| 数据操作 | `InsertInto` | 9 | INSERT ... INTO |
| 返回 | `Perform` | 10 | PERFORM（忽略结果） |
| 异常 | `Raise` | 11 | RAISE 抛出异常 |
| 返回 | `Return` | 12 | RETURN（标量） |
| 控制流 | `ScopeBegin` | 13 | 作用域开始 |
| 控制流 | `ScopeEnd` | 14 | 作用域结束 |
| 数据操作 | `SelectInto` | 15 | SELECT ... INTO |
| 数据操作 | `UpdateInto` | 16 | UPDATE ... INTO |
| 返回 | `ReturnQuery` | 17 | RETURN QUERY |
| 循环 | `ForQueryInit` | 18 | FOR 循环初始化 |
| 循环 | `ForQueryNext` | 19 | FOR 循环迭代 |
| 变量操作 | `DeclareRecord` | 20 | 声明记录变量 |
| 动态 SQL | `ExecuteInto` | 21 | EXECUTE ... INTO |
| 未知 | `Unknown` | 22 | 未实现操作码 |

---

## 相关概念

* [plpgsql 解释器与函数系统](/concepts/05-plpgsql-and-functions.md) — OpCode 23 种操作码与 InterpretedFunction 接口
* [类型系统与 pg_type](/concepts/04-type-system.md) — 函数参数与返回类型系统

> **注意**：当前环境未安装 `doltgresql` 二进制，本文档以源码锚点形式呈现，供查阅实现细节。
