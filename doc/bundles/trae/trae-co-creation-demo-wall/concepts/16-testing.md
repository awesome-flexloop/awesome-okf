---
type: Concept
title: 测试体系
description: Demo Wall 的测试策略：Node.js test runner、Docker 原生依赖测试、运行时启动测试、Prisma seed 序列测试、部署配置测试。
tags: [demo-wall, testing, test, docker, seed]
generated: { by: "reference_agent/trae-cn", at: "2026-04-22" }
verified: { by: "process:seven-concepts-v", at: "2026-04-22" }
status: stable
stale_after: "2026-10-22"
sources:
  - id: src
    resource: "/references/demo-wall-source.md"
    title: "Demo Wall 源码信源"
---

## 测试策略

Demo Wall 的测试聚焦于部署和基础设施层面，使用 Node.js 内置 test runner，通过 npm scripts 执行（F-012）。

## 测试脚本（F-012）

package.json 中定义了四个测试命令：

| 命令 | 测试对象 | 说明 |
|------|---------|------|
| test:docker-deps | Docker 依赖 | 验证 Docker 环境和依赖服务（db/redis）可用性 |
| test:docker-runtime | 运行时启动 | 验证应用在 Docker 容器中能正常启动 |
| test:seed | 数据库种子 | 验证 seed.ts 序列执行正确性 |
| test:deploy-config | 部署配置 | 验证 docker-compose/nginx/env 等部署配置 |

## Docker 原生依赖测试

test:docker-deps 验证：
- Docker daemon 是否可用
- docker-compose 是否可用
- PostgreSQL 容器能否正常启动和连接
- Redis 容器能否正常启动和连接

这种测试方式不需要本地安装 PostgreSQL/Redis，直接使用 Docker 运行依赖服务，保证测试环境一致性。

## 运行时启动测试

test:docker-runtime 验证：
- Docker 镜像能否成功构建
- 容器能否正常启动（entrypoint.sh 执行）
- 应用能否监听 3000 端口
- 健康检查端点是否返回正常

## Seed 序列测试

test:seed 验证：
- prisma db push 能否成功创建表结构
- seed.ts 能否无错误执行
- 系统角色是否正确创建（root/admin/common）
- 系统字典是否正确初始化（6个系统字典 + 国家城市）
- 默认管理员账号是否可登录
- seed 幂等性：重复执行 seed 不报错（addItem upsert 逻辑）

## 部署配置测试

test:deploy-config 验证：
- docker-compose.yml 配置有效性
- nginx.conf 语法正确性
- 必需的环境变量是否有默认值或示例
- 端口映射不冲突
- volumes 配置正确

## intl 版本测试（F-162）

intl 版本有 test/ 目录，包含 filter-options-sort.test.ts 测试文件，对 sortFilterOptions 排序函数进行单元测试。

## 测试设计思路

项目的测试策略偏**部署验证**而非单元测试：
- 核心业务逻辑（CRUD/认证/审核）通过类型系统（TypeScript + zod）和运行时校验提供安全保障
- 部署是最高风险点（数据库迁移/环境变量/容器网络），因此重点测试
- 使用 Docker 原生测试避免"在我机器上能跑"的环境问题

## 相关概念

- [Docker 部署](/concepts/15-docker-deployment.md)
- [快速开始](/concepts/01-getting-started.md)
