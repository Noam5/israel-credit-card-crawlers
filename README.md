# Credit Card Management System

This project provides an interface to interact with credit card providers. The project currently supports interaction with CalOnline and Isracard. The functionality includes authenticating with these services, retrieving credit card information, and fetching transaction details for a specified card, month, and year.

## Getting Started

These instructions will help you get a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

- Python 3.6 or higher

### Installing

1. Clone this repository:

   ```git clone https://github.com/Noam5/israel-credit-card-crawlers.git```

2. Install dependencies:

   ```pip install -r requirements.txt```

### Usage
This project includes several Python files, each with a specific purpose:

- cal.py: Provides an interface to interact with CalOnline, including methods to login, get credit cards, and fetch transaction details.

- isracard.py: Similar to cal.py but provides an interface for Isracard.

- common.py: Includes abstract base classes and common utilities used by cal.py and isracard.py.

Here are basic examples of how to use the functionality provided by cal.py and isracard.py:

For cal.py:

```
from cal import CalOnline

cal = CalOnline()
username = input("Enter your username: ")
password = input("Enter your password: ")
cal.login(username, password)
cards = cal.get_credit_cards()
for card in cards:
    transactions = cal.get_card_transactions(card.card_id, 5, 2023)
```

For isracard.py:

```
from isracard import Isracard

isracard = Isracard()
israeli_id = input("Enter your israeli id: ")
password = input("Enter your password: ")
las6digits = input("Enter last 6 digits: ")
isracard.login(israeli_id, password, las6digits)
cards = isracard.get_credit_cards()
for card in cards:
   transactions = isracard.get_card_transactions(card.card_id, 5, 2023)
```

License
This project is licensed under the MIT License - see the LICENSE.md file for details.





