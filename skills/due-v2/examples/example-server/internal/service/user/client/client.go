package client

import (
	"example-server/internal/service/user/pb"

	"github.com/dobyte/due/v2/transport"
	"google.golang.org/grpc"
)

// target 微服务发现地址，域名与 server 端 AddServiceProvider 的注册名一致。
const target = "discovery://user"

// NewClient 创建用户微服务客户端，供业务层通过 mesh 调用。
func NewClient(fn transport.NewMeshClient) (pb.UserClient, error) {
	client, err := fn(target)
	if err != nil {
		return nil, err
	}

	return pb.NewUserClient(client.Client().(grpc.ClientConnInterface)), nil
}
