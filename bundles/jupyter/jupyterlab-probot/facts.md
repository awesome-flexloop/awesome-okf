---
okf_version: '0.2'
generated: '2026-08-22'
source_root: d:\spaces\SpecWeave\external\libs\jupyter\jupyterlab-probot
tags:
- probot
- github-app
- automation
- maintenance
- ci
sources:
- ../../../../../external/libs/jupyter/jupyterlab-probot/package.json
- ../../../../../external/libs/jupyter/jupyterlab-probot/README.md
- ../../../../../external/libs/jupyter/jupyterlab-probot/src/index.ts
- ../../../../../external/libs/jupyter/jupyterlab-probot/schema.json
- ../../../../../external/libs/jupyter/jupyterlab-probot/app.yml
- ../../../../../external/libs/jupyter/jupyterlab-probot/tsconfig.json
- ../../../../../external/libs/jupyter/jupyterlab-probot/test/fixtures/duplicate_pull_requests.json
- ../../../../../external/libs/jupyter/jupyterlab-probot/test/fixtures/duplicate_pushes.json
- ../../../../../external/libs/jupyter/jupyterlab-probot/test/index.test.ts
- ../../../../../external/libs/jupyter/jupyterlab-probot/jest.config.js
- ../../../../../external/libs/jupyter/jupyterlab-probot/test/fixtures/issue_comment.created.json
- ../../../../../external/libs/jupyter/jupyterlab-probot/test/fixtures/issue_labelled.opened.json
- ../../../../../external/libs/jupyter/jupyterlab-probot/test/fixtures/issue_no_label.opened.json
- ../../../../../external/libs/jupyter/jupyterlab-probot/test/fixtures/pull_request.opened.json
type: Facts
title: jupyterlab-probot 源码事实清单
---

# jupyterlab-probot 事实清单

## 项目概况

- F-001: package.json:2-6 — 包名为 jupyterlab-probot，版本 1.0.0，私有包，描述为 "A Probot app for JupyterLab Maintenance"
- F-002: package.json:7 — 许可证为 ISC，作者为 Project Jupyter
- F-003: README.md:1-3 — 基于 Probot 框架构建的 GitHub App，用于 JupyterLab 仓库维护自动化
- F-004: package.json:34-36 — Node.js 引擎要求 >= 10.13.0

## 构建与运行

- F-005: package.json:15 — 构建命令为 tsc（TypeScript 编译）
- F-006: package.json:16 — 启动命令为 `probot run ./lib/index.js`
- F-007: package.json:17 — 测试使用 Jest 框架
- F-008: package.json:18 — 覆盖率测试：`DEBUG=true; jest --collect-coverage --clear-cache`
- F-009: package.json:19 — 监听模式：tsc -w
- F-010: Dockerfile:1-8 — Docker 部署基于 node:18-slim，npm ci --production 安装依赖，CMD 为 npm start

## 依赖

- F-011: package.json:22 — 使用 ajv ^8.6.2 进行 JSON Schema 验证
- F-012: package.json:23 — 核心框架 probot ^12.3.1
- F-013: package.json:26-32 — 开发依赖：@types/jest、@types/node、jest ^26.6.3、nock ^13.0.5（HTTP mocking）、smee-client ^1.2.2（webhook 代理）、ts-jest ^26.4.4、typescript ^4.1.3

## 配置系统

- F-014: src/index.ts:20-25 — Config 接口包含四个可配置字段：binderUrlSuffix、addBinderLink、triageLabel、botUser
- F-015: src/index.ts:31-45 — getConfig() 函数从仓库的 `.github/jupyterlab-probot.yml` 加载配置，使用 ajv 结合 schema.json 验证，useDefaults: true 启用默认值
- F-016: src/index.ts:34 — JSON Schema 从 ../schema.json 加载
- F-017: src/index.ts:39-43 — 配置验证失败时打印错误日志但不抛出异常，返回空对象作为降级
- F-018: schema.json:1-29 — JSON Schema 定义四个属性：addBinderLink(boolean)、binderUrlSuffix(string)、triageLabel(string)、botUser(string, 默认 "jupyterlab-bot")，禁止额外属性
- F-019: README.md:31-36 — 配置示例：addBinderLink: true、binderUrlSuffix: "?urlpath=lab-dev"、triageLabel: "status:Needs Triage"、botUser: "my-bot-name"

