import http.server
import socketserver
import json
import os
import sys
import subprocess
import threading
import time

# Define pathes
BASE_DIR = os.path.dirname(os.path.dirname(__file__)) # d:\anti\daily-report-site
SOURCES_PATH = os.path.join(BASE_DIR, 'sources.json')
WEB_DIR = os.path.join(os.path.dirname(__file__), 'admin')

PORT = 8081

class AdminHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/api/config':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            try:
                with open(SOURCES_PATH, 'r', encoding='utf-8') as f:
                    data = f.read()
                    self.wfile.write(data.encode('utf-8'))
            except FileNotFoundError:
                self.wfile.write(b'{}')
        elif self.path == '/':
            self.path = '/index.html'
            return http.server.SimpleHTTPRequestHandler.do_GET(self)
        else:
            return http.server.SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):
        try:
            if self.path == '/api/config':
                self._handle_save_config()
            elif self.path == '/api/run':
                self._handle_run_collection()
            else:
                self.send_error(404, "Endpoint not found")
        except Exception as e:
            print(f"Exception in do_POST: {e}")
            self.send_error(500, str(e))

    def _handle_save_config(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data)
            with open(SOURCES_PATH, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"status": "success"}')
        except Exception as e:
            self.send_error(500, str(e))

    def _handle_run_collection(self):
        def run_script():
            print("Starting data collection...")
            try:
                result = subprocess.run(
                    [sys.executable, "-m", "src.main"],
                    cwd=BASE_DIR,
                    capture_output=True,
                    text=True
                )
                print("Collection process finished.")
                if result.stdout: print(f"STDOUT: {result.stdout[:200]}...")
                if result.stderr: print(f"STDERR: {result.stderr[:200]}...")
            except Exception as e:
                print(f"Failed to run script: {e}")

        # Start background thread
        thread = threading.Thread(target=run_script)
        thread.start()

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(b'{"status": "started", "message": "Collection started in background"}')

    def translate_path(self, path):
        path = path.split('?',1)[0]
        path = path.split('#',1)[0]
        path = os.path.normpath(path)
        words = path.split('/')
        words = filter(None, words)
        path = WEB_DIR
        for word in words:
            if os.path.dirname(word) or word in (os.curdir, os.pardir):
                continue
            path = os.path.join(path, word)
        return path

    def send_error(self, code, message=None, explain=None):
        try:
            self.send_response(code)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(f'{{"status": "error", "message": "{message}"}}'.encode('utf-8'))
        except:
            pass

if __name__ == "__main__":
    # Force kill port if still valid (optional, but relying on shell commands before this script is better)
    
    if not os.path.exists(WEB_DIR):
        os.makedirs(WEB_DIR)

    # Enable address reuse
    socketserver.TCPServer.allow_reuse_address = True
        
    print(f"Starting Admin Server at http://localhost:{PORT}")
    
    with socketserver.TCPServer(("", PORT), AdminHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass
        httpd.server_close()
