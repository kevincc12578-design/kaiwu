"""
开物 v3.4 · 7 大高动效 UI/UX 网页与视频案例库 (motion_catalog.py)
基于实地核验的高水准交互网页与 60fps 演示视频：
  视频模态 (3):
    1. rauno_craft_video    : Rauno Craft Motion Lab (Slow Motion 0.25x · 径向菜单 · 精密缩放时间轴 · 探照灯标签)
    2. fps60_motion_video   : 60fps Physics Motion Gallery (Card Split · Swipe Stack · Scale Morph · 弹簧示波器)
    3. screen_studio_video  : Screen Studio Auto-Zoom Timeline (2.0x 自动运镜 · 阻尼光标 · 多轨时间轴 · 音频模式)
  网页模态 (4):
    4. resend_dev_web       : Resend Email Developer Console (Canvas 光束 · 多语言 SDK · HTTP 200 流式测试 · Webhook/Email 预览)
    5. linear_workspace_web : Linear Isometric Issue Workspace (等轴测拓扑描边 · 高密 Issue 台 · 交互 Code Diff 主题切换)
    6. raycast_cmd_web      : Raycast Command Palette & Keyboard (星空粒子 · 剪贴板命令面板 · 全键盘发光矩阵)
    7. amie_collab_web      : Amie Joyful AI Notes & Planner (47s 会议纪要渐显 · Ask Amie 悬浮胶囊 · 周日程矩阵)
"""
from __future__ import annotations

from typing import Any, Callable

import cases_catalog as base_cat
import skeleton_extractors as skel_base

MOTION_CASE_META: dict[str, dict[str, Any]] = {
    "rauno_craft_video": {
        "case_id": "rauno_craft_video",
        "title": "Rauno · Craft Motion Lab",
        "subtitle": "视频 → UI/UX",
        "modality": "video",
        "domain": "uiux",
        "template_id": "tpl_uiux_workspace_v1",
        "stage_url": "/cases/rauno_craft_video/app/index.html",
        "source_summary": "VIDEO · 4.800s · 慢动作微交互实验",
    },
    "fps60_motion_video": {
        "case_id": "fps60_motion_video",
        "title": "60fps · Physics Motion Gallery",
        "subtitle": "视频 → UI/UX",
        "modality": "video",
        "domain": "uiux",
        "template_id": "tpl_uiux_workspace_v1",
        "stage_url": "/cases/fps60_motion_video/app/index.html",
        "source_summary": "VIDEO · 4.400s · 弹簧分裂与共享变形",
    },
    "screen_studio_video": {
        "case_id": "screen_studio_video",
        "title": "Screen Studio · Auto-Zoom Timeline",
        "subtitle": "视频 → UI/UX",
        "modality": "video",
        "domain": "uiux",
        "template_id": "tpl_uiux_workspace_v1",
        "stage_url": "/cases/screen_studio_video/app/index.html",
        "source_summary": "VIDEO · 5.200s · 自动运镜与多轨编辑",
    },
    "resend_dev_web": {
        "case_id": "resend_dev_web",
        "title": "Resend · Email Developer Console",
        "subtitle": "网页 → UI/UX",
        "modality": "web",
        "domain": "uiux",
        "template_id": "tpl_uiux_workspace_v1",
        "stage_url": "/cases/resend_dev_web/app/index.html",
        "source_summary": "WEB · 390/768/1440px · 光束与流式 API",
    },
    "linear_workspace_web": {
        "case_id": "linear_workspace_web",
        "title": "Linear · Isometric Issue Workspace",
        "subtitle": "网页 → UI/UX",
        "modality": "web",
        "domain": "uiux",
        "template_id": "tpl_uiux_workspace_v1",
        "stage_url": "/cases/linear_workspace_web/app/index.html",
        "source_summary": "WEB · 390/768/1440px · 等轴测与 Diff 台",
    },
    "raycast_cmd_web": {
        "case_id": "raycast_cmd_web",
        "title": "Raycast · Command Palette & Keyboard",
        "subtitle": "网页 → UI/UX",
        "modality": "web",
        "domain": "uiux",
        "template_id": "tpl_uiux_workspace_v1",
        "stage_url": "/cases/raycast_cmd_web/app/index.html",
        "source_summary": "WEB · 390/768/1440px · 命令面板与键阵",
    },
    "amie_collab_web": {
        "case_id": "amie_collab_web",
        "title": "Amie · Joyful AI Notes & Planner",
        "subtitle": "网页 → UI/UX",
        "modality": "web",
        "domain": "uiux",
        "template_id": "tpl_uiux_workspace_v1",
        "stage_url": "/cases/amie_collab_web/app/index.html",
        "source_summary": "WEB · 390/768/1440px · AI 纪要与胶囊",
    },
    "nothing_dot_web": {
        "case_id": "nothing_dot_web",
        "title": "Nothing · Dot-Matrix OS HUD",
        "subtitle": "网页 → UI/UX",
        "modality": "web",
        "domain": "uiux",
        "template_id": "tpl_uiux_workspace_v1",
        "stage_url": "/cases/nothing_dot_web/app/index.html",
        "source_summary": "WEB · 390/768/1440px · 工业纯黑红点阵",
    },
    "poolsuite_os_web": {
        "case_id": "poolsuite_os_web",
        "title": "Poolsuite · 90s Retro Mac OS",
        "subtitle": "网页 → UI/UX",
        "modality": "web",
        "domain": "uiux",
        "template_id": "tpl_uiux_workspace_v1",
        "stage_url": "/cases/poolsuite_os_web/app/index.html",
        "source_summary": "WEB · 390/768/1440px · 复古拟物多窗桌面",
    },
    "daylight_eink_web": {
        "case_id": "daylight_eink_web",
        "title": "Daylight · Amber E-Ink Paper",
        "subtitle": "网页 → UI/UX",
        "modality": "web",
        "domain": "uiux",
        "template_id": "tpl_uiux_workspace_v1",
        "stage_url": "/cases/daylight_eink_web/app/index.html",
        "source_summary": "WEB · 390/768/1440px · 反射琥珀电子纸",
    },
    "family_fluid_web": {
        "case_id": "family_fluid_web",
        "title": "Family · Fluid Morphing Tray",
        "subtitle": "网页 → UI/UX",
        "modality": "web",
        "domain": "uiux",
        "template_id": "tpl_uiux_workspace_v1",
        "stage_url": "/cases/family_fluid_web/app/index.html",
        "source_summary": "WEB · 390/768/1440px · 纯白云朵变形抽屉",
    },
}

MOTION_DEFAULT_ASSUMPTIONS: dict[str, list[dict[str, Any]]] = {
    "rauno_craft_video": [
        {
            "assumption_id": "ASM-RN-01",
            "eu_id": "eu_L3_rn_motion_stage",
            "subject_ids": ["obs_rn_overshoot_transient", "eu_L3_rn_motion_stage"],
            "title": "径向菜单与时间轴刻度弹簧阻尼过冲瞬态峰值隔离",
            "category": "transient_motion_value",
            "assumed_value": "锁定稳态倍率 0.25x 慢动作与 8 扇区静态角度（45deg 步进），将回弹瞬间过冲帧隔离入假设台账",
            "evidence_gap": "原视频切换 Radial Menu 与 Adaptive Precision 瞬间存在 2 帧物理回弹过冲，未形成静止刻度真值",
            "bound_rule_id": "PV-03",
            "status": "open",
            "confirmed_at": None,
        },
        {
            "assumption_id": "ASM-RN-02",
            "eu_id": "eu_L3_rn_flashlight_array",
            "subject_ids": ["eu_L3_rn_flashlight_array", "eu_L4_rn_precision_ruler"],
            "title": "Adaptive Precision 垂直距离场与探照灯渐晕半径标定",
            "category": "motion_curve_parameter",
            "assumed_value": "以 120px 垂直指针映射区间与 260px 径向光晕半径重构 CSS/JS 连续插值曲线",
            "evidence_gap": "原视频录屏展示连续缩放与光斑边界效果，未暴露内部 JS 缓动贝塞尔拟合常数",
            "bound_rule_id": "PV-04",
            "status": "open",
            "confirmed_at": None,
        },
    ],
    "fps60_motion_video": [
        {
            "assumption_id": "ASM-FP-01",
            "eu_id": "eu_L3_fp_physics_stage",
            "subject_ids": ["obs_fp_overshoot_transient", "eu_L3_fp_physics_stage"],
            "title": "Swipe Card Stack 甩卡惯性速度与阻尼末帧隔离",
            "category": "transient_motion_value",
            "assumed_value": "采用可调 Stiffness=280 / Damping=24 稳态弹簧参数基准，不将拖拽释放瞬间角速度作为静帧真值",
            "evidence_gap": "60fps 视频展示卡片抛飞瞬间仍处减速插值阶段，末帧尚未完全静止落地",
            "bound_rule_id": "PV-03",
            "status": "open",
            "confirmed_at": None,
        },
        {
            "assumption_id": "ASM-FP-02",
            "eu_id": "eu_L3_fp_cards_array",
            "subject_ids": ["eu_L3_fp_cards_array"],
            "title": "Gumlet 原生 MP4 流体动画源的零外部脚本组件化替代",
            "category": "substitute_motion_asset",
            "assumed_value": "使用纯原生 ES6 二阶 RK4/Verlet 弹簧求解器与共享布局变形动画替代原站流媒体视频卡片",
            "evidence_gap": "原站卡片画廊依赖远程视频流播放展示 iOS 物理动效，离线工作台内重构为真实可手操交互组件",
            "bound_rule_id": "PV-02",
            "status": "open",
            "confirmed_at": None,
        },
    ],
    "screen_studio_video": [
        {
            "assumption_id": "ASM-SS-01",
            "eu_id": "eu_L3_ss_zoom_stage",
            "subject_ids": ["obs_ss_overshoot_transient", "eu_L3_ss_zoom_stage"],
            "title": "Auto-Zoom 2.0x 推镜瞬间光标速度滞后帧隔离",
            "category": "transient_motion_value",
            "assumed_value": "锁定稳态缩放倍率 2.00x 与 48kHz 音频采样基准，运动过程中的平滑过渡插值不冒充稳态坐标",
            "evidence_gap": "自动运镜推拉过程的中间插值帧呈持续位移，仅静止锁定态坐标可作稳定节点边界",
            "bound_rule_id": "PV-03",
            "status": "open",
            "confirmed_at": None,
        },
        {
            "assumption_id": "ASM-SS-02",
            "eu_id": "eu_L3_ss_timeline_array",
            "subject_ids": ["eu_L3_ss_timeline_array", "eu_L4_ss_zoom_filter"],
            "title": "多轨时间轴 Zoom 关键帧列表与音频模式导出表结构",
            "category": "unobserved_interaction_payload",
            "assumed_value": "构造确定性关键帧时间段、声波柱序列及可按音频/Zoom 模式过滤导出的 CSV 剪辑表",
            "evidence_gap": "产品演示视频展示时间轴外观与音频 Tab 切换，未公开内部工程 JSON/CSV 导出字段",
            "bound_rule_id": "GU-03",
            "status": "open",
            "confirmed_at": None,
        },
    ],
    "resend_dev_web": [
        {
            "assumption_id": "ASM-RS-01",
            "eu_id": "eu_L3_rs_console",
            "subject_ids": ["eu_L3_rs_console"],
            "title": "Test Mode 沙盒 HTTP 200 响应序列与 WebGL 光束离线替换",
            "category": "substitute_realtime_payload",
            "assumed_value": "使用本地 2D/WebGL 银灰光束 Canvas 粒子层与确定性 SMTP/REST 200 日志流替代远程后端沙盒",
            "evidence_gap": "参考页 Live Test Console 依赖线上 API Key 与远程着色器资产，离线台内以本地模拟响应闭环",
            "bound_rule_id": "PW-04",
            "status": "open",
            "confirmed_at": None,
        },
        {
            "assumption_id": "ASM-RS-02",
            "eu_id": "eu_L3_rs_webhooks_array",
            "subject_ids": ["eu_L3_rs_webhooks_array", "eu_L4_rs_filter_export"],
            "title": "Modular Webhooks 事件状态筛选与 CSV 审计导出字段",
            "category": "unobserved_interaction_payload",
            "assumed_value": "提供 delivered/bounced/opened 事件状态过滤并生成标准 Webhook 投递 CSV 明细",
            "evidence_gap": "官网展示实时滚动事件标签与双栏代码预览，未提供直接导出按钮的列格式定义",
            "bound_rule_id": "GU-03",
            "status": "open",
            "confirmed_at": None,
        },
    ],
    "linear_workspace_web": [
        {
            "assumption_id": "ASM-LN-01",
            "eu_id": "eu_L3_ln_issue_stage",
            "subject_ids": ["eu_L3_ln_issue_stage"],
            "title": "Linear 等轴测矢量拓扑脉冲节奏与仿真 Issue 集",
            "category": "substitute_motion_asset",
            "assumed_value": "采用纯矢量 SVG stroke-dashoffset 脉冲电流动画与 6 条可交互切换状态的研发 Issue 数据替代线上 GraphQL 库",
            "evidence_gap": "官网等轴测工作台为封装矢量序列与只读示例状态，离线工作台补齐状态流转闭环",
            "bound_rule_id": "PW-04",
            "status": "open",
            "confirmed_at": None,
        },
        {
            "assumption_id": "ASM-LN-02",
            "eu_id": "eu_L3_ln_diff_array",
            "subject_ids": ["eu_L3_ln_diff_array", "eu_L4_ln_filter_export"],
            "title": "Code Diff 主题配色组与冲刺状态筛选 CSV 口径",
            "category": "unobserved_interaction_payload",
            "assumed_value": "支持 Obsidian / Nord / Monochrome 三套代码语法配色实时切换与按 Backlog/In Progress 导出 CSV",
            "evidence_gap": "参考页 Code Diff 交互框支持主题下拉切换，未包含团队 Issue CSV 导出接口",
            "bound_rule_id": "GU-03",
            "status": "open",
            "confirmed_at": None,
        },
    ],
    "raycast_cmd_web": [
        {
            "assumption_id": "ASM-RY-01",
            "eu_id": "eu_L3_ry_palette_hud",
            "subject_ids": ["eu_L3_ry_palette_hud"],
            "title": "Clipboard History 离线指令索引与星空微粒参数化替代",
            "category": "substitute_background_asset",
            "assumed_value": "用轻量 Canvas 星空微粒与高对比 SVG/HEX 色卡、代码片段剪贴板条目实现命令面板实时检索",
            "evidence_gap": "Raycast 原生客户端与官网 WebGL 粒子依赖本地索引库，离线复刻以本地样本数组支撑 Cmd+K 搜索",
            "bound_rule_id": "PW-04",
            "status": "open",
            "confirmed_at": None,
        },
        {
            "assumption_id": "ASM-RY-02",
            "eu_id": "eu_L3_ry_extensions_array",
            "subject_ids": ["eu_L3_ry_extensions_array", "eu_L4_ry_filter_export"],
            "title": "全键位快捷键分类矩阵筛选与快捷键表 CSV 导出格式",
            "category": "unobserved_interaction_payload",
            "assumed_value": "支持按 Productivity / Engineering / Design / Writing 过滤扩展并导出对应键位映射 CSV",
            "evidence_gap": "官网按扩展类别展示快捷键卡片，未公开批量快捷键映射表下载文件",
            "bound_rule_id": "GU-03",
            "status": "open",
            "confirmed_at": None,
        },
    ],
    "amie_collab_web": [
        {
            "assumption_id": "ASM-AM-01",
            "eu_id": "eu_L3_am_notes_stage",
            "subject_ids": ["eu_L3_am_notes_stage"],
            "title": "47 秒 AI 会议纪要逐句渐显转写与本地 Ask Amie 对话响应",
            "category": "unobserved_interaction_payload",
            "assumed_value": "预置结构化会议发言逐句高亮时序，点击可将动作项转入周日程矩阵，Ask Amie 胶囊提供本地指令回复",
            "evidence_gap": "参考页展示 AI 会议总结逐句标亮动效与悬浮对话入口，未包含开放语音转写后端",
            "bound_rule_id": "PW-04",
            "status": "open",
            "confirmed_at": None,
        },
        {
            "assumption_id": "ASM-AM-02",
            "eu_id": "eu_L3_am_schedule_array",
            "subject_ids": ["eu_L3_am_schedule_array", "eu_L4_am_filter_export"],
            "title": "Amie 周日程排班视图过滤与 ICS/CSV 导出字段规范",
            "category": "unobserved_interaction_payload",
            "assumed_value": "按 Focus / Sync / Deep Work 标签筛选排期卡并实时计算当日协作工时导出 CSV",
            "evidence_gap": "产品官网演示卡片排版与 7 天上手阶段，未暴露完整日历同步接口数据结构",
            "bound_rule_id": "GU-03",
            "status": "open",
            "confirmed_at": None,
        },
    ],
    "nothing_dot_web": [
        {
            "assumption_id": "ASM-ND-01",
            "eu_id": "eu_L3_nd_matrix_hud",
            "subject_ids": ["eu_L3_nd_matrix_hud"],
            "title": "Nothing OS Ndot 点阵字体与 Glyph 脉冲灯环离线矢量仿真",
            "category": "substitute_motion_asset",
            "assumed_value": "以 SVG 5×7 LED 点阵矩阵、Glyph 12 节段环形开关与离线遥测序列重构工业控制 HUD",
            "evidence_gap": "真实手机端 Glyph 硬件总线与专有 Ndot 字体在无设备环境下采用纯本地 SVG 栅格等价实现",
            "bound_rule_id": "PW-04",
            "status": "open",
            "confirmed_at": None,
        },
        {
            "assumption_id": "ASM-ND-02",
            "eu_id": "eu_L3_nd_widgets_array",
            "subject_ids": ["eu_L3_nd_widgets_array", "eu_L4_nd_filter_export"],
            "title": "Nothing 微件阵列模式筛选与遥测日志 CSV 导出结构",
            "category": "unobserved_interaction_payload",
            "assumed_value": "支持按 SYSTEM / AUDIO / SENSOR 过滤点阵微件，并按当前激活模式导出标准化 CSV 日志",
            "evidence_gap": "桌面小组件规范未定义统一的 Web 端遥测导出 CSV 列字段",
            "bound_rule_id": "GU-03",
            "status": "open",
            "confirmed_at": None,
        },
    ],
    "poolsuite_os_web": [
        {
            "assumption_id": "ASM-PS-01",
            "eu_id": "eu_L3_ps_desktop_stage",
            "subject_ids": ["eu_L3_ps_desktop_stage"],
            "title": "Poolsuite FM 在线音频流与 Mac OS 9 主题调色板离线仿真",
            "category": "substitute_realtime_payload",
            "assumed_value": "使用纯本地 SVG 卡带双线波形频谱与 Malibu Peach / Tokyo Mint / Classic Platinum 实时 CSS Token 换肤",
            "evidence_gap": "原站依赖 SoundCloud/S3 远程电台流，离线工作台以本地确定性音轨队列及波形脉冲闭环",
            "bound_rule_id": "PW-04",
            "status": "open",
            "confirmed_at": None,
        },
        {
            "assumption_id": "ASM-PS-02",
            "eu_id": "eu_L3_ps_telemetry_array",
            "subject_ids": ["eu_L3_ps_telemetry_array", "eu_L4_ps_filter_export"],
            "title": "复古窗口收听统计筛选与歌单 CSV 归档格式",
            "category": "unobserved_interaction_payload",
            "assumed_value": "提供 Synthwave / Yacht / Lo-Fi 频道过滤并生成带 BPM 与播放次数的复古桌面 CSV",
            "evidence_gap": "参考站点偏重氛围播放窗交互，未提供结构化统计表下载接口",
            "bound_rule_id": "GU-03",
            "status": "open",
            "confirmed_at": None,
        },
    ],
    "daylight_eink_web": [
        {
            "assumption_id": "ASM-DL-01",
            "eu_id": "eu_L3_dl_topbar",
            "subject_ids": ["eu_L3_dl_topbar", "eu_L4_dl_amber_slider"],
            "title": "DC-1 反射式纸屏零蓝光琥珀背光光学曲线仿真",
            "category": "motion_curve_parameter",
            "assumed_value": "通过 0–100% Amber Backlight 滑块线性插值 #efe9dc 暖纸色至 #e5bc75 深夜琥珀背光表面",
            "evidence_gap": "硬件双背光 LED 的真实光谱衰减需要在普通 sRGB 显示器上以暖琥珀 CSS 表面颜色映射近似表达",
            "bound_rule_id": "PW-02",
            "status": "open",
            "confirmed_at": None,
        },
        {
            "assumption_id": "ASM-DL-02",
            "eu_id": "eu_L3_dl_notes_array",
            "subject_ids": ["eu_L3_dl_notes_array", "eu_L4_dl_filter_export"],
            "title": "Sol:OS 电子纸阅读批注筛选与专注工时 CSV 导出模型",
            "category": "unobserved_interaction_payload",
            "assumed_value": "支持按 Reading / Notes / Tasks 筛选纸面笔记条目并导出对应认知专注记录 CSV",
            "evidence_gap": "Daylight 官网重点展示无频闪阅读体验，未公布内置笔记库导出表结构",
            "bound_rule_id": "GU-03",
            "status": "open",
            "confirmed_at": None,
        },
    ],
    "family_fluid_web": [
        {
            "assumption_id": "ASM-FM-01",
            "eu_id": "eu_L3_fm_portfolio_stage",
            "subject_ids": ["eu_L3_fm_portfolio_stage", "eu_L4_fm_morph_tray"],
            "title": "Family Contextual Morphing Tray 弹性贝塞尔变形物理与本地链上沙盒",
            "category": "motion_curve_parameter",
            "assumed_value": "使用 cubic-bezier(.22,1,.36,1) / 340ms 连续高度形变抽屉与确定性 L2 Gas/组合估值替代 RPC 节点",
            "evidence_gap": "iOS 原生 SwiftUI matchedGeometry 阻尼参数及实时链上钱包余额无法在离线浏览器静态直连",
            "bound_rule_id": "PW-04",
            "status": "open",
            "confirmed_at": None,
        },
        {
            "assumption_id": "ASM-FM-02",
            "eu_id": "eu_L3_fm_tx_array",
            "subject_ids": ["eu_L3_fm_tx_array", "eu_L4_fm_filter_export"],
            "title": "多链资产流向筛选与交易收据 CSV 审计结构",
            "category": "unobserved_interaction_payload",
            "assumed_value": "支持按 Send / Swap / Yield 过滤历史签章记录，并将变形抽屉新提交的交易追加导出为 CSV",
            "evidence_gap": "Family 动效文章聚焦卡片抽屉物理衔接，未定义桌面端批量账单导出格式",
            "bound_rule_id": "GU-03",
            "status": "open",
            "confirmed_at": None,
        },
    ],
}


