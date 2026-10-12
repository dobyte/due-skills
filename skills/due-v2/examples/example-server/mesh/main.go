package main

import (
	"example-server/mesh/app"

	rediscache "github.com/dobyte/due/cache/redis/v2"
	nacosconfig "github.com/dobyte/due/config/nacos/v2"
	rediseventbus "github.com/dobyte/due/eventbus/redis/v2"
	"github.com/dobyte/due/locate/redis/v2"
	redislock "github.com/dobyte/due/lock/redis/v2"
	"github.com/dobyte/due/registry/nacos/v2"
	"github.com/dobyte/due/transport/grpc/v2"
	"github.com/dobyte/due/v2"
	"github.com/dobyte/due/v2/cache"
	"github.com/dobyte/due/v2/cluster/mesh"
	"github.com/dobyte/due/v2/config"
	"github.com/dobyte/due/v2/eventbus"
	"github.com/dobyte/due/v2/lock"
)

const name = "mesh"

func main() {
	// 设置分布式锁
	lock.SetMaker(redislock.NewMaker())
	// 设置缓存
	cache.SetCache(rediscache.NewCache())
	// 设置事件总线
	eventbus.SetEventbus(rediseventbus.NewEventbus())
	// 设置配置中心
	config.SetConfigurator(config.NewConfigurator(config.WithSources(nacosconfig.NewSource())))
	// 创建容器
	container := due.NewContainer()
	// 创建用户定位器
	locator := redis.NewLocator()
	// 创建服务注册发现
	registry := nacos.NewRegistry()
	// 创建RPC传输器
	transporter := grpc.NewTransporter()
	// 创建网格组件
	component := mesh.NewMesh(
		mesh.WithName(name),
		mesh.WithLocator(locator),
		mesh.WithRegistry(registry),
		mesh.WithTransporter(transporter),
	)
	// 初始化应用
	app.Init(component.Proxy())
	// 添加网格组件
	container.Add(component)
	// 启动容器
	container.Serve()
}
