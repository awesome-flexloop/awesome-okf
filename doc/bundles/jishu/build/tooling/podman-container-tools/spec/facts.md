---
type: spec
title: "Podman Container Tools 源码事实清单"
---

# Podman Container Tools 源码事实清单

> 本文件记录从源码中提取的可验证事实，零推断。每条事实标注源码路径。
> 生成时间：2026-08-26

---

## 一、项目概览（F-001 ~ F-008）

F-001：项目全称是 Podman (the POD MANager)，是一个用于管理OCI容器和Pods的工具。
源码路径：`podman/README.md:3`

F-002：Podman基于libpod库，该库提供容器、Pods、容器镜像和卷的管理API。
源码路径：`podman/README.md:17`

F-003：Podman无守护进程（daemonless）架构，不依赖manager daemon，提升安全性和空闲时资源利用率。
源码路径：`podman/README.md:40`

F-004：Podman在Linux上原生运行容器，在Mac和Windows上通过Podman管理的虚拟机运行。
源码路径：`podman/README.md:16`

F-005：项目Go模块路径为 `go.podman.io/podman/v6`，使用Go 1.25.9版本。
源码路径：`podman/go.mod:1,6`

F-006：项目采用Apache 2.0许可证。
源码路径：`podman/README.md:4`

F-007：Podman支持Docker兼容的CLI接口，可在本地和远程系统上运行容器。
源码路径：`podman/README.md:39`

F-008：Podman支持无root（rootless）运行容器，无需setuid二进制文件。
源码路径：`podman/README.md:77-78`

---

## 二、CLI入口与框架（F-009 ~ F-017）

F-009：CLI入口文件为 `cmd/podman/main.go`，包名为 `main`。
源码路径：`podman/cmd/podman/main.go:1`

F-010：CLI使用Cobra框架（`github.com/spf13/cobra`）。
源码路径：`podman/go.mod:61`

F-011：main()函数首先调用 `reexec.Init()` 处理子进程重新执行，然后设置日志，处理podmansh shell模式，解析命令，最后执行rootCmd。
源码路径：`podman/cmd/podman/main.go:49-77`

F-012：main.go通过空导入（`_ "go.podman.io/podman/v6/cmd/podman/..."`）注册各子命令包。
源码路径：`podman/cmd/podman/main.go:12-30`

F-013：rootCmd定义在 `cmd/podman/root.go`，Use为 `podman [options]`，Long描述为 "Manage pods, containers and images"。
源码路径：`podman/cmd/podman/root.go:82-96`

F-014：rootCmd设置了PersistentPreRunE和PersistentPostRunE钩子，Version字段绑定 `version.Version.String()`。
源码路径：`podman/cmd/podman/root.go:91-95`

F-015：init()函数中注册了多个初始化钩子：stdOutHook、loggingHook、syslogHook、earlyInitHook、configHook。
源码路径：`podman/cmd/podman/root.go:118-124`

F-016：Execute()函数执行命令后，会调用shutdown.Stop()并关闭ImageEngine和ContainerEngine。
源码路径：`podman/cmd/podman/root.go:138-169`

F-017：命令通过registry.Commands注册表管理，parseCommands()遍历该注册表添加命令，并根据EngineMode（ABIMode/TunnelMode）过滤本地/远程命令。
源码路径：`podman/cmd/podman/main.go:79-120`

---

## 三、cmd/podman/ 子命令（F-018 ~ F-030）

F-018：cmd/podman/ 下的子命令目录包括：artifact、common、completion、containers、diff、farm、generate、healthcheck、images、inspect、kube、machine、manifest、networks、parse、pods、quadlet、registry、secrets、system、utils、validate、volumes。
源码路径：`podman/cmd/podman/`（目录列表）

F-019：containers/ 子目录包含容器相关命令：attach、checkpoint、cleanup、clone、commit、container、cp、create、diff、exec、exists、export、init、inspect、kill、list、logs、mount、pause、port、prune、ps、rename、restart、restore、rm、run、runlabel、start、stats、stop、top、unmount、unpause、update、wait。
源码路径：`podman/cmd/podman/containers/`（目录列表）

F-020：images/ 子目录包含镜像相关命令：build、buildx、buildx_inspect、diff、exists、history、image、import、inspect、list、load、mount、prune、pull、push、rm、save、scp、search、sign、tag、tree、trust、trust_set、trust_show、unmount、untag、version。
源码路径：`podman/cmd/podman/images/`（目录列表）

