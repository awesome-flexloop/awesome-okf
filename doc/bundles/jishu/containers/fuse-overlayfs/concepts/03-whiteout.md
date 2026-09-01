---
type: Concept
title: Whiteout 与目录合并
description: Whiteout 白项删除机制、三种 whiteout 形式（.wh. 文件/char 0/0/.wh..wh..opq）、opaque 不透明目录、多层目录合并算法、readdir 实现
tags: [concept, whiteout, opaque, directory-merge, readdir, union-mount, rust]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-26T00:00:00+08:00" }
status: stable
stale_after: 2027-08-26
sources:
  - id: facts-fuse-overlayfs
    resource: "/.trae/specs/containers-okf-wiki/facts-fuse-overlayfs.md"
    title: fuse-overlayfs 可验证事实
  - id: overlay-source
    resource: "/bundles/containers/fuse-overlayfs/references/overlay-source.md"
    title: OverlayFs 核心文件系统 API 参考
---

# Whiteout 与目录合并

OverlayFS 的"联合挂载"视图需要解决两个关键问题：
1. **删除**：如何在不修改只读 lower 层的情况下"删除"文件？→ whiteout（白项）
2. **目录合并**：多层同名目录的内容如何呈现为一个目录？→ 逐层合并 + opaque 标记

本文档详细讲解 fuse-overlayfs 的 whiteout 机制和多层目录合并算法。

---

## 删除难题：为什么需要 Whiteout

OverlayFS 的 lower 层是只读的，你不能真正删除 lower 层中的文件——只能在 upper 层"遮盖"它们。这就像在一块玻璃上贴一张不透明贴纸来"遮住"后面的内容，而不是把后面的内容刮掉。

```
场景：lower 层有 /foo，用户执行 rm /foo

┌─────────────────────────────────────────┐
│  upper 层                                │
│  └── .wh.foo   ← whiteout 标记（遮盖）  │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│  lower 层                                │
│  └── foo       ← 文件仍然存在！只是被遮盖了│
└─────────────────────────────────────────┘

合并视图：/foo 不存在（被 whiteout 遮盖）
```

---

## 三种 Whiteout 形式 [F-039]

fuse-overlayfs 支持三种 whiteout 标记形式，与内核原生 OverlayFS 兼容：

| 形式 | 标记方式 | 用途 |
|------|---------|------|
| `.wh.<filename>` 文件 | upper 层中名为 `.wh.` + 原文件名的普通文件 | 标记单个文件/目录被删除 |
| `.wh..wh..opq`（opaque 标记） | upper 层中名为 `.wh..wh..opq` 的字符设备 | 标记目录为"不透明"（不合并下层） |
| Char device (0,0) | 主/次设备号为 0/0 的字符设备文件 | 另一种 whiteout 标记（与内核格式兼容） |

### 形式 1：.wh. 前缀文件（最常用）

删除 `/a/b/c.txt` 后，upper 层中出现 `/a/b/.wh.c.txt`：
- `.wh.c.txt` 是一个零字节普通文件
- readdir 遍历到 `.wh.c.txt` 时，知道 `c.txt` 被遮盖
- lookup(`c.txt`) 时发现 whiteout 标记，返回 ENOENT
- 白色项本身（`.wh.*` 文件）在合并视图中不可见

### 形式 2：.wh..wh..opq（不透明目录）

如果希望整个目录只显示 upper 层内容、不合并任何 lower 层内容：
- 在 upper 层该目录下创建 `.wh..wh..opq`
- 这通常用于重命名目录等场景
- 比逐个 whiteout 文件更高效

### 形式 3：Char device 0/0

这是内核 OverlayFS 传统使用的 whiteout 形式：
- `mknod .wh.foo c 0 0` 创建主/次设备号为 0/0 的字符设备
- fuse-overlayfs 也识别这种形式
- 某些容器运行时使用这种格式

---

## Opaque 目录：trusted.overlay.opaque xattr

除了 `.wh..wh..opq` 文件，还通过扩展属性标记目录不透明：

```
setxattr(path, "trusted.overlay.opaque", "y", XATTR_CREATE)
```

- xattr 名：`trusted.overlay.opaque`
- 值：`"y"`（字符串）表示不透明
- 与 `.wh..wh..opq` 文件等价，二选一即可
- readdir 检测到任一标记即停止合并下层

**Opaque 的使用场景**：
- `mkdir` 创建新目录：新目录天然不合并下层
- `rename` 目录到一个已有位置：需要将目标目录标记为 opaque
- 显式不希望看到下层内容的特殊场景

