import threading
import os
import shutil
import zipfile


# This class represents a client thread which will handle the client's files and execute them securely

class SetupThread(threading.Thread):
	PY_FILE_HEADER = "\xF3\x1BPY_FILE_INCOMING\xF3\x1B"
	DEPENDENCIES_EXTENSION = "txt"
	DONE_MESSAGE = "\xF3\x1BDONE\xF3\x1B"

	def __init__(self, channel, transport, docker_handler,thread_handler):
		super(SetupThread, self).__init__()
		self._channel = channel
		self._transport = transport
		self._docker_handler = docker_handler
		self._thread_handler = thread_handler
		self._container = None
		self._thread_dir = ".\\" + self.getName()

	def run(self):
		# asking for a docker container from the docker handler to execute the python program inside
		data = ""
		self._container = self._docker_handler.get_container()

		# creating a directory for the client's files
		if not os.path.isdir(self._thread_dir):
			os.mkdir(self._thread_dir)

		# receiving the client zip file with the contents to execute
		message = self._channel.recv(2048)
		while message != self.DONE_MESSAGE:
			data += message
			message = self._channel.recv(2048)

		with open(self._thread_dir + "\\source.zip", "wb") as source_zip_file:
			source_zip_file.write(data)

		# extracting the contents of the zip file
		zip_obj = zipfile.ZipFile(self._thread_dir + "\\source.zip", "r")
		zip_obj.extractall(self._thread_dir)
		zip_obj.close()

		# sending back the output
		self._channel.send(self.handle_source())
		self._channel.send(self.DONE_MESSAGE)

		# removing the client's directory and freeing a thread slot for new clients
		shutil.rmtree(self._thread_dir)
		self._thread_handler.remove_thread(self)

	# handling all the files which were in the zip file
	def handle_source(self):
		source_files = os.listdir(self._thread_dir)
		# installing dependencies inside the container
		self.install_dependencies([x for x in source_files if x.split(".")[-1:][0] == "txt"])
		# executing the main.py file inside the container and receiving the output and errors
		self.run_py([x for x in source_files if x.split(".")[-1:][0] == "py"])
		with open("{thread_dir}\\{output_file}.txt".format(thread_dir=self._thread_dir,
														   output_file=self._container), "rb") as output_file:
			return output_file.read()

	# moving into the container and installing each dependencies file
	def install_dependencies(self, source_files):
		for source_file in source_files:
			self._docker_handler.install_dependencies(self._thread_dir, source_file, self._container)

	# moving all the py file into the container and executing the main.py file
	def run_py(self, file_sources):
		[self._docker_handler.copy_file_to_docker(self._thread_dir, x, self._container) for x in file_sources]
		self._docker_handler.execute_py_file(self._container, self._thread_dir)

# This class handles the alive threads according to max clients capacity


class ThreadPool(object):

	def __init__(self, num_of_threads):
		self._alive_threads = []
		self._sem = threading.Semaphore(num_of_threads)

	def add_thread(self, new_thread):
		self._sem.acquire()
		self._alive_threads.append(new_thread)

	def remove_thread(self, new_thread):
		self._alive_threads.remove(new_thread)
		self._sem.release()
