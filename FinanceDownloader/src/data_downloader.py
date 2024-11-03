class MyDate():
    
    def __init__(self, date:str) -> None:
        self.date = date
        pass
    
def Period():
    
    def __init__(self, period:str):
        self.period = period
        pass
    

class FinanceRecorder():
    
    def __init__(self, symbol : str, start_date:MyDate, end_date:MyDate, period:Period) -> None:
        self.symbol = symbol
        self.start_date = start_date
        self.end_date = end_date
        self.period = period

        pass
    
    def download(self):
        
        
    
