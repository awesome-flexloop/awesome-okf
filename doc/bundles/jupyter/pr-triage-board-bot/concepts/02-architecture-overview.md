---
okf_version: "0.2"
type: "concept"
title: "架构总览"
description: "pr-triage-board-bot的目录结构、模块职责、核心数据流、全量对账同步模型与执行流程"
tags: [architecture, directory-structure, data-flow, reconciliation, module-overview]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T10:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: main-source
    resource: /references/main-source.md
    title: "入口与CLI源码"
  - id: project-source
    resource: /references/project-source.md
    title: "Project管理类源码"
  - id: field-config-source
    resource: /references/field-config-source.md
    title: "字段配置体系源码"
  - id: field-impl-source
    resource: /references/field-implementations-source.md
    title: "字段实现源码"
---

# 架构总览

## 目录结构

```
pr-triage-board-bot/
├── action.yml                    # GitHub Action 定义（composite action）
├── package.json                  # 包配置与依赖
├── tsconfig.json                 # TypeScript 编译配置
├── .swcrc                        # SWC 编译配置
├── .github/
│   └── workflows/
│       ├── ci.yaml               # CI流水线（类型检查+构建）
│       └── run.yaml              # 自身运行的workflow示例
└── src/
    ├── main.ts                   # 入口：CLI、Octokit创建、主同步循环
    ├── project.ts                # Project类：GitHub Project V2操作封装
    ├── utils.ts                  # 工具函数：GraphQL加载、协作者查询
    ├── fieldconfig.ts            # 字段类型系统与注册表
    ├── fields/                   # 7+1个字段计算实现
    │   ├── authorkind.ts         # 作者类型
    │   ├── openedat.ts           # 创建日期
    │   ├── totallineschanged.ts  # 变更行数
    │   ├── maintainerengagement.ts # 维护者参与度
    │   ├── cistatus.ts           # CI状态
    │   ├── mergeconflicts.ts     # 合并冲突
    │   ├── approvalstatus.ts     # 审批状态
    │   └── fileschangedtype.ts   # 文件变更类型（未启用）
    └── graphql/                  # GraphQL查询文件
        ├── openprs.gql           # 开放PR搜索
        ├── project.gql           # 项目字段查询
        ├── projectitems.gql      # 项目条目分页
        └── maintainers.gql       # 仓库协作者查询
```

## 模块职责分层

项目采用清晰的四层架构：

```
┌─────────────────────────────────────────────┐
│  CLI/Action层 (main.ts + action.yml)        │
│  commander参数解析 → GitHub Action 步骤编排  │
├─────────────────────────────────────────────┤
│  业务逻辑层 (main.ts 主函数)                 │
│  全量对账循环：获取PR → 获取条目 → 差异同步  │
├─────────────────────────────────────────────┤
│  Project操作层 (project.ts)                 │
│  字段CRUD、条目CRUD、动态Mutation构造        │
├─────────────────────────────────────────────┤
│  字段插件层 (fieldconfig.ts + fields/)      │
│  类型系统 + 注册表 + 7个字段计算函数         │
├─────────────────────────────────────────────┤
│  基础设施层 (utils.ts + @octokit/*)         │
│  Octokit客户端、GraphQL文件加载、缓存       │
└─────────────────────────────────────────────┘
```

## 核心数据流

```
GitHub API (GraphQL)
       │
       ▼
┌──────────────┐
│ getOpenPRs() │─── 搜索开放PR（分页）
└──────┬───────┘
       │ PR列表（含additions/deletions/reviews/CI/等）
       ▼
┌──────────────────────┐     ┌─────────────────────┐
│ Project.getProject() │     │ getExistingItems()  │
│ 获取字段定义         │     │ 获取已有项目条目    │
└──────┬───────────────┘     └─────────┬───────────┘
       │ fields[]                     │ items[]
       └──────────┬───────────────────┘
                  ▼
        ┌──────────────────┐
        │ 构建映射表       │
        │ currentPRIds     │ ← 当前开放PR集合
        │ existingItemsMap │ ← 已有条目（按PR ID）
        │ itemsToDelete    │ ← 需要删除的过期条目
        └────────┬─────────┘
                 │
        ┌────────▼─────────┐
        │ 删除过期条目     │ → project.deleteItem()
        └────────┬─────────┘
                 │
        ┌────────▼─────────────────────────────┐
        │ 遍历每个PR：                          │
        │  1. addContent()（新PR添加到项目）   │
        │  2. 遍历REQUIRED_FIELDS：            │
        │     - fieldConfig.getValue() 计算值  │
        │     - 与现有值比较                   │
        │     - 变化则 setItemValue() 更新     │
        └────────┬─────────────────────────────┘
                 │
                 ▼
        GitHub Project V2 (更新后的看板)
```

## 全量对账模型（Reconciliation Loop）

机器人采用**全量对账**而非事件驱动模型。每次运行执行以下步骤：

1. **全量获取**：通过GitHub Search API获取所有开放PR，通过Project API获取所有已有条目
2. **集合差异**：
   - PR在板上但已关闭/不存在 → 删除条目（stale cleanup）
   - PR是新开的但不在板上 → 添加条目并填充所有字段
   - PR在板上 → 逐字段比较，只更新变化的字段
3. **幂等执行**：确定性计算+值比较，重复运行不会产生副作用

这种设计的优势：
- **简单可靠**：不需要webhook、不需要事件队列、不需要状态持久化
- **自动修复**：如果有人手动修改了字段，下次运行自动纠正
- **容错性强**：即使某次运行失败，下次运行从全量数据重新同步

## 关键设计决策

### 为什么用全量对账而非Webhook？

Webhook驱动需要：配置webhook endpoint、处理事件排序和去重、维护状态存储、处理事件丢失和重放。全量对账只需要定时运行，无状态，每次从GitHub API获取当前真实状态并修正差异。对于PR分类看板这种非实时场景（小时级延迟可接受），全量对账是更简单可靠的选择。

### 为什么字段计算函数返回null而不是默认值？

当信息不足时（CI还在运行、合并状态未知、无审查），返回 `null` 清空字段而非猜测默认值。这避免了显示错误信息——维护者看到空字段就知道"信息还不可用"，而不是被误导。

### 为什么值变化才更新？

每个字段都先比较新值和现有值，相同则跳过（skipped），不同才发送mutation。这减少了API调用次数，避免不必要的Project活动日志，提高运行速度。

## 构建与运行链路

```
源代码 (src/*.ts)
    │
    │ npm run build (SWC编译)
    ▼
编译输出 (dist/src/*.js)
    │
    │ node dist/src/main.js [options] <org> <project>
    ▼
Octokit (GraphQL API) ←→ GitHub API
    │
    ▼
GitHub Project V2 (看板更新)
```

作为GitHub Action运行时，action.yml编排了完整的构建+运行步骤：
1. 复制package-lock.json到WORKSPACE（npm缓存需要）
2. setup-node配置Node.js 23.x
3. `npm ci` 安装依赖
4. `npm run build` 编译
5. 写入私钥到临时文件
6. 运行编译后的脚本
7. 清理私钥文件（always执行）

## 相关概念

- [pr-triage-board-bot 简介](00-introduction.md)
- [5分钟快速上手](01-getting-started.md)
- [GitHub App认证与Octokit配置](03-auth-and-octokit.md)
- [Project管理类](04-project-class.md)
