import http.server
import http.client
import time
import os
import json
from proxy_logger import ProxyLogger
from proxy_router import ProxyRouter, RouteTarget

# Define the target server to proxy requests to
TARGET_SERVER = os.environ.get('TARGET_SERVER', 'httpbin.org')
TARGET_PORT = int(os.environ.get('TARGET_PORT', 80))
REGISTRATION_TOKEN = "asdf"
USE_CACHE = os.environ.get('USE_CACHE', 'false').lower() == 'true'

# Initialize the logger
logger = ProxyLogger(log_dir="audit_logs")
router = ProxyRouter()

class ProxyHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.handle_request('GET')
    
    def do_POST(self):
        if self.path == "/_register_route":
            self.handle_route_registration()
        else:
            self.handle_request('POST')
    
    def do_PUT(self):
        self.handle_request('PUT')
    
    def do_DELETE(self):
        if self.path == "/_unregister_route":
            self.handle_route_unregistration()
        else:
            self.handle_request('DELETE')
    
    def do_HEAD(self):
        self.handle_request('HEAD')
    
    def handle_request(self, method):
        start_time = time.time()
        client_address = self.client_address[0]
        path = self.path
        request_size = int(self.headers.get('Content-Length', 0))
    
        logger.log_request(method, self.path, client_address, self.headers)
        
        try:
            # Read request body if present
            content_length = int(self.headers.get('Content-Length', 0))
            request_body = self.rfile.read(content_length) if content_length > 0 else None
            
            # Define which is the target server. 
            target, subpath = router.checkRoutes(path)
            
            if target is None:
                self.send_error(404, "Route not found")
                return
            
            # Open a connection to the target server
            conn = http.client.HTTPConnection(target.server, target.port)
            
            # Forward headers
            headers = dict(self.headers)
            
            # Add X-Forwarded headers
            headers['X-Forwarded-For'] = client_address
            headers['X-Forwarded-Host'] = self.headers.get('Host', '')
            headers['X-Forwarded-Proto'] = 'http'
            
            print(f"Forward to: {target.scheme}://{target.server}:{target.port}{subpath}")
            
            # Handle HTTPS connections
            if target.scheme == "https":
                conn = http.client.HTTPSConnection(target.server, target.port)
            else:
                conn = http.client.HTTPConnection(target.server, target.port)
            
            # Send the original request to the target server
            conn.request(method, subpath, body=request_body, headers=headers)
            
            # Get the response from the target server
            response = conn.getresponse()
            response_data = response.read()
            response_size = len(response_data)
            
            # Send the target server's response back to the client
            self.send_response(response.status)
            for header, value in response.getheaders():
                self.send_header(header, value)
            self.end_headers()
            self.wfile.write(response_data)
            
            # Calculate request duration
            duration = time.time() - start_time
            
            # Log the audit entry
            logger.create_audit_entry(
                method=method,
                path=self.path,
                client_address=client_address,
                status_code=response.status,
                duration=duration,
                request_size=request_size,
                response_size=response_size,
                headers=self.headers
            )
            
            # Log the response
            logger.log_response(method, self.path, response.status, duration, response_size)
            
        except Exception as e:
            # Handle errors
            self.send_error(500, f"Proxy Error: {str(e)}")
            logger.log_error(method, self.path, str(e))
        finally:
            # Close the connection
            if 'conn' in locals():
                conn.close()
    
    def handle_route_registration(self):
        content_length = int(self.headers.get("Content-Length", 0))
        token = self.headers.get("Authorization", "")
        
        if token != f"Bearer {REGISTRATION_TOKEN}":
            self.send_error(403, "Forbidden: Invalid token")
            return

        if content_length == 0:
            self.send_response(400)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({
                "error": "Request body is empty. Expected JSON like: {\"route\": \"/myservice\", \"target\": \"http://localhost:8000\"}"
            }).encode("utf-8"))
            return

        try:
            body = self.rfile.read(content_length).decode("utf-8")
            data = json.loads(body)
            route = data.get("route")
            target = data.get("target")

            if not route or not target:
                self.send_error(400, "Missing 'route' or 'target'")
                return

            router.registerRoutes(route, target)

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "registered"}).encode("utf-8"))

        except Exception as e:
            self.send_error(500, f"Error: {str(e)}")   
    
    def handle_route_unregistration(self):
        content_length = int(self.headers.get("Content-Length", 0))
        token = self.headers.get("Authorization", "")

        if token != f"Bearer {REGISTRATION_TOKEN}":
            self.send_error(403, "Forbidden: Invalid token")
            return

        if content_length == 0:
            self.send_response(400)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({
                "error": "Request body is empty. Expected JSON like: {\"route\": \"/myservice\"}"
            }).encode("utf-8"))
            return

        try:
            body = self.rfile.read(content_length).decode("utf-8")
            data = json.loads(body)
            route = data.get("route")

            if not route:
                self.send_error(400, "Missing 'route'")
                return

            removed = router.unregisterRoute(route)

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({
                "status": "deleted" if removed else "not_found",
                "route": route
            }).encode("utf-8"))

        except Exception as e:
            self.send_error(500, f"Error: {str(e)}")
            
    # Override log_message to prevent default logging
    def log_message(self, format, *args):
        # Skip default logging as we handle it ourselves
        pass

if __name__ == '__main__':
    # Start the reverse proxy server on port 8000
    port = 8000
    server_address = ('', port)
    httpd = http.server.HTTPServer(server_address, ProxyHandler)

    for path, url in router.getAllRoutes().items():
        target = RouteTarget(url)
        logger.log_server_start(path, target.server, target.port)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.log_server_stop("stopped by user")
    except Exception as e:
        logger.log_error("SERVER", "startup/operation", str(e))
