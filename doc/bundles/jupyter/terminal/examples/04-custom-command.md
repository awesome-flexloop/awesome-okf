---
type: Example
title: 注册自定义命令与环境配置
description: 通过registerAlias、registerEnvironmentVariable、registerExternalCommand定制shell环境，以及ILiteTerminalAPIClient注入方式
tags: [alias, environment-variable, external-command, custom, configuration, token-injection]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T20:00:00+08:00" }
status: stable
stale_after: 2027-08-22
prerequisites:
  - "了解JupyterLab Token依赖注入机制（参见[插件系统](../concepts/03-plugin-system.md)）"
  - "已阅读[主题同步与设置](../concepts/07-theme-and-settings.md)"
---

# 注册自定义命令与环境配置

本示例演示如何通过ILiteTerminalAPIClient的API注册别名、环境变量和外部命令，为终端shell提供自定义配置。

## 注入ILiteTerminalAPIClient

首先，在你的JupyterLab插件中声明对ILiteTerminalAPIClient的依赖：

```typescript
import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';
// 从@jupyterlite/terminal导入Token
import { ILiteTerminalAPIClient } from '@jupyterlite/terminal';

const myPlugin: JupyterFrontEndPlugin<void> = {
  id: 'my-extension:terminal-config',
  autoStart: true,
  requires: [ILiteTerminalAPIClient],  // 依赖注入
  activate: (app: JupyterFrontEnd, terminalClient: ILiteTerminalAPIClient) => {
    // 在这里配置终端
    setupTerminalConfig(terminalClient);
  }
};

function setupTerminalConfig(client: ILiteTerminalAPIClient) {
  // 注册别名
  client.registerAlias('ll', 'ls -la');
  client.registerAlias('gs', 'git status');
  client.registerAlias('..', 'cd ..');
  client.registerAlias('home', 'cd /drive');
  
  // 注册环境变量
  client.registerEnvironmentVariable('EDITOR', 'vi');
  client.registerEnvironmentVariable('PAGER', 'cat');
}

export default myPlugin;
```

## 注册别名（registerAlias）

别名是命令的快捷方式，类似于bash的alias：

```typescript
// 基本用法
client.registerAlias('ll', 'ls -la');
client.registerAlias('la', 'ls -a');
client.registerAlias('l', 'ls -CF');

// 常用导航别名
client.registerAlias('..', 'cd ..');
client.registerAlias('...', 'cd ../..');
client.registerAlias('drive', 'cd /drive');
client.registerAlias('home', 'cd /home/pyodide');

// Git别名（如果安装了git2cpp）
client.registerAlias('gs', 'git status');
client.registerAlias('ga', 'git add');
client.registerAlias('gc', 'git commit');
client.registerAlias('gp', 'git push');

// 实用别名
client.registerAlias('h', 'history');
client.registerAlias('c', 'clear');
```

在终端中使用：
```bash
$ ll          # 等价于 ls -la
$ drive       # 等价于 cd /drive
$ gs          # 等价于 git status
```

> **覆盖规则**：key重复时后注册的别名覆盖之前的。

## 注册环境变量（registerEnvironmentVariable）

```typescript
// 设置环境变量
client.registerEnvironmentVariable('MY_APP_URL', window.location.origin);
client.registerEnvironmentVariable('API_BASE', '/api');
client.registerEnvironmentVariable('LANG', 'en_US.UTF-8');
client.registerEnvironmentVariable('TERM', 'xterm-256color');

// Git CORS代理（用于git2cpp clone远程仓库）
client.registerEnvironmentVariable(
  'GIT_CORS_PROXY',
  'http://localhost:8881/'
);

// 删除环境变量（传undefined）
client.registerEnvironmentVariable('OLD_VAR', undefined);
```

在终端中验证：
```bash
$ echo $MY_APP_URL
https://your-app.example.com

$ echo $GIT_CORS_PROXY
http://localhost:8881/
```

> **注意**：环境变量对注册后创建的shell生效。已存在的交互式终端需要重新打开才能获取新的环境变量。

## 注册外部命令（registerExternalCommand）

外部命令允许你用JavaScript实现自定义shell命令，使得shell可以调用浏览器API或与其他扩展交互。

### 外部命令IOptions结构

外部命令通过`IExternalCommand.IOptions`注册，结构由@jupyterlite/cockle定义。基本形式如下：

```typescript
interface IExternalCommandOptions {
  name: string;                    // 命令名
  // 其他字段由cockle定义（执行函数、参数定义等）
  // 具体接口请参考@jupyterlite/cockle的类型定义
}
```

### 示例：注册一个通知命令

```typescript
client.registerExternalCommand({
  name: 'notify',
  // 命令实现（具体API由cockle定义，以下为概念示例）
  // execute(args, context) { ... }
} as any);

// 在终端中使用：
// $ notify "Task complete!"
// → 浏览器显示通知
```

