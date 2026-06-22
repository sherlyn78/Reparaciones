import tkinter as tk
from tkinter import Entry, ttk
import webbrowser
import sqlite3
from xmlrpc import client
from PIL import Image, ImageTk
import random
from datetime import datetime
import win32print
import win32ui
from tkinter import messagebox
import logging
from PIL import Image, ImageTk
logging.basicConfig(filename='errores.log', level=logging.ERROR)



#conecta base de datos 
conn = sqlite3.connect('clientes.db')
cursor = conn.cursor()

# tabla clientes
cursor.execute('''
CREATE TABLE IF NOT EXISTS clientes (
    id INTEGER PRIMARY KEY,
    Atendido_por TEXT,
    cliente TEXT,
    telefono TEXT,
    correo TEXT,
    modelo TEXT,
    numero_serie TEXT,
    problema TEXT,
    repuestos_utilizados TEXT,
    costos TEXT,
    forma_de_pago TEXT,
    notas TEXT
)
''')
conn.commit()

# id cliente
numero_venta_actual = random.randint(1000, 9999)


def obtener_fecha_hora_actual():
    ahora = datetime.now()
    fecha_actual = ahora.strftime("%d/%m/%Y")
    hora_actual = ahora.strftime("%H:%M:%S")
    return fecha_actual, hora_actual

def cerrar_conexion():
    if conn:
        conn.close()
    root.destroy()

#actualizar fecha y hora 
def actualizar_fecha_hora():
    fecha_actual, hora_actual = obtener_fecha_hora_actual()
    label_fecha_hora.config(text=f"    Fecha: {fecha_actual} | Hora: {hora_actual}")
    root.after(60000, actualizar_fecha_hora)  # Actualiza cada 60000 ms (1 minuto)

import sqlite3
import random
import tkinter as tk