# ==============================================================================
# 一、3 个视频模态高动效案例的统一参数化构建器 (PV-01..04 + GN-01..04 + GU-01..04)
# ==============================================================================
_VIDEO_MOTION_SPECS: dict[str, dict[str, Any]] = {
    "rauno_craft_video": {
        "prefix": "rn",
        "full_bleed": True,
        "keep_filter_edge": False,
        "duration_sec": 4.800,
        "root_name": "Rauno · Craft 微动效实验室",
        "default_seg_frame": "/cases/rauno_craft_video/frames/seg_01.png",
        "rail_w": 0,
        "obs_assumption_id": "ASM-RN-01",
        "transient_obs_id": "obs_rn_overshoot_transient",
        "steady_obs": [
            ("obs_rn_slowmo_025", "eu_L3_rn_topbar", "慢动作速度倍率", "0.25x", 28),
            ("obs_rn_radial_8", "eu_L3_rn_motion_stage", "Radial Menu 扇区数", "8 sectors", 36),
        ],
        "invariant": ("inv_rn_radial_center", "0.25x 与 1.0x 模式切换下 Radial Menu 极坐标圆心偏移恒为 0", 1.15, 2.35),
        "registry": {
            "surface_atoms": {
                "rn_surf_bg": {"name": "深邃石墨实验室基底", "kind": "color", "value": "#0b0b0c", "css_var": "--rn-bg"},
                "rn_surf_panel": {"name": "微对比卡片玻璃面", "kind": "color", "value": "#141416", "css_var": "--rn-panel"},
                "rn_surf_line": {"name": "细腻半透描边", "kind": "color", "value": "#27272a", "css_var": "--rn-line"},
                "rn_surf_ink": {"name": "高纯象牙白主文字", "kind": "color", "value": "#f4f4f5", "css_var": "--rn-ink"},
                "rn_surf_amber": {"name": "交互刻度琥珀高光", "kind": "color", "value": "#f59e0b", "css_var": "--rn-amber"},
            },
            "typography_atoms": {
                "rn_typo_h1": {"name": "实验宣言衬线字阶", "kind": "font_scale", "value": "clamp(26px, 2.8vw, 38px)", "css_var": "--rn-font-h1"},
                "rn_typo_mono": {"name": "时间轴刻度等宽字阶", "kind": "font_scale", "value": "12px", "css_var": "--rn-font-mono"},
                "rn_typo_body": {"name": "说明正文字阶", "kind": "font_scale", "value": "14px", "css_var": "--rn-font-body"},
            },
            "layout_atoms": {
                "rn_lay_radius": {"name": "实验卡圆角", "kind": "radius", "value": "14px", "css_var": "--rn-radius"},
                "rn_lay_gap": {"name": "卡片排布间距", "kind": "spacing", "value": "16px", "css_var": "--rn-gap"},
            },
            "motion_atoms": {
                "rn_mot_spring": {"name": "弹性插值基准时长", "kind": "duration", "value": "280ms", "css_var": "--rn-dur-spring"},
                "rn_mot_slow": {"name": "慢动作全局时间因子", "kind": "scale", "value": "1", "css_var": "--rn-slow-scale"},
            },
            "evidence_atoms": {
                "ev_rn_video": {"name": "Rauno Craft 4.800s 四段关键帧抽帧证据", "frame_ref": "seg_01.png", "evidence_bbox": [0, 0, 1920, 1200]},
            },
        },
        "nodes": {
            "topbar_id": "eu_L3_rn_topbar",
            "topbar_name": "Craft 顶栏与 Toggle Slow Motion 0.25x 开关",
            "topbar_feat_id": "eu_L4_rn_slowmo_ctrl",
            "topbar_feat_name": "全局物理动效 1.0x / 0.25x 速率切换特征",
            "hero_id": "eu_L3_rn_motion_stage",
            "hero_name": "Radial Menu 极坐标扇形与 Adaptive Precision 时间轴舞台",
            "hero_feat_id": "eu_L4_rn_precision_ruler",
            "hero_feat_name": "垂直指针距离缩放 15m/5m/1m 动态刻度特征",
            "array_id": "eu_L3_rn_flashlight_array",
            "array_name": "Flashlight Tabs 探照灯微交互实验四卡阵列",
            "array_count": 4,
            "dialog_id": "eu_L3_rn_inspector_dialog",
            "dialog_name": "物理曲线参数检查器弹窗",
        },
        "segments": [
            {
                "segment_id": "seg_01",
                "index": 1,
                "t0": 0.00,
                "t1": 1.15,
                "label": "0.00–1.15s · Slow Motion 速率基准与顶栏进入",
                "frame_url": "/cases/rauno_craft_video/frames/seg_01.png",
                "active_eu_ids": ["eu_L3_rn_topbar", "eu_L4_rn_slowmo_ctrl", "eu_L3_rn_motion_stage"],
                "bboxes": [
                    {"bbox_id": "bb_rn_s1_top", "eu_id": "eu_L3_rn_topbar", "label": "Toggle Slow Motion (0.25x) 顶栏", "x": 16, "y": 16, "w": 1408, "h": 76, "role": "nav"},
                    {"bbox_id": "bb_rn_s1_stage", "eu_id": "eu_L3_rn_motion_stage", "label": "微交互实验主舞台进入", "x": 16, "y": 108, "w": 1408, "h": 510, "role": "split"},
                ],
            },
            {
                "segment_id": "seg_02",
                "index": 2,
                "t0": 1.15,
                "t1": 2.35,
                "label": "1.15–2.35s · Radial Menu 极坐标扇形弹出",
                "frame_url": "/cases/rauno_craft_video/frames/seg_02.png",
                "active_eu_ids": ["eu_L3_rn_motion_stage", "eu_L4_rn_precision_ruler"],
                "bboxes": [
                    {"bbox_id": "bb_rn_s2_rad", "eu_id": "eu_L3_rn_motion_stage", "label": "8 扇区 Radial Menu 极坐标展开", "x": 16, "y": 108, "w": 692, "h": 510, "role": "split"},
                    {"bbox_id": "bb_rn_s2_prec", "eu_id": "eu_L4_rn_precision_ruler", "label": "Adaptive Precision 右侧时间轴", "x": 732, "y": 108, "w": 692, "h": 510, "role": "stage"},
                ],
            },
            {
                "segment_id": "seg_03",
                "index": 3,
                "t0": 2.35,
                "t1": 3.60,
                "label": "2.35–3.60s · Adaptive Precision 垂直距离放大",
                "frame_url": "/cases/rauno_craft_video/frames/seg_03.png",
                "active_eu_ids": ["eu_L3_rn_motion_stage", "eu_L4_rn_precision_ruler"],
                "bboxes": [
                    {"bbox_id": "bb_rn_s3_prec", "eu_id": "eu_L4_rn_precision_ruler", "label": "垂直指针距离动态切换 15m→5m→1m 刻度", "x": 732, "y": 108, "w": 692, "h": 510, "role": "split"},
                ],
            },
            {
                "segment_id": "seg_04",
                "index": 4,
                "t0": 3.60,
                "t1": 4.80,
                "label": "3.60–4.80s · Flashlight 探照灯四卡阵列与瞬态隔离",
                "frame_url": "/cases/rauno_craft_video/frames/seg_04.png",
                "active_eu_ids": ["eu_L3_rn_flashlight_array", "eu_L3_rn_inspector_dialog"],
                "bboxes": [
                    {"bbox_id": "bb_rn_s4_arr", "eu_id": "eu_L3_rn_flashlight_array", "label": "Flashlight 探照灯微交互卡片阵列 ×4", "x": 16, "y": 636, "w": 1408, "h": 248, "role": "array"},
                ],
            },
        ],
    },
    "fps60_motion_video": {
        "prefix": "fp",
        "full_bleed": True,
        "keep_filter_edge": False,
        "duration_sec": 4.400,
        "root_name": "60fps · 物理动效画廊",
        "default_seg_frame": "/cases/fps60_motion_video/frames/seg_01.png",
        "rail_w": 0,
        "obs_assumption_id": "ASM-FP-01",
        "transient_obs_id": "obs_fp_overshoot_transient",
        "steady_obs": [
            ("obs_fp_rate_60", "eu_L3_fp_topbar", "物理求解刷新率", "60fps", 30),
            ("obs_fp_stack_3", "eu_L3_fp_physics_stage", "甩卡堆叠层数", "3 cards", 24),
        ],
        "invariant": ("inv_fp_spring_energy", "Card Split 与 Scale Morph 变形前后总盒重心守恒", 1.10, 2.15),
        "registry": {
            "surface_atoms": {
                "fp_surf_bg": {"name": "超净哑光黑画廊底色", "kind": "color", "value": "#090a0d", "css_var": "--fp-bg"},
                "fp_surf_card": {"name": "玻璃质感动效框底色", "kind": "color", "value": "#13151b", "css_var": "--fp-card"},
                "fp_surf_border": {"name": "柔和冷灰微描边", "kind": "color", "value": "#242834", "css_var": "--fp-border"},
                "fp_surf_ink": {"name": "亮银白主标题字色", "kind": "color", "value": "#f6f7f9", "css_var": "--fp-ink"},
                "fp_surf_blue": {"name": "60fps 电光蓝强调色", "kind": "color", "value": "#3b82f6", "css_var": "--fp-blue"},
            },
            "typography_atoms": {
                "fp_typo_display": {"name": "物理画廊主标题字阶", "kind": "font_scale", "value": "clamp(28px, 3vw, 42px)", "css_var": "--fp-font-display"},
                "fp_typo_mono": {"name": "物理参数示波等宽体", "kind": "font_scale", "value": "12px", "css_var": "--fp-font-mono"},
                "fp_typo_body": {"name": "案例简介字阶", "kind": "font_scale", "value": "13.5px", "css_var": "--fp-font-body"},
            },
            "layout_atoms": {
                "fp_lay_radius": {"name": "物理卡片圆角", "kind": "radius", "value": "18px", "css_var": "--fp-radius"},
                "fp_lay_gap": {"name": "画廊网格间距", "kind": "spacing", "value": "18px", "css_var": "--fp-gap"},
            },
            "motion_atoms": {
                "fp_mot_split": {"name": "卡片分裂弹性周期", "kind": "duration", "value": "380ms", "css_var": "--fp-dur-split"},
                "fp_mot_morph": {"name": "共享元素变形周期", "kind": "duration", "value": "420ms", "css_var": "--fp-dur-morph"},
            },
            "evidence_atoms": {
                "ev_fp_video": {"name": "60fps Gallery 4.400s 物理动效四段抽帧证据", "frame_ref": "seg_01.png", "evidence_bbox": [0, 0, 1920, 1200]},
            },
        },
        "nodes": {
            "topbar_id": "eu_L3_fp_topbar",
            "topbar_name": "60fps 标签筛选带与 Spring/Morph 模式切换",
            "topbar_feat_id": "eu_L4_fp_tag_switcher",
            "topbar_feat_name": "Spring Physics / Shared Element / Morph 胶囊路由",
            "hero_id": "eu_L3_fp_physics_stage",
            "hero_name": "Card Split · Swipe Stack · Scale Morph 三合一物理交互舞台",
            "hero_feat_id": "eu_L4_fp_spring_solver",
            "hero_feat_name": "可调 Stiffness/Damping 弹簧示波与共享变形特征",
            "array_id": "eu_L3_fp_cards_array",
            "array_name": "2,150+ Shots 同构高帧率物理动效参数阵列 ×4",
            "array_count": 4,
            "dialog_id": "eu_L3_fp_tuning_dialog",
            "dialog_name": "弹簧刚度阻尼曲线导出弹窗",
        },
        "segments": [
            {
                "segment_id": "seg_01",
                "index": 1,
                "t0": 0.00,
                "t1": 1.10,
                "label": "0.00–1.10s · 60fps 物理动效顶栏与参数示波",
                "frame_url": "/cases/fps60_motion_video/frames/seg_01.png",
                "active_eu_ids": ["eu_L3_fp_topbar", "eu_L3_fp_physics_stage"],
                "bboxes": [
                    {"bbox_id": "bb_fp_s1_top", "eu_id": "eu_L3_fp_topbar", "label": "60fps 标签筛选胶囊顶栏", "x": 16, "y": 16, "w": 1408, "h": 76, "role": "nav"},
                    {"bbox_id": "bb_fp_s1_stage", "eu_id": "eu_L3_fp_physics_stage", "label": "三大物理交互舞台总览", "x": 16, "y": 108, "w": 1408, "h": 510, "role": "split"},
                ],
            },
            {
                "segment_id": "seg_02",
                "index": 2,
                "t0": 1.10,
                "t1": 2.15,
                "label": "1.10–2.15s · Airbnb Card Split 卡片分裂展开",
                "frame_url": "/cases/fps60_motion_video/frames/seg_02.png",
                "active_eu_ids": ["eu_L3_fp_physics_stage", "eu_L4_fp_spring_solver"],
                "bboxes": [
                    {"bbox_id": "bb_fp_s2_split", "eu_id": "eu_L3_fp_physics_stage", "label": "Card Split 双翼弹性分裂展开", "x": 16, "y": 108, "w": 470, "h": 510, "role": "split"},
                ],
            },
            {
                "segment_id": "seg_03",
                "index": 3,
                "t0": 2.15,
                "t1": 3.25,
                "label": "2.15–3.25s · Swipe Stack 惯性拖拽与 Scale Morph 变形",
                "frame_url": "/cases/fps60_motion_video/frames/seg_03.png",
                "active_eu_ids": ["eu_L3_fp_physics_stage", "eu_L4_fp_spring_solver"],
                "bboxes": [
                    {"bbox_id": "bb_fp_s3_morph", "eu_id": "eu_L4_fp_spring_solver", "label": "Scale Morph 共享布局与 Stiffness/Damping 示波", "x": 496, "y": 108, "w": 928, "h": 510, "role": "split"},
                ],
            },
            {
                "segment_id": "seg_04",
                "index": 4,
                "t0": 3.25,
                "t1": 4.40,
                "label": "3.25–4.40s · Shots 参数阵列与甩卡过冲隔离",
                "frame_url": "/cases/fps60_motion_video/frames/seg_04.png",
                "active_eu_ids": ["eu_L3_fp_cards_array", "eu_L3_fp_tuning_dialog"],
                "bboxes": [
                    {"bbox_id": "bb_fp_s4_arr", "eu_id": "eu_L3_fp_cards_array", "label": "物理标签对比指标阵列 ×4", "x": 16, "y": 636, "w": 1408, "h": 248, "role": "array"},
                ],
            },
        ],
    },
    "screen_studio_video": {
        "prefix": "ss",
        "full_bleed": False,
        "keep_filter_edge": True,
        "duration_sec": 5.200,
        "root_name": "Screen Studio · 自动运镜时间轴工作台",
        "default_seg_frame": "/cases/screen_studio_video/frames/seg_01.png",
        "rail_w": 76,
        "obs_assumption_id": "ASM-SS-01",
        "transient_obs_id": "obs_ss_overshoot_transient",
        "steady_obs": [
            ("obs_ss_zoom_2x", "eu_L3_ss_zoom_stage", "Auto-Zoom 稳态放大倍率", "2.00x", 40),
            ("obs_ss_audio_khz", "eu_L3_ss_timeline_array", "Podcast Audio 采样率", "48kHz", 44),
        ],
        "invariant": ("inv_ss_rail_fixed", "主舞台多轨编辑区独立下滚时左侧工具导轨位移恒为 0", 1.25, 2.60),
        "registry": {
            "surface_atoms": {
                "ss_surf_bg": {"name": "深紫macOS渐变工作台底", "kind": "color", "value": "#0e0b1a", "css_var": "--ss-bg"},
                "ss_surf_glass": {"name": "深烟灰半透轨道面板", "kind": "color", "value": "#19152b", "css_var": "--ss-glass"},
                "ss_surf_purple": {"name": "Studio 霓虹紫强调色", "kind": "color", "value": "#8b5cf6", "css_var": "--ss-purple"},
                "ss_surf_teal": {"name": "音频轨道青绿波形色", "kind": "color", "value": "#14b8a6", "css_var": "--ss-teal"},
                "ss_surf_ink": {"name": "高对比冷白字体色", "kind": "color", "value": "#f5f3ff", "css_var": "--ss-ink"},
            },
            "typography_atoms": {
                "ss_typo_h1": {"name": "工作台工程标题字阶", "kind": "font_scale", "value": "clamp(20px, 2vw, 28px)", "css_var": "--ss-font-h1"},
                "ss_typo_mono": {"name": "时间码与倍率等宽字阶", "kind": "font_scale", "value": "12px", "css_var": "--ss-font-mono"},
                "ss_typo_body": {"name": "控制条与标签字阶", "kind": "font_scale", "value": "13px", "css_var": "--ss-font-body"},
            },
            "layout_atoms": {
                "ss_lay_rail": {"name": "左侧轨道导轨定宽", "kind": "dimension", "value": "76px", "css_var": "--ss-rail-w"},
                "ss_lay_radius": {"name": "画布与片段胶囊圆角", "kind": "radius", "value": "16px", "css_var": "--ss-radius"},
                "ss_lay_gap": {"name": "时间轴多轨间距", "kind": "spacing", "value": "14px", "css_var": "--ss-gap"},
            },
            "motion_atoms": {
                "ss_mot_zoom": {"name": "2.0x 自动运镜缓动周期", "kind": "duration", "value": "460ms", "css_var": "--ss-dur-zoom"},
                "ss_mot_cursor": {"name": "光标平滑阻尼延迟", "kind": "duration", "value": "180ms", "css_var": "--ss-dur-cursor"},
            },
            "evidence_atoms": {
                "ev_ss_video": {"name": "Screen Studio 5.200s 四段关键帧抽帧证据", "frame_ref": "seg_01.png", "evidence_bbox": [0, 0, 1920, 1200]},
            },
        },
        "nodes": {
            "nav_name": "左侧录屏轨道工具导轨 (邻近放大)",
            "nav_kind": "component.proximity_dock",
            "topbar_id": "eu_L3_ss_topbar",
            "topbar_name": "Screen Studio 模式顶栏与 Auto-Zoom 播放控制",
            "topbar_feat_id": "eu_L4_ss_mode_switch",
            "topbar_feat_name": "Recording / Editing / Cursor & Camera / Sharing 切换",
            "hero_id": "eu_L3_ss_zoom_stage",
            "hero_name": "2.0x Auto-Zoom 自动运镜舞台、阻尼光标与 PiP 画中画",
            "hero_feat_id": "eu_L4_ss_autozoom_camera",
            "hero_feat_name": "点击热点触发 2.0x 弹簧居中聚焦变换",
            "array_id": "eu_L3_ss_timeline_array",
            "array_name": "Video / Zoom Keyframes / Audio 多轨时间轴与导出 ×3",
            "array_count": 3,
            "dialog_id": "eu_L3_ss_export_dialog",
            "dialog_name": "4K 60fps 视频与剪辑表导出弹窗",
        },
        "segments": [
            {
                "segment_id": "seg_01",
                "index": 1,
                "t0": 0.00,
                "t1": 1.25,
                "label": "0.00–1.25s · 渐变画布舞台与多模式顶栏",
                "frame_url": "/cases/screen_studio_video/frames/seg_01.png",
                "active_eu_ids": ["eu_L1_ss_nav", "eu_L3_ss_topbar", "eu_L3_ss_zoom_stage"],
                "bboxes": [
                    {"bbox_id": "bb_ss_s1_rail", "eu_id": "eu_L3_ss_rail_dock", "label": "左侧轨道工具导轨", "x": 16, "y": 16, "w": 76, "h": 868, "role": "nav"},
                    {"bbox_id": "bb_ss_s1_top", "eu_id": "eu_L3_ss_topbar", "label": "Recording / Editing 模式顶栏", "x": 108, "y": 16, "w": 1316, "h": 84, "role": "stage"},
                    {"bbox_id": "bb_ss_s1_stage", "eu_id": "eu_L3_ss_zoom_stage", "label": "渐变画布与 PiP 录屏区", "x": 108, "y": 116, "w": 1316, "h": 510, "role": "split"},
                ],
            },
            {
                "segment_id": "seg_02",
                "index": 2,
                "t0": 1.25,
                "t1": 2.60,
                "label": "1.25–2.60s · 左侧轨道工具导轨指针邻近放大",
                "frame_url": "/cases/screen_studio_video/frames/seg_02.png",
                "active_eu_ids": ["eu_L3_ss_rail_dock", "eu_L4_ss_rail_proximity"],
                "bboxes": [
                    {"bbox_id": "bb_ss_s2_prox", "eu_id": "eu_L3_ss_rail_dock", "label": "工具导轨鼠标邻近缩放 (1.35x)", "x": 16, "y": 16, "w": 96, "h": 868, "role": "split"},
                ],
            },
            {
                "segment_id": "seg_03",
                "index": 3,
                "t0": 2.60,
                "t1": 3.95,
                "label": "2.60–3.95s · 2.0x Auto-Zoom 自动运镜聚焦",
                "frame_url": "/cases/screen_studio_video/frames/seg_03.png",
                "active_eu_ids": ["eu_L3_ss_zoom_stage", "eu_L4_ss_autozoom_camera"],
                "bboxes": [
                    {"bbox_id": "bb_ss_s3_zoom", "eu_id": "eu_L3_ss_zoom_stage", "label": "2.0x Auto-Zoom 平滑聚焦靶区 + 光标轨迹", "x": 108, "y": 116, "w": 1316, "h": 510, "role": "split"},
                ],
            },
            {
                "segment_id": "seg_04",
                "index": 4,
                "t0": 3.95,
                "t1": 5.20,
                "label": "3.95–5.20s · 多轨时间轴缩放条与音频模式过滤",
                "frame_url": "/cases/screen_studio_video/frames/seg_04.png",
                "active_eu_ids": ["eu_L3_ss_timeline_array", "eu_L4_ss_filter_export", "eu_L3_ss_export_dialog"],
                "bboxes": [
                    {"bbox_id": "bb_ss_s4_tl", "eu_id": "eu_L3_ss_timeline_array", "label": "Video / Zoom / Audio 三轨时间轴 + CSV 导出", "x": 108, "y": 642, "w": 1316, "h": 242, "role": "array"},
                ],
            },
        ],
    },
}