F-021：pods/ 子目录包含Pod相关命令：clone、create、exists、inspect、kill、logs、pause、pod、prune、ps、restart、rm、start、stats、stop、top、unpause。
源码路径：`podman/cmd/podman/pods/`（目录列表）

F-022：networks/ 子目录包含网络相关命令：connect、create、disconnect、exists、inspect、list、network、prune、reload、rm、update。
源码路径：`podman/cmd/podman/networks/`（目录列表）

F-023：volumes/ 子目录包含卷相关命令：create、exists、export、import、inspect、list、mount、prune、reload、rename、rm、unmount、volume。
源码路径：`podman/cmd/podman/volumes/`（目录列表）

F-024：system/ 子目录包含系统相关命令：check、connection、context、df、dial_stdio、events、info、locks、migrate、prune、renumber、reset、service、system、unshare、version，还有connection/子目录。
源码路径：`podman/cmd/podman/system/`（目录列表）

F-025：machine/ 子目录包含虚拟机管理命令：cp、info、init、inspect、list、machine、os、reset、restart、rm、set、ssh、start、stop，还有os/子目录。
源码路径：`podman/cmd/podman/machine/`（目录列表）

F-026：kube/ 子目录包含Kubernetes相关命令：apply、down、generate、kube、play。
源码路径：`podman/cmd/podman/kube/`（目录列表）

F-027：manifest/ 子目录包含清单列表相关命令：add、annotate、create、exists、inspect、manifest、push、remove、rm。
源码路径：`podman/cmd/podman/manifest/`（目录列表）

F-028：secrets/ 子目录包含密钥相关命令：create、exists、inspect、list、rm、secret。
源码路径：`podman/cmd/podman/secrets/`（目录列表）

F-029：quadlet/ 子目录包含Quadlet systemd单元生成相关命令：install、list、print、quadlet、remove。
源码路径：`podman/cmd/podman/quadlet/`（目录列表）

F-030：根目录直接存在的命令文件（非子目录）：auto-update.go、client.go、compose.go、diff.go、inspect.go、login.go、logout.go、main.go、root.go。
源码路径：`podman/cmd/podman/`（根目录.go文件列表）

---

## 四、libpod/ 核心库结构（F-031 ~ F-045）

F-031：libpod/ 目录是核心容器生命周期管理库，文件仅在非remote构建且Linux/FreeBSD平台编译（build tag: `!remote && (linux || freebsd)`）。
源码路径：`podman/libpod/runtime.go:1`

F-032：libpod/define/ 子目录包含常量、类型定义：config.go、container.go、containerstate.go、diff.go、errors.go、healthchecks.go、info.go、mount.go、podstate.go、runtime.go、sdnotify.go、version.go、volume_inspect.go等。
源码路径：`podman/libpod/define/`（目录列表）

F-033：容器核心文件：container.go（Container结构定义）、container_api.go、container_commit.go、container_config.go、container_exec.go、container_internal.go、container_linux.go、container_log.go、container_inspect.go、healthcheck.go。
源码路径：`podman/libpod/`（容器相关文件列表）

F-034：Pod核心文件：pod.go（Pod结构定义）、pod_api.go、pod_internal.go、pod_status.go、pod_top_linux.go。
源码路径：`podman/libpod/`（Pod相关文件列表）

F-035：Runtime核心文件：runtime.go（Runtime结构定义）、runtime_ctr.go、runtime_img.go、runtime_pod.go、runtime_volume.go、runtime_linux.go、runtime_freebsd.go、runtime_worker.go、options.go。
源码路径：`podman/libpod/`（Runtime相关文件列表）

F-036：状态管理文件：state.go（State接口）、boltdb_state.go（BoltDB实现）、sqlite_state.go（SQLite实现）。
源码路径：`podman/libpod/`（状态相关文件列表）

F-037：卷核心文件：volume.go（Volume结构定义）、volume_inspect.go、volume_internal.go。
源码路径：`podman/libpod/`（卷相关文件列表）

F-038：OCI运行时相关文件：oci.go、oci_conmon.go、oci_conmon_linux.go、oci_util.go、oci_missing.go。
源码路径：`podman/libpod/`（OCI相关文件列表）

F-039：网络相关文件：networking_common.go、networking_linux.go、networking_freebsd.go、networking_pasta_linux.go、networking_rootlessport.go、networking_machine.go。
源码路径：`podman/libpod/`（网络相关文件列表）

