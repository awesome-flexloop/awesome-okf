---
type: Reference
title: 规则与变量求值 API 参考
description: src/eval_env.h/cc 源码参考——Rule、BindingEnv、EvalString、Env 完整 API
tags: [reference, api, rule, binding, eval, variable, environment, c++]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T00:00:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: ninja-eval-env
    title: src/eval_env.h
    path: external/libs/tools/ninja/src/eval_env.h
  - id: ninja-eval-env-cc
    title: src/eval_env.cc
    path: external/libs/tools/ninja/src/eval_env.cc
---

# 规则与变量求值 API 参考

> 信源文件：eval_env.h、eval_env.cc

本文档记录 Ninja 规则定义、变量绑定环境和变量字符串求值的完整 API。

---

## Env 接口

**头文件**：`src/eval_env.h`

变量查找作用域的抽象接口。

```cpp
struct Env {
  virtual ~Env() {}
  virtual std::string LookupVariable(StringPiece var) = 0;
};
```

| 方法 | 返回类型 | 说明 |
|------|---------|------|
| `LookupVariable(StringPiece var)` | `string` | 查找变量值，纯虚函数 |

BindingEnv 是 Env 的主要实现。

---

## Rule 结构体

**头文件**：`src/eval_env.h`

Rule 表示一条可调用的构建命令及其关联元数据（描述、依赖文件、池等）。与旧版 Ninja 不同，当前版本的 Rule 使用键值绑定映射（`bindings_`）存储所有属性，而非独立的 C++ 成员字段。

### 构造函数

```cpp
explicit Rule(const std::string& name);
```

- `name`：规则名称

### 静态工厂方法

| 方法 | 返回类型 | 说明 |
|------|---------|------|
| `Phony()` | `unique_ptr<Rule>` | 创建 phony 规则（不执行实际命令） |

### 方法

| 方法 | 返回类型 | 说明 |
|------|---------|------|
| `name() const` | `const string&` | 返回规则名称 |
| `IsPhony() const` | `bool` | 是否为 phony 规则 |
| `AddBinding(const string& key, const EvalString& val)` | `void` | 添加键值绑定（由 ManifestParser 调用） |
| `GetBinding(StringPiece key) const` | `const EvalString*` | 按键查找绑定值，未找到返回 NULL |
| `IsReservedBinding(StringPiece var)` | `static bool` | 判断变量名是否为保留绑定名 |

### 保留绑定名

`IsReservedBinding()` 识别以下保留变量名：

| 绑定名 | 类型 | 说明 |
|--------|------|------|
| `command` | EvalString | **必需**。构建命令字符串 |
| `depfile` | EvalString | 编译器生成的依赖文件路径（如 `.d` 文件） |
| `dyndep` | EvalString | 动态依赖文件路径（ninja 1.10+） |
| `description` | EvalString | 构建时显示的描述信息（替代命令显示） |
| `deps` | string | 头依赖模式：空/`"gcc"`/`"msvc"` |
| `generator` | bool | 是否为生成器规则（clean 默认不清理） |
| `pool` | string | 执行池名称（如 `"console"`） |
| `restat` | bool | 命令执行后是否重新 stat 输出 |
| `rspfile` | EvalString | 响应文件路径（用于超长命令行） |
| `rspfile_content` | EvalString | 响应文件内容 |
| `msvc_deps_prefix` | string | MSVC `/showIncludes` 输出前缀 |

### deps 绑定值

`deps` 绑定的值决定头依赖的处理方式（字符串类型，非枚举）：

| 值 | 说明 |
|----|------|
| 空 | 不使用 depslog 缓存头依赖 |
| `"gcc"` | 使用 gcc/clang 的 `-MMD`/`-MF` 生成的 depfile |
| `"msvc"` | 使用 MSVC 的 `/showIncludes` 输出提取头依赖 |

构建代码中通过 `edge->GetBinding("deps")` 获取字符串后比较：

```cpp
string deps_type = edge->GetBinding("deps");
if (deps_type == "msvc") {
  // MSVC 依赖提取逻辑
} else if (deps_type == "gcc") {
  // GCC depfile 解析逻辑
}
```

### 私有成员

| 成员 | 类型 | 说明 |
|------|------|------|
| `name_` | `string` | 规则名称 |
| `bindings_` | `Bindings`（`map<string, EvalString, StringPieceLess>`） | 键值绑定映射 |
| `phony_` | `bool` | 是否为 phony 规则 |

ManifestParser 被声明为 friend，可直接填充 `bindings_`。

---

## BindingEnv 结构体

**头文件**：`src/eval_env.h`

BindingEnv 是包含变量到值映射及父作用域指针的环境，继承自 Env 接口。每个 Edge 持有一个 BindingEnv，规则查找和变量求值通过作用域链进行。

### 构造函数

```cpp
BindingEnv();                               // 无父作用域（顶层环境）
explicit BindingEnv(BindingEnv* parent);   // 以 parent 为父作用域
```

### 变量查找顺序（LookupWithFallback）

Edge 的变量查找按以下顺序进行：
1. Edge 自身绑定（`edge->env_` 中的 bindings_）
2. Rule 上的绑定，在 Edge 作用域中展开求值
3. Edge 环境的父作用域（`edge->env_->parent_`）

### 方法

