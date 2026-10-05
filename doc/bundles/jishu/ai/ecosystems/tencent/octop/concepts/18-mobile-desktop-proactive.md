---
type: Concept
title: "远程手机、远程桌面与主动关怀"
description: "Remote Android 的四类后端探测、Redroid 容器与 H264 串流、6 个 mobile 工具；远程桌面的会话上限、VNC/display 与 systemd 装配；主动关怀的情绪权重评分、时间窗回退与调度约束。"
tags: [octop, mobile, redroid, adb, h264, desktop, vnc, proactive-care, scheduler]
generated: { by: "reference_agent/trae-cn", at: 2026-10-04T10:00:00+08:00 }
verified: { by: "process:grep-v", at: 2026-10-04T10:00:00+08:00 }
status: stable
stale_after: 2027-10-04
sources:
  - id: facts
    resource: /spec/facts.md
    title: Octop 源码事实清单 F-455~F-470、F-497~F-502（v1.0.2b5，commit e473dd3c）
---

# 远程手机、远程桌面与主动关怀

除了聊天与浏览器，Octop 还把两类「设备能力」收进同一进程：远程手机（Remote Android）与远程桌面（Remote Desktop）。二者都是「能力探测 → 环境装配 → 会话/串流」的同构设计；主动关怀（Proactive Care）则是一个不经过 Agent ReAct 循环的定时推送子系统。三者分别位于 `infra/mobile/`、`infra/desktop/`、`infra/proactive/`。

## 远程手机：6 个工具与四类后端

Agent 侧可见的 mobile 工具实测 **6 个**（F-455）：

| 工具名 | 作用 |
|---|---|
| `mobile_screenshot` | 截屏 |
| `mobile_tap` | 点击坐标 |
| `mobile_swipe` | 滑动（duration 约束 50~5000ms，默认 300，F-456） |
| `mobile_launch_app` | 启动 App |
| `mobile_ui_dump` | 拉取 UI 层次 XML |
| `mobile_handoff_to_user` | 把设备交还给真人操作 |

UI dump 落盘在设备侧 `/sdcard/octop_ui_dump.xml`，回传文本截断上限 48,000 字符，避免撑爆模型上下文（F-455）。工具调用前要过两道门：主机 `capabilities.mobile.enabled` 为真，且非 admin 用户必须持有 `mobile` 权限；随后 `mobile_status` 必须为 `ready`（F-455）。

主机能跑哪种 Android，由安装期探测决定。后端是一个四值 Literal（F-457）：

```python
MobileBackend = Literal["physical", "redroid", "emulator", "none"]
```

探测规则（`probe_host_capability`，F-457）：

```
            Darwin / Windows  ──▶  physical（直接假设有真机/ADB）
Linux ──┬── /dev/binder 存在或 binder_linux 已加载 ──▶ redroid
        ├── /dev/kvm 存在                            ──▶ emulator
        └── 两者皆无                                  ──▶ none, reason="no_binder_or_kvm"
其他平台 ──▶ none, reason="unsupported_platform:{system}"
```

探测结果序列化为 `config.json` 的 `capabilities.mobile` 段，共 4 个键：`enabled`、`backend`、`probed_at`、`reason`；`probed_at` 缺失时只探测一次并重载配置（F-459）。

## Redroid 容器与设备映射

云手机的默认形态是 Redroid 容器。装配常量（F-458、F-464）：

| 项 | 值 |
|---|---|
| 容器名 | `octop-mobile-android` |
| ADB 端点 | `127.0.0.1:5555` |
| 默认镜像 | `redroid/redroid:13.0.0-latest` |
| 启动等待 | `BOOT_WAIT_SECS=45` |
| 脚本目录 | `scripts/linux/v1.0` |

`install.sh` 的容器参数为 `--privileged --cgroupns=host --restart unless-stopped`，并把宿主机的 binder 能力映射进容器（F-464）：

