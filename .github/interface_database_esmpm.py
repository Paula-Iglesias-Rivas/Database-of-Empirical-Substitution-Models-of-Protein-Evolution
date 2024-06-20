import tkinter as tk
from tkinter import ttk
import sqlite3
import webbrowser
import customtkinter as ctk
from tkinter import filedialog
from tkinter import messagebox
import zipfile
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders



#________________________________________VENTANA PRINCIPAL__________________________________________________
# Crear la ventana principal
root = ctk.CTk()
root.title("Database of Empirical Substitution Models of Protein Evolution")
root.geometry('1200x500')

# Crear un Canvas en el que mostrarás los resultados
canvas = tk.Canvas(root)
canvas.pack(fill=tk.BOTH, expand=1)

# Crear un Frame para contener el contenido del Canvas
my_canvas = tk.Frame(canvas, bg='gray90')
my_canvas.pack(fill=tk.BOTH, expand=True)
canvas.create_window((0, 0), window=my_canvas, anchor='nw')

# Configurar una barra de desplazamiento vertical
scroll_y = ttk.Scrollbar(root, orient=tk.VERTICAL, command=canvas.yview)
scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
canvas.configure(yscrollcommand=scroll_y.set)

# Configurar una barra de desplazamiento horizontal si es necesario
scroll_x = ttk.Scrollbar(root, orient=tk.HORIZONTAL, command=canvas.xview)
scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
canvas.configure(xscrollcommand=scroll_x.set)

# Configurar el Canvas para expandirse según la ventana
my_canvas.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

# Ajustar el tamaño del canvas y el marco al cambiar el tamaño de la ventana principal
root.bind("<Configure>", lambda e: canvas.configure(width=e.width, height=e.height))

#_____________________________________OBTENER DATOS________________________________________________________
# Función para consultar la base de datos y mostrar los resultados según los filtros y el orden seleccionado
def consultar_base_de_datos():
    name_model = name_model_entry.get().lower()
    author = author_entry.get().lower()
    date = date_entry.get().lower()
    comments = comments_entry.get().lower()  # Cambio aquí
    taxonomic_group = taxonomic_group_combobox.get().lower()
   

    # Obtener el valor seleccionado en el desplegable 'taxonomic_group'
    taxonomic_group = taxonomic_group_combobox.get().lower()

    # Conectar a la base de datos SQLite
    conn = sqlite3.connect('models.db')
    cursor = conn.cursor()

    # Crear la consulta SQL dinámica en función de los filtros ingresados
    consulta = '''
        SELECT MSA.name AS model, MSA.author AS author, MSA.publication_date AS date,
        MSA.article AS article, MSA.taxonomic_group AS taxonomic_group, MSA.comments AS comments,
        MAT.binary_matrix AS Matrix
        FROM AMINOACID_SUBSTITUTION_MODELS AS MSA
        JOIN SUBSTITUTION_MATRIX AS MAT ON MSA.name = MAT.model_id
        WHERE 1=1
    '''

    # Agregar condiciones según los filtros ingresados (si no están vacíos)
    if name_model:
        consulta += f" AND lower(MSA.name) LIKE '%{name_model}%'"
    if author:
        consulta += f" AND lower(MSA.author) LIKE '%{author}%'"
    if date:
        consulta += f" AND lower(MSA.date) LIKE '%{date}%'"
    if comments:
        consulta += f" AND lower(MSA.comments) LIKE '%{comments}%'"
    if taxonomic_group:
        consulta += f" AND lower(MSA.taxonomic_group) LIKE '%{taxonomic_group}%'"

    # Agregar orden según la columna seleccionada
    columna_orden = columnas_orden_combobox.get()
    if columna_orden:
        consulta += f" ORDER BY {columna_orden} ASC"

    # Ejecutar la consulta SQL
    cursor.execute(consulta)
    
    resultados = cursor.fetchall()
    
    for resultado in resultados:
        # Modificar el valor del enlace para que sea un hipervínculo
        enlace = resultado[3]
        if enlace:
            lista_resultados.insert('', 'end', values=(*resultado[:3], f'<a href="{enlace}">Enlace</a>', *resultado[4:],), tags=('hipervinculo',))
        else:
            lista_resultados.insert('', 'end', values=(*resultado[:3], '', *resultado[4:]))

    # Limpiar la lista de resultados
    lista_resultados.delete(*lista_resultados.get_children())

    # Mostrar los resultados en la lista
    for resultado in resultados:
        lista_resultados.insert('', 'end', values=resultado)

    # Cerrar la conexión a la base de datos
    conn.close()

