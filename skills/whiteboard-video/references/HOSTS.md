# Codex / WorkBuddy共享执行协议

制作规则只维护于同一插件包的Skill、harness、docs、runtime；宿主仅改变发现入口和工具调用。不允许给WorkBuddy删掉语义评审、布局配额或实际听看要求。

## 宿主选择和更新

- Codex：`python3 <plugin-root>/scripts/update_latest.py --host codex`；通过Codex marketplace安装。
- WorkBuddy：`python3 <plugin-root>/scripts/update_latest.py --host workbuddy`；不调用Codex CLI，保存GitHub提交对应的完整核验包，并生成本机WorkBuddy Skill入口。
- 两者每次都联网获取main，核对完整包清单/文件哈希以及更新结束时的远端提交。成功后重读skill和全部required_read，后续路径用返回plugin_root。
- `project.py --host codex|workbuddy init/check/render/capture-stage ...` 必须显式传当前宿主，--host位于子命令之前；也可在该进程设置WHITEBOARD_HOST。不能靠发现机器装有Codex就替WorkBuddy选择Codex。
- WorkBuddy默认home为~/.workbuddy，可用WORKBUDDY_HOME覆盖；Codex仍用CODEX_HOME。状态分别存放各home/whiteboard-updates，不交叉修改账户或启用设置。
- WorkBuddy入口在home/skills/whiteboard-video/SKILL.md，只负责更新和读取共享规范，不复制维护另一套harness。旧非托管安装首次使用--migrate-workbuddy，完整备份到home/whiteboard-updates/backups再替换；不删除其他技能。
- 已有工程runtime不自动迁移，记录其版本。启动了旧上下文的对话必须显式重读新入口。当前本地执行器以macOS/Linux为验证范围，不宣称Windows执行兼容。

## 工具映射：看能力，不照抄工具名称

| 工作 | 两边共同要求 |
|---|---|
| 文件/终端 | 使用宿主实际暴露的读写与终端工具执行同一Python/Node脚本，保留退出码和报告 |
| 资料检索 | 用可用搜索/浏览工具核实来源，不把另一个Agent的工具名写成已调用 |
| 生图/路径准备 | 使用项目选定且实际可用的模型/工具，传同一style packet、参考与约束；记录模型版本、prompt、seed（可用时）和资产哈希 |
| 图像审阅 | 用能实际看图的工具打开当前候选，不能仅读文件名或让文本模型猜内容 |
| 独立评审 | 建立无制作历史的新子Agent上下文，先图后口播两轮，保存实际Agent ID和原始回答。Codex可使用fork_turns=none；WorkBuddy使用当前提供的独立Agent/任务工具，不假设存在同名参数 |
| 视频/音频 | 使用能实际播放/听取的工具；缺能力则标NOT_CHECKED，不以ffprobe/静帧替代 |

缺独立Agent或图像能力时可以继续非依赖准备工作、导出待审候选，但不得伪造独立PASS或宣称最终交付通过。不能用主Agent换一个角色提示词冒充独立评审。

## 跨宿主一致性与实测边界

保持同一source_commit、style packet、参考资产、字体、模型选择、配音、最终时间线与runtime依赖。相同输入的确定性渲染与检查应一致；不同生成模型/随机性或工具能力下，不保证重新生图逐像素相同。若需要严格复现，复用已确认的资产/路径及配音，不让另一个宿主重新想象。

跨宿主验证先比较两个安装包全部源文件哈希，再对同一scene运行check/render并比较关键帧；全片仍分别记录正常速度视听、独立语义/美术评审和用户接受。安装成功、文件相同不等于WorkBuddy已完成整片生产。

## 资料依据

WorkBuddy官方[技能说明](https://www.codebuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Skills-Market)支持本地技能、技能包上传及自然语言调用；[自定义Skill说明](https://www.codebuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Practice-Cases/Practice-Eight)说明自定义技能入口。此适配使用本地Skill，不冒称CodeBuddy CLI插件安装等于WorkBuddy桌面安装。目录布局以本机已有WorkBuddy skills安装验证；其他发行版应使用生成的WorkBuddy ZIP在“上传技能”导入。
