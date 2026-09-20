# 指纹表（回归条款）— ps-mcp

纪律：锚**语义本体**不锚标签；指纹串为字面量子串、不含 markdown 标记；作用域=锚文件内唯一
（先 grep 验证再加条款）；每条新指纹必须跑 runner `--self-test`（单点删除探针，探针对象=被
保护的语义本体）；编号连续无缺无重。

| # | 指纹串 | 锚文件 | 保护语义 | 添加版本 |
|---|---|---|---|---|
| 1 | 源文件只读——不覆盖、不另存到原路径、不 flatten 用户文档、不删用户图层 | SKILL.md | 铁律1 源文件圣域 | 0.1.0 |
| 2 | 一切编辑在 AGENT_ 前缀副本文档上进行 | SKILL.md | 铁律2 隔离编辑 | 0.1.0 |
| 3 | suspendHistory 不能替代落盘快照 | SKILL.md | 铁律3 快照先行 | 0.1.0 |
| 4 | report JSON 是文档状态的唯一可信投影 | SKILL.md | 铁律4 状态投影 | 0.1.0 |
| 5 | 只写声明过的输出路径，导出前检查目标不存在 | SKILL.md | 铁律5 导出白名单 | 0.1.0 |
| 6 | 脚本首个状态调用必须是 displayDialogs = DialogModes.NO | SKILL.md | 铁律6 操作期弹窗抑制 | 0.1.0 |
| 7 | 进程在而连不上 → F 模式 | SKILL.md | 双模式判定核心 | 0.1.0 |
| 8 | 存在性≠看过 | SKILL.md | 实看义务 | 0.1.0 |
| 9 | 先问"有什么"再问"要什么" | references/00-task-intake.md | 两段式 intake | 0.1.0 |
| 10 | 启动期可见模态框会阻塞 COM 类厂激活 | references/01-connection-safety.md | 0x80080005 根因（当日实证） | 0.1.0 |
| 11 | 用户文档只以 SaveOptions.DONOTSAVECHANGES 关闭 | references/02-document-layers.md | 文档关闭纪律 | 0.1.0 |
| 12 | colorProfileName 机验 | references/02-document-layers.md | 色彩静默失败防线（G0） | 0.1.0 |
| 13 | 本册有意接近空白 | references/03-retouch-craft.md | 工艺层留白原则 | 0.1.0 |
| 14 | 三样齐才算交付门通过 | references/04-delivery.md | G4 成图回读判据 | 0.1.0 |
| 15 | 先判用途分支（含混合用途检测），再进两段式 | SKILL.md | 输入端路由第 0 步 | 0.2.0 |
| 16 | 画笔笔触与手绘属于人的领域，agent 不代画 | references/00-task-intake.md | F 分支代做边界 | 0.2.0 |
| 17 | 一律明示并指路，不静默承接 | references/00-task-intake.md | 不承接清单纪律 | 0.2.0 |
| 18 | 禁止把候选当清单项执行 | references/craft-library.md | 工艺库条目状态纪律 | 0.3.0 |
| 19 | 清单项必须实战出处 | references/craft-library.md | 工艺层反臆测纪律（0.5.0 放宽官方级候选态登记） | 0.3.0 |
| 20 | 通道可换，协议不变 | references/01-connection-safety.md | UXP 预留接口的核心契约 | 0.4.0 |
| 21 | UXP 通道默认不启用，启用须用户明示 | references/01-connection-safety.md | 通道切换权限边界 | 0.4.0 |
| 22 | top-k 与理由进开工消息 | references/00-task-intake.md | 重排步可审计留痕 | 0.5.0 |
| 23 | 开工消息列【主分支】+【次分支】 | references/00-task-intake.md | 混合用途检测声明义务 | 0.5.0 |
| 24 | 任务型首次出现时排一次，结果写回组合缓存 | references/00-task-intake.md | L2 组合缓存固化纪律 | 0.6.0 |
| 25 | 判定分辨率不足=没看 | SKILL.md | 铁律8 视觉实看贯穿全流程 | 0.7.0 |
| 26 | 修正指令必须引用所见 | references/02-document-layers.md | Px 修正的视觉证据义务（全景吸收） | 0.7.1 |
