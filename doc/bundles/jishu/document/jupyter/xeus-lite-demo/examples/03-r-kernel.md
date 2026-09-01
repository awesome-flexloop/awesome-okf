---
type: Example
title: 使用 R 内核进行统计分析
description: 配置 xeus-r 内核，在 JupyterLite 中运行 R 语言代码，使用 tidyverse 进行数据处理和可视化
tags: [r, statistics, xeus-r, tidyverse, data-analysis, ggplot2]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T20:05:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: readme
    resource: /references/readme-source.md
    title: README 使用说明信源
---

## 目标

在 JupyterLite 中配置 R 语言内核（xeus-r），使用 tidyverse 进行统计分析和 ggplot2 可视化。

## 步骤1：配置 environment.yml

编辑 `environment.yml`，添加 xeus-r 和 R 包：

```yaml
name: xeus-kernel
channels:
  - https://repo.prefix.dev/emscripten-forge-dev
  - https://repo.prefix.dev/conda-forge
dependencies:
  - xeus-r
  - r-tidyverse
```

如果想同时保留 Python 内核，可以同时安装：

```yaml
name: xeus-kernel
channels:
  - https://repo.prefix.dev/emscripten-forge-dev
  - https://repo.prefix.dev/conda-forge
dependencies:
  - xeus-python
  - xeus-r
  - numpy
  - matplotlib
  - r-tidyverse
```

> 💡 R 包在 conda 中以 `r-` 前缀命名。例如 `tidyverse` → `r-tidyverse`，`ggplot2` → `r-ggplot2`。

## 步骤2：提交并等待构建

1. Commit changes 到 main 分支
2. 等待 GitHub Actions 构建完成（R 环境构建时间较长，约5-10分钟）
3. 刷新站点

## 步骤3：创建 R Notebook

1. 在 JupyterLite 中，点击 **File** → **New** → **Notebook**
2. 内核选择 **XR**（R 内核）
3. 等待内核启动（首次启动 R 内核可能需要较长时间）

## 步骤4：测试 R 代码

### 基础验证

```r
# R 版本信息
R.version.string

# 简单计算
x <- c(1, 2, 3, 4, 5)
mean(x)
sd(x)
```

### 使用 ggplot2 绘图

```r
library(ggplot2)

# 创建示例数据
data <- data.frame(
  x = rnorm(100),
  y = rnorm(100),
  category = sample(c("A", "B", "C"), 100, replace = TRUE)
)

# 散点图
ggplot(data, aes(x = x, y = y, color = category)) +
  geom_point(size = 2, alpha = 0.7) +
  geom_smooth(method = "lm", se = FALSE) +
  theme_minimal() +
  labs(title = "Scatter Plot with Regression Lines",
       x = "Variable X", y = "Variable Y")
```

### 使用 dplyr 数据处理

```r
library(dplyr)

# 创建示例数据框
df <- data.frame(
  group = rep(c("Control", "Treatment"), each = 50),
  value = c(rnorm(50, mean = 10, sd = 2),
            rnorm(50, mean = 12, sd = 2))
)

# 分组统计
df %>%
  group_by(group) %>%
  summarise(
    n = n(),
    mean = mean(value),
    sd = sd(value),
    se = sd / sqrt(n)
  )
```

### 统计检验

```r
# t 检验
t_test_result <- t.test(value ~ group, data = df)
print(t_test_result)
```

## README 示例：coursekata 教学包

README 中提供了 coursekata（统计学教学包）的配置示例：

```yaml
name: xeus-kernel
channels:
  - https://repo.prefix.dev/emscripten-forge-dev
  - https://repo.prefix.dev/conda-forge
dependencies:
  - xeus-r
  - r-coursekata
```

coursekata 是专为统计教学设计的 R 包集合，包含多个常用统计教学包。

## R 包可用性

| R 包 | conda 名 | WASM 可用性 |
|------|---------|------------|
| tidyverse | r-tidyverse | ✅ 可用 |
| ggplot2 | r-ggplot2 | ✅ 可用（含在 tidyverse 中） |
| dplyr | r-dplyr | ✅ 可用（含在 tidyverse 中） |
| tidyr | r-tidyr | ✅ 可用（含在 tidyverse 中） |
| readr | r-readr | ✅ 可用（含在 tidyverse 中） |
| stringr | r-stringr | ✅ 可用（含在 tidyverse 中） |
| forcats | r-forcats | ✅ 可用（含在 tidyverse 中） |
| tibble | r-tibble | ✅ 可用（含在 tidyverse 中） |
| purrr | r-purrr | ✅ 可用（含在 tidyverse 中） |
| coursekata | r-coursekata | ✅ 可用 |
| shiny | r-shiny | ❌ 不可用（需要服务器端） |
| data.table | r-data.table | ⚠️ 需验证 |

## R Notebook 使用技巧

1. **内核启动时间**：R 内核首次启动比 Python 慢，这是正常的（需要加载更多基础包）
2. **绘图输出**：ggplot2 图表直接在 cell 输出中显示
3. **数据框显示**：data.frame 和 tibble 会以表格形式漂亮输出
4. **帮助文档**：在函数名前加 `?` 查看帮助，如 `?mean`
5. **多内核切换**：如果同时安装了 Python 和 R，可以在 Kernel → Change Kernel 中切换

## 注意事项

- R WASM 环境的包可用性不如 Python 广泛，建议以 tidyverse 为核心
- 复杂的 R 包（包含大量 C/Fortran 代码）可能没有 WASM 构建
- 安装 r-tidyverse 会显著增加站点体积（约 40-50MB）
- R 内核的内存限制与 Python 相同，受浏览器内存约束

## 相关概念

- [多语言内核支持](../concepts/07-kernel-options.md) — 其他内核选项
- [运行时环境配置](../concepts/04-runtime-env-config.md) — environment.yml 配置
- [Python 科学计算环境](02-numpy-matplotlib.md) — Python 环境配置
- [C++ 内核配置](04-cpp-kernel.md) — C++ 交互编程
