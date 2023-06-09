import os
import requests
from getpass import getpass
from fake_useragent import UserAgent
import re
import json

class Isracard:
    def __init__(self):
        self.session = requests.Session()
        ua = UserAgent()
        self.user_agent = ua.random
        self.user_guid = None

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

        response = self.session.post(
            'https://digital.isracard.co.il/services/ProxyRequestHandler.ashx',
            params=params,
            headers=headers,
            json=json_data,
        )

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

        response = self.session.post(
            'https://digital.isracard.co.il/services/ProxyRequestHandler.ashx',
            params=params,
            headers=headers,
            data=data,
        )

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

        response = self.session.post(
            'https://digital.isracard.co.il/personalarea/transaction-list/',
            params=params,
            headers=headers,
            data=data,
        )

        pattern = r"var userGuid = '(.*?)'"
        match = re.search(pattern, response.text)

        # Extract the value
        if match:
            self.user_guid = match.group(1)
        else:
            raise Exception("Could not find userGuid")

    def get_credit_cards(self):
        pass

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
        pass

def main():
    ic = Isracard()
    username = getpass("Enter your username: ")
    password = getpass("Enter your password: ")
    las6digits = getpass("Enter last 6 digits: ")
    ic.login(username, password, las6digits)
    #ccs = ic.get_credit_cards()
    ic.get_card_transactions(0, 5, 2023)

if __name__ == "__main__":
    main()
