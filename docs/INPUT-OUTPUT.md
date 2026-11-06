# 输入、实际运行接口与交付

## 先确定内容，再传参数

制作需要明确文字语义，以及哪些对象必须保留。图片可以作为风格参考或实际图层；它没有天然的笔画顺序。任务输入应说明：表达意思、使用效果、必需对象、时长/口播cue、图片角色和期望的绘制方式。运行JSON只保存渲染所需字段，不替代这份内容说明。

| 输入角色 | 如何使用 | 失败边界 |
|---|---|---|
| `referenceOnly` | 看风格/理解实体，不自动进时间线 | 不能当可用运行图片或笔顺 |
| `runtimeAsset` | 复制到项目public内后，按public相对路径引用 | 缺文件/尺寸/必要路径时停止该项 |
| `existingFinishedSnapshot` | 用于D10，提供真实完成PNG和来源身份 | 缺原视频/帧/哈希时不能伪造 |

这三个角色是输入与来源台账术语，当前并非`SceneNode.asset.type`的枚举。实际asset类型见下文。

正式任务通过project.py check/render执行素材存在/解码与D10源帧像素检查。runtime检查器只有结构/预算职责，直接Remotion接口不替代这些检查。

具体命令、工作工程初始化与快照提取见[运行说明](RUNNING.md)。

## 场景接口

Remotion composition名为 `WhiteboardRecipe`，props文件顶层是 `{"scene": {...}}`。类型定义权威是 [scene.ts](../runtime/src/scene.ts)，渲染行为权威是实际Recipe实现。画布为1920×1080、30fps；参数时间均为整数帧。不要把设计意图写成未实现的参数。

WhiteboardRecipe按效果拒绝缺输入：绘画必须显式paths+cue，字形必须glyphs，成图必须objects，叠层必须foreground，分支必须nodes/edges，总览必须stages。演示composition的默认素材不作为用户任务的静默替代。

基础字段：`effectId`为D01–D11之一，`durationFrames`为总帧数，`title`为可选说明层。图内被绘制的文字必须走字形或有序路径，不能只放进title。

| 字段 | 结构与作用 |
|---|---|
| `objects` / `foreground` | `SceneNode[]`，分别为对象组/前景组 |
| `draw` | `x? / y? / scale? / paths / cue / fillAt?`；cue含`id/start/end/readHold` |
| `glyphs` | 必需`width/height/glyphs:[{x,d}]`，可选`minY`；x偏移、向上为正的字体路径及实际字形组边界 |
| `color` | `#RRGGBB`，供字内/背景填色 |
| `timing` | `enterStart/enterEnd/release?/exitEnd?`；D03/D04/D05/D07消费enterStart/enterEnd；D06另消费release/exitEnd；不用于D01/D02/D08/D09/D10/D11 |
| `contact` | 推图手与资料的舞台接触点`{x,y}` |
| `nodes` | 分支节点`{id,x,y,width,height,object:SceneNode}[]` |
| `edges` | 有向连接`{from,to}[]` |
| `stages` | 完成快照`{id,src,provenance:{sourceComposition,sourceVideoSHA256,frame,snapshotSHA256}}[]` |

`SceneNode`含可选`x/y/scale`及必需`asset`：

- `type: builtin`，`name: car | person | factory | document`。这些是现成可替换样例，不限制可讲的题材。
- `type: image`，`src/width/height`。src为项目public下的相对路径，不传远端URL或开发机绝对路径。
- `type: paths`，`paths:[{d,fill,stroke?,strokeWidth?}]`。这是完整静态对象；要逐笔绘制则放在`draw.paths`。
- `type: group`，`children:SceneNode[]`，将多个对象作为一组布局和移动。

## 每种效果消费什么

