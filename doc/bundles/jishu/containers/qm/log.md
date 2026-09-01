# QM Bundle 更新日志

## 2026-08-26 - 初始版本

### 新增

- 初始化 QM OKF Wiki Bundle 结构
- **references/** 信源登记：
  - `readme-source.md` - README.md 和 qm.8.md man 手册信源
  - `qmctl-source.md` - qmctl 工具源码信源
  - `subsystem-source.md` - KVM/Wayland/ROS2 等子系统信源
  - `index.md` - 信源索引
- **concepts/** 概念文档（5个）：
  - `00-introduction.md` - QM 定位与 ASIL 汽车功能安全场景
  - `01-nested-architecture.md` - 嵌套隔离架构（四层架构详解）
  - `02-oom-selinux.md` - 三级 OOM 策略与 SELinux 隔离
  - `03-subsystems.md` - 子系统扩展（kvm/wayland/ros2 等）
  - `04-bluechi.md` - BlueChi 多节点管理
  - `index.md` - 概念索引与学习路径
- **examples/** 示例文档（2个）：
  - `01-vm-setup.md` - 创建 QM 虚拟机环境（QEMU/KVM + AutoSD）
  - `02-kvm-subsystem.md` - KVM 子系统使用（嵌套虚拟化）
  - `index.md` - 示例索引
- **根文件**：
  - `index.md` - Bundle 主页（含快速开始、文档导航、项目结构）
  - `log.md` - 本更新日志

### 基于源码版本

- 源码路径：`d:\spaces\SpecWeave\external\dao\action\Containers\qm`
- 事实文件：`d:\spaces\SpecWeave\.trae\specs\containers-okf-wiki\facts-qm.md`（F-001 到 F-015）
- 核心信源：README.md, qm.8.md, tools/qmctl/, subsystems/, oci-hooks/
