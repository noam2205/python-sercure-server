import os
import Queue
from threading import Lock

command_start = "docker"
image = "jfloff/alpine-python:2.7-slim"
lock = Lock()

# This class handles all of the containers and the operations within them
# The class holds a queue of available containers and supply them to clients


class DockerHandler(object):

	def __init__(self, maxsize):
		self._max_size = maxsize
		self.containers = Queue.Queue(self._max_size)
		self._delete_containers()
		for i in range(maxsize):
			curr = '%s%d' % ('cont', i)
			self.containers.put(curr)
			os.system('%s create --name %s %s' % (command_start, curr, image))  # creating a container

	#  returns an available container to use
	def get_container(self):
		lock.acquire()
		container = self.containers.get()
		lock.release()
		return container

	# puts a new container back in the queue after the client's use
	def return_container(self, container_name):
		lock.acquire()
		self.containers.put(container_name)
		lock.release()

	# copy file into the container root directory
	def copy_file_to_docker(self, source_dir, source_file, container_name):
		os.system("docker cp {source_dir}\\{file_name} {container}:{file_name}".format(
			source_dir=source_dir, file_name=source_file, container=container_name
		))

	# executes the main.py file in a secure way inside the container and retrieves the output
	# after that the container will be removed and a new one with the same name will be created
	def execute_py_file(self, container_name, thread_dir):
		os.system('%s start %s' % (command_start, container_name))  # starting the container
		#  executing the file in the docker container and saving the output/errors to a file
		os.system(
			'%s exec %s python main.py > %s\\%s.txt 2>&1' % (command_start, container_name, thread_dir, container_name))
		# stopping and removing the container to make a new one with no dependencies installed
		os.system('%s stop %s' % (command_start, container_name))
		os.system('%s rm %s' % (command_start, container_name))
		os.system('%s create --name %s %s' % (command_start, container_name, image))  # creating the same container
		self.return_container(container_name)

	# install the dependencies file inside the container using pip before the execution of the main.py file
	@staticmethod
	def install_dependencies(source_dir, req_file_path, container_name):
		# copy dependencies files to container
		os.system('%s cp %s\\%s %s:requirements.txt' % (command_start, source_dir, req_file_path, container_name))
		os.system('%s start %s' % (command_start, container_name))  # starting the container
		# installing dependencies using pip
		os.system('%s exec %s pip install -r requirements.txt' % (command_start, container_name))

	# creates a new set of containers before each server's startup
	def _delete_containers(self):
		print "Deleting containers"
		for i in range(self._max_size):
			os.system("docker stop cont{index}".format(
				index=i
			))
			os.system("docker rm cont{index}".format(
				index=i
			))
		print "Finished deleting containers"
