# 默认手绘画风：粗线平涂讲解漫画

Style ID: `swaintalk-bold-flat-cartoon-v1`
English descriptor: **Bold-outline flat-color editorial explainer cartoon**.
这是描述性名称，不宣称某个作者、软件或品牌的专属画风。2026-11-06用户提供三张参考并明确选定：人物与摄像机/文件夹、向中心汇聚的机构图解、人物与法规/风险物件组合。

## 适用与优先级

这是今后新制白板插画的默认风格，替代含糊的“成熟简笔画”描述。用户当前明确覆盖优先；旧作品不自动重制。它约束绘制内容，不把真实照片、原Logo、摄影手臂、字幕和导航改成卡通。与PRESENTATION、BRAND-STATIONS和D01–D11合同同时执行。

参考图是referenceOnly，不是可公开复制的素材、角色或可恢复笔顺数据。公共包仅存描述与文件指纹，不包含这些截图。项目持有获准的本地参考时，实际传给支持图片输入的生成器；不得把示例人物/摄像机/文件夹作为所有题材默认内容。

## 风格辨识：必须保持

**S01 轮廓**：黑色或近黑色的粗实线，外轮廓强于内部细节；圆头、圆角连接，曲线流畅，带轻微手绘不对称。不是纤细工程制图，不是多次来回草稿线，不靠逐帧随机抖动表现手绘。轮廓闭合、交接干净，无双重描边或断裂。

**S02 平涂**：大面积饱满、不透明的红、蓝、黄、绿、橙、青色块，靠轮廓和色面讲清结构。每个对象通常1–3个主体色，整组选择3–5个有语义的强调色；不是每物件都塞彩虹。黑/深灰用于衣裤、头发和器械，肤色用暖浅米色。同一语义保持同色。避免透明淡彩、低饱和单蓝线稿、油画笔触、金属反光、复杂渐变和体积光。

**S03 人物**：二维商业说明漫画。可以圆头短身，也可以长脸大鼻的成人夸张肖像；两种都要保持表情、身体结构与动作可读，不把参考图差异硬锁成一种脸。点状/椭圆眼、清楚眉毛、少量鼻嘴线就能说明思考/担忧/干劲；身体要有完整衣服、手臂、手和鞋，不用圆头加线条肢体代替。手可以简化成连指手形，接触和手势必须明确。职业衣着/道具增强身份，但不要所有角色都复制蓝衣白手套。

**S04 辨识优先**：普通角色可夸张，真实指定人物仍保留辨识性的发型、脸部轮廓和服饰线索；用该漫画语言表现相似性，不转成照片写实皮肤。指定汽车/机器人/建筑保留标志性剪影与结构，不能拿通用替身。这里“更拟真”指身份/产品结构准确，而不是取消粗线平涂。

**S05 物件**：大轮廓先读得懂，内部只留能解释功能的细节。文件夹有书脊/页侧/标签，摄像机有镜头/机身/脚架，工厂有锯齿屋顶/烟囱；根据当次题材换内容。允许浅三分之四透视和一个较深侧面交代厚度，不做复杂3D渲染或精密等距网格。

**S06 表情与强调**：少量黄色短射线、蓝色汗滴、弧线、红色警示形表达动作/情绪，必须有语义且数量克制。不能为了热闹给所有对象加表情、闪光和动效。严肃事实不靠夸张表情歪曲。

**S07 关系箭头**：可用粗黑边、蓝/黄色实心宽箭头；箭身与箭头是一致的闭合轮廓，端点朝向准确。先对象后关系，绘制轮廓再平涂，不突然贴上系统默认细箭头。弯箭头服从同样视觉语法，不能穿过人物脸/文字/对象核心。支持范围仍以D09实际接口为准。

**S08 构图**：一个可辨认的叙事中心，加不等大的语义群组；人物与物件有前后、大小和留白关系。可用中心放射图、人物+物件堆、分散的小场景三种结构，不能每页复用同一放射图。无限画布随解释向任意方向生长，镜头只展示当前可读范围。不要等大卡片网格、机械左到右编号步骤或装满边角。

**S09 背景**：参考里的浅灰白纸感是一层轻微、低对比纹理；与现有SwainTalk暖象牙纸#F7F3E8兼容。纹理锁在世界纸面而不是每帧重新生成。单件资产优先透明背景，宿主统一铺纸；禁止每个对象自带不同纸色矩形、重颗粒或脏污。中性灰纸是可选项目覆盖，不静默改变片头/正文色温。

**S10 数字与文字**：截图中的10/11/13等不能当成绘制顺序模板。只有口播确实需要的年份、数量、金额可出现；不显示生产ID或1–6步骤号。图内文字短、正确、可读，用匹配粗轮廓的手绘字形；有序笔画/轮廓描绘如实命名。字幕与导航继续使用PRESENTATION的正式字体，不强迫其手写。

## 可复用起始参数（工程建议，不是从截图精密测得）

以一个屏幕可见宽400px的主体为例：外轮廓约4–7px，内部线约外轮廓的0.6–0.85；物件小于200px时优先减少细节，不把线细到看不见。1080p全画幅典型主体外线可在5–9px起步，最终以实际主体大小与320px宽缩略预览共同判断。全片统一，不因stage不同任意变粗细。

