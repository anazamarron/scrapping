
# coding: utf-8

## CNMV - Información sobre el salario de los consejeros de las empresas

# Esta información se extrae de una página de la CNMV, los enlaces que se generan son dinámicos y caducan con el tiempo por lo que hay que hacer el proceso de toda la navegación para obtener los enlaces que serviran para cada descarga

# In[1]:

import mechanize
import cookielib
import ssl
import urllib
import urllib2
import tempfile
from lxml import html,etree
from bs4 import BeautifulSoup
from cStringIO import StringIO
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.converter import HTMLConverter
from pdfminer.converter import XMLConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from pyPdf import PdfFileWriter, PdfFileReader
import re
import subprocess
import glob
import pandas as pd
import numpy as np



### HOla caracola

# In[2]:


if hasattr(ssl, '_create_unverified_context'):
    ssl._create_default_https_context = ssl._create_unverified_context


url_CNMV = "https://www.cnmv.es/Portal/Consultas/EE/InformacionGobCorp.aspx?TipoInforme=6&pageIRC="


# In[3]:

i=0
for j in range(0,9):
    browser = mechanize.Browser(factory=mechanize.RobustFactory())
    browser.set_handle_robots(False)
    browser.set_handle_equiv(False)
    url_a_usar = url_CNMV + str(j)
    page = browser.open(url_a_usar)
    htmlcontent = page.read()
    soup = BeautifulSoup(htmlcontent)

    
    for elm in  soup.find_all('table'):
        for a_elm in elm.find_all("a"):
            if i%2!=0:
                href = (a_elm.attrs["href"])
                url = "https://www.cnmv.es/Portal/" + href[6:len(href)]
                print url
                response = urllib2.urlopen(url)
                nombre_fichero = "document_" + str(i) + ".pdf"
                file = open("pdfs/total/" + nombre_fichero, 'wb')
                file.write(response.read())
                file.close()
                print("Completed")
                
            i+=1
        


# In[4]:

def ConvertPDFToText(currentPDF):
    pdfData = currentPDF.read()

    tf = tempfile.NamedTemporaryFile()
    tf.write(pdfData)
    tf.seek(0)

    outputTf = tempfile.NamedTemporaryFile()
    

    if (len(pdfData) > 0) :
        out, err = subprocess.Popen(["pdftotext", "-layout", tf.name, outputTf.name ]).communicate()
        return outputTf.read()
    else :
        return None


##### Tabla de Retribuciones

# In[5]:

def convert(fname, pages=None):
    if not pages:
        pagenums = set()
    else:
        pagenums = set(pages)

    output = StringIO()
    manager = PDFResourceManager()
    converter = TextConverter(manager, output, laparams=LAParams())
    interpreter = PDFPageInterpreter(manager, converter)

    infile = open(fname, 'rb')
    
    for page in PDFPage.get_pages(infile, pagenums):
        interpreter.process_page(page)
    
    infile.close()
    converter.close()
    text = output.getvalue()
    output.close
    return text


# In[6]:

def obtenNombreEmpresa(file_prueba):
    inputpdf = PdfFileReader(open(file_prueba, "rb"))
    encontrado1 = False
    encontrado2 = False
    salir = False
    nombre_empresa= ""
    for i in range (0,3):
        texto = convert(file_prueba,[i])
        texto = texto.split('\n')
        
        for line in texto:
            if encontrado1 and encontrado2:
                nombre_empresa = line
                
                salir = True
                break
            if encontrado1:
                encontrado2= True
            if re.search('DENOMINACI(.)+N SOCIAL',line):
                encontrado1 = True
        if salir:
            break
    return nombre_empresa



# In[7]:

# Esta función busca en el pdf la expresión regular que coincide con el inicio de la tabla
# que necesitamos y crea un txt con la misma.

