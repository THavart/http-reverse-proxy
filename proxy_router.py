from urllib.parse import urlparse
import json
import os
class ProxyRouter:
    def __init__(self):
        self.routes = {}
        self.loadRoutesFromFile("routes.json")

    def checkRoutes(self, path):
        if target_url := self.routes.get(path):
            return RouteTarget(target_url)
        else:
            raise ValueError(f"No route found for path: {path}")  

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
        self.server = parsed.hostname
        self.port = parsed.port or (443 if parsed.scheme == "https" else 80)