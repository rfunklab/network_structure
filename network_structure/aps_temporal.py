import os
import mysql.connector
import db_config
import argparse
import csv
import pandas as pd

db = mysql.connector.connect(
    host="rfunksql.csom.umn.edu",
    user=db_config.DB_CONFIG['user'],
    passwd=db_config.DB_CONFIG['passwd'])

START_YEAR = 1990
END_YEAR = 2018
WINDOW = 5
BY = 1
LOC = '/home/gebhart/projects/rfunklab/data/temporal/aps'

def run(years, window, location):

    cursor = db.cursor()
    cursor.execute("USE aps")

    # # -- create a temporary helper table
    # cursor.execute('drop table if exists aps.aps_pacs_helper;')
    # cursor.execute('create table aps.aps_pacs_helper as \
    # select doi, pacs1 as pacs from aps.pacs_raw where pacs1 is not null \
    # union distinct \
    # select doi, pacs2 as pacs from aps.pacs_raw where pacs2 is not null \
    # union distinct \
    # select doi, pacs3 as pacs from aps.pacs_raw where pacs3 is not null \
    # union distinct \
    # select doi, pacs4 as pacs from aps.pacs_raw where pacs4 is not null \
    # union distinct \
    # select doi, pacs5 as pacs from aps.pacs_raw where pacs5 is not null;')
    #
    #
    #
    # # -- add indexes
    # cursor.execute('alter table aps.aps_pacs_helper add index doi_idx (doi), add index pacs_idx (pacs);')
    #
    # # -- create helper table
    # cursor.execute('drop table if exists aps.aps_knowledge_network_helper;')
    # cursor.execute('create table aps.aps_knowledge_network_helper as \
    # select a.pacs as pacs_a, \
    #        b.pacs as pacs_b, \
    #        year(c.date) as year, \
    #        count(distinct a.doi) as dois \
    # from aps.aps_pacs_helper as a, \
    #      aps.aps_pacs_helper as b, \
    #      aps.records_raw as c \
    # where a.doi = b.doi \
    # and a.doi = c.doi \
    # and a.pacs < b.pacs \
    # group by a.pacs, b.pacs, year;')
    #
    # # -- add indexes
    # cursor.execute('alter table aps.aps_knowledge_network_helper add index pacs_a_idx (pacs_a), \
    #                 add index pacs_b_idx (pacs_b), \
    #                 add index year_idx (year);')

    for year in years:

        print('Starting year: {}'.format(year))

        cursor.execute('set @year = {};'.format(year))
        cursor.execute('set @window = {};'.format(window))

        # query edges
        cursor.execute('select a.disambiguated_id as author_id_a, b.disambiguated_id as author_id_b, count(distinct a.record_id) as papers \
                        from aps.disambiguated_epj as a, \
                             aps.disambiguated_epj as b, \
                             aps.records_raw as c \
                        where a.record_id = b.record_id \
                        and a.record_id = c.record_id \
                        and a.disambiguated_id IS NOT NULL \
                        and b.disambiguated_id IS NOT NULL \
                        and a.disambiguated_id < b.disambiguated_id \
                        and year(c.date) <= @year \
                        and year(c.date) >= (@year - @window) \
                        group by a.disambiguated_id, b.disambiguated_id;')

        rows = cursor.fetchall()
        cols = ['author_id_a', 'author_id_b', 'papers']
        cdir = os.path.join(location, 'collaboration')
        out_file = os.path.join(cdir, '{}.csv'.format(year))
        if not os.path.exists(cdir):
            os.makedirs(cdir)
        with open(out_file, 'w') as fp:
            mf = csv.writer(fp)
            mf.writerow(cols)
            for x in rows:
                mf.writerow([int(x[0]), int(x[1]), int(x[2])])

        # # -- knowledge network ---------------------------------------------------------------------
        #
        # cursor.execute('select distinct pacs_a, pacs_b, dois \
        # from aps.aps_knowledge_network_helper \
        # where year <= @year \
        # and year >= (@year - @window);')
        #
        # rows = cursor.fetchall()
        # cols = ['pacs_a', 'pacs_b', 'dois']
        # kdir = os.path.join(location, 'knowledge')
        # out_file = os.path.join(kdir, '{}.csv'.format(year))
        # if not os.path.exists(kdir):
        #     os.makedirs(kdir)
        # with open(out_file, 'w') as fp:
        #     mf = csv.writer(fp)
        #     mf.writerow(cols)
        #     for x in rows:
        #         mf.writerow([str(x[0].decode('utf-8')),str(x[1].decode('utf-8')),int(x[2])])
        #




if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='temporal collaboration and knowledge graph creation')
    parser.add_argument('-sy', '--start-year', type=int, required=False,
                        help='year start', default=START_YEAR)
    parser.add_argument('-ey', '--end-year', type=int, required=False,
                        help='year end', default=END_YEAR)
    parser.add_argument('-w', '--window', type=int, required=False,
                        help='lookback window', default=WINDOW)
    parser.add_argument('-b', '--by', type=int, required=False,
                        help='take every _ years', default=BY)
    parser.add_argument('-o', '--output-location', type=str, required=True,
                        help='location to store csvs')
    args = parser.parse_args()

    years = list(range(args.start_year, args.end_year+1, args.by))
    run(years, args.window, args.output_location)
