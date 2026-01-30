#!/usr/bin/env python3
"""
DevOps Multi-Agent Ecosystem - API Gateway
Simple Flask-based API gateway with health checks and logging.
"""

import os
import logging
import json
from datetime import datetime
from functools import wraps
from http.server import HTTPServer, BaseHTTPRequestHandler

# Configuration
PORT = int(os.getenv("PORT", 8080))
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
APP_NAME = os.getenv("APP_NAME", "api-gateway")

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(APP_NAME)


class APIHandler(BaseHTTPRequestHandler):
    """HTTP Request Handler for the API Gateway."""
    
    def _set_headers(self, status_code=200, content_type="application/json"):
        """Set response headers."""
        self.send_response(status_code)
        self.send_header("Content-Type", content_type)
        self.send_header("X-App-Name", APP_NAME)
        self.send_header("X-Request-Time", datetime.utcnow().isoformat())
        self.end_headers()
    
    def _send_json(self, data, status_code=200):
        """Send JSON response."""
        self._set_headers(status_code)
        self.wfile.write(json.dumps(data).encode())
    
    def log_message(self, format, *args):
        """Override to use custom logging."""
        logger.info(f"{self.address_string()} - {format % args}")
    
    def do_GET(self):
        """Handle GET requests."""
        path = self.path.split("?")[0]  # Remove query params
        
        routes = {
            "/": self._handle_root,
            "/health": self._handle_health,
            "/ready": self._handle_ready,
            "/api/status": self._handle_status,
            "/api/info": self._handle_info,
        }
        
        handler = routes.get(path)
        if handler:
            handler()
        else:
            self._handle_not_found()
    
    def _handle_root(self):
        """Root endpoint."""
        self._send_json({
            "service": APP_NAME,
            "version": "1.0.0",
            "status": "operational",
            "endpoints": ["/health", "/ready", "/api/status", "/api/info"]
        })
    
    def _handle_health(self):
        """Health check endpoint for liveness probes."""
        self._send_json({
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat()
        })
    
    def _handle_ready(self):
        """Readiness check endpoint."""
        # Add dependency checks here (database, external services, etc.)
        self._send_json({
            "status": "ready",
            "checks": {
                "service": "ok"
            },
            "timestamp": datetime.utcnow().isoformat()
        })
    
    def _handle_status(self):
        """API status endpoint."""
        self._send_json({
            "service": APP_NAME,
            "status": "running",
            "uptime": "operational",
            "environment": os.getenv("ENVIRONMENT", "development"),
            "timestamp": datetime.utcnow().isoformat()
        })
    
    def _handle_info(self):
        """System information endpoint."""
        self._send_json({
            "service": APP_NAME,
            "version": "1.0.0",
            "python_version": "3.11",
            "port": PORT,
            "log_level": LOG_LEVEL,
            "features": {
                "health_check": True,
                "readiness_check": True,
                "metrics": os.getenv("ENABLE_METRICS", "false").lower() == "true"
            }
        })
    
    def _handle_not_found(self):
        """Handle 404 not found."""
        self._send_json({
            "error": "Not Found",
            "message": f"Path {self.path} not found",
            "available_endpoints": ["/", "/health", "/ready", "/api/status", "/api/info"]
        }, 404)


def run_server():
    """Run the HTTP server."""
    server_address = ("", PORT)
    httpd = HTTPServer(server_address, APIHandler)
    
    logger.info(f"Starting {APP_NAME} on port {PORT}")
    logger.info(f"Log level: {LOG_LEVEL}")
    logger.info("Endpoints: /, /health, /ready, /api/status, /api/info")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("Shutting down server...")
        httpd.shutdown()


if __name__ == "__main__":
    run_server()
