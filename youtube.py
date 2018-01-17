import os
import google.oauth2.credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow
import csv
import json
import pandas as pd


CLIENT_SECRETS_FILE = "client_secret.json"

SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'

def get_authenticated_service():
  flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
  credentials = flow.run_console()
  return build(API_SERVICE_NAME, API_VERSION, credentials = credentials)

#create a csv of videos from search_text
def list_to_csv(response,search_text):
  cwd = os.getcwd()
  file_path=os.path.join(cwd,'videosBySearchDB',search_text.replace(" ","")+'.csv')
  json_parsed=response
  video_list=json_parsed['items']
  #open file
  search_file=open(file_path,'w+')
  #csv writer initilalization
  csvwriter=csv.writer(search_file)

  header=False
  for item in video_list:
    
    if not header:
      csvwriter.writerow(['id','title','description','thumbnail','channelTitle','channelId'])
      header=True
    
    if 'videoId' in item['id']:

      csvwriter.writerow([item['id']['videoId'],
        item['snippet']['title'],
        item['snippet']['description'],
        item['snippet']['thumbnails']['default']['url'],
        item['snippet']['channelTitle'],
        item['snippet']['channelId']])

  search_file.close()
  print('Successfully updated for '+search_text)
  return file_path


#Retrieve list for search by keyword
def search_list_by_keyword(client, **kwargs):
  search_text=kwargs['q']
  response = client.search().list(
    **kwargs
  ).execute()
  print("Json Retrieved")
  file_path=list_to_csv(response,search_text)
  video_statistics_info(file_path)

#Get more infor about each video using ID and combine in csv
def video_statistics_info(path):
  videoDF=pd.read_csv(path)
  videoID=videoDF['id']
  infoDF=pd.DataFrame(columns=['id','viewCount','likeCount','dislikeCount','commentCount'])
  for id in videoID:
    response=videos_list_by_id(service,
      part='statistics',
      id=id)
    for item in response['items']:
      if checkJson(item):
        infoDF.loc[len(infoDF)]=[item['id'],
        item['statistics']['viewCount'],
        item['statistics']['likeCount'],
        item['statistics']['dislikeCount'],
        item['statistics']['commentCount']]
  videoFinal=videoDF.merge(infoDF,on='id',how='inner')
  videoFinal.to_csv(path)

def checkJson(item):
  list=['viewCount','likeCount','dislikeCount','commentCount']
  counter=True
  for feature in list:
    if feature not in item['statistics']:
      counter=False

  return counter


def videos_list_by_id(client, **kwargs):
  response = client.videos().list(
    **kwargs
  ).execute()
  return response



if __name__ == '__main__':
  service = get_authenticated_service()

  searchDF=pd.read_csv('title.csv',index_col=False)
  for index,row in searchDF.iterrows():
    search_list_by_keyword(service,
      part='snippet',
      maxResults=50,
      q=row[0],
      type='')
    