def _render_motion_video_skeleton_svg(
    case_id: str,
    spec: dict[str, Any],
) -> str:
    segments = spec["segments"]
    duration_sec = float(spec["duration_sec"])
    is_full = bool(spec.get("full_bleed", True))
    rail_w = int(spec.get("rail_w", 0))
    stage_x = 16 if is_full else (16 + rail_w + 16)
    bg_url = spec["default_seg_frame"]

    parts: list[str] = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1440 956" width="100%" height="100%" data-modality="video">',
        "  <defs>",
        "    <style>",
        "      .sk-box { cursor: pointer; transition: stroke-width 0.16s, fill-opacity 0.16s; }",
        '      .sk-box:hover, .sk-box[data-active="true"] { stroke-width: 4px !important; fill-opacity: 0.28 !important; }',
        '      .sk-tag { font-family: Manrope, "Segoe UI", sans-serif; font-size: 13px; font-weight: 700; pointer-events: none; }',
        "      .sk-seg { cursor: pointer; }",
        "    </style>",
        "  </defs>",
        '  <rect x="0" y="0" width="1440" height="956" rx="14" fill="#0d0d10"/>',
        f'  <image id="skeleton-bg-frame" href="{base_cat._escape_xml(bg_url)}" x="0" y="0" width="1440" height="900" preserveAspectRatio="xMidYMid slice" opacity="0.90"/>',
        '  <g data-layer="skeleton" opacity="0.56">',
        f'    <rect x="{stage_x}" y="14" width="{1440 - stage_x - 16}" height="872" rx="16" fill="none" stroke="#f4f4f5" stroke-width="1.5" stroke-dasharray="6 4"/>',
    ]
    if not is_full:
        parts.append(f'    <line x1="{stage_x - 8}" y1="14" x2="{stage_x - 8}" y2="886" stroke="#0ea5e9" stroke-width="1.6" stroke-dasharray="5 5"/>')
    parts.append("  </g>")
    parts.append('  <g data-layer="bbox">')
    for seg in segments:
        sid = seg["segment_id"]
        op = "1" if sid == "seg_01" else "0.22"
        parts.append(f'    <g class="sk-segment-group" data-segment-id="{sid}" opacity="{op}">')
        for b in seg["bboxes"]:
            stroke, fill = skel_base.ROLE_COLORS.get(b["role"], ("#0ea5e9", "rgba(14,165,233,0.13)"))
            x, y, w, h = b["x"], b["y"], b["w"], b["h"]
            eu_id = b["eu_id"]
            lbl = base_cat._escape_xml(b["label"])
            tag_w = min(w, max(124, len(b["label"]) * 12 + 18))
            tag_y = max(4, y + 4)
            parts.append(
                f'      <g class="sk-node" data-eu-id="{eu_id}" data-segment-id="{sid}" data-bbox-id="{b["bbox_id"]}">'
                f'<rect class="sk-box" data-eu-id="{eu_id}" data-segment-id="{sid}" x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="{fill}" stroke="{stroke}" stroke-width="2.4"/>'
                f'<rect x="{x + 4}" y="{tag_y}" width="{tag_w}" height="22" rx="6" fill="{stroke}" fill-opacity="0.92"/>'
                f'<text class="sk-tag" x="{x + 11}" y="{tag_y + 15}" fill="#ffffff">{lbl}</text>'
                "</g>"
            )
        parts.append("    </g>")
    parts.append("  </g>")
    parts.append('  <g data-layer="timeline" transform="translate(16, 908)">')
    bar_w = 1408.0
    seg_palette = ["#8b5cf6", "#f97316", "#0ea5e9", "#10b981"]
    for idx, seg in enumerate(segments):
        x0 = round((seg["t0"] / duration_sec) * bar_w, 2)
        w0 = round(((seg["t1"] - seg["t0"]) / duration_sec) * bar_w, 2)
        col = seg_palette[idx % len(seg_palette)]
        short_lbl = base_cat._escape_xml(f'S{idx + 1} {seg["t0"]:.2f}-{seg["t1"]:.2f}s')
        eu_anchor = seg["active_eu_ids"][0]
        parts.append(
            f'    <g class="sk-seg" data-segment-id="{seg["segment_id"]}" data-eu-id="{eu_anchor}">'
            f'<rect x="{x0}" y="0" width="{max(4.0, w0 - 2)}" height="36" rx="7" fill="{col}" fill-opacity="0.88" stroke="#f4f4f5" stroke-width="1"/>'
            f'<text class="sk-tag" x="{x0 + 8}" y="23" fill="#ffffff" style="font-size:12px">{short_lbl}</text>'
            "</g>"
        )
    parts.append("  </g>")
    parts.append("</svg>")
    return "\n".join(parts)


