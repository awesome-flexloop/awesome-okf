---
type: Concept
title: "Docker 环境：DinD 里跑 Android 模拟器的单容器全栈"
description: "DinD 镜像分层（Android SDK 34 + Pixel_8_API_34_x86_64 AVD + noVNC）、entrypoint 十步启动序列、start_emulator.sh、proxy_chain 旁路代理、iptables nft/legacy 探测与镜像版本史、AVD 快照定制八步、dev 模式"
tags: [MobileWorld, Docker, DinD, Android模拟器, AVD, 快照]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-29T14:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-29T14:00:00+08:00" }
status: stable
stale_after: 2026-12-31
sources:
  - id: mobile-world-facts
    resource: /references/facts.md
    title: MobileWorld 源码事实台账
  - id: mobile-world-sources
    resource: /references/source-registry.md
    title: MobileWorld 信源登记
---

# Docker 环境：DinD 里跑 Android 模拟器的单容器全栈

MobileWorld 把整套 Android 评测环境压缩进单个 Docker 镜像：DinD（Docker-in-Docker）基础镜像内启动 Android 模拟器（Pixel_8_API_34_x86_64 AVD）+ FastAPI 控制服务，ADB 经 socat 中继对外暴露，健康检查直通 `/health`。直觉上 Android 模拟器需要图形界面与宿主 KVM，实际方案是"容器套 Docker 再套模拟器"的三层虚拟化，VNC 仅是可选项。

## Dockerfile：镜像分层

`docker/Dockerfile`（F-067）：

- 基础镜像 `FROM cruizba/ubuntu-dind:latest`
- 安装 `openjdk-17-jdk`、`scrcpy`、`ffmpeg`、`xvfb`、`x11vnc`、`openbox`、`novnc`、`websockify`、`socat` 等
- Android SDK：`commandlinetools-linux-13114758_latest.zip` + `emulator-linux_x64-14214601.zip` + `sdkmanager "platform-tools" "build-tools;34.0.0" "platforms;android-34" "system-images;android-34;google_apis;x86_64"`
- `ENV AVD_NAME=Pixel_8_API_34_x86_64`，COPY `docker/${AVD_NAME}.avd`、`.ini`、`adbkey/adbkey.pub` 至 `/root/.android/`
- COPY `docker/mattermost-docker` → `/app/mattermost-docker-bk`、`docker/mastodon-docker` → `/app/mastodon-docker-bk`（chown 991:991）、`docker/images` → `/app/images`
- `uv sync` 安装 Python 依赖
- `HEALTHCHECK ... CMD curl -f http://localhost:6800/health || exit 1`
- `CMD tail -f /var/log/emulator.log /var/log/server.log /var/log/dockerd.err.log`

AVD 快照（含冻结日期的 `init_state`）随镜像分发，任务初始化统一加载它（F-060、F-061）。

## entrypoint.sh：十步启动序列

容器入口的固定顺序（F-068）：

| 步 | 动作 |
|---|---|
| ① | 代理规范化并强制 `no_proxy="10.0.2.2,127.0.0.1,localhost,::1[,用户值]"` |
| ② | `sysctl net.ipv6.conf.all.disable_ipv6=1`（注释引用 Google issue 215231636，**禁 IPv6 以保 SIM 卡可用**） |
| ③ | iptables 后端自动探测（先 `iptables-nft -L -n` 成功则设 nft，否则 legacy） |
| ④ | `start-docker.sh` 后 30 秒内轮询 `docker info`，超时打印 `dockerd.err.log` 末 20 行并 exit 1 |
| ⑤ | `cd /app/images && for f in *.tar; do docker load -i "$f"; done`（加载应用镜像） |
| ⑥ | `ENABLE_VNC=true/1` 时启动 `start_novnc.sh` + `uv sync --extra dev --no-cache`，否则 `uv run mobile-world viewer --port 7860 &` |
| ⑦ | `/app/docker/start_emulator.sh`（启动模拟器） |
| ⑧ | `socat TCP-LISTEN:5556,fork,reuseaddr,bind=0.0.0.0 TCP:127.0.0.1:5555 &`（ADB 中继） |
| ⑨ | `uv run mobile-world server --port 6800 >> /var/log/server.log 2>&1 &`（控制服务） |
| ⑩ | `exec "$@"` |

部署失败排查的两个高频点：第②步（禁用 IPv6 否则 SIM 卡不可用）与第③④步（内核 6.x+ 缺 iptable_nat 导致 dockerd 静默失败，v1.2 起默认 iptables-nft 并自动回退 legacy + `docker info` 30 秒验证，F-071）。

