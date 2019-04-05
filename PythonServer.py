
import paramiko

host_key = paramiko.RSAKey(filename="server_rsa.key")
server_password = raw_input("Enter Server's Password: ")
paramiko.util.log_to_file("PythonServer.log")


class Server(paramiko.ServerInterface):

	def __init__(self):
		self.username = None
		pass

	def check_channel_request(self, kind, chanid):
		if kind == "session":
			return paramiko.OPEN_SUCCEEDED
		return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

	def check_auth_publickey(self, username, key):
		# all are allowed
		return paramiko.AUTH_SUCCESSFUL

	def check_auth_password(self, username, password):
		if password == server_password:
			self.username = username
			return paramiko.AUTH_SUCCESSFUL
		return paramiko.AUTH_FAILED

	def get_allowed_auths(self, username):
		return "password, public key"

	def check_channel_shell_request(self, channel):
		return True

	def check_channel_pty_request(
			self, channel, term, width, height, pixelwidth, pixelheight, modes
	):
		return True