# Crear una lista de opciones de origen desde la base de datos
def obtener_opciones_taxonomic_group():
    conn = sqlite3.connect('models.db')
    cursor = conn.cursor()
    cursor.execute('SELECT DISTINCT taxonomic_group FROM AMINOACID_SUBSTITUTION_MODELS')
    opciones_taxonomic_group = [row[0] for row in cursor.fetchall()]
    conn.close()
    
    # Agregar al principio de la lista de opciones un conjunto vacío
    opciones_taxonomic_group.insert(0, "")
    
    return opciones_taxonomic_group

# Obtener las opciones de origen
opciones_taxonomic_group = obtener_opciones_taxonomic_group()

#____________________________________________FILTROS___________________________________________________
# Crear un marco en el canvas para los filtros
filtro_marco = tk.Canvas(my_canvas, bg='gray90')
filtro_marco.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

font_style = ('serif', 20)
ctk.CTkLabel(filtro_marco, text="FILTERS", font=font_style).grid(row=0, column=5, padx=10, pady=10)
# Cambiar el tipo de fuente
font_style = ('serif', 12)
# Etiquetas y cuadros de entrada para los filtros
ctk.CTkLabel(filtro_marco, text="Model name:", font=font_style).grid(row=1, column=4, padx=10)
name_model_entry = ctk.CTkEntry(filtro_marco, font=font_style)
name_model_entry.grid(row=1, column=5, padx=10, pady=10)

ctk.CTkLabel(filtro_marco, text="Author/s:", font=font_style).grid(row=2, column=4, padx=10)
author_entry = ctk.CTkEntry(filtro_marco, font=font_style)
author_entry.grid(row=2, column=5, padx=10, pady=10)

ctk.CTkLabel(filtro_marco, text="Publication date:", font=font_style).grid(row=2, column=6, padx=10)
date_entry = ctk.CTkEntry(filtro_marco, font=font_style)
date_entry.grid(row=2, column=7, padx=10, pady=10)

# Etiqueta y lista desplegable para el filtro de taxonomic_group
ctk.CTkLabel(filtro_marco, text="Taxonomic group:", font=font_style).grid(row=1, column=1, padx=10)
taxonomic_group_combobox = ctk.CTkComboBox(filtro_marco, values=opciones_taxonomic_group, font=font_style)
taxonomic_group_combobox.grid(row=1, column=2, padx=10, pady=10)
taxonomic_group_combobox.set("")  # Establecer el desplegable a "todos" por defecto

ctk.CTkLabel(filtro_marco, text="Comments:", font=font_style).grid(row=1, column=6, padx=10)
comments_entry = ctk.CTkEntry(filtro_marco, font=font_style)
comments_entry.grid(row=1, column=7, padx=10, pady=10)

# Botón para consultar la base de datos
consultar_button = ctk.CTkButton(filtro_marco, text="Consult", command=consultar_base_de_datos, bg_color='green', width=10)
consultar_button.grid(row=6, column=4, columnspan=1, pady=10)

# Función para limpiar el filtro y restaurar los resultados taxonomic_groupales
def limpiar_filtro():
    name_model_entry.delete(0, ctk.END)
    author_entry.delete(0, ctk.END)
    date_entry.delete(0, ctk.END)
    taxonomic_group_combobox.set("")
    comments_entry.delete(0, ctk.END)  # Cambio aquí
    consultar_base_de_datos()

limpiar_filtro_button = ctk.CTkButton(filtro_marco, text="Clear", command=limpiar_filtro, bg_color='green', width=10)
limpiar_filtro_button.grid(row=6, column=3, pady=10)


#__________________________________RESULTADOS______________________________________________________________
# Crear un marco para contener tanto la lista de resultados 
contenedor_resultados_checkboxes = tk.Frame(my_canvas, bg='gray90')
contenedor_resultados_checkboxes.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

style = ttk.Style()
style.configure("Treeview", rowheight=27)
# Crear el Treeview dentro del marco para la lista de resultados
lista_resultados = ttk.Treeview(contenedor_resultados_checkboxes, columns=( "Model", "Author/s", "Publication date", "Article", "Taxonomic group", "Comments"))
lista_resultados.grid(row=0, column=0, sticky='nsew')

