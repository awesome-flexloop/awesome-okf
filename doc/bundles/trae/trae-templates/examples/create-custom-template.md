---
type: Example
title: 创建自定义模板
description: 遵循最小可用原则创建自定义模板的完整步骤，包括目录结构设计、文件编写、双语 README 和贡献提交流程。
tags: [trae-templates, example, custom-template, contribution, minimal-viable]
generated: { by: "reference_agent/trae-cn", at: 2026-04-22T00:00:00+08:00 }
verified: { by: "process:seven-concepts-v", at: 2026-04-22T00:00:00+08:00 }
status: stable
stale_after: 2026-10-22
sources:
  - id: src
    resource: /references/templates-source.md
    title: Trae Templates 源码信源
---

## 示例目标

创建一个名为 `hono-starter` 的自定义模板——一个基于 Hono（轻量级 TypeScript Web 框架）的后端 API 服务模板。遵循社区的最小可用设计原则。

## 步骤 1：确定分类和命名

首先判断模板属于哪个分类：

- Hono 是一个 Web 框架，运行在 Node.js/Deno/Cloudflare Workers 上
- 用途是构建后端 API 服务
- 属于 **backend-service** 分类

命名规范：
- 小写字母
- 使用连字符（`-`）
- 格式：`{framework}-starter` 或 `{type}-{name}`
- 这里命名为 `hono-starter`

## 步骤 2：创建目录结构

```bash
mkdir -p templates/backend-service/hono-starter
cd templates/backend-service/hono-starter
```

根据最小可用原则，我们只创建必需的文件：

```
hono-starter/
├── package.json        # 依赖声明和启动脚本
├── tsconfig.json       # TypeScript 配置
├── src/
│   └── index.ts        # 入口文件（单文件可运行）
├── .gitignore
├── README.md
└── README.zh-CN.md
```

注意：不要创建多余的文件（如 eslint 配置、prettier 配置、测试框架配置、Dockerfile 等）——这些由开发者按需添加。

## 步骤 3：编写入口文件

创建 `src/index.ts`：

```typescript
import { Hono } from 'hono'

const app = new Hono()

app.get('/', (c) => {
  return c.json({ message: 'Hello Hono!' })
})

export default app
```

这是最小可用的 Hono 应用：
- 一个 GET / 端点返回 JSON
- 单文件入口，逻辑清晰
- 不预设中间件、路由分组、数据库等

## 步骤 4：编写 package.json

```json
{
  "name": "hono-starter",
  "version": "1.0.0",
  "description": "Hono TypeScript API starter template",
  "scripts": {
    "dev": "tsx watch src/index.ts",
    "build": "tsc",
    "start": "node dist/index.js"
  },
  "dependencies": {
    "hono": "^4.0.0"
  },
  "devDependencies": {
    "@types/node": "^20.0.0",
    "tsx": "^4.0.0",
    "typescript": "^5.0.0"
  }
}
```

要点：
- 提供 `dev`（开发模式，带热重载）、`build`（构建）、`start`（生产启动）三个脚本
- 只包含 Hono 必需的依赖
- 不包含多余的开发依赖（如测试框架、lint 工具）

## 步骤 5：编写 tsconfig.json

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "strict": true,
    "outDir": "dist",
    "esModuleInterop": true,
    "skipLibCheck": true
  },
  "include": ["src"]
}
```

要点：
- 使用现代 ES 目标和 bundler 模块解析
- 启用 strict 模式
- 输出到 dist/ 目录
- 最小化配置，不添加路径别名等高级选项

## 步骤 6：编写 .gitignore

```
node_modules/
dist/
*.log
.env
```

只忽略必需的目录和文件。

## 步骤 7：编写双语 README

### README.md（英文）

```markdown
# Hono Starter

A minimal Hono + TypeScript API starter template.

## Tech Stack

- Hono (lightweight TypeScript web framework)
- TypeScript
- Node.js 18+

## Getting Started

```bash
npm install
npm run dev
```

The server will start at `http://localhost:3000`.

## Available Scripts

- `npm run dev` - Start development server with hot reload (tsx watch)
- `npm run build` - Build for production
- `npm start` - Start production server

## API Endpoints

- `GET /` - Returns `{"message": "Hello Hono!"}`

## Project Structure

