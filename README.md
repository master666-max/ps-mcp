# ps-mcp — Photoshop 桌面驱动 Skill（COM 直连 + 文件总线兜底）

> 通过 COM（`Photoshop.Application` + `DoJavaScript`）驱动真实运行的 Adobe Photoshop：
> 文档盘点、AGENT_ 副本隔离编辑、导出与成图实看核验。**这不是一个 MCP 服务器**——
> 是一套"驱动知识包"：连接 SOP、安全铁律、阶段门、可生长的工艺库，以及全部实测
> 过的探针脚本。零第三方依赖（PowerShell + Python stdlib）。

## 它解决什么问题

让编码 agent（Claude/ZCode 等）安全地操作本机 Photoshop，重点不在"能调 API"，
而在三件更难的事：

1. **不弄坏用户的东西**——源文件只读、AGENT_ 前缀副本隔离、破坏性操作前落盘快照、
   导出白名单（七条铁律，每条都有实测出处）；
2. **不轻信连接**——启动期模态弹窗会以 0x80080005 阻断 COM（实测根因），连接自检
   内置模态扫描与三档处置（WM_CLOSE → 截图坐标 → 用户手点）；
3. **不凭想象宣告质量**——视觉实看贯穿全流程（"判定分辨率不足=没看"），处理区
   1:1 分块瓦片实看 + 独立数字机查互证，宣告行附实看清单。

## 架构一览

```
ps-mcp/
├── SKILL.md              入口层：模式判定/七铁律/双通道门/路由/恢复 SOP
├── INSTALL.md            安装与运行要求（含社区方案评估）
├── CHANGELOG.md          逐版变更（0.1.0 → 0.7.1）
├── references/
│   ├── 00-task-intake.md      输入端路由（8 用途分支+混合检测）+ 两段式 intake
│   ├── 01-connection-safety.md 连接/模态处置/错误三形态/F 模式/UXP 预留接口
│   ├── 02-document-layers.md   文档/图层/色彩机制 + Px 操作后实看循环
│   ├── 03-retouch-craft.md     工艺层（有意留白，等实战回填）
│   ├── 04-delivery.md          导出白名单/回读核验
│   └── craft-library.md        工艺库：清单项层+候选层（P1/P2 分级）+任务型组合缓存
├── scripts/
│   ├── ps_connect.ps1         连接自检（启动/模态扫描/处置/COM 探针）
│   ├── rerank_local.py        本地 LM Studio 重排器集成（可选依赖）
│   └── jsx/                   G0 盘点脚本 + 五段式任务模板
├── evals/                      治理层：25+ 指纹回归 / 四查 runner / 台账 / --self-test
└── docs/                       研究底稿 / 决策日志 D1-D13 / 工艺调研 / worked example
```

## 快速开始

```powershell
# 1. 连接自检（会自动启动 PS、扫描并处置启动期模态弹窗）
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/ps_connect.ps1
# 预期：OK-PROCESS → OK-NO-MODAL → OK-CONNECT → RESULT: v=27.x docs=N
```

把 `SKILL.md` 装入你的 agent 工作流（或直接按它操作）。G0 盘点用
`scripts/jsx/inventory_doc.jsx`，新任务从 `scripts/jsx/task_template.jsx` 骨架起步。

## 实测环境

- Adobe Photoshop 2026 **27.10**（20260824.r.26）+ Windows 中文 UI
- 其他版本按【△文献】对待——包内全部事实带三态标注
  （【✓实测】/【△文献】/【✗待实测】），首次实测后回写

## 隐私声明

- 本仓库不含任何用户路径、用户文件名、机器名；worked example 已脱敏（占位符）
- 实测数据（版本号/时长/注册表结构）为机器事实，不含个人身份信息

## 治理（为什么这个包值得信）

- **25+ 指纹回归**：关键条款各有一个字面语义串锚，`--self-test` 对被保护语义做
  单点删除探针（检出率必须 100%）；
- **发布前四查**：①指纹全量 ②版本三处同步 ③部署哈希（N/A 留痕）④台账核对
  （④a CHANGELOG 引用的 F-NN 必须已登记 / ④b 编号单调+版本一致）；
- **台账 append-only**：全部缺陷 F-1~F-17 可追溯，含已修复的台账编辑事故本身；
- **决策日志 D1-D13**：每条与规划书/母框架的偏离都有"原样→实际→为什么"。

## 同族

- `blender-mcp`（建模域，50 轮治理史的参考实现）
- `agent-mcp-skill-达芬奇`（剪辑域，同族第二例）

## License

MIT
