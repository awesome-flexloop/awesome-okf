---
type: example
title: "高级语法实战"
description: "Mermaid图表、文件包含、内容嵌入、Raw原始内容、SI单位、化学式等高级语法的完整示例"
tags: [example, mermaid, include, embed, raw, si-units, chemistry]
generated: 2026-08-23
verified: true
status: stable
stale_after: 2027-12-31
---

# 高级语法实战

本文档提供 Mermaid 图表、文件包含、Raw 内容、SI 单位、化学式等高级语法的完整可运行示例。

## Mermaid 图表

### 流程图

````markdown
```{mermaid}
flowchart TD
    A[开始] --> B{是否登录?}
    B -->|是| C[进入主页]
    B -->|否| D[跳转登录页]
    D --> E[输入账号密码]
    E --> F{验证通过?}
    F -->|是| C
    F -->|否| D
    C --> G[结束]
```
````

### 时序图

````markdown
```{mermaid}
sequenceDiagram
    participant U as 用户
    participant F as 前端
    participant B as 后端
    participant D as 数据库

    U->>F: 点击登录按钮
    F->>B: POST /api/login
    B->>D: 查询用户
    D-->>B: 返回用户数据
    B-->>F: 返回Token
    F-->>U: 登录成功
```
````

### 类图

````markdown
```{mermaid}
classDiagram
    class Animal {
        +String name
        +int age
        +makeSound()
    }
    class Dog {
        +String breed
        +bark()
    }
    class Cat {
        +int lives
        +meow()
    }
    Animal <|-- Dog
    Animal <|-- Cat
```
````

### 状态图

````markdown
```{mermaid}
stateDiagram-v2
    [*] --> 待支付
    待支付 --> 已支付: 支付成功
    待支付 --> 已取消: 超时
    已支付 --> 已发货: 发货
    已发货 --> 已完成: 确认收货
    已完成 --> [*]
    已取消 --> [*]
```
````

### 甘特图

````markdown
```{mermaid}
gantt
    title 项目开发计划
    dateFormat  YYYY-MM-DD
    section 设计
    需求分析     :done,    des1, 2024-01-01, 7d
    UI设计       :done,    des2, after des1, 10d
    section 开发
    前端开发     :active,  dev1, after des2, 20d
    后端开发     :         dev2, after des2, 25d
    section 测试
    集成测试     :         test1, after dev1, 10d
```
````

### ER 图

````markdown
```{mermaid}
erDiagram
    CUSTOMER ||--o{ ORDER : places
    ORDER ||--|{ LINE-ITEM : contains
    CUSTOMER }|..|{ DELIVERY-ADDRESS : uses
```
````

## 文件包含（Include）

### 包含 Markdown 文件

```markdown
:::{include} sections/introduction.md
:::
```

### 以代码块形式包含文件

````markdown
```{literalinclude} src/config.py
```

:::{include} src/utils.ts
:lang: typescript
:linenos:
:::
````

### 包含文件的指定行范围

````markdown
% 包含第10-20行
```{literalinclude} src/app.py
:start-line: 9
:end-line: 20
```

% 从指定文本标记开始/结束
```{literalinclude} src/app.py
:start-after: // BEGIN_SNIPPET
:end-before: // END_SNIPPET
```
````

### 精确选择行

````markdown
```{literalinclude} src/app.py
:lines: 1,3,5-10,20-
:lineno-match:
```
````

### 自动语言推断

```markdown
:::{include} code/example.py    → 自动识别为 python
:::{include} code/example.ts    → 自动识别为 typescript
:::{include} code/example.js    → 自动识别为 javascript
:::{include} code/example.yml   → 自动识别为 yaml
:::{include} code/example.tex   → 自动识别为 latex
:::{include} code/example.md    → 自动识别为 markdown
```

## 内容嵌入（Embed）

### 嵌入图表

```markdown
% 在另一个位置复用已标记的图表
:::{embed} #fig-model
:::
```

### 嵌入 Notebook 输出

```markdown
% 嵌入代码单元格输出（不显示输入代码）
:::{embed} #cell-plot
:remove-input: true
:::
```

## Mermaid + Figure 组合

````markdown
:::{figure} #mermaid-chart
:label: fig-flowchart

用户登录流程图
:::

```{mermaid}
:label: mermaid-chart

flowchart LR
    A --> B
```
````

（mermaid 节点本身不是直接 labelable 的，可以用 div 包裹或在 figure 中引用。）

