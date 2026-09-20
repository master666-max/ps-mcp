# 工艺调研底稿 · A 照片修图（craft-research/A）— 检索 2026-09-19

格式：`CR-A-NN ｜ 论断 ｜ 类型 ｜ 来源 ｜ 可信度`。全部为**候选材料**（非清单项）。

- **CR-A-01 ｜ 宏观顺序共识：cull（选片）→ 全局调整（裁剪/镜头/曝光/白平衡）→ 局部调整 → 清理修复 → 输出锐化/导出** ｜ 顺序 ｜ Imagen AI/alanranger/DigitalPhotoMentor/LibreTexts 多源 ｜ [社区多源一致]
- **CR-A-02 ｜ cull 先行：不修落选片，选片是最大时间杠杆；"倒序选片"（先看最好的）可省一半时间** ｜ 顺序/判据 ｜ Narrative/LauraLee/Imagen ｜ [社区]
- **CR-A-03 ｜ 频率分离定位：只用于瑕疵级清理与色斑校正，**少用**；大量依赖 FS 会产"塑料皮/HDR 脸" ｜ 判据 ｜ Fstoppers "FS Rehab"(2014)+Adobe 官方教程 ｜ [权威]
- **CR-A-04 ｜ （争议）FS 与 D&B 先后无共识**：有 "D&B→FS" 也有 "FS→D&B"（干净底上塑形）两派 ｜ 争议 ｜ r/postprocessing 从业者自述 vs 教程两派 ｜ [社区·冲突]
- **CR-A-04a ｜ 原文补强（Fstoppers "FS Rehab" 原文已读 2026-09-19）：Woloszynowicz 派的主张比摘要更具体——①FS 定性为"末位问题定性工具"（"是否存在必须用 FS 的问题？"而非"该进 FS 了"），仅当其他工具（调整层/heal/D&B）解决不了时才用；②**若用 FS，放在工作流前端**——专业修图公司忌惮其破坏性（低频层后改会互相干扰）；③流行假设"低频层随便改反正纹理保得住"是错的（纹理渲染需要中频信息）；④时尚/商业类保留 rawness 与不完美，技术完美主义反而说明图像内涵不足 ｜ 判据/争议 ｜ fstoppers.com/photoshop/frequency-separation-rehab-42129（2014-10-28，Michael Woloszynowicz） ｜ [权威·原文已读]
- **CR-A-05 ｜ 高端塑形主力=D&B（50% 灰层/变亮变暗混合层，非破坏）；High Pass+5% 流量笔触保纹理法被广泛引用** ｜ 判据 ｜ RetouchMe/Fstoppers/IG 教程圈 ｜ [社区]
- **CR-A-06 ｜ 锐化三阶段：capture（补传感器软化，全局早做）→ creative（局部，如人像眼睛，全局调整之后做）→ output（按输出介质/尺寸定参，导出时做，与编辑期锐化叠加）** ｜ 顺序/规格 ｜ Bruce Fraser/Jeff Schewe 体系；Caponigro/LightroomQueen/CaptureOne 官方支持页/Adobe 社区 ｜ [权威多源]
- **CR-A-07 ｜ 校色先于调色：先把白平衡/曝光/对比度做"技术正确"，creative look 建立在平衡底上；look 建在未平衡底上行为不可预测 ｜ 顺序 ｜ MixingLight/RKColor/JMLTech 多源 ｜ [权威+社区]
- **CR-A-08 ｜ （细节争议）WB 与曝光互为先后的两派，实践常迭代；共识=两者都在 grade 之前完成** ｜ 争议 ｜ LiftGammaGain 色彩师论坛 ｜ [社区·冲突]
- **CR-A-09 ｜ 电商主图规格（Amazon 级）：纯白底 RGB(255,255,255)、产品占幅 ≥85%、无道具/文字/水印；白底不均匀是上架被拒主因 ｜ 规格 ｜ Amazon 规范经 PathEdits/FrameOnce 转述+Adobe 商业指南 ｜ [官方转述+社区]
- **CR-A-10 ｜ 产品图组一致性：整组图的背景清洁度/色彩/尘埃修复须统一，单张好看不算合格 ｜ 判据 ｜ POLA/PathEdits ｜ [社区]
- **CR-A-11 ｜ 过度修图红旗（停手判据）：过饱和（自然界不存在的颜色）、死黑/爆白、"瓷娃娃"无纹理皮肤、" Chiclet "假白牙与非人亮度眼睛、观者目光被"修痕"而非主体吸引 ｜ 判据/红线 ｜ ON1/Adorama/mikesmithphotography 多源 ｜ [社区多源]
- **CR-A-12 ｜ 停手启发式：修到"增强但可信"；离屏冷眼重看、与原 RAW 并排对比是两个实用自检 ｜ 判据 ｜ 多教程一致 ｜ [社区]
- **CR-A-13 ｜ 商业伦理/法规：广告须真实不误导（FTC）；法国/以色列/挪威等地对模特图重度修图强制披露标签；品牌方常有自有修图政策——交付前确认用途约束 ｜ 红线 ｜ DGLaw/FTC 相关报道 ｜ [权威·法务向]
- **CR-A-14 ｜ 人像眼神光/牙齿美白上限：以"不抢主体"为限——与 CR-A-11 同源的操作化表达 ｜ 判据 ｜ 同 11 ｜ [社区]
- **CR-A-15 ｜ 蒙版工艺方向（PiXimperfect 系）：Select and Mask 出主蒙版 + Curves 调整层精修；亮度蒙版按明度分区调色；复合/双重蒙版做高级控制 ｜ 判据 ｜ Fstoppers 转述 PiXimperfect/Kelby 博客 ｜ [权威社区]
- **CR-A-16 ｜ 高端 beauté 管线参考序：RAW 预备→清理（瑕疵/碎发）→FS（少量）→D&B（塑形）→校色→调色→输出润饰；与 CR-A-01 在 PS 内部分段一致 ｜ 顺序 ｜ r/postprocessing+Imagen 时尚修图指南 2026 ｜ [社区]
