package server

import (
	"context"

	"example-server/internal/code"
	"example-server/internal/service/user/pb"

	"github.com/dobyte/due/v2/cluster/mesh"
	"github.com/dobyte/due/v2/errors"
)

var _ pb.UserServer = &Server{}

// Server 用户微服务，无状态，可水平扩展。
type Server struct {
	pb.UnimplementedUserServer
	proxy *mesh.Proxy
}

func NewServer(proxy *mesh.Proxy) *Server {
	return &Server{proxy: proxy}
}

// Init 注册服务提供者。注册名须与 client 的 discovery:// 域名一致。
func (s *Server) Init() {
	s.proxy.AddServiceProvider("user", &pb.User_ServiceDesc, s)
}

// FetchUser 拉取用户信息
func (s *Server) FetchUser(ctx context.Context, args *pb.FetchUserArgs) (*pb.FetchUserReply, error) {
	if args.GetUid() <= 0 {
		return nil, errors.NewError(code.InvalidArgument)
	}

	return &pb.FetchUserReply{Uid: args.GetUid()}, nil
}

// UpdateNickname 修改昵称
func (s *Server) UpdateNickname(ctx context.Context, args *pb.UpdateNicknameArgs) (*pb.UpdateNicknameReply, error) {
	if args.GetUid() <= 0 || args.GetNickname() == "" {
		return nil, errors.NewError(code.InvalidArgument)
	}

	return &pb.UpdateNicknameReply{}, nil
}
