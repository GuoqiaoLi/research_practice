import os
from urllib2 import Request, urlopen, URLError
import subprocess
import httplib
import json
from os import listdir
class GitManager:
	project_name = None

	def __init__(self):
		pass

	def set_project_name(self, name):
		self.project_name = name

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
			if self.check_if_valid(project_name):
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
		print project_url	
		os.popen('git clone ' + project_url)
		
	'''
	check if it's a valid project(build successfully and have tests)
	@param project_name: name of project
	'''
	def check_if_valid(self, project_name):
		tag_if_compile = True
		tag_if_has_tests = False
		tag_if_has_errors = False
		tag_less_than_thirty_revisions = False

		# run mvn test
		terminal_log = os.popen('mvn test').readlines()
		for line in terminal_log:
			if "FAILURE" in line:
				tag_if_compile = False
			if "Tests run" in line:
				tag_if_has_tests = True
			if "Error:" in line:
				tag_if_has_errors = True

		number_of_revisions = os.popen("git rev-list --all").readlines()
		if len(number_of_revisions) < 30:
			tag_less_than_thirty_revisions = True



		return tag_if_compile and tag_if_has_tests and not tag_if_has_errors and not tag_less_than_thirty_revisions

	'''
	get ten revisions for the project
	'''
	def get_ten_git_revisions(self):
		ten_latest_revisions = []
		logs = os.popen("git rev-list --all").readlines()
		i = 30
		while i >= 0:
			ten_latest_revisions.append(logs[i].rstrip())
			i -= 3

		
		#write SHAs to SHAs.txt
		SHAs = open("SHAs.txt", "w")
		ten_SHAs = ""
		for revision in ten_latest_revisions:
			ten_SHAs += revision + "\n"
		SHAs.write(ten_SHAs)


		return ten_latest_revisions

	'''
	run 10 revisions for a project and return the number of tests run with and without ekstazi for those 10 revisions
	'''
	def set_up(self):
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
				tests_without_ekstazi.append("broken")
				tests_with_ekstazi.append("broken")
				continue

			# is it an ekstazi project, if not add plugin to pom.xml
			if not self.check_if_ekstazi_project():
				print "This is not an ekstazi project"
				self.write_ekstazi_to_pom()

			#run without ekstazi
			print "\n##########################"
			print "Run tests without ekstazi"
			no_test_selected_tag = True
			for line in os.popen("mvn test").readlines():
				if "Results" in line:
					flag = True
				if "Tests run" in line and flag:
					no_test_selected_tag = False
					#parse the line and get the number
					parsed_line = line.rstrip().split(",")
					tests_without_ekstazi.append(parsed_line[0][11:])
					flag = False
					break
			if no_test_selected_tag:
				tests_with_ekstazi.append("0")


			# run with ekstazi
			print "\n##########################"
			print "Run tests with ekstazi"
			no_test_selected_tag = True
			for line in os.popen("mvn ekstazi:ekstazi").readlines():
				if "Results" in line:
					flag = True
				if "Tests run" in line and flag:
					no_test_selected_tag = False
					#parse the line and get the number
					parsed_line = line.rstrip().split(",")
					print "There are " + parsed_line[0][11:] + "tests selected with ekstazi"
					tests_with_ekstazi.append(parsed_line[0][11:])
					flag = False
					break
			if no_test_selected_tag:
				tests_with_ekstazi.append("0")

		os.chdir("..")

		return (self.project_name, tests_without_ekstazi, tests_with_ekstazi)


	'''
	is it a ekstazi project?
	'''
	def check_if_ekstazi_project(self):
		project_pom = open("pom.xml", "r")
		pom_content = project_pom.read()
		if "ekstazi" not in pom_content:
			return False
		else:
			return True

	'''
	add plugin to pom.xml
	'''
	def write_ekstazi_to_pom(self):
		tag = False
		plugin_inside_pluginmanagement = False
		pom_content = ""
		project_pom_read = open("pom.xml", "r")
		for line in project_pom_read.readlines():
			if "<build>" in line:
				flag = True
			if "<pluginManagement>" in line:
				plugin_inside_pluginmanagement = True
	
			if "</pluginManagement" in line:
				plugin_inside_pluginmanagement = False

			if "<plugins>" in line and flag and not plugin_inside_pluginmanagement:
				pom_content += line
				pom_content += "<plugin>\n"
				pom_content += "<groupId>org.ekstazi</groupId>\n"
				pom_content += "<artifactId>ekstazi-maven-plugin</artifactId>\n"
				pom_content += "<version>4.6.1</version>\n"
				pom_content += "</plugin>\n"
				flag = False
				continue

			if "</build>" in line and flag:
				pom_content += "<plugins>\n"
				pom_content += "<plugin>\n"
				pom_content += "<groupId>org.ekstazi</groupId>\n"
				pom_content += "<artifactId>ekstazi-maven-plugin</artifactId>\n"
				pom_content += "<version>4.6.1</version>\n"
				pom_content += "</plugin>\n"
				pom_content += "</plugins>\n"
				flag = False

			pom_content += line


		project_pom_write = open("pom.xml", "w")
		project_pom_write.write(pom_content)
