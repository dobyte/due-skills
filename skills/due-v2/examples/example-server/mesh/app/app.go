package app

import (
	usersvc "example-server/internal/service/user/server"

	"github.com/dobyte/due/v2/cluster/mesh"
)

// Init 应用装配入口：注册所有微服务。只做装配，不写业务逻辑。
func Init(proxy *mesh.Proxy) {
	// 用户服务
	usersvc.NewServer(proxy).Init()
}
