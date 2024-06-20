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



#________________________________________MAIN WINDOW__________________________________________________
# Create main window
root = ctk.CTk()
root.title("Database of Empirical Substitution Models of Protein Evolution")
root.geometry('1200x500')

canvas = tk.Canvas(root)
canvas.pack(fill=tk.BOTH, expand=1)

my_canvas = tk.Frame(canvas, bg='gray90')
my_canvas.pack(fill=tk.BOTH, expand=True)
canvas.create_window((0, 0), window=my_canvas, anchor='nw')

#Scrollbars
scroll_y = ttk.Scrollbar(root, orient=tk.VERTICAL, command=canvas.yview)
scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
canvas.configure(yscrollcommand=scroll_y.set)

scroll_x = ttk.Scrollbar(root, orient=tk.HORIZONTAL, command=canvas.xview)
scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
canvas.configure(xscrollcommand=scroll_x.set)

my_canvas.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

root.bind("<Configure>", lambda e: canvas.configure(width=e.width, height=e.height))

#_____________________________________GET DATA________________________________________________________
def query_database():
    name_model = name_model_entry.get().lower()
    author = author_entry.get().lower()
    date = date_entry.get().lower()
    Comments = Comments_entry.get().lower()  # Cambio aquí
    taxonomic_group = taxonomic_group_combobox.get().lower()
   

    taxonomic_group = taxonomic_group_combobox.get().lower()

    conn = sqlite3.connect('models.db')
    cursor = conn.cursor()

    query = '''
        SELECT MSA.name AS model, MSA.author AS author, MSA.publication_date AS date,
        MSA.article AS article, MSA.taxonomic_group AS taxonomic_group, MSA.Comments AS Comments,
        MAT.binary_matrix AS Matrix
        FROM AMINOACID_SUBSTITUTION_MODELS AS MSA
        JOIN SUBSTITUTION_MATRIX AS MAT ON MSA.name = MAT.model_id
        WHERE 1=1
    '''

    # Add conditions based on entered filters (if not empty)
    if name_model:
        query += f" AND lower(MSA.name) LIKE '%{name_model}%'"
    if author:
        query += f" AND lower(MSA.author) LIKE '%{author}%'"
    if date:
        query += f" AND lower(MSA.date) LIKE '%{date}%'"
    if Comments:
        query += f" AND lower(MSA.Comments) LIKE '%{Comments}%'"
    if taxonomic_group:
        query += f" AND lower(MSA.taxonomic_group) LIKE '%{taxonomic_group}%'"

    order_column = columns_order_comboobox.get()
    if order_column:
        query += f" ORDER BY {order_column} ASC"

    # Ejecutar la query SQL
    cursor.execute(query)
    
    results = cursor.fetchall()
    
    for result in results:
        link = result[3]
        if link:
            results_list.insert('', 'end', values=(*result[:3], f'<a href="{link}">link</a>', *result[4:],), tags=('hipervinculo',))
        else:
            results_list.insert('', 'end', values=(*result[:3], '', *result[4:]))

    results_list.delete(*results_list.get_children())

    for result in results:
        results_list.insert('', 'end', values=result)

    conn.close()

def get_taxonomic_group_options():
    conn = sqlite3.connect('models.db')
    cursor = conn.cursor()
    cursor.execute('SELECT DISTINCT taxonomic_group FROM AMINOACID_SUBSTITUTION_MODELS')
    options = [row[0] for row in cursor.fetchall()]
    conn.close()
    
    options.insert(0, "")
    
    return options

options = get_taxonomic_group_options()

#____________________________________________FILTERS___________________________________________________
filter_frame = tk.Canvas(my_canvas, bg='gray90')
filter_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

