"""Thin WorkBuddy discovery entry; production rules remain in the shared package."""
from pathlib import Path
import shlex
import shutil
import tempfile

MARKER='<!-- generated-whiteboard-workbuddy-entry-v1 -->'

def entry(updater):
    return '''---
name: whiteboard-video
description: 制作和修改白板讲解视频；包含逐句语义、插画布局、手绘动画、独立评审与可编辑Remotion工程。
---
'''+MARKER+f'''
# Whiteboard Video — WorkBuddy

这是共享插件的WorkBuddy加载入口，不是另一套制作规范。
将下面的本Skill目录占位替换成你实际读取的SKILL.md所在绝对目录（安装器生成的绝对路径无需替换）。每次开始或继续制作，先运行：

```sh
python3 {updater} --host workbuddy
```

必须等待命令成功，读取返回的skill及全部required_read；以返回plugin_root作为后续路径基准。
WorkBuddy后续正式命令使用 `python3 <plugin_root>/scripts/project.py --host workbuddy ...`。
更新失败停止制作，不调用Codex CLI，不使用此文件旁边的旧harness副本。
使用WorkBuddy当前实际提供的文件、终端、图像和独立子Agent工具，具体映射见返回的HOSTS.md。
缺图像生成或独立看图评审能力时报告缺口，不能伪造工具调用或审核PASS。
'''


def install(home, package, migrate=False):
    home=Path(home); target=home/'skills/whiteboard-video'; backup=None
    content=entry(shlex.quote(str(package/'scripts/update_latest.py')))
    if target.is_symlink():raise ValueError('WorkBuddy skill target is a symlink; refusing to overwrite')
    if target.exists() and not ((target/'SKILL.md').is_file() and MARKER in (target/'SKILL.md').read_text()):
        if not migrate:raise ValueError('Existing WorkBuddy skill is unmanaged; use --migrate-workbuddy once to preserve it in backups')
        backup_root=home/'whiteboard-updates/backups';backup_root.mkdir(parents=True,exist_ok=True)
        backup=Path(tempfile.mkdtemp(prefix='previous-skill-',dir=backup_root))/'whiteboard-video'
        shutil.move(str(target),str(backup))
    tmp=None
    try:
        target.mkdir(parents=True,exist_ok=True)
        with tempfile.NamedTemporaryFile(mode='w',encoding='utf-8',dir=target,delete=False) as stream:
            tmp=Path(stream.name)
            stream.write(content)
        tmp.replace(target/'SKILL.md')
        if (target/'SKILL.md').read_text()!=content:raise RuntimeError('WorkBuddy entry verification failed')
    except Exception:
        if tmp and tmp.exists():tmp.unlink()
        if backup:
            shutil.rmtree(target)
            shutil.move(str(backup),str(target))
        raise
    return {'entry':str(target/'SKILL.md'),'backup':str(backup) if backup else None}
