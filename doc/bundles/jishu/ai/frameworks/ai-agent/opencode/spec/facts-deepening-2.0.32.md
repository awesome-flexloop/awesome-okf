---
type: spec
title: "OpenCode 2.0.32 同快照深化事实"
source: "../references/source-deepening-2.0.32.md"
sources:
  - id: deepening-source
    resource: ../references/source-deepening-2.0.32.md
    title: 同快照深化信源
---

# OpenCode 2.0.32 同快照深化事实

本轮新增 37 条事实 F-115～F-151，续接[前轮事实](facts-2.0.32.md)。全部源码固定到 `6ec56821d63100fe5bda45b759364f561c56b359`。路径以仓库根为基准，链接指向实现主证据；同一行的补充文件仍属于该固定快照。测试仅阅读，未运行。

## 配置与上下文

| 编号 | 客观事实 | 固定实现证据 |
|---|---|---|
| F-115 | Config.latest(entries,key) 找到最后一个该字段非undefined的document，返回其字段值info[key]；entries 顺序为 managed policies、wellknown、global supplementary、explicit、direct、project supplementary、content、managed settings。 | [config.ts:254-290](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/core/src/config.ts#L254-L290)；补充范围见下表。 |
| F-116 | ConfigDiscovery 分离来源，project walk 排除已解析的 global roots/files，direct/project 列表反转后返回。 | [discovery.ts:67-145](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/core/src/config/discovery.ts#L67-L145) |
| F-117 | ConfigInstructionPlugin 组合 global/project/configured；URL获取timeout为5秒，失败保留旧副本，否则跳过URL；空来源数组仍可产生available。editor.unavailable对应不可用状态或激活失败，不是URL失败本身。 | [instruction.ts:78-230](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/core/src/config/plugin/instruction.ts#L78-L230) |
| F-118 | ConfigSkillPlugin 消费directory的skill/skills及document.skills；后读同ID覆盖，watcher经100ms debounce后rescan/reload。 | [skill.ts:85-116,147-193](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/core/src/config/plugin/skill.ts#L85-L193) |
| F-119 | SkillScan 找到SKILL.md停止下探；无SKILL.md的根采普通.md，depth最多6；SkillFile.parse派生ID，metadata opencode/autoinvoke优先于disable-model-invocation。 | [skill-scan.ts:7-46](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/core/src/config/plugin/skill-scan.ts#L7-L46)；[skill-file.ts:39-63](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/core/src/config/plugin/skill-file.ts#L39-L63) |
| F-120 | SessionInstructions inFlight防同Session/path并发重复；持久去重来自模型可见synthetic metadata.instruction.paths；ensuring释放claim。 | [session/instructions.ts:35-109](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/core/src/session/instructions.ts#L35-L109) |
| F-121 | SessionCompaction默认auto=true、keep=15000；非manual且auto=false返回skipped，含overflow；配置插件逐document消费auto/buffer/keep.tokens。 | [session/compaction.ts:203-239](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/core/src/session/compaction.ts#L203-L239)；[plugin/compaction.ts:10-26](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/core/src/config/plugin/compaction.ts#L10-L26) |
| F-122 | compaction分summary/native；native要求provenance及路由后compatible；calculateCeiling显式buffer直接扣除，否则保留窗口15%，足够大时至少16000。 | [compaction.ts:340-373,941-947](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/core/src/session/compaction.ts#L340-L373) |

## Codemode

| 编号 | 客观事实 | 固定实现证据 |
|---|---|---|
| F-123 | CodeMode.execute委托make(options).execute(code)；executeProgram经Acorn script parse，允许顶层await/return，经Interpreter.run执行。 | [codemode.ts:139-163](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/codemode/src/codemode.ts#L139-L163)；[execute.ts:36-43,109-116](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/codemode/src/interpreter/execute.ts#L36-L116) |
| F-124 | runtime复用prepared tools/catalog；每次executeProgram的Effect.suspend新建builtins、调用记录、logs、Pending与Interpreter。 | [execute.ts:27-44](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/codemode/src/interpreter/execute.ts#L27-L44) |
| F-125 | ToolRuntime零参数归一为{}，拒绝多参数；Effect Schema解码，普通JSON Schema直接传值；未声明output时返回undefined。 | [tool-runtime.ts:399-440](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/codemode/src/tool-runtime.ts#L399-L440)；[tool-schema.ts:295-303](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/codemode/src/tool-schema.ts#L295-L303) |
| F-126 | timeoutMs/maxToolCalls/maxOutputBytes可选且无默认；校验安全整数/下限；计数在解码后、before hook前。 | [codemode.ts:21-35,126-137](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/codemode/src/codemode.ts#L126-L137)；[tool-runtime.ts:392-417](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/codemode/src/tool-runtime.ts#L392-L417) |
| F-127 | 正常返回在plain-data copy-out后中断pending；timeout在copy-out前返回失败，copy-out后未结束后台工作可返回成功及warning。 | [execute.ts:33-88](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/codemode/src/interpreter/execute.ts#L33-L88) |
| F-128 | maxOutputBytes在结果产生后裁剪value/logs；warnings有独立等额预算；toolCalls/error/截断提示不受统一响应字节预算。 | [execute.ts:102-104,119-192](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/codemode/src/interpreter/execute.ts#L119-L192) |
| F-129 | Core Tool.snapshot将codemode===false工具留direct，其余进inventory；子调用仍经beforeExecute/executeTool。 | [core/tool.ts:227-281](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/core/src/tool.ts#L227-L281) |
| F-130 | CodeModeTool用WeakMap<Inventory,Runtime<Run>>缓存，逐调用注入Run；make传tools/extensions/hooks，未传limits；typed output优先，否则text/null。 | [core/codemode/tool.ts:56-63,89-124,233-263](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/core/src/codemode/tool.ts#L89-L124) |

## 扩展与产品状态

| 编号 | 客观事实 | 固定实现证据 |
|---|---|---|
| F-131 | Plugin.Info公开source/features/state；state为active/failed；plugin.updated为data={}的ephemeral event。 | [schema/plugin.ts:10-49](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/schema/src/plugin.ts#L10-L49) |
| F-132 | Event.latest按durable version取最新，歧义重复抛错；durableMap只收durable，以type.version为键并拒绝重复。 | [schema/event.ts:151-188](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/schema/src/event.ts#L151-L188) |
| F-133 | Effect Plugin.effect(context)返回Effect<void,never,R>，R默认Scope；Promise setup返回Cleanup/void或Promise；adapter以acquireRelease调用cleanup。 | [effect/plugin.ts:57-64](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/plugin/src/effect/plugin.ts#L57-L64)；[promise/plugin.ts:55-66](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/plugin/src/promise/plugin.ts#L55-L66)；[adapter.ts:619-622](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/plugin/src/promise/adapter.ts#L619-L622) |
| F-134 | PluginModule在模块读取/npm解析前检查integration.use managed policy；default必须有string id及effect/setup函数；install=false且非本地无入口返回pending。 | [plugin/module.ts:44-61,78-151](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/core/src/plugin/module.ts#L44-L151) |
| F-135 | activate保留id/revision相同前缀，逆序关闭变化后缀、顺序加载；相同失败revision不因重排重试，新revision可重试，健康fallback可重载；Hook按注册顺序遍历，finalizer/dispose移除。 | [core/plugin.ts:90-180](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/core/src/plugin.ts#L90-L180)；[hooks.ts:69-95](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/core/src/plugin/hooks.ts#L69-L95) |
| F-136 | TUI update在Flock内重读、mutation、writeJsonAtomic再setStore；原子写临时文件+rename，失败清理并抛错。 | [tui/storage.tsx:47-93](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/tui/src/context/storage.tsx#L47-L93)；[persistence.ts:22-33](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/tui/src/util/persistence.ts#L22-L33) |
| F-137 | TUI watcher合并50ms事件后重读；读/解析失败回initial，watch失败关闭live reload；flush等待pending/allSettled，close不自动flush。 | [storage.tsx:61-67,102-149](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/tui/src/context/storage.tsx#L102-L149) |
| F-138 | App settings.v3经persisted分流storage；persistStore默认100ms延迟，async hydration仅未touched时应用，dirty时暂存remote；storage.setItem未await。 | [settings/model.tsx:306-310,345-347](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/app/src/settings/model.tsx#L306-L347)；[storage.ts:586-768](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/app/src/runtime/persistence/storage.ts#L586-L768)；[persist.ts:5-115](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/app/src/runtime/persistence/persist.ts#L5-L115) |
| F-139 | Desktop storage复用App createNamespaceStorage，driver接storeItems/update/clear；即时改cache，本地sequence/host revision排除旧ACK/event；失败重新排队未被新值替代的key。 | [desktop/storage.ts:11-38](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/desktop/src/renderer/platform/storage.ts#L11-L38)；[namespace.ts:57-170](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/app/src/runtime/persistence/namespace.ts#L57-L170) |
| F-140 | StorageUpdate payload为name/insert/remove，success为Number；handler state.update排队、广播其他窗口、返回revision；state writer延迟250ms执行SQLite transaction，失败保留可重试记录。 | [RPC storage.ts:10-17](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/desktop/src/shared/ipc-rpc/storage.ts#L10-L17)；[handler:17-30](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/desktop/src/main/ipc-handlers/storage.ts#L17-L30)；[state.ts:12-93](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/desktop/src/main/storage/state.ts#L12-L93)；[write-behind.ts:3-48](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/desktop/src/main/storage/write-behind.ts#L3-L48) |

## 回放、云端与更新

| 编号 | 客观事实 | 固定实现证据 |
|---|---|---|
| F-141 | simulationReplacements替换HTTP layer；无OPENCODE_DRIVE仅模拟网络，有值则解析manifest并安装SimulatedProvider/OpenAI route，安装失败orDie中止启动。 | [backend/index.ts:24-57](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/simulation/src/backend/index.ts#L24-L57) |
| F-142 | layerDrive每invocation建容量256的queue；stream acquireRelease关闭queue/清pending；llm.attach替换旧订阅，chunk/finish/disconnect分别入队/结束/失败。 | [simulated-provider.ts:154-295,314-355](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/simulation/src/backend/simulated-provider.ts#L154-L355) |
| F-143 | Timeline写version=1/base64 header及output/resize JSONL，pointer写sidecar，共用单调时钟；finish等待自身/子流并传播失败。 | [recording.ts:65-162](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/simulation/src/recording.ts#L65-L162) |
| F-144 | record捕获真实响应、脱敏存储副本，经Deferred按请求开始顺序append，调用返回未脱敏快照；replay用脱敏请求匹配未领取interaction并claim。 | [http/recorder.ts:72-149](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/http-recorder/src/http/recorder.ts#L72-L149) |
| F-145 | auto在CI非空且非false/0时选replay，否则按exists选replay/record；pool缓存读取，以SynchronizedRef原子领取；成功scope查未用记录，failure/尝试但零领取/missing有例外。 | [replay/state.ts:5-79](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/http-recorder/src/replay/state.ts#L5-L79) |
| F-146 | store默认cwd/test/fixtures/recordings，拒绝绝对路径/..，append检查possible secrets后临时文件+rename；multi-step夹具step1/2对应first/second；HTTP测试定义乱序、并发claim、未用记录、CI missing与live/redacted。 | [store.ts:7-159](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/http-recorder/src/cassette/store.ts#L7-L159)；[multi-step.json:1-41](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/http-recorder/test/fixtures/recordings/http/multi-step.json#L1-L41)；[http.test.ts:22-149](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/http-recorder/test/http.test.ts#L22-L149)；补充范围见下表。 |
| F-147 | Console responses POST调用proxyInference，路径/key归一后转Resource.INFERENCE.fetch；异常503/no-store，上游404转换400。 | [responses.ts:1-6](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/console/app/src/routes/zen/v1/responses.ts#L1-L6)；[inference-proxy.ts:3-60](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/console/app/src/lib/inference-proxy.ts#L3-L60) |
| F-148 | Stats以1小时节奏执行，UTC日首次full，失败再incremental且仍记录当天full已尝试；initialDelay依据lastSyncedAt。 | [stat-sync.ts:8-60](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/stats/server/src/stat-sync.ts#L8-L60) |
| F-149 | files Worker接受/files/的GET/HEAD/OPTIONS，处理条件请求/单段Range；get带etagMatches，对象变更返回503/no-store；完整可缓存且≤512MiB时异步入cache。 | [files/index.ts:1-163](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/services/files/src/index.ts#L1-L163) |
| F-150 | updater main仅packaged且非dev启用platform；machine分check/stage/install/restart，Deferred合并并发，已有downloaded时传differential:false；平台disableDifferentialDownload设置仅对Windows生效，macOS另有分支；platform autoDownload=false，restart 10秒未开始报错。 | [main.ts:9-50](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/gui-extensions/src/updater/main.ts#L9-L50)；[machine.ts:150-260](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/gui-extensions/src/updater/machine.ts#L150-L260)；[platform.ts:99-133](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/gui-extensions/src/updater/platform.ts#L99-L133)；补充范围见下表。 |
| F-151 | TUI UpdateSource分subscribe/check/apply；available时install调用apply，resolve设installed，reject设failed；installed时restart调用exit；通知历史与检查状态分开。 | [update-notification.tsx:18-140](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/tui/src/context/update-notification.tsx#L18-L140) |

## 测试与范围

### 合并事实的补充证据

以下链接补齐合并断言的实际可点击范围，编号不增加。F-146原标签中的285-309属于204/二进制测试，不是live/redacted证据。

| 编号 | 子断言 | 固定源码范围 |
|---|---|---|
| F-115 | latest返回字段值 | [config.ts:24-26](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/core/src/config.ts#L24-L26) |
| F-122 | ceiling与保留常量 | [compaction.ts:97-103](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/core/src/session/compaction.ts#L97-L103)；[941-947](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/core/src/session/compaction.ts#L941-L947) |
| F-124 | prepared/catalog构造与复用 | [codemode.ts:145-163](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/codemode/src/codemode.ts#L145-L163) |
| F-130 | WeakMap缓存与make接线 | [core/codemode/tool.ts:233-255](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/core/src/codemode/tool.ts#L233-L255) |
| F-137 | 读/解析失败回initial | [storage.tsx:61-67](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/tui/src/context/storage.tsx#L61-L67) |
| F-146 | CI missing请求失败与live/redacted | [http.test.ts:180-193](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/http-recorder/test/http.test.ts#L180-L193)；[253-277](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/http-recorder/test/http.test.ts#L253-L277) |
| F-150 | stage参数、autoDownload与平台分支 | [machine.ts:44-85](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/gui-extensions/src/updater/machine.ts#L44-L85)；[platform.ts:8-24](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/gui-extensions/src/updater/platform.ts#L8-L24)；[60-73](https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/packages/gui-extensions/src/updater/platform.ts#L60-L73) |

实现与测试/调用方对照、正文与片段读取、未读边界见[六主题信源矩阵](../references/source-deepening-2.0.32.md)。没有执行OpenCode测试、真实模型、更新或云部署；不能将本表转述为运行验证结论。

## 数量口径与勘误

- 37条指表格中的唯一F编号，不是文件或workspace总数；与R草稿逐编号对齐。
- 256/6/15000/16000/15%/100ms/50ms/250ms/1小时/512MiB/10秒都是局部实现常量或计算分支，不是整体性能、安全或容量保证。
- R草稿EOF机械检查修正八处过长证据范围，补全skill-file路径；本表使用修正后坐标，不改变机制结论。最终V需同时核验“行号在范围内”及“正文支持断言”，二者不能替代。
- 前轮39个manifest及6/4/29覆盖统计保留为历史，不合并为本轮深读总量。
- Task8内容回验修正字段值、URL失败与平台差分下载语义，并补齐合并事实证据；修订同步R草稿与概念10/15，随后执行只读回归，不把EOF检查等同内容正确。

## 相关概念

- [本轮洞察与地图](insights-deepening-2.0.32.md)
- [同快照深化信源](../references/source-deepening-2.0.32.md)