def agregar_cliente():
    try:
        id_cliente = random.randint(1000, 9999)
        Atendido_por = entry_atendido_por.get()
        nombre = entry_nombre.get()
        telefono = entry_telefono.get()
        correo = entry_correo.get()
        modelo = entry_modelo.get()
        numero_serie = entry_numero_serie.get()
        problema = text_problema.get("1.0", "end-1c")
        repuestos_utilizados = text_repuestos_utilizados.get("1.0", "end-1c")
        costos = entry_costos.get()
        forma_de_pago = entry_forma_de_pago.get()
        notas = text_notas.get("1.0", "end-1c")

        if not nombre or not correo:
            print("Error: Nombre y correo son obligatorios.")
            return

        cursor.execute('''
        INSERT INTO clientes (id, Atendido_por, cliente, telefono, correo, modelo, numero_serie, problema, 
                              repuestos_utilizados, costos, forma_de_pago, notas)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (id_cliente, Atendido_por, nombre, telefono, correo, modelo, numero_serie, problema, repuestos_utilizados, costos, forma_de_pago, notas))

        conn.commit()
        print(f"Cliente agregado correctamente con ID {id_cliente}.")
        actualizar_lista()

    except sqlite3.Error as e:
        print(f"Error en la base de datos: {e}")



# Función para actualizar la lista de clientes
def actualizar_lista():
    for row in treeview.get_children():
        treeview.delete(row)
    cursor.execute("SELECT * FROM clientes")
    for row in cursor.fetchall():
        treeview.insert('', 'end', values=row)

#eliminar cliente
def eliminar_cliente():
    try:
        selected_item = treeview.selection()[0]
        cliente_id = treeview.item(selected_item)['values'][0]
        cursor.execute("DELETE FROM clientes WHERE id = ?", (cliente_id,))
        conn.commit()
        actualizar_lista()
    except IndexError:
        print("Error: No se seleccionó ningún cliente.")
 #_____________________________________________________________________________________duplicadpo       
def buscar_cliente():
    query = Entry.get().strip().lower()
    resultados = [cliente for cliente in client if query in cliente['nombre'].lower()]
    
    if resultados:
        resultado_texto = "\n".join([f"{cliente['nombre']} - {cliente['email']}" for cliente in resultados])
        messagebox.showinfo("Resultados", resultado_texto)
    else:
        messagebox.showinfo("Resultados", "No se encontraron clientes.")
#_____________________________________________________________________________________duplicado

# Función para cerrar la conexión
def cerrar_conexion():
    conn.close()
    root.destroy()
    

#_____________________________________________________________________________________pendiente error al buscar
# Función para buscar cliente
def buscar_cliente():
    query = entry_buscar.get().strip().lower()
    if query:  # Asegurarse de que el campo no esté vacío
        treeview.delete(*treeview.get_children())  # Limpiar la tabla actual
        cursor.execute("SELECT * FROM clientes WHERE LOWER(cliente) LIKE ?", ('%' + query + '%',))
        resultados = cursor.fetchall()
        if resultados:
            for row in resultados:
                treeview.insert('', 'end', values=row)
        else:
            messagebox.showinfo("Resultados", "No se encontraron clientes.")
    else:
        messagebox.showwarning("Advertencia", "Por favor, ingrese un nombre para buscar.")
#_____________________________________________________________________________________pendiente error al buscar

# Función para editar un cliente
def editar_cliente():
    try:
        # Obtener el cliente seleccionado
        selected_item = treeview.selection()[0]
        cliente_data = treeview.item(selected_item)['values']
        cliente_id = cliente_data[0]  # Asumimos que el ID está en la primera columna

        # Crear ventana emergente para edición
        popup = tk.Toplevel(root)
        popup.title("Editar Cliente")
        popup.geometry("400x600")

        # Campos para editar
        fields = [
            "Atendido_por", "Cliente", "Teléfono", "Correo",
            "Modelo", "Número de Serie", "Problema",
            "Repuestos Utilizados", "Costos", "Forma de Pago", "Notas"
        ]
        entries = {}

        for i, field in enumerate(fields):
            tk.Label(popup, text=field).grid(row=i, column=0, pady=5, sticky="w")
            if field in ["Problema", "Repuestos Utilizados", "Notas"]:
                text = tk.Text(popup, width=40, height=4)
                text.insert("1.0", cliente_data[i + 1])  # i+1 porque el ID está en cliente_data[0]
                text.grid(row=i, column=1, padx=5, pady=5)
                entries[field] = text
            else:
                entry = tk.Entry(popup, width=40)
                entry.insert(0, cliente_data[i + 1])
                entry.grid(row=i, column=1, padx=5, pady=5)
                entries[field] = entry

        # Botón para guardar los cambios
        def guardar_cambios():
            updated_data = {}
            for field, widget in entries.items():
                if isinstance(widget, tk.Text):
                    updated_data[field] = widget.get("1.0", "end-1c")
                else:
                    updated_data[field] = widget.get()

            # Actualizar la base de datos
            cursor.execute('''
                UPDATE clientes
                SET Atendido_por = ?, cliente = ?, telefono = ?, correo = ?, modelo = ?, 
                    numero_serie = ?, problema = ?, repuestos_utilizados = ?, costos = ?, 
                    forma_de_pago = ?, notas = ?
                WHERE id = ?
            ''', (
                updated_data["Atendido_por"], updated_data["Cliente"], updated_data["Teléfono"], updated_data["Correo"],
                updated_data["Modelo"], updated_data["Número de Serie"], updated_data["Problema"],
                updated_data["Repuestos Utilizados"], updated_data["Costos"], updated_data["Forma de Pago"],
                updated_data["Notas"], cliente_id
            ))
            conn.commit()

            # Actualizar la lista
            actualizar_lista()
            popup.destroy()

        tk.Button(popup, text="Guardar Cambios", command=guardar_cambios).grid(row=len(fields), column=0, columnspan=2, pady=10)

    except IndexError:
        messagebox.showwarning("Advertencia", "Por favor, selecciona un cliente para editar.")

# Función para el botón
def compartir_en_whatsapp():
    numero_telefono = "525555555555"  # Reemplaza con el número de teléfono (formato internacional sin +)
    mensaje = "Hola, esto es un mensaje desde mi aplicación en Python."  # Mensaje personalizado
    enlace = f"https://wa.me/{numero_telefono}?text={mensaje.replace(' ', '%20')}"  # Codifica espacios en %20
    webbrowser.open(enlace)  # Abre el enlace en el navegador predeterminado

root = tk.Tk()
root.title("Formulario con Lista de Clientes")
root.geometry("900x600")
root.configure(bg="white")  # Fondo blanco

# Crear el marco principal
container = tk.Frame(root, bg="white")
container.pack(fill="both", expand=True)


# Área principal
main_content = tk.Frame(container, bg="white")
main_content.pack(side="right", fill="both", expand=True)

# Encabezado
header = tk.Frame(main_content, bg="white", height=50)
header.pack(fill="x")

# Configurar columnas para organizar los elementos del encabezado
header.columnconfigure(0, weight=1)  # Columna de la hora (izquierda)
header.columnconfigure(1, weight=1)  # Columna central (puedes agregar texto si necesario)
header.columnconfigure(2, weight=1)  # Columna del logo (derecha)

# Hora en la esquina superior izquierda
tk.Label(header, text="12:21 a.m.", bg="white", fg="#002b5c", font=("Arial", 12)).grid(row=0, column=0, sticky="w", padx=10)

# Fecha en el centro
tk.Label(header, text="27/01/2025", bg="white", fg="#002b5c", font=("Arial", 12)).grid(row=0, column=1, sticky="n")

# Logo en la esquina superior derecha
try:
    ruta_imagen = r"C:\Users\52771\Desktop\Menu\isca.png"
    imagen_original = Image.open(ruta_imagen)
    imagen_reducida = imagen_original.resize((400, 150))  # Tamaño del logo ajustado
    imagen = ImageTk.PhotoImage(imagen_reducida)
    
    label_imagen = tk.Label(header, image=imagen, bg="white")
    label_imagen.image = imagen
    label_imagen.grid(row=0, column=2, sticky="e", padx=10)  # Esquina superior derecha
except FileNotFoundError:
    print(f"Archivo no encontrado: {ruta_imagen}")
except Exception as e:
    print(f"Error al cargar la imagen: {e}")

 

# Crear el Notebook (pestañas)
notebook = ttk.Notebook(main_content)
notebook.pack(fill="both", expand=True, padx=10, pady=10)

# Pestaña 1: Formulario
tab1 = ttk.Frame(notebook, style="TFrame")
notebook.add(tab1, text="Formulario")

form_frame = tk.Frame(tab1, bg="#e8e8e8", padx=20, pady=20)
form_frame.place(relx=0, rely=0, relwidth=1, relheight=1)


# Cuadro Azul (empieza donde termina el rojo)
canvas1 = tk.Canvas(form_frame, width=1170, height=650, bg="#193579")
# Coloca el canvas en el lado derecho sin afectar su tamaño
canvas1.place(relx=1.0, rely=canvas1.winfo_height() / 1000, anchor="ne")


# Cuadro Rojo en Pestaña 1

canvas2 = tk.Canvas(form_frame, width=300, height=800, bg="#d7251C")
canvas2.place(relx=0.0, rely=0.0, anchor="nw")

label_venta = tk.Label(
    canvas2, 
    text=f"Número de Venta:\n{numero_venta_actual}",  # Salto de línea antes del número
    bg="#d7251C", 
    fg="#d9d9d9", 
    font=("Open Sans", 15, "bold")  # Texto en negrita
)
canvas2.create_window(250, 50, window=label_venta, anchor="ne")


# Pestaña 2: Lista de Clientes
tab2 = ttk.Frame(notebook, style="TFrame")
notebook.add(tab2, text="Lista de Clientes")

list_frame = tk.Frame(tab2, bg="#e8e8e8", padx=20, pady=20)
list_frame.place(relx=0, rely=0, relwidth=1, relheight=1)

tk.Label(list_frame, text="Lista de Clientes", font=("Arial", 16), bg="#e8e8e8").pack(pady=10)
tk.Button(list_frame, text="Cargar Clientes").pack(pady=10)
tk.Label(list_frame, text="(Aquí aparecerá la lista de clientes)", font=("Arial", 12), bg="#e8e8e8").pack(pady=10)

tk.Label(list_frame, text="").pack()  
tk.Label(list_frame, text=f"    Número de Venta: {numero_venta_actual}").place(relx=1.0, rely=0.09, anchor="ne")  # Espacio más pequeño

# Crear la etiqueta de Fecha y Hora antes de la función actualizar_fecha_hora
fecha_actual, hora_actual = obtener_fecha_hora_actual()
label_fecha_hora = tk.Label(list_frame, text=f"    Fecha: {fecha_actual} | Hora: {hora_actual}")
label_fecha_hora.place(relx=1.0, rely=0.12, anchor="ne")  # Utilizamos place() para posicionar la etiqueta

# Frame que contiene los campos dentro del canvas azul
list_frame = tk.Frame(canvas1, bg="#193579")
list_frame.place(relx=0.05, rely=0.05, relwidth=0.9, relheight=0.9)  # Ajuste de proporción dentro del canvas

# atendido por
frame_atendido_por = tk.Frame(canvas1, bg="#193579")
frame_atendido_por.pack(fill="x", pady=5)
tk.Label(frame_atendido_por, text="Atendido por:", fg="#d9d9d9", bg="#193579", font=("open sans", 13, "bold")).pack(side="left", padx=5)
entry_atendido_por = tk.Entry(frame_atendido_por, fg="black", bg="#d9d9d9", width=130)
entry_atendido_por.pack(side="left", fill="both", expand=True, padx=5, pady=2)
canvas1.create_window((100, 40), window=frame_atendido_por, anchor="nw")


# nombre
frame_nombre = tk.Frame(canvas1, bg="#193579")
frame_nombre.pack(fill="x", pady=5)
tk.Label(frame_nombre, text="Nombre:", fg="#d9d9d9", bg="#193579", font=("open sans", 13, "bold")).pack(side="left", padx=5)
entry_nombre = tk.Entry(frame_nombre, fg="black", bg="#d9d9d9", width=137)
entry_nombre.pack(side="left", fill="both", expand=True, padx=5, pady=2)
canvas1.create_window((100, 80), window=frame_nombre, anchor="nw")  # Ajusté Y a 50 para que esté debajo

# teléfono
frame_telefono = tk.Frame(canvas1, bg="#193579")
frame_telefono.pack(fill="x", pady=5)
# etiqueta 
tk.Label(frame_telefono, text="Teléfono:", fg="#d9d9d9", bg="#193579", font=("open sans", 13, "bold")).pack(side="left", padx=5)
# cuadro de texto
entry_telefono = tk.Entry(frame_telefono, fg="black", bg="#d9d9d9", width=136)
entry_telefono.pack(side="left", fill="both", expand=True, padx=5, pady=2)
# frame dentro del Canvas
canvas1.create_window((100, 120), window=frame_telefono, anchor="nw")


# Validar el campo de teléfono en la función agregar_cliente
def agregar_cliente():
    telefono = entry_telefono.get()
    if not telefono.isdigit():
        messagebox.showerror("Error", "El teléfono debe contener solo números.")
        return

    # Continuar con el flujo de agregar cliente si el teléfono es válido
    id_cliente = random.randint(1000, 9999)
    Atendido_por = entry_atendido_por.get()
    nombre = entry_nombre.get()
    correo = entry_correo.get()
    modelo = entry_modelo.get()
    numero_serie = entry_numero_serie.get()
    problema = text_problema.get("1.0", "end-1c") # type: ignore
    repuestos_utilizados = text_repuestos_utilizados.get("1.0", "end-1c")
    costos = entry_costos.get()
    forma_de_pago = entry_forma_de_pago.get()
    notas = text_notas.get("1.0", "end-1c")

    if not nombre or not correo:
        messagebox.showerror("Error", "El nombre y el correo son obligatorios.")
        return

    cursor.execute('''
    INSERT INTO clientes (id, Atendido_por, cliente, telefono, correo, modelo, numero_serie, problema, 
                          repuestos_utilizados, costos, forma_de_pago, notas)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (id_cliente, Atendido_por, nombre, telefono, correo, modelo, numero_serie, problema, repuestos_utilizados, costos, forma_de_pago, notas))
    conn.commit()
    messagebox.showinfo("Éxito", "Cliente agregado correctamente.")
    actualizar_lista()


