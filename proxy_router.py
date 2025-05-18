from urllib.parse import urlparse
import json
import os
class ProxyRouter:
    def __init__(self):
        self.routes = {}
        self.loadRoutesFromFile("routes.json")

    def checkRoutes(self, full_path):
        # Find the longest matching route prefix
        matching_routes = sorted(
            [route for route in self.routes if full_path.startswith(route)],
            key=len,
            reverse=True
        )

        if not matching_routes:
            raise ValueError(f"No route found for path: {full_path}")

        matched_prefix = matching_routes[0]
        target_url = self.routes[matched_prefix]
        target = RouteTarget(target_url)

        remaining_path = full_path[len(matched_prefix):]
        if not remaining_path.startswith("/"):
            remaining_path = f"/{remaining_path}"

        return target, remaining_path

    def registerRoutes(self, path, target_url):
        if path in self.routes:
            print(f"Warning: Overwriting route for {path}")
        self.routes[path] = target_url
        print(f"Registered route: {path} -> {target_url}")
        
    def loadRoutesFromFile(self, filename):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        full_path = os.path.join(base_dir, filename)
        with open(full_path, 'r') as f:
            data = json.load(f)
            for path, url in data.items():
                self.registerRoutes(path, url)
    def getAllRoutes(self):
        return dict(self.routes)
    
class RouteTarget:
    def __init__(self, url):
        parsed = urlparse(url)
        self.base_url = url.rstrip("/") 
        self.server = parsed.hostname
        self.port = parsed.port or (443 if parsed.scheme == "https" else 80)
        self.scheme = parsed.scheme