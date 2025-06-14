#!/usr/bin/env python3

import http.server
import socketserver
import os
from urllib.parse import urlparse

class TemplateHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # Parse the URL
        parsed_path = urlparse(self.path)
        
        # If requesting HTML files, serve with template processing
        if (parsed_path.path == '/' or 
            parsed_path.path.endswith('.html') or
            parsed_path.path == '/index.html'):
            self.serve_template()
        else:
            # For all other files, serve normally
            super().do_GET()
    
    def serve_template(self):
        try:
            # Determine which file to serve
            parsed_path = urlparse(self.path)
            if parsed_path.path == '/':
                file_path = 'index.html'
            else:
                file_path = parsed_path.path.lstrip('/')
            
            # Read the HTML template
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Get environment variables
            supabase_url = os.environ.get('SUPABASE_URL', '')
            supabase_key = os.environ.get('SUPABASE_ANON_KEY', '')
            
            # Debug output
            print(f"Serving {file_path}")
            print(f"SUPABASE_URL exists: {bool(supabase_url)}")
            print(f"SUPABASE_ANON_KEY exists: {bool(supabase_key)}")
            
            # Replace placeholders with actual values
            content = content.replace('{{ SUPABASE_URL }}', supabase_url)
            content = content.replace('{{ SUPABASE_ANON_KEY }}', supabase_key)
            
            # Send response
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Expires', '0')
            self.send_header('Content-Length', str(len(content.encode('utf-8'))))
            self.end_headers()
            self.wfile.write(content.encode('utf-8'))
            
        except FileNotFoundError:
            self.send_error(404, f"File not found: {self.path}")
        except Exception as e:
            self.send_error(500, f"Internal server error: {str(e)}")

def run_server(port=5000):
    handler = TemplateHTTPRequestHandler
    
    # Allow socket reuse
    socketserver.TCPServer.allow_reuse_address = True
    
    try:
        with socketserver.TCPServer(("0.0.0.0", port), handler) as httpd:
            print(f"Server running at http://0.0.0.0:{port}/")
            httpd.serve_forever()
    except OSError as e:
        if e.errno == 98:  # Address already in use
            print(f"Port {port} is in use, trying port {port + 1}")
            run_server(port + 1)
        else:
            raise

if __name__ == "__main__":
    run_server()