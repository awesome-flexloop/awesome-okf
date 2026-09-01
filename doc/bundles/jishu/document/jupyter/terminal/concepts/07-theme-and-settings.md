---
type: Concept
title: 主题同步与设置
description: JupyterLab暗色/亮色主题同步到终端、终端主题设置监听、全局配置（别名、环境变量、外部命令）
tags: [theme, dark-mode, light-mode, settings, alias, environment-variable, external-command]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T20:00:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: plugin-source
    resource: /references/plugin-source.md
    title: 插件系统源码信源
  - id: client-source
    resource: /references/client-source.md
    title: LiteTerminalAPIClient API信源
---

# 主题同步与设置

JupyterLite Terminal 通过 terminalThemeChangePlugin 实现主题自动同步，同时提供全局配置API（别名、环境变量、外部命令）供其他扩展定制shell行为。

## 主题同步机制

主题同步有两条路径，分别响应不同的变化事件。

### 路径1：全局主题变化（暗色/亮色切换）

当用户切换JupyterLab全局主题时（如从JupyterLab Light切换到JupyterLab Dark），且终端主题设置为`'inherit'`时：

```typescript
themeManager?.themeChanged.connect(async (_, changedArgs) => {
  if (terminalTheme === 'inherit') {
    const isDarkMode = !themeManager.isLight(changedArgs.newValue);
    liteTerminalAPIClient.themeChange(isDarkMode);
  }
});
```

1. 监听`IThemeManager.themeChanged`信号
2. 检查当前终端主题是否为`'inherit'`（继承全局主题）
3. 通过`themeManager.isLight(newTheme)`判断是否暗色模式
4. 调用`liteTerminalAPIClient.themeChange(isDarkMode)`通知所有shell

**条件**：只有当终端主题设置为`'inherit'`时，全局主题切换才会同步到终端。用户也可以在终端设置中选择固定的暗色/亮色主题，此时不受全局主题变化影响。

### 路径2：终端主题设置变化

当用户通过 JupyterLab Settings → Terminal 菜单修改终端主题时：

```typescript
settingRegistry.load('@jupyterlab/terminal-extension:plugin').then(setting => {
  terminalTheme = setting.composite.theme as string;
  setting.changed.connect(() => {
    const newTerminalTheme = setting.composite.theme as string;
    if (newTerminalTheme !== terminalTheme) {
      liteTerminalAPIClient.themeChange();
      terminalTheme = newTerminalTheme;
    }
  });
});
```

1. 加载`@jupyterlab/terminal-extension:plugin`设置（JupyterLab内置终端扩展的设置）
2. 缓存当前主题值
3. 监听设置的`changed`信号
4. 比较新主题是否与旧主题不同
5. 如果不同，调用`themeChange()`（不传isDarkMode参数，shell自行从设置读取）
6. 更新缓存

### themeChange() 实现

```typescript
themeChange(isDarkMode?: boolean): void {
  for (const [, shell] of Private.shells) {
    shell.themeChange(isDarkMode);
  }
}
```

遍历所有**交互式终端shell**（存储在Private.shells中），逐个通知主题变化。Headless shell不涉及UI渲染，不需要主题通知。

### IThemeManager是optional依赖

```typescript
optional: [IThemeManager]
```

`themeManager?.themeChanged`使用了可选链——如果IThemeManager不可用（如极简JupyterLite部署中不包含主题管理器），全局主题监听静默跳过，但终端设置变化监听仍然正常工作。

## 终端主题设置选项

JupyterLab终端设置中的theme选项通常包括：

| 值 | 行为 |
|----|------|
| `'inherit'` | 跟随JupyterLab全局主题（暗色/亮色自动切换） |
| `'dark'` | 始终使用暗色终端 |
| `'light'` | 始终使用亮色终端 |

## 全局配置API

LiteTerminalAPIClient提供三个全局配置方法，配置对所有shell生效（包括已存在的和后续创建的）。

### registerAlias

```typescript
registerAlias(key: string, value: string): void
```

注册命令别名，类似于bash的`alias`命令。

```typescript
// 示例：注册常用别名
terminalClient.registerAlias('ll', 'ls -la');
terminalClient.registerAlias('gs', 'git status');
```

- key重复时覆盖原有别名
- 别名存储在客户端的`_aliases`对象中
- shell创建时（createShell/createHeadlessShell）自动应用别名
- 对已运行的shell也生效（别名在shell级别维护）

### registerEnvironmentVariable

```typescript
registerEnvironmentVariable(key: string, value: string | undefined): void
```

注册环境变量。value为undefined时删除该变量。

```typescript
// 示例：设置环境变量
terminalClient.registerEnvironmentVariable('EDITOR', 'vi');
terminalClient.registerEnvironmentVariable('GIT_CORS_PROXY', 'http://localhost:8881/');
terminalClient.registerEnvironmentVariable('OLD_VAR', undefined);  // 删除
```

- 环境变量存储在`_environment`对象中
- 创建shell时合并environment（headless shell还会额外设置PS1: ''）
- 注意：对已运行的shell设置新环境变量不会回溯生效——只影响后续创建的shell

### registerExternalCommand

```typescript
registerExternalCommand(options: IExternalCommand.IOptions): void
```

注册外部命令，扩展shell的命令能力。

```typescript
terminalClient.registerExternalCommand({
  name: 'my-command',
  // ...命令定义（由cockle定义IOptions结构）
});
```

- 命令添加到`_externalCommands`数组
- shell启动时加载所有已注册的外部命令
- 可以用此机制在shell中调用JavaScript功能（如调用浏览器API、与其他扩展交互）

## isAvailable开关

LiteTerminalAPIClient通过PageConfig检查终端是否启用：

```typescript
get isAvailable(): boolean {
  return PageConfig.getOption('terminalsAvailable') === 'true';
}
```

这由`jupyter-lite.json`中的`terminalsAvailable: true`配置。如果为false，JupyterLab不会显示终端菜单，插件虽然激活但功能不可用。

## 配置优先级

| 配置层级 | 位置 | 影响范围 |
|---------|------|---------|
| 站点级配置 | jupyter-lite.json | terminalsAvailable开关 |
| 全局API设置 | registerAlias/EnvironmentVariable/ExternalCommand | 所有shell |
| 会话级配置 | headless shell的environment参数 | 单个shell实例 |
| shell内命令 | shell中直接执行export/alias | 仅当前shell（关闭后丢失） |

## 扩展定制示例

在自定义JupyterLite扩展中定制终端配置：

```typescript
const myPlugin: JupyterFrontEndPlugin<void> = {
  id: 'my-extension:terminal-config',
  autoStart: true,
  requires: [ILiteTerminalAPIClient],
  activate: (app, terminalClient) => {
    // 注册别名
    terminalClient.registerAlias('ll', 'ls -la');
    terminalClient.registerAlias('..', 'cd ..');
    
    // 设置环境变量
    terminalClient.registerEnvironmentVariable('MY_APP_URL', window.location.origin);
    
    // 注册自定义外部命令
    terminalClient.registerExternalCommand({
      name: 'open-browser',
      // ...
    });
  }
};
```

## 相关概念

- [插件系统](03-plugin-system.md)：terminalThemeChangePlugin详细实现
- [安装与快速开始](01-getting-started.md)：jupyter-lite.json配置
- [示例：自定义外部命令](../examples/04-custom-command.md)：外部命令注册示例
- [LiteTerminalAPIClient API参考](../references/client-source.md)：完整方法签名