## 功能一：Issue 自动 Triage 标签

- F-020: src/index.ts:53-69 — 监听 issues.opened 事件
- F-021: src/index.ts:57-58 — 读取配置中的 triageLabel
- F-022: src/index.ts:60-62 — 如果未配置 triageLabel 则直接返回不操作
- F-023: src/index.ts:64 — 检查 issue 现有标签中是否已包含 triageLabel，避免重复添加
- F-024: src/index.ts:65-67 — 未包含标签时调用 octokit.issues.addLabels() 添加标签

## 功能二：PR Binder 链接自动评论

- F-025: src/index.ts:71-101 — 监听 pull_request.opened 事件
- F-026: src/index.ts:72-75 — 从 PR head 获取 ref（分支名，URL编码）、user（用户名）、repo（仓库名）
- F-027: src/index.ts:79-81 — 读取配置中的 binderUrlSuffix，默认为空字符串
- F-028: src/index.ts:88-92 — 如果 addBinderLink 为 false/未设置则跳过
- F-029: src/index.ts:93 — Binder 链接格式：`https://mybinder.org/v2/gh/{user}/{repo}/{ref}{urlSuffix}`
- F-030: src/index.ts:97-98 — 评论内容：感谢 PR + Binder 徽章链接，Markdown 格式含 Binder logo 图片
- F-031: src/index.ts:99-100 — 使用 context.issue() 构造评论参数，调用 octokit.issues.createComment() 发布评论

## 功能三：重复 Workflow Run 自动取消

- F-032: src/index.ts:103-197 — 监听 workflow_run.requested 事件
- F-033: src/index.ts:12-14 — RunData 接口仅包含 id 字段
- F-034: src/index.ts:106-108 — 如果 workflow_id 不存在则跳过（istanbul 忽略）
- F-035: src/index.ts:109-114 — 提取 event_type、branch、workflow_id、owner、repo
- F-036: src/index.ts:118-123 — 忽略 issue_comment 和 workflow_dispatch 触发的运行（这些是手动触发不应取消）
- F-037: src/index.ts:125-127 — DEBUG 模式下将 payload 写入 outputs.txt
- F-038: src/index.ts:129 — 查询三种状态的 workflow runs：queued、in_progress、requested
- F-039: src/index.ts:130-165 — 并行查询三种状态的 runs，提取 id 和 created_at，过滤掉当前触发的 run 和比当前 run 更新的 run，剩余的为重复项
- F-040: src/index.ts:158-163 — 去重逻辑：排除当前 run id，且只保留创建时间早于当前 run 的（更早创建的是重复的旧 run）
- F-041: src/index.ts:171-186 — 并行取消所有重复 runs，调用 octokit.rest.actions.cancelWorkflowRun()
- F-042: src/index.ts:183 — 取消成功返回 HTTP 202（istanbul 忽略错误检查）
- F-043: src/index.ts:188-196 — 日志输出：仓库、分支、workflow名、事件类型、取消消息列表

## 功能四：评论触发 CI 重启

- F-044: src/index.ts:199-246 — 监听 issue_comment.created 事件
- F-045: src/index.ts:206 — 去除评论首尾空白
- F-046: src/index.ts:208-209 — 从配置读取 botUser，默认 jupyterlab-bot；期望的评论内容为 `@{botUser}, please restart ci`
- F-047: src/index.ts:210 — 精确匹配评论内容（== 比较）
- F-048: src/index.ts:211-232 — 重启 CI 的实现方式：先关闭 issue/PR（state: closed），再重新打开（state: open），通过 close-reopen 触发 CI
- F-049: src/index.ts:218-219 — 关闭失败（非200）时记录错误消息，不再尝试打开
- F-050: src/index.ts:227-230 — 关闭成功但打开失败时记录错误；两者都成功则记录 "Successfully closed/opened!"
- F-051: src/index.ts:233-234 — 评论内容不匹配时输出 "Ignored"

