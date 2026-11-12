# 逐句制作检查：主题引入、品牌口播、画面覆盖

0.3.0整片默认顺序为：**3–5句主题引入 → 频道名与slogan配音同步的品牌站 → 正文逐句绘制**。开场主题视频/照片可以使用；频道Logo、小水印、口号和报幕在引入完成前全部隐藏。正文每句至少一个具体对应的绘制/描边/手掌摆图事件，不能仅保持旧画面或显示文字。

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
| schema | `whiteboard.production.v1` |
| duration | 最终全片秒数，须与presentation一致 |
| narration | narration.json的文件身份 |
| brand | 下述品牌站配置 |
| visual_events | 下述逐句画面事件数组 |
| candidate | delivery必需，最终视频身份 |
| timeline | delivery必需，当前可编辑合成入口身份 |
| review | delivery必需，实际审阅JSON身份 |

narration.json包含 `audio`（最终旁白文件身份）和 `sentences` 数组。每项为 `id/text/start/end/phase`；text保留完整原话，phase为 `hook/brand/body`。顺序必须为3–5条hook、1条brand报幕块、至少1条body；时间顺序不重叠。品牌块是唯一允许合并频道名和两个口号短句的专门记录，正文每条必须为完整单句。

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
| kind | 正文为 `draw_paths / outline_trace / hand_place`；hook额外允许 `footage / photo` |
| start/end | 该句内的绘制/置入动作窗口，必要主体必须完成 |
| readable_until | 完成画面保持可读至该句结束或更晚，不超过全片 |
| asset | 可用资产文件身份；draw_paths/outline_trace必须为SVG或路径JSON，PNG不能冒充笔顺 |

额外动画、静态保持、字幕或镜头运动可存在于宿主时间线，但不作为合格覆盖事件填入这个数组。相邻句可给原场景增画有语义的物件、动作线或关系；不能只重复出现同一图标或无关装饰来凑数。检查器不会辨认资产画得对不对，subject/meaning与实际画面的对应必须人工或具备实际视听能力的Agent审核。

## delivery审阅记录

review.json要求：

- `candidate_sha256 / timeline_sha256 / narration_sha256`：与当前视频、合成入口及句清单一致。句清单又绑定当前旁白音频。
- `visual_events_sha256 / brand_sha256`：对production对应字段执行 `hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()`；改画面计划或品牌时码后旧审核失效。
- `normal_speed_viewing: true`、`actual_audio_listening: true` 只能在实际完成后填写。
- `hook_no_brand: "PASS"`、`brand_av_sync: "PASS"`；引入与正文的 `sentences` 为逐句 `id/status/evidence`，每条须PASS且有具体审阅窗口/观察说明。未检查应如实写NOT_CHECKED，不能为了让脚本返回0伪造记录。

机器检查证明文件身份、声明的覆盖/时间关系和审阅记录是否齐全；**不会独立观看、听音或识别语义，也不能验证一个人是否真的执行了review**。计划PASS、记录PASS和用户接受必须分开。最终像素/听感不符合时仍应返修。
