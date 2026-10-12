package model

// User 用户模型，对应数据表 user。
// 表结构变更须同步 database/*.sql，DAO 由生成器产出，禁止手写。
type User struct {
	ID        int64  `gorm:"column:id;primaryKey"`
	UID       int64  `gorm:"column:uid"`
	Nickname  string `gorm:"column:nickname"`
	Avatar    string `gorm:"column:avatar"`
	CreatedAt int64  `gorm:"column:created_at"`
	UpdatedAt int64  `gorm:"column:updated_at"`
}

// TableName 指定表名
func (User) TableName() string {
	return "user"
}