```bash
# /dev/binder  → Redroid 需要的 binder 字符设备
# /dev/binderfs → 存在时整目录绑定挂载，嵌套 Redroid 更稳
if [ -d /dev/binderfs ]; then _run_args+=(-v /dev/binderfs:/dev/binderfs); fi
if [ -e /dev/binder ];    then _run_args+=(--device /dev/binder);    fi

# 优先 host 网络（与 dockerd 共享 localhost，adb 127.0.0.1:5555 直达）
# 不可用再退回 -p 5555:5555
docker run -d "${_run_args[@]}" redroid/redroid:13.0.0-latest \
    androidboot.redroid_gpu_mode=guest
```

设备节点与后端是一一对应的：**redroid 吃 `/dev/binder`（或 binderfs/binder_linux 模块），emulator 吃 `/dev/kvm`**——这正是探测函数两个分支的由来（F-457、F-464）。若三者都没有，脚本直接退出并提示改用真机 USB 或 KVM 模拟器。

Docker 环境本身可由系统自动安装，`docker_install.py` 内置 **5 个安装源**，官方源优先、按延时竞速、不做地域判断（F-460）：

```
https://download.docker.com
https://mirrors.aliyun.com/docker-ce
https://mirrors.tencent.com/docker-ce
https://mirrors.163.com/docker-ce
https://mirrors.cernet.edu.cn/docker-ce
```

超时预算为：每源测速 3 次、单次 5 秒，probe 3 秒，daemon 就绪 10 秒，重启后等待 30 秒、轮询间隔 2 秒，安装脚本 readline 容忍 600 秒（F-461）；daemon 配置写入 `/etc/docker/daemon.json`，腾讯云上的专用镜像主机是 `mirror.ccs.tencentyun.com`（F-460）。

## ADB、H264 串流与单例绑定

`adb.py` 是设备交互层：设备行正则匹配 `(device|emulator)`，读取 `ANDROID_HOME`/`ANDROID_SDK_ROOT` 定位 adb，默认连接 `127.0.0.1:5555`（F-462）。屏幕录制直接消费 `screenrecord` 的裸 H.264 输出（F-462）：

```python
# adb.py:155-166
bit_rate: int = 4_000_000        # 4 Mbps
size: str | None = "720x1600"    # 竖屏 720p
# screenrecord --output-format=h264 --time-limit=0 --bit-rate=4000000 --size=720x1600
```

`--time-limit=0` 表示持续录制，由 Octop 侧维持长连接；NAL 拆帧在 `h264.py` 的 `AnnexBSplitter` 中完成，类型常量 SLICE=1、IDR=5、SPS=7、PPS=8，并输出浏览器可播的 `avc1` 编解码串（F-464）。截屏 JPEG 路径把图片缩到 max_side=720、quality=80；输入注入超时 20 秒，常用 keycode 为 HOME=3、BACK=4、APP_SWITCH=187、POWER=26、音量 ±（F-463）。

`MobileAgentControl` 是 frozen dataclass（字段 `enabled`、`device`），持有进程级单例：**同一时刻整个进程只绑定一台设备**（F-464）。模块也可用 `python -m octop.infra.mobile <config.json>` 独立运行，参数个数错误时退出码 2（F-464）。

## 远程桌面：3 路会话上限

桌面能力属于 `infra/desktop/`（在 compose 模板中被称为已预装的 desktop 附加组件）。会话注册是进程内的全局字典（F-465）：

```python
_capture_executor = ThreadPoolExecutor(max_workers=4)   # 截屏线程池
_input_executor   = ThreadPoolExecutor(max_workers=8)   # 输入线程池
_MAX_DESKTOP_SESSIONS = 3
# 超限文案：desktop session limit exceeded ({active}/{limit})
```

超过 3 路并发流抛 `DesktopSessionLimitError`；同一用户的新流会取代旧流（F-465）。每个 `DesktopSession` 各持有一个 `ScreenCapture` 与 `InputInjector`（F-465）。

Linux 装配面（`setup.py` + 随包 systemd 脚本）：