## start_emulator.sh

模拟器启动脚本（F-069）：

- 先 kill 现有 emulator（`adb devices | grep emulator | cut -f1 | xargs -I {} adb -s "{}" emu kill`）
- 选项 `options="-no-audio -no-snapshot -gpu swiftshader_indirect"`（软件渲染，不依赖宿主 GPU）；`ENABLE_VNC` 开启时有窗口（`DISPLAY=:0`），否则 `-no-window`
- 启动日志写 `/var/log/emulator.log`
- `check_emulator_status` 轮询 `adb shell getprop sys.boot_completed`，超时 `${EMULATOR_TIMEOUT:-600}` 秒，成功后 `adb shell input keyevent 82`
- `disable_animation` 置三个 animation scale 为 0.0（动画禁用，利于确定性）
- 配置 HTTP 代理时启动 `proxy_chain.py`（`LOCAL_PROXY_PORT` 默认 38888）并 `adb shell settings put global http_proxy "10.0.2.2:${LOCAL_PROXY_PORT}"`
- 最后 `adb root`

## proxy_chain.py：旁路代理

代理拓扑（F-070）：`emulator app → proxy_chain.py(listens 0.0.0.0:LOCAL_PORT) → {10.0.2.x/127.*/localhost 直连 | 其余转发 UPSTREAM_PROXY}`。

- `is_bypass(host)` 精确匹配 `localhost/127.0.0.1/::1` 与前缀 `10.0.2.`、`127.`
- `rewrite_bypass_host(host)` 将 `10.0.2.*` 重写为 `127.0.0.1`（10.0.2.2 仅为 guest 侧 slirp 网关别名）
- 环境变量 `UPSTREAM_PROXY`（必需）与 `LOCAL_PORT`（默认 38888）；日志写 `/var/log/proxy_chain.log`

这落实了 `--http-proxy` 的承诺："10.0.2.2/127.0.0.1/localhost are always excluded"（F-024）。

## 镜像版本史

docs/docker_changelog.md 记录（F-071）：

| 版本 | 日期 | 变更 |
|---|---|---|
| v1.0 | 2025-12-24 | 初版：cruizba/ubuntu-dind + Android SDK 34 + Pixel_8_API_34_x86_64 AVD + emulator build 14214601 + DinD + noVNC |
| v1.1 | — | 加 socat 做 ADB 中继 0.0.0.0:5556→127.0.0.1:5555；CMD 增加 tail dockerd.err.log |
| v1.2 | 2026-04-12 | 修 kernel 6.x+ 缺 iptable_nat 导致的 dockerd 静默失败——默认 iptables-nft 并自动回退 legacy；entrypoint 用 `docker info` 30 秒验证 dockerd 可用；`mw env check` 新增 iptables NAT 检查 |

## AVD 快照定制八步

docs/configure_avd.md 的流程（F-073）——也是确定性复现三件套中"快照"的维护入口（另见 `/examples/02-customize-avd-snapshot.md` 的逐步解读）：

```bash
# 1. 启动 dev 容器
sudo mobile-world env run --image mobile_world:v1.1 --dev
# 2. 进入容器
mobile-world env exec mobile_world_env_0_dev
# 3. 加载初始快照
adb emu avd snapshot load init_state
# 4. 通过 VNC 页面手动配置
# 5. 定冻结日期（2025-10-16 12:00:00）
adb shell su root date 101612002025.00
# 6. 保存快照并关闭模拟器
adb emu avd snapshot save init_state && adb emu kill
# 7. 拷回宿主
docker cp mobile_world_env_0_dev:/root/.android/avd/Pixel_8_API_34_x86_64.avd docker/
# 8. 重建镜像
docker buildx build -t mobile_world:v1.2 -f docker/Dockerfile .
```

## dev 模式

`mobile-world env run --dev` 挂载本地 `src/` 至 `/app/service/src` 并自动启用 VNC，仅支持单容器；`mobile-world env restart <container_name>` 重启容器内服务（服务由 `uv run mobile-world server` 启动）；容器内日志 `tail -f /app/service/logs/server.log`，测试 `cd /app/service && uv run pytest`（F-077、F-024）。

## 相关概念

- [/concepts/01-quickstart-installation.md](/concepts/01-quickstart-installation.md)——宿主侧启动命令与 WSL/KVM 前置
- [/concepts/04-tasks-registry.md](/concepts/04-tasks-registry.md)——init_state 快照与冻结时钟如何被任务初始化消费
- [/examples/02-customize-avd-snapshot.md](/examples/02-customize-avd-snapshot.md)——八步流程的逐步实操解读
