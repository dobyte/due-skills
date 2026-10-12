---
title: "项目骨架示例"
slug: "example-server"
keywords: ["due", "项目骨架", "目录结构", "多服务", "脚手架"]
description: "按 due-v2 工程规范搭建的多服务项目骨架"
hide_title: true
---

# 项目骨架示例

本示例演示按 `due-v2` 的**工程规范**（`references/工程规范/`）搭建的多服务项目骨架：`gate` / `hall` / `mesh` / `web` 四个服务 + 顶层 `internal/` 共享内核。

## 项目结构

```
example-server/
├── go.mod / go.sum               # 未提交，由 scripts/init-deps.sh 生成
├── build.sh                      # 单服务构建与发布（宿主机编译 + 运行时打包）
├── protoc.sh                     # 统一协议生成
├── scripts/
│   ├── init-deps.sh              # 依赖版本解析（拉取最新，不固化）
│   └── gen-etc.sh                # 按角色生成各服务 etc.toml
├── internal/                     # 跨服务共享内核
│   ├── code/ define/ event/ middleware/ model/
│   ├── protocol/                 # .proto 源 + 生成物
│   ├── service/user/{pb,server,client}
│   └── share/etc/                # 共享配置（构建期分发）
├── gate/                         # 接入层（纯连接层，无 app/）
├── hall/                         # 业务层（Node）
├── mesh/                         # 服务层（Mesh）
├── web/                          # HTTP 服务
└── database/                     # DDL
```

## 如何从零生成

```bash
bash scripts/init-deps.sh    # 1) 解析最新依赖（无 go.mod 时按目录名初始化模块）
bash scripts/gen-etc.sh      # 2) 按角色生成各服务 etc.toml
bash protoc.sh               # 3) 生成协议代码
go mod tidy                  # 4) 依赖定稿
go build ./...               #    编译校验
```

## 说明

- 本目录**未提交 `go.mod` / `go.sum`**：依赖版本由 `scripts/init-deps.sh` 在脚手架时按当刻最新解析，不固化版本。
- `*.pb.go` 与 `etc/etc.toml` 为生成物快照，仅供结构参考；实际以脚本重新生成为准（`*.pb.go` 禁止手改）。
- **目录名即模块名**：`init-deps.sh` 默认用目录名初始化模块，而代码内的 import 为 `example-server/...`。换目录时请显式传入模块名（`bash scripts/init-deps.sh <module>`）并同步调整 import 与 `.proto` 的 `go_package`。
- 规范细节见 `../../references/工程规范/`（架构设计 / 目录规范 / 命名规范 / 协议规范 / 构建与交付 / 配置规范）。