def _build_motion_video_skeleton(case_id: str) -> dict[str, Any]:
    spec = _VIDEO_MOTION_SPECS[case_id]
    p = spec["prefix"]
    dur = float(spec["duration_sec"])
    segs = spec["segments"]
    all_bboxes: list[dict[str, Any]] = []
    for seg in segs:
        for b in seg["bboxes"]:
            item = dict(b)
            item["segment_id"] = seg["segment_id"]
            item["color_role"] = b["role"]
            all_bboxes.append(item)

    covered = sum(round(s["t1"] - s["t0"], 6) for s in segs)
    obs_list: list[dict[str, Any]] = [
        {
            "id": oid,
            "eu_id": eu_id,
            "label": lbl,
            "value": val,
            "settle_state": "steady",
            "stable_frames": sf,
            "verified": True,
        }
        for oid, eu_id, lbl, val, sf in spec["steady_obs"]
    ]
    obs_list.append(
        {
            "id": spec["transient_obs_id"],
            "eu_id": spec["nodes"]["hero_id"],
            "label": "动效插值过冲末帧瞬态值",
            "value": "spring_overshoot_unsettled",
            "settle_state": "transient",
            "stable_frames": 0,
            "verified": False,
            "assumption_id": spec["obs_assumption_id"],
        }
    )

    inv_id, inv_desc, inv_t0, inv_t1 = spec["invariant"]
    return {
        "case_id": case_id,
        "modality": "video",
        "fps": 60.0,
        "duration_sec": dur,
        "coverage_ratio": round(covered / dur, 6),
        "viewport": {
            "width": 1440,
            "height": 900,
            "raw_video_size": [1920, 1600],
            "crop_bbox": [0, 0, 1920, 1200],
            "scale": 0.75,
        },
        "viewport_transform": {
            "source_size": {"w": 1920, "h": 1600},
            "crop_rect": {"x": 0, "y": 0, "w": 1920, "h": 1200},
            "scale": 0.75,
            "target_size": {"w": 1440, "h": 900},
        },
        "noise_regions": [
            {
                "id": f"nr_{p}_overlay_bar",
                "kind": "platform_overlay",
                "bbox": [0, 1280, 1920, 320],
                "desc": "录屏外围平台播放器控件及外框噪声带",
            }
        ],
        "observations": obs_list,
        "frame_invariants": [
            {
                "id": inv_id,
                "desc": inv_desc,
                "holds": True,
                "evidence": {
                    "t0": inv_t0,
                    "t1": inv_t1,
                    "frame_bbox": [24, 24, 1872, 1140],
                },
            }
        ],
        "segments": segs,
        "bboxes": all_bboxes,
        "skeleton_svg": _render_motion_video_skeleton_svg(case_id, spec),
    }


