#!/usr/bin/env python

import sys
import ssl
import socket
import logging
import multiprocessing
from socketserver import BaseRequestHandler, ThreadingTCPServer, ThreadingUDPServer

# Setup logging configuration
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

# Define the Cloudflare DNS server address, proxy, buffersize and port number.
DNS_SERVER = '1.1.1.1'
DNS_PROXY = ''
PROXY_PORT = 53
BUFFER_SIZE = 1024

#function provides a secure TLS wrapper for socket communication with Cloudfare DNS server.
def tls_wrapper(packet, hostname, port=853) -> bytes:
    context = ssl.create_default_context(purpose=ssl.Purpose.SERVER_AUTH)
    with socket.create_connection((hostname, port), timeout=5) as sock:
        with context.wrap_socket(sock, server_hostname=hostname) as tlssock:
            tlssock.send(packet)
            result = tlssock.recv(BUFFER_SIZE)
            return result

# DNSoverUDP class which handles DNS-over-UDP requests from client.
class DNSoverUDP(BaseRequestHandler):

    # method handling the UDP requests.
    def handle(self) -> None:        
        try:
            logging.info('UDP connection from %s', self.client_address)
            msg, sock = self.request
            tcp_packet = self.udp_to_tcp(msg)
            tls_answer = tls_wrapper(tcp_packet, hostname=DNS_SERVER)
            udp_answer = tls_answer[2:]
            sock.sendto(udp_answer, self.client_address)
        except socket.timeout as err:
            logging.error('TIMEOUT ERROR: %s', err)
            sys.exit(1)
        except socket.error as err:
            logging.error('ERROR OCCURRED: %s', err)
            sys.exit(1)

    # method used to convert UDP packets to TCP packets.
    @staticmethod
    def udp_to_tcp(packet) -> bytes:
        packet_len = bytes([00]) + bytes([len(packet)])
        packet = packet_len + packet
        return packet

# DNSoverTCP class which handles DNS-over-TCP requests from client.
class DNSoverTCP(BaseRequestHandler):

    # method handling the TCP requests.
    def handle(self) -> None:       
        try:
            logging.info('TCP connection from %s', self.client_address)
            while True:
                msg = self.request.recv(BUFFER_SIZE)
                if not msg:
                    break
                answer = tls_wrapper(msg, hostname=DNS_SERVER)
                self.request.send(answer)
        except socket.timeout as err:
            logging.error('TIMEOUT ERROR: %s', err)
            sys.exit(1)
        except socket.error as err:
            logging.error('ERROR OCCURRED: %s', err)
            self.request.close()
            sys.exit(1)

# sets up DNS proxy instances, one for TCP and one for UDP.
def main() -> None:
    ThreadingTCPServer.allow_reuse_address = True
    ThreadingUDPServer.allow_reuse_address = True
    tcp_proxy = ThreadingTCPServer((DNS_PROXY, PROXY_PORT), DNSoverTCP)
    udp_proxy = ThreadingUDPServer((DNS_PROXY, PROXY_PORT), DNSoverUDP)
    tcp_process = multiprocessing.Process(target=tcp_proxy.serve_forever)
    udp_process = multiprocessing.Process(target=udp_proxy.serve_forever)
    tcp_process.start()
    logging.info('DNS Proxy over TCP started and listening on port %s', PROXY_PORT)
    udp_process.start()
    logging.info('DNS Proxy over UDP started and listening on port %s', PROXY_PORT)

if __name__ == '__main__':
    main()