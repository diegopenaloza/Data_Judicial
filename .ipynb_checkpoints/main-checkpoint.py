from playwright.sync_api import sync_playwright
import time
import time 
from plyer import notification
import yaml
import pandas as pd
from bs4 import BeautifulSoup

# +
entidad_names=["Municipalidad de Guayaquil",
"Municipio de Guayaquil",
"MI MUNICIPALIDAD DE GUAYAQUIL",
"MI MUNICIPIO DE GUAYAQUIL",
"MUNICIPIO GUAYAQUIL"]

entidad_ruc=["0960000220001"]
# -

import pickle


direct = "C:/Users/Diego/AppData/Local/Mozilla/Firefox/Profiles/ow35cx67.default"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    # browser = p.firefox.launch_persistent_context(channel="firefox"
    #                                                               ,headless=False,
    #                                                               user_data_dir=direct)
    # browser = p.firefox.launch(headless=False,)
    page = browser.new_page()
    page.goto("http://consultas.funcionjudicial.gob.ec/informacionjudicial/public/informacion.jsf", wait_until='domcontentloaded')

    time.sleep(2)
    usuario="MUNICIPIO GUAYAQUIL"
    page.locator("input[id='form1:txtDemandadoApellido']").type(usuario, delay=50);
    page.locator("button[id='form1:butBuscarJuicios']").click()
    time.sleep(5)
    html_table_0=page.locator(".ui-datatable-tablewrapper:nth-of-type(2)").inner_html()
    tables_0 = pd.read_html(html_table_0,decimal=',', thousands='.')
    tables_0=tables_0[0]
    tables_0.to_csv("registros_proceso.csv",index=False)
    
    por_recorrer=len(tables_0)
    for g,k in zip(range(0,por_recorrer),tables_0["No. proceso"]):
        
        page.locator(f"button[id='form1:dataTableJuicios2:{g}:btnAbrirMovimientos']").click()
        time.sleep(2)
        def optain_labe(class_selec):
            legends = page.query_selector_all(class_selec)
            labels = []
            for legend in legends:
                labels.append(legend.inner_text())
            return labels

        html_table_1=page.locator("div[id='formJuicioDialogo:juiDetail']").inner_html()
        tables_1 = pd.read_html(html_table_1,decimal=',', thousands='.')
        
        tables_1=tables_1[1][1:][["No. de Ingreso","Fecha"]]
        counter = 1
        odd_rows = []
        for index, row in tables_1.iterrows():
            if counter % 2 != 0:
                odd_rows.append(row)
            counter += 1

        tables_1 = pd.DataFrame(odd_rows)
        print(tables_1)
        # tables_1.to_csv("movimientos_proceso.csv",index=False)
        tables_1["headers"]=optain_labe(".ui-datatable-subtable-header")
        lista_datos=optain_labe("dl[id^='formJuicioDialogo:dataTableMovimiento:']")
        counter = 1
        ofendidos=[]
        demandados=[]
        for i in lista_datos:
            if counter % 2 != 0:
                ofendidos.append(i)
            else:
                demandados.append(i)
            counter += 1
        print(ofendidos)
        print(demandados)
        tables_1["Ofendidos"]=ofendidos
        tables_1["demandados"]=demandados
        tables_1["codigo_proceso"]=k
        tables_1.to_csv("movimientos_proceso.csv",index=False)
        
        sub_recorrer=len(tables_1)
        for l,m in zip(range(0,sub_recorrer),tables_1["headers"]):
        
            page.locator(f"button[id^='formJuicioDialogo:dataTableMovimiento:{l}:']").click()
            time.sleep(2)
            dates=optain_labe("tbody[id='formJuicioDetalle:dataTable_data'] td[style='width:9%;text-align: center']")   
            labels=optain_labe(".ui-fieldset-legend")
            contend=optain_labe(".ui-fieldset-content")
            df_v2=pd.DataFrame({"Fecha":dates,"etiquetas":labels,"Contenido":contend})
            df_v2["headers"]=m              
            df_v2["codigo_proceso"]=k
            print(df_v2)
            df_v2.to_csv("detalles_proceso.csv",index=False)
            page.locator("#juicioDetalleDialogo .ui-icon-closethick").click()
            time.sleep(2)
        
        page.locator("div[id='formJuicioDialogo:juicioDialogo'] .ui-icon-closethick").click()
        time.sleep(2)

    time.sleep(10)
    browser.close()

pd.read_csv("registros_proceso.csv")

pd.read_csv("movimientos_proceso.csv")

pd.read_csv("detalles_proceso.csv")
