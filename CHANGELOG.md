# 变更记录

## 3.4.0 · 2026-11-23

净室重建为 **开物 v3.4 · Kaiwu Adaptive-EU Design Workbench**。

### 新增
- Y 型双向路由三层正交规则体系：`rules/` 下 6 个 YAML、24 条 BLOCKER 规则（PV / PI / PW / GN / GU / GG），单项目动态激活 12 条；规则文件零单项目数字。
- 原型模板库：`tpl_uiux_workspace_v1`（开场外壳 / 导航坞 / 主舞台 / 辅助浮层）与 `tpl_graphic_poster_v1`（品牌页眉 / 主视觉 / 规格网格 / 版权页脚），含 L0~L5 槽位契约、分裂 / 折叠阈值与必检横向边。
- 自适应语义树：`TEMPLATE_ANCHOR`、`SPLIT_HIGH_INTERACTION`、`FOLD_ARRAY`、`ATOMIC_MOUNT`、`PRUNE_OPTIONAL_SLOT`。
- 6 类白名单横向边 Edge-as-EU：`TRIGGERS_STATE`、`RESTORES_FOCUS`、`FILTERS_VIEW`、`MODULATES_NEIGHBOR`、`SCROLLS_INDEPENDENTLY`、`SHARES_TOKEN`。
- 单源双索引 `atomic_registry`（surface / typography / layout / motion / evidence）与 No-Evidence-No-Verified。
- 24 个反事实预设与首障归因约定（目标规则优先，`co_failed_rule_ids` 列出连带失败）。
- 同源跨领域对照案例 `code_xr_poster`（图片 → 平面设计）。
- `UI与交互EU错误排查台账.md`：RES-KW-01 ~ RES-KW-08，各绑定唯一主规则与反事实预设。
- `docs/ARCHITECTURE_v3.4.md`：权威架构与前后端 JSON / postMessage 契约。

### 修复
- Code XR 整段 5.689 s 录屏结案：六段连续切分，覆盖率 100%，替代 v3.3 只补查 1.60–2.23 s 的局部验收（RES-KW-01 → PV-01）。
- 片尾 Analytics 滚动数字改为显式 AssumptionRecord，初始诚实处于 `PROVISIONAL`（RES-KW-02 → PV-03）。
- 收起侧栏邻近放大由横向边 `MODULATES_NEIGHBOR` 驱动生成与回检（RES-KW-06 → GU-03）。

### 变更
- 交互不再以包含关系进入纵向树（RES-KW-04 → GN-01）。
- 界面文案禁用解释性、防御性小字，并由回检自动核验（RES-KW-07 → GU-04）。
