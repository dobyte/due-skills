package basic

// FetchUserReq 拉取用户信息请求
type FetchUserReq struct {
	UID int64 `json:"uid" validate:"required"`
}
