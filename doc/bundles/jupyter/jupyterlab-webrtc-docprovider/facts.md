---
type: Facts
okf_version: "0.2"
title: "jupyterlab-webrtc-docprovider 源码事实清单"
generated: "2026-08-22"
tags: [jupyter, webrtc, yjs, collaboration, jupyterlab]
sources:
  - ../../../../../external/libs/jupyter/jupyterlab-webrtc-docprovider/package.json
  - ../../../../../external/libs/jupyter/jupyterlab-webrtc-docprovider/src/provider.ts
  - ../../../../../external/libs/jupyter/jupyterlab-webrtc-docprovider/src/manager.ts
  - ../../../../../external/libs/jupyter/jupyterlab-webrtc-docprovider/src/plugin.ts
  - ../../../../../external/libs/jupyter/jupyterlab-webrtc-docprovider/src/tokens.ts
  - ../../../../../external/libs/jupyter/jupyterlab-webrtc-docprovider/vendor/SimplePeerExtended.js
  - ../../../../../external/libs/jupyter/jupyterlab-webrtc-docprovider/schema/plugin.json
  - ../../../../../external/libs/jupyter/jupyterlab-webrtc-docprovider/jupyterlab_webrtc_docprovider/__init__.py
  - ../../../../../external/libs/jupyter/jupyterlab-webrtc-docprovider/setup.py
  - ../../../../../external/libs/jupyter/jupyterlab-webrtc-docprovider/webpack.config.js
---
# jupyterlab-webrtc-docprovider 源码事实清单

## 项目元数据与依赖（npm）

- F-001: `package.json:2-3` — npm 包名 `@jupyterlite/webrtc-docprovider`，version 为 `0.1.2`
- F-002: `package.json:4` — description 为 "Document collaboration for JupyterLab and JupyterLite, powered by y-webrtc"
- F-003: `package.json:53-64` — dependencies 声明 `@jupyterlab/*`（application/apputils/coreutils/docprovider/settingregistry/statusbar/translation/ui-components，均 `^3.1.0`）与 `sjcl ^1.0.8`、`y-webrtc ^10.2.0`
- F-004: `package.json:20-26` — scripts：`build` 依次执行 `build:schema` → `build:lib` → `build:labextension:dev`；`build:schema` 为 `json2ts schema/plugin.json src/_schema.ts`，`build:lib` 为 `tsc`
- F-005: `package.json:109-113` — `jupyterlab` 段声明 `extension: "./lib/plugin.js"`、`outputDir: "jupyterlab_webrtc_docprovider/labextension"`、`schemaDir: "schema"`、`webpackConfig: "./webpack.config.js"`
- F-006: `package.json:114-170` — `sharedPackages` 配置：`y-webrtc`（bundled true + singleton true）、`lib0`/`y-protocols`（bundled false + singleton true）、全部 `@jupyterlab/*`（bundled false + singleton true 且 requiredVersion `^3.1.0`）、`sjcl`（bundled true）
- F-007: `package.json:172-173` — `style: "style/index.css"`、`styleModule: "style/index.js"`

## Python 打包与包结构

