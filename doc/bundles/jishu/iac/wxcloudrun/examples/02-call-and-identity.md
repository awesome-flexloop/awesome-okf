---
type: Example
title: "从小程序调用服务并透传用户身份"
description: "给出小程序 callContainer 接入云托管的完整步骤：基础库门槛、init 时序、参数约束、服务端读取微信身份 header 的示例代码与体积限制。"
tags: [微信云托管, callContainer, 身份透传, 小程序, 接口调用]
generated: { by: "agent:blog-article-to-okf-wiki", at: "2026-10-22T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-10-22T00:00:00Z" }
status: draft
stale_after: 2027-04-22
sources:
  - id: docs
    resource: https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/basic/intro.html
    title: 微信开放文档 · 云托管（2026-10-22 采集）
---

# 从小程序调用服务并透传用户身份

微信链路与公网链路是两种完全不同的接入形态：前者由平台代为完成调用方身份校验并附带权威用户信息，后者不包含任何微信用户信息、需要业务自建鉴权体系（F-004、F-082）。本文档只走微信链路（小程序 `callContainer`），并在每一步标注对应的编号事实。

## 目标与前置条件

**目标**：小程序通过 `callContainer` 调用云托管服务，服务端无需任何登录置换代码即可读到调用方的 openid / unionid 等身份信息。

**前置条件**：

| 前置条件 | 说明 | 依据 |
|---|---|---|
| 环境授权 | `callContainer` 方法仅限被该微信云托管环境授权的小程序/公众号使用，仅凭环境 id 和服务名无法调用对应服务 | F-071 |
| 基础库版本 | 需在「小程序管理后台」-「设置」-「功能设置」-「基础库最低版本设置」中把值设定为 2.23.0 及以上，否则无法正常使用 `callContainer` 方法 | F-072 |
| 版本状态 | 被调服务需已有处于「线上」状态的版本；版本分线上、线下两种状态 | F-060 |
| 协议形态 | 目前仅支持 HTTP 协议，不支持 tcp/udp/mqtt 等其他协议 | F-070 |

## 步骤

### 步骤 1：设置基础库最低版本

**操作**：进入「小程序管理后台」-「设置」-「功能设置」-「基础库最低版本设置」，把值设定为 2.23.0 及以上。

**关键配置**：基础库低于该版本时 `callContainer` 方法无法正常使用（F-072）。这同时是获得 DDoS 防护链条的一环——官方写明「采用 callcontainer 方式调用后端接口」「关闭公网访问开关」「基础库最低版本设定为 2.23.0 及以上」三条缺一不可（F-159）。

**依据**：F-072、F-159

### 步骤 2：在 app.js 中初始化并等待完成

**操作**：在小程序 `app.js` 中执行 `wx.cloud.init()`，全局执行一次即可；init 过程是异步的，必须等 init 完成后再发起调用。

> 以下为非官方示例代码，基于官方文档描述自行编写。
```javascript
// app.js
App({
  onLaunch() {
    // init 是异步的，需要等待完成后才可以发起调用（F-074）
    this.cloudReady = wx.cloud.init({
      env: '填入云环境ID',
    });
  },
});
```

**关键配置**：`wx.cloud.init()` 全局执行一次即可，init 过程是异步的，需要等待 init 完成才可以发起调用（F-074）。

**依据**：F-074

### 步骤 3：发起 callContainer 调用

**操作**：在页面逻辑中等待 init 完成后再发起调用，`header` 中的 `X-WX-SERVICE` 填服务名称。

> 以下为非官方示例代码，基于官方文档描述自行编写。
```javascript
// 发起调用前先确保 init 已完成（F-074）
await app.cloudReady;

wx.cloud.callContainer({
  config: { env: '填入云环境ID' },
  path: '/api/orders',
  method: 'POST',
  header: { 'X-WX-SERVICE': '填入服务名称' },
  data: { orderId: '占位订单号' },
  success(res) {
    console.log('调用结果', res);
  },
});
```

**关键配置**：小程序调用示例为 `wx.cloud.callContainer({ config: { env: '填入云环境ID' }, path: '/xxx', method: 'POST', header: { 'X-WX-SERVICE': 'xxx' } })`，`X-WX-SERVICE` 填服务名称（F-073）。

**依据**：F-073、F-074

### 步骤 4：校对请求参数

**操作**：按参数表逐项校对；超时值不要超过上限。

