# 运行时镜像：二进制由 build.sh / CI 在宿主机编译后拷入，镜像内不含 Go 工具链，
# 因此不存在 Go 版本固化与漂移问题。基础镜像需自带 CA 证书与时区数据。
FROM go-base:latest

# 构建期传入环境：test / audit / master
ARG ENV

COPY main /home/server/main
COPY ./etc/etc.${ENV}.toml /home/server/etc/etc.toml

WORKDIR /home/server/

# 内部 RPC 端口
EXPOSE 9928

ENTRYPOINT ["/home/server/main"]
