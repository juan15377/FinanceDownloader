import yfinance as yf
import pandas as pd 
import pickle
import gzip
import io

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
        self.already_downloaded = False

    def download(self):
        # No se utiliza el periodo aquí, ya que se usan las fechas start y end
         
        data = yf.download(self.symbol, start=self.start_date.date, end=self.end_date.date)
        data.index = data.index.tz_localize(None)
        self.already_downloaded = True
        return data

            


def compress_dataframe(df):
    buffer = io.BytesIO()
    with gzip.GzipFile(fileobj=buffer, mode='wb') as f:
        pickle.dump(df, f)
    return buffer.getvalue()

def decompress_dataframe(df_compressed):
    # Crear un buffer de BytesIO con los datos comprimidos
    buffer = io.BytesIO(df_compressed)
    
    # Descomprimir y cargar el DataFrame
    with gzip.GzipFile(fileobj=buffer, mode='rb') as f:
        return pickle.load(f)
    
def save_financial_data(path_file: str, dict_financial_df_compressed: dict):
    with pd.ExcelWriter(path_file) as writer:
        for (fr, df_compressed) in dict_financial_df_compressed.items():
            name_symbol = fr.symbol
            data = decompress_dataframe(df_compressed)
            data.to_excel(writer, sheet_name=name_symbol)
