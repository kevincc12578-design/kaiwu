# UI与交互EU错误排查台账（开物 v3.4）

本台账沉淀 Code XR 复刻与开物 v3.3 期间真实出现过的 8 条残差（`RES-KW-01 ~ RES-KW-08`）。每条都绑定到 v3.4 三层正交规则中的**唯一主规则**，并给出可在沙盒中复现的反事实预设，保证同类错误今后在对应层被 `BLOCKED`，而不是靠人工记得。

- 机器读取约定：下方「总表」每行以 `| RES-KW-` 开头，列顺序固定为 `res_id | title | layer | rule_id | counterfactual_preset | symptom | root_cause | fix | status`；后端 `GET /api/error_ledger` 按此表解析为 `entries[]`，字段名与列名一致。
- `status` 取值：`closed_by_rule`（新规则已能自动拦截，且对应反事实预设实测阻断）。

## 总表

| res_id | title | layer | rule_id | counterfactual_preset | symptom | root_cause | fix | status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| RES-KW-01 | 局部录屏冒充整片验收 | parsing | PV-01 | violate_PV01_partial_video_coverage | 只补查了 1.60–2.23 s 邻近放大一段，整段 5.689 s 未逐段建证据，父任务长期停在 validating | 没有「全时段切分闭合」硬约束，局部时段的通过结论被当成全片结论 | 0 → 片长连续切分、首尾相接、覆盖率 100%，每段至少一帧并绑定 EU | closed_by_rule |
| RES-KW-02 | 片尾滚动数字当定值 | parsing | PV-03 | violate_PV03_transient_value_as_truth | 5.62 s Analytics 四指标在片尾仍在滚动，险些被写成最终数值 | 观测值没有 steady / transient 区分，未定值可直接成为 verified 原子 | 观测值强制标注 settle_state；transient 不得 verified，必须挂 AssumptionRecord | closed_by_rule |
| RES-KW-03 | 视频版式代码窗混入界面 | parsing | PV-02 | violate_PV02_layout_noise_leak | 1920×2560 竖版视频下半部是代码窗排版，不属于网页，早期取样容易把它算进画面 | 缺少噪声区登记与可复核裁切变换 | 登记 noise_regions，记录 source_size / crop_rect / scale / target_size，EU 包络不得落入噪声区 | closed_by_rule |
| RES-KW-04 | 交互塞入纵向组件树 | general | GN-01 | violate_GN01_interaction_in_tree | 邻近放大被建成「主单元 + 指针距离 + 搜索球 + 选中项 + 邻项 + 复位边界」六单元五条包含关系，交互与结构混在同一棵树 | 树与图不分，状态联动以父子包含表达 | 交互一律走 6 类白名单横向边，纵向树禁止 interaction./event./state. 前缀；同构项折叠防止度溢出（GN-02） | closed_by_rule |
| RES-KW-05 | 位图贴皮实心退化 | generation | GU-02 | violate_GU02_bitmap_solid_degradation | 用录屏截图或整屏位图铺底冒充界面，文字不可选、控件不可点，窄屏直接裁切 | 生成侧没有「真 DOM 文本 + 弹性容器」硬约束，静图通过即算交付 | 文字节点 100% DOM 文本、控件 100% 真控件，UI 位图面积为 0，1440 / 390 视口零横向裁切 | closed_by_rule |
| RES-KW-06 | 收起侧栏漏掉邻近放大 | generation | GU-03 | violate_GU03_missing_proximity_magnify | r21 设计读回中收起侧栏只记了「展开」，没有指针距离、放大与邻项传递 | 交互要求靠人工点名，未从语义图横向边逐条推导实现 | 每条交互类横向边必须有回检实现：MODULATES_NEIGHBOR 要求主项 > 邻项 > 1.0、远项不动、离开复位 | closed_by_rule |
| RES-KW-07 | 界面放解释性、防御性小字 | generation | GU-04 | violate_GU04_defensive_microcopy | 折光工作台上版把验收说明写成界面文案（「不会丢」「仍可用」等保证句与引导副标题） | 文案铁律只写在设计文档里，产物没有回检 | 舞台与导出各自回读可见文本，禁用短语命中数为 0；同时回检 data-eu-id 唯一且不悬空 | closed_by_rule |
| RES-KW-08 | EU 缺席却报整体验收 | general | GN-03 | violate_GN03_missing_l5_atom | 语义读回返回 EU_PROJECT_MISSING，网页运行通过却险些被当作 EU 已识别、已验收 | 无证据项可以是 verified，L5 原子挂载没有覆盖率门槛 | 单源 atomic_registry + atom_refs 双索引，实体 L3 的 L5 覆盖率 100%，无证据推断项强制进 AssumptionRecord；准入走 GN-04 三态机 | closed_by_rule |

