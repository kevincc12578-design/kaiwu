"""
开物 v3.4 · 六大迥异视觉风格案例库 (styles_catalog.py)
覆盖流派：
  1. knob_hardware_web    : 工业硬件拟物 (KNOB k.no.b.1 · 暗棚机械键盘 + 双滚花旋钮 + 琥珀屏)
  2. nogood_brutal_web    : 新粗野主义撞色 (NoGood Studio · 酸性荧光绿 + 0px硬边 + 跑马灯电台)
  3. axiom_hud_web        : 极暗精工数据 HUD (Axiom · 纯黑细框 + 炽橙信号 + 嵌入式APL终端)
  4. monolog_swiss_poster : 瑞士国际主义杂志网格 (MONOLOG · ISO A3 12栏 + 报纸暖灰 + 巨型黑体)
  5. weeksync_paper_web   : 柔和纸感效率看板 (WeekSync · 燕麦米纸 + 虚线导航 + 实时排班工时沙盒)
  6. defined_aurora_web   : 创意极光磁流体暗调 (Defined · Canvas磁流体背景 + 纯黑L型几何遮罩)
"""
from __future__ import annotations

from typing import Any, Callable

import cases_catalog as base_cat

STYLE_CASE_META: dict[str, dict[str, Any]] = {
    "knob_hardware_web": {
        "case_id": "knob_hardware_web",
        "title": "KNOB · Industrial Hardware",
        "subtitle": "网页 → UI/UX",
        "modality": "web",
        "domain": "uiux",
        "template_id": "tpl_uiux_workspace_v1",
        "stage_url": "/cases/knob_hardware_web/app/index.html",
        "source_summary": "WEB · 390/768/1440px · 工业实体旋钮",
    },
    "nogood_brutal_web": {
        "case_id": "nogood_brutal_web",
        "title": "NoGood · Neo-Brutalist Studio",
        "subtitle": "网页 → UI/UX",
        "modality": "web",
        "domain": "uiux",
        "template_id": "tpl_uiux_workspace_v1",
        "stage_url": "/cases/nogood_brutal_web/app/index.html",
        "source_summary": "WEB · 390/768/1440px · 酸性绿新粗野",
    },
    "axiom_hud_web": {
        "case_id": "axiom_hud_web",
        "title": "Axiom · Dark Data HUD",
        "subtitle": "网页 → UI/UX",
        "modality": "web",
        "domain": "uiux",
        "template_id": "tpl_uiux_workspace_v1",
        "stage_url": "/cases/axiom_hud_web/app/index.html",
        "source_summary": "WEB · 390/768/1440px · 极暗精工终端",
    },
    "monolog_swiss_poster": {
        "case_id": "monolog_swiss_poster",
        "title": "MONOLOG · 瑞士杂志网格展板",
        "subtitle": "图片 → 平面设计",
        "modality": "image",
        "domain": "graphic",
        "template_id": "tpl_graphic_poster_v1",
        "stage_url": "/cases/monolog_swiss_poster/app/index.html",
        "source_summary": "IMAGE · ISO A3 · 瑞士杂志网格",
    },
    "weeksync_paper_web": {
        "case_id": "weeksync_paper_web",
        "title": "WeekSync · Paper Planner",
        "subtitle": "网页 → UI/UX",
        "modality": "web",
        "domain": "uiux",
        "template_id": "tpl_uiux_workspace_v1",
        "stage_url": "/cases/weeksync_paper_web/app/index.html",
        "source_summary": "WEB · 390/768/1440px · 奶油纸感排班",
    },
    "defined_aurora_web": {
        "case_id": "defined_aurora_web",
        "title": "Defined · Aurora Ferrofluid",
        "subtitle": "网页 → UI/UX",
        "modality": "web",
        "domain": "uiux",
        "template_id": "tpl_uiux_workspace_v1",
        "stage_url": "/cases/defined_aurora_web/app/index.html",
        "source_summary": "WEB · 390/768/1440px · 极光磁流体",
    },
}

STYLE_DEFAULT_ASSUMPTIONS: dict[str, list[dict[str, Any]]] = {
    "knob_hardware_web": [
        {
            "assumption_id": "ASM-KB-01",
            "eu_id": "eu_L3_kb_hardware_rig",
            "subject_ids": ["eu_L3_kb_hardware_rig", "eu_L4_kb_rotary_encoders"],
            "title": "k.no.b.1 实体机械键盘 3D 摄影渲染离线结构化替代",
            "category": "substitute_3d_hardware",
            "assumed_value": "以可交互倾斜分层 CSS/SVG 机械键帽矩阵、滚花旋钮与实时 LCD 屏幕替代原站静态 3D 光线追踪渲染图",
            "evidence_gap": "原站斜置键盘为离线高模渲染摄影素材，无法直接拆解为可按压的逐键 DOM 交互件",
            "bound_rule_id": "PW-04",
            "status": "open",
            "confirmed_at": None,
        },
        {
            "assumption_id": "ASM-KB-02",
            "eu_id": "eu_L3_kb_specs_array",
            "subject_ids": ["eu_L3_kb_specs_array"],
            "title": "轴体与按键固件配置模块说明口径",
            "category": "unobserved_interaction_payload",
            "assumed_value": "按所选模式与旋转编码器参数展现 CNC 机身、矮轴与键帽规格模块卡片组",
            "evidence_gap": "参考网页未开放离线固件配置下载文件接口",
            "bound_rule_id": "GU-03",
            "status": "open",
            "confirmed_at": None,
        },
    ],
    "nogood_brutal_web": [
        {
            "assumption_id": "ASM-NG-01",
            "eu_id": "eu_L3_ng_artwork_hero",
            "subject_ids": ["eu_L3_ng_artwork_hero"],
            "title": "NoGood 原创赛博头盔插画高精度矢量重绘声明",
            "category": "substitute_illustration_asset",
            "assumed_value": "以粗黑轮廓 SVG 矢量几何海报插画替代受版权保护的原作高分位图插画",
            "evidence_gap": "原作精细人物插画为独立版权美术资源，离线包内采用可控纯矢量重绘",
            "bound_rule_id": "PW-04",
            "status": "open",
            "confirmed_at": None,
        },
        {
            "assumption_id": "ASM-NG-02",
            "eu_id": "eu_L3_ng_system_log",
            "subject_ids": ["eu_L3_ng_system_log", "eu_L4_ng_radio_toggle"],
            "title": "NOGOOD RADIO 音轨与实时节点日志离线模拟",
            "category": "unobserved_interaction_payload",
            "assumed_value": "采用本地合成节奏脉冲动画与确定性系统日志流替代远程直播流媒体",
            "evidence_gap": "离线静态产物环境无外部广播音频流服务端",
            "bound_rule_id": "GU-03",
            "status": "open",
            "confirmed_at": None,
        },
    ],
    "axiom_hud_web": [
        {
            "assumption_id": "ASM-AX-01",
            "eu_id": "eu_L3_ax_query_hud",
            "subject_ids": ["eu_L3_ax_query_hud", "eu_L4_ax_apl_editor"],
            "title": "APL 查询终端离线支付失败日志样本数据集",
            "category": "unobserved_interaction_payload",
            "assumed_value": "内置确定性 payment-service charge.failed 结构化日志样本供 Run 执行汇总并导出 CSV",
            "evidence_gap": "官网演示端后端事件流依赖云端演示集群，离线按同构表结构生成",
            "bound_rule_id": "GU-03",
            "status": "open",
            "confirmed_at": None,
        },
        {
            "assumption_id": "ASM-AX-02",
            "eu_id": "eu_L3_ax_hero_deck",
            "subject_ids": ["eu_L3_ax_hero_deck"],
            "title": "多租户实时流监控指标刷新频率假设",
            "category": "telemetry_sampling_rate",
            "assumed_value": "按 Last 15m / 30m / 24h 时间窗切换确定性聚合序列，不建立长连接轮询",
            "evidence_gap": "参考页面静态展示了单次查询代码，未公开实时流采样周期参数",
            "bound_rule_id": "PW-04",
            "status": "open",
            "confirmed_at": None,
        },
    ],
    "monolog_swiss_poster": [
        {
            "assumption_id": "ASM-MN-01",
            "eu_id": "eu_L3_mn_wins_graphic",
            "subject_ids": ["eu_L3_mn_wins_graphic"],
            "title": "OH Arch 实景建筑摄影转为纯矢量建筑网格图形声明",
            "category": "vector_poster_adaptation",
            "assumed_value": "遵守 GG-03 零死位图与纯矢量原则，将实景建筑背景转为几何透视线条 SVG",
            "evidence_gap": "参考网页案例卡内含摄影底图，导入平面印刷 A3 展板须转为矢量可编辑图形",
            "bound_rule_id": "GG-03",
            "status": "open",
            "confirmed_at": None,
        },
        {
            "assumption_id": "ASM-MN-02",
            "eu_id": "eu_L4_mn_bleed_crop",
            "subject_ids": ["eu_L4_mn_bleed_crop"],
            "title": "报纸暖灰 (#D9DAD6) 特种非涂布纸印前 3mm 出血契约",
            "category": "prepress_bleed_spec",
            "assumed_value": "按 tpl_graphic_poster_v1 标准设定 297×420mm 裁切框与四边 3mm 出血、12mm 安全边距",
            "evidence_gap": "原参考站为屏幕视口排版，未附带实体印刷专色 ICC 与刀版文件",
            "bound_rule_id": "GG-01",
            "status": "open",
            "confirmed_at": None,
        },
    ],
    "weeksync_paper_web": [
        {
            "assumption_id": "ASM-WS-01",
            "eu_id": "eu_L3_ws_planner_grid",
            "subject_ids": ["eu_L3_ws_planner_grid"],
            "title": "多人实时协同光标位置与并发排班持久化假设",
            "category": "unobserved_realtime_sync",
            "assumed_value": "以本地浏览器状态保存周排班增删与工时汇总，并以轻量动画模拟团队光标状态",
            "evidence_gap": "原站多人同步依赖在线 WebSocket 房间，离线以单机沙盒持久化",
            "bound_rule_id": "GU-03",
            "status": "open",
            "confirmed_at": None,
        },
        {
            "assumption_id": "ASM-WS-02",
            "eu_id": "eu_L3_ws_summary_cards",
            "subject_ids": ["eu_L3_ws_summary_cards"],
            "title": "周标准工时上限 40h 口径与 CSV 导出字段",
            "category": "domain_business_rule",
            "assumed_value": "沿用参考图 40h of 40h 周工时配额基准实时计算剩余工时并生成周报 CSV",
            "evidence_gap": "参考画面仅呈现 23 Nov – 29 Nov 周视图，未展示完整后台加班/假期设置",
            "bound_rule_id": "PW-04",
            "status": "open",
            "confirmed_at": None,
        },
    ],
    "defined_aurora_web": [
        {
            "assumption_id": "ASM-DF-01",
            "eu_id": "eu_L3_df_aurora_stage",
            "subject_ids": ["eu_L3_df_aurora_stage", "eu_L4_df_ferrofluid_canvas"],
            "title": "高阶 GLSL 磁流体 Shader 降级为原生 2D Canvas 粒子流体场",
            "category": "substitute_shader_engine",
            "assumed_value": "使用零依赖 HTML5 2D Canvas 多层有机极光色团与微粒星尘响应鼠标引力，兼容 prefers-reduced-motion",
            "evidence_gap": "原站采用定制 WebGL 流体着色器，离线受控产物以稳定高帧率原生 2D Canvas 复刻",
            "bound_rule_id": "GU-01",
            "status": "open",
            "confirmed_at": None,
        },
        {
            "assumption_id": "ASM-DF-02",
            "eu_id": "eu_L3_df_portfolio_grid",
            "subject_ids": ["eu_L3_df_portfolio_grid"],
            "title": "Defined Frontier 投资组合与宣言条目数据口径",
            "category": "unobserved_interaction_payload",
            "assumed_value": "围绕 AI Frontier 主题补全可筛选投资组合矩阵与全屏宣言弹窗内容",
            "evidence_gap": "参考站首屏主要展示流体视觉与宣言入口，内页具体组合清单需按公开定位补齐",
            "bound_rule_id": "PW-04",
            "status": "open",
            "confirmed_at": None,
        },
    ],
}


