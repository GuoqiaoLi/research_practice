class revision_graph:

	def __init__(self):
		self.nodes = []
		self.edges = dict()
		self.back_edges = dict()

	def add_nodes(self, nodes):
		for node in nodes:
			if node not in self.nodes:
				self.nodes.append(node)
				self.edges[node] = []
				self.back_edges[node] = []

	def add_edge(self, child, parents):
		for parent in parents:
			if parent in self.edges:
				self.edges[parent].append(child)
			else:
				self.edges[parent] = [child]

		if child in self.back_edges:
			self.back_edges[child].extend(parents)
		else:
			self.back_edges[child] = parents

	def print_edges(self):
		for key in self.edges:
			print "start point: " + key
			for child in self.edges[key]:
				print "child: " + child
			print "\n"

	def top_sort(self):
		visited = []
		output = []

		for node in self.nodes:
			if node not in visited:
				self.top_sort_helper(node, visited, output)

		return output



	def top_sort_helper(self, node, visited, output):
		visited.append(node)

		for child in self.edges[node]:
			if child not in visited:
				self.top_sort_helper(child, visited, output)

		output.append(node)




