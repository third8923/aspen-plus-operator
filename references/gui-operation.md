# GUI 启动纪律、排错、提速与验证

本文是 Aspen GUI 路径的唯一权威操作规范。**执行任何 GUI 操作前必须完整读一遍。**

## 0-WB WorkBuddy 环境适配（在本环境优先看这条）

本文正文里的「豆包虚拟桌面 / computer_use `list_apps`+`launch_app`」是**另一套 agent 环境**的通道名。
在 **WorkBuddy** 下对应做法：

| 本文写法 | WorkBuddy 对应 |
|-|-|
| computer_use `list_apps` / `launch_app` / 截图 | 加载 **`workbuddy-computer-use`** skill（控制 Windows 桌面应用：点击、输入、截图） |
| 豆包虚拟桌面（用户可见会话） | WorkBuddy 的桌面控制通道；**仍需先确认目标窗口在用户可见的会话里** |

不变的原则（两个环境都成立）：

1. **COM 优先**：批量跑工况、取数、参数寻优一律走 Python win32com，不开 GUI。
2. **GUI 只用于**：看引擎报错原文、单点演示/教学、确认界面状态。
3. **报错文本其实可以不开 GUI**：`doc.Export(2, "<路径>.rep")`（`HAPEXP_REPORT=2`）直接导出报告，
   `doc.Export(6, "...")`（`HAPEXP_RUNMSG=6`）导出运行消息——**优先用这个，别为一个弹窗去开 GUI**。
4. GUI 与 COM 是两个独立会话，**交换介质只有同一个 bkp 文件**（GUI 保存 → COM 重开重跑）。

## 0. 通道分界（先于一切）

| 操作 | 启动位置 | 通道 | 用户是否可见 |
|-|-|-|-|
| **GUI 操作**（开界面、看报错、点参数、演示） | **豆包虚拟桌面**（用户可见会话） | computer_use `list_apps` + `launch_app` | 必须可见 |
| **COM 操作**（批量跑工况、取数、参数寻优） | 本机引擎（后台，无窗口） | Python win32com 直连 | 无需可见 |

- GUI 与 COM 是两个独立会话，互不感知；交换介质只有「同一个 bkp 文件」。
- 需要 GUI 时只开 GUI，需要 COM 时只跑 COM；不要为排错在 GUI 里反复点参数（COM 更快），也不要为了"看到"而把 COM 模型塞进 GUI。

## 1. 启动纪律（最高优先级）

- **禁止用 Bash 直接启动本地 GUI 软件（Aspen Plus / HYSYS / EDR 等）。**
- **禁止把 GUI 启动在本机真实桌面**——本机真实桌面与豆包虚拟桌面不是同一显示会话，用户在虚拟桌面看不到窗口，等同白启动，还会占住引擎/许可。
- 必须用 computer_use 的 `list_apps` + `launch_app`（桌面控制通道）启动，**目标必须是豆包虚拟桌面**，并用截图确认窗口真的出现在虚拟桌面上。

### 启动成功判定（硬标准）

`launch_app` 返回 `ready` 或 `accepted_unverified` 都不算数，**唯一成功标准 = 截图里能在豆包虚拟桌面看到目标应用窗口**（欢迎页/主窗口都算）。判定流程：

1. `list_apps()` 过滤出目标应用（名字精确匹配）；
2. `launch_app(精确名)`；
3. 等待后 `cu.screenshot()` 确认窗口可见；
4. **看不到窗口 → 立即判定 GUI 路径失败**：不要傻等、不要反复重试启动、不要"一通排错"改参数；停手，改用 COM 完成排错（COM 读诊断/状态/错误信息），或报告需要人工确认显示会话。

### 为什么（历史排错教训）

曾多次把 Aspen GUI 启动在本机真实桌面：豆包虚拟桌面截图什么都看不到，然后 agent 原地傻等或盲目重试/改参数，浪费大量轮次。根因：

- 豆包 agent 的「虚拟桌面」是独立显示会话，与本地 Windows 桌面不是同一套显示环境；
- 启动在本机/不可见会话里的 GUI 进程，agent 的截图通道与用户都看不到它的窗口；
- 软件其实可能启动了，但不可见，于是误判为失败，陷入无效排错循环。

**正确的诊断顺序**：先确认走 `list_apps` + `launch_app`；再确认窗口出现在虚拟桌面截图；若不可见，直接回退 COM，不要盲改参数。

## 2. GUI 排错

GUI 是「看报错、读提示」的第一现场，排错顺序：

1. **COM 报错时先看 GUI 提示**：例如「所需输入不完整（Required input incomplete）」，不要瞎试参数。打开模型后在 GUI 里看 **Input Summary / Diagnostics / 报错对话框**——它直接指明缺哪个对象（如某流股无进料、某块缺参数）。
2. **模型结构问题看 bkp 文本**：如「ZERO FEED TO THE BLOCK」→ FEED 段缺 `STREAM MATERIAL` 前缀（见 bkp-diagnostics.md）。
3. **引擎「空转」**（状态 Ready 但不出数）→ 运行协议漏了 Reinit，GUI 里先 Reset 再 Run。
4. **弹窗挂起**：COM 必须 `doc.SuppressDialogs = True`，否则引擎报错弹窗会在不可见会话里挂起，COM 调用永久等待。

## 3. GUI 提速

GUI 慢，但要提速也有办法（已确认可行方向）：

- **定制虚拟桌面**：去掉无关桌面图标与壁纸背景、降低分辨率，减少重绘负载，提高操作频率。
- **缩小 GUI 操作面**：单点操作（改一个参数、看一个报告）比全流程点击快；批量工作仍走 COM。
- **快捷键与命令框**：Aspen Plus 支持命令输入（Command line / Run 快捷键），减少菜单点击。
- **用 bkp 文本预检**：开 GUI 前先用文本层确认模型结构与参数位置，进去只做目标操作。

## 4. GUI 验证（结果必须验证）

| 验证对象 | 方法 |
|-|-|
| 界面/弹窗/报错对话框 | 虚拟桌面截图确认（launch_app 后立即截图，操作后重新截图） |
| 运行是否收敛 | GUI 控制面板状态（Converged / Results Available），不是「Ready」 |
| 模型结果一致性 | GUI 的 Results / Stream Results 与 COM 取数交叉核对（同一 bkp，同一工况） |
| 修改生效 | 改参后必须 Reset/Reinit + Run，再读输出；只看 Input 不算生效 |

## 5. 常见坑速查

- 截图看不到界面 → 判定 GUI 路径失败（会话错位），立即回退 COM 完成排错；不要用 Bash 重试启动，不要反复 launch_app。
- 引擎报错但不弹窗 → SuppressDialogs 未开时 COM 挂起；开了之后报错会以异常/状态返回。
- GUI 改了参数没反映到 COM 取数 → GUI 与 COM 是两个会话，互不感知；以「同一个 bkp 文件」为交换介质：GUI 保存 → COM 打开重跑。
