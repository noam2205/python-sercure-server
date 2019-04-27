import paramiko
import socket
from PythonServer import Server
from ThreadHandler import SetupThread, ThreadPool
from DockerHandler import DockerHandler

HOST_KEY = paramiko.RSAKey.from_private_key_file(".\\server_rsa.key")
MAX_CLIENTS = 3

# accepts a new clients and creates a new thread for him


def handle_new_client(client_socket, thread_controller, docker_handler, ssh_server):
	transport = paramiko.Transport(client_socket)
	transport.add_server_key(HOST_KEY)
	transport.start_server(server=ssh_server)
	print "Ready to open channels!"
	channel = transport.accept()
	print str(ssh_server.username) + " Connected"
	user_thread = SetupThread(channel, transport, docker_handler, thread_controller)
	thread_controller.add_thread(user_thread)
	user_thread.start()

# setup for the server's socket binding


def setup_server(ip, port):
	server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	server_socket.bind((ip, port))
	server_socket.listen(10)
	return server_socket

# setting up server's data structures and credentials


def main():
	server_password = raw_input("Server's Password: ")
	ip = "127.0.0.1"
	port = int(raw_input("Port: "))
	ssh_server = Server(server_password)
	docker_handler = DockerHandler(MAX_CLIENTS)
	thread_controller = ThreadPool(MAX_CLIENTS)
	socket_server = setup_server(ip, port)
	# waiting for new clients
	while True:
		try:
			print("\nwaiting for connections on %s:%d" % (ip, port))
			client, addr = socket_server.accept()
			print "{client_info} connected".format(client_info=addr)
			handle_new_client(client, thread_controller, docker_handler, ssh_server)
		except Exception as e:
			print "Exception: {exc}".format(exc=e)


if __name__ == "__main__":
	main()


