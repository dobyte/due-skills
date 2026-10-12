package user

// 事件主题。命名格式：<domain>:<action>
const (
	TopicRegister = "user:register" // 用户注册
	TopicLogin    = "user:login"    // 用户登录
)

// RegisterPayload 用户注册事件载荷
type RegisterPayload struct {
	UID      int64  `json:"uid"`
	Nickname string `json:"nickname"`
}
