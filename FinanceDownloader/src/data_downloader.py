import yfinance as yf
import pandas as pd 

class MyDate():
    def __init__(self, date: str) -> None:
        self.date = date

class MyPeriod():
    def __init__(self, period: str) -> None:
        self.p = period

class FinanceRecorder():
    def __init__(self, symbol: str, start_date: MyDate, end_date: MyDate, period: MyPeriod) -> None:
        self.symbol = symbol
        self.start_date = start_date
        self.end_date = end_date
        self.period = period

    def download(self):
        # No se utiliza el periodo aquí, ya que se usan las fechas start y end
        data = yf.download(self.symbol, start=self.start_date.date, end=self.end_date.date)
        data.index = data.index.tz_localize(None)
        return data

def save_financial_data(path_file: str, financialrecorders: list):
    with pd.ExcelWriter(path_file) as writer:
        for r in financialrecorders:
            data = r.download()
            name = r.symbol
            data.to_excel(writer, sheet_name=name)