- F-008: `pyproject.toml:1-6` — build-system 声明 `jupyter_packaging>=0.10,<1` 与 `jupyterlab>=3.1,<4`，build-backend 为 `jupyter_packaging.build_api`
- F-009: `pyproject.toml:8-15` — `[tool.jupyter-packaging.options]`：skip-if-exists 指向 `labextension/static/style.js`，ensured-targets 指向 `labextension/package.json` 与 `labextension/static/style.js`
- F-010: `pyproject.toml:17-22` — builder 为 `jupyter_packaging.npm_builder`，build-args `build_cmd = "build:prod"`、`npm = ["jlpm"]`
- F-011: `setup.py:13-18` — 从 `package.json` 读取 `pkg_json`，`lab_path = HERE / pkg_json["jupyterlab"]["outputDir"]`
- F-012: `setup.py:25-32` — `data_files_spec` 把 labextension 目录与 `install.json` 安装到 `share/jupyter/labextensions/<labext_name>`
- F-013: `setup.py:36-41` — version 由 `pkg_json["version"]` 的 `-alpha.`/`-beta.`/`-rc.` 替换为 `a`/`b`/`rc` 得到
- F-014: `setup.py:80-88` — 通过 `jupyter_packaging` 的 `wrap_installers`/`npm_builder`/`get_data_files` 注入 `cmdclass`（post_develop 用 `build_cmd="install:extension"`）与 `data_files`
- F-015: `jupyterlab_webrtc_docprovider/__init__.py:5-6` — `_jupyter_labextension_paths()` 返回 `[{"src": "labextension", "dest": __js__["name"]}]`
- F-016: `jupyterlab_webrtc_docprovider/_version.py:5-13` — `__js__` 读取 `labextension/package.json`，`__version__` 由其 `version` 字段做 alpha/beta/rc 替换后得到
- F-017: `jupyterlab_webrtc_docprovider/tests/test_metadata.py:4-15` — `test_version` 断言 `__version__` 非空；`test_labextensions` 断言 `_jupyter_labextension_paths()` 长度恰为 1

## 常量与 token（src/tokens.ts）

- F-018: `tokens.ts:12` — `NS = '@jupyterlite/webrtc-docprovider'`
- F-019: `tokens.ts:17-32` — 四个插件 ID：`PLUGIN_ID`/`FACTORY_PLUGIN_ID`/`STATUS_PLUGIN_ID`/`RETRO_STATUS_PLUGIN_ID` 均为 `${NS}:<后缀>`
- F-020: `tokens.ts:35-43` — `RETRO_NOTEBOOK_PAGE = 'notebooks'`、`RETRO_EDIT_PAGE = 'edit'`、`RETRO_STATUS_PAGES` 数组聚合两者
- F-021: `tokens.ts:48-57` — `DEFAULT_SIGNALING_SERVERS` 含三个公共信令服务器 URL（`wss://signaling.yjs.dev` 等）；`LOCAL_HOSTS = ['127.0.0.1', 'localhost']`
- F-022: `tokens.ts:62-93` — `CommandIds.disable = 'webrtc-docprovider:disable'`；`PageOptions` 定义 `urls='fullWebRtcSignalingUrls'`、`prefix='webRtcRoomPrefix'`、`collaborative='collaborative'` 三个 page-config 键；`IWebRtcManager = new Token<IWebRtcManager>(`${NS}:IWebRtcManager`)` 及其接口定义（createProvider/username/usercolor/roomName/disabled/peerCount/signalingUrls/stateChanged）

## WebRtcProvider 适配层（src/provider.ts）

- F-023: `provider.ts:14` — `export class WebRtcProvider extends WebrtcProvider implements IDocumentProvider`
- F-024: `provider.ts:15-30` — 构造函数以 `` `${options.room}${options.path}` `` 作为 room、`options.ymodel.ydoc` 作为文档，`this.awareness = options.ymodel.awareness`；当本地 state 存在且无 `name` 字段时调用 `setLocalStateField('user', {name, color})`
- F-025: `provider.ts:36-55` — `requestInitialContent()` 返回 Promise：首次调用注册 'synced' 事件监听并 resolve 同步结果，1 秒（`setTimeout`）内未同步则 `resolve(false)`
- F-026: `provider.ts:57-67` — `setPath()` 为空方法体；`putInitializedState()` 为 no-op；`acquireLock()` 返回 `Promise.resolve(0)`；`releaseLock(lock)` 为 no-op
- F-027: `provider.ts:75-91` — `WebRtcProvider.IOptions` 接口（room/username/usercolor/signalingUrls，extends `IDocumentProviderFactory.IOptions`）与 `IYjsWebRtcOptions` 接口（signaling/password/awareness/maxConns/filterBcConns/peerOpts）
- F-028: `provider.ts:100-114` — `yProviderOptions()`：`signaling` 缺省取 `DEFAULT_SIGNALING_SERVERS`、`password: null`、`awareness: new Awareness(ydoc)`、`maxConns: 20 + Math.floor(Math.random() * 15)`、`filterBcConns: true`、`peerOpts: {}`

