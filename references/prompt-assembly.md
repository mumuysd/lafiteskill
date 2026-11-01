# 组装契约 · 1.29.1

Character Plan 保留 role、facial_character、charm_contrast、character_silhouette、action_design、paw_prop_roles、posture、gaze、clothing_response、animal_traits、visible_character_hook。identity_anchors 写特征组合。未指定衣服时 clothing_options 至少两项；clothing_choice_reason 给可见理由。用户指定衣物/无衣用 clothing_override 记录依据。

composition_intent 保留 viewer_relationship、whole_picture_goal、reconstruction_plan、visibility_plan、background_plan。gaze_mode 必须与 viewer_relationship 一致。design_review.status 为 reviewed_as_design；传结构图时 structure_status 必须为 pass。

reference_inputs 每项有 path、sha256、role（identity/structure/quality）。CLI 的相对 path **以计划文件所在目录为基准**，可显式用 --reference-root 改变；Python assemble(..., base_dir=...) 对应同一约定。哈希必须匹配，不允许同一文件重复充当两个角色。真实宠物默认必需 identity；只有用户明确要求虚构动物才可 identity_waiver，不能因照片没存成本地文件就豁免。

脚本产生 referenced_image_paths 的本地文件请求草案，不支持自动识别对话图片、不上传、不连接服务。若用户只有对话附件，按当前工具的真实 schema 单独适配，记录实际图片窗口和职责；不能伪造本地 path/hash。无法排除无关图时先解决输入。

prompt 顺序：参考职责 → 可见人物关系与身份 → 动作/衣物 → 本幅形色空间 → 完整绘画指令一次 → 用户要求。--request、--trace 保存实际组装内容；调用时若改动，必须另存真正发送版本，不能用草案冒充实际请求。

5–8 块仅是可选构思辅助，无统一材质预算。每图说明脸、衣体、接触、背景的转面、明暗、边缘和方向笔怎样服务人物。自然结构、细毛和厚笔可成立，不靠统一表面纹理代替重构。
