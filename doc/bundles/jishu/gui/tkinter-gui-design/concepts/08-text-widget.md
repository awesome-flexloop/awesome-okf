---
type: Concept
title: Text 多行文本部件
description: tkinter Text 经典部件：创建与 width/height/wrap（none/char/word）、state（normal/disabled，无 instate）、滚动条联动（yscrollcommand/xscrollcommand）、索引体系（1.0/end/insert/行.列）、insert/get/delete、tag_configure/tag_add/tag_remove 文本标签样式、search 搜索高亮、undo 撤销栈、event_generate 虚拟事件（Cut/Copy/Paste/Undo/Redo）、行号栏与当前行高亮实现
tags: [tkinter, Text, 文本编辑器, tag_configure, search, event_generate, undo, ScrolledText, 索引]
generated: { by: "blog-article-to-okf-wiki", at: "2026-09-02T21:30:00+08:00" }
verified: { by: "process:bundle-self-check", at: "2026-09-02T21:30:00+08:00" }
status: stable
stale_after: 2027-09-02
sources:
  - id: tgd-sources
    resource: /references/sources.md
    title: 简书文集《tkinter GUI 设计》信源登记（F-TGD-01 ~ F-TGD-34）
  - id: tkdocs-text
    resource: https://tkdocs.com/tutorial/text.html
    title: 'TKDocs: Text Widget'
---

# Text 多行文本部件

> 对应信源：F-TGD-08《3.7 tkinter 之 Text》、F-TGD-25《9 tkinter 创建文本编辑器》。Text 是经典 Tk 部件（非 ttk 主题部件），功能强大，已被用作全字处理器、Outliner、Web 浏览器等的基础。完整编辑器实战见 [文本编辑器](../examples/07-text-editor.md)。

## 1 创建与基本配置

```python
from tkinter import Text
t = Text(parent, width=40, height=10)
```

- `width`/`height`：以**字符数和行数**计的请求尺寸；
- `wrap`：换行方式——`"none"`（不换行，可水平滚动）、`"char"`（任意字符处换行）、`"word"`（仅在单词边界换行）；
- `undo=1`：开启撤销/重做栈；
- Text 是经典部件，**没有 ttk 的 `state()`/`instate()` 方法**，改用配置选项 `state='normal'|'disabled'`（只读文本栏置 disabled）。

滚动条联动方式与 Listbox 相同：

```python
content_text = Text(wrap='word', undo=1)
scroll_bar = ttk.Scrollbar(content_text)
content_text.configure(yscrollcommand=scroll_bar.set)
scroll_bar.config(command=content_text.yview)
```

简单场景也可直接用 `tkinter.scrolledtext.ScrolledText`（见 [基础 Widgets](02-basic-widgets.md)）。

## 2 索引体系

Text 的位置用**"行.列"**字符串表示，行从 1 起、列从 0 起：

- `'1.0'`：第一行第零列（文本开头）；
- `'end'`：文本末尾；
- `'insert'`：插入光标当前位置；
- 表达式索引：`'insert linestart'`/`'insert lineend'`（当前行首/行尾）、`f'{pos}+{n}c'`（pos 后 n 个字符）。

```python
row, col = content_text.index('insert').split('.')   # 当前光标行列
row_end, _ = content_text.index("end").split('.')    # 总行数
```

## 3 insert / get / delete

```python
content_text.insert(1.0, text)          # 在指定索引插入文本
content = content_text.get(1.0, 'end')  # 取全部文本
content_text.delete(1.0, 'end')         # 清空
```

## 4 tag：文本标签与样式

tag 是给 Text 中文本区间附加样式/行为的机制：

- `tag_configure(tag, **opts)`：定义标签样式（foreground/background 等）；
- `tag_add(tag, start, end)`：把标签应用到区间；
- `tag_remove(tag, start, end)`：移除区间上的标签；
- 内置 `'sel'` 标签表示选中区，`tag_add('sel', '1.0', 'end')` 即全选。

**搜索高亮**：循环 `search()` 找到每个匹配，打上 `'match'` 标签：

