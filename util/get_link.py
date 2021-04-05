import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from util.paths import *
from util.general import store_data

SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly']

TOKENS = ["acc1_token.pickle","acc2_token.pickle","acc3_token.pickle","acc4_token.pickle","acc5_token.pickle","acc6_token.pickle","acc7_token.pickle"]

creds = None

def login(creds):
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                f'{TOKEN}/credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open(f'{TOKEN}/token.pickle', 'wb') as token:
            pickle.dump(creds, token)

def load_cred(name):
    if os.path.exists(f'{TOKEN}/{name}'):
        with open(f'{TOKEN}/{name}', 'rb') as token:
            creds = pickle.load(token)
            return creds
    else:
        print("token not found")

def match_file_name(file_name,data_name):
    if(file_name.find("metadata")!=-1 and data_name=="adni_metadata"):
        return True
    if(file_name.find("part")!=-1 and data_name=="adni_data" and file_name.find("metadata")==-1 ):
        return True
    if(file_name.find("CAN_META")!=-1 and data_name=="cancer_metadata"):
        return True
    if(file_name.find("CAN")!=-1 and data_name=="cancer_data" and file_name.find("_META")==-1):
        return True   
    if(file_name.find("filtered_adni")!=-1 and data_name=="filtered_adni"):
        return True 
    if(file_name.find("filtered_cancer")!=-1 and data_name=="filtered_cancer"):
        return True
    return False


def get_id(creds,name):
    files=[]
    items=[]
    service = build('drive', 'v3', credentials=creds)
    page_token = None
    while True:
        response = service.files().list(fields='nextPageToken, files(id, name)',
        pageToken=page_token).execute()
        items+=response.get('files', [])
        page_token = response.get('nextPageToken', None)
        if page_token is None:
            break
    if items:
        for item in items:
            if(match_file_name(item['name'],name)):
                print(f"NAME: {item['name']}\t ID: {item['id']}")
                files.append(item)
    else:
        print("-")
    return files

def get_file_ids(name):
    print("GETTING FILES \n")
    files=[]
    for token in TOKENS:
        creds=load_cred(token)
        files.extend(get_id(creds,name))
    store_data(files,f"{PICKLE}/file_id.pkl")
    return files
    
if __name__ == '__main__':
    get_file_ids("preprocessed_adni")
