import os
import numpy as np
import networkx as nx
import pandas as pd
import argparse

DATA_LOC = '/home/gebhart/projects/rfunklab/data/patents_20190722'
COLLAB_EDGES_NAME = 'collaboration_edges.csv'
COLLAB_OUT_NAME = 'collaboration_graph.flag'
KNOWL_EDGES_NAME = 'knowledge_edges.csv'
KNOWL_OUT_NAME = 'knowledge_graph.flag'
DATA = True


def write_flag_file(g, output_file, data=DATA):
    zeros = np.zeros(len(g.nodes()), dtype=int)
    d = {k: v for v, k in enumerate(list(g.nodes()))}
    with open(output_file, 'w') as f:
        f.write('dim 0')
        f.write('\n')
        f.write(' '.join(map(str, zeros)))
        f.write('\n')
        f.write('dim 1')
        f.write('\n')
        if data:
            for e in g.edges(data=True):
                f.write('{} {} {}'.format(str(d[e[0]]), str(d[e[1]]), str(e[2]['weight'])))
                f.write('\n')
        else:
            for e in g.edges(data=False):
                f.write('{} {} {}'.format(str(d[e[0]]), str(d[e[1]]), '0'))
                f.write('\n')


def run(data_loc, output_location, collab=False, knowl=False, up_to=None, data=DATA):

    if collab:
        collab_graph = nx.Graph()
        print('Reading Collaboration Network ...')
        collab_df = pd.read_csv(os.path.join(data_loc, COLLAB_EDGES_NAME), header=0)
        if up_to is None:
            up_to = collab_df.shape[0]
        for idx, row in collab_df.iterrows():
            if idx > up_to:
                break
            if data:
                collab_graph.add_edge(row['inventor_id_a'], row['inventor_id_b'], weight=row['patents'])
            else:
                collab_graph.add_edge(row['inventor_id_a'], row['inventor_id_b'])
        print('Writing Collaboration Network ...')
        write_flag_file(collab_graph, os.path.join(output_location, COLLAB_OUT_NAME), data=data)

    if knowl:
        knowl_graph = nx.Graph()
        print('Reading Knowledge Network ...')
        knowl_df = pd.read_csv(os.path.join(data_loc, KNOWL_EDGES_NAME), header=0)
        if up_to is None:
            up_to = knowl_df.shape[0]
        for idx, row in knowl_df.iterrows():
            if idx > up_to:
                break
            if data:
                knowl_graph.add_edge(row['subgroup_id_a'], row['subgroup_id_b'], weight=row['patents'])
            else:
                knowl_graph.add_edge(row['subgroup_id_a'], row['subgroup_id_b'])
        print('Writing Knowledge Network ...')
        write_flag_file(knowl_graph, os.path.join(output_location, KNOWL_OUT_NAME), data=data)



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Patents read and write .flag')
    parser.add_argument('-d', '--data-location', type=str, required=False,
                        help='location of patent data', default=DATA_LOC)
    parser.add_argument('-c', '--collaboration', action='store_true',
                        help='whether to run collaboration graph')
    parser.add_argument('-k', '--knowledge', action='store_true',
                        help='whether to run knowledge graph')
    parser.add_argument('-o', '--output-location', type=str, required=False,
                        help='location to store .homology output', default=DATA_LOC)
    parser.add_argument('-u', '--up-to', type=int, required=False,
                        help='number of edges to include in the graph', default=None)
    parser.add_argument('-nw', '--no-weight', action='store_true',
                        help='throw to not include graph weights')

    args = parser.parse_args()
    if not args.collaboration and not args.knowledge:
        print('Throw either -k or -c (or both) to run')
    else:
        run(args.data_location, args.output_location, collab=args.collaboration,
            knowl=args.knowledge, up_to=args.up_to, data=(not args.no_weight))
