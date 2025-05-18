import logging
import json
import os
import time
from datetime import datetime

class ProxyLogger:
    def __init__(self, log_dir="audit_logs", log_level=logging.INFO):
        """Initialize the proxy logger"""
        # Create logs directory if it doesn't exist
        self.log_dir = log_dir
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        # Configure the Python logger
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(f"{log_dir}/audit.log"),
                logging.StreamHandler()  # Also log to console
            ]
        )
        self.logger = logging.getLogger('reverse_proxy')
        
    def log_request(self, method, path, client_address, headers):
        """Log the initial request"""
        self.logger.info(f"REQUEST: {method} {path} from {client_address}")
        self.logger.debug(f"Headers: {dict(headers)}")
        
    def log_response(self, method, path, status_code, duration, response_size):
        """Log the response"""
        self.logger.info(f"RESPONSE: {method} {path} - Status: {status_code} - "
                         f"Time: {duration:.4f}s - Size: {response_size} bytes")
        
    def log_error(self, method, path, error_message, exc_info=True):
        """Log an error"""
        self.logger.error(f"ERROR: {method} {path} - {error_message}", exc_info=exc_info)
    
    def log_server_start(self, port, target_server, target_port):
        """Log server startup"""
        self.logger.info(f"Reverse proxy server running on port {port}, "
                         f"proxying requests to {target_server}:{target_port}")
    
    def log_server_stop(self, reason="unknown"):
        """Log server shutdown"""
        self.logger.info(f"Server stopped: {reason}")
    
    def create_audit_entry(self, method, path, client_address, status_code, 
                           duration, request_size, response_size, headers):
        """Create and store a detailed audit log entry"""
        # Create audit log entry
        audit_log = {
            "timestamp": datetime.now().isoformat(),
            "client_ip": client_address,
            "method": method,
            "path": path,
            "status_code": status_code,
            "duration_ms": round(duration * 1000, 2),
            "request_size_bytes": request_size,
            "response_size_bytes": response_size,
            "user_agent": headers.get('User-Agent', 'Unknown')
        }
        
        # Write detailed audit log for this request
        audit_filename = f"{self.log_dir}/audit_{datetime.now().strftime('%Y%m%d')}.log"
        with open(audit_filename, "a") as f:
            f.write(json.dumps(audit_log) + "\n")
        
        return audit_log