```python
def search_output(self, needle, if_ignore_case, ...):
    self.content_text.tag_remove('match', '1.0', 'end')
    matches_found = 0
    if needle:
        start_pos = '1.0'
        while True:
            start_pos = self.content_text.search(
                needle, start_pos, nocase=if_ignore_case, stopindex='end')
            if not start_pos:
                break
            end_pos = f'{start_pos}+{len(needle)}c'
            self.content_text.tag_add('match', start_pos, end_pos)
            matches_found += 1
            start_pos = end_pos
        self.content_text.tag_config('match', foreground='red', background='yellow')
```

**当前行高亮**：用 `after()` 周期地把 `active_line` 标签刷新到光标所在行：

```python
content_text.tag_configure('active_line', background='ivory2')

def highlight_line(interval=100):
    content_text.tag_remove("active_line", 1.0, "end")
    content_text.tag_add("active_line", "insert linestart", "insert lineend+1c")
    content_text.after(interval, highlight_line)
```

## 5 编辑命令：event_generate 虚拟事件

剪贴板与撤销/重做不必手动实现，向 Text 发送标准虚拟事件即可：

```python
content_text.event_generate("<<Cut>>")
content_text.event_generate("<<Copy>>")
content_text.event_generate("<<Paste>>")
content_text.event_generate("<<Undo>>")
content_text.event_generate("<<Redo>>")
```

这些事件与菜单/右键菜单/快捷键绑定后即构成完整编辑能力。快捷键直接绑在 Text 上（回调返回 `"break"` 阻止默认处理）：

```python
content_text.bind('<Control-n>', self.new_file)
content_text.bind('<Control-s>', self.save)
content_text.bind('<Control-f>', self.find_text)
content_text.bind('<Control-a>', self.select_all)
content_text.bind('<Control-y>', self.redo)
content_text.bind('<KeyPress-F1>', self.display_help_messagebox)
```

## 6 行号栏实现

用一个窄的只读 Text 作为行号栏，内容变化时重填行号（先置 normal 写入再置 disabled）：

```python
line_number_bar = Text(width=4, padx=3, takefocus=0, border=0,
                       background='khaki', state='disabled', wrap='none')

def get_line_numbers(self):
    output = ''
    if self.show_line_number.get():
        row, _ = self.content_text.index("end").split('.')
        for k in range(1, int(row)):
            output += str(k) + '\n'
    return output

def update_line_numbers(self, event=None):
    self.line_number_bar.config(state='normal')
    self.line_number_bar.delete('1.0', 'end')
    self.line_number_bar.insert('1.0', self.get_line_numbers())
    self.line_number_bar.config(state='disabled')
```

正文栏绑定 `<Any-KeyPress>` 触发行号与光标位置栏刷新；光标行列用 `index('insert')` 解析后显示在右下角 Label。

## 延伸阅读

- [基础 Widgets](02-basic-widgets.md)：Entry/ScrolledText 等输入部件
- [事件绑定与变量联动](07-events-and-variables.md)：bind、trace_add 与快捷键
- [菜单、多窗口与标准对话框](05-menus-windows-dialogs.md)：查找窗口 Toplevel、filedialog/messagebox
- 实战：[文本编辑器（行号/搜索高亮/主题/右键菜单）](../examples/07-text-editor.md)

## 事实溯源

F-TGD-08（[信源登记](../references/sources.md)）：Text 为经典非主题部件、width/height 以字符行计、wrap 三值（none/char/word）、state 配置选项替代 instate、xscrollcommand/yscrollcommand 与 xview/yview 滚动联动、insert/get 方法。
F-TGD-25（[信源登记](../references/sources.md)）：wrap='word'/undo=1 配置、索引体系（1.0/end/insert/linestart/lineend/+Nc）、tag_configure/tag_add/tag_remove/search 搜索高亮、event_generate 五个虚拟事件、行号栏实现、`<Any-KeyPress>` 与 Control 快捷键绑定、sel 标签全选（源出 *Tkinter GUI Application Development Blueprints*）。