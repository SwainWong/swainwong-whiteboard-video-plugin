# attention输入与检查

0.5.0整片production.json必须有attention对象，沿用production v2但旧清单须补字段。详细工作流见[注意力与独立评审](../skills/whiteboard-video/harness/ATTENTION-SEMANTIC-REVIEW.md)。

- `paint`: 每个需要上色的完整对象一条`{element_id,passes,start,end}`。passes为可见扫色遍数1–3，end-start<=1.5秒（含间歇）；无上色时显式空数组。不可按色层拆对象或漏登记。核对实际笔触程序与连续播放，机器只验证声明值。
- `shots`: 每个正文区域离开前的保持帧一条，含唯一`id`、`viewport:[width,height]`、`safe_rect:[x,y,width,height]`、`frame`文件身份和`subjects`数组。四周最少5%padding，UI保留区也须排除；safe_rect预先确定，不为凑比率缩小。
- `subjects`: `{element_id,rect:[x,y,width,height],focal:true/false}`，全部坐标为最终输出屏幕像素。只填语义主体紧占用框。检查框并集占有效区>=85%，主体不得越界，至少一个focal，focal短边>=有效区短边20%。连接线/背景/手/UI不计；必须对照帧审核框真实性及保持窗口，不能只登记一个合格镜头。
- `associations`: 每个narration target一条，含`target_id,literal_meaning,depiction,why_direct,likely_confusion,alternatives`，alternatives至少两个具体候选字符串。
- delivery时每条association新增`review`：`author_agent,reviewer_agent,blind_first:true,blind_guess,scores:[身份,动作关系,直接性,小尺寸],status:"PASS",small_preview_readable:true,evidence`。evidence为两轮原始评审消息文件身份，不是主Agent重写的结论；角色ID须不同。四项各>=4且合计>=17。
- review还需`narration_sha256`等于当前句清单文件哈希，`frames_sha256`为attention.shots的规范JSON哈希。全片review.json新增`attention_sha256`，绑定完整attention字段（含独立评审记录）。哈希算法统一`sha256(json.dumps(value,sort_keys=True,ensure_ascii=False).encode())`。

文件身份统一`{path:项目内相对路径,sha256:实际SHA256}`。plan验证框/计时/关联与预览文件，delivery额外检查独立评分记录；最终视频身份仍由原交付检查约束。脚本不提供模型识图服务，主制作Agent须实际调用独立子Agent，缺能力则保留未验收状态。