| 项 | 值 | 信源 |
|---|---|---|
| 默认 VNC 端口 | 5900（仅监听 loopback：127.0.0.1/::1/[::1]） | F-467 |
| 虚拟显示 | display `:99` | F-468 |
| 默认分辨率 | 1920x1080，合法范围 640x480 ~ 7680x4320 | F-468 |
| Python 依赖 | mss>=9.0、pynput>=1.7、pillow>=10.0 | F-466 |
| systemd unit | `octop-desktop-xvnc`、`octop-desktop-session`、`octop-desktop-openbox`（3 个） | F-469 |
| EL 兼容 | almalinux/centos/ol/rhel/rocky 5 系，主版本 ≥10 判不支持 | F-466 |
| SetupState | `ready`/`needs_install`/`needs_start`/`unsupported`/`deps_missing`/`permission_denied`（6 值） | F-468 |

采集侧 `ScreenCapture` 默认 display `:0`，支持 mss 的 xgetimage/xlib/default 三种 backend；虚拟显示分支优先用 ImageMagick `import`（超时 4 秒），输出 `CaptureFrame(jpeg_b64, width, height)`，默认 JPEG quality=80（F-470）。输入侧 `InputInjector` 经 xdotool（超时 3 秒）注入，鼠标键映射 left=1/middle=2/right=3，键盘表把 Enter→Return、Control→ctrl、Meta→super 并覆盖 F1-F12（F-470）。安装流程含 6 次重试循环与 15 次收尾探测（F-469）。

## 主动关怀：情绪加权的 episode 挑选

主动关怀不发普通对话请求，而是由调度器驱动的一段程序化流程：从记忆 episode 中挑出「最值得关心」的事件，让 LLM 生成 ≤200 字的关怀文案，再经网关推送（F-497、F-498）。

挑选器 `EpisodePicker` 的评分公式（F-500）：

```
score = intensity × emotion_weight × recency_weight
```

10 种情绪的权重表（F-499）：

| 权重 | 情绪 |
|---:|---|
| 1.5（×4） | `sad`、`angry`、`anxious`、`frustrated` |
| 1.2（×2） | `tired`、`reflective` |
| 1.0（×4） | `happy`、`excited`、`grateful`、`neutral` |

时间新鲜度衰减：<1 天为 1.0，<3 天为 0.8，其余 0.6（F-500）。挑选参数默认 **top_k=3、窗口 7 天、回退窗口 30 天**；7 天内候选都已推送时自动扩到 30 天重挑；同一人多条记录去重时只保留最高分（F-498、F-500）。候选集来自 `list_episodes(limit=200)`，人格基调读 `SOUL.md`，LLM 调用超时 30 秒，默认时区 `Asia/Shanghai`，且只有推送成功后才写 `care_push_records`（F-497、F-498）。

调度器 `ProactiveCareScheduler` 的约束（F-501、F-502）：

- 最小睡眠粒度 `_MIN_SLEEP_SECONDS = 60`：再密的触发也不会短于 1 分钟轮询
- 触发间隔在分钟量级加随机抖动，越界偏移用 `random.randint(0, 120)` 分钟
- 时区解析失败回退 UTC；活跃时段判定与下次触发时间由 `is_in_active_hours`/`compute_next_trigger` 给出
- 会话挑选优先取 `channel_id` 非空者（能真实推送），否则取首个；每 Agent 的任务名形态为 `proactive_care_{agent_id}`
- 默认开启、除非用户显式退出，启动日志逐字为 `"ProactiveCareScheduler: agent=%s scheduled (default enabled unless opted out)"`

三者共同体现 Octop 的设备扩展哲学：能力先探测、装配声明式、运行时单例/限额，把高风险的外设在单进程模型下收敛为可审计的受控资源。

## 相关概念

- [/concepts/00-architecture.md](00-architecture.md)
- [/concepts/20-api-cli-surface.md](20-api-cli-surface.md)
- [/concepts/17-users-auth-security.md](17-users-auth-security.md)
