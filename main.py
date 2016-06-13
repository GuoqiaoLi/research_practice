import os
from os import listdir
# from os import isfile, join
from git_manager import GitManager


'''
calculate the col length in order to print
'''
def cal_col_length(project_name, tests_without_ekstazi, tests_with_ekstazi):
	col_length = []

	# first calculate first col
	if len(project_name) > 21:
		project_name = project_name[0:16] + "..."

	col_length.append(21 - len(project_name))

	# then calculate the rest
	for i in range(len(tests_without_ekstazi)):
		col_content = tests_without_ekstazi[i] + "/" + tests_with_ekstazi[i]
		col_length.append(7 - len(col_content))

	return col_length


# create git_projects folder
if not os.path.exists("git_projects"):
	os.makedirs("git_projects")

# clone five projects
git_manager = GitManager()
git_manager.find_projects()



project_names = []
project_tests_without_ekstazi = []
project_tests_with_ekstazi = []

os.chdir("git_projects")

# get results for each project
for project in listdir("./"):
	git_manager.set_project_name(project)
	(project_name, tests_without_ekstazi, tests_with_ekstazi) = git_manager.set_up()
	project_names.append(project_name)
	project_tests_without_ekstazi.append(tests_without_ekstazi)
	project_tests_with_ekstazi.append(tests_with_ekstazi)

# print the result
print "Results: "
print "-" * 106
for i in range(len(project_names)):
	project_name = project_names[i]
	tests_without_ekstazi = project_tests_without_ekstazi[i]
	tests_with_ekstazi = project_tests_with_ekstazi[i]
	col_length = cal_col_length(project_name, tests_without_ekstazi, tests_with_ekstazi)

	output = " " + project_name + ' ' * col_length[0]
	for j in range(len(tests_without_ekstazi)):
		output += " " + tests_without_ekstazi[j] + "/" + tests_with_ekstazi[j] + " " * col_length[j+1]
	print output
print "-" * 106

