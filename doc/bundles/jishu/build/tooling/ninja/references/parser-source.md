---
type: Reference
title: 清单解析器 API 参考
description: src/manifest_parser.h/cc、src/lexer.h/cc、src/parser.h 源码参考——ManifestParser、Lexer、Parser 完整 API
tags: [reference, api, parser, lexer, manifest, token, c++]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T00:00:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: ninja-manifest-parser
    title: src/manifest_parser.h
    path: external/libs/tools/ninja/src/manifest_parser.h
  - id: ninja-manifest-parser-cc
    title: src/manifest_parser.cc
    path: external/libs/tools/ninja/src/manifest_parser.cc
  - id: ninja-lexer
    title: src/lexer.h
    path: external/libs/tools/ninja/src/lexer.h
  - id: ninja-lexer-cc
    title: src/lexer.cc
    path: external/libs/tools/ninja/src/lexer.cc
  - id: ninja-parser
    title: src/parser.h
    path: external/libs/tools/ninja/src/parser.h
---

# 清单解析器 API 参考

> 信源文件：manifest_parser.h、lexer.h、parser.h

本文档记录 Ninja 构建清单（.ninja 文件）解析模块的完整 API。

---

## Parser 基类

**头文件**：`src/parser.h`

所有解析器的抽象基类，提供文件加载和词法分析器管理。

### 构造函数

```cpp
Parser(State* state, FileReader* file_reader);
virtual ~Parser();
```

### 公共方法

| 方法 | 返回类型 | 说明 |
|------|---------|------|
| `Load(const string& filename, string* err, Lexer* parent = NULL)` | `bool` | 加载并解析文件；parent 用于追踪 include/subninja 嵌套 |

### 保护方法

| 方法 | 返回类型 | 说明 |
|------|---------|------|
| `ExpectToken(Lexer::Token expected, string* err)` | `bool` | 期望下一个 token 为指定类型，否则生成错误信息 |

### 保护成员

| 成员 | 类型 | 说明 |
|------|------|------|
| `state_` | `State*` | 全局构建状态 |
| `file_reader_` | `FileReader*` | 文件读取接口 |
| `lexer_` | `Lexer` | 词法分析器实例 |

### 私有虚方法

| 方法 | 返回类型 | 说明 |
|------|---------|------|
| `Parse(const string& filename, const string& input, string* err)` | `bool` | 纯虚函数，解析文件内容字符串 |

---

## ManifestParser 结构体

**头文件**：`src/manifest_parser.h`

继承自 Parser，负责解析 .ninja 构建清单文件。

### 构造函数

```cpp
ManifestParser(State* state, FileReader* file_reader,
               ManifestParserOptions options = ManifestParserOptions());
```

### ManifestParserOptions

```cpp
struct ManifestParserOptions {
  PhonyCycleAction phony_cycle_action_ = kPhonyCycleActionWarn;
};

enum PhonyCycleAction {
  kPhonyCycleActionWarn,   // phony 循环时发出警告
  kPhonyCycleActionError   // phony 循环时报错
};

enum DupeEdgeAction {
  kDupeEdgeActionWarn,     // 重复边时警告
  kDupeEdgeActionError     // 重复边时报错
};
```

### 公共方法

| 方法 | 返回类型 | 说明 |
|------|---------|------|
| `ParseTest(const string& input, string* err)` | `bool` | 解析文本字符串（测试用），设置 quiet_=true |

### 私有解析方法

| 方法 | 返回类型 | 说明 |
|------|---------|------|
| `Parse(const string& filename, const string& input, string* err)` | `bool` | 实现 Parser::Parse，解析文件内容 |
| `ParsePool(string* err)` | `bool` | 解析 `pool` 声明 |
| `ParseRule(string* err)` | `bool` | 解析 `rule` 声明 |
| `ParseLet(string* key, EvalString* val, string* err)` | `bool` | 解析变量赋值（`key = value`） |
| `ParseEdge(string* err)` | `bool` | 解析 `build` 边声明 |
| `ParseDefault(string* err)` | `bool` | 解析 `default` 目标声明 |
| `ParseFileInclude(bool new_scope, string* err)` | `bool` | 解析 `include` 或 `subninja` 指令 |

