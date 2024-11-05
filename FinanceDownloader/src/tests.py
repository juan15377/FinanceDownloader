from Downloader import * 

fr = FinanceRecorder("ftgybhjnkm", MyDate("2020-10-10"), MyDate("2021-10-10"), MyPeriod("1d"))

print(fr.download())