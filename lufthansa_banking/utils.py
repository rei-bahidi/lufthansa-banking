import logging
from functools import wraps
from django.http import HttpResponseForbidden


logging.basicConfig(filename='./example.log', encoding='utf-8', level=logging.DEBUG)

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
    if from_currency == to_currency:
        return
    
    currency_rates = {
        'USD': {'EUR': 0.85, 'ALL': 100.0},
        'EUR': {'USD': 1.18, 'ALL': 123.0},
        'ALL': {'USD': 0.01, 'EUR': 0.0081}
    }

    return currency_rates.get(from_currency, {}).get(to_currency)
    
def admin_required(view_func):
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        else:
            return HttpResponseForbidden("You do not have access to this resource.")
    return wrapped_view


def banker_required(view_func):
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseForbidden("You do not have access to this resource.")
        
        if request.user.user_type == 'CUSTOMER':
            return HttpResponseForbidden("You do not have access to this resource.")

        if request.user.user_type == 'BANKER' or request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        
        return HttpResponseForbidden("You do not have access to this resource.")
    return wrapped_view

def customer_required(view_func):
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseForbidden("You do not have access to this resource.")
        
        if request.user.user_type == 'BANKER':
            return HttpResponseForbidden("You do not have access to this resource.")

        if request.user.user_type == 'CUSTOMER' or request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        
        return HttpResponseForbidden("You do not have access to this resource.")
    return wrapped_view

