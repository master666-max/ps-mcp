# 研究底稿：Photoshop 脚本通道事实与来源（ps-mcp v0.1.0 建包日 2026-09-19）

来源分级：**[实测]** 本机真机验证（全部发生于 2026-09-19 当天，探针在
`agent-mcp-skill-PS/_probe/`）；**[网调]** 在线来源（二手，生态信息，摘要级可信度，
检索日期 2026-09-19）；**[推测]** 未经证据支撑的假设——本底稿不允许出现此级事实。
凡【✓实测】条目均可由 _probe/ 脚本复跑复现。

## 1. 本机环境（全 [实测]）

- **Adobe Photoshop 2026，v27.10.0**，build `27.10 (20260824.r.26 9d9635d)`，
  安装于 `C:\Program Files\Adobe\Adobe Photoshop 2026\`；界面语言 **zh_CN**（唯一语言包）
- COM 注册健康：ProgID `Photoshop.Application`（版本化 `Photoshop.Application.200`）；
  CLSID `{2682BB05-0A88-430F-8614-EE4E60E6D916}`，LocalServer32 =
  `…\Photoshop.exe /Automation`；TypeLib 在册
- 启动行为：`Start-Process` 后约 **12 秒**主窗口就绪（ splash → Home ）
- **COM 全生命周期可用**（连接 0.0s / DoJavaScript 往返 0.3s@689字符 / Quit 0.0s 进程正常退出），
  沙箱内外无差别（本 harness 的 Bash 沙箱不挡 COM 激活）
- **建档→编辑→导出→回读全链路通**：`documents.add`(120x80 RGB) → 加层 → 选区填色 →
  `saveAs`(PNG, asCopy) → `close(DONOTSAVECHANGES)`；中文+全角字符路径不碍事；
  导出 PNG 由 Read 工具实图回读成功（红色实图，与填充参数一致）
- **订阅激活态（运营级证据）**：无任何许可拦截，全部文档操作正常执行。PS 无"许可状态"
  脚本 API [推测→已核实不存在直接查询]；以运营级全链路成功为激活证据
- 磁盘：C: 剩 22GB / 930GB；D: 剩 56.5GB / 953GB
- UXP Developer Tool 未安装；`C:\Program Files\Common Files\Adobe\UXP\extensions\` 仅
  Adobe 自家 3 件（ccx.start / substance viewer / uam），无第三方
- CEP 运行时仍在（`Required/CEP/`），Presets/Scripts 下有全套官方 .jsx 脚本
- 注册表偏好键 `HKCU\Software\Adobe\Photoshop\200.0` 在册（本机此前跑过 PS）
- **包内脚本实作验证**（同日第二轮）：`scripts/ps_connect.ps1` 从零完整跑通
  Start-Process→就绪→模态发现→WM_CLOSE 自动处置→连接→探针（**F-2 预言当场证实**：
  暂存盘警告每次启动重现，自动处置有效）；`scripts/jsx/inventory_doc.jsx` 盘点全字段
  机读成功（含 `doc.resolution`、`historyStates.length`=4——两条由【△文献】升【✓实测】，
  已回写 02 册），zh_CN 默认背景层名「背景」原样进 report（用户图层名照收纪律实证），
  G0 预览导出→Read 实图回读与声明一致

## 2. 当日核心发现：模态弹窗是 COM 0x80080005 的已证成因（全 [实测]）

证据链（复跑脚本：`_probe/check_env.ps1` → `probe_com_retry.ps1` → `dismiss_modal*.ps1` →
`close_dialog.ps1`）：

1. PS 冷启动后 `New-Object -ComObject Photoshop.Application` 稳定失败
   `0x80080005 CO_E_SERVER_EXEC_FAILURE`，重试 8 次跨 3 分钟不变；
2. ROT 直连（`Marshal.GetActiveObject`）同样"服务器运行失败"——类厂激活被阻，非注册缺失；
3. CLSID/AppID 注册信息健康，排除注册损坏；客户端提权态=非提权，排除提权不对称；
4. 枚举 PS 顶层窗口发现**可见模态框「暂存盘空间不足」**（C: 剩 22GB 低于 PS 推荐值）；
5. 对该模态框 `PostMessage WM_CLOSE` → 弹窗消失 → COM **立即连上**（0.0s）。

结论：**启动期可见模态框会阻塞 COM 类厂激活**。规划书"脚本首行 displayDialogs=NO 防
模态卡死"只覆盖了**操作期**弹窗（脚本运行中的弹窗抑制），防不了**启动期**模态（出现在
任何脚本之前）——两者是不同层，连接 SOP 必须含"启动模态扫描"（见 01 分册 §2）。

勘误注（同日二次观测）：暂存盘警告**非 100% 每次启动重现**（当日三次冷启动 1 弹 2 不弹
——与启动时磁盘瞬时状态/时序有关，与 F-2 首记"预计每次重现"相比下修）；扫描 SOP 保持
不变（每次连接都扫，弹了就处置）。

附：该弹窗内容为 CEP/UXP 自绘容器（`DroverLord - Window Class`/`OS_ViewContainer`），
UIA 树下无按钮元素——**程序化关闭走 WM_CLOSE，按钮定位走截图+坐标**（UIA 对 PS 的
自绘对话框不可靠 [实测]）。另 [实测]：**启动期主窗口句柄会漂移**（MainWindowHandle
先指向 splash/过渡窗口，真正的 2026 主窗口在过渡期会被误判为"多余窗口"）——模态扫描
必须先等窗口稳定（连续两次轮询句柄一致）并**跳过与主窗口同标题的窗口**（同标题≠模态）；
ps_connect.ps1 已按此修复（0.3.0）。

## 3. COM DoJavaScript 机制事实（[实测] 除注明外）

- `app.DoJavaScript(js)` 返回最后表达式的值；JSX 对象用 `.toSource()` 序列化回传，
  PowerShell 侧直接收到字符串（`({a:"b",…})` 形态）
- 每字段独立 `try/catch` 的防御写法有效：缺属性返回 `"undefined"` 字符串而非炸探针
- `app.systemName` / `app.language` 在 27.10 的 COM DOM 中**不存在**（返回 undefined）——
  别信旧教程清单，字段先用 typeof 探
- 无文档时 `app.activeDocument` 抛"没有这种元素"（错误三形态·报错形态的样例）
- `displayDialogs = DialogModes.NO` 赋值生效（回读 `DialogModes.NO`）
- `doc.colorProfileName` 可机读（探针文档返回 `sRGB IEC61966-2.1`）——G0 色彩机验可行
- 大 JS 串长度上限【✗待实测】（今日最大 1835 字符，无碍）；`DoJavaScriptFile`【✗待实测】
- COM 冷启动（PS 未运行时 CoCreateInstance 直接拉起、无模态时）【✗待实测】——今日冷启动
  全部撞上暂存盘模态，SOP 按"Start-Process → 就绪等待 → 模态扫描 → 连接"设计（01 分册）

## 4. 生态现状（2026-09-19 网调 [网调]，摘要级可信度）

- **官方已入场但走云端**：Adobe "for Creativity" 官方 MCP 连接器（blog.adobe.com
  2026-04-28 发布）把 50+ 工具（Photoshop/Firefly/Express/Premiere 等）接进 Claude 等
  客户端——**基于 Adobe 云 API，不驱动本机桌面应用**；另 Creative Agent 已内置进
  PS 桌面版（对话式编辑 2026-03 起，2026-06-18 宣布扩展）。
  → 对"本机 PS 桌面自动化"而言官方仍无桌面直控方案，本 skill 与官方连接器**互补不冲突**：
  官方管线=云生成/AI 编辑，本 skill=本机安装版的脚本级细粒度控制（图层/选区/批量/落盘）。
- **社区本地方案两族**：
  - COM 族：`loonghao/photoshop-python-api`（Windows-only，COM 包装）及其
    `photoshop-python-api-mcp-server`——与本 skill 同通道，可作 API 速查参考；
  - UXP 族：`mikechambers/adb-mcp`（2025-06 起，PS/Premiere/InDesign）——UXP 面板即
    agent，WebSocket+MCP，需 UXP Developer Tool 手动 Load 插件。
- **UXP vs CEP**：UXP 是推荐新路线，CEP "保留一段时间后移除"（社区 2026-01 讨论指向
  2026 窗口；Premiere 已确认 CEP 终止时间表，PS 时间表未官宣）；ExtendScript 引擎
  向 UXP DOM/现代 JS 过渡。**新建扩展一律 UXP，不碰 CEP**（规划书判断维持）。
- ActionManager/batchPlay 社区参考（ActionDescriptor 机制文档）可用性【✗待复核】——
  机制层 02 册写 ActionManager 条目前先复核（社区绿化文档常年断链）。

## 5. 闸门清单（开工日状态）

| 闸门 | 状态 | 处置 |
|---|---|---|
| 订阅激活态 | **通过**（运营级证据，§1） | 无需降级 |
| 暂存盘空间 | **触发**：C: 22GB < 推荐值，每次启动弹警告模态 | 台账 F-2 待用户决策（清 C 盘 / 改暂存盘偏好到 D:) |
| IT 策略禁 COM | 未触发（COM 已实测可用） | 无 |
| PS 多实例 | 未实测（预期单实例；SOP 按单实例+队列预设） | 【✗待实测】 |
| UXP 文件系统权限模型 | 未进入（UXP 路线未启用） | 台账待办 |

## 6. 待实测清单（按优先级，前 15）

> 0.6.1 进度：#1 F 模式命令行链路 ✓实测（冷启动 16s 全链；菜单触发与"模态在场时
> F 模式行为"分别留用户路径与 F-15）；#4 暂存盘偏好已打通（见 §7）。

1. **JSX 文件总线 F 模式全链路**：`photoshop.exe script.jsx` 触发 + JSX 内 `File.write`
   落盘 report（F 兜底通道的成立性，台账 F-3）
2. COM 冷启动（无模态时）是否可行（决定 SOP 能否省 Start-Process 步，台账 F-4）
3. DoJavaScript 大串上限（二分测长度）+ `DoJavaScriptFile` 可用性（台账 F-5）
4. 暂存盘偏好改到 D: 的无 GUI 方法（注册表 `ScratchDisk` 键 or prefs 文件）——若可脚本化，
   F-2 可由 agent 代处置；否则人工 GUI（A7 分工）
5. `executeMenuCommand` 在 zh_CN UI 下用内部英文名（台账 F-6）
6. `suspendHistory` 打组行为 + 历史栈深度读取（report 字段候选）
7. ActionManager `batchPlay` 经 COM DoJavaScript 调用（如 `app.activeDocument` 之外的
   batchPlay 全局是否可用）——02 册 ActionManager 条目的地基
8. 智能对象缩放/栅格化的 report 可观测性（规划书风险 4 的机验字段）
9. 多实例行为（两个 photoshop.exe 手动拉起看是否合流）
10. 大 PSD（>1GB）单脚本小步纪律的实测工作量标定（20s 纪律按通道分写的 PS 版数值）
11. AI 生成/增强工具脚本可达性：executeMenuCommand/batchPlay 触发生成式填充/扩展/
    Harmonize/Generative Upscale（F-9，G 分支承接前置；积分成本确认纪律同批落地）
12. 文字图层与字体清单机读：textItem 字段（contents/font/size）逐项探（F-10，
    C 分支 G3 机验依赖）
13. 画板（artboard）API 可达性：artboards 集合/画板导航经 COM DOM（C/D 分支；
    后备=Artboards To Files 内置脚本路径）
14. 动作（.atn）与变量数据集经 COM 可达性（E 分支；无则 agent 自写循环替代）
15. UXP 链路实测（F-13 预留接口启用前置）：UXP Developer Tool 安装链路 / PS 开发者
    模式 / 面板 Load 与驻留方式 / UXP 文件系统权限模型 / batchPlay 经面板往返——
    仅在 D11 触发条件之一出现后才启动

## 7. 暂存盘偏好 AM 路径（0.6.1 实测，F-2 处置记录）

- 读取：`executeActionGet(ref)`，ref=property `scratchDiskPreferences` of class
  `application`；返回外层描述符键=属性名，`getObjectValue(getKey(0))` 进入内层；
  内层键 `scratchDisks` 为 **ActionList of STRING**（本地化卷名：系统盘="启动"）；
- 写入：`setd` 事件，null=同款引用，**新值键为 `charIDToTypeID("T   ")`（to）**——
  putObject 键用属性名会报"程序错误"（两轮失败后按 Listener 标准结构修正）；
  内层描述符 `scratchDisks` list：putString("D:\\") + putString("启动")；
- 验证：读回 ["D:\\","启动"] → Quit（偏好落盘）→ 冷启动读回持久 ✓、暂存盘警告消失 ✓；
- 配置现值：D:\ 主 + 启动 副（双暂存盘）；
- 途中坑：ExtendScript 为 ES3，**无 Array.prototype.forEach**（用 for 循环）；
  描述符 getter 需传数值 typeID（getKey(i) 原值），展示用 typeIDToStringID 转换。
