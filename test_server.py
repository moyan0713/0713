from flask import Flask, jsonify, render_template_string
import sys
import socket

# 设置控制台输出编码
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

app = Flask(__name__)

# 简单的HTML模板
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>测试服务器</title>
    <meta charset="utf-8">
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 40px;
            background-color: #f0f0f0;
        }
        .container {
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            max-width: 600px;
            margin: 0 auto;
        }
        h1 {
            color: #333;
            text-align: center;
        }
        .status {
            text-align: center;
            padding: 10px;
            background-color: #e8f5e9;
            border-radius: 4px;
            margin: 20px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>测试服务器</h1>
        <div class="status">
            <p>服务器状态: {{ status }}</p>
            <p>服务器消息: {{ message }}</p>
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    try:
        return render_template_string(HTML_TEMPLATE, 
            status="正常运行",
            message="服务器连接成功！"
        )
    except Exception as e:
        return f"错误: {str(e)}", 500

@app.route('/api/status')
def status():
    return jsonify({
        "message": "服务器运行正常",
        "status": "ok"
    })

def get_ip():
    try:
        # 获取本机IP地址
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "localhost"

if __name__ == '__main__':
    ip = get_ip()
    print("\n" + "="*50)
    print("正在启动服务器...")
    print(f"请使用以下地址访问服务器：")
    print(f"本地访问: http://localhost:5000")
    print(f"局域网访问: http://{ip}:5000")
    print("="*50 + "\n")
    
    try:
        app.run(debug=True, host='0.0.0.0', port=5000)
    except Exception as e:
        print(f"\n启动服务器时出错: {str(e)}")
        print("\n可能的原因：")
        print("1. 端口 5000 已被占用")
        print("2. 防火墙阻止了连接")
        print("3. Flask 未正确安装")
        print("\n请尝试以下解决方案：")
        print("1. 关闭占用端口 5000 的其他程序")
        print("2. 检查防火墙设置")
        print("3. 重新安装 Flask: pip install flask==2.3.3")
        input("\n按回车键退出...") 