## Raw 原始内容

### LaTeX 专用内容

```markdown
:::{raw:latex}
\newpage
\thispagestyle{empty}
:::
```

### Typst 专用内容

```markdown
:::{raw:typst}
#pagebreak()
#set text(size: 10pt)
:::
```

### 行内 Raw

```markdown
这是普通文本 {raw:latex}`\TeX{}` 这也是普通文本。
在 Typst 中 {raw:typst}`#super("TM")` 显示商标符号。
```

### 通用 Raw 指令

```markdown
:::{raw} latex
\vspace{2em}
:::

:::{raw} typst
#v(2em)
:::
```

## SI 单位

### 基本单位

```markdown
光速：{si}`3e8<\meter\per\second>`
质量：{si}`10<\kilo\gram>`
温度：{si}`25<\degreeCelsius>`
时间：{si}`3600<\second>`（即1小时）
长度：{si}`100<\micro\meter>`（100微米）
```

### 复合单位

```markdown
力：{si}`10<\newton>`（10 N）
电压：{si}`220<\volt>`
电阻：{si}`100<\ohm>`
功率：{si}`1.5<\kilo\watt>`
频率：{si}`50<\hertz>`
能量：{si}`1<\kilo\watt\hour>`（度电）
```

### 科学计数法

```markdown
普朗克常数：{si}`6.626e-34<\joule\second>`
```

## 化学式

```markdown
水：{chem}`H2O`
二氧化碳：{chem}`CO2`
葡萄糖：{chem}`C6H12O6`
硫酸：{chem}`H2SO4`
乙醇：{chem}`C2H5OH`
```

## 键盘按键

```markdown
按 {kbd}`Ctrl+C` 复制，{kbd}`Ctrl+V` 粘贴。

按 {kbd}`Ctrl+Shift+P` 打开命令面板。

按 {kbd}`Enter` 确认，{kbd}`Esc` 取消。
```

## 文本格式化角色

```markdown
H{sub}`2`O 是水的化学式。

2{sup}`10` = 1024。

{underline}`下划线文本`。

{delete}`已删除的内容`。

{smallcaps}`Small Caps Text`。

{abbr}`JSON (JavaScript Object Notation)` 是一种数据格式。
```

## 折叠面板（Dropdown）

```markdown
:::{dropdown} 点击展开常见问题
:open: false

**Q: MyST 和 Markdown 有什么区别？**
A: MyST 是 Markdown 的超集，增加了指令、角色、交叉引用等科学写作功能。

**Q: 如何添加自定义指令？**
A: 通过插件机制可以注册自定义指令和角色。
:::
```

## Div 通用容器

```markdown
:::{div}
:class: warning-box custom-style

这是一个自定义样式的容器，可以通过 CSS 控制外观。
:::
```

## 索引

### 标记索引条目

```markdown
:::{index}
single: Transformer
pair: 注意力机制; 自注意力
see: MyST; Markedly Structured Text
:::

Transformer 架构{index}`Transformer` 是现代NLP的基础...
```

### 显示索引

```markdown
## 索引

:::{show-index} 关键词索引
:::
```

## 综合示例：技术文档片段

````markdown
# API 使用指南

:::{note}
本文档基于 API v2 版本。v1 版本用户请参考 {doc}`migration-guide`。
:::

## 认证

所有请求需要在 Header 中携带 Token：

```{code} bash
:caption: API 认证示例
:label: code-auth

curl -H "Authorization: Bearer YOUR_TOKEN" \
     https://api.example.com/v2/data
```

如 {ref}`code-auth` 所示...

## 请求限制

:::{table} API 速率限制
:label: tbl-limits

| 计划 | 请求/分钟 | 并发数 |
|------|----------|--------|
| 免费 | 60 | 1 |
| 专业 | 600 | 10 |
| 企业 | 6000 | 100 |
:::

速率限制如 {ref}`tbl-limits` 所示...

## 流程

```{mermaid}
flowchart LR
    A[发起请求] --> B{认证通过?}
    B -->|是| C[处理请求]
    B -->|否| D[返回401]
    C --> E{速率限制?}
    E -->|正常| F[返回数据]
    E -->|超限| G[返回429]
```

响应时间约为 {si}`100<\milli\second>`，最大负载支持 {si}`1000<\request\per\second>`。

:::{seealso}
更多信息请参考 {cite:p}`api-docs-2024`。
:::

:::{bibliography}
:::
````
