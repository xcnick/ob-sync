# ObSync

> [!NOTE]
> 这是 [obi-sync](https://github.com/acheong08/obi-sync) 的 Python 实现
> 仅支持 Obsidian 1.4.5 及以下版本

## 运行说明

直接运行服务，需要提前安装相关的依赖项

```bash
# 启动服务
DB_PATH=/your_db_files_dir python start_server.py
# 或者
DB_PATH=/your_db_files_dir uvicorn start_server:app --host 0.0.0.0 --port 3000
```

使用容器运行服务

```bash
# 制作 docker image
docker build -t ob-sync -f dockerfile .

# 启动容器
docker compose up -d
```

用户注册

```bash
DB_PATH=/your_db_files_dir python sign_up.py -n name -e example@email.com -p password
# 或者
docker exec -it -e DB_PATH=/workspace/your_db_files_dir ob-sync python sign_up.py -n name -e example@email.com -p password
```

服务端部署完成后，在 Obsidian 客户端安装配置 https://github.com/acheong08/rev-obsidian-sync-plugin 插件

## 感谢

- [acheong08/obi-sync](https://github.com/acheong08/obi-sync)