def obten_txt_total_retribuciones(file_prueba,nombre_empresa):
    
    inputpdf = PdfFileReader(open(file_prueba, "rb"))
    continua = False
    
    
    num_pages = inputpdf.getNumPages()
    
    for i in range (7,num_pages-1):
        texto = convert(file_prueba,[i])
        
        if re.search ('Resumen de las retribuciones \(en miles de (.)+\)',texto):
            output = PdfFileWriter()

            if(re.search('ejercicio',texto)):

                output.addPage(inputpdf.getPage(i))
                if not re.search('Sistemas de retribuci',texto):
                    tabla =convert(file_prueba,[i+1])
                    output.addPage(inputpdf.getPage(i+1))

            else:
                tabla =convert(file_prueba,[i+1])
                output.addPage(inputpdf.getPage(i+1))

                if not re.search('Sistemas de retribuci',texto):
                    tabla =convert(file_prueba,[i+2])
                    output.addPage(inputpdf.getPage(i+2))
            
                        
            # creo un pdf con el contenido de la tabla que buscamos únicamente. 
            # En general guardo 2 páginas, por lo que he llamado 2paginas a la carpta
            nombre_fichero = "pdfs/2paginas/" +  nombre_empresa + ".pdf"
            print output
            print nombre_fichero
            
            with open(nombre_fichero, "wb") as outputStream:
                output.write(outputStream)
            
            # ahora abro el documento que acabo de guardar, porque quiero crear un txt 
            # con el contenido
            mi_pdf = open(nombre_fichero)    
            mi_txt = ConvertPDFToText(mi_pdf)
            mi_pdf.close()
            #y lo devuelvo
            return mi_txt
            break
       
    



# In[299]:

pdfs = glob.glob('pdfs/total/*.pdf')

##itero sobre los pdfs
#pdfs = ['pdfs/total/document_193.pdf']

for pdf in pdfs:

    
    try:
        nombre_empresa = obtenNombreEmpresa(pdf)
        print nombre_empresa
        print pdf
        texto= obten_txt_total_retribuciones(pdf,nombre_empresa)

        #print "Bien:", nombre_empresa
        txt_guardar = 'pdfs/2paginas/' + nombre_empresa + ".txt"
        text_file = open(txt_guardar, "wb")
        text_file.write(texto)
        text_file.close()
    except Exception,e:
        #Dan error de lectura, así que le cambio los permisos con un comando de linux
        nombre_mover = pdf + ".old"
        mvcommand = ['mv', pdf, nombre_mover]
        gsProc = subprocess.call(mvcommand)
        
        print "MAL"
        print "pdf: ", pdf
        print "error:", str(e)
        

print "FIN"







# In[9]:

olds = glob.glob('pdfs/total/*.old')

#Vamos a ver si podemos hacer algo con los que han fallado. Pinto el comando que tengo que ejecutar en la consola
for old in olds:
    nombre_nuevo =  old + ".new.pdf"        
    print 'gs','-q', '-dNOPAUSE', '-dBATCH', '-sDEVICE=pdfwrite', '-sOutputFile=%stdout%' ,'-c', '.setpdfwrite', '-f', old ,'>', nombre_nuevo
    
    #error = gsProc.communicate()[0]

    
#copiar el resultado y pegarlo en la línea de comandos, porque no he conseguido hacerlo desde aquí


# In[11]:

#Saco los que me dieron error y que he modificado sus permisos y repito el proceso
pdfs = glob.glob('pdfs/total/*.old.new.pdf')

##itero sobre los pdfs
#pdfs = ['pdfs/total/document_193.pdf']

for pdf in pdfs:

    
    try:
        nombre_empresa = obtenNombreEmpresa(pdf)
        print nombre_empresa

        texto= obten_txt_total_retribuciones(pdf,nombre_empresa)
        #print "Bien:", nombre_empresa
        txt_guardar = 'pdfs/2paginas/' + nombre_empresa + ".txt"
        text_file = open(txt_guardar, "wb")
        text_file.write(texto)
        text_file.close()
    except Exception,e:
        #Dan error de lectura, así que le cambio los permisos con un comando de linux
        nombre_mover = pdf + ".old"
        mvcommand = ['mv', pdf, nombre_mover]
        gsProc = subprocess.call(mvcommand)
        print ""
        print "******"
        print "MAL"
        print "pdf: ", pdf
        print "error:", str(e)
        print "*****"
        print ""
        

print "FIN"







# In[12]:

