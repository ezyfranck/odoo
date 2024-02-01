import requests
import json
import os

class APIConnect:
    
    scope:str= os.environ.get("API_SCOPE")

######################################################################################    
    def get_error(response):
        
        print("status: ", response.status_code)
        print("texte: ", response.text)
        print("content: ", response.content)
        print("header: ", response.headers)
        print("reason: ", response.reason)
        print("bool: ", response.ok)
        print("histoire: ", response.history)  
        
#######################################################################################    
    def get_new_token(secret, ident) -> str:   
        
        print("Entrée dans get_new_token") 
        token_url:str = "https://auth.ezytail.com/connect/token"
        client_id:str = ident
        client_secret:str = secret
        scope= "ezy_connect"
        
        payload:dict = {            
            "Content-Type": "application/json",
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
            "scope": scope,
            }
        
        print(f"Payload OAuth a envoyé: {payload}")
        try:      
            token_response:dict = requests.post(token_url, data=payload)
            if token_response.status_code == 200:
                print(f"\n+++ SUCCESS ACCESS TOKEN: {token_response.status_code} +++ ", end="") 
                token: str = json.loads(token_response.text).get("access_token")
                return token
            else:
                print("\n--- UNSUCCESS ACCESS TOKEN ---")
                APIConnect.get_error(token_response)
        except requests.exceptions.RequestException as err:
            raise err

#######################################################################################        
    def connect(secret, ident) -> dict:
        # entry point
        # call get_new_token to get access_token
        print("Entrée dans connect !")
        token:str = APIConnect.get_new_token(secret, ident)
        
        if token:
            print("token généré !")
            return token
        else:
            raise ValueError("Problème avec l'access token !")
        
        
