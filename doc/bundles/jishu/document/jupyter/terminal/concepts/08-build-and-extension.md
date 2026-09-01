---
type: Concept
title: 构建系统与扩展开发
description: TypeScript+Rspack+JupyterBuilder构建流程、Python包构建、WASM资源处理、开发模式和自定义扩展开发
tags: [build, rspack, typescript, jupyter-builder, hatch, wasm, extension-development]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T20:00:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: metasource
    resource: /references/metasource.md
    title: 项目元信源
  - id: python-source
    resource: /references/python-source.md
    title: Python端源码信源
---

# 构建系统与扩展开发

JupyterLite Terminal 使用多阶段构建系统：TypeScript编译 → Rspack打包Worker → JupyterBuilder构建labextension → Python wheel打包（含WASM资源）。

## 构建流程总览

```
源码(ts/tsx/css)
    │
    ├── 1. TypeScript编译 (tsc)
    │       ↓
    │   lib/*.js + lib/*.d.ts
    │       │
    │       ├── 2. Rspack打包Worker
    │       │       ↓
    │       │   lib/coincident.worker.js
    │       │   lib/comlink.worker.js
    │       │
    │       └── 3. JupyterBuilder (integrity)
    │               ↓
    │           jupyterlite_terminal/labextension/
    │           (package.json + static/*.js)
    │
    └── 4. Python构建 (hatch + hatch-jupyter-builder)
            ↓
        dist/jupyterlite_terminal-*.whl
        (包含labextension + install.json)
            │
            └── 5. JupyterLite构建 (post_build hook)
                    ↓
                _output/extensions/@jupyterlite/terminal/static/wasm/
                (cockle WASM文件)
```

## npm scripts详解

| 命令 | 具体执行 | 用途 |
|------|---------|------|
| `build` | `npm run build:lib && npm run build:worker && npm run build:dev` | 开发构建 |
| `build:prod` | `npm run clean && npm run build:lib:prod && npm run build:worker:prod && npm run build:labextension` | 生产构建 |
| `build:lib` | `tsc --build` | TypeScript编译（sourceMap） |
| `build:lib:prod` | `tsc --build --sourceMap=false` | 生产编译（无sourceMap） |
| `build:worker` | `rspack build --config ./worker.rspack.config.js -m development` | Worker打包（dev模式） |
| `build:worker:prod` | `rspack build --config ./worker.rspack.config.js -m production` | Worker打包（prod模式） |
| `build:dev` | `jupyter labextension build . --development` | labextension开发构建 |
| `build:labextension` | `jupyter labextension build .` | labextension生产构建 |
| `watch` | `run-p watch:lib watch:labextension` | 并行监听tsc和labextension |
| `watch:lib` | `tsc -w --build` | TS增量编译 |
| `watch:labextension` | `jupyter-builder watch .` | labextension增量构建 |
| `clean` | `rimraf lib tsconfig.tsbuildinfo jupyterlite_terminal/labextension` | 清理构建产物 |
| `install:extension` | `jupyter labextension develop . --overwrite` | 开发模式链接 |

## TypeScript配置

tsconfig.json目标ES2022，使用references配置：

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ES2022",
    "moduleResolution": "bundler",
    "lib": ["ES2022", "DOM", "WebWorker"],
    "strict": true,
    "declaration": true,
    "sourceMap": true,
    "composite": true
  },
  "include": ["src/**/*.ts", "src/**/*.tsx"],
  "exclude": ["src/**/*.spec.ts", "src/**/__tests__/**"]
}
```

- `lib: ["DOM", "WebWorker"]`：同时支持主线程DOM和Worker环境类型
- `composite: true`：支持TypeScript项目引用和增量构建

## Worker独立打包

Worker需要单独打包（worker.rspack.config.js），因为它们运行在独立的Worker上下文中：

- 入口：`lib/coincident.worker.js` 和 `lib/comlink.worker.js`（tsc编译后的JS）
- 输出：`lib/[name].js`（Worker bundle）
- `globalObject: 'self'`：Worker中全局对象是self而非window
- `resolve.fallback`：禁用fs/child_process/crypto等Node.js模块
- 需要先执行`build:lib`（tsc）再`build:worker`（rspack）

## JupyterBuilder（labextension构建）

`jupyter labextension build .`命令使用JupyterBuilder处理：
1. 构建前端资源（js/css打包、代码分割）
2. 生成`jupyterlite_terminal/labextension/`目录
3. 创建`package.json`（包含extension元数据）
4. 生成`static/`目录（包含打包后的JS bundle和style.js）
5. 运行integrity校验（文件hash用于缓存）

产物结构：
```
jupyterlite_terminal/labextension/
├── package.json          # 扩展元数据
├── install.json          # 安装信息
└── static/
    ├── 123main.js        # 主代码bundle（hash命名）
    ├── 456remoteEntry.js # Module Federation入口
    ├── style.js          # 样式入口
    └── coincident.worker.js, comlink.worker.js  # Worker文件
```

## Python包构建

使用hatchling作为构建后端，配合hatch-jupyter-builder和hatch-nodejs-version插件。

### 版本同步

```toml
[tool.hatch.version.hook]
path = "jupyterlite_terminal/_version.py"

