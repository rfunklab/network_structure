import os
from ast import literal_eval as make_tuple

def read_txt(data_loc):
    with open(data_loc, "r") as f:
        return f.read()

def parse_interval_text(txt):
    intervals = []
    pi_txt = '# persistence intervals in dimension {}'
    end_txt = 'The remaining homology groups are trivial.'
    end_txt2 = '# Betti numbers:'
    i = 0
    while i >= 0:
        ifmt = pi_txt.format(i)
        i1fmt = pi_txt.format(i+1)
        idxi = txt.find(ifmt)
        idxi1 = txt.find(i1fmt)
        if idxi > -1 and idxi1 > -1:
            # internal interval
            intervals.append(txt[idxi+len(ifmt):idxi1].strip().replace(' ', '').split('\n'))
            i += 1
        elif idxi > -1 and idxi1 == -1:
            # last interval
            endidx = txt.find(end_txt)
            if endidx == -1:
                endidx = txt.find(end_txt2)
                if endidx == -1:
                    raise IndexError('Cannot find final interval break `{}`'.format(end_txt))
                else:
                    intervals.append(txt[idxi+len(ifmt):endidx].strip().replace(' ', '').split('\n'))
            else:
                intervals.append(txt[idxi+len(ifmt):endidx].strip().replace(' ', '').split('\n'))
            i = -1
        else:
            raise IndexError('Cannot find interval {}'.format(i))
            i = -1
    return intervals

def parse_betti_text(txt, barcode=True):
    bettis = []
    if barcode:
        st_txt = '# Betti numbers:'
        end_txt = '# Cell counts:'
        lines = txt[txt.find(st_txt)+len(st_txt):txt.find(end_txt)].replace('#\t\t', '').split('\n')
        lines = [int(line[line.find('=')+1:]) for line in lines if line != '']
        return lines
    else:
        st_txt = '# Betti numbers '
        stidx = txt.find(st_txt)+len(st_txt)
        stidx2 = txt.find(':\n', stidx)+2
        line = [int(b) for b in txt[stidx2:].split()]
        return line

def parse_cell_count_text(txt, barcode=True):
    if barcode:
        cells = []
        st_txt = '# Cell counts:'
        lines = txt[txt.find(st_txt)+len(st_txt):].replace('#\t\t', '').split('\n')
        lines = [int(line[line.find('=')+1:]) for line in lines if line != '']
        return lines
    else:
        st_txt = '# Cell counts: '
        end_txt = '# Euler characteristic:'
        stidx = txt.find(st_txt)+len(st_txt)
        stidx2 = txt.find(':\n', stidx)+2
        end_idx = txt.find(end_txt)
        line = [int(c) for c in txt[stidx2:end_idx].split()]
        return line

def parse_euler_characteristic_text(txt, barcode=True):
    if barcode:
        st_txt = '# Euler characteristic: '
        stidx = txt.find(st_txt)+len(st_txt)
        line = txt[stidx:txt.find('\n', stidx)]
        return int(line)
    else:
        st_txt = '# Euler characteristic:\n'
        end_txt = '# Betti numbers'
        stidx = txt.find(st_txt)+len(st_txt)
        line = txt[stidx:txt.find(end_txt)].replace('\n','')
        if line != '':
            return int(line)
        return 0

def tuplefy(interval):
    return make_tuple(interval.replace('[','('))

def parse_intervals(data_loc):
    str_intervals = parse_interval_text(read_txt(data_loc))
    return [[tuplefy(interval) if interval != '' else () for interval in intervals] for intervals in str_intervals]

def parse_betti(data_loc, barcode=True):
    return parse_betti_text(read_txt(data_loc), barcode=barcode)

def parse_cell_counts(data_loc, barcode=True):
    return parse_cell_count_text(read_txt(data_loc), barcode=barcode)

def parse_euler_characteristic(data_loc, barcode=True):
    return parse_euler_characteristic_text(read_txt(data_loc), barcode=barcode)