## WebRtcManager 工厂（src/manager.ts）

- F-029: `manager.ts:33-42` — `export class WebRtcManager implements IWebRtcManager`；构造函数连接 `settings.changed` → `_stateChanged.emit(void 0)`，并调用 `initUrlParams()`/`initRandomParams()`
- F-030: `manager.ts:49-73` — `createProvider`：`this.disabled` 时返回 `new ProviderMock()`；否则构造 `WebRtcProvider` 并监听 'peers' 事件，以 `room.webrtcConns.size + room.bcConns.size` 更新 `peerCount`
- F-031: `manager.ts:78-94` — `initUrlParams()` 从 `window.location.search` 解析 `room`/`username`/`usercolor` 三个 URL 参数；`initRandomParams()` 生成 `UUID.uuid4()` room、`getRandomColor().slice(1)` usercolor、`getAnonymousUserName()` username
- F-032: `manager.ts:107-113` — `disabled` getter：仅当 `PageConfig.getOption('collaborative') === 'true'` 时返回 `this._composite.disabled`，否则直接返回 true
- F-033: `manager.ts:123-157` — `username`/`usercolor`/`roomName` 三个 getter 均按"URL 参数 → 插件设置 → 随机值"的短路求值顺序（`||`）解析
- F-034: `manager.ts:167-178` — `fullRoomId`：roomPrefix 依次取 `PageConfig 'webRtcRoomPrefix'`、设置 `roomPrefix`、否则本地主机（`LOCAL_HOSTS`）用 `UUID.uuid4()` 而其他 host 用 `window.location.origin`；最终 `codec.hex.fromBits(hash.sha256.hash(`${roomPrefix}-${roomName}`))`
- F-035: `manager.ts:188-210` — `signalingUrls`：先 `JSON.parse(PageConfig 'fullWebRtcSignalingUrls')`，再取设置 `signalingUrls`，均无效时 `console.warn` 提示"不推荐用于生产"并返回 `DEFAULT_SIGNALING_SERVERS`
- F-036: `manager.ts:215-249` — `peerCount` setter 在值变化时 emit `stateChanged`；`stateChanged`/`trans` getter 与 `_settings`/`_urlParams`/`_randomParams`/`_peerCount` 私有字段

## 插件注册（src/plugin.ts）

- F-037: `plugin.ts:31-82` — 主插件：`id: PLUGIN_ID`、`autoStart: true`、`provides: IWebRtcManager`、`optional: [ISettingRegistry, ITranslator, ICommandPalette]`；activate 中 `settingRegistry.load(PLUGIN_ID)` 加载设置，`commands.addCommand(CommandIds.disable, ...)`（isToggleable、isToggled 读 `settings.composite.disabled`、execute 写 `settings.set('disabled', ...)`），palette 存在时 `palette.addItem`，最后 `new WebRtcManager(options)`
- F-038: `plugin.ts:84-95` — factoryPlugin：`id: FACTORY_PLUGIN_ID`、`provides: IDocumentProviderFactory`、`requires: [IWebRtcManager]`，activate 返回 `manager.createProvider`
- F-039: `plugin.ts:97-111` — statusPlugin：`requires: [IWebRtcManager]`、`optional: [IStatusBar]`，创建 `WebRtcStatus.Model` 与 `WebRtcStatus`，`status.registerStatusItem(STATUS_PLUGIN_ID, {align: 'right', item})`
- F-040: `plugin.ts:113-144` — retroStatusPlugin：读取 `PageConfig.getOption('retroPage')`，为空则返回；否则为 `app.docRegistry` 注册 `Notebook` 与 `Editor` 的 widget extension，在 `retropage === 'edit'` 时插入 spacer，`toolbar.addItem(RETRO_STATUS_PLUGIN_ID, item)` 并返回 `DisposableDelegate`
- F-041: `plugin.ts:146` — `export default [plugin, statusPlugin, factoryPlugin, retroStatusPlugin]`

