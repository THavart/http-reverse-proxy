from urllib.parse import urlparse
import json
import os

FILENAME = "routes.json"

class ProxyRouter:
    def __init__(self):
        self.routes = {}
        self.loadRoutesFromFile(FILENAME)

    def checkRoutes(self, full_path):
        # Find the longest matching route prefix
        matching_routes = sorted(
            [route for route in self.routes if full_path.startswith(route)],
            key=len,
            reverse=True
        )

        if not matching_routes:
            return None, None

        matched_prefix = matching_routes[0]
        target_url = self.routes[matched_prefix]
        target = RouteTarget(target_url)

        remaining_path = full_path[len(matched_prefix):]
        if not remaining_path.startswith("/"):
            remaining_path = f"/{remaining_path}"

        return target, remaining_path

    def getAllRoutes(self):
        return dict(self.routes)

    def registerRoutes(self, path, target_url, save=True):
        if path in self.routes:
            print(f"Warning: Overwriting route for {path}")
        self.routes[path] = target_url
        print(f"Registered route: {path} -> {target_url}")
        if save:
            self.saveRoutes(FILENAME)
        
    def loadRoutesFromFile(self, filename):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        full_path = os.path.join(base_dir, filename)

        if not os.path.exists(full_path):
            print(f"Routes file '{filename}' not found. Starting with empty route table.")
            with open(full_path, 'w') as f:
                json.dump({}, f, indent=2)
            return

        with open(full_path, 'r') as f:
            try:
                data = json.load(f)
                for path, url in data.items():
                    self.registerRoutes(path, url, save=False)
            except json.JSONDecodeError as e:
                print(f"Error parsing routes file '{filename}': {e}")

                
    def unregisterRoute(self, path: str):
        if path in self.routes:
            del self.routes[path]
            self.saveRoutes(FILENAME)
            return True
        return False
    
    def saveRoutes(self, filename):
        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            full_path = os.path.join(base_dir, filename)
            
            with open(full_path, "w") as f:
                json.dump(self.routes, f, indent=2)
            
        except Exception as e:
            print(f"Error saving routes to {filename}: {e}")

class RouteTarget:
    def __init__(self, url):
        parsed = urlparse(url)
        self.base_url = url.rstrip("/") 
        self.server = parsed.hostname
        self.port = parsed.port or (443 if parsed.scheme == "https" else 80)
        self.scheme = parsed.scheme