F-040：事件系统文件：events.go，以及events/子目录：events.go、config.go、filters.go、logfile.go、journal_linux.go、nullout.go。
源码路径：`podman/libpod/events/`（目录列表）

F-041：锁机制文件：lock.go，lock/子目录包含file/和shm/两种锁实现。
源码路径：`podman/libpod/lock/`（目录列表）

F-042：存储相关文件：storage.go、storageService相关。
源码路径：`podman/libpod/storage.go`

F-043：日志相关文件：logs/log.go，logs/reversereader/子目录。
源码路径：`podman/libpod/logs/`（目录列表）

F-044：关闭处理文件：shutdown/handler.go。
源码路径：`podman/libpod/shutdown/handler.go`

F-045：名称生成器：namesgenerator/names-generator.go。
源码路径：`podman/libpod/namesgenerator/names-generator.go`

---

## 五、核心数据结构（F-046 ~ F-056）

F-046：Runtime是libpod核心运行时结构，定义在libpod/runtime.go:67-129，字段包括：config（*config.Config）、storageConfig（storage.StoreOptions）、state（State）、store（storage.Store）、storageService（*storageService）、imageContext（types.SystemContext）、defaultOCIRuntime（OCIRuntime）、ociRuntimes（map[string]OCIRuntime）、network（nettypes.ContainerNetwork）、conmonPath（string）、libimageRuntime（*libimage.Runtime）、lockManager（lock.Manager）、eventer（events.Eventer）、secretsManager（*secrets.SecretsManager）、workerChannel、workerGroup、valid等。
源码路径：`podman/libpod/runtime.go:67-129`

F-047：RuntimeOption是函数式选项类型，用于NewRuntime创建Runtime时修改配置，定义为 `type RuntimeOption func(*Runtime) error`。
源码路径：`podman/libpod/runtime.go:53-55`

F-048：NewRuntime函数创建新的容器运行时，接受context和可变数量的RuntimeOption参数，返回(*Runtime, error)。
源码路径：`podman/libpod/runtime.go:173-181`

F-049：Container结构表示单个OCI容器，定义在libpod/container.go:96-128，字段包括：config（*ContainerConfig）、state（*ContainerState）、batched（bool）、valid（bool）、lock（lock.Locker）、runtime（*Runtime）、ociRuntime（OCIRuntime）、reservedPorts、perNetworkOpts、restoreFromCheckpoint、pastaResult等。
源码路径：`podman/libpod/container.go:96-128`

F-050：Container操作访问状态前必须调用syncContainer()，该注释明确要求所有访问状态的Container操作以syncContainer()开头。
源码路径：`podman/libpod/container.go:87-95`

F-051：ContainerState结构包含容器当前状态，定义在libpod/container.go:132-150，字段包括：State（define.ContainerStatus）、ConfigPath、RunDir、Mounted、Mountpoint、StartedTime、FinishedTime、ExitCode等。
源码路径：`podman/libpod/container.go:132-150`

F-052：LinuxNS类型表示Linux命名空间，定义在libpod/container.go:46，枚举值包括：IPCNS、MountNS、NetNS、PIDNS、UserNS、UTSNS、CgroupNS。
源码路径：`podman/libpod/container.go:46-65`

F-053：Pod结构表示一组共同管理的容器，定义在libpod/pod.go:30-37，字段包括：config（*PodConfig）、state（*podState）、valid（bool）、runtime（*Runtime）、lock（lock.Locker）。
源码路径：`podman/libpod/pod.go:30-37`

F-054：Pod操作访问状态前必须调用updatePod()，该注释明确要求所有访问状态的Pod操作以updatePod()开头。
源码路径：`podman/libpod/pod.go:20-28`

F-055：PodConfig结构表示Pod的静态配置，定义在libpod/pod.go:40-98，字段包括：ID、Name、Namespace、Hostname、Labels、CgroupParent、UsePodCgroup、UsePodPID/IPC/Net/Mount/User/UTS/CgroupNS、HasInfra、ServiceContainerID、CreatedTime、CreateCommand、ExitPolicy、RestartPolicy、RestartRetries、LockID、ResourceLimits等。
源码路径：`podman/libpod/pod.go:40-98`

F-056：podState结构表示Pod的运行时状态，定义在libpod/pod.go:101-107，字段包括：CgroupPath、InfraContainerID。
源码路径：`podman/libpod/pod.go:101-107`

---

## 六、pkg/ 主要包目录（F-057 ~ F-068）