---

## 多层目录合并算法

readdir（读取目录）时，fuse-overlayfs 需要合并所有层的同名目录内容，正确处理 whiteout 和 opaque 标记。

### 核心数据结构：DirState.whiteouts [F-012]

```rust
DirState::Dir {
    children: FxHashMap<Vec<u8>, NodeId>,
    whiteouts: FxHashSet<Vec<u8>>,  // ← 已删除项集合
    loaded: bool,
}
```

### 合并算法步骤

```
readdir(dir_node):
  result = {}  // 最终输出的目录项集合
  
  // 从最高层（upper，layer 0）开始向下遍历
  for layer_idx in 0..layers.len():
      layer = layers[layer_idx]
      
      // 检查该层此目录是否标记为 opaque
      if is_opaque(layer, dir_node):
          break  // 停止向更下层查找
      
      // 读取该层目录内容
      entries = readdir_layer(layer, dir_node)
      
      for entry in entries:
          name = entry.name
          
          // 跳过 . 和 ..
          if name == "." || name == "..":
              continue
          
          // 处理 whiteout 标记
          if is_whiteout_name(name):
              if name == ".wh..wh..opq":
                  // 不透明标记，停止向下合并
                  opaque = true
                  break
              else:
                  // 普通 whiteout：将被遮盖的名字加入 whiteouts
                  deleted_name = strip_wh_prefix(name)
                  result.remove(deleted_name)
                  whiteouts.insert(deleted_name)
                  continue
          
          // 如果该名字已被上层 whiteout 遮盖，跳过
          if whiteouts.contains(name):
              continue
          
          // 如果该名字已被上层添加/找到，跳过（上层优先）
          if result.contains(name):
              continue
          
          // 检查这是否是 char 0/0 whiteout
          if entry.is_char_device_0_0():
              result.remove(name)
              whiteouts.insert(name)
              continue
          
          // 这个条目应该出现在结果中
          result.insert(name, entry)
      
      if opaque:
          break
  
  // 过滤掉 .wh. 开头的条目本身（不暴露给用户）
  result = result.filter(|name| !name.starts_with(b".wh."))
  
  return result
```

### 算法关键点

| 规则 | 说明 |
|------|------|
| **上层优先** | 从 upper（layer 0）向下遍历，先看到的条目优先 |
| **whiteout 遮盖** | 遇到 `.wh.foo` 时，将 `foo` 从结果中移除并加入 whiteouts，下层的 `foo` 也被跳过 |
| **opaque 停止** | 遇到 `.wh..wh..opq` 或 xattr 标记时，不再合并更下层 |
| **隐藏 whiteout 文件** | `.wh.` 开头的文件本身不展示给用户 |
| **Char 0/0 识别** | 字符设备 0/0 也作为 whiteout 处理 |

### 合并示例

假设有三层：

```
layer 0 (upper):    a.txt, .wh.b.txt, subdir/
layer 1 (lower1):   b.txt, subdir/, c.txt
layer 2 (lower2):   c.txt, d.txt, .wh.dummy
```

合并过程：

1. 处理 layer 0：
   - `a.txt` → 加入 result
   - `.wh.b.txt` → `b.txt` 加入 whiteouts
   - `subdir/` → 加入 result
2. 处理 layer 1：
   - `b.txt` → 在 whiteouts 中，跳过
   - `subdir/` → 已存在，跳过
   - `c.txt` → 加入 result
3. 处理 layer 2：
   - `c.txt` → 已存在，跳过
   - `d.txt` → 加入 result
   - `.wh.dummy` → `dummy` 加入 whiteouts（但 dummy 不在任何层）
4. 过滤 `.wh.` 条目后最终结果：`a.txt`, `c.txt`, `d.txt`, `subdir/`

合并视图中：
- `a.txt` 来自 upper
- `b.txt` 被 whiteout 遮盖（不可见）
- `c.txt` 来自 lower1（虽然 lower2 也有，但 lower1 更上层）
- `d.txt` 来自 lower2
- `subdir/` 需要进一步合并各层 subdir 内容

---

## Lookup 路径解析

lookup（按名查找）是 readdir 的单条目版本，但不需要遍历所有层——找到即返回：