#Voy a crearme los objetos que almacenarán el contenido de las tablas
nombre_empresa = []
consejero = []
sociedad_total_metalico = []
sociedad_acciones_otorgadas =[]
sociedad_acciones_ejecutadas = []
sociedad_total = []
otras_total_metalico = []
otras_acciones_otorgadas =[]
otras_acciones_ejecutadas = []
otras_total = []
total_2014=[]
total_2013=[]
aportaciones_ahorro=[]

#Este dataframe será la tabla final
retribuciones2 = pd.DataFrame()

#Itero sobre los txts que me he creado anteriormente
txts = glob.glob('pdfs/2paginas/*.txt')
print len(txts)
for txt in txts:
    start = False
    infile = open(txt, 'r')
    nombre = txt.split("/")
    empresa = nombre[2]
    empresa = empresa[:len(empresa)-4]
    print empresa
    for line in infile.readlines():
        
        if start:
            
            mach1 = re.findall('^Nombre',line.strip())
            mach2 = re.findall('^TOTAL', line.strip())
            if len(mach2)>0 or len(mach1)>0:
               
                start = False
            else:
                if len(line.replace(" ", ""))>10:
                    campos = line.split("  ")
                    campos = filter(None, campos)
    
                    for i in range(0, len(campos)):
                        campos[i] = campos[i].strip()
                    
                    if len(campos)== 12:
                        nombre_empresa.append(empresa)
                        consejero.append(campos[0])
                        sociedad_total_metalico.append(campos[1])
                        sociedad_acciones_otorgadas.append(campos[2])
                        sociedad_acciones_ejecutadas.append(campos[3])
                        sociedad_total.append(campos[4])
                        otras_total_metalico.append(campos[5])
                        otras_acciones_otorgadas.append(campos[6])
                        otras_acciones_ejecutadas.append(campos[7])
                        otras_total.append(campos[8])
                        total_2014.append(campos[9])
                        total_2013.append(campos[10])
                        aportaciones_ahorro.append(campos[11])
                    else:
                        if len(campos)== 11:
                            nombre_empresa.append(empresa)
                            consejero.append(campos[0])
                            sociedad_total_metalico.append(campos[1])
                            sociedad_acciones_otorgadas.append(campos[2])
                            sociedad_acciones_ejecutadas.append(campos[3])
                            sociedad_total.append(campos[4])
                            otras_total_metalico.append(campos[5])
                            otras_acciones_otorgadas.append(campos[6])
                            otras_acciones_ejecutadas.append(campos[7])
                            otras_total.append(campos[8])
                            total_2014.append(campos[9])
                            total_2013.append('0')
                            aportaciones_ahorro.append(campos[10])                
                        else:
                            print "este da error: ", empresa, "->", campos
        else:
            mach = re.findall('^ejercicio',line.strip())
            if len(mach)>0:
                start= True
                #consejeros.append(mach)
                #fila_c = fila
retribuciones2["nombre_empresa"] = nombre_empresa
retribuciones2["consejero"] = consejero
retribuciones2["sociedad_total_metalico"] = sociedad_total_metalico
retribuciones2["sociedad_acciones_otorgadas"] = sociedad_acciones_otorgadas
retribuciones2["sociedad_acciones_ejecutadas"] = sociedad_acciones_ejecutadas
retribuciones2["sociedad_total"] = sociedad_total
retribuciones2["otras_total_metalico"] = otras_total_metalico
retribuciones2["otras_acciones_otorgadas"] = otras_acciones_otorgadas
retribuciones2["otras_acciones_ejecutadas"] = otras_acciones_ejecutadas
retribuciones2["otras_total"] = otras_total
retribuciones2["total_2014"] = total_2014
retribuciones2["total_2013"] = total_2013
retribuciones2["aportaciones_ahorro"] = aportaciones_ahorro


retribuciones2.to_csv("retribuciones_final_total.csv")


# In[13]:

print (retribuciones2.nombre_empresa.unique())


# In[14]:

print retribuciones2[retribuciones2.nombre_empresa=='IBERDROLA, S.A.']


# In[305]:

#gs -q -dNOPAUSE -dBATCH -sDEVICE=pdfwrite -sOutputFile=%stdout% -c .setpdfwrite -f document_29.pdf > document_29_new.pdf
#mv document_29.pdf document_29.old


# In[15]:

print len(retribuciones2.nombre_empresa.unique())


# In[ ]:



