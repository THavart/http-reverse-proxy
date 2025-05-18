

Load balancing: Reverse proxies can distribute incoming traffic across multiple servers to improve performance and handle more requests. This helps ensure that no single server is overwhelmed by traffic, leading to better response times and improved reliability.
Caching: Reverse proxies can cache frequently requested resources, reducing server load and improving response times for subsequent requests. This is particularly useful for static resources such as images, CSS files, and JavaScript files.
Security: Reverse proxies can provide an additional layer of security by filtering incoming traffic, blocking malicious requests, and hiding server IP addresses. This can help protect servers from DDoS attacks, brute-force attacks, and other security threats.
SSL encryption: Reverse proxies can provide SSL encryption for incoming traffic, enabling secure communication between clients and servers. This helps protect sensitive data such as passwords, credit card information, and other personal information from interception and eavesdropping.

Plans:

- Stand up basic K8s cluster.
- Allow proxy server to spin up additional nodes for load balancing (What does a node look like?)
    - Audit Logging
    - Encryption
    - Caching
    - Proxy server should use the node that has the cache it needs
    - But we should probably allow each node to cache the same data, for now.
    - This means each node needs to communicate, share the same cache. 
    - So we need cache nodes, and proxy nodes. 
- Set thresholds for when to do so, when to spin down
- 