```
lookup(parent_node, name):
  current = parent_node.layer_idx
  
  while current < layers.len():
      layer = layers[current]
      
      // 检查该层目录是否 opaque
      if is_opaque(layer, parent_node):
          break
      
      // 在该层查找
      entry = statat(layer, parent_node, name)
      
      if entry.exists():
          // 检查是否是 char 0/0 whiteout
          if entry.is_char_device_0_0():
              return ENOENT  // 被 whiteout
          
          // 检查 upper 层是否有 whiteout
          if current > 0 && has_whiteout_in_upper_layers(parent_node, name, current):
              return ENOENT
          
          // 找到有效条目
          return entry
      
      // 检查是否在该层被 whiteout（.wh.name 文件）
      wh_entry = statat(layer, parent_node, whiteout_name(name))
      if wh_entry.exists():
          return ENOENT  // 被 whiteout，停止查找
      
      current += 1
  
  return ENOENT  // 所有层都没找到
```

---

## Whiteout 的创建时机

哪些操作会在 upper 层创建 whiteout？

| 操作 | whiteout 创建逻辑 |
|------|------------------|
| `unlink(name)` | 如果文件在 lower 层：在 upper 创建 `.wh.name`；如果在 upper 层：直接删除 |
| `rmdir(name)` | 类似 unlink：如果目录在 lower 层，创建 whiteout；如果目录是合并目录（有下层内容）：需要创建 `.wh..wh..opq` 或 whiteout 所有子项 |
| `rename(old, new)` | 如果目标 `new` 存在且在 lower 层：对 `new` 创建 whiteout；源 `old` 如果在 lower 层：copy-up 后 whiteout 源 |
| `create/mkdir/...` 覆盖 | 如果目标名在 lower 层存在：创建 whiteout 遮盖 lower 版本 |

### unlink 详细流程

```rust
fn unlink(parent: &mut OvlNode, name: &[u8]) -> FsResult<()> {
    // 查找文件在哪个层
    let (layer_idx, entry) = lookup_entry(parent, name)?;
    
    if layer_idx == 0 {
        // 文件已在 upper 层：直接删除
        unlinkat(upper_fd, parent, name);
    } else {
        // 文件在 lower 层：创建 whiteout
        let wh_name = whiteout_name(name);  // ".wh." + name
        
        // 1. 在 workdir 创建临时 whiteout 文件
        let tmp_name = format!(".wh.{name}#{random}");
        mknodat(workdir_fd, tmp_name, S_IFCHR, 0);  // char 0/0
        
        // 2. 原子 rename 到 upper
        renameat(workdir_fd, tmp_name, upper_fd, wh_name);
        
        // 3. 更新内存状态
        parent.dir_state.whiteouts.insert(name.to_vec());
        parent.remove_child(name);
    }
    
    Ok(())
}
```

---

## 目录删除的复杂性

删除目录比删除文件复杂，因为目录可能合并了多层内容：

### 情况 1：目录仅在 upper 层存在

直接 `rmdir()` 即可。

### 情况 2：目录仅在某 lower 层存在

在 upper 创建 whiteout（`.wh.dirname`），整个目录被遮盖。

### 情况 3：目录合并了多层内容（upper 和 lower 都有同名目录）

这是最复杂的情况：
1. 如果 upper 目录**完全为空**（没有用户创建的文件）：只需一个 `.wh.dirname` whiteout
2. 如果 upper 目录**有内容**：需要将目录标记为 opaque（`.wh..wh..opq`），然后清空所有 upper 层内容
   - 这样 lower 层内容被完全屏蔽
   - 然后删除 upper 目录

**为什么不能只 whiteout 每个子项？**
- 因为 lower 层目录可能有大量子项，逐个 whiteout 效率低
- lower 层可能新增子项（基础镜像更新），逐个 whiteout 无法遮盖未来新增的项
- Opaque 标记是"停止合并"的信号，一次性屏蔽所有下层内容

---

## 开发规则相关：unsafe 与错误处理 [F-008]

whiteout 和目录合并涉及大量系统调用，项目严格要求：
- `src/sys/` 之外**禁止 unsafe**：所有 `libc::ioctl`、`libc::mknodat` 等 unsafe 调用必须封装在 `src/sys/` 模块中
- **禁止 unwrap/expect/panic**：whiteout 创建失败必须返回正确的 errno（如 EIO、ENOSPC），而不是 panic
- 所有 whiteout 操作使用 workdir + rename 原子模式，避免崩溃导致不一致状态

---

## 相关概念

- [FUSE 与 OverlayFS 基础](00-introduction.md) — OverlayFS 层结构
- [节点与 inode 管理](01-node-inode.md) — DirState 中的 whiteouts 集合
- [Copy-up 三级优化策略](02-copyup.md) — unlink/rmdir/rename 触发 copy-up
- [挂载选项与运行时统计](04-mount-options.md) — 环境变量影响 whiteout 行为
