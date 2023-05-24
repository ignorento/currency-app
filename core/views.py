from django.shortcuts import render

from currency.models import ExchangeRateProvider  # noqa
from currency.services import ExchangeRatesService, ProviderService  # noqa


# Create your views here.
def index(request):
    providers = {
        'name': "Privat Bank",
        'api_url': "https://api.privatbank.ua/p24api/exchange_rates"
    }
    # url = "https://api.privatbank.ua/p24api/exchange_rates"
    # name = "Privat Bank"

    # provider = ProviderService(name=providers['name'], api_url=providers['api_url']).get_or_create()
    # print(provider)
    service = ExchangeRatesService(name=providers['name'], api_url=providers['api_url'])
    rates = service.get_rates()  # noqa
    return render(request, 'core/index.html')
