# due-skills

[English](README.EN.md)

[![skills.sh](https://skills.sh/b/dobyte/due-skills)](https://skills.sh/dobyte/due-skills)

Due 框架的 AI Agent 技能集。本仓库将 Due v2 框架参考文档、示例代码和开发指南整理为可复用的 skills，方便 AI 编程助手在开发 Due 项目时快速获得框架上下文。

## 安装

使用 `skills` CLI 安装：

```bash
npx skills add dobyte/due-skills
```

安装后，如果你的 AI Agent 没有自动发现新技能，请重启或重新加载 Agent。

## 包含的技能

### due-skills

仓库级入口技能，用于概览 Due 框架技能集。

### due-v2

Due v2 框架完整开发参考，内容包括：

- 框架设计：架构、通信协议、路由、配置、运行模式、错误处理、并发模型、Actor 模型和滚动更新。
- 核心模块：网络通信、服务注册、用户定位、RPC 传输、加密签名、分布式锁、缓存、配置中心、事件总线和日志组件。
- 集群服务：网关服务器、节点服务器、网格服务器、Web 服务器和客户端。
- 三方集成：GORM、Redis、MongoDB、JWT 和 Casbin。
- 示例代码：`skills/due-v2/examples/` 下提供多个可运行示例。

## 使用示例

安装后，可以让 AI Agent 使用 `due-v2` 技能处理 Due 框架相关任务，例如：

```text
Use the due-v2 skill to create a minimal Due node server.
```

```text
Use the due-v2 skill to explain how gate binding and node binding work.
```

```text
Use the due-v2 skill to choose the right runtime mode and configuration pattern for a production deployment.
```
