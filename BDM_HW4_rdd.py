from pyspark import SparkContext
import datetime
import csv
import functools
import json
import numpy as np
import sys

def main(sc):
    '''
    Transfer our code from the notebook here, however, remember to replace
    the file paths with the ones provided in the problem description.
    '''
    rddPlaces = sc.textFile('/data/share/bdm/core-places-nyc.csv')
    rddPattern = sc.textFile('/data/share/bdm/weekly-patterns-nyc-2019-2020/*')
    OUTPUT_PREFIX = sys.argv[1]

    CAT_CODES = {'445210', '445110', '722410', '452311', '722513', '445120', '446110', '445299', '722515', '311811',
                 '722511', '445230', '446191', '445291', '445220', '452210', '445292'}
    CAT_GROUP = {'452210': 0, '452311': 0, '445120': 1, '722410': 2, '722511': 3, '722513': 4, '446110': 5, '446191': 5,
                 '722515': 6, '311811': 6, '445210': 7, '445299': 7, '445230': 7, '445291': 7, '445220': 7, '445292': 7,
                 '445110': 8}
    ...
    def filterPOIs(_, lines):
      for line in lines:
        row = line.split(",")
        if row[9] in CAT_CODES:
          value = CAT_GROUP.get(row[9],-1)
          yield (row[0], value)

    rddD = rddPlaces.mapPartitionsWithIndex(filterPOIs) \
            .cache()

    rddD.take(5)

    storeGroup = dict(rddD.collect())
    print(storeGroup['23g-222@627-wc8-7h5'])  # for sanity check, should be 6

    groupCount = rddD \
        .map(lambda x: (x[1], 1)) \
        .groupByKey() \
        .mapValues(len) \
        .map(lambda x: (x[1])) \
        .sortBy(lambda x: x) \
        .collect()
    groupCount

    def extractVisits(storeGroup, _, lines):
        startDate = datetime.datetime(2019, 1, 1)
        delta = datetime.timedelta(days=1)
        for row in csv.reader(lines):
            lineStore = storeGroup.get(row[0], -1)
            try:
                if lineStore >= 0 and int(row[14]) > 0:
                    date = datetime.datetime.strptime(row[12][0:10], '%Y-%m-%d')
                    visits = row[16].split(",")
                    if date >= startDate:
                        yield ((lineStore, date.strftime("%Y-%m-%d")), int(visits[0].replace("[", "")))
                    date = date + delta
                    if date >= startDate:
                        yield ((lineStore, date.strftime("%Y-%m-%d")), int(visits[1]))
                    date = date + delta
                    if date >= startDate:
                        yield ((lineStore, date.strftime("%Y-%m-%d")), int(visits[2]))
                    date = date + delta
                    if date >= startDate:
                        yield ((lineStore, date.strftime("%Y-%m-%d")), int(visits[3]))
                    date = date + delta
                    if date >= startDate:
                        yield ((lineStore, date.strftime("%Y-%m-%d")), int(visits[4]))
                    date = date + delta
                    if date >= startDate:
                        yield ((lineStore, date.strftime("%Y-%m-%d")), int(visits[5]))
                    date = date + delta
                    if date >= startDate:
                        yield ((lineStore, date.strftime("%Y-%m-%d")), int(visits[6].replace("]", "")))
            except ValueError:
                pass

    rddF = rddPattern \
        .mapPartitionsWithIndex(functools.partial(extractVisits, storeGroup))

    rddF.take(5)

    def extractVisits(storeGroup, _, lines):
        startDate = datetime.datetime(2019, 1, 1)
        delta = datetime.timedelta(days=1)
        for row in csv.reader(lines):
            lineStore = storeGroup.get(row[0], -1)
            try:
                if lineStore >= 0 and int(row[14]) > 0:
                    date = datetime.datetime.strptime(row[12][0:10], '%Y-%m-%d')
                    visits = row[16].split(",")
                    if date >= startDate:
                        newdate = abs((date - startDate).days)
                        yield ((lineStore, newdate), int(visits[0].replace("[", "")))
                    date = date + delta
                    if date >= startDate:
                        newdate = abs((date - startDate).days)
                        yield ((lineStore, newdate), int(visits[1]))
                    date = date + delta
                    if date >= startDate:
                        newdate = abs((date - startDate).days)
                        yield ((lineStore, newdate), int(visits[2]))
                    date = date + delta
                    if date >= startDate:
                        newdate = abs((date - startDate).days)
                        yield ((lineStore, newdate), int(visits[3]))
                    date = date + delta
                    if date >= startDate:
                        newdate = abs((date - startDate).days)
                        yield ((lineStore, newdate), int(visits[4]))
                    date = date + delta
                    if date >= startDate:
                        newdate = abs((date - startDate).days)
                        yield ((lineStore, newdate), int(visits[5]))
                    date = date + delta
                    if date >= startDate:
                        newdate = abs((date - startDate).days)
                        yield ((lineStore, newdate), int(visits[6].replace("]", "")))
            except ValueError:
                pass

    rddG = rddPattern \
        .mapPartitionsWithIndex(functools.partial(extractVisits, storeGroup)) \

    rddG.take(5)


    def computeStats(groupCount, _, records):
      startDate = datetime.datetime(2019, 1 ,1)
      for record in records:
        (group, days) = record[0]
        visits = list(record[1])
        median = np.median(visits)
        stdev = np.std(visits)
        date = startDate + datetime.timedelta(days=days)
        stats = (median, max(0, median-stdev+0.5), median+stdev+0.5)
        stats = ','.join(map(lambda x: str(int(x)), stats))
        yield(group, f'{date.year},2020-{date.month:02d}-{date.day:02d},{stats}')

    rddH = rddG.groupByKey() \
            .mapPartitionsWithIndex(functools.partial(computeStats, groupCount))

    rddH.take(5)

    rddJ = rddH.sortBy(lambda x: x[1][:15])
    header = sc.parallelize([(-1, 'year,date,median,low,high')]).coalesce(1)
    rddJ = (header + rddJ).coalesce(10).cache()
    rddJ.take(5)

    OUTPUT_PREFIX = '/content/output'
    filename = 'big_box_grocers'
    rddJ.filter(lambda x: x[0] == 0 or x[0] == -1).values() \
        .saveAsTextFile(f'{OUTPUT_PREFIX}/{filename}')

    filename = 'convenience_stores.csv'
    rddJ.filter(lambda x: x[0] == 1 or x[0] == -1).values() \
        .saveAsTextFile(f'{OUTPUT_PREFIX}/{filename}')

    filename = 'drinking_places.csv'
    rddJ.filter(lambda x: x[0] == 2 or x[0] == -1).values() \
        .saveAsTextFile(f'{OUTPUT_PREFIX}/{filename}')

    filename = 'full_service_restaurants.csv'
    rddJ.filter(lambda x: x[0] == 3 or x[0] == -1).values() \
        .saveAsTextFile(f'{OUTPUT_PREFIX}/{filename}')

    filename = 'limited_service_restaurants.csv'
    rddJ.filter(lambda x: x[0] == 4 or x[0] == -1).values() \
        .saveAsTextFile(f'{OUTPUT_PREFIX}/{filename}')

    filename = 'pharmacies_and_drug_stores.csv'
    rddJ.filter(lambda x: x[0] == 5 or x[0] == -1).values() \
        .saveAsTextFile(f'{OUTPUT_PREFIX}/{filename}')

    filename = 'snack_and_bakeries.csv'
    rddJ.filter(lambda x: x[0] == 6 or x[0] == -1).values() \
        .saveAsTextFile(f'{OUTPUT_PREFIX}/{filename}')

    filename = 'specialty_food_stores.csv'
    rddJ.filter(lambda x: x[0] == 7 or x[0] == -1).values() \
        .saveAsTextFile(f'{OUTPUT_PREFIX}/{filename}')

    filename = 'supermarkets_except_convenience_stores.csv'
    rddJ.filter(lambda x: x[0] == 8 or x[0] == -1).values() \
        .saveAsTextFile(f'{OUTPUT_PREFIX}/{filename}')


if __name__=='__main__':
    sc = SparkContext()
    main(sc)