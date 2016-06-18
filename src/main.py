import os
from os import listdir
# from os import isfile, join
from git_manager import GitManager
from revision_graph import revision_graph

'''
calculate the col length in order to print
'''
def cal_col_length(project_name, tests_without_ekstazi, tests_with_ekstazi):
	col_length = []
	col_length.append(30 - len(project_name))

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

projects_without_ekstazi = dict()
projects_with_ekstazi = dict()
os.chdir("git_projects")

# get results for each project
for project in listdir("./"):
	print project
	git_manager.set_project_name(project)
	(project_name, tests_without_ekstazi, tests_with_ekstazi) = git_manager.set_up()
	projects_without_ekstazi[project_name] = tests_without_ekstazi
	projects_with_ekstazi[project_name] = tests_with_ekstazi


os.chdir("..")

# # print the result
print "Results: "
with open("output.txt","w") as file:
	output = ""
	output += "-" * 106
	for key in projects_without_ekstazi:
		project_name = key
		tests_without_ekstazi = projects_without_ekstazi[key]
		tests_with_ekstazi = projects_with_ekstazi[key]
		col_length = cal_col_length(project_name, tests_without_ekstazi, tests_with_ekstazi)

		output += project_name + ' ' * col_length[0]
		for j in range(len(tests_without_ekstazi)):
			output += tests_without_ekstazi[j] + "/" + tests_with_ekstazi[j] + " " * col_length[j+1]
		output += "\n"
	output += "-" * 106
	file.write(output)