font_style = ('serif', 20)
ctk.CTkLabel(filter_frame, text="FILTERS", font=font_style).grid(row=0, column=5, padx=10, pady=10)
# Font style
font_style = ('serif', 12)
# Labels and entry boxes for filters
ctk.CTkLabel(filter_frame, text="Model name:", font=font_style).grid(row=1, column=4, padx=10)
name_model_entry = ctk.CTkEntry(filter_frame, font=font_style)
name_model_entry.grid(row=1, column=5, padx=10, pady=10)

ctk.CTkLabel(filter_frame, text="Author/s:", font=font_style).grid(row=2, column=4, padx=10)
author_entry = ctk.CTkEntry(filter_frame, font=font_style)
author_entry.grid(row=2, column=5, padx=10, pady=10)

ctk.CTkLabel(filter_frame, text="Publication date:", font=font_style).grid(row=2, column=6, padx=10)
date_entry = ctk.CTkEntry(filter_frame, font=font_style)
date_entry.grid(row=2, column=7, padx=10, pady=10)

# Taxonomic_group filter label and combobox
ctk.CTkLabel(filter_frame, text="Taxonomic group:", font=font_style).grid(row=1, column=1, padx=10)
taxonomic_group_combobox = ctk.CTkComboBox(filter_frame, values=options, font=font_style)
taxonomic_group_combobox.grid(row=1, column=2, padx=10, pady=10)
taxonomic_group_combobox.set("")  # Establecer el desplegable a "todos" por defecto

ctk.CTkLabel(filter_frame, text="Comments:", font=font_style).grid(row=1, column=6, padx=10)
Comments_entry = ctk.CTkEntry(filter_frame, font=font_style)
Comments_entry.grid(row=1, column=7, padx=10, pady=10)

# Query buttom
query_button = ctk.CTkButton(filter_frame, text="Consult", command=query_database, bg_color='green', width=10)
query_button.grid(row=6, column=4, columnspan=1, pady=10)

# Función para limpiar el filtro y restaurar los results taxonomic_groupales
def clear_filter():
    name_model_entry.delete(0, ctk.END)
    author_entry.delete(0, ctk.END)
    date_entry.delete(0, ctk.END)
    taxonomic_group_combobox.set("")
    Comments_entry.delete(0, ctk.END)  # Cambio aquí
    query_database()

clear_filter_button = ctk.CTkButton(filter_frame, text="Clear", command=clear_filter, bg_color='green', width=10)
clear_filter_button.grid(row=6, column=3, pady=10)


#__________________________________RESULTS______________________________________________________________
results_frame_checkboxes = tk.Frame(my_canvas, bg='gray90')
results_frame_checkboxes.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

style = ttk.Style()
style.configure("Treeview", rowheight=27)
results_list = ttk.Treeview(results_frame_checkboxes, columns=( "Model", "Author/s", "Publication date", "Article", "Taxonomic group", "Comments"))
results_list.grid(row=0, column=0, sticky='nsew')

# Configure columns
results_list.heading("#1", text="Model", command=lambda: order_results("#1"))
results_list.heading("#2", text="Author/s", command=lambda: order_results("#2"))
results_list.heading("#3", text="Publication date", command=lambda: order_results("#3"))
results_list.heading("#4", text="Article", command=lambda: order_results("#4"))
results_list.heading("#5", text="Taxonomic group", command=lambda: order_results("#5"))
results_list.heading("#6", text="Comments", command=lambda: order_results("#6"))

# Align columns
results_list.column("#1", anchor="w")
results_list.column("#2", anchor="w")
results_list.column("#3", anchor="w")
results_list.column("#4", anchor="w")
results_list.column("#5", anchor="w")
results_list.column("#6", anchor="w")


# Show results list
results_list.grid(row=0, column=0, padx=5, pady=5)

# Function to get models list from database
def get_models_from_database():
    conn = sqlite3.connect('models.db')
    cursor = conn.cursor()

    cursor.execute('SELECT name FROM AMINOACID_SUBSTITUTION_MODELS')

    results = cursor.fetchall()

    conn.close()

    models = [result[0] for result in results]

    return models