# Campo "Correo"
frame_correo = tk.Frame(canvas1, bg="#193579")
frame_correo.pack(fill="x", pady=5)
# Etiqueta "Correo"
tk.Label(frame_correo, text="Correo:", fg="#d9d9d9", bg="#193579", font=("open sans", 13, "bold")).pack(side="left", padx=5)
# Cuadro de texto para "Correo"
entry_correo = tk.Entry(frame_correo, fg="black",bg="#d9d9d9", width=138)
entry_correo.pack(side="left", fill="both", expand=True, padx=5, pady=2)
# Agregar el Frame dentro del Canvas
canvas1.create_window((100, 160), window=frame_correo, anchor="nw")


# modelo
frame_modelo = tk.Frame(canvas1, bg="#193579")
frame_modelo.pack(fill="x", pady=5)
# etiqueta 
tk.Label(frame_modelo, text="Modelo:", fg="#d9d9d9", bg="#193579", font=("open sans", 13, "bold")).pack(side="left", padx=5)
# cuadro de texto
entry_modelo = tk.Entry(frame_modelo, fg="black", bg="#d9d9d9", width=138)
entry_modelo.pack(side="left", fill="both", expand=True, padx=5, pady=2)
# frame dentro del Canvas
canvas1.create_window((100, 200), window=frame_modelo, anchor="nw")


