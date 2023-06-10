import os
import requests
import json
from pprint import pprint
from getpass import getpass
from fake_useragent import UserAgent

from common import CardProvider, CreditCard

class CalOnline(CardProvider):
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

    def login(self, username, password, cardsixdigits=None):
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

    def get_credit_cards(self):
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

        cards = []
        for card in json_data.get("result", {}).get("cards", []):
            cards.append(
                    CreditCard(card_id=card["cardUniqueId"], last4digits=card["last4Digits"], innerdata=card)
            )

        return cards
    
        return json_data.get("result", {}).get("cards", [])
        
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

        #total_amount = json_result["result"]["bankAccounts"][0]["debitDates"][0]["totalDebits"]

        assert(len(json_result["result"]["bankAccounts"]) == 1)
        assert(len(json_result["result"]["bankAccounts"][0]["debitDates"]) == 1)

        return json_result["result"]["bankAccounts"][0]["debitDates"][0]["transactions"]
        #for transaction in json_result["result"]["bankAccounts"][0]["debitDates"][0]["transactions"]:
            #pprint(transaction)
        
    
def main():
    co = CalOnline()
    username = getpass("Enter your username: ")
    password = getpass("Enter your password: ")
    co.cal_login(username, password)
    ccs = co.get_credit_cards()
    for cc in ccs:
        co.get_card_transactions(cc["cardUniqueId"], 5, 2023)
    
if __name__ == "__main__":
    main()