| 效果 | 内容输入 | 输出与边界 |
|---|---|---|
| D01 | draw有序路径+cue | 完整轮廓逐笔及填色；用户场景必须显式给路径；示例车的简化逻辑不能视为任意图自动简化 |
| D02 | objects + draw | 保留旧组并画新对象；布局由调用方预先给定 |
| D03 | objects + timing? | 固定位置渐入的成图，不产生笔顺 |
| D04 | objects + draw + timing? | 整组上移后新对象绘制 |
| D05 | objects + draw + timing? | 旧组左移后在右侧绘制 |
| D06 | objects + contact?/timing? | 图手共移动后分离；手图有固定校准，非任意图片自动接触 |
| D07 | objects + foreground + timing? | 底层保留，上层渐入 |
| D08 | glyphs + color? | 字形轮廓→字内填色，不自动文字转路径 |
| D09 | nodes + edges | 对象→曲线单线箭头；仅向下且上下间距≥100像素 |
| D10 | stages | 从末项到单列纵向总览；真实完成快照、扁平PNG，不支持虚构stage或横向排列 |
| D11 | glyphs + color? | 字形轮廓→自然手绘背景；固定确定性边界形状，颜色可配置 |

完整11项必需/可选输入及使用场景见[动画目录](ANIMATION-CATALOG.md)。当前不会自动从文字选择素材或生成真实笔顺。真实完成帧由准备阶段调用`capture-stage`从实际完成视频提取。

## 一个最小成图输入

以下展示格式，不代表真实任务都应该用汽车：

```json
{
  "scene": {
    "effectId": "D03",
    "durationFrames": 240,
    "objects": [{"x": 600, "y": 350, "scale": 1.5, "asset": {"type": "builtin", "name": "car"}}]
  }
}
```

若改为真实图片，将asset改为`{"type":"image","src":"assets/your-image.png","width":720,"height":480}`并确实提供文件。图片许可/来源登记在任务资产清单中。

## 时间预算与文字准备

`cue.end - cue.readHold`是绘画截止时间；之后留给观众阅读，另保留手部完整退出所需帧。路径按舞台缩放后的弧长分配绘制时间。不能通过减少路径数组尾部来保证任意图仍完整；应标出必要语义组，或准备另一份完整简化图。

`draw.fillAt`默认等于deadline，只允许整数帧且必须位于`drawEnd..deadline`，不能提前上色。`drawingPlan(scene)`按实际路径/缩放计算；默认缩放D01为2、D02为1.2、D04为1.7、D05为1.6。显式scale覆盖默认，预算随之重算。D04/D05的`draw.cue.start`不能早于移屏`timing.enterEnd`（默认分别100/70帧）。

D08/D11的glyphs必须声明`width`、`height`，可选`minY`（默认0）；路径使用字体坐标，y向上。实际轮廓按声明边界采样校验，并整体等比fit到1100×400，不拉伸高字或单字。包含下伸部时给正确minY，不用虚假边界蒙混校验。

D08/D11的总帧数至少为`20 + glyph数量 × 27 + 100`，不足直接拒绝，不能截掉末字/填色/退场。

任意字样先排版，再用选定字体生成glyph轮廓；真实汉字书写则提供可靠笔顺的有序路径。插件不依赖一台机器的字体，也不把SALE当用户输入。字体/笔顺数据来源与实际权限随工程交付，详见[资产准备](../skills/whiteboard-video/references/assets-and-writing.md)。

## 输出与证据

项目应交付：内容简报、实际props、可搬迁public资产、来源/锚点/快照台账、选用/省略计划、渲染MP4、当前文件哈希及检查报告。文字/路径仍可编辑，D10快照需要回原composition修改后再生成。

失败返回具体字段或资产缺口；必需输入缺失不默默换成研究示例。技术检查只证明对应技术事实：路径存在不证明画得好，快照哈希不证明源帧正确，像素相符不证明正常速度流畅，均不等于用户接受。

## 整片展示层输入（独立于 scene）

`presentation.json` 为全片合成合同，不传入 D01–D11 scene，不改变旧效果接口。必需字段及默认token见 [PRESENTATION](../skills/whiteboard-video/harness/PRESENTATION.md) 和 [profile](presentation-profile.json)。制作前校验配置，交付前以最终音轨时长重新运行 `python3 scripts/check_presentation.py presentation.json`。失败只阻止整片展示层交付，不阻止独立动画素材准备。输出JSON报告含配置范围和错误，退出码0/1；不自动创建平台工程或给出像素/AV通过。
