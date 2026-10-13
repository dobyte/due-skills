---
name: due-v2
description: Due v2 高性能分布式游戏服务器框架完整开发指南。涵盖框架设计(架构、协议、路由、并发模型、滚动更新)、核心模块(网络、注册中心、用户定位、RPC传输、加密、分布式锁、缓存、配置中心、事件总线、日志)、集群服务(网关服务器、节点服务器、网格服务器、Web服务器、客户端)、三方集成(GORM、Redis、MongoDB、JWT、Casbin)、工程规范(从零搭建项目的架构、目录、命名、协议、构建与交付、配置)。为Go语言分布式游戏服务器开发者提供完整的框架设计理念、最佳实践和丰富示例。当用户使用 due/due-v2 框架进行 Go 分布式游戏服务器开发、搭建项目骨架、查阅框架模块用法或核对 API 时使用。
license: MIT
---

# Due v2 框架开发参考

本技能包提供 Due v2 框架的完整参考文档和示例代码,帮助开发者深入理解框架的设计理念和核心机制,并快速上手开发。

## 使用流程

1. **分类任务** — 概念/设计类问题 → 直接查 `references/` 对应文档;从零搭建 → 读 `references/工程规范/` 并对照 `examples/example-server/`;具体编码 → 先读下方「关键约定」,再查对应模块文档与 `examples/` 示例。
2. **核对 API(🔴 CHECKPOINT)** — 编码前用「关键约定」+ 对应 reference 核对 API 名 / 签名 / 配置键,**禁止凭记忆写**;涉及协议改动(`.proto`)、路由号段分配或生产配置(`release` / 注册中心 / 定位)时,先与用户确认再落代码。
3. **复用示例** — 优先取 `examples/` 中最接近的可运行示例做增量改造,而非从零编写。
4. **自查反模式** — 交付前对照下方「反模式(不要做)」清单。

### 遇到冲突时(失败分支)

