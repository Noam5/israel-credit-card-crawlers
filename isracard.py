import os
import requests
from getpass import getpass
from fake_useragent import UserAgent
import re
from datetime import datetime
from dateutil.relativedelta import relativedelta
import json

from common import CardProvider, CreditCard

class Isracard(CardProvider):

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
            data=data,
        )

        if response.status_code != 200:
            raise Exception(f"Request failed with status {response.status_code}")

        return response


    def login(self, username, password, cardsixdigits):
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9,he;q=0.8',
            'Connection': 'keep-alive',
            'Origin': 'https://digital.isracard.co.il',
            'Referer': 'https://digital.isracard.co.il/personalarea/Login/',
            'User-Agent': self.user_agent,
            '__RequestVerificationToken': 'FZAlQryGvN4WFnNSKMBQqL7wmb-1-6AzLfnxPIBpyleMQZzNwC6gmE5493rmtFgGaMG3HpkIJt1WVI38JmIlFxsC7MM1',
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
            'companyCode': '11',
            'countryCode': '212',
            'isGoogleCaptcha': True,
        }
        response = self.send_request('https://digital.isracard.co.il/services/ProxyRequestHandler.ashx', 'post', params=params, headers=headers, json=json_data)

        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9,he;q=0.8',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': 'https://digital.isracard.co.il',
            'Referer': 'https://digital.isracard.co.il/personalarea/dashboard/',
            'User-Agent': self.user_agent,
        }
        params = {
            'reqName': 'performLogonI',
        }
        data = {
            'MisparZihuy': username,
            'countryCode': '212',
            'idType': '1',
            'Sisma': password,
            'cardSuffix': cardsixdigits,
            'isGoogleCaptcha': True,
        }
        response = self.send_request('https://digital.isracard.co.il/services/ProxyRequestHandler.ashx', 'post', params=params, headers=headers, data=data)

        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9,he;q=0.8',
            'Connection': 'keep-alive',
            'Referer': 'https://digital.isracard.co.il/personalarea/transaction-list/?requiredDate=K',
            'User-Agent': self.user_agent,
        }
        params = {
            'requiredDate': 'K',
        }
        data = {
            'dashboardChargesDetails': '{"HolderId":"","CardIndex":"","AccountNumber":"","Filter":"","RequiredDate":""}',
        }
        response = self.send_request('https://digital.isracard.co.il/personalarea/transaction-list/', 'post', params=params, headers=headers, data=data)

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
                'Referer': 'https://digital.isracard.co.il/personalarea/transaction-list/?requiredDate=K',
                'User-Agent': self.user_agent,
            }

            params = {
                'reqName': 'CardsTransactionsList',
                'userGuid': self.user_guid,
                'month': str(next_month.month).zfill(2),
                'year': str(next_month.year),
                'cardIdx': card_idx,
                'requiredDate': 'K',
            }

            response = self.session.get(
                'https://digital.isracard.co.il/services/ProxyRequestHandler.ashx',
                params=params,
                headers=headers,
            )
            json_data = response.json()

            if json_data["Header"]["Status"] == '-1':
                return cards
            
            cards.append(
                CreditCard(card_idx, json_data["CardsTransactionsListBean"]["cardNumberTail"], innerdata=json_data)
            )
            card_idx += 1

    def get_card_transactions(self, card_idx, month, year):
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9,he;q=0.8',
            'Connection': 'keep-alive',
            'Referer': 'https://digital.isracard.co.il/personalarea/transaction-list/?requiredDate=K',
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

        response = self.session.get(
            'https://digital.isracard.co.il/services/ProxyRequestHandler.ashx',
            params=params,
            headers=headers,
        )
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
    ic = Isracard()
    israeli_id = getpass("Enter your israeli id: ")
    password = getpass("Enter your password: ")
    las6digits = getpass("Enter last 6 digits: ")
    ic.login(israeli_id, password, las6digits)
    ccs = ic.get_credit_cards()
    ic.get_card_transactions(0, 5, 2023)

if __name__ == "__main__":
    main()