F-057：pkg/ 目录下的一级包目录包括：annotations、api、auth、autoupdate、bindings、channel、checkpoint、copy、criu、ctime、domain、emulation、env、errorhandling、farm、fileserver、inspect、k8s.io、logiface、lookup、machine、namespaces、parallel、pidhandle、ps、rctl、rootless、seccomp、selinux、signal、specgen、specgenutil、specgenutilexternal、syncmap、systemd、terminal、trust、util。
源码路径：`podman/pkg/`（目录列表）

F-058：pkg/api/ 包含REST API服务：handlers/（compat/ Docker兼容API、libpod/ Podman原生API、swagger/）、server/（HTTP服务器注册）、grpcpb/、bindings相关。
源码路径：`podman/pkg/api/`（目录列表）

F-059：pkg/bindings/ 包含HTTP客户端绑定（稳定API），子目录包括：artifacts、containers、generate、images、kube、manifests、network、pods、secrets、system、volumes、test。
源码路径：`podman/pkg/bindings/`（目录列表）

F-060：pkg/domain/ 是业务逻辑层，包含entities/（接口和数据结构）、infra/abi/（本地实现）、infra/tunnel/（远程实现）。
源码路径：`podman/AGENTS.md`（代码结构说明）

F-061：pkg/specgen/ 包含容器/Pod规范生成器，子目录generate/用于生成OCI规范。
源码路径：`podman/pkg/specgen/`（目录列表）

F-062：pkg/machine/ 包含虚拟机管理（用于Mac/Windows），子目录包括：apple/、define/、e2e/、env/、lock/、ocipull/、os/、ports/、qemu/、shim/、stdpull/、wsl/。
源码路径：`podman/pkg/machine/`（目录列表）

F-063：pkg/systemd/ 包含systemd集成，子目录包括：quadlet/、parser/、generate/、notifyproxy/、define/。
源码路径：`podman/pkg/systemd/`（目录列表）

F-064：pkg/rootless/ 包含无root运行支持。
源码路径：`podman/pkg/rootless/rootless.go`

F-065：pkg/auth/ 包含认证相关功能。
源码路径：`podman/pkg/auth/auth.go`

F-066：pkg/util/ 包含通用工具函数。
源码路径：`podman/pkg/util/utils.go`

F-067：pkg/k8s.io/ 包含vendored的Kubernetes API Machinery类型（intstr、uid、meta/v1、resource等）。
源码路径：`podman/pkg/k8s.io/`（目录列表）

F-068：pkg/domain/entities/engine.go定义了ContainerEngine和ImageEngine接口。
源码路径：`podman/cmd/podman/root.go:160-164`（引用registry.ContainerEngine()和ImageEngine()）

---

## 七、依赖与集成（F-069 ~ F-077）

F-069：核心依赖库包括：containers/buildah（镜像构建）、containers/image（镜像管理）、containers/storage（存储）、containers/common（共享工具）、containers/netavark（网络）、containers/gvisor-tap-vsock（VM网络）。
源码路径：`podman/go.mod:13,67-70`

F-070：CLI框架使用github.com/spf13/cobra v1.10.2和github.com/spf13/pflag v1.0.10。
源码路径：`podman/go.mod:61-62`

F-071：日志库使用github.com/sirupsen/logrus v1.10.1。
源码路径：`podman/go.mod:60`

F-072：HTTP路由使用github.com/gorilla/mux v1.8.1，schema解码使用github.com/gorilla/schema v1.4.1。
源码路径：`podman/go.mod:30-31`

F-073：状态存储支持BoltDB（go.etcd.io/bbolt v1.5.0）和SQLite（github.com/mattn/go-sqlite3 v1.14.50）。
源码路径：`podman/go.mod:40,66`

F-074：测试框架使用github.com/onsi/ginkgo/v2 v2.32.1和github.com/onsi/gomega v1.42.1，以及github.com/stretchr/testify v1.12.0。
源码路径：`podman/go.mod:49-50,63`

F-075：JSON库使用github.com/json-iterator/go v1.1.12（别名为json）。
源码路径：`podman/libpod/runtime.go:19,51`

F-076：默认OCI运行时设置为crun（当conf.Engine.OCIRuntime为空时）。
源码路径：`podman/libpod/runtime.go:186-188`

F-077：Conmon是用于监控OCI运行时的工具，conmonPath字段存储其路径。
源码路径：`podman/libpod/runtime.go:80`，`README.md:111`

