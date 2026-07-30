"""
应用启动入口
运行Flask开发服务器
"""
from dotenv import load_dotenv

# 加载 .env 中的环境变量（需在 create_app 之前）
load_dotenv()

from app import create_app

# 创建应用实例
app = create_app()

if __name__ == '__main__':
    # 启动开发服务器
    # debug=True 开启调试模式，代码修改后自动重启
    # host='0.0.0.0' 允许外部访问
    # port=5000 指定端口
    app.run(debug=True, host='0.0.0.0', port=5000)
