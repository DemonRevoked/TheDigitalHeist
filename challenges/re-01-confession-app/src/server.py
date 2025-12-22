#!/usr/bin/env python3
"""
Server that validates passphrase and returns key and flag.
Only accessible from localhost inside the container.
"""
import socket
import json
import os
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler

# Expected passphrase (from reverse engineering the binary)
EXPECTED_PASSPHRASE = "The network gateway location is now revealed to us"

class PassphraseHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        """Handle POST request with passphrase"""
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data.decode('utf-8'))
            passphrase = data.get('passphrase', '')
        except:
            passphrase = ''
        
        # Validate passphrase
        if passphrase == EXPECTED_PASSPHRASE:
            # Read key and flag
            key = os.environ.get('CHALLENGE_KEY', 'offline-session-key')
            
            # Read flag from secure root-only location
            flag = None
            flag_paths = [
                '/root/.flag_storage',  # Secure location only root can read
                '/app/basics.txt',  # Fallback
                '/challenge-files/re-01-confession-app/basics.txt'  # Fallback
            ]
            for path in flag_paths:
                if os.path.exists(path):
                    try:
                        with open(path, 'r') as f:
                            flag = f.read().strip()
                        break
                    except PermissionError:
                        # Skip if no permission (expected for /root/.flag_storage if not root)
                        continue
                    except:
                        continue
            
            if not flag:
                flag = 'TDHCTF{confession_gateway_phrase}'
            
            # Return success response
            response = {
                'status': 'success',
                'key': key,
                'flag': flag
            }
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode('utf-8'))
        else:
            # Invalid passphrase
            response = {
                'status': 'error',
                'message': 'Invalid passphrase'
            }
            
            self.send_response(403)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode('utf-8'))
    
    def do_GET(self):
        """Reject GET requests"""
        self.send_response(405)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({'error': 'Method not allowed'}).encode('utf-8'))
    
    def log_message(self, format, *args):
        """Suppress server logs"""
        pass

def run_server(port=31337):
    """Start the server on localhost only"""
    # Drop privileges if running as root (but keep ability to read /root/.flag_storage)
    # Server must run as root to access secure flag file
    server_address = ('127.0.0.1', port)
    try:
        httpd = HTTPServer(server_address, PassphraseHandler)
        print(f"Server listening on localhost:{port}", file=sys.stderr)
        sys.stderr.flush()
        
        # Hide process from non-root users (they can't see /proc/PID anyway if not root)
        httpd.serve_forever()
    except OSError as e:
        print(f"Server failed to start: {e}", file=sys.stderr)
        sys.stderr.flush()
        raise  # Re-raise to see the error
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.stderr.flush()
        raise
    except KeyboardInterrupt:
        if 'httpd' in locals():
            httpd.shutdown()

if __name__ == '__main__':
    try:
        port = int(os.environ.get('SERVER_PORT', 31337))
        run_server(port)
    except Exception as e:
        print(f"Fatal error starting server: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.stderr.flush()
        sys.exit(1)
