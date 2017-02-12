import argparse

from tracergui.traced_data import Graphviz, FilterException


def main():
    parser = argparse.ArgumentParser(prog="tracer2dot")
    parser.add_argument('-f', '--filter', help='Filter query to filter out unwanted objects from graph')
    parser.add_argument('directory', nargs='+', help='list of directories with reports')

    options = parser.parse_args()

    try:
        graph = Graphviz()
        for directory in options.directory:
            graph.load(directory)

        print(graph.create_graph(options.filter).get_content())
    except FileNotFoundError as e:
        print("Report error: {}".format(e))
    except FilterException as e:
        print("Filter error: {}".format(e.message))
