import paramiko

host_key = paramiko.RSAKey(filename="server_rsa.key")
paramiko.util.log_to_file("PythonServer.log")


# This class represents the setup for the server including: authentication methods and clients credentials handling

class Server(paramiko.ServerInterface):

	def __init__(self, server_password):
		self.username = None
		self._password = server_password

	def check_channel_request(self, kind, chanid):
		if kind == "session":
			return paramiko.OPEN_SUCCEEDED
		return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

	def check_auth_publickey(self, username, key):
		# all are allowed
		return paramiko.AUTH_SUCCESSFUL

	def check_auth_password(self, username, password):
		if password == self._password:
			self.username = username
			return paramiko.AUTH_SUCCESSFUL
		return paramiko.AUTH_FAILED

	def get_allowed_auths(self, username):
		return "password, public key"

	def check_channel_shell_request(self, channel):
		return True

	def check_channel_pty_request(self, channel, term, width, height, pixelwidth, pixelheight, modes):
		return True
