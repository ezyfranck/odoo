import requests
from . import api_connect as APC
import json


class DataMapper:

############################################################################################
    def post_data_API(url, headers, data): 
        print("Entrée dans post_data_api")
            
        try:
            response = requests.request("POST", url, headers=headers, data=data)
           
            if response.status_code == 200:
                print(f"\n+++ SUCCESS POST REQUEST +++ {response.status_code}")
                return response.text   #recup errors
            else:
                print("Problème requête !")
                APC.APIConnect.get_error(response)    
                
        except requests.exceptions.RequestException as err:
            raise err

###############################################################################################        
    def get_data_API(url, headers, data):
        print("Entrée dans get_data_api")
                   
        try:
            response = requests.request("GET", url, headers=headers, data=data)
            if response.status_code == 200:
                 response = json.loads(response.text)
                 return response.text
            else:
                APC.APIConnect.get_error(response) 
                 
        except requests.exceptions.RequestException as err:
            raise err
        
###############################################################################################
    def map_product_data(flux, token, data):
        print("Entrée dans le MAPPER")
        headers:dict = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}',
        }
        
        if flux == 'REFART':
            url = "https://api-ezyconnect.ezytail.com/articles" 
            response_txt= DataMapper.post_data_API(url, headers, data)
        elif flux == 'ANAPRO':
            url = ''
            response_txt= DataMapper.post_data_API(url, headers, data)
        elif flux == 'CMDCLI':
            url = ''
            response_txt= DataMapper.post_data_API(url, headers, data)
        elif flux == 'CRAPRO':
            url = ''
            response_txt= DataMapper.get_data_API(url, headers, data)
        elif flux == 'CRPCMD':
            url = ''
            response_txt= DataMapper.get_data_API(url, headers, data)
        elif flux == 'STKETA':
            url = ''
            response_txt= DataMapper.get_data_API(url, headers, data)
        elif flux == 'STKMVT':
            url = ''
            response_txt= DataMapper.get_data_API(url, headers, data)
                
        response_data= json.loads(response_txt)
        print(response_data)         
                
        # map dapa received from API ezyconnect to odoo
        # send data to odoo
        # store datas



            

                