# mframe_numero_serie
frame_numero_serie = tk.Frame(canvas1, bg="#193579")
frame_numero_serie.pack(fill="x", pady=5)
# etiqueta 
tk.Label(frame_numero_serie, text="Número de Serie:", fg="#d9d9d9", bg="#193579", font=("open sans", 13, "bold")).pack(side="left", padx=5)
# cuadro de texto
entry_numero_serie = tk.Entry(frame_numero_serie, fg="black", bg="#d9d9d9", width=125)
entry_numero_serie.pack(side="left", fill="both", expand=True, padx=5, pady=2)
# frame dentro del Canvas
canvas1.create_window((100, 240), window=frame_numero_serie, anchor="nw")


#problema
frame_problema = tk.Frame(canvas1, bg="#193579")
frame_problema.pack(fill="x", pady=5)
# etiqueta 
tk.Label(frame_problema, text="Problema:", fg="#d9d9d9", bg="#193579", font=("open sans", 13, "bold")).pack(side="left", padx=5)
# cuadro de texto
text_problema = tk.Text(frame_problema, fg="black", bg="#d9d9d9", height=4, width=101)  
text_problema.pack(side="left", fill="both", expand=True, padx=5, pady=2)  

# frame dentro del Canvas
canvas1.create_window((100, 280), window=frame_problema, anchor="nw")


