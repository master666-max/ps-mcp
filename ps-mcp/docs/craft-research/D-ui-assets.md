# 工艺调研底稿 · D UI 资产切图（craft-research/D）— 检索 2026-09-19

- **CR-D-01 ｜ iOS 主图标：1024×1024 一张母版；Xcode 14+ "Single Size" 自动派生全部变体 ｜ 规格 ｜ Apple Developer 官方+UseYourLoaf ｜ [官方]
- **CR-D-02 ｜ iOS 文件命名：`icon@2x.png`/`icon@3x.png` 后缀制（@2x=2×、@3x=3×），资产目录 AppIcon.appiconset 管理 ｜ 规格 ｜ Apple 官方 ｜ [官方]
- **CR-D-03 ｜ Android 启动图标：48×48 dp 设计基准；密度桶 mipmap-mdpi 48 / hdpi 72 / xhdpi 96 / xxhdpi 144 / xxxhdpi 192（px）** ｜ 规格 ｜ Android Developers 官方 ｜ [官方]
- **CR-D-04 ｜ Android 自适应图标（8.0+）：108dp 规格、66dp 安全区，前景/背景两层 ｜ 规格 ｜ Android 官方 ｜ [官方]
- **CR-D-05 ｜ Google Play 商店图标：512×512 px 独立交付 ｜ 规格 ｜ MobileAction 等转述 ｜ [社区转述官方]
- **CR-D-06 ｜ 两平台命名范式差异：iOS=@后缀文件名；Android=密度桶目录名——切图脚本按目标平台选范式（可机验）** ｜ 判据 ｜ 本轮对比归纳 ｜ [本项目归纳·基于官方]
- **CR-D-07 ｜ Web 导出格式决策：2026 默认 WebP（全浏览器支持、比 JPEG 小 25-35%）；追求极致体积用 AVIF（比 JPEG 省约 50%）；兼容回退保留 JPEG/PNG ｜ 规格 ｜ web.dev/Hiredigital/Smashting ｜ [官方+社区]
- **CR-D-08 ｜ 质量等效参考：JPEG q60 ≈ AVIF q50 ≈ WebP q65（视觉等效起点，非定律）** ｜ 规格 ｜ IndustrialEmpathy（Google 工程师博客） ｜ [权威·待官方原文核]（web.dev 深读待补）
- **CR-D-09 ｜ 响应式交付：srcset/sizes 按设备送正确尺寸——切图任务的尺寸清单应由断点决定而非拍脑袋 ｜ 判据 ｜ MDN(2025-11)/DebugBear/imgix ｜ [官方+权威]
- **CR-D-10 ｜ 无损场景用 WebP 无损/PNG；截图/透明层级 UI 元素优先 PNG 或 WebP 无损，照片类一律有损系** ｜ 判据 ｜ web.dev 摘要+社区 ｜ [官方+社区]
- **CR-D-11 ｜ 资产包交付纪律：命名=设计稿图层名约定（D 分支 G3 对账的输入）；多倍率成组交付时逐组机验尺寸** ｜ 判据 ｜ 由 skill G3+本轮命名规范归纳 ｜ [本项目归纳]
- **CR-D-12 ｜ 社媒平台规格同 CR-C-11（共享条目，Sprout 原文 2026-05-11 已核），切图任务直接引用当期规格页 ｜ 规格 ｜ 同 C-11 ｜ [权威·原文已读·时效敏感]
- **CR-D-13 ｜ SVG/矢量资产：PS 的 CopySVG/CopyCSS 内置脚本存在【实测·静态在装】——矢量交付优先源矢量工具，PS 只做位图侧 ｜ 判据 ｜ 装机证据+生态常识 ｜ [实测·静态]
- **CR-D-14 ｜ 图标网格与视觉重心：平台规范建议图标在网格内留视觉边距（内容与容器非等大）——具体网格数值各平台文档为准（HIG 深读待补）** ｜ 判据 ｜ HIG 摘要级 ｜ [官方转述·待深读]
