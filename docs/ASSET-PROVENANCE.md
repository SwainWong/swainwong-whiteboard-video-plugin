# 随包素材与来源

插件不携带第三方参考视频、原作者插画、口播或截图。白板动画的名称参考 [VideoScribe官方说明](https://www.videoscribe.co/en/whiteboard-animation/)，手绘与成图入场混用参考其[动画方式组合说明](https://blog.videoscribe.co/how-to-use-different-animation-styles-together-in-one-video)。这些链接用于界定方法，不代表采用VideoScribe软件或获得其品牌授权。

## 插画与手臂

`runtime/src/Artwork.tsx`包含本项目制作的成熟说明插画。手绘版本与完成版本共享路径；内置人物、汽车、工厂是可替换示例，不是所有题材的默认答案。

`writing-hand-long.png`与`palm-real.png`为此前本地制作中生成的照片质感透明资产，属于生成素材，不是实拍演员。写字手校准见`runtime/src/hand-config.json`；推图手校准在`PalmPlace.tsx`及D06合同中。替换手臂必须重新量笔尖/接触点、透明边界及屏外退出位置。

文件身份见[素材清单](asset-manifest.json)。清单记录本次包的文件，不把某一次用户对效果的认可扩成每个后续内容的自动验收。

## 字体

示例SALE字形由[Noto Sans](https://github.com/google/fonts/tree/main/ofl/notosans)生成，附字体、[SIL OFL许可证](../runtime/public/fonts/OFL.txt)及[来源记录](../runtime/public/fonts/provenance.json)。原实验的Arial派生轮廓没有作为本插件字形来源保留。

调用者可以提供其他有依据的字形路径；字形外轮廓不等于真实笔顺。汉字逐笔书写需要有序笔画。示例的中文说明标题属于普通阅读层，具体系统中文字体的外观可能不同；需要跨机器一致的正式标题应提供可用字体或轮廓。

## 完成画布与依赖

示例总览快照来自本插件实际渲染的十个完成画面，带视频SHA256、帧号和快照SHA256。它们仅供示范；正式影片必须换成该影片自身的完成帧。`capture-stage`可从项目已导出的MP4提取并登记；渲染入口重新解码比对像素，不凭一段来源文字认定真实来源。

Remotion、React等运行依赖由`package-lock.json`精确记录，安装时从npm获取；其许可归各上游项目。包内不复制依赖安装目录。