# ==============================================================================
# 5 个 Web -> UI/UX 风格案例的统一参数化构建器（零重复、100%规则闭合）
# ==============================================================================
_WEB_STYLE_SPECS: dict[str, dict[str, Any]] = {
    "knob_hardware_web": {
        "prefix": "kb",
        "full_bleed": True,
        "keep_filter_edge": False,
        "root_name": "KNOB 工业硬件品牌发布页",
        "frame_url": "/cases/knob_hardware_web/frames/ref_knob_desktop.png",
        "data_source": "knob.hardware.telemetry",
        "rail_w": 0,
        "panel_radius": 18,
        "registry": {
            "surface_atoms": {
                "kb_surf_bg": {"name": "暗棚纯黑基底", "kind": "color", "value": "#080808", "css_var": "--kb-bg"},
                "kb_surf_chassis": {"name": "CNC 阳极氧化铝机身", "kind": "color", "value": "#1c1c1a", "css_var": "--kb-chassis"},
                "kb_surf_keycap": {"name": "磨砂暖灰键帽", "kind": "color", "value": "#c8c7c2", "css_var": "--kb-keycap"},
                "kb_surf_rust": {"name": "焦糖铁锈红功能键", "kind": "color", "value": "#8f2b14", "css_var": "--kb-rust"},
                "kb_surf_volt": {"name": "荧光黄绿行动胶囊", "kind": "color", "value": "#d4e600", "css_var": "--kb-volt"},
            },
            "typography_atoms": {
                "kb_typo_serif": {"name": "编辑感衬线主标题", "kind": "font_scale", "value": "clamp(34px, 3.8vw, 54px)", "css_var": "--kb-font-serif"},
                "kb_typo_body": {"name": "技术规格说明字阶", "kind": "font_scale", "value": "14px", "css_var": "--kb-font-body"},
                "kb_typo_mono": {"name": "LCD 屏幕等宽读数字阶", "kind": "font_scale", "value": "12px", "css_var": "--kb-font-mono"},
            },
            "layout_atoms": {
                "kb_lay_key": {"name": "物理键帽栅格尺寸", "kind": "dimension", "value": "56px", "css_var": "--kb-key-size"},
                "kb_lay_radius": {"name": "键帽与面板圆角", "kind": "radius", "value": "14px", "css_var": "--kb-radius"},
                "kb_lay_gap": {"name": "硬件组件间距", "kind": "spacing", "value": "18px", "css_var": "--kb-gap"},
            },
            "motion_atoms": {
                "kb_mot_dial": {"name": "滚轮旋钮物理阻尼曲线", "kind": "duration", "value": "220ms", "css_var": "--kb-dur-dial"},
                "kb_mot_key": {"name": "矮轴键帽触发行程", "kind": "duration", "value": "110ms", "css_var": "--kb-dur-key"},
            },
            "evidence_atoms": {
                "ev_kb_dom": {"name": "KNOB 全宽三断点与旋钮触觉快照", "breakpoints": [390, 768, 1440], "frame_ref": "ref_knob_desktop.png"},
            },
        },
        "nodes": {
            "hero_id": "eu_L3_kb_hardware_rig",
            "hero_name": "k.no.b.1 机械键盘与双旋钮控制台",
            "hero_feat_id": "eu_L4_kb_rotary_encoders",
            "hero_feat_name": "双滚花旋钮调参与琥珀 LCD 实时联动",
            "topbar_id": "eu_L3_kb_topbar",
            "topbar_name": "KNOB 品牌顶栏与邮件订阅入口",
            "topbar_feat_id": "eu_L4_kb_mode_tabs",
            "topbar_feat_name": "Keyboard/Numpad/Keysets/Lightswitch 切页",
            "array_id": "eu_L3_kb_specs_array",
            "array_name": "机械轴体与硬件规格四卡阵列",
            "array_count": 4,
            "dialog_id": "eu_L3_kb_order_dialog",
            "dialog_name": "预订配置与固件更新弹窗",
        },
        "bboxes": [
            {"bbox_id": "bb_kb_top", "eu_id": "eu_L3_kb_topbar", "label": "KNOB 水平顶栏与 Get Updates", "x": 16, "y": 16, "w": 1408, "h": 68, "role": "nav"},
            {"bbox_id": "bb_kb_rig", "eu_id": "eu_L3_kb_hardware_rig", "label": "全幅暗棚 Hero + k.no.b.1 倾斜键盘与双旋钮", "x": 16, "y": 96, "w": 1408, "h": 540, "role": "split"},
            {"bbox_id": "bb_kb_specs", "eu_id": "eu_L3_kb_specs_array", "label": "硬件规格与模式卡片阵列 ×4", "x": 16, "y": 650, "w": 1408, "h": 234, "role": "array"},
        ],
    },
    "nogood_brutal_web": {
        "prefix": "ng",
        "full_bleed": True,
        "keep_filter_edge": False,
        "root_name": "NoGood 新粗野主义全屏网格站",
        "frame_url": "/cases/nogood_brutal_web/frames/ref_nogood_desktop.png",
        "data_source": "nogood.studio.feed",
        "rail_w": 0,
        "panel_radius": 0,
        "registry": {
            "surface_atoms": {
                "ng_surf_acid": {"name": "酸性荧光绿全屏基底", "kind": "color", "value": "#c7f544", "css_var": "--ng-acid"},
                "ng_surf_ink": {"name": "纯黑锐利描边主字色", "kind": "color", "value": "#0b0b0a", "css_var": "--ng-ink"},
                "ng_surf_red": {"name": "朱红书刊撞色强调", "kind": "color", "value": "#e13726", "css_var": "--ng-red"},
                "ng_surf_paper": {"name": "插画米白画纸底", "kind": "color", "value": "#eae7df", "css_var": "--ng-paper"},
            },
            "typography_atoms": {
                "ng_typo_display": {"name": "粗野主义无衬线声明体", "kind": "font_scale", "value": "clamp(30px, 3.3vw, 46px)", "css_var": "--ng-font-display"},
                "ng_typo_mono": {"name": "系统日志与报价等宽体", "kind": "font_scale", "value": "12px", "css_var": "--ng-font-mono"},
                "ng_typo_body": {"name": "Bento 文案正文字阶", "kind": "font_scale", "value": "14px", "css_var": "--ng-font-body"},
            },
            "layout_atoms": {
                "ng_lay_navh": {"name": "硬边顶栏行高", "kind": "dimension", "value": "58px", "css_var": "--ng-nav-h"},
                "ng_lay_border": {"name": "零圆角黑线网格宽度", "kind": "spacing", "value": "1.5px", "css_var": "--ng-border-w"},
                "ng_lay_gap": {"name": "网格内边距单元", "kind": "spacing", "value": "16px", "css_var": "--ng-gap"},
            },
            "motion_atoms": {
                "ng_mot_marquee": {"name": "顶栏无限跑马灯周期", "kind": "duration", "value": "18s", "css_var": "--ng-dur-marquee"},
                "ng_mot_snap": {"name": "硬切反色微动效", "kind": "duration", "value": "120ms", "css_var": "--ng-dur-snap"},
            },
            "evidence_atoms": {
                "ev_ng_dom": {"name": "NoGood 无边框网格三断点快照", "breakpoints": [390, 768, 1440], "frame_ref": "ref_nogood_desktop.png"},
            },
        },
        "nodes": {
            "hero_id": "eu_L3_ng_artwork_hero",
            "hero_name": "赛博头盔插画与创作声明双栏区",
            "hero_feat_id": "eu_L4_ng_radio_toggle",
            "hero_feat_name": "NOGOOD RADIO 实时电台开关",
            "topbar_id": "eu_L3_ng_marquee_nav",
            "topbar_name": "跑马灯公告带与五格硬边顶栏",
            "topbar_feat_id": "eu_L4_ng_route_links",
            "topbar_feat_name": "Work / Sketchbook / Shop / About / Now 切换",
            "array_id": "eu_L3_ng_system_log",
            "array_name": "NOW / SHOP 画册 / SYSTEM LOG 三格列",
            "array_count": 3,
            "dialog_id": "eu_L3_ng_cart_dialog",
            "dialog_name": "购物车与画册下单硬边弹窗",
        },
        "bboxes": [
            {"bbox_id": "bb_ng_top", "eu_id": "eu_L3_ng_marquee_nav", "label": "滚动跑马灯 & 5格硬边顶栏", "x": 16, "y": 16, "w": 1408, "h": 92, "role": "nav"},
            {"bbox_id": "bb_ng_hero", "eu_id": "eu_L3_ng_artwork_hero", "label": "赛博头盔矢量插画 & 反叛创作宣言", "x": 16, "y": 116, "w": 968, "h": 768, "role": "split"},
            {"bbox_id": "bb_ng_log", "eu_id": "eu_L3_ng_system_log", "label": "NOW / NOGOOD VOL.1 / SYSTEM LOG ×3", "x": 992, "y": 116, "w": 432, "h": 768, "role": "array"},
        ],
    },
    "axiom_hud_web": {
        "prefix": "ax",
        "full_bleed": True,
        "keep_filter_edge": True,
        "root_name": "Axiom 极暗精工数据平台与 APL HUD",
        "frame_url": "/cases/axiom_hud_web/frames/ref_axiom_desktop.png",
        "data_source": "axiom.telemetry.apl_events",
        "rail_w": 0,
        "panel_radius": 8,
        "registry": {
            "surface_atoms": {
                "ax_surf_void": {"name": "深邃纯黑终端底色", "kind": "color", "value": "#050608", "css_var": "--ax-void"},
                "ax_surf_panel": {"name": "哑光暗夜 HUD 面板", "kind": "color", "value": "#0b0d11", "css_var": "--ax-panel"},
                "ax_surf_line": {"name": "1px 极细冷灰线框", "kind": "color", "value": "#1f242d", "css_var": "--ax-line"},
                "ax_surf_orange": {"name": "工业信号炽橙主色", "kind": "color", "value": "#e8642c", "css_var": "--ax-orange"},
                "ax_surf_ink": {"name": "纯白高对比主字色", "kind": "color", "value": "#f3f4f6", "css_var": "--ax-ink"},
            },
            "typography_atoms": {
                "ax_typo_h1": {"name": "终端宣言大字阶", "kind": "font_scale", "value": "clamp(34px, 4vw, 54px)", "css_var": "--ax-font-h1"},
                "ax_typo_code": {"name": "APL 查询等宽代码字阶", "kind": "font_scale", "value": "13px", "css_var": "--ax-font-code"},
                "ax_typo_body": {"name": "HUD 工具栏标签字阶", "kind": "font_scale", "value": "13.5px", "css_var": "--ax-font-body"},
            },
            "layout_atoms": {
                "ax_lay_maxw": {"name": "中心化 HUD 面板版心宽", "kind": "dimension", "value": "1240px", "css_var": "--ax-container-w"},
                "ax_lay_radius": {"name": "HUD 精工微圆角", "kind": "radius", "value": "8px", "css_var": "--ax-radius"},
                "ax_lay_gap": {"name": "网格间距", "kind": "spacing", "value": "14px", "css_var": "--ax-gap"},
            },
            "motion_atoms": {
                "ax_mot_run": {"name": "查询脉冲与图表刷新", "kind": "duration", "value": "180ms", "css_var": "--ax-dur-run"},
            },
            "evidence_atoms": {
                "ev_ax_dom": {"name": "Axiom 全宽开发平台与 APL 终端快照", "breakpoints": [390, 768, 1440], "frame_ref": "ref_axiom_desktop.png"},
            },
        },
        "nodes": {
            "hero_id": "eu_L3_ax_query_hud",
            "hero_name": "The modern machine data platform. + APL 查询 HUD",
            "hero_feat_id": "eu_L4_ax_apl_editor",
            "hero_feat_name": "Builder/Editor 切换 · Last 30 mins · Run 执行",
            "topbar_id": "eu_L3_ax_hero_deck",
            "topbar_name": "AXIOM 居中顶栏与 Start free 入口",
            "topbar_feat_id": "eu_L4_ax_cta_bar",
            "topbar_feat_name": "Platform / Solutions / Docs 导航与 Sign in",
            "array_id": "eu_L3_ax_results_array",
            "array_name": "支付失败聚合直方图与事件日志表阵列",
            "array_count": 4,
            "dialog_id": "eu_L3_ax_query_dialog",
            "dialog_name": "接入 Token 与快速开始弹窗",
        },
        "bboxes": [
            {"bbox_id": "bb_ax_top", "eu_id": "eu_L3_ax_hero_deck", "label": "AXIOM 居中平台顶栏 & The modern machine data platform.", "x": 16, "y": 16, "w": 1408, "h": 270, "role": "nav"},
            {"bbox_id": "bb_ax_hud", "eu_id": "eu_L3_ax_query_hud", "label": "全宽嵌入式 Query / Stream HUD · APL 编辑器 · Run", "x": 16, "y": 298, "w": 1408, "h": 320, "role": "split"},
            {"bbox_id": "bb_ax_res", "eu_id": "eu_L3_ax_results_array", "label": "Results 时序分布图与日志流 ×4", "x": 16, "y": 632, "w": 1408, "h": 252, "role": "array"},
        ],
    },
    "weeksync_paper_web": {
        "prefix": "ws",
        "root_name": "WeekSync 奶油纸感排班沙盒工作台",
        "frame_url": "/cases/weeksync_paper_web/frames/ref_weeksync_desktop.png",
        "data_source": "weeksync.planner.schedule",
        "rail_w": 200,
        "panel_radius": 24,
        "registry": {
            "surface_atoms": {
                "ws_surf_oat": {"name": "燕麦米纸外画布底", "kind": "color", "value": "#d7d4cb", "css_var": "--ws-oat"},
                "ws_surf_cream": {"name": "奶白卡片主纸基", "kind": "color", "value": "#f8f7f3", "css_var": "--ws-cream"},
                "ws_surf_stone": {"name": "浅石色任务标签块", "kind": "color", "value": "#ebeae4", "css_var": "--ws-stone"},
                "ws_surf_ink": {"name": "温暖墨黑印刷字色", "kind": "color", "value": "#181817", "css_var": "--ws-ink"},
                "ws_surf_sage": {"name": "鼠尾草浅黄绿点缀", "kind": "color", "value": "#dee499", "css_var": "--ws-sage"},
            },
            "typography_atoms": {
                "ws_typo_mono": {"name": "打字机等宽导航与工时字阶", "kind": "font_scale", "value": "12.5px", "css_var": "--ws-font-mono"},
                "ws_typo_body": {"name": "成员姓名与任务标签字阶", "kind": "font_scale", "value": "13.5px", "css_var": "--ws-font-body"},
                "ws_typo_head": {"name": "日期表头与总览标题字阶", "kind": "font_scale", "value": "18px", "css_var": "--ws-font-head"},
            },
            "layout_atoms": {
                "ws_lay_rail": {"name": "虚线边框侧栏宽度", "kind": "dimension", "value": "200px", "css_var": "--ws-rail-w"},
                "ws_lay_radius": {"name": "纸感卡片圆角", "kind": "radius", "value": "24px", "css_var": "--ws-radius"},
                "ws_lay_gap": {"name": "排班网格间距", "kind": "spacing", "value": "12px", "css_var": "--ws-gap"},
            },
            "motion_atoms": {
                "ws_mot_card": {"name": "排班增删与协同光标微动效", "kind": "duration", "value": "200ms", "css_var": "--ws-dur-ui"},
            },
            "evidence_atoms": {
                "ev_ws_dom": {"name": "WeekSync 三断点与工时沙盒快照", "breakpoints": [390, 768, 1440], "frame_ref": "ref_weeksync_desktop.png"},
            },
        },
        "nodes": {
            "nav_name": "虚线框单选导航导轨",
            "nav_kind": "component.dotted_rail",
            "hero_id": "eu_L3_ws_planner_grid",
            "hero_name": "Try It 免登可编辑周排班沙盒",
            "hero_feat_id": "eu_L4_ws_hours_calc",
            "hero_feat_name": "+/- 实时增删工时与多人气泡光标",
            "topbar_id": "eu_L3_ws_week_header",
            "topbar_name": "23 Nov – 29 Nov 周历表头与筛选栏",
            "topbar_feat_id": "eu_L4_ws_days_weeks",
            "topbar_feat_name": "Days/Weeks 切换与周报 CSV 导出",
            "array_id": "eu_L3_ws_summary_cards",
            "array_name": "成员周工时配额汇总阵列",
            "array_count": 3,
            "dialog_id": "eu_L3_ws_task_dialog",
            "dialog_name": "新增排班任务弹窗",
        },
        "bboxes": [
            {"bbox_id": "bb_ws_nav", "eu_id": "eu_L3_ws_rail_dock", "label": "虚线框导航导轨 (Try It)", "x": 18, "y": 18, "w": 200, "h": 864, "role": "nav"},
            {"bbox_id": "bb_ws_head", "eu_id": "eu_L3_ws_week_header", "label": "23–29 Nov 表头与 Days/Weeks", "x": 236, "y": 18, "w": 1186, "h": 88, "role": "stage"},
            {"bbox_id": "bb_ws_grid", "eu_id": "eu_L3_ws_planner_grid", "label": "实时增删工时排班沙盒 & 协作光标", "x": 236, "y": 118, "w": 1186, "h": 540, "role": "split"},
            {"bbox_id": "bb_ws_sum", "eu_id": "eu_L3_ws_summary_cards", "label": "成员工时汇总与能力卡 ×3", "x": 236, "y": 674, "w": 1186, "h": 208, "role": "array"},
        ],
    },
    "defined_aurora_web": {
        "prefix": "df",
        "full_bleed": True,
        "keep_filter_edge": False,
        "root_name": "Defined 全幅极光磁流体空间页",
        "frame_url": "/cases/defined_aurora_web/frames/ref_defined_desktop.png",
        "data_source": "defined.frontier.portfolio",
        "rail_w": 0,
        "panel_radius": 0,
        "registry": {
            "surface_atoms": {
                "df_surf_black": {"name": "锐利纯黑 L 型几何遮罩", "kind": "color", "value": "#000000", "css_var": "--df-black"},
                "df_surf_ink": {"name": "纯白标语高对比字色", "kind": "color", "value": "#ffffff", "css_var": "--df-ink"},
                "df_surf_cobalt": {"name": "钴蓝极光磁流体色", "kind": "color", "value": "#0055ff", "css_var": "--df-cobalt"},
                "df_surf_magenta": {"name": "洋红霓虹色散核心", "kind": "color", "value": "#ff2a85", "css_var": "--df-magenta"},
                "df_surf_gold": {"name": "熔金微粒星尘高光", "kind": "color", "value": "#f5c438", "css_var": "--df-gold"},
            },
            "typography_atoms": {
                "df_typo_hero": {"name": "Build the AI Frontier 大字阶", "kind": "font_scale", "value": "clamp(40px, 5.4vw, 76px)", "css_var": "--df-font-hero"},
                "df_typo_body": {"name": "宣言正文与导航字阶", "kind": "font_scale", "value": "14px", "css_var": "--df-font-body"},
                "df_typo_caption": {"name": "领域标签与年份字阶", "kind": "font_scale", "value": "11.5px", "css_var": "--df-font-caption"},
            },
            "layout_atoms": {
                "df_lay_cutw": {"name": "L 型纯黑切块宽度", "kind": "dimension", "value": "540px", "css_var": "--df-cut-w"},
                "df_lay_gap": {"name": "几何框留白间距", "kind": "spacing", "value": "20px", "css_var": "--df-gap"},
            },
            "motion_atoms": {
                "df_mot_fluid": {"name": "极光流体波纹过渡周期", "kind": "duration", "value": "340ms", "css_var": "--df-dur-fluid"},
            },
            "evidence_atoms": {
                "ev_df_dom": {"name": "Defined 无侧栏全幅极光与黑框快照", "breakpoints": [390, 768, 1440], "frame_ref": "ref_defined_desktop.png"},
            },
        },
        "nodes": {
            "hero_id": "eu_L3_df_aurora_stage",
            "hero_name": "全幅 Canvas 极光磁流体与纯黑 L 型宣言框",
            "hero_feat_id": "eu_L4_df_ferrofluid_canvas",
            "hero_feat_name": "指针引力扰动粒子与极光色团",
            "topbar_id": "eu_L3_df_brand_menu",
            "topbar_name": "defined® 悬浮徽标与四点矩阵切换",
            "topbar_feat_id": "eu_L4_df_view_matrix",
            "topbar_feat_name": "Frontier / Portfolio / Manifesto 矩阵路由",
            "array_id": "eu_L3_df_portfolio_grid",
            "array_name": "AI Frontier 投资组合极简阵列",
            "array_count": 4,
            "dialog_id": "eu_L3_df_manifesto_dialog",
            "dialog_name": "全屏极简宣言模态浮层",
        },
        "bboxes": [
            {"bbox_id": "bb_df_top", "eu_id": "eu_L3_df_brand_menu", "label": "defined® & 4-Dot 矩阵按钮", "x": 16, "y": 16, "w": 1408, "h": 68, "role": "nav"},
            {"bbox_id": "bb_df_stage", "eu_id": "eu_L3_df_aurora_stage", "label": "全屏磁流体 Canvas + 纯黑 L 型 Build the AI Frontier®", "x": 16, "y": 96, "w": 1408, "h": 580, "role": "split"},
            {"bbox_id": "bb_df_port", "eu_id": "eu_L3_df_portfolio_grid", "label": "AI Frontier 投资组合卡片阵列 ×4", "x": 16, "y": 690, "w": 1408, "h": 194, "role": "array"},
        ],
    },
}


