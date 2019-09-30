import os
import subprocess

graph_type = 'knowledge'
category_id = 1
graph_loc = '/home/gebhart/projects/rfunklab/data/temporal/1_1/{}/{}/flag'.format(graph_type,category_id)
out_loc = '/home/gebhart/projects/rfunklab/data/temporal/1_1/{}/{}/homology'.format(graph_type, category_id)

yrs = list(range(1970,2017))

fnames = [f for f in os.listdir(graph_loc) if os.path.isfile(os.path.join(graph_loc, f))]
fnames.sort()
for name in fnames:
    if int(name[:4]) in yrs:
        print(name)
        inf = os.path.join(graph_loc, name)
        outf = os.path.join(out_loc, name.replace('flag', 'homology'))
        print(subprocess.run(["/home/gebhart/projects/flagser/flagser --undirected --max-dim 9 --approximate 1000 --filtration max --out {} {}".format(outf, inf)], shell=True))
