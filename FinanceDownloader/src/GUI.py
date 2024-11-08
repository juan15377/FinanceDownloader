import flet as ft
from Downloader.data_downloader import FinanceRecorder, MyDate, MyPeriod  # clases
from Downloader.data_downloader import save_financial_data, compress_dataframe, decompress_dataframe

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
                self.icon_wifi.name = ft.icons.SIGNAL_WIFI_0_BAR
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
                    height= 60,
                    width = 120
                    )
    pass


class TableFinancialRecorders(ft.Container):
    
    def __init__(self):
        self.rows_financial_recorders = {}
        self.financial_dfs_downloaded_compressed = {}
        self.financial_recorders = []
        self.buttons_downloaded = {}
        table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Symbol"      , size = 15)),
                ft.DataColumn(ft.Text("Fecha Inicio", size = 15)),
                ft.DataColumn(ft.Text("Fecha Final" , size = 15)),
                ft.DataColumn(ft.Text("Periodo"     , size = 15)),
                ft.DataColumn(ft.Text("Descargar"   , size = 15)),
                ft.DataColumn(ft.Text("Eliminar"    , size = 15)),
            ],
            width=700,
            height=1000,
            vertical_lines=ft.BorderSide(1, "green"),
            horizontal_lines=ft.BorderSide(1, "green"),
            heading_row_height=30,
            data_row_color={ft.ControlState.HOVERED: "green"},
            sort_column_index=0,
            sort_ascending=True,
            show_checkbox_column=True,
            divider_thickness=0,
            column_spacing=40,
            )
        
        self.table = table
        column_scrolling = ft.Column(controls = [table],
                                   height = 300,
                                   width = 700,
                                   scroll=ft.ScrollMode.ALWAYS,
                                   expand=False)
        
        row_scrolling = ft.Row(controls = [column_scrolling],
                                   height = 300,
                                   width = 700,
                                   scroll=ft.ScrollMode.ALWAYS,            
                              )
        super().__init__(content = row_scrolling,
                         ink = True,
                         theme=ft.Theme(color_scheme_seed=ft.colors.BLUE),
                         padding=10,
                         border_radius=10,
                         border=ft.border.all(1, "green")
                         )
        
        
    def update_financial_recorders(self):
        self.table.rows = list(self.rows_financial_recorders.values())
        self.table.update()
        
        
    def restart(self):
        self.rows_financial_recorders = {}
        self.financial_dfs_downloaded_compressed = {}
        self.financial_recorders = []
        self.buttons_downloaded = {}
        
        self.update_financial_recorders()

    def remove(self, financial_recorder):
        self.financial_recorders.remove(financial_recorder)    
        del self.buttons_downloaded[financial_recorder]  
        del self.rows_financial_recorders[financial_recorder]
        try :
            del self.financial_dfs_downloaded_compressed[financial_recorder]
        except KeyError:
            pass  # financial_recorder no se encuentra en financial_dfs_downloaded, no se hace nada 
        #volvemos a actualizar todos los nuevos 
        self.update_financial_recorders()

        pass 
    
    def download_all(self):
        for fr in self.financial_recorders :
            if fr.already_downloaded:
                continue 
            else :
                button_download_fr = self.buttons_downloaded[fr]
                e = 1 # como no se usa el objecto e dentro de la funcion podemos hacer esto
                button_download_fr.on_click(e)
            

    def add(self, financial_recorder):
        button_download = ft.TextButton(icon = ft.icons.DOWNLOAD)
        button_delete = ft.TextButton(icon = ft.icons.DELETE)
        
        self.financial_recorders.append(financial_recorder)
        
        def delete_financial_recorder(e, fr = financial_recorder):
            # part encarged of delete fr in the table and in financial_recorders 
            self.remove(fr)
            self.update_financial_recorders()
            
        button_delete.on_click = delete_financial_recorder
        
        
        def download_financial_recorder(e, fr = financial_recorder, button_download = button_download,
                                                                    button_delete = button_delete):
            # part encarged of add fr in the table and in financial_recorders
            data = fr.download()
            if data.empty:
                button_download.icon = ft.icons.ERROR
                button_download.on_click = None
                button_download.update()
                return None 
            self.financial_dfs_downloaded_compressed[fr] = compress_dataframe(data)
            del data
            button_download.icon = ft.icons.CHECK
            button_download.update()
            pass
        
        button_download.on_click = download_financial_recorder
        self.buttons_downloaded[financial_recorder] = button_download
        
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
        
