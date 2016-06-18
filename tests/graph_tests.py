from nose.tools import *
from src.revision_graph import revision_graph
import os
from os import listdir
		

def test_add_node():
	graph = revision_graph()
	nodes = [1]

	graph.add_nodes(nodes)
	assert 1 in graph.nodes

	more_nodes = [1,1]
	graph.add_nodes(nodes)
	assert len(graph.nodes) == 1

def test_add_edge():
	graph = revision_graph()

	graph.add_edge("A",["B"])
	assert "B" in graph.edges

def test_top_sort():
	graph = revision_graph()

	graph.add_nodes(["B","E","A","D","C","F","G"])

	graph.add_edge("A",["C"])
	graph.add_edge("B",["C"])
	graph.add_edge("B",["D"])
	graph.add_edge("C",["E"])
	graph.add_edge("E",["F"])
	graph.add_edge("F",["G"])
	graph.add_edge("D",["G"])

	output = graph.top_sort()

	assert output.index("D") > output.index("B")
	assert output.index("C") > output.index("A")
	assert output.index("E") > output.index("A")
	assert output.index("G") > output.index("C")
	assert output.index("F") > output.index("B")