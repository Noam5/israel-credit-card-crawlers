import os
import requests
from getpass import getpass
from fake_useragent import UserAgent
import re
from datetime import datetime
from dateutil.relativedelta import relativedelta
import json

from common import CardProvider, CreditCard

class AmericanExpress(CardProvider):

    def __init__(self):
        self.session = requests.Session()
        ua = UserAgent()
        self.user_agent = ua.random
        self.user_guid = None

    def send_request(self, url, method='get', params=None, headers=None, json=None, data=None):

        response = self.session.request(
            method,
            url,
            params=params,
            headers=headers,
            json=json,
            data=data,,
        )

        if response.status_code != 200:
            raise Exception(f"Request failed with status {response.status_code}")

        return response


    def login(self, username, password, cardsixdigits):

        response = self.send_request('https://he.americanexpress.co.il/', 'get')
        pattern = r'name="__RequestVerificationToken" type="hidden" value="(.*?)"'
        match = re.search(pattern, response.text)
        if match:
            self.request_verification_token = match.group(1)
        else:
            raise Exception("Could not find __RequestVerificationToken")

        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9,he;q=0.8',
            'Connection': 'keep-alive',
            'Origin': 'https://he.americanexpress.co.il',
            'Referer': 'https://he.americanexpress.co.il/personalarea/login/',
            'User-Agent': self.user_agent,
            '__RequestVerificationToken': self.request_verification_token,
            'Content-Type': 'application/json; charset=UTF-8',
        }
        params = {
            'reqName': 'ValidateIdDataNoReg',
        }
        json_data = {
            'id': username,
            'idType': '1',
            'cardSuffix': cardsixdigits,
            'sisma': password,
            'checkLevel': '1',
            'companyCode': '77',
            'countryCode': '212',
            'isGoogleCaptcha': True,
        }
        response = self.send_request('https://he.americanexpress.co.il/services/ProxyRequestHandler.ashx', 'post', params=params, headers=headers, json=json_data)

        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9,he;q=0.8',
            'Connection': 'keep-alive',
            'Origin': 'https://he.americanexpress.co.il',
            'Referer': 'https://he.americanexpress.co.il/personalarea/login/',
            'User-Agent': self.user_agent,
            '__RequestVerificationToken': self.request_verification_token,
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        }
        params = {
            'reqName': 'IsRegisterNoReg',
        }
        json_data = {
            "id": username, 
            "idType":"1"
        }
        response = self.send_request('https://he.americanexpress.co.il/services/ProxyRequestHandler.ashx','post',params=params,headers=headers,json=json_data)

        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9,he;q=0.8',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': 'https://he.americanexpress.co.il',
            'Referer': 'https://he.americanexpress.co.il/personalarea/dashboard/',
            'User-Agent': self.user_agent,
        }
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9,he;q=0.8',
            'Connection': 'keep-alive',
            'Origin': 'https://he.americanexpress.co.il',
            'Referer': 'https://he.americanexpress.co.il/personalarea/login/',
            'User-Agent': self.user_agent,
            '__RequestVerificationToken': self.request_verification_token,
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        }
        params = {
            'reqName': 'performLogonA',
        }
        json_data = {
            'MisparZihuy': username,
            'countryCode': '212',
            'idType': '1',
            'Sisma': password,
            'cardSuffix': cardsixdigits,
            'isGoogleCaptcha': True,
        }
        response = self.send_request('https://he.americanexpress.co.il/services/ProxyRequestHandler.ashx', 'post', params=params, headers=headers, json=json_data)

        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9,he;q=0.8',
            'Connection': 'keep-alive',
            'Referer': 'https://he.americanexpress.co.il/personalarea/login/',
            'User-Agent': self.user_agent,
        }

        response = self.send_request('https://he.americanexpress.co.il/personalarea/dashboard/', 'get', headers=headers)

        # Extract userguid
        pattern = r"var userGuid = '(.*?)'"
        match = re.search(pattern, response.text)
        if match:
            self.user_guid = match.group(1)
        else:
            raise Exception("Could not find userGuid")

    def get_credit_cards(self):
        next_month = datetime.now() + relativedelta(months=1)

        cards = []
        card_idx = 0
        while True:

            headers = {
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'en-US,en;q=0.9,he;q=0.8',
                'Connection': 'keep-alive',
                'Referer': 'https://he.americanexpress.co.il/personalarea/transactionlist/?requiredDate=H',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.43',
            }

            params = {
                'reqName': 'CardsTransactionsList',
                'userGuid': self.user_guid,
                'month': str(next_month.month).zfill(2),
                'year': str(next_month.year),
                'cardIdx': card_idx,
                'requiredDate': 'H',
            }

            response = self.send_request('https://he.americanexpress.co.il/services/ProxyRequestHandler.ashx', 'get', params=params, headers=headers)

            json_data = response.json()

            if json_data["Header"]["Status"] == '-1':
                return cards

            card_idx_str = f"Index{card_idx}"
            assert(json_data["CardsTransactionsListBean"][card_idx_str]["CurrentCardTransactions"][1]["txnInfo"] is None)

            local_transactions_sum = 0
            local_transactions = json_data["CardsTransactionsListBean"][card_idx_str]["CurrentCardTransactions"][0]["txnIsrael"]
            if local_transactions is not None:
                local_transactions_sum = float(local_transactions[-1]["paymentSum"])
            
            abroad_transactions_sum = 0
            abroad_transactions = json_data["CardsTransactionsListBean"][card_idx_str]["CurrentCardTransactions"][2]["txnAbroad"]
            if abroad_transactions is not None:
                abroad_transactions_sum = float(abroad_transactions[-1]["paymentSumOutbound"])

            total_to_date = local_transactions_sum + abroad_transactions_sum
            
            cards.append(
                CreditCard(card_idx, json_data["CardsTransactionsListBean"]["cardNumberTail"], total_to_date=total_to_date, innerdata=json_data)
            )
            card_idx += 1

    def get_card_transactions(self, card_idx, month, year):
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9,he;q=0.8',
            'Connection': 'keep-alive',
            'Referer': 'https://he.americanexpress.co.il/personalarea/transactionlist/?requiredDate=H',
            'User-Agent': self.user_agent,
        }

        params = {
            'reqName': 'CardsTransactionsList',
            'userGuid': self.user_guid,
            'month': str(month).zfill(2),
            'year': str(year),
            'cardIdx': card_idx,
            'requiredDate': 'K',
        }

        response = self.send_request('https://he.americanexpress.co.il/services/ProxyRequestHandler.ashx', 'get', params=params, headers=headers)


        json_data = response.json()
        assert(json_data["Header"]["Status"] != '-1')
        assert(json_data["CardsTransactionsListBean"].get(f"Index{card_idx}") != None)

        transactions = []
        for txn_type in json_data["CardsTransactionsListBean"][f"Index{card_idx}"]["CurrentCardTransactions"]:
            transactions.extend(txn_type.get("txnIsrael") if txn_type.get("txnIsrael") != None else [])
            transactions.extend(txn_type.get("txnInfo") if txn_type.get("txnInfo") != None else [])
            transactions.extend(txn_type.get("txnAbroad") if txn_type.get("txnAbroad") != None else [])
        return transactions

def main():
    ae = AmericanExpress()
    israeli_id = getpass("Enter your israeli id: ")
    password = getpass("Enter your password: ")
    las6digits = getpass("Enter last 6 digits: ")
    ae.login(israeli_id, password, las6digits)
    ccs = ae.get_credit_cards()
    ae.get_card_transactions(0, 5, 2023)

if __name__ == "__main__":
    main()
