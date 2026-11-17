# SkillHub 发布版（due-v2）

本目录存放 `due-v2` 技能面向 **skillhub.cn** 的适配包与发布工作流。

## 为什么需要单独适配

主技能 `skills/due-v2` 不能直接上传 SkillHub：

| 限制 | SkillHub 规则 | 主技能现状 |
|------|---------------|-----------|
| 根入口 | 根目录必须有 `SKILL.md` | 满足 |
| 文件类型 | `.md` `.txt` `.json` `.yaml` `.yml` `.js` `.cjs` `.mjs` `.ts` `.py` `.sh` `.png` `.jpg` `.svg` | `examples/` 含 `.go`、`.proto`、`.toml`、`.sql`、`.mod` 等 |
| 文件数量 | ≤ 100 个 | 167 个 |
| 单文件大小 | ≤ 1MB | 满足 |
| 总包大小 | ≤ 10MB | 满足 |

因此 SkillHub 版只保留 Markdown 参考文档，`examples/` 改为指向 GitHub 仓库。

## 目录结构

```
release/skillhub/
├── SKILL.template             # SkillHub 专用 SKILL.md 源（手工维护，无 .md 后缀避免被链接检查）
├── build.py                   # 生成 due-v2/ 与 zip，并校验全部限制
├── publish.py                 # 调用官方 skillhub CLI 做 dry-run / 发布
├── due-v2/                    # build.py 生成的可发布目录
├── due-v2-1.1.0.zip           # build.py 生成的上传包
└── README.md
```

## 构建

```bash
python release/skillhub/build.py
```

build.py 会：

1. 校验 `SKILL.template` 的 `slug` / `version` / `displayName` 与 SkillHub 规则；
2. 校验模板 `version` 与 `skills/due-v2/SKILL.md` 一致（不一致直接失败）；
3. 复制 `skills/due-v2/references/*.md`，把 `README.MD` 重命名为 `README.md`；
4. 校验文件类型、文件数量、单文件/总大小、隐藏文件与包内相对链接；
5. 生成 `due-v2/` 与 `due-v2-<version>.zip`（zip 使用 `/` 分隔、UTF-8 文件名）。

当前包统计（由 build.py 输出）：44 个文件、约 420KB、最大单文件约 23KB。

## 本地发布

只做构建与 frontmatter dry-run（不需要 API Key）：

```bash
python release/skillhub/publish.py --dry-run
```

正式发布（`SKILLHUB_KEY` 为 `skh_` 开头的 API Key）：

```bash
export SKILLHUB_KEY=skh_xxx
python release/skillhub/publish.py --changelog "v1.1.0: SkillHub 首发"
```

PowerShell：

```powershell
$env:SKILLHUB_KEY = "skh_xxx"
python release/skillhub/publish.py --changelog "v1.1.0: SkillHub 首发"
```

publish.py 内部执行：`skillhub login --key ... --host https://api.skillhub.cn`，然后 `skillhub publish ./release/skillhub/due-v2 --host https://api.skillhub.cn`；不会打印 Key。

## GitHub Actions 工作流

工作流文件：[.github/workflows/publish-skillhub.yml](../../.github/workflows/publish-skillhub.yml)

- 手动触发（workflow_dispatch）；
- 输入 `publish=false`（默认）只构建、上传 artifact 并做 dry-run，不发布；
- 输入 `publish=true` 才会调用 `publish.py` 正式发布；
- 需要在仓库 Secrets 中配置 `SKILLHUB_KEY`（`skh_` 开头）；
- 工作流会自动安装官方 `skillhub` CLI，并上传 `due-v2-*.zip` 作为 artifact。

## Web UI 上传

打开 <https://skillhub.cn/dashboard/publish>，上传 `release/skillhub/due-v2-<version>.zip`。zip 根目录即 `SKILL.md`，无需再套一层目录。

## 更新流程

1. 修改 `skills/due-v2` 的文档后，同步更新 `SKILL.template`：
   - 保留 SkillHub 专用 frontmatter；
   - 同步主 `SKILL.md` 的「关键约定」、模块表与版本基线；
   - `## 示例代码` 段保留 GitHub 链接，不恢复本地 `examples/` 链接。
2. 升级 `SKILL.template` 与 `skills/due-v2/SKILL.md` 的 `version`（两者必须一致；已发布版本不可覆盖）。
3. 运行 `python release/skillhub/build.py` 重新生成目录与 zip。
4. 提交 `SKILL.template`、生成物（如需要）与代码改动。
5. 运行工作流或本地 `publish.py` 发布。

## 发布前检查清单

- [ ] `SKILL.md` 顶层包含 `slug`、`version`、`displayName`（SkillHub.cn 硬性要求）
- [ ] `slug` 为 `due-v2`（kebab-case，2–128 字符；发布后不可改）
- [ ] `version` 已递增且为合法 SemVer，且与主技能一致
- [ ] `summary`、`tags`、`homepage`、`license` 已填写
- [ ] `tags` 使用行内列表 `[a, b, c]`
- [ ] 文件数 ≤ 100、单文件 ≤ 1MB、总包 ≤ 10MB
- [ ] 没有 `.go`、`.proto`、`.toml`、`.sql` 等白名单外文件
- [ ] 所有相对 Markdown 链接在包内可解析

## SkillHub.cn CLI 注意事项

- 当前 `skillhub` CLI 的 frontmatter 解析器只支持平铺的 `key: value` 与 `key: [a, b]` 列表；**不要写嵌套 `metadata:` 块或 `- item` 块列表**，否则字段不会被正确读取。
- `--dry-run` 只校验 frontmatter 的 `slug` / `version` / `displayName`，**不校验文件类型、文件数量与大小**；这些由 `build.py` 在本地校验。
- 服务端发布接口限制约 10MB；CLI 解压上限 50MB。本包约 420KB，余量充足。
- `displayName` 参与搜索召回；`summary` / `description` / `tags` 主要影响展示与检索文本，建议保持简洁。

## 已知差异

- SkillHub 版不含 `examples/` 可运行工程；示例入口改为 GitHub 链接。
- 其余参考文档与主技能保持同步，API/配置以 v2.6.8 为基线。
