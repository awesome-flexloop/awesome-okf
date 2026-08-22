# 源码信源

本章节登记 JupyterLab Desktop 主进程的核心源码文件，每个信源文档包含：文件职责、关键函数/类签名、核心逻辑说明、相关概念链接。

## 信源文档列表

| 信源 | 源码文件 | 说明 |
|------|---------|------|
| [应用入口](main-source.md) | `src/main/main.ts` | 应用入口、生命周期、Snap修复、单实例锁、CLI解析、捆绑环境更新 |
| [主应用类](app-source.md) | `src/main/app.ts` | JupyterApplication 类、SessionWindowManager 窗口管理器、事件注册、自动更新 |
| [Jupyter服务器](server-source.md) | `src/main/server.ts` | JupyterServer 类（启停/进程管理/自动重启）、JupyterServerFactory 工厂模式 |
| [Python环境工具](env-source.md) | `src/main/env.ts` | 环境验证、conda/venv路径处理、版本检查、环境信息获取、命令执行 |
| [CLI命令](cli-source.md) | `src/main/cli.ts` | yargs 配置、env/config/appdata/logs 子命令、环境创建逻辑 |
| [设置系统](settings-source.md) | `src/main/config/settings.ts` | SettingType 枚举、Setting泛型类、UserSettings/WorkspaceSettings 双层设置 |
| [核心类型](tokens-source.md) | `src/main/tokens.ts` | IPythonEnvironment、ICLIArguments、IDisposable、IRect、IEnvironmentType |
| [会话窗口](sessionwindow-source.md) | `src/main/sessionwindow/sessionwindow.ts` | SessionWindow 类、ContentViewType、LabView加载、环境切换、标题栏管理 |
| [事件系统](event-source.md) | `src/main/eventtypes.ts` + `eventmanager.ts` | EventTypeMain/Renderer 枚举、EventManager IPC事件注册/注销/分发 |
| [导航安全](navigation-source.md) | `src/main/navigationguard.ts` | 全局导航守卫、WebContents声明、外部链接处理、WebView阻止 |
| [环境注册表](registry-source.md) | `src/main/registry.ts` | Registry 类、环境发现（PATH/Conda/注册表）、环境排序、运行服务器列表 |
| [应用数据与会话配置](config-source.md) | `src/main/config/appdata.ts` + `sessionconfig.ts` | ApplicationData 单例持久化、SessionConfig 本地/远程会话配置、序列化 |

---

**导航：**
- [核心概念](../concepts/index.md) — 概念文档
- [示例文档](../examples/index.md) — 实战示例
- [返回首页](../index.md)
