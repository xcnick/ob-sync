# ObSync

## 运行说明

```bash
# 将当前路径加入 PYTHONPATH 中
export PYTHONPATH=${PYTHONPATH}:${PWD}

# 启动服务
DB_PATH=${PWD}/db_files python start_server.py
# 或者
DB_PATH=${PWD}/db_files uvicorn start_server:app --host 0.0.0.0 --port 3000

# signup
DB_PATH=${PWD}/db_files python sign_up.py -n xcnick -e xcnick@163.com -p 1
```

## 依赖项

- fastapi
- uvicorn
- pyjwt
- scrypt
- websockets