# Configurar las columnas
lista_resultados.heading("#1", text="Model", command=lambda: ordenar_resultados("#1"))
lista_resultados.heading("#2", text="Author/s", command=lambda: ordenar_resultados("#2"))
lista_resultados.heading("#3", text="Publication date", command=lambda: ordenar_resultados("#3"))
lista_resultados.heading("#4", text="Article", command=lambda: ordenar_resultados("#4"))
lista_resultados.heading("#5", text="Taxonomic group", command=lambda: ordenar_resultados("#5"))
lista_resultados.heading("#6", text="Comments", command=lambda: ordenar_resultados("#6"))

# Alinear las columnas
lista_resultados.column("#1", anchor="w")
lista_resultados.column("#2", anchor="w")
lista_resultados.column("#3", anchor="w")
lista_resultados.column("#4", anchor="w")
lista_resultados.column("#5", anchor="w")
lista_resultados.column("#6", anchor="w")


# Mostrar la lista de resultados
lista_resultados.grid(row=0, column=0, padx=5, pady=5)

# Función para obtener la lista de modelos desde la base de datos
def obtener_modelos_desde_base_de_datos():
    # Conectar a la base de datos SQLite
    conn = sqlite3.connect('models.db')
    cursor = conn.cursor()

    # Realizar una consulta SQL para obtener los nombres de los modelos
    cursor.execute('SELECT name FROM AMINOACID_SUBSTITUTION_MODELS')

    # Obtener los resultados de la consulta
    resultados = cursor.fetchall()

    # Cerrar la conexión a la base de datos
    conn.close()

    # Obtener una lista de nombres de modelos desde los resultados
    modelos = [resultado[0] for resultado in resultados]

    return modelos

# Llamar a la función para obtener la lista de modelos
modelos = obtener_modelos_desde_base_de_datos()

    
#_____________________________________DESCARGAR SELECCIÓN/SELECCIONAR TODO_______________________________
import zipfile
from tkinter import messagebox

# Función para descargar elementos marcados
def descargar_seleccionados():
    selected_items = lista_resultados.selection()
    
    if not selected_items:
        messagebox.showinfo("Sin selección", "No hay elementos seleccionados para descargar.")
        return

    # Nombre del archivo ZIP
    zip_filename = "matrices_seleccionadas.zip"

    with zipfile.ZipFile(zip_filename, "w", zipfile.ZIP_DEFLATED) as zipf:
        for item in selected_items:
            modelo = lista_resultados.item(item, 'values')[0]
            matriz = lista_resultados.item(item, 'values')[6]
            if modelo and matriz:
                # Agregar la matriz al archivo ZIP
                zipf.writestr(f"{modelo}.txt", str(matriz))  # Convertir matriz a str si no lo es

    messagebox.showinfo("Descarga Completada", f"Las matrices seleccionadas han sido comprimidas en {zip_filename}.")

# Función para seleccionar todos los elementos
def seleccionar_todos():
    items = lista_resultados.get_children()
    selected_items = lista_resultados.selection()
    
    if len(selected_items) == len(items):
        # Si todos los elementos están seleccionados, deselecciona todo
        lista_resultados.selection_remove(*selected_items)
    else:
        # Si no todos los elementos están seleccionados, selecciona todo
        lista_resultados.selection_add(*items)

# Crear botones para descargar elementos marcados y seleccionar/deseleccionar todo
descargar_seleccionados_button = ctk.CTkButton(root, text="Download Selected", command=descargar_seleccionados, bg_color='green', width=15)
descargar_seleccionados_button.pack()

seleccionar_todo_button = ctk.CTkButton(root, text="Select/Deselect All", command=seleccionar_todos, bg_color='green', width=20)
seleccionar_todo_button.pack()

#______________________________________ORDENAR__________________________________________________
# Opciones para el orden
ctk.CTkLabel(filtro_marco, text="Filters:", font=font_style).grid(row=2, column=1, padx=10)
columnas_orden = ["Model", "Author", "Date", "Article", "Taxonomic group", "comments"]
columnas_orden_combobox = ttk.Combobox(filtro_marco, values=columnas_orden, font=font_style)
columnas_orden_combobox.grid(row=2, column=2, padx=10)
columnas_orden_combobox.set("")  # Dejar sin selección inicial

