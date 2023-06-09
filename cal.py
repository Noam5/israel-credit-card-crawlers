import os
import requests
import json
from pprint import pprint
from getpass import getpass
from fake_useragent import UserAgent

class CalOnline:
    BASE_URL = 'https://api.cal-online.co.il'
    SITE_ID = '09031987-273E-2311-906C-8AF85B17C8D9'
    
    def __init__(self):
        self.session = requests.Session()
        ua = UserAgent()
        self.user_agent = ua.random

    def get_headers(self, additional_headers=None):
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9,he;q=0.8',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json',
            'User-Agent': self.user_agent,
        }
        if additional_headers:
            headers.update(additional_headers)
        return headers

    def cal_login(self, username, password):
        headers = self.get_headers({
            'Origin': f'{self.BASE_URL}',
            'Referer': f'{self.BASE_URL}/',
            'X-Site-Id': self.SITE_ID,
        })
        json_data = {'username': username, 'password': password, 'recaptcha': '',}

        response = self.session.post(
            f'{self.BASE_URL}/col-rest/calconnect/authentication/login',
            headers=headers,
            json=json_data,
        )

        response.raise_for_status()
        self.login_token = response.json().get("token")

    def get_user_details(self):
        headers = self.get_headers({
            'Authorization': f'CALAuthScheme {self.login_token}',
            'Origin': f'{self.BASE_URL}',
            'Referer': f'{self.BASE_URL}/',
            'X-Site-Id': self.SITE_ID,
        })

        json_data = {'tokenGuid': '',}

        response = self.session.post(
            f'{self.BASE_URL}/Authentication/api/account/init',
            headers=headers,
            json=json_data,
        )

        response.raise_for_status()
        json_data = response.json()

        for card_details in json_data.get("result", {}).get("cards", []):
            self.get_card_transactions(card_details["cardUniqueId"], 5, 2023)
        
    def get_card_transactions(self, card_id, month, year):
        headers = self.get_headers({
            'Authorization': f'CALAuthScheme {self.login_token}',
            'Origin': f'{self.BASE_URL}',
            'Referer': f'{self.BASE_URL}/',
            'X-Site-Id': self.SITE_ID,
        })

        json_data = {
            'cardUniqueId': card_id,
            'month': str(month),
            'year': str(year),
        }

        response = self.session.post(
            f'{self.BASE_URL}/Transactions/api/transactionsDetails/getCardTransactionsDetails',
            headers=headers,
            json=json_data,
        )

        json_result = response.json()
        assert(json_result["statusDescription"] == "הצלחה")

        total_amount = json_result["result"]["bankAccounts"][0]["debitDates"][0]["totalDebits"]
        for transaction in json_result["result"]["bankAccounts"][0]["debitDates"][0]["transactions"]:
            pprint(transaction)
        
    
def main():
    co = CalOnline()
    username = getpass("Enter your username: ")
    password = getpass("Enter your password: ")
    co.cal_login(username, password)
    co.get_user_details()
    
if __name__ == "__main__":
    main()
