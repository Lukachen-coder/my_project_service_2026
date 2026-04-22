import http.server
import socketserver
import os
import urllib.parse

# 定义服务器端口
PORT = 8000

# 设置工作目录
os.chdir('D:/AI/project/shangmen/front-end')

class MyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # 处理查询参数
        if '?' in self.path:
            # 移除查询参数
            self.path = self.path.split('?')[0]
        # 调用父类的do_GET方法
        super().do_GET()

# 创建服务器
with socketserver.TCPServer(('', PORT), MyHandler) as httpd:
    print(f'Server running at http://localhost:{PORT}')
    httpd.serve_forever()