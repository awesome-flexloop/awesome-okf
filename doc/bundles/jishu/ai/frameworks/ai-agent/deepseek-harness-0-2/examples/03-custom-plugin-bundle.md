---
type: example
title: "编写并安装自己的插件与组合包"
description: "从零写一个 dsh 插件与组合包：package.json 清单、cordis.patch.yml、插件行按包名引用、dsh plugin 安装与本地开发热重载流程。"
tags: [deepseek-harness, plugin, bundle, example, plugin-dev]
generated: { by: "process:seven-concepts-cmd+source-code-to-okf-wiki", at: "2026-10-22T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-10-22T00:00:00+08:00" }
status: stable
stale_after: 2027-04-22
sources:
  - id: dsh-upstream
    resource: https://github.com/deepseek-ai/deepseek-harness
    title: DeepSeek Harness 官方仓库 docs/user/develop/basic/publish.zh.md 与 docs/cookbook/adding-a-package
---

# 编写并安装自己的插件与组合包

> 场景：把一组插件 + 配置打成可分发的组合包，用 `dsh plugin` 装进任意 profile。

## 1. 插件的三种形态

```ts
// ① 函数式
export const name = 'my-plugin'
export const inject = ['tools']
export function apply(ctx: Context, config: Config) { /* ... */ }

// ② 对象式
export default { name: 'my-plugin', inject: ['tools'], apply(ctx, config) { /* ... */ } }

// ③ 类式（继承 Service）
export default class MyPlugin extends Service {
  static inject = ['tools']
  constructor(ctx: Context, config: Config) {
    super(ctx, 'myPlugin')
    // ...
  }
}
```

配置 schema 必须导出 `interface Config` 与同名 `const Config: Schema<Config>`（Schemastery）：

```ts
export const Config = Schema.object({
  endpoint: Schema.string().default('https://example.com'),
  retries: Schema.number().default(3),
})
export type Config = typeof Config.Static
```

> 导出普通对象作 `Config` **不工作**——Cordis 接受任意 Standard Schema 验证器。

## 2. 组合包目录结构

```text
hello-plugin/
├── package.json
├── cordis.patch.yml
└── index.js
```

`package.json`：

```json
{
  "name": "hello-plugin",
  "version": "0.1.0",
  "type": "module",
  "main": "index.js",
  "engines": { "dsh": ">=0.2.0 <0.3.0" },
  "dsh": { "bundle": { "patch": "./cordis.patch.yml" } }
}
```

`engines.dsh` 声明兼容的 DSH 版本范围（未声明时会查 `@deepseek-ai/dsh*` 的 peer 范围）。

`cordis.patch.yml`：

```yaml
- insert:
    - id: hello-plugin
      name: 'hello-plugin'      # 按包名引用，不是相对路径
      config:
        endpoint: 'https://example.com'
```

> ⚠️ 插件行按**包名**引用，而不是相对路径——否则 Node 模块解析找不到已安装的代码。

## 3. 安装

```sh
dsh plugin --profile demo add ./hello-plugin
```

- `dsh plugin` 把参数转发给 `pnpm`（`add` / `remove` / `why` / `update` 等），**pnpm 必须在 PATH 上**
- 相对路径 spec 会先锚定到**调用目录**，所以在插件 checkout 里执行 `add .` 安装的是那个 checkout
- 每次成功运行后会更新 `dsh.profile.bundles`：依赖若声明了 `"dsh": { "bundle": { "patch": "./cordis.patch.yml" } }`，就会加入配置层栈
- 没有组合包声明的依赖仍作为普通依赖保留，并显示一次性警告
- 安装后**须重启 profile**（组合包成员变化属于启动边界）

从 Git 仓库安装：

```sh
dsh plugin --profile demo add github:my-org/hello-plugin
```

> git 安装需作者提供自包含的 `prepare` 脚本，且使用方要在 profile 的 `pnpm-workspace.yaml` 里授权 `allowBuilds`（pnpm ≥10 默认阻止该脚本）。安装已构建好的 tarball 或本地 checkout 则无需授权。

## 4. 本地开发

```sh
# 用 --patch 直接挂载，无需安装
dsh web --patch ./hello-plugin/cordis.yml
```

开发时启用 HMR：base 以 `root: []` 启用配置监听（仅当 profile 上下文存在时），编辑 `cordis.patch.yml` 会热重载；**模块替换**则由 `dsh-hmr` 的 Loader 机制处理。

> headless / SDK / ACP profile 在 YAML 中**禁用 HMR**——保证一条 stdio 连接不观察到依赖被替换。

## 5. 配置 schema 与 --dump-config-schema

`--dump-config-schema` 输出 JSON Schema 2020-12，其中 `x-cordis` 注释保留 `secret`、`credential-ref`、`ms` 等 role 元信息与 `volatile` 实时更新元信息。适合在 CI 里校验用户提交的 patch。

## 6. 发布到插件市场

市场索引 JSON 关键字段：

```json
{
  "format": 1,
  "title": "Team plugins",
  "plugins": [
    {
      "name": "hello-plugin",
      "versions": [
        { "source": { "type": "npm", "url": "hello-plugin@0.1.0" },
          "engines": { "dsh": ">=0.2.0" } }
      ]
    }
  ]
}
```

用官方生成器产出：

```sh
pnpm --filter @deepseek-ai/dsh-plugin-market-generator start \
  --input plugins.txt --output site/index.json --title "Team plugins"
```

用户侧：在插件市场添加索引源 → 「发现」标签浏览 → 确认安装（实际安装走 `ctx.pluginManager.installBundle`）。

## 相关

- [Cordis 插件模型](../concepts/02-cordis-plugin-model.md)
- [Profile 与组合包](../concepts/03-profile-and-bundle.md)
- [能力 seam 与子系统地图](../concepts/08-capability-seams.md)
