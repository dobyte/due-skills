package main

import (
	"example-server/web/app"

	"github.com/dobyte/due/component/http/v2"
	"github.com/dobyte/due/registry/nacos/v2"
	"github.com/dobyte/due/transport/grpc/v2"
	"github.com/dobyte/due/v2"
)

const name = "web"

func main() {
	// 创建容器
	container := due.NewContainer()
	// 创建服务注册发现
	registry := nacos.NewRegistry()
	// 创建RPC传输器
	transporter := grpc.NewTransporter()
	// 创建HTTP组件
	component := http.NewServer(
		http.WithName(name),
		http.WithRegistry(registry),
		http.WithTransporter(transporter),
	)
	// 初始化应用
	app.Init(component.Proxy())
	// 添加HTTP组件
	container.Add(component)
	// 启动容器
	container.Serve()
}
