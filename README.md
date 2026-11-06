# SwainWong Whiteboard Video

把讲解文字、插画和资料图组织成连贯的 **Whiteboard Animation（白板动画）**，交付可编辑的 Remotion 工程与视频。

这是独立插件，入口是 `$whiteboard-video`。它维护11项动画方法及配套输入、素材与检查规则，不依赖原视频制作插件，不附带第三方参考片。照片质感手臂为生成资产，不能标作真人实拍。

## 整体怎么用

给出要解释的文字意思，以及可选的参考图/运行素材 → 选择适合的动画 → 准备路径或现成图 → 按讲解时间安排绘制与阅读 → 校验并渲染 → 查看实际画面 → 交付工程与视频。

可以只画一个足以说明意思的对象。文字、卡通、图形、照片都能进入白板，但进入方式不同：逐笔绘制需要路径；已有图片适合渐入、摆放或叠加。图片不是笔顺，生成图片也不是绘画过程。

- [完整11项动画目录](docs/ANIMATION-CATALOG.md)：每项适用场景及详细合同。
- [资产来源与使用边界](docs/ASSET-PROVENANCE.md)：生成手臂、原创示意资产及字体的来源。
- [实际输入与输出](docs/INPUT-OUTPUT.md)：哪些字段可调用，哪些准备仍需完成。
- [风格与连续性Harness](skills/whiteboard-video/harness/HARNESS.md)：稳定画面的必做、禁止和检查边界。
- [Skill入口](skills/whiteboard-video/SKILL.md)：给Agent的简短路由。

## 安装与开始

需要 Node 22+、Python 3.10+、npm、FFmpeg/ffprobe。构建本地marketplace后安装插件，再创建独立的可编辑视频工程。

```sh
python3 scripts/package_plugin.py
codex plugin marketplace add ./dist
codex plugin add swainwong-whiteboard-video-plugin@swainwong-whiteboard-local
python3 scripts/project.py init ../my-whiteboard-video --install
```

[运行说明](docs/RUNNING.md)包含场景校验、渲染、真实完成帧提取和浏览器兼容处理；每次输出使用新文件名，避免覆盖已有视频。

## 内容与分镜

**接收**讲解文字、要解释的对象、时长或口播cue，以及参考图片。

**处理**一句话究竟需要什么画面；选择完整主体、关键词或关系图，安排先后次序与留白。

**输出**对象语义、效果ID、必要内容和时间窗，交给资产准备。

## 资产与笔画

**接收**对象、画风、参考与绘制要求。

**处理**成熟说明插画、可用照片、有序路径或字形轮廓；把参考图、运行资产、真实完成stage快照分开登记。准备透明手臂及笔尖/接触点校准。

**输出**可用资产、路径、来源和锚点，交给动画实现。没有路径的成图不会被假装成真实逐笔绘制。

## 动画与渲染

**接收**效果输入、资产、布局和时间。

**处理**路径绘制、手部连续移动、成图置入、图层与画布运动。口播时间不足时减少完整内容或换完整简化画法；必要部分仍容不下就报出缺口。

**输出**输入JSON、工程、视频和技术验证，交给画面检查及下游剪辑。总览只沿纵向展示实际已经完成的stage，不新造卡片。

## 画面检查与交付

**接收**当前视频、文件身份和来源记录。

**处理**入场、绘制、接触、保持、退出与最终画面；检查自然手绘边缘、可替换图片节点、时间预算及总览来源。改变内容或时序后复查受影响窗口。

**输出**实际检查范围、具体问题与修复结果，交给用户确认。输入校验、渲染成功、局部像素检查、正常速度观感和用户接受分别记录。

这些角色是组织工作的建议，不要求每次派齐Agent或重复请求审批。完整分工见[工作流说明](skills/whiteboard-video/references/workflow.md)。

## 可移植性与当前边界

运行素材使用项目public目录相对路径；字体文字应先变成可移植路径，并保留字体或笔顺来源。项目可用内置原创样例，也可换任意合法准备好的图片与路径。插件不提供“任意JPEG自动变真实笔顺”或“任意布局自动布线”。

D09当前为向下曲线分支；D10使用带原视频/帧/哈希的完成PNG，仅纵向排列；D08/D11的字形由调用方提供，背景颜色可配。具体实现能力和限制以[输入输出合同](docs/INPUT-OUTPUT.md)及runtime类型为准。

## 长篇制作与发布规则

[Production harness](skills/whiteboard-video/harness/PRODUCTION.md) 将逐句口播映射到有机画布上的简笔画与资料图，规定对象辨识、连续手部与可验证的交付。输入为 brief、口播时间、来源和品牌资产；输出为 cue map、动画输入、审核证据与发布包，交给动画、剪辑和发布环节。

SwainTalk 封面配置使用右下角商标、清晰短标题和可辨认的人物/产品。标题与描述须贴合成片；不承诺关键词避让能保证推荐或广告收益。OpenFilm / Video Factory 对接仅在项目要求时使用，不是插件内置依赖。

## 整片展示层与制作平台

[展示层合同](skills/whiteboard-video/harness/PRESENTATION.md)接收平台、最终音轨时钟、章节、字幕语言和原Logo，以独立屏幕层组织顶部进度、底中短语字幕与右下透明水印。输出展示配置和检查报告交给用户选定的OpenFilm或ChatCut合成；双平台分别验收。Remotion继续生成白板动画素材。

复制[参数配置](docs/presentation-profile.json)到项目的layout字段，按合同准备presentation.json，然后运行 `python3 scripts/check_presentation.py /path/to/presentation.json`。校验不自动装配平台，也不代替最终像素与实际听看。该合同不会将白板改成纸艺或强制第三方满屏；封面Logo与视频水印独立。
