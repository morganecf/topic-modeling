import re
import numpy as np
import pandas as pd
from datetime import datetime
from sklearn.feature_extraction.text import CountVectorizer

# january 1st, 1601 - first year of Gregorian cycle
base_time = 11644473600000000
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


def to_timestamp(t):
  return pd.Timestamp(datetime.fromtimestamp((t - base_time) / 1000000))


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
  df = pd.read_csv('data/urls.csv')

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
  urls = pd.DataFrame(pd.read_csv('data/urls.csv'), columns=['id', 'url'])
  urls.set_index('id')

  # read in visits
  visits = pd.DataFrame(pd.read_csv('data/visits.csv'), columns=['url', 'visit_duration'])

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
Print time series and seasonality stats
'''
def get_event_data(event_domains):
  # read in urls
  urls = pd.DataFrame(pd.read_csv('data/urls.csv'), columns=['id', 'url'])
  urls.set_index('id')

  # convert urls to domains
  urls['domain'] = urls['url'].map(to_domain)

  # read in visits
  visits = pd.DataFrame(pd.read_csv('data/visits.csv'), columns=['url', 'visit_time'])

  # merge urls with visits, since visits only contain url id
  merged = pd.merge(visits, urls, left_on='url', right_index=True, how='left')

  # only keep event visits
  event_df = merged[merged.domain.isin(event_domains)]

  # create series out of these events
  event_times = event_df.visit_time.map(to_timestamp)
  events = pd.Series(np.ones(event_times.count()), event_times)

  # weekdays this event happened
  workdays = filter(is_weekday, events.index)

  # weekend days this event happened
  weekends = filter(lambda e: not is_weekday(e), events.index)

  print 'Number of workdays:', len(workdays), '\t', len(workdays) / float(len(weekends) + len(workdays))
  print 'Number of weekends:', len(weekends), '\t', len(weekends) / float(len(weekends) + len(workdays))
  print

  ### series

  # group by month
  month_ts = events.groupby([lambda t: t.year, lambda t: t.month]).sum()
  print 'Distribution since May (monthly level):'
  print month_ts
  print

  # group by day
  day_ts = events.groupby([lambda t: t.year, lambda t: t.month, lambda t: t.day]).sum()
  print 'Distribution since May (daily level):'
  print day_ts
  print

  # group by hour of day
  hour_ts = events.groupby([lambda t: t.year, lambda t: t.month, lambda t: t.day, lambda t: t.hour]).sum()
  print 'Distribution since May (hourly level):'
  print hour_ts
  print

  ### seasonality distribution

  # weekday
  by_weekday = events.groupby([lambda t: t.weekday()]).sum()
  print 'Counts by day of week:'
  print by_weekday
  print

  # hour of day
  by_hour = events.groupby([lambda t: t.hour]).sum()
  print 'Counts by hour of day:'
  print by_hour
  print

  # hour of workday
  by_workday_hour = events.drop(weekends).groupby([lambda t: t.hour]).sum()
  print 'Counts by hour of workday:'
  print by_workday_hour
  print

  # hour of weekend
  by_weekend_hour = events.drop(workdays).groupby([lambda t: t.hour]).sum()
  print 'Counts by hour of weekend:'
  print by_weekend_hour
  print


'''
When do I watch netflix?
'''
def netflix():
  get_event_data(['netflix.com'])


'''
When do I message? (Slack, messenger, facebook)
'''
def messages():
  get_event_data(['messenger.com', 'facebook.com', 'cultofmelancholy.slack.com', 'l.facebook.com'])


'''
When do I check email?
'''
def emails():
  get_event_data(['mail.google.com', 'gmail.com', 'photos.google.com', 'accounts.google.com'])


'''
When do I work? (code/datarobot stuff)
'''
def work():
  work_events = [
    'docs.google.com',
    'localhost:8000',
    'github.com',
    'datarobot.atlassian.net',
    'jenkins.hq.datarobot.com:8080',
    'staging.datarobot.com',
    'stackoverflow.com',
    'hangouts.google.com',
    'calendar.google.com',
    'app.datarobot.com',
    'projects.invisionapp.com',
    'lodash.com',
    'app.greenhouse.io',
    'docs.angularjs.org',
    'atlassian.com',
    'raw.githubusercontent.com'
    ]
  get_event_data(work_events)


'''
When do I consume news/entertainment?
'''


messages()

# good pandas tutorial: https://github.com/brandon-rhodes/pycon-pandas-tutorial
# create CLVs: https://github.com/bitly/data_hacks