## GitHub App 权限配置

- F-052: app.yml:15-48 — 默认订阅事件：仅启用 issues（注意：代码注释中 pull_request、issue_comment、workflow_run 相关事件被注释掉，但实际代码监听了这些事件）
- F-053: app.yml:73 — Issues 权限：write（需要添加标签和评论）
- F-054: app.yml:77 — Metadata 权限：read
- F-055: 代码实际需要的权限：actions: write（取消 workflow runs）、pull_requests: write（PR 评论）—— app.yml 中被注释但功能实际使用

## 测试

- F-056: test/index.test.ts:16-19 — 测试使用 fixtures/mock-cert.pem 作为私钥
- F-057: test/index.test.ts:24-37 — 每个测试前：禁用网络连接、创建 Probot 实例（禁用重试和限流）、加载应用
- F-058: test/index.test.ts:39-58 — 测试用例：配置了 triageLabel 时，无标签的 issue 会被添加标签
- F-059: test/index.test.ts:60-74 — 测试用例：配置缺少 triageLabel 时不操作
- F-060: test/index.test.ts:76-92 — 测试用例：issue 已有标签时不重复添加
- F-061: test/index.test.ts:94-117 — 测试用例：addBinderLink 未配置时不创建 Binder 评论
- F-062: test/index.test.ts:119-145 — 测试用例：addBinderLink 为 true 时创建 Binder 评论
- F-063: test/index.test.ts:147-171 — 测试用例：配置类型错误（binderUrlSuffix 为数字）时优雅降级
- F-064: test/index.test.ts:173-201 — 测试用例：取消重复的 push 触发的 workflow runs
- F-065: test/index.test.ts:203-231 — 测试用例：取消重复的 pull_request 触发的 workflow runs
- F-066: test/index.test.ts:233-258 — 测试用例：无重复 runs 时不操作
- F-067: test/index.test.ts:260-289 — 测试用例：识别 restart ci 评论并执行 close/reopen
- F-068: test/index.test.ts:291-320 — 测试用例：无配置文件时（404）仍能处理 restart 评论（使用默认 botUser）
- F-069: test/index.test.ts:322-347 — 测试用例：评论不匹配时忽略
- F-070: test/index.test.ts:349-380 — 测试用例：自定义 botUser 时使用配置中的用户名匹配
- F-071: test/index.test.ts:382-385 — 每个测试后清理 nock mocks 并恢复网络连接
- F-072: jest.config.js — Jest 配置文件存在
- F-073: tsconfig.json — TypeScript 配置文件存在

## 测试 Fixtures

- F-074: test/fixtures/duplicate_pull_requests.json — 重复 PR runs 的测试数据
- F-075: test/fixtures/duplicate_pushes.json — 重复 push runs 的测试数据
- F-076: test/fixtures/issue_comment.created.json — issue 评论创建事件的 fixture
- F-077: test/fixtures/issue_labelled.opened.json — 已有标签的 issue 打开事件 fixture
- F-078: test/fixtures/issue_no_label.opened.json — 无标签的 issue 打开事件 fixture
- F-079: test/fixtures/pull_request.opened.json — PR 打开事件 fixture
- F-080: test/fixtures/mock-cert.pem — 测试用的模拟 PEM 私钥

## 部署

- F-081: README.md:22 — Docker 运行需要环境变量 APP_ID 和 PRIVATE_KEY
- F-082: README.md:49-55 — Heroku 部署支持，设置 LOG_LEVEL=trace 可查看详细日志
- F-083: .env.example — 环境变量示例文件存在
- F-084: README.md:40 — 默认 botUser 为 jupyterlab-bot
- F-085: README.md:45 — 重启 CI 命令：`@jupyterlab-bot, please restart ci`