### 私有成员

| 成员 | 类型 | 说明 |
|------|------|------|
| `env_` | `BindingEnv*` | 当前变量绑定环境 |
| `options_` | `ManifestParserOptions` | 解析器选项 |
| `quiet_` | `bool` | 是否静默模式（测试时设置） |
| `subparser_` | `unique_ptr<ManifestParser>` | 子解析器，用于解析 include/subninja |
| `ins_` | `vector<EvalString>` | ParseEdge 复用的输入列表（避免重复分配） |
| `outs_` | `vector<EvalString>` | ParseEdge 复用的输出列表 |
| `validations_` | `vector<EvalString>` | ParseEdge 复用的验证列表 |

---

## Lexer 结构体

**头文件**：`src/lexer.h`

词法分析器，将 .ninja 文件文本分解为 token 流。

### 构造函数

```cpp
Lexer();                              // 默认构造
explicit Lexer(const char* input);    // 测试用辅助构造
```

### Token 枚举

```cpp
enum Token {
  ERROR,     // 错误 token
  BUILD,     // "build" 关键字
  COLON,     // ":" 冒号
  DEFAULT,   // "default" 关键字
  EQUALS,    // "=" 等号
  IDENT,     // 标识符（规则名、变量名等）
  INCLUDE,   // "include" 关键字
  INDENT,    // 缩进（build 块内的缩进）
  NEWLINE,   // 换行符
  PIPE,      // "|" 单管道（隐式依赖分隔）
  PIPE2,     // "||" 双管道（order-only 依赖分隔）
  PIPEAT,    // "|@" 管道+at（验证依赖分隔）
  POOL,      // "pool" 关键字
  RULE,      // "rule" 关键字
  SUBNINJA,  // "subninja" 关键字
  TEOF       // 文件结束
};
```

### 核心方法

| 方法 | 返回类型 | 说明 |
|------|---------|------|
| `Start(StringPiece filename, StringPiece input)` | `void` | 开始解析输入文本 |
| `ReadToken()` | `Token` | 读取下一个 Token |
| `UnreadToken()` | `void` | 回退到上一个已读 Token |
| `PeekToken(Token token)` | `bool` | 若下一个 token 匹配指定类型则读取并返回 true |
| `ReadIdent(string* out)` | `bool` | 读取简单标识符（规则名或变量名），失败返回 false |
| `ReadPath(EvalString* path, string* err)` | `bool` | 读取路径（含 $ 转义），内联调用 ReadEvalString(path, true, err) |
| `ReadVarValue(EvalString* value, string* err)` | `bool` | 读取变量值（`=` 右侧，含 $ 转义），内联调用 ReadEvalString(value, false, err) |
| `Error(const string& message, string* err)` | `bool` | 构造带上下文的错误信息，返回 false |

### 静态方法

| 方法 | 返回类型 | 说明 |
|------|---------|------|
| `TokenName(Token t)` | `const char*` | 返回 token 的可读名称（用于错误消息） |
| `TokenErrorHint(Token expected)` | `const char*` | 返回 token 错误提示（用于错误消息） |

### 公共成员

| 成员 | 类型 | 说明 |
|------|------|------|
| `manifest_version_major` | `int` | 从清单解析出的 ninja_required_version 主版本号 |
| `manifest_version_minor` | `int` | 从清单解析出的 ninja_required_version 次版本号 |

### 私有方法

| 方法 | 返回类型 | 说明 |
|------|---------|------|
| `EatWhitespace()` | `void` | 跳过空白（在每次读取 token/ident 后调用） |
| `ReadEvalString(EvalString* eval, bool path, string* err)` | `bool` | 读取 $-转义字符串；path=true 时在分隔符处停止 |

### 私有成员

