# 安装、创建工程与渲染

需要 Node 22+、Python 3.10+、npm、FFmpeg 和 ffprobe 可在命令行找到。下列命令在插件根目录执行；工作工程放在插件源目录/安装目录之外。

## 打包与本地安装

```sh
python3 scripts/package_plugin.py
codex plugin marketplace add ./dist
codex plugin add swainwong-whiteboard-video-plugin@swainwong-whiteboard-local
```

打包器生成`dist/`本地marketplace和0.1.0版本zip。安装插件与创建视频工程是两件事：不要直接改安装包中的runtime或把渲染输出写进插件。

## 创建可编辑工程

```sh
python3 scripts/project.py init ../my-whiteboard-video --install
```

复制runtime并安装其锁定依赖。目标目录必须尚不存在，防止覆盖已有工作。工程是后续素材、输入JSON和输出的存放位置。

将图片放到工程`public/assets/`；在场景里以`assets/filename.png`引用。把props保存到工程的`scene.json`，内容格式见[输入输出](INPUT-OUTPUT.md)。也可以先用工程中的现成`examples/*.json`熟悉输入格式。

## 校验并渲染

```sh
python3 scripts/project.py check ../my-whiteboard-video scene.json
python3 scripts/project.py render ../my-whiteboard-video scene.json --output out/revision-01.mp4
```

`SCENE`与`--output`路径可以相对工程或为绝对路径；默认输出为`out/Dxx.mp4`。输出已存在就拒绝覆盖，请使用新的修订文件名。wrapper将输入、素材及时间约束检查后再调用Remotion，完成后解码并写入同名`.receipt.json`。原始scene或`{"scene":{...}}`包裹形式均可给wrapper；直接Remotion调用使用包裹形式。

如果宿主的Remotion下载浏览器无法启动，可设置`REMOTION_BROWSER_EXECUTABLE`为本机兼容浏览器的可执行文件路径；wrapper会传给官方`--browser-executable`参数。不要复制开发者机器的绝对路径。本次开发环境的下载版Headless Shell启动失败，使用系统Chrome完成实际渲染；这不保证所有宿主浏览器都已测试。

正式自定义任务使用`project.py check/render`。runtime的`check-scene.cjs`仅检查结构/预算；直接`npx remotion`是开发用低级接口，不会自动完成wrapper的本地素材存在/解码与D10来源像素验证，不能绕过后声称合格。

## 从完成视频提取总览快照

先把真实完成的1920×1080视频放到工程`out/CompositionName.mp4`；文件名只能含字母、数字、下划线或短横线。然后：

```sh
python3 scripts/project.py capture-stage ../my-whiteboard-video out/CompositionName.mp4 --id stage01
```

默认提取最后一帧；用`--frame N`指定从0开始的实际帧号。工具生成`public/assets/completed-stages/stage01.png`及同名`.stage.json`，其中包括原视频哈希、composition标识、帧号和PNG哈希。不要手工编造这些值。已有stage拒绝覆盖，修改后使用新ID。

发布包包含用于预览的已生成完成PNG，但不附源MP4；它们不能免除正式D10的来源检查。新工作区应提供自己的真实源视频，或先在工作区运行`python3 render-all.py`重建全部示例视频与快照。

查看所选帧确实已完成且没有手遮挡关键内容，再将各`.stage.json`对象按实际完成顺序加入D10场景的`stages`。D10的check/render wrapper会重新解码原视频指定帧，与快照逐像素比较；不仅检查哈希字符串。源视频仍需保留在工程`out/`，不能只搬走PNG后宣称可核验。

## 当前验证边界

技术验证含Python wrapper测试、runtime输入边界测试、11项示例实际渲染及自定义输入的独立尝试。具体数量与当前产物身份以交付验证报告为准，不把文档中的测试描述当运行证明。解码成功、源帧像素相符和独立输入尝试不等于正常速度视听或用户接受。