# Función para ordenar los resultados según una columna
def ordenar_resultados(columna):
    # Obtener la dirección de orden (ASC o DESC)
    direccion_orden = "ASC"
    if lista_resultados.heading(columna, "text") == columna and columna != "":
        direccion_orden = "DESC"

    # Actualizar el encabezado de la columna para mostrar la dirección de orden
    for col in columnas_orden:
        lista_resultados.heading(col, text=col)
    lista_resultados.heading(columna, text=f"{columna} {direccion_orden}")
    if columna == 'taxonomic_group':
        # Cuando ordenas por "Taxonomic group", debes utilizar "taxonomic_group" en la consulta
            columnas_orden = "taxonomic_group"
    else:
            columnas_orden = columna
    # Ejecutar la consulta de nuevo con el orden seleccionado
    consultar_base_de_datos()
#______________________________________HIPERVÍNCULO_________________________________
# Variable para almacenar el índice del último clic y el último enlace abierto
last_click_index = None
last_opened_link = None

# Función para abrir el enlace cuando se hace clic derecho en la fila seleccionada
def open_link(event):
    global last_click_index
    item = lista_resultados.identify_row(event.y)  # Identificar la fila en la que se hizo clic

    if item:
        column = lista_resultados.identify_column(event.x)
        enlace = lista_resultados.item(item, 'values')[3]

        if enlace and column == "#4":
            webbrowser.open_new(enlace)

# Detectar la selección de una fila con el clic izquierdo
def on_select(event):
    item = lista_resultados.identify_row(event.y)  # Identificar la fila seleccionada
    global last_click_index

    if item:
        last_click_index = item

# Asociar la función open_link al evento de clic derecho en el Canvas
lista_resultados.bind("<Button-3>", open_link)

# Asociar la función on_select al evento de selección de fila
lista_resultados.bind("<Button-1>", on_select)

# Ejecutar la consulta inicial al abrir la aplicación
consultar_base_de_datos()

#______________________________________________ABRIR MATRIZ y DESCARGARLA__________________________
def mostrar_matriz(modelo, matriz):
    ventana_matriz = tk.Toplevel(root)
    ventana_matriz.title(f"Matrix for Model: {modelo}")

    # Crear un widget de texto para mostrar el contenido de la matriz
    texto_matriz = tk.Text(ventana_matriz, wrap=tk.WORD, height=30, width=200)
    texto_matriz.pack()
    texto_matriz.insert(tk.END, matriz)

    # Agregar un botón en la ventana para descargar la matriz
    def descargar():
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
        if file_path:
            with open(file_path, 'w') as archivo:
                archivo.write(matriz)
            messagebox.showinfo("Descarga Completada", f"La matriz para {modelo} ha sido descargada con éxito.")

    boton_descargar = tk.Button(ventana_matriz, text="Download", command=descargar)
    boton_descargar.pack()
# Asociar la función para mostrar la matriz con un doble clic en la lista
lista_resultados.bind("<Double-1>", lambda event: mostrar_matriz(lista_resultados.item(lista_resultados.selection())["values"][0], lista_resultados.item(lista_resultados.selection())["values"][6]))

#___________________________________________AÑADIR INFORMACIÓN_____________________________________________
# Configuración del servidor SMTP de Outlook
smtp_server = "smtp.office365.com"
smtp_port = 587  # Puerto para STARTTLS
smtp_username = "p.rivas@udc.es"
smtp_password = "34433443Pau:)"

# Variables globales para almacenar los datos ingresados por el usuario
autor_var = None
fecha_publicacion_var = None
enlace_articulo_var = None
comentarios_var = None
nombre_archivo_label= None

def cargar_archivo():
    global nombre_archivo_label
    file_path = filedialog.askopenfilename()
    if file_path:
        with open(file_path, 'r') as archivo:
            contenido = archivo.read()
        
        # Inicializar la etiqueta si no se ha hecho antes
        if nombre_archivo_label is None:
            nombre_archivo_label = tk.Label(root, text="")
            nombre_archivo_label.grid(row=5, column=0, columnspan=2, pady=10)

        # Actualizar la etiqueta con el nombre del archivo
        nombre_archivo_label.config(text=f"Archivo cargado: {file_path}")
        nombre_archivo_label.bind("<Button-1>", lambda event, path=file_path: descargar_archivo(path))


def descargar_archivo(archivo_path):
    # Implementa la lógica para descargar el archivo nuevamente
    # En este ejemplo, simplemente imprime el nombre del archivo
    print(f"Descargando archivo: {archivo_path}")

