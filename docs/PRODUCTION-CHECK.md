# 逐句制作检查：主题引入、品牌口播、画面覆盖

0.4.0整片默认顺序为：**3–5句主题引入 → 频道名与slogan配音同步的品牌站 → 正文逐句绘制**。开场主题视频/照片可以使用；频道Logo、小水印、口号和报幕在引入完成前全部隐藏。正文每句至少一个具体对应的绘制/描边/笔刷显图事件，不能仅保持旧画面或显示文字。

这份合同不枚举题材。人物、飞机、树木或新产品都可按语义新制；允许沿同一画布连续增画，不能为凑句数机械切页或重复手部进出。

## 工作流程

1. 根据文稿和实际最终配音制作完整句清单。音频文件的一段可能包含多句，字幕的一句可能拆成多条；都不能直接当作这里的句子单位。逐句核对实际音轨，遗漏或合并多句逃避覆盖均不合格。
2. 准备production.json，把引入、品牌短语时码、每句绘制事件和资产身份交给动画/剪辑。
3. presentation.json加入 `"production_path": "production.json"`。批量制作前运行plan检查；缺图、漏句、品牌提前或时码越界先修复。
4. 修改开场或增加品牌口播时重做受影响配音与时间线，字幕、章节和进度一起重算，不能以保留旧音轨为理由省去新要求。
5. 导出候选，逐句实际听看并记录具体证据；交付前运行delivery检查。缺实际听看时可以保留候选文件，但不能宣称通过交付验收。

```sh
python3 scripts/check_presentation.py PROJECT/presentation.json --mode plan
python3 scripts/check_presentation.py PROJECT/presentation.json --mode delivery
# 独立定位制作清单问题：
python3 scripts/check_production.py PROJECT/production.json --mode plan
```

这些是配置检查入口，不生成或修改视频。使用前仍遵守Skill的GitHub更新步骤。单项D01–D11素材开发不需要凭空补一部整片。

## 文件身份与时间单位

所有时码是最终整片音轨上的秒数，允许小数。每个文件引用为 `{"path":"项目内相对路径","sha256":"实际文件SHA256"}`；以production.json所在目录为根，不允许绝对路径或逃逸项目。音轨可以是全片旁白总线，品牌口播必须包含在其中。

production.json：

| 字段 | 内容 |
|---|---|
| schema | `whiteboard.production.v2` |
| duration | 最终全片秒数，须与presentation一致 |
| narration | narration.json的文件身份 |
| brand | 下述品牌站配置 |
| visual_events | 下述逐句画面事件数组 |
| candidate | delivery必需，最终视频身份 |
| timeline | delivery必需，当前可编辑合成入口身份 |
| review | delivery必需，实际审阅JSON身份 |

旧v1不能只改schema后继续制作，须补下述targets和canvas。

narration.json包含 `audio`（最终旁白文件身份）和 `sentences` 数组。每项为 `id/text/start/end/phase/targets`（brand块不需要targets）；text保留完整原话，phase为 `hook/brand/body`。顺序必须为3–5条hook、1条brand报幕块、至少1条body；时间顺序不重叠。品牌块是唯一允许合并频道名和两个口号短句的专门记录，正文每条必须为完整单句。

## 品牌同步

brand包含 `start/end/first_identity_at/phrases`：

- start/end是整个片头品牌站窗口，位于最后引入句之后、第一正文句之前。
- first_identity_at是全片最早出现任何频道身份的时刻，包括小水印。不得早于品牌站，也不能晚于频道名开始。
- 品牌块实际口播为 `SwainTalk. Follow the tech. Follow the money.`，不得用主题口播替代报幕。
- phrases有三项，依次为 `SwainTalk`、`Follow the tech.`、`Follow the money.`。每项包含 `text/start/end/visible_start/visible_end`，start/end来自实际短语配音，visible区间必须覆盖该短语完整声音并位于品牌站内。Logo表示频道名，slogan对应文字；不要求文字逐笔描出。画面排版仍保留规范的两空格口号。
- 这只验证声明的时码关系。实际Logo显隐、词音对应和尾音仍须连续听看，不能凭JSON中的数字宣称同步通过。

## 逐句画面事件

visual_events每项：

| 字段 | 内容 |
|---|---|
| id | 全片唯一事件ID |
| sentence_id | 唯一对应的完整口播句ID，不接受ID数组代替逐句设计 |
| subject | 要让观众看见的具体人物、物件或场景 |
| meaning | 它表达该句什么含义、动作或关系 |
| kind | 正文为 `draw_paths / outline_trace / brush_reveal`；hook额外允许 `footage` |
| start/end | 该句内的绘制/笔刷显露动作窗口，必要主体必须完成 |
| readable_until | 完成画面保持可读至该句结束或更晚，不超过全片 |
| asset | 可用资产文件身份；draw_paths/outline_trace必须为SVG或路径JSON，PNG不能冒充笔顺 |

