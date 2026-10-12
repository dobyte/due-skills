package app

import (
	"example-server/hall/app/logic"

	"github.com/dobyte/due/v2/cluster/node"
)

// Init 应用装配入口。只做装配，不写业务逻辑。
func Init(proxy *node.Proxy) {
	logic.NewCore(proxy).Init()
}
