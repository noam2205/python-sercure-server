import socket
from paramiko import transport

from Tkinter import *
import tkFileDialog


class PythonClient(object):
	BUFFER_SIZE = 1024
	DONE_MESSAGE = "\xF3\x1BDONE\xF3\x1B"

	DEPENDENCIES_EXTENSION = ".txt"
	PY_EXTENSION = ".py"

	def __init__(self, (host, port), username, password):
		self._server_endpoint = (host, port)
		self._username = username
		self._password = password
		self._sock = None
		self._ssh_client = None
		self._ssh_session = None

	# Connects to the server and creates a secure channel

	def connect(self):
		self._sock = socket.socket()
		self._sock.connect(self._server_endpoint)
		self._ssh_client = transport.Transport(self._sock)
		self._ssh_client.connect(username=self._username, password=self._password)
		self._ssh_session = self._ssh_client.open_session()

	# Close the connection to the server

	def close(self):
		self._ssh_session.close()
		self._ssh_client.close()

	# Opens a file chooser dialog and sends the chosen file to the server

	def send_file(self):
		# file dialog handling
		root = Tk()
		root.withdraw()
		filename = tkFileDialog.askopenfilename(parent=root)
		# sending the file and the DONE flag at the end
		with open(filename, "rb") as send_file:
			f_buffer = send_file.read(self.BUFFER_SIZE)
			while f_buffer:
				self._ssh_session.send(f_buffer)
				f_buffer = send_file.read(self.BUFFER_SIZE)
			self._ssh_session.send(self.DONE_MESSAGE)

	# receive output from the server


	def recv_output(self):
		data = ""
		message = self._ssh_session.recv(2048)
		while message != self.DONE_MESSAGE:
			data += message
			message = self._ssh_session.recv(2048)
		return data


def main():
	ip = "127.0.0.1"
	port = int(raw_input("Port:"))
	username = raw_input("Username: ")
	password = raw_input("Password: ")

	client = PythonClient((ip, port), username, password)
	try:
		client.connect()
		client.send_file()
		print client.recv_output()
	except Exception as e:
		print str(e)
		client.close()


if __name__ == "__main__":
	main()