| 症状 | 一线修复 | 仍不确定的兜底 |
|------|---------|---------------|
| 文档里的 API / 配置键在代码中不存在 | 以框架源码为准,回对应 reference 核对 | 查 [pkg.go.dev/github.com/dobyte/due/v2](https://pkg.go.dev/github.com/dobyte/due/v2) 当前版本 API |
| 示例跑不起来(缺依赖) | 看 `examples/<name>/README` 的运行前置(如 Redis / Consul) | 改用 `examples/quick-start/` 最小示例隔离问题 |
| 技能内找不到对应文档 | 用 `references/README.MD` 索引按关键词定位 | 明确告知用户「这是技能盲区」,**不要编造 API** |

## 关键约定(速查)

> 以下约定已对照框架源码(当前版本 `v2.6.3`,对应 `v2-feature-main` 分支)核实,编写代码前请先确认,避免使用不存在的 API。**本技能包不含框架源码**;需复核时用 `go mod download github.com/dobyte/due/v2@v2.6.3` 拉取对应版本(发布前可用 `go get github.com/dobyte/due/v2@v2-feature-main` 拉取,或查 [pkg.go.dev/github.com/dobyte/due/v2](https://pkg.go.dev/github.com/dobyte/due/v2))。**文档与源码冲突时,一律以源码为准。**

- **集群实例类型**:`Gate` / `Node` / `Mesh`(另有预留的 `Master`)。
- **实例状态**:`Shut` / `Work` / `Busy` / `Hang`;`SetState` 只在 `Work`/`Busy` 间切换,`Close` → `Hang`,`Destroy` → `Shut`。
- **生命周期 Hook**:`cluster.Init` / `cluster.Start` / `cluster.Close` / `cluster.Destroy`。
- **集群事件**:`cluster.Connect` / `cluster.Reconnect` / `cluster.Disconnect`。
- **路由选项**:`node.RouteOptions{Internal, Stateful, Authorized, Middlewares}`,预设 `node.InternalRoute` / `node.StatefulRoute` / `node.AuthorizedRoute`;**不存在 `StatelessRoute`**,默认即无状态路由。
- **路由注册**:`proxy.AddRouteHandler(route int32, handler, opts ...RouteOptions)`,等价写法 `proxy.Router().AddRouteHandler(...)`;路由组用 `proxy.RouteGroup(...)` 或 `proxy.Router().Group(...)`;中间件签名为 `func(mw *node.Middleware, ctx node.Context)`,用 `mw.Next(ctx)` 继续;**不存在 `Router.Use` 与 `ctx.Abort()`**。
- **网关分发策略**:`etc.cluster.gate.dispatch` = `random`(默认)/ `rr` / `wrr`;**值是配置字符串**(Go 常量名为 `RoundRobin`/`WeightedRoundRobin`,但配置里写 `rr`/`wrr`)。
- **并发模型**:节点默认单线程分发(dispatch 协程);`ctx.Task` 投递到全局协程池;`ctx.Next` 交调度器二次分发到 Actor。
- **通信协议**:数据包 `size(4)|header(1)|route(n)|seq(m)|message(x)`,其中 `size = 1 + n + m + len(message)`(不含 4 字节 size 自身);header bit7=心跳、bit6=心跳时间;配置键前缀 `etc.packet.*`(对应 `etc.toml` 中的 `[packet]` 段)。
- **会话类型**:`session.Conn` / `session.User`。
- **用户定位**:`locate` 包,默认 Redis 实现;配置前缀 `locate.redis`(默认 `prefix = "due:locate"`)。

## 反模式(不要做)

> 以下均为框架/工程规范明确**禁止**的做法(详见括注文档),编码前对照自查:

- **手改生成物**(`*.pb.go` / `*_grpc.pb.go`),或让 `.proto` 与生成物不一致 —— 改协议必须改 `.proto` 再重新生成([协议规范](references/工程规范/协议规范.md))。
- **路由号裸写数字、跨模块复用号段、复用已废弃的字段序号**([协议规范](references/工程规范/协议规范.md))。
- **使用不存在的 API**,如 `StatelessRoute`、`Router.Use`、`ctx.Abort()`(见上方「关键约定」)。
- **在路由入口 / 中间件里做阻塞 IO、长耗时计算或跨服务同步调用**;有状态处理必须落到 Actor 单协程串行([协议规范](references/工程规范/协议规范.md))。
- **错误码硬编码数字**;业务错误码必须先在 `common.proto` 登记([协议规范](references/工程规范/协议规范.md))。
- **release 模式输出敏感调试信息**([运行模式](references/框架设计/运行模式.md))。
- **命名 / 目录违规**(脱敏、大小写、目录越界等)([命名规范](references/工程规范/命名规范.md) / [目录规范](references/工程规范/目录规范.md))。

## 框架设计(references/框架设计/)

| 文档 | 说明 |
|------|------|
| [架构设计](references/框架设计/架构设计.md) | Due v2 整体架构概览,核心组件与分层设计 |
| [通信协议](references/框架设计/通信协议.md) | 心跳包与数据包的协议格式设计 |
| [路由设计](references/框架设计/路由设计.md) | 无状态路由与有状态路由的分发机制 |
| [配置管理](references/框架设计/配置管理.md) | 启动配置(etc)的读取、格式支持与全部配置项 |
| [绑定网关](references/框架设计/绑定网关.md) | GID/CID/UID 三者绑定关系与消息流转 |
| [绑定节点](references/框架设计/绑定节点.md) | NID/UID 绑定关系与有状态路由定向 |
| [单线程模型](references/框架设计/单线程模型.md) | 顺序执行的单线程消息处理模型 |
| [多协程模型](references/框架设计/多协程模型.md) | 基于协程池的并发消息处理模型 |
| [Actor模型](references/框架设计/Actor模型.md) | 基于消息传递的Actor并发编程模型 |
| [运行模式](references/框架设计/运行模式.md) | debug/test/pre-release/release 四种运行模式 |
| [错误处理](references/框架设计/错误处理.md) | 框架错误与错误码的设计与使用 |
| [滚动更新](references/框架设计/滚动更新.md) | 网关服、节点服、网格服的滚动更新方案 |

## 核心模块(references/核心模块/)

| 文档 | 说明 |
|------|------|
| [网络通信](references/核心模块/网络通信.md) | TCP/KCP/WebSocket 网络层抽象与实现 |
| [服务注册](references/核心模块/服务注册.md) | Consul/Etcd/Nacos 服务发现与注册 |
| [用户定位](references/核心模块/用户定位.md) | Redis 用户网关/节点绑定信息定位 |
| [RPC传输](references/核心模块/RPC传输.md) | gRPC/RPCX RPC 通信传输层 |
| [加密签名](references/核心模块/加密签名.md) | RSA/ECC 加密与签名算法 |
| [分布式锁](references/核心模块/分布式锁.md) | Redis/Memcache 分布式锁实现 |
| [缓存方案](references/核心模块/缓存方案.md) | Redis/Memcache 缓存方案 |
| [配置中心](references/核心模块/配置中心.md) | File/Consul/Etcd/Nacos 配置中心 |
| [事件总线](references/核心模块/事件总线.md) | Process/NATS/Redis/Kafka 事件总线 |
| [日志组件](references/核心模块/日志组件.md) | 多终端日志组件(控制台、文件、云日志) |
| [任务池](references/核心模块/任务池.md) | 全局任务池与任务组(ErrGroup) |
| [性能分析](references/核心模块/性能分析.md) | PProf 性能分析组件 |

## 集群服务(references/集群服务/)

| 文档 | 说明 |
|------|------|
| [网关服务器](references/集群服务/网关服务器.md) | Gate 网关服务器,处理客户端连接与消息转发 |
| [节点服务器](references/集群服务/节点服务器.md) | Node 节点服务器,处理游戏业务逻辑 |
| [网格服务器](references/集群服务/网格服务器.md) | Mesh 网格服务器,提供微服务 RPC 调用 |
| [Web服务器](references/集群服务/Web服务器.md) | Web HTTP 服务器,支持 Swagger 文档 |
| [客户端](references/集群服务/客户端.md) | TCP/WebSocket 客户端实现 |

## 三方集成(references/三方集成/)

| 文档 | 说明 |
|------|------|
| [GORM数据库](references/三方集成/GORM数据库.md) | GORM ORM 框架集成,支持连接池与多实例 |
| [Redis客户端](references/三方集成/Redis客户端.md) | Redis 客户端集成,支持单机/集群/哨兵模式 |
| [MongoDB驱动](references/三方集成/MongoDB驱动.md) | MongoDB 驱动集成,支持 DSN 配置 |
| [JWT认证](references/三方集成/JWT认证.md) | JWT 认证集成,支持 Redis 存储与 Token 管理 |
| [Casbin权限](references/三方集成/Casbin权限.md) | Casbin 权限控制集成,支持 RBAC 模型 |

## 工程规范(references/工程规范/)

从零搭建 Due 项目的工程化规范(初始架构、目录、命名、协议、构建与交付、配置):

| 文档 | 说明 |
|------|------|
| [架构设计](references/工程规范/架构设计.md) | 角色分层、进程形态、`internal/` 内核职责 |
| [目录规范](references/工程规范/目录规范.md) | 完整目录骨架、三条硬约定、新增服务清单 |
| [命名规范](references/工程规范/命名规范.md) | 命名全表、脱敏规则、反例 |
| [协议规范](references/工程规范/协议规范.md) | proto 组织、路由号段、错误码、字段兼容 |
| [构建与交付](references/工程规范/构建与交付.md) | 宿主机编译 + 运行时打包、多环境配置 |
| [配置规范](references/工程规范/配置规范.md) | `etc.toml` 从框架最新版模板动态生成、裁剪规则 |

可运行参考实现与脚手架脚本见 `examples/example-server/`。

## 示例代码(examples/)

提供 18+ 个完整可运行的示例项目,涵盖框架所有核心功能:

| 示例 | 说明 |
|------|------|
| [快速开始](examples/quick-start/) | 最简节点服务器示例 |
| [节点服务器](examples/node-server/) | 完整节点服务器与路由处理 |
| [Actor模型](examples/actor-model/) | Actor 并发模型示例 |
| [绑定网关](examples/bind-gate/) | 网关绑定流程示例 |
| [绑定节点](examples/bind-node/) | 节点绑定流程示例 |
| [TCP网关](examples/gate-tcp/) | TCP 网关服务器 |
| [WebSocket网关](examples/gate-ws/) | WebSocket 网关服务器 |
| [gRPC网格](examples/mesh-grpc/) | gRPC 网格服务器与客户端 |
| [TCP客户端](examples/client-tcp/) | TCP 客户端连接 |
| [WebSocket客户端](examples/client-ws/) | WebSocket 客户端连接 |
| [Redis缓存](examples/cache-redis/) | Redis 缓存使用 |
| [Redis分布式锁](examples/lock-redis/) | Redis 分布式锁使用 |
| [文件配置](examples/config-file/) | 文件配置中心 |
| [NATS事件总线](examples/eventbus-nats/) | NATS 事件总线 |
| [GORM集成](examples/third-gorm/) | GORM ORM 集成 |
| [Redis集成](examples/third-redis/) | Redis 客户端集成 |
| [JWT集成](examples/third-jwt/) | JWT 认证集成 |
| [项目骨架](examples/example-server/) | 多服务项目骨架(gate/hall/mesh/web + `internal/` 内核),含脚手架脚本 |
