
import paramiko
import socket
import os
from PythonServer import Server
from ThreadHandler import SetupThread, ThreadPool

PORT = int(raw_input("Listening Port: "))
IP = "127.0.0.1"

server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((IP, PORT))
server_socket.listen(10)
thread_control=ThreadPool(10)
current_path = os.path.realpath(os.getcwd()).__str__()

while True:
	try:
		print("waiting for connections on %s:%d" % (IP, PORT))
		client, addr = server_socket.accept()
		print str(addr) + " connected"
		transport = paramiko.Transport(client)
		host_key = paramiko.RSAKey.from_private_key_file(current_path + "\server_rsa.key")
		transport.add_server_key(host_key)
		ssh_server = Server()
		transport.start_server(server=ssh_server)
		print "Ready to open channels!"
		channel = transport.accept()
		print str(ssh_server.username) + " Connected"
		userThread = SetupThread(channel, transport)
		thread_control.add_thread(userThread)
		userThread.start()
	except Exception as e:
		print e

