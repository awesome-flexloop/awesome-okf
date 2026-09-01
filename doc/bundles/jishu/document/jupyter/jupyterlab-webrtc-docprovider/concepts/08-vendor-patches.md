---
type: Concept
title: Vendor补丁与大消息传输
description: SimplePeerExtended扩展simple-peer实现WebRTC DataChannel大消息分块传输，解决Yjs文档同步时大消息被截断的问题
tags: [vendor, simple-peer, chunking, datachannel, webrtc, patch, webpack, int64be]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T07:06:00Z" }
verified: { by: "process:grep-verify", at: "2026-08-22T07:10:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: vendor-src
    resource: /references/vendor-source.md
    title: vendor/SimplePeerExtended.js - Chunking patch
---

## 为什么需要Vendor补丁

y-webrtc 依赖 [simple-peer](https://github.com/feross/simple-peer) 库处理 WebRTC DataChannel 通信。原版 simple-peer 在发送较大消息时存在缓冲溢出问题：

1. WebRTC DataChannel 有消息大小限制（取决于浏览器和网络条件）
2. simple-peer 的 `send()` 方法直接将消息写入 DataChannel，不检查缓冲量
3. 当同步大型 Notebook（含输出、图片等）时，Yjs 更新消息可能很大
4. 缓冲溢出导致消息丢失、连接断开、同步失败

jupyterlab-webrtc-docprovider 通过两个 vendored 补丁解决此问题：
- `vendor/SimplePeerExtended.js`：扩展 simple-peer 添加分块传输
- `vendor/int64-buffer.min.js`：64位整数编解码库（用于分块头部）

## SimplePeerExtended 类

```javascript
class SimplePeerExtended extends Peer {
  constructor(opts) {
    super(opts);
    this._txOrdinal = 0;         // 发送序号
    this._rxPackets = [];         // 接收包缓存
    this._txPause = false;        // 发送暂停标志
    this.webRTCMessageQueue = []; // 发送消息队列
    this.webRTCPaused = false;    // WebRTC 暂停标志
  }
}
```

继承自 simple-peer 的 `Peer` 类，添加分块编码/解码和流量控制。

## 分块协议

### 常量

```javascript
export const CHUNK_SIZE = 1024 * 16 - 512;    // 15872 字节（约15.5KB）
export const TX_SEND_TTL = 1000 * 30;          // 30秒发送超时
export const MAX_BUFFERED_AMOUNT = 64 * 1024;  // 64KB 缓冲上限
```

- `CHUNK_SIZE`：每个分块的数据载荷大小（16KB - 512字节头部预留）
- `TX_SEND_TTL`：发送超时30秒，超时后丢弃消息
- `MAX_BUFFERED_AMOUNT`：DataChannel 缓冲阈值，超过则暂停发送

### 分块编码格式（encodePacket）

每个分块包含 **40字节头部** + **数据载荷**：

```
┌──────────┬──────────┬──────────┬──────────┬──────────┬──────────────┐
│  txOrd   │  index   │  length  │ totalSize│ chunkSize│    chunk     │
│  8 bytes │  8 bytes │  8 bytes │  8 bytes │  8 bytes │  up to 15872B│
│ Int64BE  │ Int64BE  │ Int64BE  │ Int64BE  │ Int64BE  │  Uint8Array  │
└──────────┴──────────┴──────────┴──────────┴──────────┴──────────────┘
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `txOrd` | Int64BE | 发送事务序号（每个原始消息递增） |
| `index` | Int64BE | 当前分块在消息中的索引（从0开始） |
| `length` | Int64BE | 当前分块的数据长度 |
| `totalSize` | Int64BE | 原始消息总大小 |
| `chunkSize` | Int64BE | 分块大小（固定为 CHUNK_SIZE） |
| `chunk` | Uint8Array | 实际数据 |

使用 `Int64BE`（大端64位整数）编码头部字段，由 vendored 的 `int64-buffer.min.js` 提供。

### 编码实现

```javascript
encodePacket({ chunk, txOrd, index, length, totalSize, chunkSize }) {
  const encoded = concatenate(Uint8Array, [
    new Uint8Array(new Int64BE(txOrd).toArrayBuffer()),
    new Uint8Array(new Int64BE(index).toArrayBuffer()),
    new Uint8Array(new Int64BE(length).toArrayBuffer()),
    new Uint8Array(new Int64BE(totalSize).toArrayBuffer()),
    new Uint8Array(new Int64BE(chunkSize).toArrayBuffer()),
    chunk,
  ]);
  return encoded;
}
```

将头部5个 Int64BE 字段和数据块拼接成单个 Uint8Array 发送。

### 解码实现

接收方按相同格式解析分块，缓存所有分块后按 index 顺序重组原始消息。

## Webpack 集成补丁

补丁文件本身不能自动替换 simple-peer，需要通过 webpack 构建配置在编译时替换引用：

```javascript
// webpack.config.js
const path = require('path');
module.exports = {
  resolve: {
    fallback: {
      crypto: false,  // 浏览器环境不需要 Node.js crypto
    },
  },
  devtool: 'source-map',
  module: {
    rules: [
      // Fix WebRTC buffered transmission: https://github.com/yjs/y-webrtc/pull/25
      {
        test: /y-webrtc\.js$/,
        loader: 'string-replace-loader',
        options: {
          search: 'simple-peer/simplepeer.min.js',
          replace: ['./', '..', '..', '..', 'vendor', 'SimplePeerExtended.js']
            .join(path.sep)
            .replace(/\\/g, '\\\\'),
        },
      },
    ],
  },
};
```

### 工作原理

1. `string-replace-loader` 在 webpack 编译过程中搜索匹配 `y-webrtc.js` 文件
2. 将文件中对 `'simple-peer/simplepeer.min.js'` 的 require/import 字符串替换为 vendored `SimplePeerExtended.js` 的路径
3. 路径分隔符需要双反斜杠转义（`\\`）以适配 Windows 路径
4. y-webrtc 在运行时加载的是打了补丁的 SimplePeerExtended 而非原版 simple-peer

### crypto polyfill

```javascript
fallback: { crypto: false }
```

webpack 5 不再自动 polyfill Node.js 核心模块。设置 `crypto: false` 告诉 webpack 不要包含 crypto polyfill，因为 sjcl 库自带 crypto 实现。

## JupyterLab sharedPackages 配置

package.json 中的 `jupyterlab.sharedPackages` 配置控制依赖的打包策略：

```json
{
  "sharedPackages": {
    "sjcl": { "bundled": true },
    "y-webrtc": { "bundled": true, "singleton": true },
    "lib0": { "bundled": false, "singleton": true },
    "y-protocols": { "bundled": false, "singleton": true },
    "@jupyterlab/application": { "bundled": false, "singleton": true, "requiredVersion": "^3.1.0" }
  }
}
```

| 包 | bundled | singleton | 说明 |
|----|---------|-----------|------|
| sjcl | true | false | 打包进扩展（需要SHA256） |
| y-webrtc | true | true | 打包进扩展，全局单例（含补丁） |
| lib0 | false | true | 使用宿主版本，单例 |
| y-protocols | false | true | 使用宿主版本，单例 |
| @jupyterlab/* | false | true | 使用 JupyterLab 宿主版本 |

**关键设计**：y-webrtc 必须 bundled=true，因为补丁需要随扩展一起分发。singleton=true 确保整个应用只有一个 y-webrtc 实例（避免多实例冲突）。

## 上游合并状态

补丁最初由 @datakurre 贡献，README 中提到：

> Two vendored patches (special thanks to @datakurre) are applied to simple-peer and int64-buffer, both of which are licensed under the MIT license, and should hopefully be merged some day.

这些补丁是临时方案，期望未来合并到上游 simple-peer 或被 y-webrtc 原生支持。

## 相关概念

- [WebRtcProvider文档提供者](04-document-provider.md)
- [构建与打包系统](10-build-and-packaging.md)
- [房间ID与信令机制](05-room-and-signaling.md)
