# 示例索引（Examples）

本目录包含 Pillow 的完整可运行示例，全部基于 2020 年前后教程（简书连载《matplotlib & pillow & networkx 手册》）。

## 示例列表

| 文档 | 覆盖内容 |
|------|---------|
| [手绘/石雕/油画特效](00-hand-drawn-effects.md) | 灰度/三通道梯度重构、虚拟光源模拟、归一化与灰度值裁剪重构图像（F-170~F-176） |
| [模拟电子显示屏](01-electronic-display.md) | 读取图像尺寸、按间距计算行列数、嵌套循环绘制网格并保存（F-198~F-200） |

## 运行环境

- Python 3.10+
- Pillow（教程为 7.x 时代，8.x/9.x 兼容）
- NumPy（仅手绘/石雕/油画示例的 `np.gradient` 需要）
- 中文字体渲染依赖系统字体（Windows 自带 `simkai.ttf`/`simsun.ttc`）

```{toctree}
:hidden:
:maxdepth: 7

00-hand-drawn-effects
01-electronic-display
```