#repuestos Utilizados
frame_repuestos = tk.Frame(canvas1, bg="#193579")
frame_repuestos.pack(fill="x", pady=5)
# etiqueta 
tk.Label(frame_repuestos, text="Repuestos Utilizados:", fg="#d9d9d9", bg="#193579", font=("Arial", 13, "bold")).pack(side="left", padx=5)
# cuadro de texto
text_repuestos_utilizados  = tk.Entry(frame_repuestos, fg="black", bg="#d9d9d9", width=120)
text_repuestos_utilizados.pack(side="left", fill="both", expand=True, padx=5, pady=2)
# frame dentro del Canvas
canvas1.create_window((100, 380), window=frame_repuestos, anchor="nw")


#costos
frame_costos = tk.Frame(canvas1, bg="#193579")
frame_costos.pack(fill="x", pady=5)
# etiqueta 
tk.Label(frame_costos, text="Costos:", fg="#d9d9d9", bg="#193579", font=("open sansl", 13, "bold")).pack(side="left", padx=5)
# cuadro de texto
entry_costos = tk.Entry(frame_costos, fg="black", bg="#d9d9d9", width=138)
entry_costos.pack(side="left", fill="both", expand=True, padx=5, pady=2)
# frame dentro del Canvas
canvas1.create_window((100, 440), window=frame_costos, anchor="nw")


