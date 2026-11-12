# 安装、创建工程与渲染

需要 Node 22+、Python 3.10+、npm、FFmpeg 和 ffprobe 可在命令行找到。下列命令在插件根目录执行；工作工程放在插件源目录/安装目录之外。

## 打包与本地安装

```sh
python3 scripts/package_plugin.py
codex plugin marketplace add ./dist
codex plugin add swainwong-whiteboard-video-plugin@swainwong-whiteboard-local
```

打包器生成`dist/`本地marketplace和与 `plugin.json` 一致的版本zip。安装插件与创建视频工程是两件事：不要直接改安装包中的runtime或把渲染输出写进插件。

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

## 制作前更新

首次从当前源码打包安装后，每次制作开始或继续时运行：

```sh
python3 scripts/update_latest.py
```

入口固定信任本项目 GitHub 仓库的 `main`，不是 GitHub Release 或最高版本 tag。每次浅克隆最新 main，记录提交、按源码生成包，使用 Codex marketplace list/remove/add 迁移同名旧来源（添加失败恢复旧来源），调用 `codex plugin add`，核对安装清单及全部文件 SHA256，再核对远端 main 未在更新期间变化。变化则要求重试。没有离线继续、TTL 或旧版本回退模式。

成功 JSON 中的 `skill` 与 `required_read` 是 Agent 下一步必须实际阅读的文件；不要继续使用旧会话已加载的文档。CLI 无法替模型完成阅读，也不能拦截绕过本插件的任意外部工具。正式 project.py 命令自动执行更新并在同一进程转交最新安装入口；Python 内部函数和 runtime 直调仅用于开发测试。

更新要求 Git、Python 3.10+、Codex CLI 与 GitHub 网络访问。源码包与锁放在 `$CODEX_HOME/whiteboard-updates`（默认 `~/.codex/whiteboard-updates`）；`last-success.json` 是历史证据，不能用来跳过下次联网。依赖缺失、断网、包或安装身份不符时命令非零退出，停止生产并修复相应错误后重新运行。不能直接修改安装缓存。

已有工程及其自定义 runtime 不被升级器覆盖。新工程复制最新模板并记录插件版本；旧工程若需要新的 runtime，应保留原工程，创建新工程迁移素材与输入并重新验证。包清单 `source_commit` 和逐文件哈希用于区分版本号相同但内容不同的情况。更新成功不代表风格、观看或听音验收通过。

## 整片制作检查

0.3.0整片需要production.json（完整句清单、最终旁白身份、品牌配音和逐句画面事件），并在presentation.json中设置production_path。批量制作前执行 `python3 scripts/check_presentation.py PROJECT/presentation.json --mode plan`；交付前执行 `--mode delivery`。缺清单、漏句、开场品牌提前、品牌配音不同步或缺实际听看记录时拒绝对应检查。完整格式和边界见 [制作检查](PRODUCTION-CHECK.md)。

## 0.4.0迁移

新整片执行production v2及 [全程落笔合同](../skills/whiteboard-video/harness/PEN-SEMANTICS-CANVAS.md)。已有v1须补实体参考、全元素笔触和canvas记录；既有视频/工程不会因更新插件自动合格。D01严格模式使用scene.pen，参考 [笔触程序](PEN-PROGRAM.md)。创建新工程或显式迁移新runtime后重新校验受影响窗口，不能仅改manifest版本。
