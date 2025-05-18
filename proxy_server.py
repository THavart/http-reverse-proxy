import http.server
import http.client
import time
from proxy_logger import ProxyLogger

# Define the target server to proxy requests to
TARGET_SERVER = 'httpbin.org'
TARGET_PORT = 80

# Initialize the logger
logger = ProxyLogger(log_dir="proxy_logs")

class ProxyHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.handle_request('GET')
    
    def do_POST(self):
        self.handle_request('POST')
    
    def do_PUT(self):
        self.handle_request('PUT')
    
    def do_DELETE(self):
        self.handle_request('DELETE')
    
    def do_HEAD(self):
        self.handle_request('HEAD')
    
    def handle_request(self, method):
        # Start timing the request
        start_time = time.time()
        
        # Extract client information for logging
        client_address = self.client_address[0]
        request_size = int(self.headers.get('Content-Length', 0))
        
        # Log the incoming request
        logger.log_request(method, self.path, client_address, self.headers)
        
        try:
            # Read request body if present
            content_length = int(self.headers.get('Content-Length', 0))
            request_body = self.rfile.read(content_length) if content_length > 0 else None
            
            # Open a connection to the target server
            conn = http.client.HTTPConnection(TARGET_SERVER, TARGET_PORT)
            
            # Forward headers
            headers = dict(self.headers)
            
            # Add X-Forwarded headers
            headers['X-Forwarded-For'] = client_address
            headers['X-Forwarded-Host'] = self.headers.get('Host', '')
            headers['X-Forwarded-Proto'] = 'http'
            
            # Send the original request to the target server
            conn.request(method, self.path, body=request_body, headers=headers)
            
            # Get the response from the target server
            response = conn.getresponse()
            
            # Read response data
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
    
    # Override log_message to prevent default logging
    def log_message(self, format, *args):
        # Skip default logging as we handle it ourselves
        pass

if __name__ == '__main__':
    # Start the reverse proxy server on port 8000
    port = 8000
    server_address = ('', port)
    httpd = http.server.HTTPServer(server_address, ProxyHandler)
    
    logger.log_server_start(port, TARGET_SERVER, TARGET_PORT)
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.log_server_stop("stopped by user")
    except Exception as e:
        logger.log_error("SERVER", "startup/operation", str(e))
