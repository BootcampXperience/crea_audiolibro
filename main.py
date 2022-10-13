import cv2
import pytesseract
from deep_translator import GoogleTranslator
import os
from tkinter import *
from PIL import ImageTk,Image  
from tkinter import ttk
import glob
import time
import re
pytesseract.pytesseract.tesseract_cmd = r'/opt/homebrew/bin/tesseract'
window = Tk()
paginas = []
indice = 0
idioma_traduccion = 'Frances'
window.title('AudioBook Converter')
window.geometry("1920x1080")

def siguiente():
    global indice
    global paginas
    if indice < (len(paginas)-1):
        resultado.configure(text='')
        indice+=1
        picture = Image.open(paginas[indice])
        picture = picture.resize((570, 700))
        img = ImageTk.PhotoImage(picture)
        image_widget.configure(image=img)
        image_widget.image = img
        if indice == (len(paginas)-1):
            titulo.config(text = 'Final')
        else:
            titulo.config(text = 'Pag ' + re.search('/pag(.*).jpg', paginas[indice]).group(1))

def anterior():
    global indice
    global paginas
    if indice > 0:
        resultado.configure(text='')
        indice-=1
        picture = Image.open(paginas[indice])
        picture = picture.resize((570, 700))
        img = ImageTk.PhotoImage(picture)
        image_widget.configure(image=img)
        image_widget.image = img
        if indice == 0:
            titulo.config(text = 'Portada')
        else:
            titulo.config(text = 'Pag ' + re.search('/pag(.*).jpg', paginas[indice]).group(1))

def cambio_idioma(event):
    global idioma_traduccion
    if idioma.get() != idioma_traduccion:
        resultado.configure(text='')
    idioma_traduccion = idioma.get()
    
def replace(texto):
    texto = texto.replace('tragique, ne', 'tragique, la vie')
    texto = texto.replace('monotoni n', 'monotonie et')
    texto = texto.replace(' u _', ' une')
    texto = texto.replace(' cou ;', ' court')
    texto = texto.replace('I1 ', 'Il ')
    texto = texto.replace(' Je', ' le')
    texto = texto.replace(' diserétion ', ' discrétion ')
    texto = texto.replace(' Jes', ' les')
    texto = texto.replace(' q un', ''' d'un''')
    texto = texto.replace('LEt ', 'Et ')
    texto = texto.replace(' mol', ' moi')
    texto = texto.replace(' Alan ', ' allant ')
    return texto

def dividir_texto(texto):
    contador = 0
    texto_final = ''
    for palabra in texto.split():
        contador=contador+len(palabra)
        texto_final=texto_final+palabra+' '
        if contador>48:
            texto_final=texto_final+'\n'
            contador = 0
    return texto_final
    
def traducir():
    global paginas
    global indice
    global idioma_traduccion
    resultado.configure(text='')
    texto_final = ''
    contador=0    
    if idioma_traduccion == 'Ingles': translator = GoogleTranslator(source='fr', target='en')
    if idioma_traduccion == 'Portugues': translator = GoogleTranslator(source='fr', target='pt')
    if idioma_traduccion == 'Español': translator = GoogleTranslator(source='fr', target='es')
    if idioma_traduccion == 'Frances': translator = GoogleTranslator(source='fr', target='fr')
        
    img = cv2.imread(paginas[indice])
    img = cv2.resize(img, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
    img = cv2.medianBlur(img,1)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    thresh1 = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY_INV)[1]
    rect_kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (100, 100))
    dilation = cv2.dilate(thresh1, rect_kernel, iterations = 1)
    contours, hierarchy = cv2.findContours(dilation, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    
    for cnt in contours[::-1]:
        x, y, w, h = cv2.boundingRect(cnt)
        cropped = thresh1[y:y + h, x:x + w]
        config = ('-l fra --oem 1 --psm 6')
        text = pytesseract.image_to_string(cropped, config=config)
        text = text.replace('\n',' ')
        if text != '':
            traduzido = translator.translate(replace(text))
            traduzido = dividir_texto(traduzido)
            if contador>0:
                texto_final = texto_final + '\n\n' + traduzido
            else:
                texto_final = texto_final + '\n' + traduzido
            resultado.configure(text=texto_final)
            contador+=1

def escuchar():
    global idioma_traduccion
    if resultado.cget('text') != '':
        for linea in resultado.cget('text').split('\n\n'):
            time.sleep(1)
            result = " ".join(line.strip() for line in linea.splitlines())
            result = result.replace("'", "")            
            result = result.replace("-", "")
            result = result.replace("|", "")
            result = result.replace('''"''', "")
            if idioma_traduccion == 'Ingles': os.system("say -r 150 -v Alex " + result) 
            if idioma_traduccion == 'Portugues': os.system("say -r 150 -v Luciana " + result)
            if idioma_traduccion == 'Español': os.system("say -r 150 -v Juan " + result)
            if idioma_traduccion == 'Frances': os.system("say -r 150 -v Thomas " + result)
    
paginas = glob.glob("/Users/alejandro/Documents/traductor_libros/*.jpg")
paginas.sort()

picture = Image.open(paginas[indice])
picture = picture.resize((570, 700))
img = ImageTk.PhotoImage(picture)
image_widget = Label(window, image=img)
image_widget.place(x=50, y=50)

titulo = Label(window, text='Portada', font=("Arial", 18))
titulo.pack()
titulo.place(x=300, y=20)

button_next = Button(window, text='Siguiente', command=siguiente)
button_next.pack()
button_next.place(x=530, y=20)

button_anterior = Button(window, text='Anterior', command=anterior)
button_anterior.pack()
button_anterior.place(x=50, y=20)

resultado = Label(window, text='', font=("Arial", 17), bg="white", justify='left')
resultado.pack()
resultado.place(x=815, y=50, height=700, width=570)

titulo2 = Label(window, text='Idioma: ', font=("Arial", 16))
titulo2.pack()
titulo2.place(x=1010, y=22)
idioma = ttk.Combobox(window, width=10, font=("Arial", 15), textvariable='Frances')
idioma['values'] = ['Frances', 'Ingles', 'Portugues', 'Español']
idioma['state'] = 'readonly'
idioma.pack()
idioma.place(x=1070, y=23)
idioma.set('Frances')
idioma.bind('<<ComboboxSelected>>', cambio_idioma)

button_traducir = Button(window, font=("Helvetica", 18), text='Traducir', command=traducir)
button_traducir.pack()
button_traducir.place(x=668, y=365)

button_play = Button(window, font=("Helvetica", 18), text='Escuchar', command=escuchar)
button_play.pack()
button_play.place(x=664, y=415)

window.mainloop()