| 方法 | 返回类型 | 说明 |
|------|---------|------|
| `LookupVariable(StringPiece var)` | `string` | 查找变量值（override Env）；先查当前作用域，未找到递归查父作用域 |
| `AddRule(unique_ptr<const Rule> rule)` | `void` | 向当前作用域添加规则 |
| `LookupRule(StringPiece rule_name)` | `const Rule*` | 查找规则（当前作用域+父作用域链） |
| `LookupRuleCurrentScope(StringPiece rule_name)` | `const Rule*` | 仅在当前作用域查找规则 |
| `GetRules() const` | `const map<string, unique_ptr<const Rule>, StringPieceLess>&` | 获取当前作用域所有规则 |
| `AddBinding(const string& key, StringPiece val)` | `void` | 添加字符串变量绑定（值为已求值的字符串） |
| `LookupWithFallback(StringPiece var, const EvalString* eval, Env* env)` | `string` | 三阶段查找：当前绑定 → 规则求值 → 父作用域 |

### 私有成员

| 成员 | 类型 | 说明 |
|------|------|------|
| `bindings_` | `map<string, string, StringPieceLess>` | 当前作用域的变量→已求值字符串映射 |
| `rules_` | `map<string, unique_ptr<const Rule>, StringPieceLess>` | 当前作用域的规则映射 |
| `parent_` | `BindingEnv*` | 父作用域指针（NULL 表示顶层） |

### 注意

- Rule 上的 `AddBinding()` 接受 `EvalString`（未求值的含变量引用字符串），而 BindingEnv 上的 `AddBinding()` 接受 `StringPiece`（已求值的纯字符串）。
- `subninja` 指令创建新的 BindingEnv（以当前 env 为 parent），形成作用域嵌套。
- `include` 指令复用当前 BindingEnv，不创建新作用域。

---

## EvalString 结构体

**头文件**：`src/eval_env.h`

EvalString 是标记化后的字符串，包含变量引用（如 `$in`、`$out`、`${cflags}`）。可相对于 Env 求值得到最终字符串。

### TokenType 枚举

```cpp
enum TokenType { RAW, SPECIAL };
```

- `RAW`：原始文本
- `SPECIAL`：变量引用（`$` 开头的变量名）

### 方法

| 方法 | 返回类型 | 说明 |
|------|---------|------|
| `Evaluate(Env* env) const` | `string` | 在指定环境中展开变量，返回求值后的字符串 |
| `Unparse() const` | `string` | 返回未展开的原始字符串（含 `$` 变量引用） |
| `Clear()` | `void` | 清空解析结果 |
| `empty() const` | `bool` | 是否为空 |
| `AddText(StringPiece text)` | `void` | 添加原始文本片段 |
| `AddSpecial(StringPiece text)` | `void` | 添加变量引用片段 |
| `Serialize() const` | `string` | 生成人类可读的解析状态表示（测试用） |

### 内部存储优化

| 成员 | 类型 | 说明 |
|------|------|------|
| `parsed_` | `TokenList`（`vector<pair<string, TokenType>>`） | 标记列表（多 token 时使用） |
| `single_token_` | `string` | 单 RAW token 优化：若只有一个原始文本片段，直接存储在此避免 vector 分配；`parsed_` 非空时忽略此值 |

当字符串仅包含单一 RAW 片段（无变量引用）时，Ninja 不分配 TokenList vector，直接将文本存入 `single_token_`，这是一个常见场景优化。

### 解析方式

EvalString 不自行解析输入文本，而是由 Lexer 填充：

- `Lexer::ReadPath()` → `ReadEvalString(eval, true, err)`：读取路径，在分隔符（空格、换行、`:`、`|`）处停止
- `Lexer::ReadVarValue()` → `ReadEvalString(eval, false, err)`：读取变量值，在换行处停止

Lexer 扫描 `$` 转义序列：
- `$varname`：变量引用（标识符字符）
- `${varname}`：带花括号的变量引用
- `$ `（空格）：转义空格
- `$:`：转义冒号
- `$$`：转义美元符号
- `$\n`：换行续行（版本依赖）

### Edge 的快捷求值方法

Edge 结构体提供了便捷方法访问常用绑定：

| 方法 | 返回类型 | 说明 |
|------|---------|------|
| `GetBinding(StringPiece key) const` | `string` | Shell 转义后的绑定值 |
| `GetBindingBool(StringPiece key) const` | `bool` | 获取布尔绑定（`"1"` 等非空值为 true） |
| `GetUnescapedDepfile() const` | `string` | 获取 depfile 路径（不 shell 转义） |
| `GetUnescapedDyndep() const` | `string` | 获取 dyndep 路径（不 shell 转义） |
| `GetUnescapedRspfile() const` | `string` | 获取 rspfile 路径（不 shell 转义） |
| `EvaluateCommand(bool incl_rsp_file = false) const` | `string` | 求值完整命令字符串；incl_rsp_file=true 时包含响应文件内容 |
| `is_phony() const` | `bool` | 是否使用 phony 规则 |
| `use_console() const` | `bool` | 是否使用 console 池 |

### 代码示例

```cpp
// 变量查找
BindingEnv toplevel;
toplevel.AddBinding("cflags", "-Wall -O2");

BindingEnv subenv(&toplevel);  // 子作用域
subenv.AddBinding("cflags", "-g");  // 覆盖

// subenv 中 $cflags → "-g"
// toplevel 中 $cflags → "-Wall -O2"

// EvalString 求值
EvalString eval;
eval.AddText("gcc ");
eval.AddSpecial("cflags");
eval.AddText(" -c ");
eval.AddSpecial("in");
eval.AddText(" -o ");
eval.AddSpecial("out");

string cmd = eval.Evaluate(&subenv);
// cmd → "gcc -g -c foo.c -o foo.o"

// Rule 绑定访问
const Rule* rule = state.bindings_.LookupRule("cc");
if (rule) {
  const EvalString* cmd_bind = rule->GetBinding("command");
  if (cmd_bind) {
    string command = cmd_bind->Evaluate(edge_env);
  }
}
```
