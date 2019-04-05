import paramiko
import threading
import string
import os
import errno

class SetupThread(threading.Thread):

	def __init__(self, channel, transport):
		super(SetupThread, self).__init__()
		self.channel = channel
		self.transport = transport

	def run(self):
		current_path = os.path.realpath(os.getcwd()).__str__()
		thread_dir=current_path+"\\"+self.getName()
		os.mkdir(thread_dir)
		self.channel.send("Please submit the name of the .py file to run\r\n")
		self.channel.send("Make sure both the file and the requirements file are in the working directory\r\n")
		file_name = self.channel.recv(20)
		sftp_client = paramiko.SFTPClient.from_transport(self.transport)
		sftp_client.get(file_name,thread_dir+"\index.py")
		# checking if requirements file exists
		try:
			sftp_client.stat(file_name)
			sftp_client.get("requirements.txt",thread_dir+"requirements.txt")
		except IOError as e:
			if e.errno == errno.ENOENT:
				print "no requirements file exists"
		sftp_client.close()
		os.rmdir(thread_dir)

class ThreadPool():

	def __init__(self,NumOfThreads):
		self.alive_threads = []
		self.sem=threading.Semaphore(NumOfThreads)

	def add_thread(self,other):
		self.sem.acquire()
		self.alive_threads.append(other)

	def remove_thread(self,other):
		self.alive_threads.remove(other)
		self.sem.release()