---

## 八、其他关键事实（F-078 ~ F-086）

F-078：项目使用JSON-iterator配置为与标准库兼容（jsoniter.ConfigCompatibleWithStandardLibrary）。
源码路径：`podman/libpod/runtime.go:51`

F-079：SetXdgDirs()函数确保设置XDG_RUNTIME_DIR和XDG_CONFIG_HOME环境变量，供containers/image和containers.conf使用。
源码路径：`podman/libpod/runtime.go:131-171`

F-080：cmd/目录下除了podman/，还有其他入口：podman-testing/、quadlet/、rootlessport/、winpath/。
源码路径：`podman/cmd/`（目录列表）

F-081：rootless模式下使用用户命名空间，将容器内root映射到运行Podman的用户，容器权限不超过启动用户的权限。
源码路径：`podman/README.md:79-82`

F-082：项目每年发布4次主要/次要版本，在2月、5月、8月、11月的第二周发布。
源码路径：`podman/README.md:19`

F-083：Buildah专注于构建OCI镜像，Podman专注于维护和运行OCI镜像及容器，两者互补。
源码路径：`podman/README.md:158-194`

F-084：Podman提供REST API，包含Docker兼容接口和暴露Podman高级功能的改进接口。
源码路径：`podman/README.md:41`

F-085：libpod的valid字段表示运行时是否可用，从GetRuntime()返回时设为true，关闭后设为false。
源码路径：`podman/libpod/runtime.go:118-122`

F-086：Runtime包含workerChannel和workerGroup用于异步工作处理。
源码路径：`podman/libpod/runtime.go:91-92`

---

## 九、automation/ 子目录（F-100 ~ F-110）

F-100：目录用途：托管各类CI自动化脚本，供不同仓库使用
F-101：包含README.md说明文件
F-102：顶层文件：.gitignore、CODE-OF-CONDUCT.md、GOVERNANCE.md、LICENSE、LLM_POLICY.md、MAINTAINERS.md、create-tag.sh
F-103：子目录：.github/、container-images/、images/、mac_pw_pool/、renovate/、scripts/
F-104：.github/workflows/ 包含工作流文件：build_container_images.yml、build_images.yml、pr.yml、release.yml、validate.yml
F-105：.github/ 包含 renovate.json5 配置文件
F-106：container-images/ 子目录包含3个镜像构建目录：podman-machine-os-ci/、podman_cidev/、skopeo_cidev/，每个目录均含Containerfile和README.md
F-107：images/ 目录包含：build.sh、debian_packaging.sh、fedora.pgp、fedora_packaging.sh、get_fedora_url.sh、local-cache-registry
F-108：mac_pw_pool/ 目录包含Mac密码池相关脚本：AllocateTestDH.sh、Cron.sh、InstanceSSH.sh、LaunchInstances.sh、README.md、SetupInstances.sh、Utilization.gnuplot、cleanup_hook.sh、inscp.sh、nightly_maintenance.sh、pw_lib.sh、runner_api.sh、service_pool.sh、setup.sh、shutdown.sh，以及html/子目录
F-109：renovate/ 目录包含 defaults.json5 配置文件
F-110：scripts/ 目录包含 upload-to-oci-par.sh 脚本

---

## 十、community/ 子目录（F-200 ~ F-207）

F-200：目录用途：Podman Container Tools组织的中央社区仓库，托管项目治理、贡献指南和社区文档
F-201：包含README.md说明文件
F-202：顶层文件：CODE-OF-CONDUCT.md、CONTRIBUTING.md、CONTRIBUTING_GO.md、GOVERNANCE.md、LLM_POLICY.md、MAINTAINERS.md、SECURITY.md
F-203：子目录：.github/、minutes/
F-204：.github/ 包含 CODEOWNERS 文件
F-205：minutes/ 目录是会议记录归档，包含：README.md、20260424.md、20260626.md
F-206：关键文档包括：治理结构(GOVERNANCE.md)、行为准则(CODE-OF-CONDUCT.md)、安全政策(SECURITY.md)、贡献指南(CONTRIBUTING.md)、Go语言贡献指南(CONTRIBUTING_GO.md)、LLM政策(LLM_POLICY.md)
F-207：为以下项目提供共享文档：Podman、Buildah、Skopeo、Container Libraries

---

## 十一、image_build/ 子目录（F-300 ~ F-314）

