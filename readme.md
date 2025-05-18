# 🚀 How could someone get started with your codebase?

To get started with the codebase:

- Clone the repo
- Make sure you have the following installed:
  - Docker
  - kubectl
  - Minikube
  - Python

- Mac:
  - ```brew install --cask docker kubectl minikube && brew install python```
- PC:
  - ```choco install -y docker-desktop kubernetes-cli minikube python```
  
- For local testing, simply run:

  ```bash
  python3 proxy_server.py
  ```

- For Minikube testing, complete the following steps or run the `deploy.sh` script located in the directory:

  ```bash
  eval $(minikube docker-env)
  docker build -t proxy-server:latest .
  kubectl apply -f proxy-deployment.yaml
  kubectl rollout restart deployment proxy-server
  ```

- Access the Minikube service using:

  ```bash
  minikube service proxy-server-service
  ```

  or

  ```bash
  minikube ip
  ```

---

# 📚 What resources did you use to build your implementation?

- Medium's super basic reverse-proxy:  
  https://thebytestream.medium.com/reverse-proxy-d0ff1b7b2231

- NGINX, as a real-world use case for ideas:  
  https://docs.nginx.com/nginx/admin-guide/web-server/reverse-proxy/

- ChatGPT/Claude for summaries, simplifications & further queries

---

# 🎨 Explain any design decisions you made, including limitations of the system

## 🛠 Design Decisions

- Super simple layout with a router, server, and logger
- Dynamic configuration of routes to allow flexibility (difficult with NGINX)
- Basic security implemented using bearer token, with room for expansion
- Minikube used to handle load balancing, as scaling is important
- Included routing allowing services to dynamically add their own routes

## ⚠️ Limitations

- No caching — Redis caching would improve speed and reduce backend load
- Security is minimal; improvements could include:
  - Whitelisting routing endpoints to a subnet
  - Adding encryption (TLS/SSL)
  - More robust bearer token system with expiries and request limits
  - Blocking known malicious requests dynamically
- No metrics collection
- No concurrency — no simultaneous request processing, which is a major bottleneck
- Audit logs are not very useful in current form
- Request and response handling need review, including passing all headers/data for edge cases
- No alerting system to filter or validate outgoing data for sensitive content

---

# 📈 How would you scale this?

- Implement concurrency to handle multiple simultaneous requests
- Use Minikube/Kubernetes for load balancing and scaling across nodes
- Add Redis caching to reduce backend load and improve response times

---

# 🔒 How would you make it more secure?

- Whitelist routing endpoints to trusted subnets
- Add TLS/SSL encryption
- Enhance bearer token system with expiry and rate limiting
- Dynamically block malicious requests and update blocklists

---

# 🤖 What resources (including programming tool assistants) did you use to build your implementation?

Most of the programming was done without standard programming assistants due to environment restrictions. Claude/ChatGPT and Python linters were used mainly for:

- Writing audit logging code
- General syntax and direction

The core ```proxy_router.py```and ```proxy_server.py``` components (beyond initial structure) were **NOT** coded using AI, as this is part of a technical evaluation.

---
