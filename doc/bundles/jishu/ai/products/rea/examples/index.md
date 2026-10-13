# REA 实操示例

共 8 篇。REA 命令经固定源码与官方文档核对，未本机实跑；Notes formatter、官网教学算法已独立执行。需要真实目标、Evidence 或 scenario 的调用保留接口示意说明，不将它们称作完整重建。

| 示例 | 内容 |
|------|------|
| [CLI 与 MCP 使用示例](cli-and-mcp-usage.md) | `npx rea-agents setup`、`rea analyze <path>`、`rea doctor` 等单次命令 + 接入 agent 客户端的 MCP 配置要点 |
| [分析工具安装与 Provider 接入](provider-setup.md) | Ghidra/IDA/Hopper/JADX/ADB/EVM/WASM/固件工具链本地准备与 doctor 校验 |
| [JavaScript 应用重建示例](js-reconstruction-example.md) | `analyze_javascript_application` + 应用图 + 运行时观测/协同 + Web 源定位的实际走查（F-067~F-077） |
| [平台深层分析示例](platform-deep-example.md) | Apple/Electron/HarmonyOS/Android/固件 代表性 CLI 命令、环境变量与资源限制（F-103~F-118） |
| [重建工程工作流示例](reconstruction-workflow-example.md) | 9 阶段判据与合法空台账请求，非完整工程复现（F-129~F-131） |
| [官方 showcase 逆向重建案例](showcase-cases-example.md) | DX-Ball / Notion / TH04 / Aegis / CTF 五案例的检查对象与剩余义务 |
| [Notes 首次调查](notes-first-investigation.md) | 静态 IPC 与 CSV 文件路径；独立 formatter 验证，不启动 Electron |
| [官网教学实验](official-site-labs.md) | 计算器、恐龙、公开测试 key 的 TOTP；固定输入与教学归属 |

```{toctree}
:maxdepth: 2
:hidden:

cli-and-mcp-usage
provider-setup
js-reconstruction-example
platform-deep-example
reconstruction-workflow-example
showcase-cases-example
notes-first-investigation
official-site-labs
```