F-300：目录用途：容器镜像和相关构建自动化的monorepo
F-301：包含README.md说明文件
F-302：顶层文件：CODE-OF-CONDUCT.md、GOVERNANCE.md、LICENSE、LLM_POLICY.md、MAINTAINERS.md、SECURITY.md
F-303：子目录：.github/、aio/、buildah/、ci/、podman/、skopeo/
F-304：.github/workflows/ 包含工作流文件：build.yml、build_aio.yml、cron.yml、pr.yml、zizmor.yml
F-305：.github/ 还包含 actionlint.yaml、filters.yaml、renovate.json5
F-306：aio/ 目录是"All In One"镜像（包含Podman、Buildah、Skopeo），包含：Containerfile、README.md、containers.conf、test.sh、user-containers.conf
F-307：buildah/ 目录包含Buildah镜像：Containerfile、README.md、containers.conf
F-308：podman/ 目录包含Podman镜像：Containerfile、README.md、containers.conf、podman-containers.conf
F-309：skopeo/ 目录包含Skopeo镜像：Containerfile、README.md
F-310：ci/ 目录包含构建自动化脚本：README.md、aio_build_push.sh、build-push.sh、containers_build_push.sh、lib.sh、setup_qemu.sh、shellcheck.sh、tag_version.sh、test.sh
F-311：镜像发布在quay.io的containers/和对应工具命名空间下，支持多架构（amd64、arm64、ppc64le、s390x）
F-312：镜像标签策略包括：stable版本标签、-immutable不可变标签、latest标签、testing标签、upstream标签、aio带日期戳标签
F-313：核心构建脚本是ci/build-push.sh，支持并行多架构构建，使用qemu-user-static
F-314：构建脚本添加built.by前缀的标签和注解用于审计（built.by.logs、built.by.commit、built.by.exec、built.by.digest）

---

## 十二、podman-machine-os/ 子目录（F-400 ~ F-415）

F-400：目录用途：构建podman machine的磁盘镜像
F-401：包含README.md说明文件
F-402：顶层文件：.gitignore、.gitmodules、.packit.yaml、CODE-OF-CONDUCT.md、GOVERNANCE.md、LICENSE、LLM_POLICY.md、MAINTAINERS.md、build.sh、gather.sh、podman-rpm-info-vars.sh、tmt-test.sh、util.sh
F-403：子目录：.fmf/、.github/、hack/、plans/、podman-image/、verify/
F-404：使用git submodules，克隆时需使用--recurse-submodules或执行git submodule update --init
F-405：构建入口脚本：./build.sh
F-406：构建要求：仅在Linux上以root运行，依赖curl、rootful podman、rpm-ostree、zstd、SELinux（可能需permissive模式）、osbuild及相关工具、jq、xfsprogs、e2fsprogs、koji（仅从PR构建podman时需要）
F-407：环境变量：OUTDIR（镜像输出目录，默认./outdir）、REPO（容器镜像仓库，默认quay.io/podman）
F-408：podman-rpm-info-vars.sh中设置的变量：PODMAN_VERSION（用于镜像标签，仅x.y版本）、PODMAN_PR_NUM（从PR添加podman版本，默认从rhcontainerbot/podman-next copr获取）
F-409：.fmf/ 包含version文件
F-410：.github/workflows/ 包含工作流：build.yml、pr.yml、release.yml、zizmor.yml；.github/还包含PULL_REQUEST_TEMPLATE.md、renovate.json5
F-411：hack/ci/ 包含CI辅助脚本：gha_mac_cleanup.sh、win-verify.ps1、windows_setup.ps1
F-412：plans/ 包含 main.fmf 测试计划文件
F-413：podman-image/ 目录包含镜像构建配置：00-podman-machine.preset、00-trigger-fixup-subuid-subgid.conf、10-autologin.conf、999-podman-machine-wsl.conf、Containerfile.COREOS、Containerfile.WSL、build_common.sh、fixup-subuid-subgid.service、notes.md、podman-iptables.conf、podman-user-wait-network-online-override.conf、qemu-guest-agent.service、qemu_guest_agent_vsock.te、rosetta-activation.service、rosetta-activation.sh
F-414：verify/ 目录是测试目录，包含Go测试代码（basic_test.go、config_darwin.go、config_linux.go、config_test.go、image_test.go、image_verify_test.go、run_test.sh、win_run_test.ps1）、go.mod、go.sum、README.md，以及vendor/目录（包含ginkgo、gomega等Go依赖）
F-415：测试要求：golang、ginkgo（需通过go install安装）