平涂优先参考色：近黑#151515、红#E2231A、蓝#0867D9、黄#F2D72E、绿#12A33A、橙#EF8A16、青#16B8CE、肤色#E8D3B3、深灰#303030。不是声称截图精确取色；允许为品牌、色弱区分或实体真色调整，保存选定tokens。不要把屏幕导航玫红强制传播到所有绘画对象。

可选阴影最多一层较深色面；不要用透明叠色或泛光取代坚实主体色。简单人物约3–4头身可作起点，成人长脸漫画单独按参考比例设计；不强制所有人统一头身比或套相同脸。

## 跨Agent/模型交接协议

每个制作任务必须提供同一style packet，而不只给一句“画成手绘风”：
1. style ID、本文版本/文件哈希、选定tokens、画幅与最终可见对象尺寸。
2. referenceOnly清单及参考图哈希/用途；可看图模型必须实际看图。文本模型只使用全文规格，并标记未读取图片，不能伪报参考一致。
3. 题材语义、所对应口播cue、必须辨认的实体特征、不要出现的无关物件。
4. 同一人物/产品的已批准样张及身份锁定信息；换模型、换Agent都复用此packet。
5. 资产角色、透明背景要求、输出层拆分和动画机制（真实路径/轮廓描绘/成图置入）。
6. 生成器/模型版本（可得时）、完整prompt、seed（支持时）、输出hash与实际复核结果。不承诺同seed跨模型生成相同像素。

第一次或更换模型时，先生成/绘制一组包含“人物、功能物件、关系箭头”的小样，内部检查匹配后再扩展全片；用户已授权制作不因此重复索要批准。优先复用本项目已确认角色/线宽/色板。模型不能稳定满足时缩小单次任务和修订样张，不能声称换一个风格名称就解决。

## 固定英文提示词骨架

Use style ID swaintalk-bold-flat-cartoon-v1. Create [SUBJECT] explaining [NARRATION MEANING]. Bold near-black smooth hand-drawn outlines, rounded joins, clean closed silhouettes, strong opaque flat red/blue/yellow/green/orange/cyan accents chosen by meaning, sparse darker side planes, expressive adult editorial cartoon characters with complete clothed bodies and readable gestures. Simple but recognizable functional objects. Slight organic asymmetry, no sketch scribble. Compose unequal semantic clusters with ample whitespace around [FOCAL SUBJECT], not a regular card grid. Preserve [IDENTITY FEATURES]. Match the supplied style reference images for contour weight, color blocking and detail density; do not copy their subjects or layout. [TRANSPARENT ASSET / UNIFIED LIGHT PAPER]. Only include [EXACT REQUIRED LABELS], no production numbering. Separate [REQUIRED LAYERS].

Negative constraints: photorealistic skin, dense painted illustration, thin monochrome outline, pale watercolor, gradients, glossy 3D, dramatic lighting, rough repeated sketch strokes, stick figures, toddler doodles, generic substitutes for named people/products, rigid equal-size grids, random decorative symbols, illegible generated text, extraneous numbers, background rectangles around cutout assets.

提示词是给生成器的完整样式约束，不代表PNG带笔顺。代码/SVG绘制同样执行上述tokens与轮廓要求。不要将negative prompt当作自动验收。

## 手绘动画准备

绘制顺序建议：主体外轮廓→关键结构→表情/功能细节→平涂→有意义强调→关系箭头。按口播调整对象先后；要求真实手绘时提供有序路径和填色区域。轮廓线宽、最终色块和透明mask在整个reveal中稳定。照片式手臂继续来自手部合同，不转换为此卡通画风；内容里的卡通人物手与执行绘画的手是两类资产。

## 风格验收表

每项记录PASS/REVISE/NOT_CHECKED及实际图片/时间窗，不只写总体“很像”。

|检查|通过标准|返修信号|
|---|---|---|
|轮廓|粗黑、干净、圆润、一致|细线、双线、碎线、抖动|
|色块|饱满平涂，多色有语义|全蓝淡彩、渐变泛光、重材质|
|人物|表情姿态清楚，实体特征正确|火柴人、幼儿涂鸦、指定人物泛化|
|物件|剪影功能可辨，少量结构细节|普通方框替代所有对象、错误产品轮廓|
|构图|有主次，大小变化，语义关联|整齐卡片、固定顺序编号、杂乱装饰|
|纸面|统一浅纸、纹理轻且稳定|每对象不同底色、纹理闪烁|
|可动画|路径/层次支持声明的绘制机制|整张擦显冒充逐笔、必要对象画不完|
|兼容性|照片手、品牌、字幕、进度层各守合同|把水印重画、字幕手写、品牌纸面接缝|

检查完整尺寸、320px宽缩览、描绘中间态和最终态；动态连续性还需正常速度播放。轮廓/色块/实体辨识/机制真实性任一返修就不能称风格通过。风格稳定来自统一packet、同项目样张及逐次复核，无法保证任意模型无需返修就完全一致。

## 形成过程与直接语义（0.4.0）

饱满平涂是最终视觉要求，不代表色面可以自动出现。执行 [PEN-SEMANTICS-CANVAS](PEN-SEMANTICS-CANVAS.md)，轮廓逐笔形成，色面可在轮廓内随画笔快速扫显；原图可由笔刷局部显露，不能称为真实笔顺。style packet同时携带逐句实体目标、身份参考、必需辨识特征和world坐标；固定三位置模板与通用替身即使线条颜色正确也不合格。