#pago
frame_pago = tk.Frame(canvas1, bg="#193579")
frame_pago.pack(fill="x", pady=5)
# etiqueta 
tk.Label(frame_pago, text="Pago:", fg="#d9d9d9", bg="#193579", font=("open sans", 13, "bold")).pack(side="left", padx=5)
# cuadro de texto
opciones_pago = ["Efectivo", "Tarjeta de crédito o débito"]
entry_forma_de_pago = ttk.Combobox(frame_pago, values=opciones_pago, state="readonly")
entry_forma_de_pago.set("Seleccionar")
entry_forma_de_pago.pack(side="left", fill="x", expand=True)
# frame dentro del Canvas
canvas1.create_window((100, 480), window=frame_pago, anchor="nw")


#notas
frame_notas = tk.Frame(canvas1, bg="#193579")
frame_notas.pack(fill="x", pady=5)
# Etiqueta
tk.Label(frame_notas, text="Notas:", fg="#d9d9d9", bg="#193579", font=("open sans", 13, "bold")).pack(side="left", padx=5)
# Cuadro de texto para "Notas"
text_notas = tk.Text(frame_notas, fg="black", bg="#d9d9d9", height=4, width=105)  # Usamos Text para multilinea
text_notas.pack(side="left", fill="both", expand=True, padx=5, pady=2)
# Agregar el Frame dentro del Canvas
canvas1.create_window((100, 520), window=frame_notas, anchor="nw")



# Lista de clientes (Pestaña 2)

# Campo de búsqueda en la pestaña de lista de clientes
frame_buscar = tk.Frame(tab2)
frame_buscar.pack(fill="x", pady=5)

# Crear un Frame para la barra de búsqueda
frame_buscar.pack(fill="x", pady=10)
# Botón "buscra Cliente"
imagen_buscar= Image.open("buscar.png").resize((40, 40))
icono_buscar = ImageTk.PhotoImage(imagen_buscar) 
# Campo de entrada y botón
entry_buscar = tk.Entry(frame_buscar)
entry_buscar.pack(side="right", fill="x", expand=True, padx=5)  # Campo de búsqueda ocupa el espacio restante

btn_buscar = tk.Button(frame_buscar, image=icono_buscar, command=buscar_cliente, bd=0, highlightthickness=0, relief="flat")
btn_buscar.pack(side="right", padx=5)  # Mueve el botón a la derecha

# Cambiar el tipo de texto, tamaño y color
label_lista_clientes = tk.Label(tab2, text="LISTA DE CLIENTES GUARDADOS", font=("Roboto", 14, "bold"), fg="#3F51B5", bd=0, highlightthickness=0, relief="flat")
label_lista_clientes.pack()