## Schema 定义（schema/plugin.json + src/_schema.ts）

- F-042: `schema/plugin.json:2-13` — `$schema` 为 draft-07、`additionalProperties: false`、`jupyter.lab.setting-icon` 为 `webrtc-docprovider:webrtc`；`disabled` 属性 `default: false`、`type: boolean`
- F-043: `schema/plugin.json:14-48` — `room` 与 `roomPrefix` 均为 `oneOf [null, string]`，其中 `roomPrefix` 的 string 分支带 `minLength: 10`
- F-044: `schema/plugin.json:49-69` — `signalingUrls` 为 `oneOf`：string 数组（item `pattern: "wss?://.*"`）或 null（默认公共信令）
- F-045: `schema/plugin.json:70-104` — `usercolor`（string 分支 `pattern: "[0-9a-f]{3}|[0-9a-f]{6}"`）与 `username` 均为 `oneOf [null, string]`
- F-046: `src/_schema.ts:1-83` — 文件头注释声明该文件由 `json-schema-to-typescript` 自动生成、勿手改（应修改 `schema/plugin.json`）；`interface WebRTCSharing` 聚合 `disabled`/`room`/`roomPrefix`/`signalingUrls`/`usercolor`/`username` 六个可选属性

## Vendor 增强传输层（vendor/SimplePeerExtended.js）

- F-047: `vendor/SimplePeerExtended.js:1-6` — `import Peer from 'simple-peer/simplepeer.min.js'`、`require('./int64-buffer.min.js')`；常量 `CHUNK_SIZE = 1024*16 - 512`（约 16KB）、`TX_SEND_TTL = 30s`、`MAX_BUFFERED_AMOUNT = 64KB`
- F-048: `vendor/SimplePeerExtended.js:22-31` — `class SimplePeerExtended extends Peer`，构造函数初始化 `_txOrdinal`/`_rxPackets`/`webRTCMessageQueue`/`webRTCPaused`
- F-049: `vendor/SimplePeerExtended.js:33-76` — `encodePacket` 把 `txOrd`/`index`/`length`/`totalSize`/`chunkSize` 五个 `Int64BE`（各 8 字节）头与 chunk 拼接；`packetArray` 按 `CHUNK_SIZE` 切块并逐块编码
- F-050: `vendor/SimplePeerExtended.js:78-108` — `_onChannelMessage` 按 `txOrd` 收集分片，chunkSize 等于 totalSize 时直接 `push`，否则凑齐所有 index 后 `sortPacketArray` 排序、`concatenate` 重组并 `push`，`TX_SEND_TTL` 后清理 `_rxPackets`
- F-051: `vendor/SimplePeerExtended.js:109-146` — `send` 把消息切块后并入 `webRTCMessageQueue`；`sendMessageQueued` 实现背压：`_channel.bufferedAmount > MAX_BUFFERED_AMOUNT` 时置 `webRTCPaused=true` 并监听 `bufferedamountlow` 事件恢复发送

## 构建 hack（webpack.config.js）

- F-052: `webpack.config.js:6-27` — `resolve.fallback: { crypto: false }`、`devtool: 'source-map'`；`string-replace-loader` 规则匹配 `/y-webrtc\.js$/`，把 `y-webrtc.js` 内的 `'simple-peer/simplepeer.min.js'` 引用替换为 `vendor/SimplePeerExtended.js`（注释引用 y-webrtc PR #25 修复 WebRTC buffered transmission）

## 图标与样式

- F-053: `src/icons.ts:10-23` — `webrtcIcon`/`shareIcon`/`shareOffIcon` 三个 `LabIcon`（name 分别为 `webrtc-docprovider:webrtc`/`:share`/`:share-off`，svgstr 来自 `style/img/*.svg`）；`style/index.js:4` 仅 `import './base.css'`；`install.json:2-4` — `packageManager: "python"`、`packageName: "jupyterlab-webrtc-docprovider"`
