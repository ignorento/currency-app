import requests
import datetime

from currency.models import ExchangeRateProvider, ExchangeRate


class ProviderService:
    def __init__(self, name, api_url):
        self.name = name
        self.api_url = api_url

    def get_or_create(self):
        provider = ExchangeRateProvider.objects.get_or_create(name=self.name, api_url=self.api_url)[0]
        return provider

    # def add_provider(self):
    #     provider = {
    #         'name': self.name,
    #         'api_url': self.url
    #     }
    #     return provider

class ExchangeRatesService:

    CURRENCIES = ['GBP', 'USD', 'CHF', 'EUR']
    # очищает базу перед парсингом и записью в базу
    # ExchangeRate.objects.all().delete()
    def __init__(self, name, api_url):
        self.name = name
        self.api_url = api_url
        self.provider = ProviderService(name=self.name, api_url=self.api_url).get_or_create()

    def get_rates(self):
        start_date = datetime.datetime(2023, 1, 1)
        end_date = datetime.datetime.now()

        while start_date < end_date:
            currency_rates = self.get_rate(date=start_date)
            print(currency_rates)
            if isinstance(currency_rates, str):
                break
            exchange_rates = [
                ExchangeRate(
                    base_currency=item['base_currency'],
                    currency=item['currency'],
                    date=item['date'],
                    sale_rate=item['sale_rate'],
                    buy_rate=item['buy_rate'],
                    provider_id=item['provider_id']
                )
                for item in currency_rates
            ]

            ExchangeRate.objects.bulk_create(exchange_rates)

            start_date += datetime.timedelta(days=1)


    def get_rate(self, date=None):
        # url = "https://api.privatbank.ua/p24api/exchange_rates"

        params = {
            "date": date.strftime("%d.%m.%Y")
        }
        response = requests.get(self.provider.api_url, params=params)
        data = response.json()

        try:
            data["exchangeRate"]
        except KeyError:
            # print("no exchange rate for today yet")
            return "no exchange rate for today yet"

        rates = data["exchangeRate"]
        currency_rates = []
        base_currency = data["baseCurrencyLit"]
        date = data['date']


        for r in rates:
            if r['currency'] not in self.CURRENCIES:
                continue

            currency_rates.append(
                {
                    'base_currency': base_currency,
                    'currency': r['currency'],
                    'date': date,
                    'sale_rate': r['saleRate'],
                    'buy_rate': r['purchaseRate'],
                    'provider_id': self.provider.id

                }
            )

        return currency_rates
