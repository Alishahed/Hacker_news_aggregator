import requests as req
import simplejson as json
import pandas as pd
from bs4 import BeautifulSoup


def api_call(source = 'hn',query = "autonomous vehicle",no_page = 5):
    pages = range(no_page)
    df_hn = pd.DataFrame(index = range(max(pages)*20),columns=['date','URL','title','text'])
    #query = "autonomous vehicle"
    news_index = 0
    if source == 'hn':
        for search_page in pages:
            r = req.get('http://hn.algolia.com/api/v1/search_by_date?query='+query+'&page='+str(search_page))
            r = r.json()
            for stories in r['hits']:
                df_hn['URL'][news_index] = stories['story_url']
                df_hn['title'][news_index] = stories['story_title']
                df_hn['date'][news_index] = stories['created_at']
                news_index += 1
    return df_hn

def scrapper(df_in):
    for df_index in range(len(df_in)):
        if df_index%10 == 0:
            print 'scapping '+str(df_index)+' out of '+str(len(df_in))
        text = ''
        if df_in['URL'][df_index] != None:
            page = req.get(df_in['URL'][df_index])
            soup = BeautifulSoup(page.content, 'html.parser')
            text_list = soup.find_all('p')
            content = ''
            for content_sent in range(len(text_list)):
                content = content + text_list[content_sent].get_text() + '\n'
            df_in['text'][df_index] = content
        else:
            df_in['URL'][df_index] = 'NaN'
    return df_in

#Main file to search HackerNews and scrap pages based on their links
df_hn_out = api_call(no_page = 6)
df_hn_scrap = scrapper(df_hn_out)
df_hn_scrap = df_hn_scrap.dropna(axis=0)
df_hn_scrap = df_hn_scrap.drop_duplicates(subset = 'title',keep = 'first',inplace = False)
df_hn_scrap = df_hn_scrap.reset_index(drop = True)

today_date = pd.to_datetime('today')
today_str = str(today_date.month)+'_'+str(today_date.day)+'_'+str(today_date.year)

writer = pd.ExcelWriter('/Users/alishahed/OneDrive/HN_weekly_bahar/HN_news_AC_'+today_str+'.xlsx')
df_hn_scrap.to_excel(writer,'Sheet1')
writer.save()
