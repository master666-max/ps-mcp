# 02 文档与图层（机制层）

标注体系同 SKILL.md。【✓实测】=2026-09-19 本机探针验证；【△文献】=ExtendScript DOM
通用文档知识（社区文档/同族经验），未在本机逐项复验——**用前先探一条**。

## 1. 文档对象（Document）

- 已验证字段【✓实测】：`name` / `width.as("px")` / `height.as("px")` / `mode`
  (DocumentMode.RGB) / `colorProfileName`（"sRGB IEC61966-2.1"）/ `artLayers.add()`；
- 新建【✓实测】：`app.documents.add(UnitValue(w,"px"), UnitValue(h,"px"), 72,
  "AGENT_名", NewDocumentMode.RGB, DocumentFill.WHITE)`；
- 打开【△文献】：`app.open(File(path))`；副本【△文献】：`doc.duplicate()`——副本纪律
  见 §2；
- 关闭【✓实测】：`doc.close(SaveOptions.DONOTSAVECHANGES)`；用户文档只以 SaveOptions.DONOTSAVECHANGES 关闭（AGENT_ 副本按需 SAVECHANGES+saveAs）；
- 无文档时 `app.activeDocument` 抛"没有这种元素"【✓实测】——先判
  `app.documents.length`；
- 分辨率【✓实测】：`doc.resolution`；历史栈【✓实测】：`doc.historyStates.length`
  （可机读，探针文档=4；关文档清零，铁律 3 的依据）。

## 2. AGENT_ 副本与快照（铁律 2/3 的操作面）

1. 打开源文件后立即 `var agent = doc.duplicate(); agent.name = "AGENT_<任务>_v1";`
   【△文献】——duplicate 不落盘，落盘快照另做；
2. 快照：`agent.saveAs(File(OUTDIR + "/AGENT_<任务>_v1.psd"), new PSDSaveOptions(),
   false, Extension.LOWERCASE)`【△文献】——版本号递增不覆盖（铁律 5）；
   `suspendHistory(agent, "<任务>")` 可把中间步骤打组成一个历史条目【△文献】，但
   suspendHistory 不能替代落盘快照（SKILL 铁律 3）；
3. 每个破坏性操作（合并/栅格化/删层/滤镜）之前：先快照，再操作，返回值进 report。

## 3. 图层（ArtLayer / LayerSet）

- 已验证【✓实测】：`artLayers.add()` → `name` 赋值 → `kind`（LayerKind.NORMAL）；
- 遍历【△文献】：`doc.layers`（LayerSet 与 ArtLayer 混合集合）；组=`LayerSet`，
  判断 `obj.typename`（"ArtLayer"/"LayerSet"）递归；可见性 `visible`、锁 `allLocked`
  【△文献】；
- **用户图层名照收不猜**：中文名原样进 report，不改名不猜语义；
- 智能对象【△文献】：`layer.kind == LayerKind.SMARTOBJECT`；缩放/替换/栅格化属破坏性
  操作（静默损质家族）——参数进 report，操作前快照；
- 大文档图层树按组分页进 report（上下文经济：先报 top-level 计数与组名，用户/agent
  要哪组再展开哪组）。

## 4. 选区与填充（已验证的操作基元）【✓实测】

```jsx
var c = new SolidColor(); c.rgb.red = 200; c.rgb.green = 40; c.rgb.blue = 40;
doc.selection.selectAll(); doc.selection.fill(c); doc.selection.deselect();
```
- 选区 API【△文献】：`select(RectBounds)/selectBounds/feather/grow/similar/deselect`；
  bounds 数组顺序 [left, top, right, bottom]（单位随 doc.rulerUnits【△文献】）；
- 调整层/非破坏调整【△文献】：调整层属于"无损结构"步骤（管线第三阶段），具体 API
  用前先探一条。

## 5. 色彩机制（静默失败家族主战场）

- colorProfileName 机验【✓实测】——G0 必进 report；assigned vs converted：
  `doc.assignProfile(name)` vs `doc.convertProfile(name, intent)`【△文献】——转换是
  破坏性像素操作，先快照；
- **profile 不匹配不报错只偏色**【△文献】：任何跨文档操作（拖拽/置入/复制粘贴）前
  先对齐两侧 report 的 profile 并显式声明转换决策；
- 模式转换（RGB↔CMYK↔灰度）【△文献】：`doc.changeMode()` 破坏性，先快照+用户确认。

## 6. 修图结构工艺（待实战回填的槽位）

> 本节只放"结构顺序的 API 可达性速记"，工艺判据（哪脏先修/瑕疵判据/融合顺序）
> **一条不预写**——等 ≥2 次实战回填（母框架 1c）。目前已知：无损结构步骤
> （副本/智能对象/调整层/蒙版）先于像素破坏步骤；每步可导出实看（SKILL §4）。
> 实战记录入 docs/ 与台账，≥2 次后升级为清单项并删除本提示。

## 7. 操作后实看循环（Px 过程检查点——实时检查与修正）

每个**写操作**（修整/填充/滤镜/变换/合并）完成后立即执行，不等任务收尾：

1. **导出**：操作区 1:1 小瓦片（≤512px 边长），与操作前同区并排（一张图两半）；
2. **实看**：Read 瓦片进上下文，按该操作关联的工艺库条目"核（视觉核验点）"判：
   通过 / 异常（异常要说出**看见什么**：亮度阶梯/纹理错位/颜色断层/边缘发糊）；
3. **修正**：异常→调参或换法重跑**该操作**（副本上，快照纪律不变）；
   **修正指令必须引用所见**——不许写"重跑一下"，必须写"v1485 段 -4px 处有 α≈0.04 的暗带，故二次
   校正该列"（所见=瓦片里可指认的视觉证据）；同一操作 ≥2 次修正仍异常 → 停手，
   带着瓦片升 G1 交用户裁决；
4. **留痕**：瓦片文件名+判定结论进 report 实看清单（存在性与文件系统互证）。

成本纪律：每操作一轮瓦片；全长度核验（沿处理线全长分块）只在 G3 成品检验做一次；
禁止用降采样视图做质量宣告（SKILL 铁律 8）。
