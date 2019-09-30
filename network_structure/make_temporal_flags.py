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

patentsview_knowledge_keys = ['subgroup_id_a','subgroup_id_b','patents']
aps_knowledge_keys = ['pacs_a','pacs_b','dois']
patentsview_collaboration_keys = ['inventor_id_a','inventor_id_b','patents']
aps_collaboration_keys = ['author_id_a', 'author_id_b', 'papers']


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


def run(data_loc, output_location, collab=False, knowl=False, dataset='patentsview', up_to=None, data=DATA, keys=[]):

    if not collab and not knowl:
        raise ValueError('one of collaboration or knowledge must be true')

    if len(keys) == 0:
        if dataset == 'patentsview':
            keys = patentsview_collaboration_keys if collab else patentsview_knowledge_keys
        if dataset == 'aps':
            keys = aps_collaboration_keys if collab else aps_knowledge_keys
        else:
            raise ValueError('dataset {} not understood'.format(dataset))

    fs = [f for f in os.listdir(data_loc) if os.path.isfile(os.path.join(data_loc, f))]
    fs.sort()
    for f in fs:
        g = nx.Graph()
        print('{}'.format(f))
        df = pd.read_csv(os.path.join(data_loc, f), header=0)
        for idx, row in df.iterrows():
            g.add_edge(row[keys[0]], row[keys[1]], weight=row[keys[2]])
        write_flag_file(g, os.path.join(data_loc, 'flag', '{}.flag'.format(f.replace('.csv',''))), data=True)



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Patents read and write .flag')
    parser.add_argument('-d', '--data-location', type=str, required=False,
                        help='location of patent data', default=DATA_LOC)
    parser.add_argument('-ds', '--dataset', type=str, required=True,
                        help='which dataset from which these graphs are derived')
    parser.add_argument('-c', '--collaboration', action='store_true',
                        help='whether to run collaboration graph')
    parser.add_argument('-k', '--knowledge', action='store_true',
                        help='whether to run knowledge graph')
    parser.add_argument('-o', '--output-location', type=str, required=True,
                        help='location to store .homology output')
    parser.add_argument('-u', '--up-to', type=int, required=False,
                        help='number of edges to include in the graph', default=None)
    parser.add_argument('-nw', '--no-weight', action='store_true',
                        help='throw to not include graph weights')

    args = parser.parse_args()
    if not args.collaboration and not args.knowledge:
        print('Throw either -k or -c (or both) to run')
    else:
        run(args.data_location, args.output_location, collab=args.collaboration,
            knowl=args.knowledge, up_to=args.up_to, data=(not args.no_weight), dataset=args.dataset)
