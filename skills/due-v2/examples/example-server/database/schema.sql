-- 示例项目建表脚本。DDL 变更须同步 model 与 changelog。

CREATE TABLE IF NOT EXISTS `user` (
    `id`         BIGINT       NOT NULL AUTO_INCREMENT COMMENT '自增主键',
    `uid`        BIGINT       NOT NULL DEFAULT 0 COMMENT '用户ID',
    `nickname`   VARCHAR(64)  NOT NULL DEFAULT '' COMMENT '昵称',
    `avatar`     VARCHAR(255) NOT NULL DEFAULT '' COMMENT '头像',
    `created_at` BIGINT       NOT NULL DEFAULT 0 COMMENT '创建时间（秒）',
    `updated_at` BIGINT       NOT NULL DEFAULT 0 COMMENT '更新时间（秒）',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_uid` (`uid`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COMMENT = '用户表';
