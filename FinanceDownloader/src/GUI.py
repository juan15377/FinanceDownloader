import flet as ft
from Downloader import FinanceRecorder, MyDate, MyPeriod  # clases
from Downloader import save_financial_data, compress_dataframe, decompress_dataframe

import socket
import time as tm
import threading



from flet import (
    ElevatedButton,
    FilePicker,
    FilePickerResultEvent,
    Page,
    Row,
    Text,
    icons,
)
def check_internet():
    try:
        # Intento de conexión al servidor de Google DNS
        socket.create_connection(("8.8.8.8", 53), timeout=5)
        return True
    except OSError:
        return False


class WifiActiveIcon(ft.Container):
    
    def __init__(self):
        self.icon_wifi = ft.Icon(ft.icons.WIFI_CALLING)
        self.status_text = ft.Text("Conectado")
        
        super().__init__(
            content=ft.Row(
                controls=[self.status_text, self.icon_wifi]
            )
        )

        # Crear y ejecutar el hilo en segundo plano para actualizar el icono
        threading.Thread(target=self.monitor_connection, daemon=True).start()

    def monitor_connection(self):
        """Verifica la conexión periódicamente y actualiza el ícono."""
        while True:
            tm.sleep(0.5)
            if check_internet():
                self.icon_wifi.name = ft.icons.SIGNAL_WIFI_4_BAR
                self.status_text.value = "Conectado"
            else:
                self.icon_wifi.name = ft.icons.WIFI_CALLING
                self.status_text.value = "Desconectado"
            
            # Actualizar el componente en pantalla
            self.update()


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
        self.rows_financial_recorders = {}
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
            horizontal_lines = ft.Border.bottom,
            vertical_lines= ft.Border.top
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
                         ink = True,
                         bgcolor = ft.colors.BLUE                     
                         )
        
        
    def update_financial_recorders(self):
        self.table.rows = list(self.rows_financial_recorders.values())
        self.table.update()
        
        
    def restart(self):
        self.financial_dfs_downloaded = {}
        self.financial_recorders = []
        self.table.update()

    def remove(self, financial_recorder):
        self.financial_recorders.remove(financial_recorder)       
        try :
            del self.financial_dfs_downloaded_compressed[financial_recorder]
            del self.rows_financial_recorders[financial_recorder]
        except KeyError:
            pass  # financial_recorder no se encuentra en financial_dfs_downloaded, no se hace nada 
        #volvemos a actualizar todos los nuevos 
        self.update_financial_recorders()

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
            del self.rows_financial_recorders[fr]
            self.update_financial_recorders()
            
        button_delete.on_click = delete_financial_recorder
        
        
        def download_financial_recorder(e, fr = financial_recorder, bd = button_download):
            # part encarged of add fr in the table and in financial_recorders
            data = fr.download()
            print(data)
            self.financial_dfs_downloaded_compressed[fr] = compress_dataframe(data)
            bd.icon = ft.icons.CHECK
            print("Icono actualizado")
            bd.update()
            pass
        
        button_download.on_click = download_financial_recorder
        self.buttons_downloaded.append(button_download)
        
        self.rows_financial_recorders[financial_recorder] = ft.DataRow(
                cells=[
                        ft.DataCell(ft.Text(financial_recorder.symbol)),
                        ft.DataCell(ft.Text(financial_recorder.start_date.date)),
                        ft.DataCell(ft.Text(financial_recorder.end_date.date)),
                        ft.DataCell(ft.Text(financial_recorder.period.p)),
                        ft.DataCell(button_download),
                        ft.DataCell(button_delete),
                    ]
        )
        
        self.update_financial_recorders()
        
        
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
        
        wifi_icon = WifiActiveIcon()

        super().__init__(controls = [
            symbol_textfiled,
            start_date_textfiled,
            end_date_textfiled,
            period,
            button_add,
            wifi_icon
        ])
        
        
class ButtonsSaveFinanceRecorder(ft.Container):
    
    def __init__(self, table:TableFinancialRecorders, page : ft.Page):
        reset_button = ft.TextButton(text = "Reiniciar")
        
        def save_file_result(e: FilePickerResultEvent):
            save_file_path.value = e.path if e.path else "Cancelled!"
            path_name = save_file_path.value  + ".xlsx"
            print(path_name)
            save_financial_data(path_name, table.financial_dfs_downloaded_compressed)
            
            ### aqui va el codigo para guardar 

        save_file_dialog = FilePicker(on_result=save_file_result)
        save_file_path = Text()

        # Open directory dialog
        def get_directory_result(e: FilePickerResultEvent):
            directory_path.value = e.path if e.path else "Cancelled!"
            directory_path.update()

        get_directory_dialog = FilePicker(on_result=get_directory_result)
        directory_path = Text()

        # hide all dialogs in overlay
        page.overlay.extend([save_file_dialog, get_directory_dialog])

        super().__init__(
            content = ElevatedButton(
                        "Save file",
                        icon=icons.SAVE,
                        on_click=lambda _: save_file_dialog.save_file(),
                        disabled=page.web,
                    )
        )


        
import flet as ft
import time as tm 

def main(page: ft.Page):
    page.expand = False
    table_financial_recorders = TableFinancialRecorders()
    table_financial_recorders.financial_recorders = [
        FinanceRecorder("AAPL", MyDate("2021-01-01"), MyDate("2021-12-31"), MyPeriod("1d")),
        FinanceRecorder("GOOGL", MyDate("2021-01-01"), MyDate("2021-12-31"), MyPeriod("1d")),
        FinanceRecorder("MSFT", MyDate("2021-01-01"), MyDate("2021-12-31"), MyPeriod("1d"))  
    ]
    guardador = ButtonsSaveFinanceRecorder(table_financial_recorders, page)
    hola = NewFinancialRecorder(table_financial_recorders)
    page.add(hola, table_financial_recorders, guardador)
    table_financial_recorders.update_financial_recorders()
    table_financial_recorders.table.update()
    
    
    table_financial_recorders.table.update()
    
    tm.sleep(20)
    
    #table_financial_recorders.download_all()



ft.app(main)
            
      