| 成员 | 类型 | 说明 |
|------|------|------|
| `filename_` | `StringPiece` | 当前文件名（用于错误定位） |
| `input_` | `StringPiece` | 输入文本 |
| `ofs_` | `const char*` | 当前解析位置指针 |
| `last_token_` | `const char*` | 上一个 token 位置（用于 UnreadToken） |
| `newline_version_checked_` | `bool` | 是否已检查 `$^`（换行转义）版本要求 |

### DescribeLastError

```cpp
string DescribeLastError();
```

若最后读取的 token 是 ERROR，提供更多信息或返回空字符串。

---

## 清单解析流程

解析 .ninja 文件时，ManifestParser::Parse() 按以下流程逐行处理：

```
Parse(filename, input, err)
  ├─ lexer_.Start(filename, input)
  ├─ 循环读取 Token:
  │   ├─ IDENT → 可能是变量赋值或顶级声明
  │   │   ├─ 下一个 token 是 EQUALS → ParseLet()（变量赋值）
  │   │   ├─ 标识符是 "rule" → ParseRule()
  │   │   ├─ 标识符是 "build" → ParseEdge()
  │   │   ├─ 标识符是 "pool" → ParsePool()
  │   │   ├─ 标识符是 "default" → ParseDefault()
  │   │   ├─ 标识符是 "include" → ParseFileInclude(false)（同作用域）
  │   │   ├─ 标识符是 "subninja" → ParseFileInclude(true)（新作用域）
  │   │   └─ 其他 → 错误
  │   ├─ NEWLINE → 跳过空行
  │   ├─ TEOF → 解析完成
  │   └─ 其他 → 错误
  └─ 返回 true/false
```

### 各类声明解析要点

**pool 声明**（ParsePool）：
1. 读取 pool 名称（IDENT）
2. 期望 NEWLINE/INDENT
3. 读取 `depth = N` 变量赋值
4. 创建 Pool 对象并通过 state_->AddPool() 注册

**rule 声明**（ParseRule）：
1. 读取 rule 名称（IDENT）
2. 期望 NEWLINE/INDENT
3. 循环读取缩进的变量赋值（command、description、depfile、deps、pool、dyndep、generator、restat、rspfile、rspfile_content 等保留绑定名）
4. 创建 Rule 对象并通过 env_->AddRule() 添加

**build 声明**（ParseEdge）：
1. 读取输出路径列表（outs_）
2. 期望 COLON
3. 读取规则名（IDENT）
4. 读取显式输入路径列表（ins_）
5. 按分隔符分段：PIPE → 隐式依赖，PIPE2 → order-only 依赖，PIPEAT → 验证依赖
6. 期望 NEWLINE
7. 循环读取缩进的变量赋值（覆盖 rule 级别绑定）
8. 创建 Edge，通过 state_->AddOut()/AddIn()/AddValidation() 连接节点

**default 声明**（ParseDefault）：
1. 读取目标路径列表
2. 通过 state_->AddDefault() 注册默认目标

**include/subninja**（ParseFileInclude）：
1. 读取包含文件路径（EvalString）
2. 在当前环境中求值路径
3. 创建 subparser_ 或复用当前解析器
4. `new_scope=true`（subninja）时创建新 BindingEnv（以当前 env 为 parent）
5. 调用 file_reader_->ReadFile() 读取文件内容
6. 递归调用 Parse() 解析被包含文件
7. subninja 结束后恢复原 env_

### 代码示例

```cpp
// 基本用法：加载 build.ninja
State state;
RealDiskInterface disk_interface;
ManifestParser parser(&state, &disk_interface);
string err;
if (!parser.Load("build.ninja", &err)) {
  fprintf(stderr, "parse error: %s\n", err.c_str());
  return 1;
}

// 测试用：直接解析字符串
State state2;
ManifestParser parser2(&state2, /*file_reader=*/nullptr);
string test_input =
    "rule cc\n"
    "  command = gcc -c $in -o $out\n"
    "build foo.o: cc foo.c\n";
string err2;
if (!parser2.ParseTest(test_input, &err2)) {
  fprintf(stderr, "parse error: %s\n", err2.c_str());
  return 1;
}
```
