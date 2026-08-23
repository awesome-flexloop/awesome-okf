---
type: Example
title: 基础终端使用
description: 在JupyterLite中打开终端、执行基础shell命令、文件操作、Tab补全和交互式命令
tags: [terminal, shell, basic, file-io, tab-completion, interactive]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T20:00:00+08:00" }
status: stable
stale_after: 2027-08-22
prerequisites:
  - "已安装jupyterlite-terminal并构建JupyterLite站点（参见[安装与快速开始](../concepts/01-getting-started.md)）"
  - "jupyter-lite.json中terminalsAvailable设为true"
---

# 基础终端使用

本示例演示如何在JupyterLite中打开终端并执行常用shell命令。

## 1. 打开终端

1. 启动JupyterLite站点（`jupyter lite serve`或其他静态服务器）
2. 在JupyterLab界面中，点击菜单 **File → New → Terminal**
3. 一个新的终端标签页打开，显示初始内容类似：

```
Last login: ...
JupyterLite Terminal v1.7.0-a0 (cockle)
Type 'help' for a list of commands.
$
```

## 2. 基本导航命令

```bash
# 查看当前工作目录
$ pwd
/home/pyodide

# 列出当前目录文件
$ ls

# 列出详细信息
$ ls -la

# 切换到DriveFS（JupyterLite文件系统）
$ cd /drive
$ pwd
/drive

# 查看DriveFS中的文件（对应JupyterLite文件浏览器中的内容）
$ ls
months.txt  hello.txt
```

## 3. 文件操作

```bash
# 查看文件内容
$ cat months.txt
January
February
March
April
May
June
July
August
September
October
November
December

# 创建文件（使用重定向）
$ echo "Hello from terminal!" > greeting.txt

# 查看新文件
$ cat greeting.txt
Hello from terminal!

# 复制文件
$ cp months.txt months-backup.txt
$ ls
greeting.txt  months.txt  months-backup.txt

# 创建目录
$ mkdir mydir
$ cd mydir

# 移动/重命名文件
$ mv ../greeting.txt ./hello.txt
$ ls
hello.txt

# 删除文件
$ rm hello.txt
$ cd ..
$ rm -r mydir

# 追加内容到文件
$ echo "Additional line" >> months-backup.txt
```

## 4. 管道和过滤

```bash
# 使用grep过滤（注意：cockle的grep支持基本模式匹配）
$ cat months.txt | grep ember
September
October
November
December

# 搜索包含"J"的月份
$ cat months.txt | grep J
January
June
July
```

## 5. Tab补全

Tab补全是终端效率的核心功能：

### 命令名补全

```bash
# 输入部分命令名后按Tab
$ una<TAB>
# 自动补全为
$ uname

# 按Tab两次显示所有可用命令
$ <TAB><TAB>
alias  cat  cd  cockle-config  cp  echo  grep  ls  mkdir  pwd  rm  uname  ...
```

### 文件名补全

```bash
# 在/drive目录下
$ cat mon<TAB>
# 自动补全为
$ cat months.txt

# 部分文件名按Tab
$ grep ember mon<TAB>
# 自动补全为
$ grep ember months.txt
```

## 6. 交互式命令

某些命令（如grep不带文件名参数时）会等待stdin输入：

```bash
$ grep o
# shell等待输入，输入文本行
Hello World
How are you
# 按 Ctrl+D (EOF) 结束输入，显示匹配行
Hello World
How are you
```

注意：在浏览器终端中，Ctrl+D是EOF快捷键。Ctrl+C用于中断当前命令。

## 7. 别名

```bash
# 定义别名
$ alias ll='ls -la'

# 使用别名
$ ll
# 等价于 ls -la

# 查看所有别名
$ alias

# 注意：在shell中直接定义的别名仅在当前shell会话有效
# 要永久生效，通过扩展API调用registerAlias()
```

## 8. cockle-config命令

`cockle-config`是cockle shell内置的配置工具：

```bash
# 查看当前stdin模式
$ cockle-config stdin
Current stdin mode: sw

# 切换到SAB模式（需要COOP/COEP头）
$ cockle-config stdin sab
Switched to SAB stdin mode

# 切回SW模式
$ cockle-config stdin sw
Switched to Service Worker stdin mode
```

## 9. 终端设置

在JupyterLab的Settings菜单中可以调整终端：

- **Settings → Terminal → Theme**：选择inherit/dark/light
- **Settings → Theme**：切换全局暗色/亮色主题（当终端主题为inherit时同步）
- 终端大小可通过拖拽标签页分割线调整，shell会自动接收set_size事件

## 10. 关闭终端

- 点击终端标签页的关闭按钮（X）
- 或在shell中输入`exit`（如果支持）

关闭后shell资源自动释放，下次打开终端会创建新的shell实例。

## 常见问题

**Q: /drive目录为空？**
确保你上传了文件到JupyterLite文件浏览器，或通过终端创建了文件。DriveFS对应JupyterLite ContentsManager的根目录。

**Q: 某些命令不可用？**
cockle是一个精简的WASM shell，只实现了常用的Unix命令子集。不支持&&、||、$(...)等shell特性。

**Q: git clone失败？**
远程git操作需要CORS代理。参见[安装与快速开始](../concepts/01-getting-started.md)中的CORS配置说明。

## 相关概念

- [Shell与Worker机制](../concepts/04-shell-and-worker.md)：终端背后的工作原理
- [文件系统与Stdin路由](../concepts/06-drivefs-and-stdin.md)：/drive挂载机制
- [执行shell命令示例](02-execute-shell-command.md)：编程式API调用
