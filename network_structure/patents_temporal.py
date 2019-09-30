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
END_YEAR = 2016
WINDOW = 5
BY = 1
CAT_IDS = list(range(1,8))
LOC = '/home/gebhart/projects/rfunklab/data/temporal'

def run(years, window, location, cat_ids=CAT_IDS):

    cursor = db.cursor()
    cursor.execute("USE patentsview")

    for year in years:
        for cat_id in cat_ids:

            print('Starting year: {}, Category ID: {}'.format(year, cat_id))

            cursor.execute('set @year = {};'.format(year))
            cursor.execute('set @window = {};'.format(window))
            cursor.execute('set @cat_id = {};'.format(cat_id))

            cursor.execute('drop table if exists patentsview.temp_collaboration_vertices;')
            cursor.execute('drop table if exists patentsview.temp_collaboration_edges;')
            cursor.execute('drop table if exists patentsview.temp_knowledge_vertices;')
            cursor.execute('drop table if exists patentsview.temp_knowledge_edges;')
            cursor.execute('drop table if exists patentsview.knowledge_network_helper;')

            # collaboration network -----------------------------------------------------------------

            # # create a temporary table to hold the vertices
            # cursor.execute('drop table if exists patentsview.temp_collaboration_vertices;')
            # cursor.execute('create table patentsview.temp_collaboration_vertices \
            #                 select inventor_id, count(distinct a.patent_id) as patents \
            #                 from patentsview.patent_inventor as a, patentsview.application as b \
            #                 where a.patent_id = b.patent_id \
            #                 and b.UTILITY_FLAG = 1 \
            #                 and year(b.date) <= @year \
            #                 and year(b.date) >= (@year - @window) \
            #                 group by inventor_id;')

            # # create a temporary table to hold the edges
            # cursor.execute('drop table if exists patentsview.temp_collaboration_edges;')
            # cursor.execute('create table patentsview.temp_collaboration_edges \
            #                 select a.inventor_id as inventor_id_a, b.inventor_id as inventor_id_b, count(distinct a.patent_id) as patents \
            #                 from patentsview.patent_inventor as a, \
            #                      patentsview.patent_inventor as b, \
            #                      patentsview.application as c, \
            #                      patentsview.nber as d \
            #                 where a.patent_id = b.patent_id \
            #                 and a.patent_id = c.patent_id \
            #                 and a.patent_id = d.patent_id \
            #                 and a.inventor_id < b.inventor_id \
            #                 and year(c.date) <= @year \
            #                 and year(c.date) >= (@year - @window) \
            #                 and d.category_id = @cat_id \
            #                 and c.UTILITY_FLAG = 1 \
            #                 group by a.inventor_id, b.inventor_id;')
            #
            # cursor.execute('select * from patentsview.temp_collaboration_edges')
            #
            # rows = cursor.fetchall()
            # cols = ['inventor_id_a', 'inventor_id_b', 'patents']
            # cdir = os.path.join(location, 'collaboration', str(cat_id))
            # out_file = os.path.join(cdir, '{}.csv'.format(year))
            # if not os.path.exists(cdir):
            #     os.makedirs(cdir)
            # with open(out_file, 'w') as fp:
            #     mf = csv.writer(fp)
            #     mf.writerow(cols)
            #     for x in rows:
            #         mf.writerow([str(x[0].decode('utf-8')), str(x[1].decode('utf-8')), int(x[2])])


            # knowledge network ---------------------------------------------------------------------

            # # create knowledge network helper table
            # cursor.execute('drop table if exists patentsview.knowledge_network_helper;')
            # cursor.execute('create table patentsview.knowledge_network_helper as \
            #                 select a.subgroup_id as subgroup_id_a, \
            #                        b.subgroup_id as subgroup_id_b, \
            #                        year(c.date) as year, \
            #                        count(distinct a.patent_id) as patent_ids \
            #                 from patentsview.cpc_current as a, \
            #                      patentsview.cpc_current as b, \
            #                      patentsview.application as c \
            #                 where a.patent_id = b.patent_id \
            #                 and a.patent_id = c.patent_id \
            #                 and a.subgroup_id < b.subgroup_id \
            #                 and year(c.date) <= @year \
            #                 and year(c.date) >= (@year - @window) \
            #                 and c.UTILITY_FLAG = 1 \
            #                 group by a.subgroup_id, b.subgroup_id, year;')

            cursor.execute('select a.subgroup_id as subgroup_id_a, \
                                   b.subgroup_id as subgroup_id_b, \
                                   year(c.date) as year, \
                                   count(distinct a.patent_id) as patents \
                            from patentsview.cpc_current as a, \
                                 patentsview.cpc_current as b, \
                                 patentsview.application as c, \
                                 patentsview.nber as d \
                            where a.patent_id = b.patent_id \
                            and a.patent_id = c.patent_id \
                            and a.patent_id = d.patent_id \
                            and a.subgroup_id < b.subgroup_id \
                            and year(c.date) <= @year \
                            and year(c.date) >= (@year - @window) \
                            and d.category_id = @cat_id \
                            and c.UTILITY_FLAG = 1 \
                            group by a.subgroup_id, b.subgroup_id, year;')

            # create a temporary table to hold the vertices
            # cursor.execute('drop table if exists patentsview.temp_knowledge_vertices;')
            # cursor.execute('create table patentsview.temp_knowledge_vertices \
            #                 select subgroup_id, count(distinct a.patent_id) as patents \
            #                 from patentsview.cpc_current as a, patentsview.application as b \
            #                 where a.patent_id = b.patent_id \
            #                 and b.UTILITY_FLAG = 1 \
            #                 and year(b.date) <= @year \
            #                 and year(b.date) >= (@year - @window) \
            #                 group by subgroup_id;')

            # create a temporary table to hold the edges
            # cursor.execute('drop table if exists patentsview.temp_knowledge_edges;')
            # cursor.execute('create table patentsview.temp_knowledge_edges \
            #                 select distinct subgroup_id_a, subgroup_id_b, patent_ids as patents \
            #                 from patentsview.knowledge_network_helper \
            #                 where year <= @year \
            #                 and year >= (@year - @window);')

            # cursor.execute('select distinct subgroup_id_a, subgroup_id_b, patent_ids as patents \
            #                 from patentsview.knowledge_network_helper \
            #                 where year <= @year \
            #                 and year >= (@year - @window);')
            rows = cursor.fetchall()
            cols = ['subgroup_id_a', 'subgroup_id_b', 'patents']
            kdir = os.path.join(location, 'knowledge', str(cat_id))
            out_file = os.path.join(kdir, '{}.csv'.format(year))
            if not os.path.exists(kdir):
                os.makedirs(kdir)
            with open(out_file, 'w') as fp:
                mf = csv.writer(fp)
                mf.writerow(cols)
                for x in rows:
                    mf.writerow([str(x[0].decode('utf-8')),str(x[1].decode('utf-8')),int(x[3])])

            # drop the temporary tables
            # cursor.execute('drop table if exists patentsview.temp_collaboration_vertices;')
            # cursor.execute('drop table if exists patentsview.temp_collaboration_edges;')
            # cursor.execute('drop table if exists patentsview.temp_knowledge_vertices;')
            # cursor.execute('drop table if exists patentsview.temp_knowledge_edges;')
            cursor.execute('drop table if exists patentsview.knowledge_network_helper;')




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