额外动画、静态保持、字幕或镜头运动可存在于宿主时间线，但不作为合格覆盖事件填入这个数组。相邻句可给原场景增画有语义的物件、动作线或关系；不能只重复出现同一图标或无关装饰来凑数。检查器不会辨认资产画得对不对，subject/meaning与实际画面的对应必须人工或具备实际视听能力的Agent审核。

## delivery审阅记录

review.json要求：

- `candidate_sha256 / timeline_sha256 / narration_sha256`：与当前视频、合成入口及句清单一致。句清单又绑定当前旁白音频。
- `visual_events_sha256 / brand_sha256 / canvas_sha256`：对production对应字段执行 `hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()`；改画面计划或品牌时码后旧审核失效。
- `canvas_checks`含 `pen_contact / no_automatic_reveal / literal_semantics / freeform_layout / canvas_continuity`，每项为 `{status:"PASS", evidence:"实际检查窗口与观察"}`。必须检查每个元素的形成、实体所指、纸面文字、布局及全体过渡，不能只抽一例代表全片。
- `normal_speed_viewing: true`、`actual_audio_listening: true` 只能在实际完成后填写。
- `hook_no_brand: "PASS"`、`brand_av_sync: "PASS"`；引入与正文的 `sentences` 为逐句 `id/status/evidence`，每条须PASS且有具体审阅窗口/观察说明。未检查应如实写NOT_CHECKED，不能为了让脚本返回0伪造记录。

机器检查证明文件身份、声明的覆盖/时间关系和审阅记录是否齐全；**不会独立观看、听音或识别语义，也不能验证一个人是否真的执行了review**。计划PASS、记录PASS和用户接受必须分开。最终像素/听感不符合时仍应返修。

## 直接实体与canvas字段（v2必需）

每条非brand口播的`targets`包含所有必要主体、对象、动作/关系及关键数据：

- `id`全片唯一，`mention`逐字引用该句中的指代，`depiction`说明直接画什么。
- `entity_type`为`named_person / organization / product / role / object / action / data`。
- 指定人物/机构/产品额外提供`identity`准确名称、`recognition_cues`辨识特征、`reference`参考文件身份及`source`出处。代词可作为mention，但identity仍指向已明确的实体。不能为了绕过参考要求把命名实体填成object。
- 匿名角色使用role，必须`illustrative: true`，不得编造真实身份。

`canvas`为以下对象：

| 字段 | 内容 |
|---|---|
| world_id | 唯一世界画布标识 |
| persistent | 必须true，已画对象持续保留 |
| layout | `semantic_freeform`，不得使用固定三槽/页式模板 |
| elements | 全部纸面元素，包括字、色、箭头和原图 |
| overlaps | 有意相交数组，每项`elements:[id1,id2]`与具体`reason`；普通碰撞失败 |
| camera | 同世界、连续全片相机记录 |

每个element包含`id/event_id/target_ids/role/world_id/bounds/reveal`：

- `event_id`对应visual_events。一个事件可含多个图形/图层，数量不固定；所有事件和语义target均须有元素覆盖。
- `target_ids`引用句清单中的必要所指；同一已画元素可以对应后续句的目标，但实际镜头必须仍可读，每句仍需自己的新语义动作。元素不得晚于对应句出现。
- `role`为drawing/text/image/footage；`bounds:[x,y,width,height]`是世界占用框，包括伸出内容。正尺寸、有限数值。碰撞检查不判断实际透明像素，因此有意前后景/接触须说明。
- drawing/text的`reveal.method`为`pen_path`，image为`pen_mask`；二者均含`program`（笔触JSON文件身份）、`layer_id`、全片秒数`offset`和`fps:30`。全片时间=`offset + strokeFrame/30`，该层全部笔触须位于对应事件内。
- program采用[D01 scene.pen格式](PEN-PROGRAM.md)，不能含旧draw/objects/foreground/title。program里的每个layer都要映射到元素，同层不能冒充多个对象。运行时进一步检查笔速、移笔、复合路径、图片文件及解码。
- 仅hook视频可使用`role:footage, reveal:{method:"hook_footage"}`。静态图不享有视频例外。字幕/导航/频道品牌站属于另外已约定层，不把正文图解伪装成这些例外。

camera含`world_id`、`interpolation:"continuous"`、`route_basis`（为何这样移动）、`keyframes:[{t,x,y,scale},...]`。t从0到整片duration严格递增，scale正数；x/y为世界中心，连续插值。允许多方向/回看，不强制方向配额。记录并不自动装配宿主相机；禁止页索引乘屏宽、重置对象、幻灯片滑页。

程序检查元数据与笔触绑定，不自动识别漏登记的事实目标、被错误分类的实体、假占用框、巨型擦除、实际可见性或重复模板。制作Agent必须逐句核对，delivery证据绑定当前canvas，实际画面不符合仍返修。具体拒绝示例与流程见[严格harness](../skills/whiteboard-video/harness/PEN-SEMANTICS-CANVAS.md)。
