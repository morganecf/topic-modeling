import re
import numpy as np
import pandas as pd
from datetime import datetime
from sklearn.feature_extraction.text import CountVectorizer


url_regex = re.compile(r'(http|https):\/\/(www\.)?([a-zA-Z0-9.:_-]+)\/')

def to_domain(url):
  if type(url) == str:
    match = re.match(url_regex, url)
    if match:
      return match.group(3)
    return 'local filesystem'
  return None


def is_weekday(ts):
  wd = ts.weekday()
  return wd >= 0 and wd < 5


'''
What are the most common n-grams for search terms?
'''
def get_search_ngrams():
  df = pd.read_csv('keyword_search_terms.csv')

  # to convert text to token counts
  word_vectorizer = CountVectorizer(ngram_range=(1, 5), analyzer='word')  # stop_words='english'

  # create the term x document matrix
  sparse_matrix = word_vectorizer.fit_transform(df['lower_term'])

  # for each term sum all document appearances
  frequencies = sum(sparse_matrix).toarray()[0]

  # store in dataframe (word : frequency)
  counts = pd.Series(frequencies, index=word_vectorizer.get_feature_names())

  # sort by frequency
  sorted_counts = counts.sort_values(ascending=False)

  # save
  sorted_counts.to_csv('analysis/frequent_search_ngrams.csv', encoding='utf-8')


'''
Which domains do I visit the most?
'''
def get_domains():
  df = pd.read_csv('urls.csv')

  # add column of domains
  df['domain'] = df['url'].map(to_domain)

  # group by domain
  grouped = df.groupby('domain')

  # size of each group (# of urls per subdomain)
  sizes = grouped.size()

  # counts and means for each group
  counts = grouped.aggregate({'visit_count': [np.sum, np.mean]})

  # save sizes
  sizes.sort_values(ascending=False).to_csv('analysis/domain_group_sizes.csv', encoding='utf-8')

  # save counts and means (sorted by count)
  counts.sort_values([('visit_count', 'sum')], ascending=False).to_csv('analysis/domain_counts.csv', encoding='utf-8')


'''
Which domains do I spend the most time on?
'''
def get_time_spent():
  # read in urls
  urls = pd.DataFrame(pd.read_csv('urls.csv'), columns=['id', 'url'])
  urls.set_index('id')

  # read in visits
  visits = pd.DataFrame(pd.read_csv('visits.csv'), columns=['url', 'visit_duration'])

  # add columns for hours and minutes and days
  visits['visit_duration_min'] = visits['visit_duration'].map(lambda t: t / 6e+7)
  visits['visit_duration_hr'] = visits['visit_duration'].map(lambda t: t / (6e+7 * 60))
  visits['visit_duration_day'] = visits['visit_duration'].map(lambda t: t / (6e+7 * 60 * 24))

  # merge urls with visits, since visits only contain url id
  merged = pd.merge(visits, urls, left_on='url', right_index=True, how='left')

  merged['domain'] = merged['url_y'].map(to_domain)

  # group by domain
  grouped = merged.groupby('domain')

  # aggregate total and average time spent on each domain
  time_spent = grouped.aggregate({'visit_duration': [np.sum, np.mean],
                                  'visit_duration_min': [np.sum, np.mean],
                                  'visit_duration_hr': [np.sum, np.mean],
                                  'visit_duration_day': [np.sum, np.mean]})

  # save
  time_spent.sort_values([('visit_duration_min', 'sum')], ascending=False).to_csv('analysis/domain_time_spent.csv', encoding='utf-8')


'''
Create time series count data. This isn't concerned with
content, just whether or not a website was visited.
'''
def time_series():
  # january 1st, 1601 - first year of Gregorian cycle
  base_time = 11644473600000000

  # read in visits
  visits = pd.read_csv('visits.csv')

  # convert to pd-digestible timestamps
  dates = visits['visit_time'].map(lambda t: pd.Timestamp(datetime.fromtimestamp((t - base_time) / 1000000)))

  # create series
  ts = pd.Series(np.ones(dates.count()), dates)

  # workdays
  workdays = filter(is_weekday, ts.index)

  # weekends
  weekends = filter(lambda t: not is_weekday(t), ts.index)

  ### series

  # group by month
  month_ts = ts.groupby([lambda t: t.year, lambda t: t.month]).sum()

  # group by day
  day_ts = ts.groupby([lambda t: t.year, lambda t: t.month]).sum()

  # group by hour of day
  hour_ts = ts.groupby([lambda t: t.year, lambda t: t.month, lambda t: t.hour]).sum()

  ### not series, aggregations

  # weekday
  by_weekday = ts.groupby([lambda t: t.weekday()]).sum()

  # hour of day
  by_hour = ts.groupby([lambda t: t.hour]).sum()

  # hour of workday
  by_workday_hour = ts.drop(weekends).groupby([lambda t: t.hour]).sum()

  # hour of weekend
  by_weekend_hour = ts.drop(workdays).groupby([lambda t: t.hour]).sum()


'''
When do I watch netflix?
'''
def netflix():
  pass


'''
When do I message?
'''
def messages():
  pass


'''
When do I email?
'''
def emails():
  pass


get_time_spent()

# good pandas tutorial: https://github.com/brandon-rhodes/pycon-pandas-tutorial
# create CLVs: https://github.com/bitly/data_hacks