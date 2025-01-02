import http.server
import socketserver
import os

# 设置工作目录为frontend文件夹
os.chdir('frontend')

PORT = 8000
DIRECTORY = '.'

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

with socketserver.TCPServer(("127.0.0.1", PORT), Handler) as httpd:
    print(f"服务器启动在: http://127.0.0.1:{PORT}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n服务器已停止") 