models = get_models_from_database()

    
#_____________________________________DOWNLOAD SELECTED MATRIX/SELECT ALL_______________________________

def download_selected_models():
    selected_items = results_list.selection()
    
    if not selected_items:
        messagebox.showwarning("Warning", "No model selected. Please select a model.")
        return
    # Open a file dialog to choose where to save the download
    save_path = filedialog.askdirectory()

    if not save_path:
        return
    # Nombre del file ZIP
    zip_filename = "Selected matrix.zip"

    with zipfile.ZipFile(zip_filename, "w", zipfile.ZIP_DEFLATED) as zipf:
        for item in selected_items:
            model = results_list.item(item, 'values')[0]
            matrix = results_list.item(item, 'values')[6]
            # Save binary matrix as a zip file
            file_path = f'{save_path}/{model}.txt'
            with open(file_path, 'wb') as f:
                f.write(matrix)
    messagebox.showinfo("Success", "Selected models have been downloaded successfully.")

# Función para seleccionar todos los elementos
def seleccionar_todos():
    items = results_list.get_children()
    selected_items = results_list.selection()
    
    if len(selected_items) == len(items):
        results_list.selection_remove(*selected_items)
    else:
        results_list.selection_add(*items)

download_selected_models_button = ctk.CTkButton(root, text="Download Selected", command=download_selected_models, bg_color='green', width=15)
download_selected_models_button.pack()

seleccionar_todo_button = ctk.CTkButton(root, text="Select/Deselect All", command=seleccionar_todos, bg_color='green', width=20)
seleccionar_todo_button.pack()

#______________________________________ORDER__________________________________________________
# Options for sorting
ctk.CTkLabel(filter_frame, text="Filters:", font=font_style).grid(row=2, column=1, padx=10)
columns_order = ["Model", "Author", "Date", "Article", "Taxonomic group", "Comments"]
columns_order_comboobox = ttk.Combobox(filter_frame, values=columns_order, font=font_style)
columns_order_comboobox.grid(row=2, column=2, padx=10)
columns_order_comboobox.set("") 

def order_results(column):
    order_direction = "ASC"
    if results_list.heading(column, "text") == column and column != "":
        order_direction = "DESC"

    for col in columns_order:
        results_list.heading(col, text=col)
    results_list.heading(column, text=f"{column} {order_direction}")
    if column == 'taxonomic_group':
            columns_order = "taxonomic_group"
    else:
            columns_order = column
    query_database()
#______________________________________HIPERLINK_________________________________
last_click_index = None
last_opened_link = None

def open_link(event):
    global last_click_index
    item = results_list.identify_row(event.y)  

    if item:
        column = results_list.identify_column(event.x)
        link = results_list.item(item, 'values')[3]

        if link and column == "#4":
            webbrowser.open_new(link)

def on_select(event):
    item = results_list.identify_row(event.y)  
    global last_click_index

    if item:
        last_click_index = item

results_list.bind("<Button-3>", open_link)

results_list.bind("<Button-1>", on_select)

query_database()

#______________________________________________OPEN MATRIZ AND DOWNLOAD__________________________
def show_matrix(model, matrix):
    matrix_frame = tk.Toplevel(root)
    matrix_frame.title(f"Matrix for Model: {model}")

    matrix_test = tk.Text(matrix_frame, wrap=tk.WORD, height=30, width=200)
    matrix_test.pack()
    matrix_test.insert(tk.END, matrix)

    def download():
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
        if file_path:
            with open(file_path, 'w') as file:
                file.write(matrix)
            messagebox.showinfo("Download Completed", f"The matrix for {model} has been successfully downloaded.")

    download_button = tk.Button(matrix_frame, text="Download", command=download)
    download_button.pack()
results_list.bind("<Double-1>", lambda event: show_matrix(results_list.item(results_list.selection())["values"][0], results_list.item(results_list.selection())["values"][6]))

root.mainloop()
