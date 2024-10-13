import logging
from functools import wraps
from django.http import HttpResponseForbidden

# Utils file where general concepts used thoruguout the project are defined


# Set the logger configs such as the logger location and name, 
# the provisory location is the root of the project but normally it should be in a log folder,
# in the root of the system
logging.basicConfig(filename='./example.log', encoding='utf-8', level=logging.DEBUG)

# Create a factory function to create loggers
logger = lambda name: logging.getLogger(name) 

def convert_currency(amount: float, from_currency: str, to_currency: str) -> float:
    """
    Convert the amount from one currency to another
    :param amount: the amount to convert
    :param from_currency: the currency of the amount
    :param to_currency: the currency to convert to
    :return: the converted amount
    """
    exhchange_rate = get_exchange_rate(from_currency, to_currency)
    if exhchange_rate:
        return amount * exhchange_rate
    return amount


def get_exchange_rate(from_currency: str, to_currency: str) -> float:
    """
    Get the exchange rate between two currencies
    :param from_currency: the currency to convert from
    :param to_currency: the currency to convert to
    :return: the exchange rate
    """
    if from_currency == to_currency:
        return
    
    currency_rates = {
        'USD': {'EUR': 0.85, 'ALL': 100.0},
        'EUR': {'USD': 1.18, 'ALL': 123.0},
        'ALL': {'USD': 0.01, 'EUR': 0.0081}
    }

    return currency_rates.get(from_currency, {}).get(to_currency)