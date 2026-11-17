# SkillHub 发布版（due-skills）

本目录存放 **`due-skills`** 技能面向 **skillhub.cn** 的适配包与发布工作流（内容为 Due v2 框架指南，更新现有 `@indiv-dobyte/due-skills` 列表）。

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
├── build.py                   # 生成 due-skills/ 与 zip，并校验全部限制
├── bump_version.py            # 自动递增版本（auto/patch/minor/major/none）
├── remote_version.py          # 读取 skillhub.cn 线上最新版本
├── publish.py                 # 调用官方 skillhub CLI 做 dry-run / 发布
├── due-skills/                # build.py 生成的可发布目录
├── due-skills-1.1.0.zip       # build.py 生成的上传包
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
5. 生成 `due-skills/` 与 `due-skills-<version>.zip`（zip 使用 `/` 分隔、UTF-8 文件名）。

当前包统计（由 build.py 输出）：44 个文件、约 420KB、最大单文件约 23KB。

## 线上版本解析

[remote_version.py](remote_version.py) 调用 SkillHub.cn API：

```text
GET /api/v1/auth/me                     -> 解析发布者 handle
GET /api/v1/skills/{slug}?namespace=…   -> latestVersion.version
```

工作流会先读取线上版本，再通过 `bump_version.py --online <version>` 决定新版本：

- 本地版本高于线上 → 直接发布本地版本；
- 本地版本等于线上 → patch +1；
- 本地版本低于线上 → 从线上版本 patch +1；
- 查不到线上版本（首次发布）→ 当前版本 patch +1。

需要 `SKILLHUB_KEY`；默认 slug `due-skills`、namespace `indiv-dobyte`，可用 `SKILLHUB_SLUG` / `SKILLHUB_NAMESPACE` 覆盖。公开技能可加 `--allow-anonymous --namespace <handle>` 查询；本地证书链异常时可加 `--insecure` 仅用于诊断。

## 本地发布

只做构建与 frontmatter dry-run（不需要 API Key）：

```bash
python release/skillhub/publish.py --dry-run
```

正式发布前先递增版本（本地 `publish.py` 不会自动 bump）：

```bash
python release/skillhub/bump_version.py --mode patch
export SKILLHUB_KEY=skh_xxx
python release/skillhub/publish.py --changelog "v1.1.1: 更新内容"
```

PowerShell：

```powershell
python release/skillhub/bump_version.py --mode patch
$env:SKILLHUB_KEY = "skh_xxx"
python release/skillhub/publish.py --changelog "v1.1.1: 更新内容"
```

publish.py 内部执行：`skillhub login --key ... --host https://api.skillhub.cn`，然后 `skillhub publish ./release/skillhub/due-skills --host https://api.skillhub.cn`；不会打印 Key。

## GitHub Actions（自动版本 + 发布）

工作流文件：[.github/workflows/publish-skillhub.yml](../../.github/workflows/publish-skillhub.yml)

**自动触发**：push 到 `main` 且改动以下路径时执行：

- `skills/due-v2/SKILL.md`
- `skills/due-v2/references/**`
- `release/skillhub/SKILL.template`

**手动触发**：workflow_dispatch，`mode` 可选：

| mode | 行为 |
|------|------|
| `auto`（默认） | HEAD 已改过版本则沿用；否则 patch +1 |
| `none` | 不递增，发布当前版本（用于失败重试） |
| `patch` / `minor` / `major` | 强制递增对应位 |

**自动流程**：

1. `remote_version.py` 读取线上版本，`bump_version.py` 按本地/线上版本决定并写入 `skills/due-v2/SKILL.md` 与 `SKILL.template`；
2. `build.py` 生成并校验发布包；
3. 提交版本号、生成目录与 zip，commit message 带 `[skip ci]`；
4. 调用 `publish.py` 发布到 skillhub.cn；
5. 成功后创建 `skillhub-v<version>` tag（tag 失败不阻塞发布）。

**失败重试**：版本提交发生在发布之前，所以发布失败时 main 上已经是新版本；重新运行 `mode=auto` 会沿用当前版本重试，不会再次递增。

**前置条件**：

- 现有列表为 `@indiv-dobyte/due-skills`（线上 1.0.0）；`slug` 固定 `due-skills`，工作流默认 namespace 为 `indiv-dobyte`。
- 当前本地版本 `1.1.0` 高于线上 `1.0.0`，首次运行会直接发布 `1.1.0`，不会额外跳号；之后每次文档更新再 patch +1。
- 若线上版本高于本地，先把 `SKILL.template` 与 `skills/due-v2/SKILL.md` 改成线上版本，避免撞版本。
- 仓库 Secret `SKILLHUB_KEY`（`skh_` 开头）；
- 允许 GitHub Actions 写入 `main`（branch protection 需放行）；
- 工作流自动安装官方 `skillhub` CLI，并上传 `due-skills-*.zip` artifact。

## Web UI 上传

打开 <https://skillhub.cn/dashboard/publish>，上传 `release/skillhub/due-skills-<version>.zip`。zip 根目录即 `SKILL.md`，无需再套一层目录。

## 更新流程

1. 修改 `skills/due-v2` 的文档后，同步更新 `SKILL.template`：
   - 保留 SkillHub 专用 frontmatter；
   - 同步主 `SKILL.md` 的「关键约定」、模块表与版本基线；
   - `## 示例代码` 段保留 GitHub 链接，不恢复本地 `examples/` 链接。
2. 提交文档改动并 push 到 `main`；自动工作流会：
   - 将 patch 版本 +1（若本次提交已手动改版本则沿用）；
   - 重新构建、提交版本号与 zip；
   - 发布到 skillhub.cn 并打 `skillhub-v<version>` tag。
3. 如果只想本地验证，运行 `python release/skillhub/publish.py --dry-run`。
4. 如果自动发布失败：修复原因后手动运行工作流，`mode=auto`（沿用当前版本重试）或 `mode=none`。

## 发布前检查清单

- [ ] `SKILL.md` 顶层包含 `slug`、`version`、`displayName`（SkillHub.cn 硬性要求）
- [ ] `slug` 为 `due-skills`（kebab-case，2–128 字符；发布后不可改）
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
