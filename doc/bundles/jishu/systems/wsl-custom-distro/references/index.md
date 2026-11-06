# 信源、事实与验证（References）

## 事实与洞察

- [事实清单（R 阶段，81 条）](facts.md) — 版本门槛、rootfs、两份配置、OOBE、终端、安装、清单、企业分发与官方建议
- [洞察与模式（I/E 阶段）](insights.md) — 五条四元组洞察、可迁移模式「四段式分发契约」、文档覆盖矩阵
- [核验报告（V 阶段）](verification.md) — P0 矩阵、6 处源页面瑕疵、4 项官方缺口、四视角对抗审查与证据边界

## 官方信源

| 信源 | 地址 | 用途 |
|---|---|---|
| Microsoft Learn 中文页 | <https://learn.microsoft.com/zh-cn/windows/wsl/build-custom-distro> | 主信源（S1） |
| Microsoft Learn 英文页 | <https://learn.microsoft.com/en-us/windows/wsl/build-custom-distro> | 术语与代码块校正（S2） |
| WSL 发布页 | <https://github.com/microsoft/WSL/releases> | 版本 2.4.4 门槛（F-004） |
| 分发清单 | <https://github.com/microsoft/WSL/blob/master/distributions/DistributionInfo.json> | 清单结构（F-050） |
| 旧 appx 打包说明 | <https://github.com/microsoft/WSL-DistroLauncher> | 历史方式（F-005） |
| 导入任意发行版 | <https://learn.microsoft.com/zh-cn/windows/wsl/use-custom-distro> | 容器导出 rootfs 入口（F-014） |
| WSL 配置参考 | <https://learn.microsoft.com/zh-cn/windows/wsl/wsl-config> | `/etc/wsl.conf` 全部设置（F-042） |
| Terminal JSON 片段 | <https://learn.microsoft.com/zh-cn/windows/terminal/json-fragment-extensions> | 终端模板结构（F-035） |

```{toctree}
:hidden:
:maxdepth: 2

facts
insights
verification
```