| 参数 | 约束 | 依据 |
|---|---|---|
| `config.env` | 必填 | F-075 |
| `path` | 必填 | F-075 |
| `header` | 必填；不能设置 Referer；content-type 默认为 application/json | F-075 |
| `timeout` | 单位毫秒，最大值不能超过 15 秒，否则无效 | F-075 |
| `method` | 合法值为 OPTIONS、GET、HEAD、POST、PUT、DELETE、TRACE、CONNECT | F-076 |
| `dataType` | 合法值为 json（默认）与 other | F-076 |
| `responseType` | 合法值为 text（默认）与 arraybuffer | F-076 |

> **勘误说明（E-004）**：官方文档不同页面口径不一致——`development/call/index.html` 称请求最大超时 60 秒，`development/call/mini.html` 与 `faq.html` 称 timeout 最大值不能超过 15 秒。本处采信 **15 秒**（参数级约束更具体，F-075）。

**依据**：F-075、F-076

### 步骤 5：服务端读取身份信息

**操作**：在服务端从请求 header 中读取身份字段；先打印一次真实到达的 header 键名，再固化取值逻辑。

**关键配置**：容器内收到的请求 header 包含 `X-WX-OPENID`、`X-WX-APPID`、`X-WX-UNIONID`、`X-WX-FROM-OPENID`、`X-WX-FROM-APPID`、`X-WX-FROM-UNIONID`、`X-WX-ENV`、`X-WX-SOURCE`、`X-Original-Forwarded-For`（F-077）。header 大小写不敏感，但部分框架会将原始 header 转为小写、无划线驼峰或下划线形式，业务开发前需先打印测试 header 信息；判断调用来源是否为微信生态端可判断 `X-WX-SOURCE` 头部是否存在（F-078）。

> 以下为非官方示例代码，基于官方文档描述自行编写。
```javascript
// 服务端读取微信身份，兼容框架对 header 的改写（F-077 / F-078）
function readWechatIdentity(req) {
  const headers = req.headers || {};
  const pick = (name) =>
    headers[name] ??
    headers[name.toLowerCase()] ??
    headers[name.toLowerCase().replace(/-/g, '_')];

  return {
    // 判断是否来自微信生态端：X-WX-SOURCE 是否存在（F-078）
    isWechatSource: pick('X-WX-SOURCE') !== undefined,
    openid: pick('X-WX-OPENID'),
    unionid: pick('X-WX-UNIONID'),
    appid: pick('X-WX-APPID'),
    fromOpenid: pick('X-WX-FROM-OPENID'),
    envId: pick('X-WX-ENV'),
    clientIp: pick('X-Original-Forwarded-For'),
  };
}
```

**依据**：F-077、F-078

### 步骤 6：确认服务端无需登录置换

**操作**：不要在服务端写 `wx.login` 换取 openid 的逻辑；直接使用 header 中已有的身份信息。

**关键配置**：小程序发起 callContainer 调用时，服务请求 header 中会自动带有 openid、unionid、IP 地址、可信来源等用户信息，无需再通过 `wx.login` 登录置换（F-079）。微信生态客户端向云托管后端服务发送请求时自动经过微信接入层（内网），并附带微信校验的权威用户信息（F-004）。

**依据**：F-079、F-004

### 步骤 7：划清链路边界

**操作**：把「哪些入口能拿到微信身份」写进接口设计文档；公网入口走另一套鉴权分支。

| 入口形态 | 是否含微信用户信息 | 依据 |
|---|---|---|
| 小程序 `callContainer` | 含，平台校验并附带 | F-004、F-079 |
| 公众号未登录模式下的 `callContainer` | 不包含微信用户信息 | F-080 |
| 公网调用（普通 WEB、APP 等） | 不包含任何微信用户信息，需自己搭建用户登录鉴权等用户体系 | F-082 |
| 小程序内 web-view | 只能走公网调用，不支持 call container 内网调用 | F-081 |

**关键配置**：公网调用不支持通过公网 IP 访问服务（F-082）。

**依据**：F-080、F-082、F-081

### 步骤 8：守住请求与响应体积

**操作**：大文件走对象存储而非接口体；长任务改成「提交 + 回查」两段式。

| 项 | 限制 | 依据 |
|---|---|---|
| 请求大小 | 100KiB（文本 100KiB，二进制 20MiB） | F-088 |
| 返回包大小 | 1000KiB | F-088 |
| 错误码 -606001 | 请求包大小超过 100KB | F-088 |
| 错误码 -606002 | 响应包大小超过 1MB | F-088 |