def _build_web_style_skeleton(case_id: str) -> dict[str, Any]:
    spec = _WEB_STYLE_SPECS[case_id]
    p = spec["prefix"]
    is_full = bool(spec.get("full_bleed", False))
    rail_w = int(spec["rail_w"])
    stage_x = 16 if is_full else (16 + rail_w + 16)
    stage_w = 1440 - stage_x - 16 if is_full else (1440 - stage_x - 20)
    root_id = f"eu_L0_{p}_workspace"
    nav_l1 = f"eu_L1_{p}_nav"
    nav_l2 = f"eu_L2_{p}_nav_rail"
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
            1440: (stage_x, 16, stage_w, 100),
        },
        hero_l2: {
            390: (12, 150 if is_full else 218, 366, 780),
            768: (18 if is_full else 114, 150, 732 if is_full else 636, 620),
            1440: (stage_x, 126, stage_w, 510),
        },
        arr_l2: {
            390: (12, 950 if is_full else 1012, 366, 600),
            768: (18 if is_full else 114, 782, 732 if is_full else 636, 370),
            1440: (stage_x, 646, stage_w, 238),
        },
        ov_l1: {390: (16, 140, 358, 360), 768: (140, 150, 488, 380), 1440: (420, 170, 580, 410)},
        ov_l2: {390: (16, 140, 358, 360), 768: (140, 150, 488, 380), 1440: (420, 170, 580, 410)},
    }
    if not is_full:
        rect_specs[nav_l1] = {390: (12, 46, 366, 60), 768: (18, 48, 84, 1120), 1440: (16, 16, rail_w, 868)}
        rect_specs[nav_l2] = {390: (12, 46, 366, 60), 768: (18, 48, 84, 1120), 1440: (16, 16, rail_w, 868)}

    dom = base_cat._build_three_breakpoint_rects(root_id, rect_specs)

    reg = spec["registry"]
    first_surf = next(iter(reg["surface_atoms"].items()))
    first_typo = next(iter(reg["typography_atoms"].items()))
    first_lay = next(iter(reg["layout_atoms"].items()))
    first_mot = next(iter(reg["motion_atoms"].items()))
    nodes_meta = spec["nodes"]

    computed_styles = [
        {"id": f"{p}_cs_surf", "eu_id": nodes_meta["topbar_id"], "property": "color", "value": first_surf[1]["value"], "token_ref": first_surf[0], "delta_e": 0.0},
        {"id": f"{p}_cs_typo", "eu_id": nodes_meta["hero_id"], "property": "font-size", "value": first_typo[1]["value"], "token_ref": first_typo[0], "delta_e": 0.0},
        {"id": f"{p}_cs_lay", "eu_id": nodes_meta["array_id"], "property": "gap", "value": first_lay[1]["value"], "token_ref": first_lay[0], "delta_e": 0.0},
        {"id": f"{p}_cs_mot", "eu_id": nodes_meta["topbar_id"] if is_full else f"eu_L3_{p}_rail_dock", "property": "transition-duration", "value": first_mot[1]["value"], "token_ref": first_mot[0], "delta_e": 0.0},
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
        {"id": f"{p}_el_top", "eu_id": nodes_meta["topbar_id"], "role": "tab", "accessible_name": nodes_meta["topbar_name"], "states": ["default", "hover", "focus-visible", "active"]},
        {"id": f"{p}_el_hero", "eu_id": nodes_meta["hero_id"], "role": "button", "accessible_name": nodes_meta["hero_name"], "states": ["default", "hover", "focus-visible", "active"]},
        {"id": f"{p}_el_dlg", "eu_id": nodes_meta["dialog_id"], "role": "dialog", "accessible_name": nodes_meta["dialog_name"], "states": ["default", "hover", "focus-visible", "active"]},
    ]
    if not is_full:
        interactive_elements.insert(
            1,
            {"id": f"{p}_el_rail", "eu_id": f"eu_L3_{p}_rail_dock", "role": "link", "accessible_name": nodes_meta["nav_name"], "states": ["default", "hover", "focus-visible", "active"]},
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
            {"id": f"{p}_cn_hero", "eu_id": nodes_meta["hero_id"], "content_class": "data", "aria_hidden": False, "data_source": spec["data_source"], "children_classes": ["data"]},
            {"id": f"{p}_cn_arr", "eu_id": nodes_meta["array_id"], "content_class": "data", "aria_hidden": False, "data_source": f"{spec['data_source']}.items", "children_classes": ["data"]},
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


def _build_web_style_eu_tree(case_id: str, finalize_fn: Callable[..., dict[str, Any]]) -> dict[str, Any]:
    spec = _WEB_STYLE_SPECS[case_id]
    p = spec["prefix"]
    is_full = bool(spec.get("full_bleed", False))
    keep_filter = bool(spec.get("keep_filter_edge", True))
    reg = spec["registry"]
    ev_id = f"ev_{p}_dom"
    surf_ids = list(reg["surface_atoms"].keys())
    typo_ids = list(reg["typography_atoms"].keys())
    lay_ids = list(reg["layout_atoms"].keys())
    mot_ids = list(reg["motion_atoms"].keys())
    all_design_atoms = surf_ids + typo_ids + lay_ids + mot_ids + [ev_id]
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
            {"eu_id": f"eu_L5_{p}_rail_atoms", "name": "导轨全量样式动效原子束", "level": "L5", "node_kind": "atom.bundle", "parent_id": rail_prox_id, "adaptation_mode": "ATOMIC_MOUNT", "atom_refs": all_design_atoms},
        ])

    nodes.extend([
        {"eu_id": f"eu_L1_{p}_stage", "name": "全宽主舞台领地" if is_full else "独立滚动主舞台领地", "level": "L1", "node_kind": "territory.main_stage", "parent_id": root_id, "template_slot": "main_stage", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [stage_x, 16, stage_w, 868], "rendered": True},
        {"eu_id": f"eu_L2_{p}_topbar", "name": "顶栏导航与操作带", "level": "L2", "node_kind": "region.topbar", "parent_id": f"eu_L1_{p}_stage", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [stage_x, 16, stage_w, 100]},
        {"eu_id": nm["topbar_id"], "name": nm["topbar_name"], "level": "L3", "entity": True, "node_kind": "component.stage_topbar", "parent_id": f"eu_L2_{p}_topbar", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [stage_x, 16, stage_w, 100], "dom_selector": f'[data-eu-id="{nm["topbar_id"]}"]', "rendered": True},
        {"eu_id": nm["topbar_feat_id"], "name": nm["topbar_feat_name"], "level": "L4", "motion": True, "node_kind": "feature.route_switch", "parent_id": nm["topbar_id"], "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [stage_x, 16, stage_w, 100], "rendered": True},
        {"eu_id": f"eu_L5_{p}_top_atoms", "name": "顶栏全量样式动效原子束" if is_full else "顶栏原子束", "level": "L5", "node_kind": "atom.bundle", "parent_id": nm["topbar_feat_id"], "adaptation_mode": "ATOMIC_MOUNT", "atom_refs": all_design_atoms},

        {"eu_id": f"eu_L2_{p}_hero_zone", "name": "核心交互主展区", "level": "L2", "node_kind": "region.hero_stage", "parent_id": f"eu_L1_{p}_stage", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [stage_x, 126, stage_w, 510]},
        {"eu_id": nm["hero_id"], "name": nm["hero_name"], "level": "L3", "entity": True, "interaction_density": 4, "node_kind": "component.primary_interactive", "parent_id": f"eu_L2_{p}_hero_zone", "adaptation_mode": "SPLIT_HIGH_INTERACTION", "envelope_bbox": [stage_x, 126, stage_w, 510], "dom_selector": f'[data-eu-id="{nm["hero_id"]}"]', "rendered": True},
        {"eu_id": nm["hero_feat_id"], "name": nm["hero_feat_name"], "level": "L4", "motion": True, "node_kind": "feature.primary_control", "parent_id": nm["hero_id"], "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [stage_x, 126, stage_w, 510], "rendered": True},
        {"eu_id": f"eu_L5_{p}_hero_atoms", "name": "核心交互区原子束", "level": "L5", "node_kind": "atom.bundle", "parent_id": nm["hero_feat_id"], "adaptation_mode": "ATOMIC_MOUNT", "atom_refs": all_design_atoms},

        {"eu_id": f"eu_L2_{p}_array_zone", "name": "下方结构化阵列带", "level": "L2", "node_kind": "region.lower_array", "parent_id": f"eu_L1_{p}_stage", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [stage_x, 646, stage_w, 238]},
        {"eu_id": nm["array_id"], "name": nm["array_name"], "level": "L3", "entity": True, "node_kind": "component.spec.array", "parent_id": f"eu_L2_{p}_array_zone", "adaptation_mode": "FOLD_ARRAY", "array_count": int(nm["array_count"]), "envelope_bbox": [stage_x, 646, stage_w, 238], "dom_selector": f'[data-eu-id="{nm["array_id"]}"]', "rendered": True},
        {"eu_id": f"eu_L4_{p}_filter_export", "name": "同构条目筛选与结构特征" if not keep_filter else "同构条目筛选与 CSV 导出", "level": "L4", "node_kind": "feature.filter_export", "parent_id": nm["array_id"], "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [stage_x, 646, stage_w, 238], "rendered": True},
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
        edges.append({"edge_id": f"edge_{p}_filter", "edge_type": "FILTERS_VIEW", "source_eu_id": nm["hero_id"], "target_eu_id": nm["array_id"], "label": "参数筛选联动数组与同口径 CSV 导出", "evidence_ref": ev_id})
    edges.extend([
        {"edge_id": f"edge_{p}_focus", "edge_type": "RESTORES_FOCUS", "source_eu_id": nm["dialog_id"], "target_eu_id": nm["topbar_id"], "label": "模态对话框关闭后焦点归还触发控件", "evidence_ref": ev_id},
        {"edge_id": f"edge_{p}_token", "edge_type": "SHARES_TOKEN", "source_eu_id": nm["hero_id"], "target_eu_id": nm["array_id"], "label": "共享风格表面色、字阶与圆角 Token", "evidence_ref": ev_id},
    ])
    return finalize_fn("tpl_uiux_workspace_v1", "UI/UX 工作台原型", root_id, nodes, reg, edges)


# ==============================================================================
# 4. 瑞士国际主义展板：MONOLOG (image -> GN -> graphic, ISO A3 12 栏网格)
# ==============================================================================
def _monolog_col_span(c1: int, c2: int) -> tuple[float, float]:
    col_w = 229.0 / 12.0
    x = 12.0 + (c1 - 1) * (col_w + 4.0)
    w = (c2 - c1 + 1) * col_w + (c2 - c1) * 4.0
    return round(x, 4), round(w, 4)


def build_image_skeleton_monolog() -> dict[str, Any]:
    col_w = 229.0 / 12.0
    x1_6, w1_6 = _monolog_col_span(1, 6)
    x7_12, w7_12 = _monolog_col_span(7, 12)
    x1_4, w1_4 = _monolog_col_span(1, 4)
    x5_12, w5_12 = _monolog_col_span(5, 12)
    x1_8, w1_8 = _monolog_col_span(1, 8)
    x9_12, w9_12 = _monolog_col_span(9, 12)

    bboxes: list[dict[str, Any]] = [
        {"bbox_id": "bb_mn_header", "eu_id": "eu_L1_mn_header", "label": "MONOLOG 页眉 (Col 1–12)", "x": 12.0, "y": 14.0, "w": 273.0, "h": 28.0, "role": "nav"},
        {"bbox_id": "bb_mn_logo", "eu_id": "eu_L3_mn_logo_lockup", "label": "MONOLOG 标志与导航 (Col 1–6)", "x": x1_6, "y": 14.0, "w": w1_6, "h": 28.0, "role": "nav"},
        {"bbox_id": "bb_mn_cta", "eu_id": "eu_L3_mn_cta_pill", "label": "Start a project ↗ (Col 7–12)", "x": x7_12, "y": 14.0, "w": w7_12, "h": 28.0, "role": "stage"},
        {"bbox_id": "bb_mn_intro", "eu_id": "eu_L3_mn_intro_copy", "label": "B2B 定位声明左栏 (Col 1–4)", "x": x1_4, "y": 48.0, "w": w1_4, "h": 190.0, "role": "stage"},
        {"bbox_id": "bb_mn_head", "eu_id": "eu_L3_mn_headline", "label": "巨型紧字距黑体主标题 (Col 5–12)", "x": x5_12, "y": 48.0, "w": w5_12, "h": 190.0, "role": "split"},
        {"bbox_id": "bb_mn_wins", "eu_id": "eu_L3_mn_wins_graphic", "label": "CLIENT WINS 纯矢量建筑图 (Col 1–6)", "x": x1_6, "y": 244.0, "w": w1_6, "h": 76.0, "role": "split"},
        {"bbox_id": "bb_mn_pal", "eu_id": "eu_L3_mn_palette_fold", "label": "报纸暖灰四色卡阵列 ×4 (Col 7–12)", "x": x7_12, "y": 244.0, "w": w7_12, "h": 76.0, "role": "array"},
        {"bbox_id": "bb_mn_spec", "eu_id": "eu_L3_mn_specimen", "label": "瑞士印刷字阶样张 (Col 1–8)", "x": x1_8, "y": 326.0, "w": w1_8, "h": 50.0, "role": "stage"},
        {"bbox_id": "bb_mn_grid", "eu_id": "eu_L3_mn_grid_box", "label": "12 栏瑞士网格参数卡 (Col 9–12)", "x": x9_12, "y": 326.0, "w": w9_12, "h": 50.0, "role": "array"},
        {"bbox_id": "bb_mn_foot", "eu_id": "eu_L1_mn_footer", "label": "版权页脚与印记 (Col 1–12)", "x": 12.0, "y": 382.0, "w": 273.0, "h": 24.0, "role": "nav"},
    ]
    svg_parts: list[str] = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 297 420" width="100%" height="100%" data-modality="image">',
        "  <defs><style>.sk-box{cursor:pointer;}.sk-tag{font-family:Manrope,sans-serif;font-size:4.2px;font-weight:700;pointer-events:none;}</style></defs>",
        '  <rect x="0" y="0" width="297" height="420" fill="#d9dad6"/>',
        '  <image id="skeleton-bg-frame" href="/cases/monolog_swiss_poster/frames/ref_monolog_poster.png" x="12" y="14" width="273" height="220" preserveAspectRatio="xMidYMid slice" opacity="0.32"/>',
        '  <g data-layer="skeleton">',
        '    <rect x="3" y="3" width="291" height="414" fill="none" stroke="#b94130" stroke-width="0.6" stroke-dasharray="2 1.5"/>',
        '    <rect x="12" y="12" width="273" height="396" fill="none" stroke="#111111" stroke-width="0.5" stroke-dasharray="1.5 1.5"/>',
    ]
    for c in range(12):
        cx = 12.0 + c * (col_w + 4.0)
        svg_parts.append(f'    <rect x="{cx:.2f}" y="12" width="{col_w:.2f}" height="396" fill="rgba(17,17,17,0.04)" stroke="rgba(17,17,17,0.16)" stroke-width="0.25"/>')
    svg_parts.append("  </g>")
    svg_parts.append('  <g data-layer="bbox">')
    for b in bboxes:
        stroke, fill = base_cat.ROLE_COLORS.get(b["role"], ("#0ea5e9", "rgba(14,165,233,0.12)"))
        svg_parts.append(
            f'    <g class="sk-node" data-eu-id="{b["eu_id"]}" data-segment-id="seg_poster_full">'
            f'<rect class="sk-box" data-eu-id="{b["eu_id"]}" x="{b["x"]}" y="{b["y"]}" width="{b["w"]}" height="{b["h"]}" rx="2.5" fill="{fill}" stroke="{stroke}" stroke-width="0.9"/>'
            f'<rect x="{b["x"] + 1}" y="{b["y"] + 1}" width="{min(b["w"] - 2, max(36, len(b["label"]) * 2.2))}" height="7.5" rx="1.5" fill="{stroke}" fill-opacity="0.92"/>'
            f'<text class="sk-tag" x="{b["x"] + 2.5}" y="{b["y"] + 6.2}" fill="#ffffff">{base_cat._escape_xml(b["label"])}</text>'
            "</g>"
        )
    svg_parts.extend(["  </g>", "</svg>"])

    return {
        "case_id": "monolog_swiss_poster",
        "modality": "image",
        "duration_sec": None,
        "coverage_ratio": 1.0,
        "viewport": {"width": 297.0, "height": 420.0, "unit": "mm", "format": "ISO_A3"},
        "source_image": {"url": "/cases/monolog_swiss_poster/frames/ref_monolog_poster.png", "w": 297.0, "h": 420.0, "unit": "mm"},
        "canvas": {"w": 297.0, "h": 420.0, "unit": "mm", "bleed_mm": 3.0, "declared_ratio": round(297.0 / 420.0, 4)},
        "grid": {"columns": 12, "margin_left": 12.0, "margin_right": 12.0, "gutter": 4.0, "column_width": col_w},
        "layers": [
            {"layer_id": "lyr_mn_paper", "layer_role": "background_material", "contains_text": False, "desc": "报纸暖灰 (#D9DAD6) 颗粒纸基与浅灰图形水印"},
            {"layer_id": "lyr_mn_vector", "layer_role": "foreground_graphic", "contains_text": False, "desc": "纯 SVG 建筑结构线稿与色卡色块"},
            {"layer_id": "lyr_mn_type", "layer_role": "foreground_text", "contains_text": True, "desc": "52/26/14/11px 瑞士排版活文字"},
        ],
        "noise_regions": [],
        "segments": [
            {
                "segment_id": "seg_poster_full",
                "index": 1,
                "t0": 0.0,
                "t1": 1.0,
                "label": "ISO A3 报纸暖灰瑞士网格全幅",
                "frame_url": "/cases/monolog_swiss_poster/frames/ref_monolog_poster.png",
                "active_eu_ids": [b["eu_id"] for b in bboxes],
                "bboxes": bboxes,
            }
        ],
        "bboxes": [dict(b, segment_id="seg_poster_full", color_role=b["role"]) for b in bboxes],
        "skeleton_svg": "\n".join(svg_parts),
    }


def build_eu_tree_monolog_poster(finalize_fn: Callable[..., dict[str, Any]]) -> dict[str, Any]:
    x1_6, w1_6 = _monolog_col_span(1, 6)
    x7_12, w7_12 = _monolog_col_span(7, 12)
    x1_4, w1_4 = _monolog_col_span(1, 4)
    x5_12, w5_12 = _monolog_col_span(5, 12)
    x1_8, w1_8 = _monolog_col_span(1, 8)
    x9_12, w9_12 = _monolog_col_span(9, 12)

    reg: dict[str, dict[str, Any]] = {
        "surface_atoms": {
            "mn_surf_paper": {"name": "报纸暖灰纸基", "kind": "color", "value": "#d9dad6", "css_var": "--mn-paper"},
            "mn_surf_ink": {"name": "纯黑印刷主字色", "kind": "color", "value": "#111111", "css_var": "--mn-ink"},
            "mn_surf_muted": {"name": "深岩灰辅助说明色", "kind": "color", "value": "#383936", "css_var": "--mn-muted"},
            "mn_surf_accent": {"name": "深炭黑徽标框底色", "kind": "color", "value": "#262825", "css_var": "--mn-accent"},
        },
        "typography_atoms": {
            "mn_typo_display": {"name": "巨型宣言黑体字阶", "kind": "font_scale", "value": "52px", "size_px": 52.0, "css_var": "--mn-font-display"},
            "mn_typo_headline": {"name": "二级小标题字阶", "kind": "font_scale", "value": "26px", "size_px": 26.0, "css_var": "--mn-font-headline"},
            "mn_typo_body": {"name": "左栏说明正文字阶", "kind": "font_scale", "value": "14px", "size_px": 14.0, "css_var": "--mn-font-body"},
            "mn_typo_caption": {"name": "括号注释与页脚字阶", "kind": "font_scale", "value": "11px", "size_px": 11.0, "css_var": "--mn-font-caption"},
        },
        "layout_atoms": {
            "mn_lay_unit": {"name": "瑞士网格基础单位", "kind": "spacing", "value": 16, "css_var": "--mn-unit"},
            "mn_lay_gutter": {"name": "12 栏槽宽间距", "kind": "spacing", "value": 12, "css_var": "--mn-gutter"},
        },
        "motion_atoms": {},
        "evidence_atoms": {
            "ev_mn_poster": {"name": "MONOLOG ISO A3 12 栏扫描坐标", "frame_ref": "ref_monolog_poster.png", "evidence_bbox": [12.0, 14.0, 273.0, 392.0]},
        },
    }

    nodes: list[dict[str, Any]] = [
        {"eu_id": "eu_L0_mn_poster", "name": "MONOLOG · 瑞士杂志网格展板", "level": "L0", "node_kind": "product.poster", "parent_id": None, "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [0.0, 0.0, 297.0, 420.0], "role": "background_material", "rendered": True},

        {"eu_id": "eu_L1_mn_header", "name": "品牌页眉领地", "level": "L1", "node_kind": "territory.header_brand", "parent_id": "eu_L0_mn_poster", "template_slot": "header_brand", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [12.0, 14.0, 273.0, 28.0], "rendered": True},
        {"eu_id": "eu_L2_mn_logo_region", "name": "MONOLOG 标志与单行导航区", "level": "L2", "node_kind": "region.logo", "parent_id": "eu_L1_mn_header", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [x1_6, 14.0, w1_6, 28.0], "source": "parsed", "evidence_bbox": [x1_6, 14.0, w1_6, 28.0]},
        {"eu_id": "eu_L3_mn_logo_lockup", "name": "MONOLOG 字标与 About/Work 导航", "level": "L3", "entity": True, "node_kind": "component.logo_lockup", "parent_id": "eu_L2_mn_logo_region", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [x1_6, 14.0, w1_6, 28.0], "source": "parsed", "evidence_bbox": [x1_6, 14.0, w1_6, 28.0], "carries_text": True, "rendered_as": "dom_text", "rendered": True},
        {"eu_id": "eu_L4_mn_logo_feat", "name": "字标锁定与单行导览特征", "level": "L4", "node_kind": "feature.logo_nav", "parent_id": "eu_L3_mn_logo_lockup", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [x1_6, 14.0, w1_6, 28.0]},
        {"eu_id": "eu_L5_mn_logo_atoms", "name": "页眉标志原子", "level": "L5", "node_kind": "atom.bundle", "parent_id": "eu_L4_mn_logo_feat", "adaptation_mode": "ATOMIC_MOUNT", "atom_refs": ["mn_surf_ink", "mn_surf_paper", "mn_typo_body", "mn_lay_gutter", "ev_mn_poster"]},

        {"eu_id": "eu_L2_mn_cta_region", "name": "右栏 Start a project 矩形区", "level": "L2", "node_kind": "region.issue_meta", "parent_id": "eu_L1_mn_header", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [x7_12, 14.0, w7_12, 28.0], "source": "parsed", "evidence_bbox": [x7_12, 14.0, w7_12, 28.0]},
        {"eu_id": "eu_L3_mn_cta_pill", "name": "Start a project ↗ 与版本胶囊", "level": "L3", "entity": True, "node_kind": "component.issue_badge", "parent_id": "eu_L2_mn_cta_region", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [x7_12, 14.0, w7_12, 28.0], "source": "parsed", "evidence_bbox": [x7_12, 14.0, w7_12, 28.0], "carries_text": True, "rendered_as": "dom_text", "rendered": True},
        {"eu_id": "eu_L4_mn_cta_feat", "name": "斜箭头矩形按钮特征", "level": "L4", "node_kind": "feature.issue_stamp", "parent_id": "eu_L3_mn_cta_pill", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [x7_12, 14.0, w7_12, 28.0]},
        {"eu_id": "eu_L5_mn_cta_atoms", "name": "页眉矩形原子", "level": "L5", "node_kind": "atom.bundle", "parent_id": "eu_L4_mn_cta_feat", "adaptation_mode": "ATOMIC_MOUNT", "atom_refs": ["mn_surf_ink", "mn_surf_paper", "mn_typo_caption", "mn_lay_gutter", "ev_mn_poster"]},

        {"eu_id": "eu_L1_mn_hero", "name": "非对称主视觉领地", "level": "L1", "node_kind": "territory.hero_key_visual", "parent_id": "eu_L0_mn_poster", "template_slot": "hero_key_visual", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [12.0, 48.0, 273.0, 190.0], "rendered": True},
        {"eu_id": "eu_L2_mn_intro_col", "name": "左窄栏 B2B 简介列 (Col 1–4)", "level": "L2", "node_kind": "region.intro_col", "parent_id": "eu_L1_mn_hero", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [x1_4, 48.0, w1_4, 190.0], "source": "parsed", "evidence_bbox": [x1_4, 48.0, w1_4, 190.0]},
        {"eu_id": "eu_L3_mn_intro_copy", "name": "B2B 定位声明与括号注释", "level": "L3", "entity": True, "node_kind": "component.intro_copy", "parent_id": "eu_L2_mn_intro_col", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [x1_4, 48.0, w1_4, 190.0], "source": "parsed", "evidence_bbox": [x1_4, 48.0, w1_4, 190.0], "carries_text": True, "rendered_as": "dom_text", "rendered": True},
        {"eu_id": "eu_L4_mn_intro_feat", "name": "左栏克制正文与括号脚注特征", "level": "L4", "node_kind": "feature.intro_hierarchy", "parent_id": "eu_L3_mn_intro_copy", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [x1_4, 48.0, w1_4, 190.0]},
        {"eu_id": "eu_L5_mn_intro_atoms", "name": "左栏排版原子", "level": "L5", "node_kind": "atom.bundle", "parent_id": "eu_L4_mn_intro_feat", "adaptation_mode": "ATOMIC_MOUNT", "atom_refs": ["mn_surf_muted", "mn_typo_body", "mn_typo_caption", "mn_lay_unit", "ev_mn_poster"]},

        {"eu_id": "eu_L2_mn_headline_col", "name": "右宽栏巨型黑体宣言区 (Col 5–12)", "level": "L2", "node_kind": "region.headline", "parent_id": "eu_L1_mn_hero", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [x5_12, 48.0, w5_12, 190.0], "source": "parsed", "evidence_bbox": [x5_12, 48.0, w5_12, 190.0]},
        {"eu_id": "eu_L3_mn_headline", "name": "巨型紧字距黑体主标题", "level": "L3", "entity": True, "node_kind": "component.headline", "parent_id": "eu_L2_mn_headline_col", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [x5_12, 48.0, w5_12, 190.0], "source": "parsed", "evidence_bbox": [x5_12, 48.0, w5_12, 190.0], "carries_text": True, "rendered_as": "dom_text", "rendered": True},
        {"eu_id": "eu_L4_mn_type_hierarchy", "name": "52/26/14/11px 四级字阶阶梯", "level": "L4", "node_kind": "feature.type_hierarchy", "parent_id": "eu_L3_mn_headline", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [x5_12, 48.0, w5_12, 140.0]},
        {"eu_id": "eu_L4_mn_bleed_crop", "name": "A3 3mm 出血与 12mm 安全框特征", "level": "L4", "node_kind": "feature.bleed_safe", "parent_id": "eu_L3_mn_headline", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [x5_12, 188.0, w5_12, 50.0], "rendered": True},
        {"eu_id": "eu_L5_mn_head_atoms", "name": "主标题原子", "level": "L5", "node_kind": "atom.bundle", "parent_id": "eu_L4_mn_type_hierarchy", "adaptation_mode": "ATOMIC_MOUNT", "atom_refs": ["mn_surf_ink", "mn_surf_paper", "mn_typo_display", "mn_lay_unit", "ev_mn_poster"]},
        {"eu_id": "eu_L5_mn_bleed_atoms", "name": "出血安全框原子", "level": "L5", "node_kind": "atom.bundle", "parent_id": "eu_L4_mn_bleed_crop", "adaptation_mode": "ATOMIC_MOUNT", "atom_refs": ["mn_surf_accent", "mn_typo_caption", "mn_lay_gutter", "ev_mn_poster"]},

        {"eu_id": "eu_L1_mn_spec_grid", "name": "战绩规格与色卡领地", "level": "L1", "node_kind": "territory.spec_grid", "parent_id": "eu_L0_mn_poster", "template_slot": "spec_grid", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [12.0, 244.0, 273.0, 132.0], "rendered": True},
        {"eu_id": "eu_L2_mn_wins_region", "name": "CLIENT WINS 战绩插画区 (Col 1–6)", "level": "L2", "node_kind": "region.key_graphic", "parent_id": "eu_L1_mn_spec_grid", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [x1_6, 244.0, w1_6, 76.0], "source": "parsed", "evidence_bbox": [x1_6, 244.0, w1_6, 76.0]},
        {"eu_id": "eu_L3_mn_wins_graphic", "name": "CLIENT WINS 2026 纯矢量建筑透视图", "level": "L3", "entity": True, "node_kind": "component.vector_graphic", "parent_id": "eu_L2_mn_wins_region", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [x1_6, 244.0, w1_6, 76.0], "source": "parsed", "evidence_bbox": [x1_6, 244.0, w1_6, 76.0], "layer_role": "foreground_graphic", "rendered_as": "svg_shape", "rendered": True},
        {"eu_id": "eu_L4_mn_wins_feat", "name": "建筑几何透视 SVG 图层", "level": "L4", "node_kind": "feature.vector_arch", "parent_id": "eu_L3_mn_wins_graphic", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [x1_6, 244.0, w1_6, 76.0]},
        {"eu_id": "eu_L5_mn_wins_atoms", "name": "矢量建筑原子", "level": "L5", "node_kind": "atom.bundle", "parent_id": "eu_L4_mn_wins_feat", "adaptation_mode": "ATOMIC_MOUNT", "atom_refs": ["mn_surf_accent", "mn_typo_headline", "mn_lay_unit", "ev_mn_poster"]},

        {"eu_id": "eu_L2_mn_palette_region", "name": "色卡矩阵区 (Col 7–12)", "level": "L2", "node_kind": "region.palette", "parent_id": "eu_L1_mn_spec_grid", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [x7_12, 244.0, w7_12, 76.0]},
        {"eu_id": "eu_L3_mn_palette_fold", "name": "MONOLOG 四色卡阵列宿主", "level": "L3", "entity": True, "node_kind": "component.swatch.array", "parent_id": "eu_L2_mn_palette_region", "adaptation_mode": "FOLD_ARRAY", "array_count": 4, "envelope_bbox": [x7_12, 244.0, w7_12, 76.0], "rendered": True},
        {"eu_id": "eu_L4_mn_swatch_feat", "name": "报纸灰与高对比黑阶样本", "level": "L4", "node_kind": "feature.swatch_array", "parent_id": "eu_L3_mn_palette_fold", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [x7_12, 244.0, w7_12, 76.0]},
        {"eu_id": "eu_L5_mn_swatch_atoms", "name": "色卡原子", "level": "L5", "node_kind": "atom.bundle", "parent_id": "eu_L4_mn_swatch_feat", "adaptation_mode": "ATOMIC_MOUNT", "atom_refs": ["mn_surf_paper", "mn_surf_ink", "mn_surf_muted", "mn_surf_accent", "mn_typo_caption", "mn_lay_gutter", "ev_mn_poster"]},

        {"eu_id": "eu_L2_mn_specimen_region", "name": "字阶标本区 (Col 1–8)", "level": "L2", "node_kind": "region.type_specimen", "parent_id": "eu_L1_mn_spec_grid", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [x1_8, 326.0, w1_8, 50.0]},
        {"eu_id": "eu_L3_mn_specimen", "name": "紧字距黑体印刷字阶样张", "level": "L3", "entity": True, "node_kind": "component.type_specimen", "parent_id": "eu_L2_mn_specimen_region", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [x1_8, 326.0, w1_8, 50.0], "carries_text": True, "rendered_as": "dom_text", "rendered": True},
        {"eu_id": "eu_L4_mn_specimen_feat", "name": "四级字阶尺阶示范特征", "level": "L4", "node_kind": "feature.specimen", "parent_id": "eu_L3_mn_specimen", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [x1_8, 326.0, w1_8, 50.0]},
        {"eu_id": "eu_L5_mn_specimen_atoms", "name": "字阶原子", "level": "L5", "node_kind": "atom.bundle", "parent_id": "eu_L4_mn_specimen_feat", "adaptation_mode": "ATOMIC_MOUNT", "atom_refs": ["mn_surf_ink", "mn_typo_display", "mn_typo_headline", "mn_lay_unit", "ev_mn_poster"]},

        {"eu_id": "eu_L2_mn_grid_region", "name": "网格规范区 (Col 9–12)", "level": "L2", "node_kind": "region.grid_spec", "parent_id": "eu_L1_mn_spec_grid", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [x9_12, 326.0, w9_12, 50.0]},
        {"eu_id": "eu_L3_mn_grid_box", "name": "12 栏瑞士网格基准盒", "level": "L3", "entity": True, "node_kind": "component.grid_box", "parent_id": "eu_L2_mn_grid_region", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [x9_12, 326.0, w9_12, 50.0], "rendered": True},
        {"eu_id": "eu_L4_mn_swiss_grid", "name": "12 栏 19.08mm / 槽 4mm 栅格特征", "level": "L4", "node_kind": "feature.swiss_grid", "parent_id": "eu_L3_mn_grid_box", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [x9_12, 326.0, w9_12, 50.0]},
        {"eu_id": "eu_L5_mn_grid_atoms", "name": "网格原子", "level": "L5", "node_kind": "atom.bundle", "parent_id": "eu_L4_mn_swiss_grid", "adaptation_mode": "ATOMIC_MOUNT", "atom_refs": ["mn_surf_paper", "mn_typo_caption", "mn_lay_unit", "mn_lay_gutter", "ev_mn_poster"]},

        {"eu_id": "eu_L1_mn_footer", "name": "版权与印记页脚领地", "level": "L1", "node_kind": "territory.footer_colophon", "parent_id": "eu_L0_mn_poster", "template_slot": "footer_colophon", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [12.0, 382.0, 273.0, 24.0], "rendered": True},
        {"eu_id": "eu_L2_mn_note_region", "name": "左注脚区 (Col 1–6)", "level": "L2", "node_kind": "region.credits", "parent_id": "eu_L1_mn_footer", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [x1_6, 382.0, w1_6, 24.0]},
        {"eu_id": "eu_L3_mn_credits", "name": "工作室出版署名", "level": "L3", "entity": True, "node_kind": "component.credits", "parent_id": "eu_L2_mn_note_region", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [x1_6, 382.0, w1_6, 24.0], "carries_text": True, "rendered_as": "dom_text", "rendered": True},
        {"eu_id": "eu_L4_mn_credits_feat", "name": "页脚署名排版特征", "level": "L4", "node_kind": "feature.credits", "parent_id": "eu_L3_mn_credits", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [x1_6, 382.0, w1_6, 24.0]},
        {"eu_id": "eu_L5_mn_credits_atoms", "name": "署名原子", "level": "L5", "node_kind": "atom.bundle", "parent_id": "eu_L4_mn_credits_feat", "adaptation_mode": "ATOMIC_MOUNT", "atom_refs": ["mn_surf_muted", "mn_typo_caption", "mn_lay_gutter", "ev_mn_poster"]},

        {"eu_id": "eu_L2_mn_imprint_region", "name": "右印前规范区 (Col 7–12)", "level": "L2", "node_kind": "region.imprint", "parent_id": "eu_L1_mn_footer", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [x7_12, 382.0, w7_12, 24.0]},
        {"eu_id": "eu_L3_mn_imprint", "name": "平面领域零栅格化印记", "level": "L3", "entity": True, "node_kind": "component.imprint", "parent_id": "eu_L2_mn_imprint_region", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [x7_12, 382.0, w7_12, 24.0], "carries_text": True, "rendered_as": "dom_text", "rendered": True},
        {"eu_id": "eu_L4_mn_imprint_feat", "name": "印前参数印记特征", "level": "L4", "node_kind": "feature.imprint", "parent_id": "eu_L3_mn_imprint", "adaptation_mode": "TEMPLATE_ANCHOR", "envelope_bbox": [x7_12, 382.0, w7_12, 24.0]},
        {"eu_id": "eu_L5_mn_imprint_atoms", "name": "印记原子", "level": "L5", "node_kind": "atom.bundle", "parent_id": "eu_L4_mn_imprint_feat", "adaptation_mode": "ATOMIC_MOUNT", "atom_refs": ["mn_surf_muted", "mn_typo_caption", "mn_lay_gutter", "ev_mn_poster"]},
    ]

    edges: list[dict[str, Any]] = [
        {"edge_id": "edge_mn_token_1", "edge_type": "SHARES_TOKEN", "source_eu_id": "eu_L3_mn_headline", "target_eu_id": "eu_L3_mn_specimen", "label": "巨型主标题与字阶样张共享 52px 黑体与 #111111 墨黑 Token", "evidence_ref": "ev_mn_poster"},
        {"edge_id": "edge_mn_token_2", "edge_type": "SHARES_TOKEN", "source_eu_id": "eu_L3_mn_palette_fold", "target_eu_id": "eu_L3_mn_intro_copy", "label": "四色卡阵列与左栏定位声明共享报纸暖灰纸基 Token", "evidence_ref": "ev_mn_poster"},
    ]
    return finalize_fn("tpl_graphic_poster_v1", "平面视觉展板原型", "eu_L0_mn_poster", nodes, reg, edges)


def extract_style_skeleton(case_id: str) -> dict[str, Any]:
    if case_id == "monolog_swiss_poster":
        return build_image_skeleton_monolog()
    if case_id in _WEB_STYLE_SPECS:
        return _build_web_style_skeleton(case_id)
    raise ValueError(f"Unknown style case_id: {case_id}")


def build_style_eu_tree(case_id: str, finalize_fn: Callable[..., dict[str, Any]]) -> dict[str, Any]:
    if case_id == "monolog_swiss_poster":
        return build_eu_tree_monolog_poster(finalize_fn)
    if case_id in _WEB_STYLE_SPECS:
        return _build_web_style_eu_tree(case_id, finalize_fn)
    raise ValueError(f"Unknown style case_id: {case_id}")
