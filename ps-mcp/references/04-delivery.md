# 04 导出与交付（机制层）

## 1. 导出白名单（铁律 5 的操作面）

1. 任务开场声明 AGENT_ 输出目录（绝对路径，进 report）；
2. 每次导出前 `if (f.exists) → SKIP+report`，永不覆盖；
3. 版本化命名：`AGENT_<任务>_v<N>.<ext>`，v 递增；
4. 导出后立即核对：存在 + 大小>0 + 尺寸/模式读回核对。

## 2. 格式与选项【△文献：选项对象字段用前先探一条】

- PNG【✓实测链路】：`new PNGSaveOptions()` + `doc.saveAs(f, opt, true,
  Extension.LOWERCASE)`（asCopy=true 写副本不换当前文档关联）；
- JPEG【△文献】：`JPEGSaveOptions`（quality 0-12；embedColorProfile 项显式声明）；
- PSD 快照【△文献】：`PSDSaveOptions`（铁律 3 落盘快照用，asCopy=false 覆盖仅允许
  对 AGENT_ 自身版本文件）；
- TIFF/PDF【△文献】：选项对象字段未探，用前先探；
- **profile 转换显式声明进宣告行**：导出时是否 embed profile、是否转换到目标
  profile（如 sRGB for web）——转换是像素操作（02 分册 §5），先快照。

## 3. 回读核验（G4 交付门）

导出文件存在 + 大小>0 + 尺寸/模式核对（读回的数字与声明一致）+ **成图实看**：
Read 读 PNG 进上下文（首/中/区域裁剪——大图导低分辨率预览+关键区域裁剪两张）。
导出文件存在+尺寸核对+成图实看三样齐才算交付门通过；差任何一样标 △ 并说明原因。

## 4. 验收宣告行（交付消息模板）

> G0 盘点 ✓（N 文档/profile/图层数）｜G1 方向 ✓（对比图已过目）｜G3 技术一致 ✓
> （尺寸/模式/profile 逐项数字）｜G4 交付 ✓（文件/尺寸/实看）
> N/A 门注明理由；任何 △ 项列出待补动作。
