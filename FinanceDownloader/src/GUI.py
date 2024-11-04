import flet as ft
from data_downloader import FinanceRecorder, MyDate, MyPeriod # classes
from data_downloader import save_financial_data, compress_dataframe, decompress_dataframe





class PeriodSelector(ft.Dropdown):
    
    def __init__(self):
        super().__init__(label = "Periodo",
                         options =  [
                    ft.dropdown.Option("1d"),
                    ft.dropdown.Option("1w"),
                    ft.dropdown.Option("1y"),
                    ],
                    width = 120,
                    height= 60)
    pass


class TableFinancialRecorders(ft.Container):
    
    def __init__(self):
        self.financial_dfs_downloaded_compressed = {}
        self.financial_recorders = []
        self.buttons_downloaded = []
        table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Symbol")),
                ft.DataColumn(ft.Text("Fecha Inicio")),
                ft.DataColumn(ft.Text("Fecha Final")),
                ft.DataColumn(ft.Text("Periodo")),
                ft.DataColumn(ft.Text("Descargar")),
                ft.DataColumn(ft.Text("Eliminar")),
            ],
            width=700,
            height=1000,
            )
        self.table = table
        column_scrolling = ft.Column(controls = [table],
                                   height = 300,
                                   width = 700,
                                   scroll=ft.ScrollMode.ALWAYS,
                                   expand=True)
        
        row_scrolling = ft.Row(controls = [column_scrolling],
                                   height = 300,
                                   width = 700,
                                   scroll=ft.ScrollMode.ALWAYS,            
                              )
        super().__init__(content = row_scrolling,
                         )
        
        
    def update(self):
        self.table.rows = []
        for r in self.financial_recorders:
            self.add(r)
        self.table.update() # the table
        
    def restart(self):
        self.financial_dfs_downloaded = {}
        self.financial_recorders = []
        self.table.update()

    def remove(self, financial_recorder):
        self.financial_recorders.remove(financial_recorder)        
        #volvemos a actualizar todos los nuevos 
        self.update()

        pass 
    
    def download_all(self):
        for button in self.buttons_downloaded :
            e = 1 # como no se usa el objecto e dentro de la funcion podemos hacer esto
            button.on_click(e)
            

    def add(self, financial_recorder):
        button_download = ft.TextButton(icon = ft.icons.DOWNLOAD)
        button_delete = ft.TextButton(icon = ft.icons.DELETE)
        
        self.financial_recorders.append(financial_recorder)
        
        def delete_financial_recorder(e, fr = financial_recorder):
            # part encarged of delete fr in the table and in financial_recorders 
            self.remove(fr)
            try :
                del self.financial_dfs_downloaded[fr]
            except KeyError:
                pass  # fr no se encuentra en financial_dfs_downloaded, no se hace nada
            self.update()
            
        button_delete.on_click = delete_financial_recorder
        
        
        def download_financial_recorder(e, fr = financial_recorder):
            # part encarged of add fr in the table and in financial_recorders
            self.financial_dfs_downloaded_compressed[fr.symbol] = compress_dataframe(fr.download())
            button_download.icon = ft.icons.CHECK
            button_download.update()
            pass
        
        button_download.on_click = download_financial_recorder
        self.buttons_downloaded.append(button_download)
        
        self.table.rows.append(
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
        
        
class NewFinancialRecorder(ft.Row):
    
    def __init__(self, table:TableFinancialRecorders):
        symbol_textfiled = ft.TextField(label = "Symbol", height=60, width = 120)
        start_date_textfiled = ft.TextField(label = "Fecha Inicio", height=60, width = 120)
        end_date_textfiled = ft.TextField(label = "Fecha Final", height=60, width = 120)
        period = PeriodSelector()
        
        button_add = ft.TextButton(text = "Añadir")
        
        def add_to_table(e, table = table):
            table.add(FinanceRecorder(symbol_textfiled.value, 
                                      MyDate(start_date_textfiled.value), 
                                      MyDate(end_date_textfiled.value), 
                                      MyPeriod(period.value)))
            table.table.update()
        button_add.on_click = add_to_table

        super().__init__(controls = [
            symbol_textfiled,
            start_date_textfiled,
            end_date_textfiled,
            period,
            button_add,
        ])
        
        
class ButtonsSaveFinanceRecorder(ft.Container):
    
    def __init__(self, table:TableFinancialRecorders):
        save_button = ft.TextButton(text = "Guardar")
        reset_button = ft.TextButton(text = "Reiniciar")
        
        
        def save_data(e, table = table):
            nombre = "hola.xlsx"
            save_financial_data(nombre, table.financial_dfs_downloaded_compressed)
            # aqui se puede guardar los datos en un archivo, base de datos, etc...
            pass 
        
        save_button.on_click = save_data
        
        self.table = table
        super().__init__(save_button)
        
    

        
import flet as ft
import time as tm 

def main(page: ft.Page):
    table_financial_recorders = TableFinancialRecorders()
    guardador = ButtonsSaveFinanceRecorder(table_financial_recorders)
    hola = NewFinancialRecorder(table_financial_recorders)
    page.add(hola, table_financial_recorders, guardador)
    
    table_financial_recorders.table.update()
    
    tm.sleep(20)
    
    table_financial_recorders.download_all()



ft.app(main)
            
      
