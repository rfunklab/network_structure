import os
import subprocess

graph_type = 'collaboration'
window = '1_1'
graph_loc = '/home/gebhart/projects/rfunklab/data/temporal/aps/{}/{}/flag'.format(window,graph_type)
out_loc = '/home/gebhart/projects/rfunklab/data/temporal/aps/{}/{}/homology'.format(window,graph_type)

yrs = list(range(1970,2019))

fnames = [f for f in os.listdir(graph_loc) if os.path.isfile(os.path.join(graph_loc, f))]
fnames.sort()
for name in fnames:
    if int(name[:4]) in yrs:
        print(name)
        inf = os.path.join(graph_loc, name)
        outf = os.path.join(out_loc, name.replace('flag', 'homology'))
        print(subprocess.run(["/home/gebhart/projects/flagser/flagser --undirected --max-dim 9 --filtration max --out {} {}".format(outf, inf)], shell=True))