label_EXTRA = tk.Label(tab2, text="", font=("LATO", 14, "bold"), fg="#26428B", bd=0, highlightthickness=0, relief="flat")
label_EXTRA.pack()

frame_treeview = tk.Frame(tab2)
frame_treeview.pack(fill='both', expand=True)

scrollbar_vertical = ttk.Scrollbar(frame_treeview, orient="vertical")
scrollbar_horizontal = ttk.Scrollbar(frame_treeview, orient="horizontal")

columns = ("ID", "Atendido_por", "Cliente", "Teléfono", "Correo", "Modelo", "Número de Serie", "Problema", "Repuestos Utilizados", "Costos", "Forma de Pago", "Notas")
treeview = ttk.Treeview(frame_treeview, columns=columns, show="headings", yscrollcommand=scrollbar_vertical.set, xscrollcommand=scrollbar_horizontal.set)

scrollbar_vertical.config(command=treeview.yview)
scrollbar_horizontal.config(command=treeview.xview)

scrollbar_vertical.pack(side="right", fill="y")
scrollbar_horizontal.pack(side="bottom", fill="x")
treeview.pack(fill='both', expand=True)

for col in columns:
    treeview.heading(col, text=col)
    treeview.column(col, width=100)


def mostrar_todos():
    actualizar_lista()
    
    

def imprimir_cliente():
    try:
        # Obtener el cliente seleccionado
        selected_item = treeview.selection()[0]
        cliente_data = treeview.item(selected_item)['values']

        # Formato del ticket (80x70 mm)
        ticket = f"""
        =============================
               ISCA Reparaciones
               
        =============================
        Fecha: {obtener_fecha_hora_actual()[0]}  Hora: {obtener_fecha_hora_actual()[1]}
        

        Atendido por: {cliente_data[1]}
        Cliente: {cliente_data[2]}
        Teléfono: {cliente_data[3]}
        Correo: {cliente_data[4]}

        Modelo: {cliente_data[5]}
        Número de Serie: {cliente_data[6]}

        Problema:
        {cliente_data[7]}

        Repuestos Utilizados:
        {cliente_data[8]}

        Costos: {cliente_data[9]}
        Forma de Pago: {cliente_data[10]}

        Notas:
        {cliente_data[11]}

            =============================
        ¡Esperamos verte de nuevo pronto! 😊
            =============================
        """

        # Seleccionar impresora por defecto
        printer_name = win32print.GetDefaultPrinter()

        # Configurar y enviar a la impresora
        hprinter = win32print.OpenPrinter(printer_name)
        printer_info = win32print.GetPrinter(hprinter, 2)
        printer_name = printer_info['pPrinterName']

        # Crear el contexto de dispositivo para la impresora
        hdc = win32ui.CreateDC()
        hdc.CreatePrinterDC(printer_name)
        hdc.StartDoc('Ticket de Cliente')
        hdc.StartPage()

        # Configuración de fuente
        font = win32ui.CreateFont({
            'name': 'Courier New',
            'height': 12,
            'weight': 400,
        })
        hdc.SelectObject(font)

        # Imprimir el contenido del ticket
        y = 0
        for line in ticket.split('\n'):
            hdc.TextOut(0, y, line)
            y += 20  # Ajusta la separación entre líneas

        hdc.EndPage()
        hdc.EndDoc()
        hdc.DeleteDC()

        messagebox.showinfo("Éxito", "El cliente ha sido impreso correctamente.")

    except IndexError:
        messagebox.showwarning("Advertencia", "Por favor, selecciona un cliente para imprimir.")
    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error al imprimir: {e}")
        
# Botón "buscra Cliente"
imagen_buscar= Image.open("buscar.png").resize((30, 30))
icono_buscar = ImageTk.PhotoImage(imagen_buscar)
btn_buscar= tk.Button(frame_buscar, image=icono_buscar, command=buscar_cliente, bd=0, highlightthickness=0, relief="flat")
btn_buscar.pack(side="left", padx=5)        

