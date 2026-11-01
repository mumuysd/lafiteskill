---
name: lafiteskill
description: Create individual cat and dog characters as oil-painted pet portraits from real pet photos, ordinary human behavior and character-aware clothing. Use for “宠物油画”, “拉菲风格人物”, pet character redesign, or a scoped clothing/painting edit to an approved portrait. Keep identity, structure and visual-quality references separate. Requires an available image-generation tool. Do not use for human portraits, photo retouching, batch generation without a quantity, or exact copying of an existing artwork.
---

# Lafiteskill · 1.29.1

让真实动物拥有自己的生活。先看[认可视觉基准](references/approved-visual-reference.md)和实际图片，再为新主体设计。已有三张用户认可成图；[多主体样例](references/approved-examples.md)用于比较关系，仍不代表跨猫狗效果已经稳定。

1. **身份。** 查看用户照片，记录特征组合、未知项、允许重构与用户要求。眼/耳/颊/鼻口、毛色和体态共同识别个体；不按照片坐标复刻，也不把“越不像越好”当目标。
2. **人物。** 用[Character Grammar](references/character-grammar.md)设计脸、整体轮廓、动作、注意力和一个可见生活关系。检查连接、遮挡、接触与承重；不清楚就先改设计。可爱由具体关系产生，不强制大眼、短嘴、搞笑或两爪异任务。
3. **衣物。** 未指定时比较两套用途或轮廓不同的衣物，说明领袖、松量、下摆怎样参与体态、动作和毛色关系。用户指定或无衣优先；不默认冲浪衫、背心、旧衣、标志或厚袖。
4. **参考与组装。** 按[组装契约](references/prompt-assembly.md)填写计划。照片管 identity，可选草图管 structure，可选认可图管 quality。先核查当前工具能接收哪些参考；看过的图不等于已传入。用 scripts/assemble_character.py 保存精确 prompt、请求和 hash。脚本只组装，不调用、不上传；不支持的工具字段不得擅自转译。
5. **生成与编辑。** 冻结计划、版本、输入、prompt 和实际请求后，只完成本轮授权数量。工具失败保存错误后停止；不自动重试或追加绘画编辑。用户认可后指定局部修改时，明确保留关系与允许变化范围。
6. **验收。** 按[验收说明](references/acceptance.md)先整幅、再局部、再回整幅。分别记录结构检查、视觉判断、用户认可；关键 fail/uncertain 仍未通过。自然动物结构、细毛、密织或厚笔都不是单项通过/失败条件。交付实际文件路径与简短评审。

工具不可用时交付设计和请求草案并停止，不能声称已经生成。用户只授权研究/设计时保持零调用。脚本的离线通过不能证明新图的艺术质量。