> **勘误说明（E-005）**：官方文档不同页面口径不一致——`development/call/index.html` 写作 100KiB（文本）/ 20MiB（二进制），`development/call/h5.txt` 与 `faq.html` 写作 100K / 100KB。本处采信 **100KiB 文本 + 20MiB 二进制**（F-088）。

**依据**：F-088

### 步骤 9：不需要身份信息时主动减负

**操作**：若业务确实不需要用户身份信息，在 header 中添加 `X-WX-EXCLUDE-CREDENTIALS`。

**关键配置**：可在 header 中添加 `X-WX-EXCLUDE-CREDENTIALS: unionid, cloudbase-access-token, openid`；附带信息会占用大概 10ms-50ms 时间（F-087）。

**依据**：F-087

### 步骤 10：资源复用场景下的调用构造

**操作**：调用他人环境时，构造带 `resourceAppid` 的 Cloud 实例并显式 `init`。

> 以下为非官方示例代码，基于官方文档描述自行编写。
```javascript
// 资源复用场景（F-092）
const c1 = new wx.cloud.Cloud({
  resourceAppid: '填入环境所属的账号 appid',
  resourceEnv: '填入被复用的环境 ID',
});
await c1.init();
```

**关键配置**：资源复用场景下需构造 `new wx.cloud.Cloud({ resourceAppid: 'WXAAA', resourceEnv: 'prod_001' })` 并 `await c1.init()`，`resourceAppid` 填环境所属的账号 appid（F-092）。资源复用当前仅支持小程序、小游戏、公众号、小商店的账号间复用，不支持第三方平台、开放平台 WEB 网站等其他账号类型；被复用方不需要开通微信云托管（F-049）。

**依据**：F-092、F-049

## 调用参数要点表

| 关注点 | 结论 | 依据 |
|---|---|---|
| 准入 | 仅限被该环境授权的小程序/公众号使用 | F-071 |
| 基础库 | 2.23.0 及以上 | F-072 |
| 初始化 | `wx.cloud.init()` 全局一次，需等待完成 | F-074 |
| 必填参数 | `config.env`、`path`、`header` | F-075 |
| 禁止项 | header 中不能设置 Referer | F-075 |
| 超时上限 | 15 秒（毫秒单位） | F-075 |
| 身份来源 | header 自动附带，无需 `wx.login` 置换 | F-079 |
| 身份字段 | 8 个 `X-WX-*` + `X-Original-Forwarded-For`，共 9 个 | F-077 |
| 读取风险 | 框架可能改写 header 大小写形式 | F-078 |
| 体积限制 | 请求 100KiB 文本 / 20MiB 二进制，响应 1000KiB | F-088 |
| 免身份 | `X-WX-EXCLUDE-CREDENTIALS`，代价 10ms-50ms | F-087 |

## 已知边界

- **公众号未登录模式没有身份**：公众号处于未登录模式时，`callContainer` 方法中不包含微信用户信息（F-080）。
- **公网链路必须自建鉴权**：公网调用不包含任何微信用户信息，且不支持通过公网 IP 访问服务（F-082）。
- **web-view 只能走公网**：小程序中使用 web-view 时，web-view 部分只能走公网调用（F-081）。
- **header 名称可能被框架改写**：HTTP 层大小写不敏感不等于框架不会改名，取值逻辑必须基于实际打印结果（F-078）。
- **同步长任务被排除在形态之外**：15 秒超时上限与 1000KiB 响应上限叠加，超长任务只能拆成异步形态（F-075、F-088）。
- **默认公网域名不是生产通道**：默认公网域名性能有限制，仅能支持接口测试使用（F-007）。

## 相关文档

- [微信云托管的平台定位与资源模型](../concepts/00-platform-model.md)——环境与服务的关系、端口语义
- [发布单、灰度与回滚](../concepts/01-release-and-rollback.md)——被调服务的版本切换与流量分配
- [调用链路与身份透传](../concepts/02-call-and-identity.md)——两条链路的完整对比与洞察
- [微信生态集成：开放接口、支付、推送与存储](../concepts/03-wechat-ecosystem.md)——容器内调用开放接口与支付回调
- [安全边界与迁移陷阱](../concepts/05-security-and-migration.md)——关闭公网访问与 DDoS 防护三段链条

---

> **边界声明**：本文档为基于官方文档编写的参考流程，本次未在真实云托管环境部署验证。文中所有配置项、命令与参数均以官方文档表述为准，实际行为请以真实环境为准。