## 逐条说明

### RES-KW-01 · 局部录屏冒充整片验收 → `PV-01`
- 来源：Code XR《录屏验收规则与EU更新》——「已补查原片 1.60–2.23 秒……整段 5.689 秒没有按新规则逐项重新核对」。
- v3.4 处置：Code XR 视频被切为 6 个连续时段（0.00–0.75 / 0.75–1.60 / 1.60–2.23 / 2.23–3.80 / 3.80–4.85 / 4.85–5.689 s），PV-01 以 `coverage_ratio == 1.0`、零缝零叠判定；删除任一中段即 `BLOCKED@parsing`。

### RES-KW-02 · 片尾滚动数字当定值 → `PV-03`
- 来源：《设计与验收》——「原 Analytics 数字在片尾仍在滚动，不视为最终值」。
- v3.4 处置：该观测标为 `transient`，以 AssumptionRecord 显式登记，项目初始诚实处于 `PROVISIONAL`。

### RES-KW-03 · 视频版式代码窗混入界面 → `PV-02`
- 来源：《设计与验收》——「下半部的代码窗是视频排版，不是网页组成部分」，网页范围约为画幅 y=380–1420，按 0.75 缩放。
- v3.4 处置：裁切变换写入 `skeleton.viewport_transform`，代码窗登记为 `code_window` 噪声区。

### RES-KW-04 · 交互塞入纵向组件树 → `GN-01`
- 来源：《录屏验收规则与EU更新》中「六单元和五条包含关系」的建模方式。
- v3.4 处置：邻近放大改为 `SPLIT_HIGH_INTERACTION` 拆出的 L3 组件 + `L4 feature.proximity_magnify`，联动以 `MODULATES_NEIGHBOR` 横向边表达。

### RES-KW-05 · 位图贴皮实心退化 → `GU-02`
- 来源：v3.3 前历次「静图与网页运行通过本身不能补绿」的教训，以及以截图冒充界面的退化风险。
- v3.4 处置：`generator_readback` 真实扫描产物 DOM，统计文本节点、控件与位图角色。

### RES-KW-06 · 收起侧栏漏掉邻近放大 → `GU-03`
- 来源：《邻近放大修订》——「r21 的设计读回中，收起侧栏只记了展开，没有记录指针距离、放大或相邻传递」。
- v3.4 处置：GU-03 以 `probe_by_edge_type` 逐边核验，缺实现即 `BLOCKED@generation`。

### RES-KW-07 · 界面放解释性、防御性小字 → `GU-04`
- 来源：折光工作台 `DESIGN.md`「文案硬规则：不放解释性、防御性小字」与 r3 交付记录。
- v3.4 处置：禁用短语表写入 GU-04 阈值，平面领域 GG-04 复用同一表。

### RES-KW-08 · EU 缺席却报整体验收 → `GN-03`
- 来源：《邻近放大修订》——EU 语义读回 `EU_PROJECT_MISSING`，「这些证据不代表 EU 读取过原视频」。
- v3.4 处置：No-Evidence-No-Verified；任何 verified 节点必须挂 evidence 原子，否则进入假设并阻止 `RELEASE_READY`。