[tool.hatch.build.hooks.version]
path = "package.json"
```

hatch-nodejs-version从package.json读取版本号，写入`_version.py`，确保Python包和npm包版本一致。

### 构建钩子

```toml
[tool.hatch.build.hooks.jupyter-builder]
dependencies = ["hatch-jupyter-builder>=0.5"]
build-function = "hatch_jupyter_builder.npm_builder"
ensured-targets = [
    "jupyterlite_terminal/labextension/static/style.js",
    "jupyterlite_terminal/labextension/package.json",
]
build-kwargs = { build_cmd = "build:prod", npm = ["jlpm"] }
```

- 构建Python wheel时自动执行`jlpm build:prod`
- 确保目标文件存在（验证前端构建成功）
- editable模式（pip install -e）使用`install:extension`命令

### Wheel共享数据

labextension静态资源通过shared-data打包到wheel中：

```toml
[tool.hatch.build.targets.wheel.shared-data]
"jupyterlite_terminal/labextension" = "share/jupyter/labextensions/@jupyterlite/terminal"
"install.json" = "share/jupyter/labextensions/@jupyterlite/terminal/install.json"
```

安装wheel后，文件位于Python环境的`share/jupyter/labextensions/@jupyterlite/terminal/`目录，JupyterLab/JupyterLite可以自动发现。

## JupyterLite构建插件（TerminalAddon）

jupyterlite_terminal/add_on.py中的TerminalAddon是JupyterLite构建时的post_build钩子，负责将cockle WASM文件复制到输出目录。

### post_build执行流程

```
1. 确定cockle prepare_wasm.js路径
   ├── 已安装？→ node_modules/@jupyterlite/cockle/lib/tools/prepare_wasm.js
   └── 未安装？→ 临时npm install到.cockle_temp/
   
2. 运行 prepare_wasm.js --list
   → 输出文件列表到cockle-files.txt
   → 格式：每行source路径，下一行packageName

3. yield copy actions
   → 对每个文件：copy_one(source, assetDir/packageName/basename)

4. 清理临时文件
```

### 为什么需要post_build

cockle的WASM文件（.wasm和.data文件）不在jupyterlite-terminal的npm包中，而是在`@jupyterlite/cockle`依赖中。构建JupyterLite站点时，需要将这些WASM文件复制到最终输出目录，以便Worker可以在运行时加载它们。

TerminalAddon自动处理这个过程，无需用户手动复制文件。

## 开发模式

### 前端开发（配合JupyterLab）

```bash
# 1. 克隆并安装
git clone https://github.com/jupyterlite/terminal.git
cd terminal
pip install -e "."
jlpm install

# 2. 链接到JupyterLab开发环境
jupyter labextension develop . --overwrite

# 3. 启动TypeScript监听（终端1）
jlpm watch

# 4. 启动JupyterLab（终端2）
jupyter lab
```

修改src/下的TypeScript文件后，tsc自动重新编译，jupyter-builder自动重建labextension，刷新浏览器即可看到变化。

### JupyterLite站点开发

```bash
# 在deploy目录下
cd deploy
jupyter lite build --contents contents
jupyter lite serve
```

修改源码后需要重新执行`jlpm build:prod`（或在watch模式下自动构建），然后重新运行`jupyter lite build`。

## 扩展开发指南

### 基本项目结构

如果你要开发一个类似的JupyterLite终端扩展：

```
my-terminal/
├── src/
│   ├── index.ts            # 插件入口
│   ├── tokens.ts           # Token定义
│   ├── client.ts           # API客户端
│   ├── shell.ts            # Shell实现
│   ├── exec.ts             # 编程式命令（可选）
│   └── *.worker.ts         # Web Worker
├── style/
│   └── base.css            # 样式
├── my_terminal/            # Python包
│   ├── __init__.py         # 入口+labextension路径
│   └── add_on.py           # JupyterLite构建钩子（如需WASM复制）
├── package.json            # npm元数据+scripts
├── pyproject.toml          # Python元数据+构建配置
├── tsconfig.json           # TS配置
├── worker.rspack.config.js # Worker打包配置
└── install.json            # JupyterLab扩展安装信息
```

### 关键API扩展点

| 扩展点 | 方法 | 用途 |
|--------|------|------|
| 自定义Shell | 继承TerminalShell，重写createShell() | 自定义Worker初始化、文件系统等 |
| 自定义APIClient | 继承LiteTerminalAPIClient | 重写startNew、createShell等方法 |
| 外部命令 | registerExternalCommand() | 添加shell可调用的JS命令 |
| 别名/环境变量 | registerAlias/registerEnvironmentVariable() | 预设shell环境 |
| 编程式命令 | 通过CommandRegistry | 添加新的app.commands |

### 子类化LiteTerminalAPIClient

```typescript
class MyTerminalClient extends LiteTerminalAPIClient {
  protected async createShell(options: ITerminalShell.IOptions): Promise<ITerminalShell> {
    // 自定义shell创建逻辑
    const shell = await super.createShell(options);
    // 额外初始化...
    return shell;
  }
}
```

在插件activate中使用子类替换默认实现。

### Worker自定义

如需自定义Worker行为，可以基于coincident.worker.ts/comlink.worker.ts创建自己的Worker：

1. 继承CoincidentShellWorker或ComlinkShellWorker
2. 重写initDriveFS添加自定义文件系统
3. 在initProxy中添加自定义proxy方法
4. 在主线程TerminalShell子类的createRemote中设置回调

### CSS样式

style/index.css是样式入口，默认@import base.css。可以在base.css中添加自定义样式覆盖xterm.js默认样式。

## 测试

| 测试类型 | 位置 | 运行命令 |
|---------|------|---------|
| 单元测试 | src/__tests__/ | `jlpm test` (Jest) |
| E2E测试 | ui-tests/ | Playwright（需要先启动JupyterLite） |

## 相关概念

- [插件系统](03-plugin-system.md)：插件定义和依赖注入
- [安装与快速开始](01-getting-started.md)：开发模式安装步骤
- [Shell与Worker机制](04-shell-and-worker.md)：Worker打包原因
- [Python端源码信源](../references/python-source.md)：TerminalAddon完整实现
- [项目元信源](../references/metasource.md)：完整依赖和构建配置