```
.
├── src/
│   └── index.ts    # App entry point
├── package.json
└── tsconfig.json
```

## License

MIT
```

### README.zh-CN.md（中文）

```markdown
# Hono Starter

极简 Hono + TypeScript API 启动模板。

## 技术栈

- Hono（轻量级 TypeScript Web 框架）
- TypeScript
- Node.js 18+

## 快速开始

```bash
npm install
npm run dev
```

服务器将在 `http://localhost:3000` 启动。

## 可用脚本

- `npm run dev` - 启动开发服务器（热重载）
- `npm run build` - 生产构建
- `npm start` - 启动生产服务器

## API 端点

- `GET /` - 返回 `{"message": "Hello Hono!"}`

## 项目结构

```
.
├── src/
│   └── index.ts    # 应用入口
├── package.json
└── tsconfig.json
```

## 许可证

MIT
```

README 编写要点：
- 明确技术栈和版本要求
- 提供完整的启动命令
- 列出所有 npm scripts
- 说明默认端点/功能
- 展示项目结构
- 双语版本内容对齐

## 步骤 8：验证模板

在提交前验证模板可用性：

```bash
# 在临时目录测试
mkdir /tmp/test-hono
cd /tmp/test-hono
cp -r /path/to/templates/backend-service/hono-starter/* .
npm install
npm run dev
# 访问 http://localhost:3000 确认返回 {"message":"Hello Hono!"}
```

验证清单：
- [ ] `npm install` 成功无报错
- [ ] `npm run dev` 启动成功
- [ ] 默认端口可访问
- [ ] 示例端点正常响应
- [ ] 所有文件路径正确
- [ ] README 中的命令可执行
- [ ] 没有多余的配置文件

## 步骤 9：检查最小可用原则

对照最小可用原则自查：

| 检查项 | 状态 |
|--------|------|
| 单入口文件可运行 | ✅ src/index.ts |
| 文件数量精简（≤8个） | ✅ 6 个文件 |
| 无多余依赖锁定文件 | ✅ 无 lockfile |
| 不替用户做技术决策 | ✅ 未添加路由库/ORM/测试框架 |
| 双语 README | ✅ README.md + README.zh-CN.md |
| 启动命令明确 | ✅ npm install && npm run dev |

注意 svelte-starter 的教训——README 中不要出现复制遗留的错误描述（如写着 React 实际是 Svelte）。

## 步骤 10：提交贡献

1. Fork trae-templates 仓库
2. 创建特性分支：`git checkout -b feature/hono-starter`
3. 添加模板文件
4. 更新根目录 `README.md` 的模板目录表格，添加 hono-starter
5. 提交变更
6. 创建 Pull Request

## 反模式：什么不应该做

### ❌ 不要创建完整项目脚手架

```
# 错误：文件太多
hono-starter/
├── src/
│   ├── controllers/
│   ├── middlewares/
│   ├── models/
│   ├── routes/
│   ├── services/
│   ├── utils/
│   └── index.ts
├── tests/
├── .eslintrc.js
├── .prettierrc
├── jest.config.js
├── docker-compose.yml
├── Dockerfile
└── ...（20+ 个文件）
```

这违背了最小可用原则。

### ❌ 不要锁定依赖版本

不要在模板中包含 `package-lock.json`、`pnpm-lock.yaml` 或 `yarn.lock`。这些文件在用户安装时会根据其包管理器自动生成。

### ❌ 不要预设技术选型

不要替用户决定：
- 使用什么测试框架（Jest/Vitest/不测试）
- 使用什么数据库 ORM（Prisma/Drizzle/TypeORM）
- 使用什么日志库（winston/pino/console）
- 使用什么验证库（zod/valibot/joi）

模板只提供框架本身的最小起点。

### ❌ 不要忘记中文 README

社区要求所有模板必须包含 `README.md` 和 `README.zh-CN.md` 双语说明文件（superpowers-trae-init 是唯一例外，中文文件名为 TEMPLATE_README.zh-CN.md）。

## 相关概念

- [五维分面分类体系](/concepts/01-template-classification.md)
- [后端服务模板](/concepts/03-backend-templates.md)
- [Trae Templates 简介](/concepts/00-introduction.md)

## 相关内容

- [源码信源索引](/references/templates-source.md)
- [使用 Next.js 模板创建项目](/examples/use-nextjs-template.md)
