# 可执行笔触程序：D01的严格绘制模式

`scene.pen`替代旧`scene.draw`，仅适用于D01。它是可调用的绘制组件，不是自动插画生成器。轮廓沿路径绘制；色面可随笔的一次连续扫过快速显露，不在最后自动补全整图。

```json
{
  "scene": {
    "effectId": "D01",
    "durationFrames": 150,
    "pen": {
      "layers": [{"id": "outline"}],
      "strokes": [{
        "id": "line-1", "layer": "outline",
        "d": "M 600 400 L 900 500",
        "width": 8, "color": "#151515",
        "start": 30, "end": 70
      }]
    }
  }
}
```

- `layers`按渲染叠放顺序排列，每层唯一id；可选`clip`为SVG封闭轮廓，用于裁掉越界笔刷。
- 图层可选`image: {src,x,y,width,height}`，src是工程public内可由FFmpeg解码的PNG/JPEG等位图相对路径；SVG标志先准备路径或显式栅格化副本，不能假设本机FFmpeg可解SVG。此时该层所有笔触累积成局部alpha mask，原图只在笔刷经过处显露；`color`仍须合法，但遮罩使用白色。wrapper同时检查图片文件和解码身份。
- `strokes`按实际落笔顺序排列，id唯一、layer存在、d只有一条连续子路径（一个M/m）。多个离散轮廓拆成多笔并预留移笔时间。width为世界像素、color为#RRGGBB；start/end为30fps素材帧号。
- 第一笔至少从第20帧开始；末笔结束至少留45帧供阅读和整组退场。路径平均速度上限30世界像素/帧，移笔距离也须留足帧数；时间不够报错，不删笔画。该上限不是美术速度保证，仍须按可读性放慢。
- 色面可使用 `sweep: {bounds:[x,y,width,height], direction:"left-to-right" | "right-to-left" | "top-left-to-bottom-right"}`，目标层必须提供 `clip` 轮廓。该笔画的进度驱动区域扫显，同一时间路径驱动画笔位置，调用方需按扫色方向设置路径并核对动作；扫显是视觉效果，不代表逐像素笔尖接触。扫过该clip后只证明这个clip完成，不能证明整个对象完成；调用方必须先按对象列全所有目标色面、颜色和有意留白，并核对目标图与最终画面。不能越出clip或用透明度整块淡入。示例见 `pen-painted-shape.json`。普通笔触速度上限30像素/帧，扫色路径允许至120像素/帧。
- 同一支校准笔由当前stroke前缀端点驱动，笔间连续移到下一起点，整组结束后退场。笔刷尺寸和手图笔尖的视觉匹配必须实际复核。
- 此模式禁止同时提供`draw`、`objects`、`foreground`和非空`title`。纸面字也转为stroke；本组件不会预置题目或参考图。

完整涂色样例：`runtime/examples/pen-painted-shape.json`。在新建工程中：

```sh
python3 <plugin-root>/scripts/project.py render PROJECT examples/pen-painted-shape.json --output out/pen-check.mp4
```

具体CLI参数以`project.py render --help`为准。原图需由项目明确提供，通用插件不预置具体项目的实体参考素材。

整片对接：将各局部素材坐标统一变换到canvas世界坐标，并以`offset + localFrame/30`同步全片。宿主只显露已绘制像素，不能在素材结束后切到更完整的终图；连续手部和相机需宿主实现并复核。旧workspace不自动获取这个组件，需从新版建立工程或显式迁移源文件后重新验证。

宿主可从runtime/src/library.ts导入PenDrawing，保留其透明SVG图层并统一world变换。独立D01导出的MP4带纸色背景，是机制素材/预览；不能把多个不透明矩形视频并排滑动就宣称实现无限画布。
