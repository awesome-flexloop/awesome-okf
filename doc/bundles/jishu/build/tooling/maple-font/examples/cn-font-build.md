---
type: Example
title: "中英文字体构建"
description: "下载 Resource Han Rounded 中文基字体并合并得到完整中日韩支持版本"
tags: ["maple-mono", "cjk", "chinese", "resource-han", "font-merge"]
sources:
  - id: BUILD-CN
    resource: "build.py#build_cn"
    description: "CN 构建函数——下载、合并、宽度调整"
  - id: CN-README
    resource: "source/cn/README.md"
    description: "中文基字体说明"
  - id: CONFIG-CN
    resource: "config.json#cn"
    description: "cn 配置段默认值"
prerequisites:
  - "basic-build.md"
  - "../concepts/07-cn-font-merge.md"
status: draft
---

# 示例 4：中英文字体构建

本示例展示如何构建带完整中日韩支持的 Maple Mono CN 版——下载 Resource Han Rounded 基字体、合并、调整 2:1 宽度对齐。

## 快速构建

```bash
python build.py --cn
```

这条命令会：
1. 检查本地是否有中文基字体（`source/cn/` 下）
2. 如果没有，从 GitHub Release 下载 `cn-base-static.zip`（约 40MB）
3. 解压并 SHA256 校验
4. merge_ttfonts 合并拉丁基字体与中文基字体
5. 调整中文字形宽度为 2× 拉丁宽度

**预期输出**：

```
fonts/
├── CN/
│   ├── MapleMono-CN-Regular.ttf      ← 中英合并版
│   ├── MapleMono-CN-Bold.ttf
│   └── ...
└── Variable/
    ├── MapleMono-CN-VF.ttf           ← CN 版变量字体
    └── ...
```

## 配置选项

### cn.enable（开关）

```bash
python build.py --cn   # 启用
python build.py --no-cn  # 禁用（默认）
```

### cn.narrow（窄中文模式）

```bash
# 中文字形宽度压缩为 1.5×（视觉更紧凑但不再严格等宽）
python build.py --cn --cn-narrow
```

### cn.scale_factor（精细缩放）

```json
{
  "cn": {
    "enable": true,
    "scale_factor": [1.15, 1.0]  // 宽度 1.15×，高度 1.0×
  }
}
```

或通过 config.json 直接配置：

```json
{
  "cn": {
    "enable": true,
    "narrow": false,
    "scale_factor": 1.0,
    "use_static_base_font": true,
    "with_nerd_font": false
  }
}
```

## 同时构建 CN + NF

```bash
python build.py --cn --nf

# 或配置
{
  "cn": {"enable": true, "with_nerd_font": true},
  "nerd_font": {"enable": true}
}
```

产物额外包含：

```
fonts/
└── NF-CN/
    └── MapleMono-NF-CN-Regular.ttf  ← 图标 + 中日韩
```

## 从变量字体重建中文基字体

默认用预构建静态基字体。如果需要最新版 Resource Han Rounded：

```bash
# 拉取 Resource Han Rounded 变量字体
python task.py cn --pull

# 从变量字体实例化出各字重静态包
python task.py cn --rebuild
```

这会重新调用 robofont 或 fontParts 实例化变量字体，比较慢但保证版本最新。

## 哈希校验与版本锁定

Maple Mono 用 `source/cn/static.sha256` 锁定中文基字体版本：

```
# static.sha256 内容示例
abc123def456...  cn-base-static.zip
```

每次构建 CN 版时，先下载 zip 再校验 SHA256。如果校验不通过：
- 下载损坏
- 版本不匹配（本地 config.json 期望的版本与下载的不一致）

手动更新哈希：

```bash
python task.py cn --update-hash
```

## 实战：VS Code 中日韩编码环境

配置 VS Code 使用 Maple Mono CN 版，实现中英混排等宽：

### step 1：构建

```bash
# narrow 中文 + NF 图标 + cv01 品牌化 + slim 宽度
python build.py --cn --nf --cn-narrow --width slim --feat cv01
```

### step 2：安装

```bash
cp fonts/CN/Variable/MapleMono-CN-VF.ttf ~/Library/Fonts/
```

### step 3：VS Code 设置

```json
// .vscode/settings.json
{
  "editor.fontFamily": "Maple Mono CN, Menlo, Monaco, 'Courier New'",
  "editor.fontSize": 14,
  "editor.fontLigatures": true,
  "terminal.integrated.fontFamily": "Maple Mono NF CN"
}
```

### step 4：验证

打开包含中文注释的 Python 文件：

```python
# 这是一个计算矩阵乘法的示例
def matmul(A, B):
    # A: m×n, B: n×p → C: m×p
    C = [[0 for _ in range(len(B[0]))] for _ in range(len(A))]
    for i in range(len(A)):
        for j in range(len(B[0])):
            for k in range(len(B)):
                C[i][j] += A[i][k] * B[k][j]
    return C  # 返回结果矩阵
```

中文注释应该正确显示、等宽对齐（narrow 模式下可能略有偏差）。

## 性能影响

| 构建类型 | 字重数 | 预期耗时（pool_size=4） |
|---------|--------|------------------------|
| 基础 TTF | 9 | ~6s |
| NF 版 | 9 | ~10s |
| **CN 版** | 9 | **~20s** |
| NF-CN 版 | 9 | ~28s |

CN 版最慢的原因：
1. merge_ttfonts 需要处理 28000+ 中文字形（35× 拉丁数量）
2. 中文字形宽度调整
3. OS/2 表重算

## 常见问题

### 中文下载慢或失败？

换 GitHub 镜像：

```json
"github_mirror": "mirror.ghproxy.com"
```

或手动下载 `cn-base-static.zip` 放到 `source/cn/` 目录下。

### CN 版不是等宽字体？

用了 `--cn-narrow` 后确实不再严格等宽。配置里有明确的风险提示。如果要严格等宽，不要用 narrow 模式。

### 部分生僻字显示为方块？

Maple Mono CN 版基于 Resource Han Rounded，覆盖约 28000 字形。非常生僻的 CJK 扩展 B-E 区可能缺失。可以考虑用更大的基字体（如 Noto Sans CJK SC）重新构建。

### 中文看起来太小/太大？

调整 `cn.scale_factor`：
```json
"cn": {"scale_factor": [1.2, 1.1]}
```
第一个值控制宽度，第二个值控制高度。
