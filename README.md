# 开物 v3.4 · Kaiwu Adaptive-EU Design Workbench

版本 `3.4.0`。以 **Code XR · Glass Workspace** 为基线，把录屏 / 静图 / 网页解析成同一棵 L0~L5 自适应语义树，经三层正交规则门禁后生成可编辑、可回检的 UI 或平面产物。

## 快速开始

```powershell
python backend/server.py --port 4340
# 浏览器打开 http://127.0.0.1:4340/
```

仅依赖 Python 标准库（若已安装 PyYAML 则优先使用）。前端为零构建原生 HTML/CSS/JS，离线可用。

## 核心

- **Y 型三层正交规则**：6 个 YAML × 4 条 = 24 条 BLOCKER 规则；单项目按 `解析模态(4) + 总规则(4) + 生成领域(4)` 激活 12 条。
  - 解析层：`rules/parsing_video.yaml`（PV）· `rules/parsing_image.yaml`（PI）· `rules/parsing_web.yaml`（PW）
  - 总规则：`rules/general_rules.yaml`（GN，必检）
  - 生成层：`rules/generation_uiux.yaml`（GU）· `rules/generation_graphic.yaml`（GG）
- **原型模板锚定 + 自适应伸缩**：`templates/uiux_workspace_template.yaml`（`tpl_uiux_workspace_v1`）、`templates/graphic_poster_template.yaml`（`tpl_graphic_poster_v1`）；`TEMPLATE_ANCHOR` / `SPLIT_HIGH_INTERACTION` / `FOLD_ARRAY` / `ATOMIC_MOUNT`。
- **树图分离**：纵向六级单父树（度 ≤ 7）+ 6 类白名单横向边。
- **单源双索引原子**：`atomic_registry` 五区段 + `atom_refs`，No-Evidence-No-Verified。
- **三态准入**：`BLOCKED` / `PROVISIONAL` / `RELEASE_READY`。
- **反事实沙盒**：24 个预设，在内存快照中真实注入并由同一引擎拦截。

## 案例

| 案例 | 路由 | 模板 |
| --- | --- | --- |
| `code_xr_uiux` | 视频 → 总规则 → UI/UX（5.689 s 六段全覆盖） | `tpl_uiux_workspace_v1` |
| `code_xr_poster` | 图片 → 总规则 → 平面设计（A3 品牌视觉展板） | `tpl_graphic_poster_v1` |

## 目录

```text
VERSION  README.md  CHANGELOG.md  UI与交互EU错误排查台账.md
docs/ARCHITECTURE_v3.4.md   架构与 JSON API 契约（权威）
rules/       6 个规则 YAML
templates/   2 个原型模板
backend/     解析、自适应 EU 引擎、回检、AI 工具、HTTP 服务
cases/       code_xr_uiux / code_xr_poster
frontend/    折光三窗格检验台
tests/       verify_v34_kaiwu.py
```

## 文档

- [架构与 API 契约](docs/ARCHITECTURE_v3.4.md)
- [UI与交互EU错误排查台账](UI与交互EU错误排查台账.md)
- [变更记录](CHANGELOG.md)

## 验收

```powershell
python tests/verify_v34_kaiwu.py
```

报告输出到 `tests/v34_verification_report.json`。