def _build_motion_video_eu_tree(case_id: str, finalize_fn: Callable[..., dict[str, Any]]) -> dict[str, Any]:
    spec = _VIDEO_MOTION_SPECS[case_id]
    p = spec["prefix"]
    is_full = bool(spec.get("full_bleed", True))
    keep_filter = bool(spec.get("keep_filter_edge", False))
    rail_w = int(spec.get("rail_w", 0))
    stage_x = 16 if is_full else (16 + rail_w + 16)
    stage_w = 1440 - stage_x - 16 if is_full else (1440 - stage_x - 16)
    dur = float(spec["duration_sec"])
    reg = spec["registry"]
    ev_id = f"ev_{p}_video"
    surf_ids = list(reg["surface_atoms"].keys())
    typo_ids = list(reg["typography_atoms"].keys())
    lay_ids = list(reg["layout_atoms"].keys())
    mot_ids = list(reg["motion_atoms"].keys())
    all_atoms = surf_ids + typo_ids + lay_ids + mot_ids + [ev_id]
    base_atoms = [surf_ids[0], typo_ids[0], lay_ids[0], ev_id]

    nm = spec["nodes"]
    root_id = f"eu_L0_{p}_workspace"
    rail_dock_id = f"eu_L3_{p}_rail_dock"
    rail_prox_id = f"eu_L4_{p}_rail_proximity"
    stage_l1_id = f"eu_L1_{p}_stage"
    nav_l1_id = f"eu_L1_{p}_nav"

    nodes: list[dict[str, Any]] = [
        {"eu_id": root_id, "name": spec["root_name"], "level": "L0", "node_kind": "product.workspace", "parent_id": None, "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [0, 0, 1440, 900], "frame_bbox": [0, 0, 1920, 1200], "time_range": [0.0, dur], "segment_ids": ["seg_01", "seg_02", "seg_03", "seg_04"], "rendered": True},

        {"eu_id": f"eu_L1_{p}_intro", "name": "无障碍跳转与片头域", "level": "L1", "node_kind": "territory.intro_shell", "parent_id": root_id, "template_slot": "intro_shell", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [16, 8, 1404, 34], "frame_bbox": [24, 12, 1872, 44], "time_range": [0.0, 1.15]},
        {"eu_id": f"eu_L2_{p}_intro_bar", "name": "顶部快捷跳转条", "level": "L2", "node_kind": "region.intro_strip", "parent_id": f"eu_L1_{p}_intro", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [16, 8, 1404, 34]},
        {"eu_id": f"eu_L3_{p}_skip_entry", "name": "跳过导航快捷按钮", "level": "L3", "entity": True, "node_kind": "component.skip_button", "parent_id": f"eu_L2_{p}_intro_bar", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [16, 8, 180, 34], "dom_selector": f'[data-eu-id="eu_L3_{p}_skip_entry"]', "rendered": True},
        {"eu_id": f"eu_L4_{p}_skip_feat", "name": "键盘焦点直达特征", "level": "L4", "node_kind": "feature.skip_a11y", "parent_id": f"eu_L3_{p}_skip_entry", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [16, 8, 180, 34]},
        {"eu_id": f"eu_L5_{p}_skip_atoms", "name": "入口基础原子束", "level": "L5", "node_kind": "atom.bundle", "parent_id": f"eu_L4_{p}_skip_feat", "adaptation_mode": "ATOMIC_MOUNT", "atom_refs": base_atoms},
    ]

    if not is_full:
        nodes.extend([
            {"eu_id": nav_l1_id, "name": "左侧轨道导轨领地", "level": "L1", "node_kind": "territory.nav_dock", "parent_id": root_id, "template_slot": "nav_dock", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [16, 16, rail_w, 868], "frame_bbox": [22, 22, 102, 1156], "time_range": [0.0, dur], "segment_ids": ["seg_01", "seg_02"], "rendered": True},
            {"eu_id": f"eu_L2_{p}_nav_rail", "name": "左侧独立交互导轨区", "level": "L2", "node_kind": "region.nav_rail", "parent_id": nav_l1_id, "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [16, 16, rail_w, 868]},
            {"eu_id": rail_dock_id, "name": nm["nav_name"], "level": "L3", "entity": True, "interaction_density": 3, "node_kind": nm["nav_kind"], "parent_id": f"eu_L2_{p}_nav_rail", "adaptation_mode": "SPLIT_HIGH_INTERACTION", "envelope_bbox": [16, 16, rail_w, 868], "dom_selector": f'[data-eu-id="{rail_dock_id}"]', "rendered": True},
            {"eu_id": rail_prox_id, "name": "指针邻近放大与浮签特征", "level": "L4", "motion": True, "node_kind": "feature.proximity_magnify", "parent_id": rail_dock_id, "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [16, 16, rail_w, 640], "rendered": True},
            {"eu_id": f"eu_L5_{p}_rail_atoms", "name": "导轨动效原子束", "level": "L5", "node_kind": "atom.bundle", "parent_id": rail_prox_id, "adaptation_mode": "ATOMIC_MOUNT", "atom_refs": all_atoms},
        ])

    filter_feat_id = f"eu_L4_{p}_filter_export" if keep_filter else f"eu_L4_{p}_array_feat"
    filter_feat_name = "多轨筛选与剪辑表 CSV 导出" if keep_filter else "同构实验卡片矩阵特征"

    nodes.extend([
        {"eu_id": stage_l1_id, "name": "全宽主舞台领地" if is_full else "独立滚动主舞台领地", "level": "L1", "node_kind": "territory.main_stage", "parent_id": root_id, "template_slot": "main_stage", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [stage_x, 16, stage_w, 868], "frame_bbox": [stage_x, 22, 1872 if is_full else 1750, 1156], "time_range": [0.0, dur], "segment_ids": ["seg_01", "seg_02", "seg_03", "seg_04"], "rendered": True},
        {"eu_id": f"eu_L2_{p}_topbar", "name": "顶栏模式切换带", "level": "L2", "node_kind": "region.topbar", "parent_id": stage_l1_id, "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [stage_x, 16, stage_w, 88]},
        {"eu_id": nm["topbar_id"], "name": nm["topbar_name"], "level": "L3", "entity": True, "node_kind": "component.stage_topbar", "parent_id": f"eu_L2_{p}_topbar", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [stage_x, 16, stage_w, 88], "dom_selector": f'[data-eu-id="{nm["topbar_id"]}"]', "rendered": True},
        {"eu_id": nm["topbar_feat_id"], "name": nm["topbar_feat_name"], "level": "L4", "motion": True, "node_kind": "feature.route_switch", "parent_id": nm["topbar_id"], "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [stage_x, 16, stage_w, 88], "rendered": True},
        {"eu_id": f"eu_L5_{p}_top_atoms", "name": "顶栏与动效原子束", "level": "L5", "node_kind": "atom.bundle", "parent_id": nm["topbar_feat_id"], "adaptation_mode": "ATOMIC_MOUNT", "atom_refs": all_atoms},

        {"eu_id": f"eu_L2_{p}_hero_zone", "name": "高密物理动效交互主展区", "level": "L2", "node_kind": "region.hero_stage", "parent_id": stage_l1_id, "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [stage_x, 108, stage_w, 514]},
        {"eu_id": nm["hero_id"], "name": nm["hero_name"], "level": "L3", "entity": True, "interaction_density": 4, "node_kind": "component.primary_interactive", "parent_id": f"eu_L2_{p}_hero_zone", "adaptation_mode": "SPLIT_HIGH_INTERACTION", "envelope_bbox": [stage_x, 108, stage_w, 514], "dom_selector": f'[data-eu-id="{nm["hero_id"]}"]', "rendered": True},
        {"eu_id": nm["hero_feat_id"], "name": nm["hero_feat_name"], "level": "L4", "motion": True, "node_kind": "feature.primary_control", "parent_id": nm["hero_id"], "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [stage_x, 108, stage_w, 514], "rendered": True},
        {"eu_id": f"eu_L5_{p}_hero_atoms", "name": "物理动效核心原子束", "level": "L5", "node_kind": "atom.bundle", "parent_id": nm["hero_feat_id"], "adaptation_mode": "ATOMIC_MOUNT", "atom_refs": all_atoms},

        {"eu_id": f"eu_L2_{p}_array_zone", "name": "下方结构化实验阵列带", "level": "L2", "node_kind": "region.lower_array", "parent_id": stage_l1_id, "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [stage_x, 636, stage_w, 248]},
        {"eu_id": nm["array_id"], "name": nm["array_name"], "level": "L3", "entity": True, "node_kind": "component.spec.array", "parent_id": f"eu_L2_{p}_array_zone", "adaptation_mode": "FOLD_ARRAY", "array_count": int(nm["array_count"]), "envelope_bbox": [stage_x, 636, stage_w, 248], "dom_selector": f'[data-eu-id="{nm["array_id"]}"]', "rendered": True},
        {"eu_id": filter_feat_id, "name": filter_feat_name, "level": "L4", "node_kind": "feature.array_grid", "parent_id": nm["array_id"], "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [stage_x, 636, stage_w, 248], "rendered": True},
        {"eu_id": f"eu_L5_{p}_array_atoms", "name": "阵列基础原子束", "level": "L5", "node_kind": "atom.bundle", "parent_id": filter_feat_id, "adaptation_mode": "ATOMIC_MOUNT", "atom_refs": base_atoms},

        {"eu_id": f"eu_L1_{p}_overlay", "name": "参数检查浮层领地", "level": "L1", "node_kind": "territory.auxiliary_overlay", "parent_id": root_id, "template_slot": "auxiliary_overlay", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [420, 170, 580, 410]},
        {"eu_id": f"eu_L2_{p}_dialog_host", "name": "对话框宿主区", "level": "L2", "node_kind": "region.dialog", "parent_id": f"eu_L1_{p}_overlay", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [420, 170, 580, 410]},
        {"eu_id": nm["dialog_id"], "name": nm["dialog_name"], "level": "L3", "entity": True, "node_kind": "component.modal_sheet", "parent_id": f"eu_L2_{p}_dialog_host", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [420, 170, 580, 410], "dom_selector": f'[data-eu-id="{nm["dialog_id"]}"]', "rendered": True},
        {"eu_id": f"eu_L4_{p}_focus_trap", "name": "关闭弹窗归还触发焦点特征", "level": "L4", "node_kind": "feature.modal_focus_restore", "parent_id": nm["dialog_id"], "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [420, 170, 580, 410]},
        {"eu_id": f"eu_L5_{p}_dialog_atoms", "name": "弹窗原子束", "level": "L5", "node_kind": "atom.bundle", "parent_id": f"eu_L4_{p}_focus_trap", "adaptation_mode": "ATOMIC_MOUNT", "atom_refs": base_atoms},
    ])

    edges: list[dict[str, Any]] = [
        {
            "edge_id": f"edge_{p}_state",
            "edge_type": "TRIGGERS_STATE",
            "source_eu_id": nm["topbar_id"],
            "target_eu_id": nm["hero_id"],
            "label": "顶栏速率/模式开关切换主舞台动效演练状态",
            "source": "observed",
            "evidence_ref": ev_id,
            "evidence": {"t0": 0.0, "t1": 1.15, "frame_bbox": [48, 24, 1824, 1140]},
        },
        {
            "edge_id": f"edge_{p}_focus",
            "edge_type": "RESTORES_FOCUS",
            "source_eu_id": nm["dialog_id"],
            "target_eu_id": nm["topbar_id"],
            "label": "参数检查对话框关闭后精准归还触发控件焦点",
            "source": "inferred_realized",
            "evidence_ref": ev_id,
            "evidence": {"t0": 3.25, "t1": dur, "frame_bbox": [420, 170, 580, 410]},
        },
        {
            "edge_id": f"edge_{p}_token",
            "edge_type": "SHARES_TOKEN",
            "source_eu_id": nm["hero_id"],
            "target_eu_id": nm["array_id"],
            "label": "动效主展区与下方矩阵共享暗房表面色及动效时长 Token",
            "source": "observed",
            "evidence_ref": ev_id,
            "evidence": {"t0": 2.35, "t1": dur, "frame_bbox": [48, 24, 1824, 1140]},
        },
    ]
    if not is_full:
        edges.extend([
            {
                "edge_id": f"edge_{p}_proximity",
                "edge_type": "MODULATES_NEIGHBOR",
                "source_eu_id": rail_dock_id,
                "target_eu_id": rail_prox_id,
                "label": "左侧轨道导轨指针距离邻近放大 (1.35x) 与离开复位",
                "source": "observed",
                "evidence_ref": ev_id,
                "evidence": {"t0": 1.25, "t1": 2.60, "frame_bbox": [24, 24, 140, 1140]},
            },
            {
                "edge_id": f"edge_{p}_scroll",
                "edge_type": "SCROLLS_INDEPENDENTLY",
                "source_eu_id": stage_l1_id,
                "target_eu_id": nav_l1_id,
                "label": "主舞台独立纵向滚动时左侧导轨位移恒为 0",
                "source": "observed",
                "evidence_ref": ev_id,
                "evidence": {"t0": 2.60, "t1": 3.95, "frame_bbox": [132, 24, 1740, 1140]},
            },
        ])
    if keep_filter:
        edges.append(
            {
                "edge_id": f"edge_{p}_filter",
                "edge_type": "FILTERS_VIEW",
                "source_eu_id": nm["hero_id"],
                "target_eu_id": nm["array_id"],
                "label": "轨道模式筛选联动时间轴片段及同口径 CSV 导出",
                "source": "inferred_realized",
                "evidence_ref": ev_id,
                "evidence": {"t0": 3.95, "t1": dur, "frame_bbox": [132, 820, 1740, 340]},
            }
        )
    return finalize_fn("tpl_uiux_workspace_v1", "UI/UX 工作台原型", root_id, nodes, reg, edges)


# ==============================================================================
# 二、4 个网页模态高交互案例的参数化规格 (PW-01..04 + GN-01..04 + GU-01..04)
# ==============================================================================
_WEB_MOTION_SPECS: dict[str, dict[str, Any]] = {
    "resend_dev_web": {
        "prefix": "rs",
        "full_bleed": True,
        "keep_filter_edge": True,
        "root_name": "Resend · 开发者邮件平台与实时测试控制台",
        "frame_url": "/cases/resend_dev_web/frames/ref_rs_desktop.png",
        "data_source": "resend.telemetry.emails",
        "rail_w": 0,
        "panel_radius": 12,
        "registry": {
            "surface_atoms": {
                "rs_surf_bg": {"name": "纯黑开发者基础设施基底", "kind": "color", "value": "#000000", "css_var": "--rs-bg"},
                "rs_surf_card": {"name": "半透暗玻璃代码台", "kind": "color", "value": "#0a0a0c", "css_var": "--rs-card"},
                "rs_surf_line": {"name": "1px 暗银轮廓线", "kind": "color", "value": "#1f2026", "css_var": "--rs-line"},
                "rs_surf_emerald": {"name": "HTTP 200 成功翡翠信号", "kind": "color", "value": "#10b981", "css_var": "--rs-emerald"},
                "rs_surf_ink": {"name": "高对比冷白字体色", "kind": "color", "value": "#ededef", "css_var": "--rs-ink"},
            },
            "typography_atoms": {
                "rs_typo_h1": {"name": "Resend Hero 标题字阶", "kind": "font_scale", "value": "clamp(32px, 3.8vw, 52px)", "css_var": "--rs-font-h1"},
                "rs_typo_code": {"name": "SDK 与 JSON 响应等宽字阶", "kind": "font_scale", "value": "12.5px", "css_var": "--rs-font-code"},
                "rs_typo_body": {"name": "说明文案正文字阶", "kind": "font_scale", "value": "14px", "css_var": "--rs-font-body"},
            },
            "layout_atoms": {
                "rs_lay_maxw": {"name": "平台内容最大宽", "kind": "dimension", "value": "1180px", "css_var": "--rs-maxw"},
                "rs_lay_radius": {"name": "控制台圆角", "kind": "radius", "value": "12px", "css_var": "--rs-radius"},
                "rs_lay_gap": {"name": "网格基准间距", "kind": "spacing", "value": "16px", "css_var": "--rs-gap"},
            },
            "motion_atoms": {
                "rs_mot_beam": {"name": "光束扫描微动效时长", "kind": "duration", "value": "240ms", "css_var": "--rs-dur-beam"},
            },
            "evidence_atoms": {
                "ev_rs_dom": {"name": "Resend 三断点与 Test Mode 控制台快照", "breakpoints": [390, 768, 1440], "frame_ref": "ref_rs_desktop.png"},
            },
        },
        "nodes": {
            "topbar_id": "eu_L3_rs_topbar",
            "topbar_name": "Resend 极简顶栏与多页面路由切换",
            "topbar_feat_id": "eu_L4_rs_route_tabs",
            "topbar_feat_name": "Test Mode / Webhooks / React Email 路由胶囊",
            "hero_id": "eu_L3_rs_console",
            "hero_name": "WebGL 暗银光束 + 多语言 SDK + Send Test 200 流式台",
            "hero_feat_id": "eu_L4_rs_stream_send",
            "hero_feat_name": "SDK 滑块弹簧切换与实时 HTTP 200 JSON 注入",
            "array_id": "eu_L3_rs_webhooks_array",
            "array_name": "Webhook 事件流 + React Email 双栏预览阵列 ×4",
            "array_count": 4,
            "dialog_id": "eu_L3_rs_api_dialog",
            "dialog_name": "API Key 沙盒权限生成弹窗",
        },
        "bboxes": [
            {"bbox_id": "bb_rs_top", "eu_id": "eu_L3_rs_topbar", "label": "Resend 全宽顶栏与路由入口", "x": 16, "y": 16, "w": 1408, "h": 72, "role": "nav"},
            {"bbox_id": "bb_rs_hero", "eu_id": "eu_L3_rs_console", "label": "光束 Hero + 多语言 SDK + Send Test 流式台", "x": 16, "y": 100, "w": 1408, "h": 510, "role": "split"},
            {"bbox_id": "bb_rs_arr", "eu_id": "eu_L3_rs_webhooks_array", "label": "Webhook 状态过滤 + React Email 双栏 ×4", "x": 16, "y": 626, "w": 1408, "h": 258, "role": "array"},
        ],
    },
    "linear_workspace_web": {
        "prefix": "ln",
        "full_bleed": False,
        "keep_filter_edge": True,
        "root_name": "Linear · 等轴测研发工作台与 Code Diff 引擎",
        "frame_url": "/cases/linear_workspace_web/frames/ref_ln_desktop.png",
        "data_source": "linear.workspace.issues",
        "rail_w": 78,
        "panel_radius": 10,
        "registry": {
            "surface_atoms": {
                "ln_surf_void": {"name": "曜石深邃暗黑基底", "kind": "color", "value": "#08090a", "css_var": "--ln-bg"},
                "ln_surf_panel": {"name": "哑光石板组件面", "kind": "color", "value": "#101216", "css_var": "--ln-panel"},
                "ln_surf_line": {"name": "1px 金属质感分隔线", "kind": "color", "value": "#20232b", "css_var": "--ln-line"},
                "ln_surf_indigo": {"name": "Linear 靛蓝交互高亮色", "kind": "color", "value": "#5e6ad2", "css_var": "--ln-indigo"},
                "ln_surf_ink": {"name": "极高对比白灰主字色", "kind": "color", "value": "#f7f8f8", "css_var": "--ln-ink"},
            },
            "typography_atoms": {
                "ln_typo_h1": {"name": "研发看板大标题字阶", "kind": "font_scale", "value": "clamp(26px, 3vw, 38px)", "css_var": "--ln-font-h1"},
                "ln_typo_code": {"name": "Issue ID 与 Diff 等宽字阶", "kind": "font_scale", "value": "12px", "css_var": "--ln-font-code"},
                "ln_typo_body": {"name": "工作台标签字阶", "kind": "font_scale", "value": "13.5px", "css_var": "--ln-font-body"},
            },
            "layout_atoms": {
                "ln_lay_rail": {"name": "细窄左侧导轨定宽", "kind": "dimension", "value": "78px", "css_var": "--ln-rail-w"},
                "ln_lay_radius": {"name": "精密微圆角", "kind": "radius", "value": "10px", "css_var": "--ln-radius"},
                "ln_lay_gap": {"name": "模块间距", "kind": "spacing", "value": "14px", "css_var": "--ln-gap"},
            },
            "motion_atoms": {
                "ln_mot_snap": {"name": "零拖沓弹簧展开时长", "kind": "duration", "value": "160ms", "css_var": "--ln-dur-snap"},
                "ln_mot_dash": {"name": "等轴测电流描边周期", "kind": "duration", "value": "2400ms", "css_var": "--ln-dur-dash"},
            },
            "evidence_atoms": {
                "ev_ln_dom": {"name": "Linear 三断点与等轴测 Diff 工作台快照", "breakpoints": [390, 768, 1440], "frame_ref": "ref_ln_desktop.png"},
            },
        },
        "nodes": {
            "nav_name": "左侧高对比细窄工作区导轨 (邻近放大)",
            "nav_kind": "component.proximity_dock",
            "topbar_id": "eu_L3_ln_topbar",
            "topbar_name": "Cycle 42 顶栏、Linear Agent 开关与 New Issue",
            "topbar_feat_id": "eu_L4_ln_route_switch",
            "topbar_feat_name": "Issues / Isometric / Code Diff 视图跃迁",
            "hero_id": "eu_L3_ln_issue_stage",
            "hero_name": "等轴测矢量拓扑脉冲画布 + 可状态流转 Issue 列表",
            "hero_feat_id": "eu_L4_ln_isometric_svg",
            "hero_feat_name": "SVG 等轴测电流脉冲描边与 Issue 行点击切换",
            "array_id": "eu_L3_ln_diff_array",
            "array_name": "多主题 Code Diff 实时面板与状态筛选导出 ×3",
            "array_count": 3,
            "dialog_id": "eu_L3_ln_issue_dialog",
            "dialog_name": "快捷键创建 Issue 模态表单",
        },
        "bboxes": [
            {"bbox_id": "bb_ln_nav", "eu_id": "eu_L3_ln_rail_dock", "label": "细窄导轨 (邻近放大)", "x": 16, "y": 16, "w": 78, "h": 868, "role": "nav"},
            {"bbox_id": "bb_ln_top", "eu_id": "eu_L3_ln_topbar", "label": "Cycle 42 顶栏与视图切换", "x": 110, "y": 16, "w": 1310, "h": 82, "role": "stage"},
            {"bbox_id": "bb_ln_hero", "eu_id": "eu_L3_ln_issue_stage", "label": "等轴测脉冲拓扑 + Issue 工作区", "x": 110, "y": 114, "w": 1310, "h": 496, "role": "split"},
            {"bbox_id": "bb_ln_diff", "eu_id": "eu_L3_ln_diff_array", "label": "Code Diff 主题切换与 CSV 导出 ×3", "x": 110, "y": 626, "w": 1310, "h": 258, "role": "array"},
        ],
    },
    "raycast_cmd_web": {
        "prefix": "ry",
        "full_bleed": True,
        "keep_filter_edge": True,
        "root_name": "Raycast · 命令面板与全键盘快捷键矩阵",
        "frame_url": "/cases/raycast_cmd_web/frames/ref_ry_desktop.png",
        "data_source": "raycast.commands.shortcuts",
        "rail_w": 0,
        "panel_radius": 14,
        "registry": {
            "surface_atoms": {
                "ry_surf_bg": {"name": "夜空渐变暗黑基底", "kind": "color", "value": "#070709", "css_var": "--ry-bg"},
                "ry_surf_hud": {"name": "玻璃态命令面板底面", "kind": "color", "value": "#121318", "css_var": "--ry-hud"},
                "ry_surf_line": {"name": "微弱冷白高光边框", "kind": "color", "value": "#27272e", "css_var": "--ry-line"},
                "ry_surf_flame": {"name": "Raycast 炽红光晕强调色", "kind": "color", "value": "#ff6363", "css_var": "--ry-flame"},
                "ry_surf_ink": {"name": "纯白命令聚焦字色", "kind": "color", "value": "#f4f4f6", "css_var": "--ry-ink"},
            },
            "typography_atoms": {
                "ry_typo_h1": {"name": "Raycast 宣言字阶", "kind": "font_scale", "value": "clamp(30px, 3.6vw, 48px)", "css_var": "--ry-font-h1"},
                "ry_typo_kbd": {"name": "按键帽等宽标识字阶", "kind": "font_scale", "value": "12px", "css_var": "--ry-font-kbd"},
                "ry_typo_body": {"name": "剪贴板描述正文字阶", "kind": "font_scale", "value": "13.5px", "css_var": "--ry-font-body"},
            },
            "layout_atoms": {
                "ry_lay_hudw": {"name": "命令面板版心最大宽", "kind": "dimension", "value": "1160px", "css_var": "--ry-hud-w"},
                "ry_lay_radius": {"name": "键帽与 HUD 圆角", "kind": "radius", "value": "14px", "css_var": "--ry-radius"},
                "ry_lay_gap": {"name": "键盘与卡片间距", "kind": "spacing", "value": "14px", "css_var": "--ry-gap"},
            },
            "motion_atoms": {
                "ry_mot_key": {"name": "发光键帽按压回弹时长", "kind": "duration", "value": "140ms", "css_var": "--ry-dur-key"},
            },
            "evidence_atoms": {
                "ev_ry_dom": {"name": "Raycast 三断点、命令面板与全键盘阵列快照", "breakpoints": [390, 768, 1440], "frame_ref": "ref_ry_desktop.png"},
            },
        },
        "nodes": {
            "topbar_id": "eu_L3_ry_topbar",
            "topbar_name": "Raycast 全宽顶栏与 Quicklinks/Commands 切换",
            "topbar_feat_id": "eu_L4_ry_nav_tabs",
            "topbar_feat_name": "Clipboard History / Keyboard Matrix 模式胶囊",
            "hero_id": "eu_L3_ry_palette_hud",
            "hero_name": "粒子星空背景 + Clipboard 命令面板 + 发光虚拟键阵",
            "hero_feat_id": "eu_L4_ry_key_glow",
            "hero_feat_name": "实时搜索聚焦滑动框与真实键盘按键/点击点亮联动",
            "array_id": "eu_L3_ry_extensions_array",
            "array_name": "Productivity / Engineering / Design / Writing 扩展与导出 ×4",
            "array_count": 4,
            "dialog_id": "eu_L3_ry_shortcut_dialog",
            "dialog_name": "自定义全局热键绑定弹窗",
        },
        "bboxes": [
            {"bbox_id": "bb_ry_top", "eu_id": "eu_L3_ry_topbar", "label": "Raycast 顶栏与模式入口", "x": 16, "y": 16, "w": 1408, "h": 72, "role": "nav"},
            {"bbox_id": "bb_ry_hero", "eu_id": "eu_L3_ry_palette_hud", "label": "Clipboard 命令面板 + 发光全键盘矩阵", "x": 16, "y": 100, "w": 1408, "h": 510, "role": "split"},
            {"bbox_id": "bb_ry_arr", "eu_id": "eu_L3_ry_extensions_array", "label": "Raycast 扩展分类阵列 ×4 + CSV 导出", "x": 16, "y": 626, "w": 1408, "h": 258, "role": "array"},
        ],
    },
    "amie_collab_web": {
        "prefix": "am",
        "full_bleed": False,
        "keep_filter_edge": True,
        "root_name": "Amie · 明快 AI 会议纪要与协作日程",
        "frame_url": "/cases/amie_collab_web/frames/ref_am_desktop.png",
        "data_source": "amie.notes.schedule",
        "rail_w": 76,
        "panel_radius": 16,
        "registry": {
            "surface_atoms": {
                "am_surf_paper": {"name": "明快纯净纸白基底", "kind": "color", "value": "#fcfcfd", "css_var": "--am-bg"},
                "am_surf_tint": {"name": "柔和云雾浅灰卡片面", "kind": "color", "value": "#f3f4f8", "css_var": "--am-tint"},
                "am_surf_border": {"name": "细腻发丝灰边框", "kind": "color", "value": "#e4e6ef", "css_var": "--am-border"},
                "am_surf_coral": {"name": "Joyful 草莓红交互点缀", "kind": "color", "value": "#f43f5e", "css_var": "--am-coral"},
                "am_surf_ink": {"name": "深炭黑高清晰正文色", "kind": "color", "value": "#111827", "css_var": "--am-ink"},
            },
            "typography_atoms": {
                "am_typo_h1": {"name": "Amie 圆润声明标题字阶", "kind": "font_scale", "value": "clamp(28px, 3vw, 40px)", "css_var": "--am-font-h1"},
                "am_typo_mono": {"name": "47s 纪要时间标签字阶", "kind": "font_scale", "value": "12px", "css_var": "--am-font-mono"},
                "am_typo_body": {"name": "会议纪要正文字阶", "kind": "font_scale", "value": "14px", "css_var": "--am-font-body"},
            },
            "layout_atoms": {
                "am_lay_rail": {"name": "左侧轻量日程导轨定宽", "kind": "dimension", "value": "76px", "css_var": "--am-rail-w"},
                "am_lay_radius": {"name": "Joyful 胶囊与大圆角", "kind": "radius", "value": "16px", "css_var": "--am-radius"},
                "am_lay_gap": {"name": "卡片节奏间距", "kind": "spacing", "value": "16px", "css_var": "--am-gap"},
            },
            "motion_atoms": {
                "am_mot_pill": {"name": "Ask Amie 胶囊弹簧展开时长", "kind": "duration", "value": "240ms", "css_var": "--am-dur-pill"},
            },
            "evidence_atoms": {
                "ev_am_dom": {"name": "Amie 三断点与 AI Notes/Planner 快照", "breakpoints": [390, 768, 1440], "frame_ref": "ref_am_desktop.png"},
            },
        },
        "nodes": {
            "nav_name": "左侧轻量日程导轨 (邻近放大)",
            "nav_kind": "component.proximity_dock",
            "topbar_id": "eu_L3_am_topbar",
            "topbar_name": "Amie 顶部导航与 Notes/Planner 切页条",
            "topbar_feat_id": "eu_L4_am_route_pills",
            "topbar_feat_name": "AI Notes / Week Grid / Ask Capsule 状态跃迁",
            "hero_id": "eu_L3_am_notes_stage",
            "hero_name": "47s 会议纪要逐句标亮 + 悬浮 Ask Amie 弹性胶囊",
            "hero_feat_id": "eu_L4_am_ask_capsule",
            "hero_feat_name": "逐句渐显转写转待办与 Ask 悬浮胶囊展开",
            "array_id": "eu_L3_am_schedule_array",
            "array_name": "周日程排班矩阵 + 7 天上手阶段与导出 ×4",
            "array_count": 4,
            "dialog_id": "eu_L3_am_event_dialog",
            "dialog_name": "Ask Amie 会议日程快速新建弹窗",
        },
        "bboxes": [
            {"bbox_id": "bb_am_nav", "eu_id": "eu_L3_am_rail_dock", "label": "轻量日程导轨 (邻近放大)", "x": 16, "y": 16, "w": 76, "h": 868, "role": "nav"},
            {"bbox_id": "bb_am_top", "eu_id": "eu_L3_am_topbar", "label": "Amie 顶栏与 Week 模式切换", "x": 108, "y": 16, "w": 1312, "h": 82, "role": "stage"},
            {"bbox_id": "bb_am_hero", "eu_id": "eu_L3_am_notes_stage", "label": "47s 会议纪要高亮 + Ask Amie 胶囊", "x": 108, "y": 114, "w": 1312, "h": 496, "role": "split"},
            {"bbox_id": "bb_am_arr", "eu_id": "eu_L3_am_schedule_array", "label": "周日程矩阵 & 7-Day Card ×4 + CSV", "x": 108, "y": 626, "w": 1312, "h": 258, "role": "array"},
        ],
    },
    "nothing_dot_web": {
        "prefix": "nd",
        "full_bleed": True,
        "keep_filter_edge": True,
        "root_name": "Nothing OS · 工业纯黑红点阵控制矩阵",
        "frame_url": "/cases/nothing_dot_web/frames/ref_nd_desktop.png",
        "data_source": "nothing.os.telemetry",
        "rail_w": 0,
        "panel_radius": 16,
        "registry": {
            "surface_atoms": {
                "nd_surf_bg": {"name": "纯粹黑曜石底面", "kind": "color", "value": "#000000", "css_var": "--nd-bg"},
                "nd_surf_panel": {"name": "工业哑光炭黑模块面", "kind": "color", "value": "#111111", "css_var": "--nd-panel"},
                "nd_surf_border": {"name": "1px 精密分隔边界", "kind": "color", "value": "#262626", "css_var": "--nd-border"},
                "nd_surf_red": {"name": "Nothing 标志脉冲红", "kind": "color", "value": "#d71921", "css_var": "--nd-red"},
                "nd_surf_ink": {"name": "高对比光学纯白字色", "kind": "color", "value": "#ffffff", "css_var": "--nd-ink"},
            },
            "typography_atoms": {
                "nd_typo_h1": {"name": "点阵矩阵大标题字阶", "kind": "font_scale", "value": "clamp(26px, 3vw, 38px)", "css_var": "--nd-font-h1"},
                "nd_typo_mono": {"name": "Ndot 技术遥测等宽字阶", "kind": "font_scale", "value": "12px", "css_var": "--nd-font-mono"},
                "nd_typo_body": {"name": "面板正文字阶", "kind": "font_scale", "value": "13.5px", "css_var": "--nd-font-body"},
            },
            "layout_atoms": {
                "nd_lay_maxw": {"name": "点阵矩阵容器最大宽", "kind": "dimension", "value": "1380px", "css_var": "--nd-maxw"},
                "nd_lay_radius": {"name": "硬朗工程圆角", "kind": "radius", "value": "16px", "css_var": "--nd-radius"},
                "nd_lay_gap": {"name": "网格节奏间距", "kind": "spacing", "value": "14px", "css_var": "--nd-gap"},
            },
            "motion_atoms": {
                "nd_mot_dot": {"name": "LED 点阵瞬态响应时长", "kind": "duration", "value": "180ms", "css_var": "--nd-dur-dot"},
            },
            "evidence_atoms": {
                "ev_nd_dom": {"name": "Nothing OS 三断点与点阵 HUD 快照", "breakpoints": [390, 768, 1440], "frame_ref": "ref_nd_desktop.png"},
            },
        },
        "nodes": {
            "topbar_id": "eu_L3_nd_topbar",
            "topbar_name": "Nothing 极简顶栏与 [GLYPH / STUDIO / QUIET] 模式切换",
            "topbar_feat_id": "eu_L4_nd_mode_switch",
            "topbar_feat_name": "模式胶囊联动 Glyph 灯环、点阵图表与诊断弹窗",
            "hero_id": "eu_L3_nd_matrix_hud",
            "hero_name": "LED 点阵时钟 + Glyph 12 节段灯环 + 点阵 CPU/音频频谱图组",
            "hero_feat_id": "eu_L4_nd_glyph_pulse",
            "hero_feat_name": "Glyph 灯环分节开关与点阵波形/频谱实时渲染",
            "array_id": "eu_L3_nd_widgets_array",
            "array_name": "SYSTEM / AUDIO / SENSOR 微件日志与 CSV 导出阵列 ×4",
            "array_count": 4,
            "dialog_id": "eu_L3_nd_diag_dialog",
            "dialog_name": "Glyph 硬件节点自检弹窗",
        },
        "bboxes": [
            {"bbox_id": "bb_nd_top", "eu_id": "eu_L3_nd_topbar", "label": "Nothing OS 顶栏与模式切换", "x": 16, "y": 16, "w": 1408, "h": 74, "role": "nav"},
            {"bbox_id": "bb_nd_hero", "eu_id": "eu_L3_nd_matrix_hud", "label": "点阵时钟 + Glyph 灯环 + 3 大点阵数据图", "x": 16, "y": 102, "w": 1408, "h": 510, "role": "split"},
            {"bbox_id": "bb_nd_arr", "eu_id": "eu_L3_nd_widgets_array", "label": "微件遥测阵列 ×4 + CSV 导出", "x": 16, "y": 626, "w": 1408, "h": 258, "role": "array"},
        ],
    },
    "poolsuite_os_web": {
        "prefix": "ps",
        "full_bleed": False,
        "keep_filter_edge": True,
        "root_name": "Poolsuite · 90s 复古暖粉 Macintosh 多窗桌面",
        "frame_url": "/cases/poolsuite_os_web/frames/ref_ps_desktop.png",
        "data_source": "poolsuite.fm.channels",
        "rail_w": 84,
        "panel_radius": 4,
        "registry": {
            "surface_atoms": {
                "ps_surf_bg": {"name": "阳光奶油米白桌面基底", "kind": "color", "value": "#f4ece1", "css_var": "--ps-bg"},
                "ps_surf_win": {"name": "复古象牙窗体面板", "kind": "color", "value": "#fbf7f0", "css_var": "--ps-win"},
                "ps_surf_peach": {"name": "Malibu 珊瑚桃粉高亮面", "kind": "color", "value": "#ffb7a5", "css_var": "--ps-peach"},
                "ps_surf_blue": {"name": "Mac OS 9 像素皇家蓝", "kind": "color", "value": "#3b6ef6", "css_var": "--ps-blue"},
                "ps_surf_ink": {"name": "复古硬边框炭墨字色", "kind": "color", "value": "#1c1917", "css_var": "--ps-ink"},
            },
            "typography_atoms": {
                "ps_typo_h1": {"name": "复古标题栏与海报字阶", "kind": "font_scale", "value": "clamp(22px, 2.5vw, 32px)", "css_var": "--ps-font-h1"},
                "ps_typo_mono": {"name": "磁带时间码像素等宽字阶", "kind": "font_scale", "value": "12px", "css_var": "--ps-font-mono"},
                "ps_typo_body": {"name": "菜单与窗口正文字阶", "kind": "font_scale", "value": "13px", "css_var": "--ps-font-body"},
            },
            "layout_atoms": {
                "ps_lay_maxw": {"name": "复古桌面容器最大宽", "kind": "dimension", "value": "1380px", "css_var": "--ps-maxw"},
                "ps_lay_radius": {"name": "90s 硬朗小窗角半径", "kind": "radius", "value": "4px", "css_var": "--ps-radius"},
                "ps_lay_gap": {"name": "窗口与图标网格间距", "kind": "spacing", "value": "14px", "css_var": "--ps-gap"},
            },
            "motion_atoms": {
                "ps_mot_win": {"name": "复古窗口置顶与切肤切换时长", "kind": "duration", "value": "160ms", "css_var": "--ps-dur-win"},
            },
            "evidence_atoms": {
                "ev_ps_dom": {"name": "Poolsuite OS 三断点与多窗交互快照", "breakpoints": [390, 768, 1440], "frame_ref": "ref_ps_desktop.png"},
            },
        },
        "nodes": {
            "nav_name": "左侧 90s 桌面快捷图标 Dock (邻近放大)",
            "nav_kind": "component.proximity_dock",
            "topbar_id": "eu_L3_ps_topbar",
            "topbar_name": "Mac OS 9 菜单栏与主题/视图切换",
            "topbar_feat_id": "eu_L4_ps_theme_switch",
            "topbar_feat_name": "Malibu Peach / Tokyo Mint / Classic Platinum 整套桌面换肤",
            "hero_id": "eu_L3_ps_desktop_stage",
            "hero_name": "Poolsuite 卡带电台窗 + 复古像素统计图窗 + System 9 监视窗",
            "hero_feat_id": "eu_L4_ps_window_stack",
            "hero_feat_name": "点击窗口标题栏切换激活置顶 (z-index) 与卡带实时播放",
            "array_id": "eu_L3_ps_telemetry_array",
            "array_name": "Synthwave / Yacht / Lo-Fi 频道目录与 CSV 归档 ×4",
            "array_count": 4,
            "dialog_id": "eu_L3_ps_system_dialog",
            "dialog_name": "About Poolsuite System 9 对话框",
        },
        "bboxes": [
            {"bbox_id": "bb_ps_nav", "eu_id": "eu_L3_ps_rail_dock", "label": "桌面快捷图标 Dock (邻近放大)", "x": 16, "y": 16, "w": 84, "h": 868, "role": "nav"},
            {"bbox_id": "bb_ps_top", "eu_id": "eu_L3_ps_topbar", "label": "Mac OS 9 菜单栏与 3 主题换肤", "x": 116, "y": 16, "w": 1304, "h": 72, "role": "stage"},
            {"bbox_id": "bb_ps_hero", "eu_id": "eu_L3_ps_desktop_stage", "label": "复古卡带电台窗 + 像素收听统计柱图/折线/圆环窗", "x": 116, "y": 100, "w": 1304, "h": 510, "role": "split"},
            {"bbox_id": "bb_ps_arr", "eu_id": "eu_L3_ps_telemetry_array", "label": "频道磁带队列 ×4 + CSV 导出", "x": 116, "y": 626, "w": 1304, "h": 258, "role": "array"},
        ],
    },
    "daylight_eink_web": {
        "prefix": "dl",
        "full_bleed": False,
        "keep_filter_edge": True,
        "root_name": "Daylight DC-1 · 反射式琥珀电子纸专注工作台",
        "frame_url": "/cases/daylight_eink_web/frames/ref_dl_desktop.png",
        "data_source": "daylight.sol.reading",
        "rail_w": 76,
        "panel_radius": 12,
        "registry": {
            "surface_atoms": {
                "dl_surf_paper": {"name": "Sol:OS 反射式日光暖纸底色", "kind": "color", "value": "#efe9dc", "css_var": "--dl-paper"},
                "dl_surf_amber": {"name": "深夜无蓝光琥珀背光高亮", "kind": "color", "value": "#e5bc75", "css_var": "--dl-amber"},
                "dl_surf_border": {"name": "1.5px 温润纸墨边界线", "kind": "color", "value": "#c5bcab", "css_var": "--dl-border"},
                "dl_surf_ink": {"name": "60fps 纯碳墨主正文色", "kind": "color", "value": "#1a1714", "css_var": "--dl-ink"},
                "dl_surf_muted": {"name": "淡墨批注次级文本色", "kind": "color", "value": "#5e574c", "css_var": "--dl-muted"},
            },
            "typography_atoms": {
                "dl_typo_h1": {"name": "电子纸编辑排版标题字阶", "kind": "font_scale", "value": "clamp(24px, 2.8vw, 36px)", "css_var": "--dl-font-h1"},
                "dl_typo_mono": {"name": "页码与番茄钟等宽字阶", "kind": "font_scale", "value": "12px", "css_var": "--dl-font-mono"},
                "dl_typo_body": {"name": "纸书正文字阶", "kind": "font_scale", "value": "14px", "css_var": "--dl-font-body"},
            },
            "layout_atoms": {
                "dl_lay_rail": {"name": "左侧 Sol 导轨定宽", "kind": "dimension", "value": "76px", "css_var": "--dl-rail-w"},
                "dl_lay_radius": {"name": "纸面卡片圆角", "kind": "radius", "value": "12px", "css_var": "--dl-radius"},
                "dl_lay_gap": {"name": "阅读栏基准间距", "kind": "spacing", "value": "14px", "css_var": "--dl-gap"},
            },
            "motion_atoms": {
                "dl_mot_ink": {"name": "E-Ink 清爽墨水刷新时长", "kind": "duration", "value": "180ms", "css_var": "--dl-dur-ink"},
            },
            "evidence_atoms": {
                "ev_dl_dom": {"name": "Daylight DC-1 三断点与色温/图表快照", "breakpoints": [390, 768, 1440], "frame_ref": "ref_dl_desktop.png"},
            },
        },
        "nodes": {
            "nav_name": "Sol:OS 电子纸左侧导轨 (邻近放大)",
            "nav_kind": "component.proximity_dock",
            "topbar_id": "eu_L3_dl_topbar",
            "topbar_name": "Sol 顶栏、Amber Backlight 色温滑块与视图切换",
            "topbar_feat_id": "eu_L4_dl_amber_slider",
            "topbar_feat_name": "0–100% 琥珀色温实时插值与 E-Ink 清墨刷新脉冲",
            "hero_id": "eu_L3_dl_reader_stage",
            "hero_name": "无眩光沉浸批注页 + 番茄钟 + 墨水风阅读柱图/热力图/圆环",
            "hero_feat_id": "eu_L4_dl_eink_focus",
            "hero_feat_name": "阅读时长统计、番茄钟启动与认知负荷可视化",
            "array_id": "eu_L3_dl_notes_array",
            "array_name": "Reading / Notes / Tasks 纸面笔记与 CSV 导出阵列 ×4",
            "array_count": 4,
            "dialog_id": "eu_L3_dl_note_dialog",
            "dialog_name": "新建纸面批注与专注计时弹窗",
        },
        "bboxes": [
            {"bbox_id": "bb_dl_nav", "eu_id": "eu_L3_dl_rail_dock", "label": "Sol 导轨 (邻近放大)", "x": 16, "y": 16, "w": 76, "h": 868, "role": "nav"},
            {"bbox_id": "bb_dl_top", "eu_id": "eu_L3_dl_topbar", "label": "Amber Backlight 色温控制顶栏", "x": 108, "y": 16, "w": 1312, "h": 82, "role": "stage"},
            {"bbox_id": "bb_dl_hero", "eu_id": "eu_L3_dl_reader_stage", "label": "纸感批注舞台 + 阅读柱图/热力矩/负荷环", "x": 108, "y": 114, "w": 1312, "h": 496, "role": "split"},
            {"bbox_id": "bb_dl_arr", "eu_id": "eu_L3_dl_notes_array", "label": "Reading/Notes 阵列 ×4 + CSV 导出", "x": 108, "y": 626, "w": 1312, "h": 258, "role": "array"},
        ],
    },
    "family_fluid_web": {
        "prefix": "fm",
        "full_bleed": False,
        "keep_filter_edge": True,
        "root_name": "Family · 软触感纯白云朵与变形抽屉台",
        "frame_url": "/cases/family_fluid_web/frames/ref_fm_desktop.png",
        "data_source": "family.wallet.tray",
        "rail_w": 76,
        "panel_radius": 28,
        "registry": {
            "surface_atoms": {
                "fm_surf_bg": {"name": "冷雾浅灰空气感底面", "kind": "color", "value": "#f2f4f7", "css_var": "--fm-bg"},
                "fm_surf_card": {"name": "纯白高曲率软触卡片面", "kind": "color", "value": "#ffffff", "css_var": "--fm-card"},
                "fm_surf_line": {"name": "极轻云雾分隔描边", "kind": "color", "value": "#e5e7eb", "css_var": "--fm-line"},
                "fm_surf_sky": {"name": "Family 流体天蓝焦点色", "kind": "color", "value": "#0ea5e9", "css_var": "--fm-sky"},
                "fm_surf_ink": {"name": "高可读深炭主字色", "kind": "color", "value": "#111827", "css_var": "--fm-ink"},
            },
            "typography_atoms": {
                "fm_typo_h1": {"name": "大数字净值柔和标题字阶", "kind": "font_scale", "value": "clamp(26px, 3vw, 38px)", "css_var": "--fm-font-h1"},
                "fm_typo_mono": {"name": "哈希地址与 Gas 费用字阶", "kind": "font_scale", "value": "12px", "css_var": "--fm-font-mono"},
                "fm_typo_body": {"name": "抽屉操作标签正文字阶", "kind": "font_scale", "value": "14px", "css_var": "--fm-font-body"},
            },
            "layout_atoms": {
                "fm_lay_rail": {"name": "左侧轻量钱包导轨定宽", "kind": "dimension", "value": "76px", "css_var": "--fm-rail-w"},
                "fm_lay_radius": {"name": "28px 软触超椭圆圆角", "kind": "radius", "value": "28px", "css_var": "--fm-radius"},
                "fm_lay_gap": {"name": "云朵卡群呼吸间距", "kind": "spacing", "value": "16px", "css_var": "--fm-gap"},
            },
            "motion_atoms": {
                "fm_mot_tray": {"name": "Morphing Tray 弹性形变时长", "kind": "duration", "value": "340ms", "css_var": "--fm-dur-tray"},
            },
            "evidence_atoms": {
                "ev_fm_dom": {"name": "Family 三断点与上下文变形抽屉快照", "breakpoints": [390, 768, 1440], "frame_ref": "ref_fm_desktop.png"},
            },
        },
        "nodes": {
            "nav_name": "Family 轻量左侧导轨 (邻近放大)",
            "nav_kind": "component.proximity_dock",
            "topbar_id": "eu_L3_fm_topbar",
            "topbar_name": "Family 账户顶栏与 1D/1W/1M/1Y 视图切换",
            "topbar_feat_id": "eu_L4_fm_range_switch",
            "topbar_feat_name": "时间周期实时重绘平滑资产面积图与持仓环",
            "hero_id": "eu_L3_fm_portfolio_stage",
            "hero_name": "净值面积图/持仓环/Gas折线 + 上下文变形抽屉 (Send/Swap/SpeedUp/Yield)",
            "hero_feat_id": "eu_L4_fm_morph_tray",
            "hero_feat_name": "Morphing Tray 弹性变高变形与零跳转交易签章反馈",
            "array_id": "eu_L3_fm_tx_array",
            "array_name": "Send / Swap / Yield 交易流水与 CSV 导出阵列 ×4",
            "array_count": 4,
            "dialog_id": "eu_L3_fm_vault_dialog",
            "dialog_name": "Recovery Vault 保险库安全配置弹窗",
        },
        "bboxes": [
            {"bbox_id": "bb_fm_nav", "eu_id": "eu_L3_fm_rail_dock", "label": "Family 导轨 (邻近放大)", "x": 16, "y": 16, "w": 76, "h": 868, "role": "nav"},
            {"bbox_id": "bb_fm_top", "eu_id": "eu_L3_fm_topbar", "label": "Family 顶栏与时间周期切换", "x": 108, "y": 16, "w": 1312, "h": 82, "role": "stage"},
            {"bbox_id": "bb_fm_hero", "eu_id": "eu_L3_fm_portfolio_stage", "label": "资产面积图/持仓环 + Contextual Morphing Tray", "x": 108, "y": 114, "w": 1312, "h": 496, "role": "split"},
            {"bbox_id": "bb_fm_arr", "eu_id": "eu_L3_fm_tx_array", "label": "交易流水筛选阵列 ×4 + CSV 导出", "x": 108, "y": 626, "w": 1312, "h": 258, "role": "array"},
        ],
    },
}


def _build_motion_web_skeleton(case_id: str) -> dict[str, Any]:
    spec = _WEB_MOTION_SPECS[case_id]
    p = spec["prefix"]
    is_full = bool(spec.get("full_bleed", False))
    rail_w = int(spec["rail_w"])
    stage_x = 16 if is_full else (16 + rail_w + 16)
    stage_w = 1440 - stage_x - 16 if is_full else (1440 - stage_x - 20)
    root_id = f"eu_L0_{p}_workspace"

    stage_l1 = f"eu_L1_{p}_stage"
    top_l2 = f"eu_L2_{p}_topbar"
    hero_l2 = f"eu_L2_{p}_hero_zone"
    arr_l2 = f"eu_L2_{p}_array_zone"
    ov_l1 = f"eu_L1_{p}_overlay"
    ov_l2 = f"eu_L2_{p}_dialog_host"

    rect_specs: dict[str, dict[int, tuple[int, int, int, int]]] = {
        f"eu_L1_{p}_intro": {390: (12, 6, 366, 34), 768: (18, 8, 732, 34), 1440: (16, 8, 1404, 34)},
        f"eu_L2_{p}_intro_bar": {390: (12, 6, 366, 34), 768: (18, 8, 732, 34), 1440: (16, 8, 1404, 34)},
        stage_l1: {
            390: (12, 48 if is_full else 114, 366, 1520),
            768: (18 if is_full else 114, 48, 732 if is_full else 636, 1120),
            1440: (stage_x, 16, stage_w, 868),
        },
        top_l2: {
            390: (12, 48 if is_full else 114, 366, 92),
            768: (18 if is_full else 114, 48, 732 if is_full else 636, 92),
            1440: (stage_x, 16, stage_w, 96),
        },
        hero_l2: {
            390: (12, 150 if is_full else 218, 366, 780),
            768: (18 if is_full else 114, 150, 732 if is_full else 636, 600),
            1440: (stage_x, 116, stage_w, 496),
        },
        arr_l2: {
            390: (12, 950 if is_full else 1012, 366, 600),
            768: (18 if is_full else 114, 762, 732 if is_full else 636, 390),
            1440: (stage_x, 626, stage_w, 258),
        },
        ov_l1: {390: (16, 140, 358, 360), 768: (140, 150, 488, 380), 1440: (420, 170, 580, 410)},
        ov_l2: {390: (16, 140, 358, 360), 768: (140, 150, 488, 380), 1440: (420, 170, 580, 410)},
    }
    if not is_full:
        rect_specs[f"eu_L1_{p}_nav"] = {390: (12, 46, 366, 60), 768: (18, 48, 84, 1120), 1440: (16, 16, rail_w, 868)}
        rect_specs[f"eu_L2_{p}_nav_rail"] = {390: (12, 46, 366, 60), 768: (18, 48, 84, 1120), 1440: (16, 16, rail_w, 868)}

    dom = base_cat._build_three_breakpoint_rects(root_id, rect_specs)
    reg = spec["registry"]
    first_surf = next(iter(reg["surface_atoms"].items()))
    first_typo = next(iter(reg["typography_atoms"].items()))
    first_lay = next(iter(reg["layout_atoms"].items()))
    first_mot = next(iter(reg["motion_atoms"].items()))
    nm = spec["nodes"]

    computed_styles = [
        {"id": f"{p}_cs_surf", "eu_id": nm["topbar_id"], "property": "color", "value": first_surf[1]["value"], "token_ref": first_surf[0], "delta_e": 0.0},
        {"id": f"{p}_cs_typo", "eu_id": nm["hero_id"], "property": "font-size", "value": first_typo[1]["value"], "token_ref": first_typo[0], "delta_e": 0.0},
        {"id": f"{p}_cs_lay", "eu_id": nm["array_id"], "property": "gap", "value": first_lay[1]["value"], "token_ref": first_lay[0], "delta_e": 0.0},
        {"id": f"{p}_cs_mot", "eu_id": nm["topbar_id"] if is_full else f"eu_L3_{p}_rail_dock", "property": "transition-duration", "value": first_mot[1]["value"], "token_ref": first_mot[0], "delta_e": 0.0},
    ]

    bboxes = spec["bboxes"]
    svg = base_cat._render_web_skeleton_svg(
        spec["frame_url"],
        bboxes,
        rail_x=16,
        stage_x=stage_x,
        panel_radius=int(spec["panel_radius"]),
    )

    interactive_elements = [
        {"id": f"{p}_el_skip", "eu_id": f"eu_L3_{p}_skip_entry", "role": "button", "accessible_name": "Skip to content", "states": ["default", "hover", "focus-visible", "active"]},
        {"id": f"{p}_el_top", "eu_id": nm["topbar_id"], "role": "tab", "accessible_name": nm["topbar_name"], "states": ["default", "hover", "focus-visible", "active"]},
        {"id": f"{p}_el_hero", "eu_id": nm["hero_id"], "role": "button", "accessible_name": nm["hero_name"], "states": ["default", "hover", "focus-visible", "active"]},
        {"id": f"{p}_el_arr", "eu_id": nm["array_id"], "role": "button", "accessible_name": nm["array_name"], "states": ["default", "hover", "focus-visible", "active"]},
        {"id": f"{p}_el_dlg", "eu_id": nm["dialog_id"], "role": "dialog", "accessible_name": nm["dialog_name"], "states": ["default", "hover", "focus-visible", "active"]},
    ]
    if not is_full:
        interactive_elements.insert(
            1,
            {"id": f"{p}_el_rail", "eu_id": f"eu_L3_{p}_rail_dock", "role": "link", "accessible_name": nm["nav_name"], "states": ["default", "hover", "focus-visible", "active"]},
        )

    return {
        "case_id": case_id,
        "modality": "web",
        "duration_sec": None,
        "coverage_ratio": 1.0,
        "breakpoints": [390, 768, 1440],
        "viewport": {"width": 1440, "height": 900, "breakpoints": [390, 768, 1440]},
        "dom": dom,
        "computed_styles": computed_styles,
        "interactive_elements": interactive_elements,
        "content_nodes": [
            {"id": f"{p}_cn_bg", "eu_id": root_id, "content_class": "decoration", "aria_hidden": True, "data_source": None, "children_classes": []},
            {"id": f"{p}_cn_hero", "eu_id": nm["hero_id"], "content_class": "data", "aria_hidden": False, "data_source": spec["data_source"], "children_classes": ["data"]},
            {"id": f"{p}_cn_arr", "eu_id": nm["array_id"], "content_class": "data", "aria_hidden": False, "data_source": f"{spec['data_source']}.items", "children_classes": ["data"]},
        ],
        "segments": [
            {
                "segment_id": "seg_web_desktop",
                "index": 1,
                "t0": 0.0,
                "t1": 1.0,
                "label": f"1440×900 · {spec['root_name']}骨架",
                "frame_url": spec["frame_url"],
                "active_eu_ids": [b["eu_id"] for b in bboxes],
                "bboxes": bboxes,
            }
        ],
        "bboxes": [dict(b, segment_id="seg_web_desktop", color_role=b["role"]) for b in bboxes],
        "skeleton_svg": svg,
    }


def _build_motion_web_eu_tree(case_id: str, finalize_fn: Callable[..., dict[str, Any]]) -> dict[str, Any]:
    spec = _WEB_MOTION_SPECS[case_id]
    p = spec["prefix"]
    is_full = bool(spec.get("full_bleed", False))
    keep_filter = bool(spec.get("keep_filter_edge", True))
    reg = spec["registry"]
    ev_id = f"ev_{p}_dom"
    surf_ids = list(reg["surface_atoms"].keys())
    typo_ids = list(reg["typography_atoms"].keys())
    lay_ids = list(reg["layout_atoms"].keys())
    mot_ids = list(reg["motion_atoms"].keys())
    all_atoms = surf_ids + typo_ids + lay_ids + mot_ids + [ev_id]
    base_atoms = [surf_ids[0], typo_ids[0], lay_ids[0], ev_id]

    rail_w = int(spec["rail_w"])
    stage_x = 16 if is_full else (16 + rail_w + 16)
    stage_w = 1440 - stage_x - 16 if is_full else (1440 - stage_x - 20)
    nm = spec["nodes"]
    root_id = f"eu_L0_{p}_workspace"
    rail_dock_id = f"eu_L3_{p}_rail_dock"
    rail_prox_id = f"eu_L4_{p}_rail_proximity"

    nodes: list[dict[str, Any]] = [
        {"eu_id": root_id, "name": spec["root_name"], "level": "L0", "node_kind": "product.workspace", "parent_id": None, "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [0, 0, 1440, 900], "rendered": True},

        {"eu_id": f"eu_L1_{p}_intro", "name": "无障碍跳转外壳", "level": "L1", "node_kind": "territory.intro_shell", "parent_id": root_id, "template_slot": "intro_shell", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [16, 8, 1404, 34]},
        {"eu_id": f"eu_L2_{p}_intro_bar", "name": "顶部快捷跳转条", "level": "L2", "node_kind": "region.intro_strip", "parent_id": f"eu_L1_{p}_intro", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [16, 8, 1404, 34]},
        {"eu_id": f"eu_L3_{p}_skip_entry", "name": "跳过导航快捷按钮", "level": "L3", "entity": True, "node_kind": "component.skip_button", "parent_id": f"eu_L2_{p}_intro_bar", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [16, 8, 180, 34], "dom_selector": f'[data-eu-id="eu_L3_{p}_skip_entry"]', "rendered": True},
        {"eu_id": f"eu_L4_{p}_skip_feat", "name": "键盘焦点直达特征", "level": "L4", "node_kind": "feature.skip_a11y", "parent_id": f"eu_L3_{p}_skip_entry", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [16, 8, 180, 34]},
        {"eu_id": f"eu_L5_{p}_skip_atoms", "name": "入口基础原子束", "level": "L5", "node_kind": "atom.bundle", "parent_id": f"eu_L4_{p}_skip_feat", "adaptation_mode": "ATOMIC_MOUNT", "atom_refs": base_atoms},
    ]

    if not is_full:
        nodes.extend([
            {"eu_id": f"eu_L1_{p}_nav", "name": "导航坞领地", "level": "L1", "node_kind": "territory.nav_dock", "parent_id": root_id, "template_slot": "nav_dock", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [16, 16, rail_w, 868], "rendered": True},
            {"eu_id": f"eu_L2_{p}_nav_rail", "name": "左侧独立导轨区", "level": "L2", "node_kind": "region.nav_rail", "parent_id": f"eu_L1_{p}_nav", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [16, 16, rail_w, 868]},
            {"eu_id": rail_dock_id, "name": nm["nav_name"], "level": "L3", "entity": True, "interaction_density": 3, "node_kind": nm["nav_kind"], "parent_id": f"eu_L2_{p}_nav_rail", "adaptation_mode": "SPLIT_HIGH_INTERACTION", "envelope_bbox": [16, 16, rail_w, 868], "dom_selector": f'[data-eu-id="{rail_dock_id}"]', "rendered": True},
            {"eu_id": rail_prox_id, "name": "指针邻近放大与浮签特征", "level": "L4", "motion": True, "node_kind": "feature.proximity_magnify", "parent_id": rail_dock_id, "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [16, 16, rail_w, 640], "rendered": True},
            {"eu_id": f"eu_L5_{p}_rail_atoms", "name": "导轨全量样式动效原子束", "level": "L5", "node_kind": "atom.bundle", "parent_id": rail_prox_id, "adaptation_mode": "ATOMIC_MOUNT", "atom_refs": all_atoms},
        ])

    nodes.extend([
        {"eu_id": f"eu_L1_{p}_stage", "name": "全宽主舞台领地" if is_full else "独立滚动主舞台领地", "level": "L1", "node_kind": "territory.main_stage", "parent_id": root_id, "template_slot": "main_stage", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [stage_x, 16, stage_w, 868], "rendered": True},
        {"eu_id": f"eu_L2_{p}_topbar", "name": "顶栏导航与操作带", "level": "L2", "node_kind": "region.topbar", "parent_id": f"eu_L1_{p}_stage", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [stage_x, 16, stage_w, 96]},
        {"eu_id": nm["topbar_id"], "name": nm["topbar_name"], "level": "L3", "entity": True, "node_kind": "component.stage_topbar", "parent_id": f"eu_L2_{p}_topbar", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [stage_x, 16, stage_w, 96], "dom_selector": f'[data-eu-id="{nm["topbar_id"]}"]', "rendered": True},
        {"eu_id": nm["topbar_feat_id"], "name": nm["topbar_feat_name"], "level": "L4", "motion": True, "node_kind": "feature.route_switch", "parent_id": nm["topbar_id"], "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [stage_x, 16, stage_w, 96], "rendered": True},
        {"eu_id": f"eu_L5_{p}_top_atoms", "name": "顶栏全量样式动效原子束", "level": "L5", "node_kind": "atom.bundle", "parent_id": nm["topbar_feat_id"], "adaptation_mode": "ATOMIC_MOUNT", "atom_refs": all_atoms},

        {"eu_id": f"eu_L2_{p}_hero_zone", "name": "核心交互主展区", "level": "L2", "node_kind": "region.hero_stage", "parent_id": f"eu_L1_{p}_stage", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [stage_x, 116, stage_w, 496]},
        {"eu_id": nm["hero_id"], "name": nm["hero_name"], "level": "L3", "entity": True, "interaction_density": 4, "node_kind": "component.primary_interactive", "parent_id": f"eu_L2_{p}_hero_zone", "adaptation_mode": "SPLIT_HIGH_INTERACTION", "envelope_bbox": [stage_x, 116, stage_w, 496], "dom_selector": f'[data-eu-id="{nm["hero_id"]}"]', "rendered": True},
        {"eu_id": nm["hero_feat_id"], "name": nm["hero_feat_name"], "level": "L4", "motion": True, "node_kind": "feature.primary_control", "parent_id": nm["hero_id"], "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [stage_x, 116, stage_w, 496], "rendered": True},
        {"eu_id": f"eu_L5_{p}_hero_atoms", "name": "核心交互区原子束", "level": "L5", "node_kind": "atom.bundle", "parent_id": nm["hero_feat_id"], "adaptation_mode": "ATOMIC_MOUNT", "atom_refs": all_atoms},

        {"eu_id": f"eu_L2_{p}_array_zone", "name": "下方结构化阵列带", "level": "L2", "node_kind": "region.lower_array", "parent_id": f"eu_L1_{p}_stage", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [stage_x, 626, stage_w, 258]},
        {"eu_id": nm["array_id"], "name": nm["array_name"], "level": "L3", "entity": True, "node_kind": "component.spec.array", "parent_id": f"eu_L2_{p}_array_zone", "adaptation_mode": "FOLD_ARRAY", "array_count": int(nm["array_count"]), "envelope_bbox": [stage_x, 626, stage_w, 258], "dom_selector": f'[data-eu-id="{nm["array_id"]}"]', "rendered": True},
        {"eu_id": f"eu_L4_{p}_filter_export", "name": "同构条目筛选与 CSV 导出", "level": "L4", "node_kind": "feature.filter_export", "parent_id": nm["array_id"], "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [stage_x, 626, stage_w, 258], "rendered": True},
        {"eu_id": f"eu_L5_{p}_array_atoms", "name": "阵列原子束", "level": "L5", "node_kind": "atom.bundle", "parent_id": f"eu_L4_{p}_filter_export", "adaptation_mode": "ATOMIC_MOUNT", "atom_refs": base_atoms},

        {"eu_id": f"eu_L1_{p}_overlay", "name": "辅助模态弹窗领地", "level": "L1", "node_kind": "territory.auxiliary_overlay", "parent_id": root_id, "template_slot": "auxiliary_overlay", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [420, 170, 580, 410]},
        {"eu_id": f"eu_L2_{p}_dialog_host", "name": "对话框宿主区", "level": "L2", "node_kind": "region.dialog", "parent_id": f"eu_L1_{p}_overlay", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [420, 170, 580, 410]},
        {"eu_id": nm["dialog_id"], "name": nm["dialog_name"], "level": "L3", "entity": True, "node_kind": "component.modal_sheet", "parent_id": f"eu_L2_{p}_dialog_host", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [420, 170, 580, 410], "dom_selector": f'[data-eu-id="{nm["dialog_id"]}"]', "rendered": True},
        {"eu_id": f"eu_L4_{p}_focus_trap", "name": "关闭弹窗归还触发焦点特征", "level": "L4", "node_kind": "feature.modal_focus_restore", "parent_id": nm["dialog_id"], "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [420, 170, 580, 410]},
        {"eu_id": f"eu_L5_{p}_dialog_atoms", "name": "弹窗原子束", "level": "L5", "node_kind": "atom.bundle", "parent_id": f"eu_L4_{p}_focus_trap", "adaptation_mode": "ATOMIC_MOUNT", "atom_refs": base_atoms},
    ])

    edges: list[dict[str, Any]] = []
    if not is_full:
        edges.extend([
            {"edge_id": f"edge_{p}_proximity", "edge_type": "MODULATES_NEIGHBOR", "source_eu_id": rail_dock_id, "target_eu_id": rail_prox_id, "label": "左侧导轨指针距离平滑邻近放大", "evidence_ref": ev_id},
            {"edge_id": f"edge_{p}_scroll", "edge_type": "SCROLLS_INDEPENDENTLY", "source_eu_id": f"eu_L1_{p}_stage", "target_eu_id": f"eu_L1_{p}_nav", "label": "主舞台独立滚动，导轨静止不随滚", "evidence_ref": ev_id},
        ])
    edges.append({"edge_id": f"edge_{p}_state", "edge_type": "TRIGGERS_STATE", "source_eu_id": nm["topbar_id"], "target_eu_id": nm["hero_id"], "label": "顶栏导航/模式切换重绘主展区", "evidence_ref": ev_id})
    if keep_filter:
        edges.append({"edge_id": f"edge_{p}_filter", "edge_type": "FILTERS_VIEW", "source_eu_id": nm["hero_id"], "target_eu_id": nm["array_id"], "label": "参数筛选联动阵列与同口径 CSV 导出", "evidence_ref": ev_id})
    edges.extend([
        {"edge_id": f"edge_{p}_focus", "edge_type": "RESTORES_FOCUS", "source_eu_id": nm["dialog_id"], "target_eu_id": nm["topbar_id"], "label": "模态对话框关闭后焦点归还触发控件", "evidence_ref": ev_id},
        {"edge_id": f"edge_{p}_token", "edge_type": "SHARES_TOKEN", "source_eu_id": nm["hero_id"], "target_eu_id": nm["array_id"], "label": "共享表面色、字阶与动效时长 Token", "evidence_ref": ev_id},
    ])
    return finalize_fn("tpl_uiux_workspace_v1", "UI/UX 工作台原型", root_id, nodes, reg, edges)


def extract_motion_skeleton(case_id: str) -> dict[str, Any]:
    if case_id in _VIDEO_MOTION_SPECS:
        return _build_motion_video_skeleton(case_id)
    if case_id in _WEB_MOTION_SPECS:
        return _build_motion_web_skeleton(case_id)
    raise ValueError(f"Unknown motion case_id: {case_id}")


def build_motion_eu_tree(case_id: str, finalize_fn: Callable[..., dict[str, Any]]) -> dict[str, Any]:
    if case_id in _VIDEO_MOTION_SPECS:
        return _build_motion_video_eu_tree(case_id, finalize_fn)
    if case_id in _WEB_MOTION_SPECS:
        return _build_motion_web_eu_tree(case_id, finalize_fn)
    raise ValueError(f"Unknown motion case_id: {case_id}")
