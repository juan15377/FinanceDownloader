import flet as ft
from data_downloader import FinanceRecorder, MyDate, MyPeriod
class TableFinancialRecorders(ft.Container):
    
    def __init__(self):
        self.financial_dfs_downloaded = {}
        self.financial_recorders = []
        table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Symbol")),
                ft.DataColumn(ft.Text("Fecha Inicio")),
                ft.DataColumn(ft.Text("Fecha Final")),
                ft.DataColumn(ft.Text("Periodo")),
                ft.DataColumn(ft.Text("Descargar")),
                ft.DataColumn(ft.Text("Eliminar")),
            ])
        super().__init__(table)
        
        
    def update(self):
        self.content.rows = []
        for r in self.financial_recorders:
            self.add(r)
        self.content.update() # the table

    def remove(self, financial_recorder):
        self.financial_recorders.remove(financial_recorder)
        self.update()
        pass 
            

    def add(self, financial_recorder):
        button_download = ft.TextButton(icon = ft.icons.DOWNLOAD)
        button_delete = ft.TextButton(icon = ft.icons.DELETE)
        
        def delete_financial_recorder(fr = financial_recorder):
            # part encarged of delete fr in the table and in financial_recorders 
            self.financial_recorders.remove(financial_recorder)
            self.update()
        
        
        def update_financial_recorder():
            # part encarged of add fr in the table and in financial_recorders
            
            pass
        
        self.content.rows.append(
            ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(financial_recorder.symbol)),
                        ft.DataCell(ft.Text(financial_recorder.start_date.date)),
                        ft.DataCell(ft.Text(financial_recorder.end_date.date)),
                        ft.DataCell(ft.Text(financial_recorder.period.p)),
                        ft.DataCell(button_download),
                        ft.DataCell(button_delete),
                    ]
            )
        )
        
        
import flet as ft

def main(page: ft.Page):
    table_financial_recorders = TableFinancialRecorders()

    page.add(table_financial_recorders)
    
    table_financial_recorders.add(FinanceRecorder("AAPL", MyDate("2022-01-01"), MyDate("2022-12-31"), MyPeriod("M")))
    
    table_financial_recorders.content.update()


ft.app(main)
            
      