def agregar_nuevo_modelo():
    global autor_var, fecha_publicacion_var, enlace_articulo_var, comentarios_var
    ventana_nuevo_modelo = tk.Toplevel(root)
    ventana_nuevo_modelo.title("Add New Model")
    
    # Variables para almacenar los datos ingresados por el usuario
    autor_var = tk.StringVar()
    fecha_publicacion_var = tk.StringVar()
    enlace_articulo_var = tk.StringVar()
    comentarios_var = tk.StringVar()

    # Etiquetas y cuadros de entrada en la nueva ventana
    ctk.CTkLabel(ventana_nuevo_modelo, text="Autor:").grid(row=0, column=0, padx=10, pady=10, sticky="e")
    autor_entry = ctk.CTkEntry(ventana_nuevo_modelo, textvariable=autor_var)
    autor_entry.grid(row=0, column=1, padx=10, pady=10)

    ctk.CTkLabel(ventana_nuevo_modelo, text="Fecha de Publicación:").grid(row=1, column=0, padx=10, pady=10, sticky="e")
    fecha_publicacion_entry = ctk.CTkEntry(ventana_nuevo_modelo, textvariable=fecha_publicacion_var)
    fecha_publicacion_entry.grid(row=1, column=1, padx=10, pady=10)

    ctk.CTkLabel(ventana_nuevo_modelo, text="Enlace al Artículo:").grid(row=2, column=0, padx=10, pady=10, sticky="e")
    enlace_articulo_entry = ctk.CTkEntry(ventana_nuevo_modelo, textvariable=enlace_articulo_var)
    enlace_articulo_entry.grid(row=2, column=1, padx=10, pady=10)

    ctk.CTkLabel(ventana_nuevo_modelo, text="Comentarios:").grid(row=3, column=0, padx=10, pady=10, sticky="e")
    comentarios_entry = ctk.CTkEntry(ventana_nuevo_modelo, textvariable=comentarios_var)
    comentarios_entry.grid(row=3, column=1, padx=10, pady=10)

    # Botón para cargar el archivo de texto
    cargar_archivo_button = ctk.CTkButton(ventana_nuevo_modelo, text="Cargar Archivo", command=cargar_archivo, bg_color='green', width=15)
    cargar_archivo_button.grid(row=4, column=0, pady=10, sticky="w")

    # Botón para guardar y enviar el correo
    guardar_button = ctk.CTkButton(ventana_nuevo_modelo, text="Guardar", command=lambda: enviar_correo(autor_entry, fecha_publicacion_entry, enlace_articulo_entry, comentarios_entry), bg_color='green', width=10)
    guardar_button.grid(row=4, column=1, pady=10, sticky="e")

def enviar_correo(autor_entry, fecha_publicacion_entry, enlace_articulo_entry, comentarios_entry):
    # Obtener los datos ingresados por el usuario
    autor = autor_entry.get()
    fecha_publicacion = fecha_publicacion_entry.get()
    enlace_articulo = enlace_articulo_entry.get()
    comentarios = comentarios_entry.get()

    # Aquí deberías manejar la carga del archivo de texto
    archivo_texto = cargar_archivo()

    # Crear y configurar el objeto servidor SMTP
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()  # Usar STARTTLS para seguridad

    # Iniciar sesión en el servidor
    server.login(smtp_username, smtp_password.encode('utf-8'))

    # Crear mensaje de correo electrónico
    msg = MIMEMultipart()
    msg['From'] = smtp_username
    msg['To'] = "p.rivas@udc.es"  # Cambia esto al destinatario correcto
    msg['Subject'] = "Nuevo modelo de aminoácidos"

    # Cuerpo del mensaje
    body = f"""
    Nuevo modelo de aminoácidos agregado.
    Detalles:
    Autor: {autor}
    Fecha de publicación: {fecha_publicacion}
    Enlace al artículo: {enlace_articulo}
    Comentarios: {comentarios}
    """
    msg.attach(MIMEText(body, 'plain'))

    # Adjuntar el archivo
    if archivo_texto:
        archivo_adjunto = MIMEBase('application', 'octet-stream')
        archivo_adjunto.set_payload(archivo_texto)
        encoders.encode_base64(archivo_adjunto)
        archivo_adjunto.add_header('Content-Disposition', f'attachment; filename=archivo_adjunto')

        msg.attach(archivo_adjunto)

    # Enviar el mensaje
    server.sendmail(smtp_username, "p.rivas@udc.es", msg.as_string())

    # Cerrar la conexión
    server.quit()


# Crear un botón "add" en la ventana principal
add_button = ctk.CTkButton(filtro_marco, text="Add new model", command=agregar_nuevo_modelo, bg_color='green', width=10)
add_button.grid(row=6, column=9, pady=10)

root.mainloop()