class NewFinancialRecorder(ft.Container):
    
    def __init__(self, table:TableFinancialRecorders):
        symbol_textfiled = ft.TextField(label = "Symbol", height=60, width = 120)
        start_date_textfiled = ft.TextField(label = "Fecha Inicio", height=60, width = 120)
        end_date_textfiled = ft.TextField(label = "Fecha Final", height=60, width = 120)
        period = PeriodSelector()
        
        button_add = ft.FilledButton(text = "Añadir")
        
        def add_to_table(e, table = table):
            table.add(FinanceRecorder(symbol_textfiled.value, 
                                      MyDate(start_date_textfiled.value), 
                                      MyDate(end_date_textfiled.value), 
                                      MyPeriod(period.value)))
            table.table.update()
        button_add.on_click = add_to_table
        
        wifi_icon = WifiActiveIcon()

        super().__init__(
            content = ft.Row(controls = [
                            symbol_textfiled,
                            start_date_textfiled,
                            end_date_textfiled,
                            period,
                            button_add,
                            wifi_icon
                            ]
                ),
            )
        
        
class ButtonsSaveFinanceRecorder(ft.Container):
    
    def __init__(self, table:TableFinancialRecorders, page : ft.Page):
        
        def save_file_result(e: FilePickerResultEvent):
            save_file_path = e.path if e.path else "Null"
            path_name = save_file_path  + ".xlsx"
            save_financial_data(path_name, table.financial_dfs_downloaded_compressed)
            
            ### aqui va el codigo para guardar 

        save_file_dialog = FilePicker(on_result=save_file_result)
        save_file_path = ""

        # Open directory dialog
        def get_directory_result(e: FilePickerResultEvent):
            directory_path.value = e.path if e.path else "Cancelled!"
            directory_path.update()

        get_directory_dialog = FilePicker(on_result=get_directory_result)
        directory_path = Text()

        # hide all dialogs in overlay
        page.overlay.extend([save_file_dialog, get_directory_dialog])
        
        def save_data():
            if len(table.financial_dfs_downloaded_compressed) != 0:
                save_file_dialog.save_file()


        super().__init__(
            content = ft.Row(
                controls = [
                        ElevatedButton(
                            "Guardar Archivo",
                            icon=icons.SAVE,
                            on_click=lambda _: save_data(),
                            disabled=page.web,
                        ),
                        ElevatedButton(
                            "Descargar Todo",
                            icon=icons.DOWNLOAD,
                            on_click=lambda _: table.download_all(),
                            disabled=page.web,
                        ),
                        ElevatedButton(
                            "Reiniciar",
                            icon=icons.RESTART_ALT,
                            on_click=lambda _: table.restart(),
                            disabled=page.web,
                        ),
                ]
            )
                        
        )


        
import flet as ft
import time as tm 


def main(page: ft.Page):
    page.expand = False
    page.theme_mode = ft.ThemeMode.DARK
    page.theme = ft.Theme(color_scheme_seed="green")
    page.update()
    
    
    table_financial_recorders = TableFinancialRecorders()
    save_finance_recorders = ButtonsSaveFinanceRecorder(table_financial_recorders, page)
    new_finance_recorder = NewFinancialRecorder(table_financial_recorders)
    all_ = ft.Column(
        controls = [
            new_finance_recorder, 
            table_financial_recorders, 
            save_finance_recorders
        ],
        expand=True,
        width=700,
        height=1000,
    )
    
    fixed_window_width = 750
    fixed_window_height = 470
    
    def page_resized(e):
        page.window.width = fixed_window_width
        page.window.height = fixed_window_height
        page.update()

    page.on_resized = page_resized
    page.title = "Yahoo Finance Downloader by JJVF"
    page.window.width = fixed_window_width
    page.window.height = fixed_window_height
    page.add(all_,)
    page.update()
    



ft.app(main)
            
      
