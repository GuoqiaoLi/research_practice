import os
from urllib2 import Request, urlopen, URLError
import subprocess
import httplib
import json
from os import listdir
from revision_graph import revision_graph


class GitManager:
	project_name = None

	def __init__(self):
		self.project_name = None
		self.graph = None

	def set_project_name(self, name):
		self.project_name = name
		self.graph = revision_graph()

	def find_projects(self):
		# use http request to search for projects
		results = urlopen('https://api.github.com/search/repositories?q=maven+language:java&sort=stars&order=desc').read()
		projects = json.loads(results)['items']
		os.chdir("git_projects")

		# iterate through projects
		count = 0
		for project in projects:
			project_name = project['name']
			project_clone_url = project['clone_url']
			project_size = project['size']

			if project_size > 5000:
				continue

			# if already exist, skip
			if project_name in listdir("./"):
				continue

			print "==================================\n"
			print "Cloning project " + project_name + "\n"
			print "==================================\n"
			self.clone_project(project_clone_url)

			os.chdir(project_name)

			# check if it's a valid project(compile and should have test)
			print "==================================\n"
			print "Checking Validality" + "\n"
			if self.check_if_valid() and self.check_if_has_thirty_revisions():
					count += 1
					print "Valid Project Number: " + str(count) + "\n"
					print project_name + " is a VALID project"
					print "==================================\n"
					os.chdir("..")
					if count == 5:
						return

					continue

			print project_name + " is an INVALID project"
			print "==================================\n"	
			os.chdir("..")
			os.system("rm -rf " + project_name) 



	'''
	clone project to git_projects file
	@param project_url: clone url of project
	'''
	def clone_project(self, project_url):	
		os.popen('git clone ' + project_url)
		
	'''
	check if it's a valid project(build successfully and have tests)
	@param project_name: name of project
	'''
	def check_if_valid(self):
		tag_if_compile = True
		tag_if_has_tests = False
		tag_if_has_errors = False

		# run mvn test
		terminal_log = os.popen('mvn test').readlines()
		for line in terminal_log:
			if "FAILURE" in line:
				tag_if_compile = False
			if "Tests run" in line:
				tag_if_has_tests = True
			if "Error:" in line:
				tag_if_has_errors = True

		return tag_if_compile and tag_if_has_tests and not tag_if_has_errors


	def check_if_has_thirty_revisions(self):
		number_of_revisions = os.popen("git rev-list --all").readlines()
		if len(number_of_revisions) < 30:
			return False
		return True

	'''
	get ten revisions for the project
	'''
	def get_ten_git_revisions(self):
		print "Getting ten lastest revisions..."

		for commit_history in os.popen("git rev-list --all").readlines():
			line = os.popen("git rev-list --parents -n 1 " + commit_history.rstrip()).readlines()[0].rstrip().split(" ")
			parents = line[1:]
			child = line[:1]
			
			self.graph.add_nodes(line)
			self.graph.add_edge(child[0],parents)

		ten_git_revisions = []
		revisions = self.graph.top_sort()[0:30]
		i = 29
		while i >= 0:
			ten_git_revisions.append(revisions[i])
			i -= 3

		write_revision_shas(ten_git_revisions)

		return ten_git_revisions



	def write_revision_shas(self, shas):
		content = ""
		for item in shas:
			content += item + "\n"
		with open("shas.txt","w") as file:
			file.write(content)

	'''
	run 10 revisions for a project and return the number of tests run with and without ekstazi for those 10 revisions
	'''
	def set_up(self):
		print "\n========================================================"
		print "Project name: " + self.project_name
		print "========================================================\n"

		tests_without_ekstazi = []
		tests_with_ekstazi = []
		flag = False

		os.chdir(self.project_name)

		ten_latest_revisions = self.get_ten_git_revisions()

		for i in range(len(ten_latest_revisions)):
			latest_revision = ten_latest_revisions[i]
			print "\n========================================================"
			print "ITERATION " + str(i)
			print "Running test for revision: " + latest_revision + "..." 

			# checkout the revision
			checkout_command = "git checkout -f " + latest_revision
			os.popen(checkout_command)

			# some revisions in the project are broken
			if not "pom.xml" in listdir("./"):
				tests_without_ekstazi.append("N")
				tests_with_ekstazi.append("N")
				continue

			# is it an ekstazi project, if not add plugin to pom.xml

			# run without ekstazi
			"\n##########################"
			print "Run tests without ekstazi"
			count = 0
			for line in os.popen("mvn test").readlines():
				if "Running" in line:
					count += 1

			tests_without_ekstazi.append(str(count))

			# add ekstazi to pom
			self.write_ekstazi_to_pom()


			# run with ekstazi
			print "\n##########################"
			print "Run tests with ekstazi"
			count = 0
			for line in os.popen("mvn test").readlines():
				if "Running" in line:
					count += 1

			tests_with_ekstazi.append(str(count))

		os.chdir("..")

		return (self.project_name, tests_without_ekstazi, tests_with_ekstazi)


	'''
	is it a ekstazi project?
	'''
	def check_if_ekstazi_project(self, path):
		with open(path, "r") as file:
			pom_content = file.read()
			if "ekstazi" not in pom_content:
				return False
			else:
				return True

	'''
	add plugin to pom.xml
	'''
	def write_ekstazi_to_pom(self):
		java_command = ""

		poms = os.popen("find . -name pom.xml").readlines()
		for pom in poms:
			pom = pom[2:]
			if not "target" in pom:
				if not self.check_if_ekstazi_project(pom.rstrip()):
					java_command += "git_projects/" + self.project_name + "/" + pom.rstrip() + " "
		os.chdir("../..")
		os.popen("java AddEkstaziToPom " + java_command)
		os.chdir("git_projects/" + self.project_name)

		return poms
