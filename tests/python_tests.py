from nose.tools import *
from src.git_manager import GitManager
import os
from os import listdir
		

def create_git_projects_dir():
	os.chdir("src")
	if not os.path.exists("git_projects"):
		os.mkdir("git_projects")
	os.chdir("..")

def set_up():
	create_git_projects_dir()
	os.chdir("src/git_projects")
	create_invalid_maven_project()
	create_simple_maven_project()

def teardown():
	remove_invalid_maven_project()
	remove_simple_maven_project()
	os.chdir("../..")

def multi_module_project_set_up():
	create_git_projects_dir()
	os.chdir("src/git_projects")
	create_simple_maven_project()
	os.chdir("my-app")
	create_second_maven_project()
	os.chdir("..")



def create_invalid_maven_project():
	if not os.path.exists("invalid_maven_proejct"):
		os.makedirs("invalid_maven_proejct")

def remove_invalid_maven_project():
	if os.path.exists("invalid_maven_proejct"):
		os.rmdir("invalid_maven_proejct")

def create_simple_maven_project():
	create_simple_maven_project_command = "mvn archetype:generate -DgroupId=com.mycompany.app -DartifactId=my-app -DarchetypeArtifactId=maven-archetype-quickstart -DinteractiveMode=false"
	os.popen(create_simple_maven_project_command)

def create_second_maven_project():
	os.popen("mvn archetype:create-from-project")
	os.chdir("target/generated-sources/archetype/")
	os.popen("mvn install")
	os.chdir("../../..")

def remove_simple_maven_project():
	if os.path.exists("my-app"):
		os.popen("rm -rf my-app")

@with_setup(set_up, teardown)
def test_check_valid():
	git_manager = GitManager()

	# first create a file in git_projects folder
	os.chdir("invalid_maven_proejct")
	assert not git_manager.check_if_valid()
	os.chdir("..")

	os.chdir("my-app")
	assert git_manager.check_if_valid()
	os.chdir("..")


@with_setup(set_up, teardown)
def test_if_ekstazi_project():
	git_manager = GitManager()
	assert not git_manager.check_if_ekstazi_project("my-app/pom.xml")



@with_setup(multi_module_project_set_up, teardown)
def test_write_tests_to_pom():
	git_manager = GitManager()
	git_manager.set_project_name("my-app")
	os.chdir("my-app")
	poms = git_manager.write_ekstazi_to_pom()
	print len(poms)
	for pom in poms:
		print pom
	for pom in poms:
		if "target" not in pom:
			pom_content = os.popen("cat " + pom).readlines()
			has_ekstazi = False
			for line in pom_content:
				if "ekstazi" in line:
					has_ekstazi = True

			assert has_ekstazi
	os.chdir("..")

