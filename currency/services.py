import concurrent
from concurrent.futures import ThreadPoolExecutor

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


class ExchangeRatesService:

    CURRENCIES = ['GBP', 'USD', 'CHF', 'EUR']

    # очищает базу перед парсингом и записью в базу
    ExchangeRate.objects.all().delete()

    def __init__(self, name, api_url):
        self.name = name
        self.api_url = api_url
        self.provider = ProviderService(**self.__dict__).get_or_create()


    def process_date(self, date):
        # Ваш код для обработки каждой даты
        if ExchangeRatesService.date_check(date):
            currency_rates = self.get_rate(date=date)
            if isinstance(currency_rates, str):
                print(currency_rates)
                return None
            return currency_rates
        else:
            print(f'exchange rate for the {date} date is already in the database')


    def get_rates(self):
        start_test = datetime.datetime.now()
        start_date = datetime.datetime(2023, 5, 11)
        end_date = datetime.datetime.now()

        dates = [
            (start_date + datetime.timedelta(days=i)).strftime("%d.%m.%Y")
            for i in range((end_date - start_date).days + 1)
        ]

        # Создаем пул потоков с ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=5) as executor:
            # Запускаем задачи обработки дат в пуле потоков
            futures = [executor.submit(self.process_date, date) for date in dates]
            # Получаем результаты выполнения задач
            for future in concurrent.futures.as_completed(futures):
                currency_rates = future.result()
                if currency_rates:
        # while start_date < end_date:
        #     start_date_format = start_date.strftime("%d.%m.%Y")

            ## if self.date_check(start_date_format):
                # future = executor.submit(self.get_rate, start_date_format)
                ## currency_rates = self.get_rate(date=start_date_format)
                # currency_rates = future.result()
                    self.add_to_db(currency_rates)
                    print(currency_rates)

                # if isinstance(currency_rates, str):
                #     break

                # self.add_to_db(currency_rates)
                # exchange_rates = [
                #     ExchangeRate(
                #         base_currency=item['base_currency'],
                #         currency=item['currency'],
                #         date=item['date'],
                #         sale_rate=item['sale_rate'],
                #         buy_rate=item['buy_rate'],
                #         provider_id=item['provider_id']
                #     )
                #     for item in currency_rates
                # ]
                #
                # ExchangeRate.objects.bulk_create(exchange_rates)

            # else:
            #     print(f'exchange rate for the {start_date_format} date is already in the database')
            #
            # start_date += datetime.timedelta(days=1)

        sorted_db_by_time = ExchangeRate.objects.all().order_by('date').values()
        end_test = datetime.datetime.now()
        execution_time = end_test - start_test
        print(f"Время выполнения программы: {execution_time}")
        return sorted_db_by_time

    def get_rate(self, date=None):
        params = {
            "date": date
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

    @staticmethod
    def date_check(date):
        my_date_in_db = (
            ExchangeRate.objects.
            filter(
                date=date
            )
            .first()
        )
        if my_date_in_db:
            return False
        return True

    @staticmethod
    def add_to_db(currency_rates):
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