# Crear un marco para botones en la pestaña 2
frame_botones = tk.Frame(tab2, bg="#4B0082")
frame_botones.pack(pady=20)

# Crear un Frame para los botones dentro de tab2
botones_frame = tk.Frame(tab2)
botones_frame.pack(pady=20)  # Centrar verticalmente con margen superior e inferior


# Botón "Eliminar Cliente"
imagen_eliminar = Image.open("eliminar.png").resize((40, 40))
icono_eliminar = ImageTk.PhotoImage(imagen_eliminar)
btn_eliminar = tk.Button(botones_frame, image=icono_eliminar, command=eliminar_cliente, bd=0, highlightthickness=0, relief="flat")
btn_eliminar.pack(side="left", padx=10)

# Botón "Editar Cliente"
imagen_editar = Image.open("editar.png").resize((40, 40))
icono_editar = ImageTk.PhotoImage(imagen_editar)
btn_editar = tk.Button(botones_frame, image=icono_editar, command=editar_cliente, bd=0, highlightthickness=0, relief="flat")
btn_editar.pack(side="left", padx=10)

# Botón "Imprimir Cliente"
imagen_imprimir = Image.open("impri.png").resize((40, 40))
icono_imprimir = ImageTk.PhotoImage(imagen_imprimir)
btn_imprimir = tk.Button(botones_frame, image=icono_imprimir, compound="left", command=imprimir_cliente, bd=0, highlightthickness=0, relief="flat")
btn_imprimir.pack(side="left", padx=10)

# Botón "Compartir en WhatsApp"
imagen_whatsapp = Image.open("whatsapp.png").resize((50, 50))
icono_whatsapp = ImageTk.PhotoImage(imagen_whatsapp)
btn_compartir = tk.Button(botones_frame, image=icono_whatsapp, command=compartir_en_whatsapp, bd=0, highlightthickness=0, relief="flat")
btn_compartir.pack(side="left", padx=10)

btn_agregar = tk.Button(form_frame, text="Agregar Cliente", command=agregar_cliente)
btn_agregar.pack(pady=10)

# Centrar el Frame en la pestaña
botones_frame.pack(anchor="center")


# Iniciar actualización automática de la fecha y hora
actualizar_fecha_hora()

# Actualizar lista inicial
actualizar_lista()

# Configuración para cerrar la conexión al cerrar la ventana
root.protocol("WM_DELETE_WINDOW", cerrar_conexion)
root.mainloop()




btn_mostrar_todos = tk.Button(frame_buscar, text="Mostrar Todos", command=mostrar_todos)
btn_mostrar_todos.pack(side="left", padx=5)


# Función para agregar cliente
def agregar_cliente():
    id_cliente = random.randint(1000, 9999)
    Atendido_por = entry_Atendido_por.get()
    nombre = entry_nombre.get()
    telefono = entry_telefono.get()
    correo = entry_correo.get()
    modelo = entry_modelo.get()
    numero_serie = entry_numero_serie.get()
    problema = text_problema.get("1.0", "end-1c")
    repuestos_utilizados = text_repuestos_utilizados.get("1.0", "end-1c")
    costos = entry_costos.get()
    forma_de_pago = entry_forma_de_pago.get()
    notas = text_notas.get("1.0", "end-1c")

    if not nombre or not correo:
        print("Error: Nombre y correo son obligatorios.")
        return

    cursor.execute('''
    INSERT INTO clientes (id, Atendido_por, cliente, telefono, correo, modelo, numero_serie, problema, 
                          repuestos_utilizados, costos, forma_de_pago, notas)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (id_cliente, Atendido_por, nombre, telefono, correo, modelo, numero_serie, problema, repuestos_utilizados, costos, forma_de_pago, notas))
    conn.commit()
    print(f"Cliente agregado correctamente con ID {id_cliente}.")
    actualizar_lista()
