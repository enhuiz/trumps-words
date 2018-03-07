import requests
import json
import string
from collections import Counter
import datetime
import pandas as pd 

class ProgressIndicator():
    def __init__(self, label, tasks):
        self.label = label
        self.tasks = tasks
        self.cur = 0

    def run_tasks(self):
        try:
            while self.run_next_task():
                continue
        except Exception as e:
            print(e)
            exit()

    def progress(self):
        return str(self.cur) + '/' + str(len(self.tasks))

    def run_next_task(self):
        self.tasks[self.cur]()
        self.cur += 1
        print('{}\t{}'.format(self.label, self.progress()))    
        return self.cur < len(self.tasks)

def download_trumps_twitters(from_year, to_year):
    def download_twitters_in(year):
        url = 'http://www.trumptwitterarchive.com/data/realdonaldtrump/{}.json'.format(year)
        content = requests.get(url).text
        return json.loads(content)

    twitters = []
    years_to_download = range(from_year, to_year + 1)
    tasks = [lambda i=year: twitters.extend(download_twitters_in(i)) for year in years_to_download]
    ProgressIndicator('Progress: ', tasks).run_tasks()
    return twitters

def get_years():
    def get_int_or_default(label, constains, default):
        i = input('Please input ' + label + ': ')
        try: 
            constains(label, i)
        except ValueError as ve:
            print('Your input "{}" is not a number!'.format(i), end=' ')
        except Exception as e:
            print(e, end=' ')
        finally:
            print('Use default {}: {}'.format(label, default))
            return default
        return i

    print('Input from years and to years')
    print('Note: 2009 <= from year <= to year <= 2018')
        
    def year_constrains(label, i):
        i = int(i)
        if i < 2009:
            raise Exception(label + ' is smaller than 2009')
        elif i > 2018:
            raise Exception(label + ' is larger than 2018')

    from_year = get_int_or_default('from year', year_constrains, 2009)

    def to_year_constrains(label, i):
        year_constrains(label, i)
        if i < from_year:
            raise Exception(label + ' is smaller than from year')

    to_year = get_int_or_default('to year', to_year_constrains, 2018)

    return from_year, to_year

def main():
    # get input
    print('---------------------------------')
    from_year, to_year = get_years()

    # download data from http://www.trumptwitterarchive.com
    print('---------------------------------')
    print('Downloading from {} to {} ...'.format(from_year, to_year))
    twitters = download_trumps_twitters(from_year, to_year)

    # extract the twitter content
    twitter_texts = [twitter['text'] for twitter in twitters if 'text' in twitter]

    # output some information
    print('---------------------------------')
    print('Number of downloaded twitters: ')
    print(len(twitter_texts))
    print('---------------------------------')
    print('Example: ')
    print('"{}"'.format(twitter_texts[0]))

    # preprocess twitter content
    lower_joined_text = ' '.join(twitter_texts).lower() # merge multiple twitter texts, change all character to lowercase
    words = [word.strip(string.punctuation) for word in lower_joined_text.split()] # split text into words, remove punctuation

    # calculate the most common words and output them
    most_common_words_df = pd.DataFrame(Counter(words).most_common())
    most_common_words_df.columns = ['WORD', 'FREQUENCY']

    # output the top common words
    print('---------------------------------')
    print('Top 100 words:')
    print(most_common_words_df.head(100))

    # write the words frequency into a txt file
    path = 'data/{}-{}.csv'.format(from_year, to_year)
    
    most_common_words_df.to_csv(path, index=None)
    print('---------------------------------')
    print('Words freqency has been written into:')
    print(path)

if __name__ == '__main__':
    main()