> **注意**：`IExternalCommand.IOptions`的具体字段定义在`@jupyterlite/cockle`包中。实际使用时请参考cockle的类型定义和文档。以下示例展示概念用法，具体字段名需根据cockle版本确认。

### 示例：文件格式转换命令

```typescript
// 概念示例：注册一个csv2json命令
client.registerExternalCommand({
  name: 'csv2json',
  // 该命令可以调用JS库将CSV转为JSON
  // 在shell中使用：$ cat data.csv | csv2json > data.json
} as any);
```

## 完整配置插件示例

以下是一个综合示例，在插件启动时为终端配置一组实用别名和环境变量：

```typescript
import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';
import { ILiteTerminalAPIClient } from '@jupyterlite/terminal';

/**
 * 终端配置插件：注册常用别名、环境变量和外部命令
 */
const terminalConfigPlugin: JupyterFrontEndPlugin<void> = {
  id: 'my-extension:terminal-setup',
  autoStart: true,
  requires: [ILiteTerminalAPIClient],
  activate: (app: JupyterFrontEnd, client: ILiteTerminalAPIClient) => {
    
    // === 注册别名 ===
    const aliases: Record<string, string> = {
      // 文件操作
      'll': 'ls -la',
      'la': 'ls -A',
      'l': 'ls -CF',
      
      // 导航
      '..': 'cd ..',
      '...': 'cd ../..',
      'drive': 'cd /drive',
      'tmp': 'cd /tmp',
      
      // 快捷命令
      'c': 'clear',
      'h': 'cockle-config stdin',  // 快速查看stdin模式
      
      // 安全操作（防误删）
      'rm': 'rm -i',
      'cp': 'cp -i',
      'mv': 'mv -i',
    };
    
    for (const [key, value] of Object.entries(aliases)) {
      client.registerAlias(key, value);
    }
    
    // === 注册环境变量 ===
    const envVars: Record<string, string | undefined> = {
      // 终端设置
      'TERM': 'xterm-256color',
      'LANG': 'en_US.UTF-8',
      'EDITOR': 'vi',
      'PAGER': 'cat',
      
      // 应用特定
      'APP_NAME': 'My JupyterLite App',
      'APP_VERSION': '1.0.0',
      'APP_URL': window.location.origin,
      
      // Git CORS代理（开发环境）
      // 'GIT_CORS_PROXY': 'http://localhost:8881/',
    };
    
    for (const [key, value] of Object.entries(envVars)) {
      client.registerEnvironmentVariable(key, value);
    }
    
    console.log('Terminal aliases and environment configured');
  }
};

export default terminalConfigPlugin;
```

## 条件配置

根据环境动态配置：

```typescript
activate: (app, client) => {
  // 开发环境vs生产环境配置
  const isDev = window.location.hostname === 'localhost';
  
  if (isDev) {
    // 开发环境：启用CORS代理
    client.registerEnvironmentVariable(
      'GIT_CORS_PROXY',
      'http://localhost:8881/'
    );
    client.registerAlias('devlog', 'cat /drive/dev.log');
  }
  
  // 检查terminalsAvailable
  if (client.isAvailable) {
    console.log('Terminal is available');
  }
}
```

## 监听终端生命周期

通过terminalDisposed信号追踪终端关闭：

```typescript
client.terminalDisposed.connect((_, shellName) => {
  console.log(`Terminal closed: ${shellName}`);
  // 可以在这里做清理工作
});
```

## 配置影响范围

| 配置类型 | 对已有交互式终端 | 对新交互式终端 | 对新Headless Shell |
|---------|----------------|--------------|-------------------|
| registerAlias | ✅ 生效 | ✅ 生效 | ✅ 生效 |
| registerEnvironmentVariable | ❌ 不回溯 | ✅ 生效 | ✅ 生效（+额外PS1=''） |
| registerExternalCommand | ❌ 不回溯 | ✅ 生效 | ✅ 生效 |

别名在shell级别实时维护，因此对已有shell也生效。环境变量和外部命令在shell启动时加载，只影响新创建的shell。

## 配置顺序建议

在插件activate中，建议按以下顺序配置：

```typescript
activate: (app, client) => {
  // 1. 环境变量（最先，因为别名和命令可能引用环境变量）
  client.registerEnvironmentVariable('MY_VAR', 'value');
  
  // 2. 外部命令（其次，因为别名可能引用外部命令）
  client.registerExternalCommand({ ... });
  
  // 3. 别名（最后，可以引用上面的命令）
  client.registerAlias('mycmd', 'my-external-command --flag');
}
```

## 相关概念

- [主题同步与设置](../concepts/07-theme-and-settings.md)：全局配置API详解
- [插件系统](../concepts/03-plugin-system.md)：Token依赖注入机制
- [LiteTerminalAPIClient API参考](../references/client-source.md)：完整API签名
- [执行shell命令](02-execute-shell-command.md)：编程式命令调用
