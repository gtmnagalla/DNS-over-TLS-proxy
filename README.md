DNS-over-TLS proxy

The code is a simple DNS-over-TLS proxy written in Python which handles multiple dns requests. It imports necessary modules such as sys, ssl, socket, logging, and multiprocessing. It defines a function called tls_wrapper that creates an SSL wrapper for a socket and sends and receives packets. It also defines two classes, DNSoverTCP and DNSoverUDP, which handle TCP and UDP requests respectively. The main function creates TCP and UDP servers and starts them as separate processes. The servers listen on a specified port and forward DNS requests to a specified DNS server using TLS encryption. The code also includes error handling for timeouts and socket errors.

listens on the port 53 for TCP and UDP communications. Prefixing the message with the two bytes of length information that the inbound UDP message has causes plain UDP packets to be converted to TCP. Default buffer size is set to 1024, and socket timeout set to 5secs.

Creates a secure connection by default over port 853 to the Cloudflare DNS (1.1.1.1). To connect with the dns_server, the Python function "create_default_context" from the built-in ssl library was used. The function loads the trusted CA certificates for the system, checks the hostname, and configures a secure protocol and cypher with appropriate values.

Sourcecode: DNS-proxy.py

Installation Steps:
1. Build docker image using 'Dockerfile':
docker build -t dns-proxy .

2. Create docker network:
docker network create --subnet 172.16.1.0/24 dnsNet

3. Run the container by using the created docker image:
docker run --net dnsNet dns-proxy sleep infinity

4. Check the container status:
docker ps


Testing: 

nslookup google.com 172.16.1.2

kdig @172.16.1.2 google.com A +tcp

dig @172.16.1.2 -p 53 google.com
