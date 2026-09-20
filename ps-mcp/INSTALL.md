# INSTALL — ps-mcp v0.7.1（Photoshop 桌面驱动 skill 安装与运行要求）

## 前置要求（本 skill 是知识包，不是安装包）

- **Adobe Photoshop**（Windows），已实测版本：Photoshop 2026 **27.10**（20260824.r.26），
  zh_CN UI。其他版本按【△文献】对待，首次使用先跑连接探针。
- **Windows PowerShell 5.1+**（系统自带）——S 模式 COM 客户端；无第三方依赖。
- 不需要 UXP Developer Tool / CEP / 任何插件（通道定案 docs/decisions D3/D6）。

## 模式与链路

| 模式 | 触发条件 | 链路 | 状态 |
|---|---|---|---|
| **S**（COM 直连） | PS 进程在且无启动模态阻塞 | `ps_connect.ps1` → `DoJavaScript(jsx)` → 返回串（toSource） | ✓实测 |
| **F**（文件总线兜底） | COM 连不上而 PS 进程在 | 任务 .jsx 落盘 → `Photoshop.exe <script.jsx>`（冷启动 ✓实测）→ report JSON 落盘 → agent 回读 | ✓实测（命令行链路；模态在场场景边界见 01 §5 / F-15） |
| **U**（UXP 预留） | 默认不启用；启用条件=01 分册 §6 三条触发之一，且须用户明示 | 契约已挂（"通道可换，协议不变"）：面板内 batchPlay → 同一 report 契约 | 预留（台账 F-13） |

## 首次自检（装机即跑）

```
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/ps_connect.ps1
```

预期输出协议：`OK-PROCESS` → `OK-NO-MODAL`（或 MODAL 行+自动处置）→ `OK-CONNECT` →
`RESULT: v=… docs=…`。任何 FAIL 行的 HINT 与处置见 references/01-connection-safety.md。

## 已知机器事实（2026-09-19 实测，换机复验）

- COM ProgID `Photoshop.Application`（版本化 `.200`）；PS 启动到主窗口就绪约 12 秒；
- 启动期可见模态框（如「暂存盘空间不足」）会以 0x80080005 阻断 COM——ps_connect.ps1
  已内置扫描+WM_CLOSE 处置；PS 自绘弹窗 UIA 无按钮元素，坐标点击/用户手点兜底；
- 无许可状态脚本 API——激活态以"建档→导出→回读探针通过"的运营级证据表述（D4）。

## 社区方案指路（评估于 2026-09-19，含本机实测；借鉴而非依赖，D6/D10）

**两族是什么**：社区让 MCP 客户端（Claude Desktop 等）驱动 PS 的两条路线——
- **COM 族**：走 Windows 系统级 COM 自动化接口（`Photoshop.Application`，与本 skill
  S 模式同通道），PS 内零插件安装。代表：`loonghao/photoshop-python-api`（Python
  COM 包装库）+ `photoshop-python-api-mcp-server`（其上的 MCP 服务器，`uvx` 即装即用）。
- **UXP 族**：走 Adobe 新插件体系，在 PS 进程内跑一个 UXP 面板、经 WebSocket 连外部
  MCP 服务器。代表：`mikechambers/adb-mcp`（PS/Premiere/InDesign）。安装链路重：
  Creative Cloud 装 UXP Developer Tool → 开启 PS 开发者模式 → Load 插件 → 面板在场
  才能连——换来进程内全权限（batchPlay 直通）。

**成熟度与本机证据**：
- COM 族底层库 `photoshop-python-api` 0.24.2 **本机实测通过**（PS 27.10：连接/版本/
  建档/关闭全链路 OK，探针 `_probe/probe_pypshop.py`；注意 Application 类在
  `photoshop.api.application` 命名空间，README 示例路径已过时）；其 MCP 服务器未经
  本机实测（需要 MCP 客户端环境）。
- UXP 族 adb-mcp（2025-06 起）活跃但安装链路重；官方 Express Developer MCP（2026-03）
  只覆盖 Express 不覆盖 PS。

**结论（D10）**：本 skill 自带同通道直连（PowerShell+COM，零依赖），社区 MCP 服务器
不引入包内；若你在 MCP 客户端（Claude Desktop 等）里想要现成工具集，轻量选
`uvx photoshop-python-api-mcp-server`（Windows+COM，与本 skill 同通道，可并存），
重装选 adb-mcp。本 skill 与它们不冲突：它们是"连接管道"，本 skill 是管道之上的
安全纪律/门/工艺层。

## 部署

v0.1.0 单包真源，无多根部署（③ 部署断言 N/A 留痕）。多宿主根需求出现时再建
deploy-roots.txt（母框架 §二.6 的全套断言已在 runner 内置，填根即生效）。
