"""Interfaz gráfica Tkinter de Huellitas."""

import tkinter as tk
from tkinter import messagebox, ttk

from base_datos import BaseDatos
from modelos import Cuidado, ESPECIES, ESTADOS, Mascota, TIPOS_CUIDADO, fecha_a_iso, fecha_para_mostrar


VERDE = "#4F8A6B"
VERDE_OSCURO = "#35664D"
FONDO = "#F3F6F4"
BLANCO = "#FFFFFF"
TEXTO = "#26332D"
GRIS = "#66736D"


class AplicacionHuellitas(tk.Tk):
    def __init__(self, base_datos: BaseDatos) -> None:
        super().__init__()
        self.base_datos = base_datos
        self.title("Huellitas")
        self.geometry("1040x650")
        self.minsize(850, 540)
        self.configure(bg=FONDO)
        self._configurar_estilos()
        self._crear_encabezado()
        self._crear_pestanas()
        self.actualizar_listas()

    def _configurar_estilos(self) -> None:
        estilo = ttk.Style(self)
        estilo.theme_use("clam")
        estilo.configure("TNotebook", background=FONDO, borderwidth=0)
        estilo.configure("TNotebook.Tab", padding=(20, 10), font=("Segoe UI", 10, "bold"))
        estilo.map("TNotebook.Tab", background=[("selected", BLANCO)], foreground=[("selected", VERDE_OSCURO)])
        estilo.configure("Treeview", rowheight=30, font=("Segoe UI", 10), background=BLANCO,
                         fieldbackground=BLANCO, foreground=TEXTO)
        estilo.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"), background="#DCEAE2",
                         foreground=TEXTO, relief="flat")
        estilo.map("Treeview", background=[("selected", "#BFD8C9")], foreground=[("selected", TEXTO)])

    def _crear_encabezado(self) -> None:
        encabezado = tk.Frame(self, bg=VERDE, height=88)
        encabezado.pack(fill="x")
        encabezado.pack_propagate(False)
        tk.Label(encabezado, text="🐾  Huellitas", bg=VERDE, fg=BLANCO,
                 font=("Segoe UI", 24, "bold")).pack(anchor="w", padx=28, pady=(13, 0))
        tk.Label(encabezado, text="Organiza el cuidado de tus mascotas", bg=VERDE, fg="#EAF4EE",
                 font=("Segoe UI", 10)).pack(anchor="w", padx=72)

    def _crear_pestanas(self) -> None:
        self.pestanas = ttk.Notebook(self)
        self.pestanas.pack(fill="both", expand=True, padx=22, pady=18)
        self.marco_mascotas = tk.Frame(self.pestanas, bg=BLANCO)
        self.marco_cuidados = tk.Frame(self.pestanas, bg=BLANCO)
        self.pestanas.add(self.marco_mascotas, text="Mis mascotas")
        self.pestanas.add(self.marco_cuidados, text="Próximos cuidados")
        self._crear_seccion_mascotas()
        self._crear_seccion_cuidados()

    def _boton(self, padre: tk.Widget, texto: str, comando, principal: bool = False) -> tk.Button:
        return tk.Button(padre, text=texto, command=comando, bg=VERDE if principal else "#E5ECE8",
                         fg=BLANCO if principal else TEXTO, activebackground=VERDE_OSCURO,
                         activeforeground=BLANCO, relief="flat", bd=0, padx=14, pady=8,
                         font=("Segoe UI", 9, "bold"), cursor="hand2")

    def _crear_seccion_mascotas(self) -> None:
        barra = tk.Frame(self.marco_mascotas, bg=BLANCO)
        barra.pack(fill="x", padx=18, pady=(18, 10))
        tk.Label(barra, text="Mascotas registradas", bg=BLANCO, fg=TEXTO,
                 font=("Segoe UI", 16, "bold")).pack(side="left")
        self._boton(barra, "+ Agregar mascota", self.abrir_mascota, True).pack(side="right")
        columnas = ("id", "nombre", "especie", "edad", "observaciones")
        self.tabla_mascotas = ttk.Treeview(self.marco_mascotas, columns=columnas, show="headings")
        titulos = ("ID", "Nombre", "Especie", "Edad", "Observaciones")
        anchos = (55, 180, 120, 70, 430)
        for columna, titulo, ancho in zip(columnas, titulos, anchos):
            self.tabla_mascotas.heading(columna, text=titulo)
            self.tabla_mascotas.column(columna, width=ancho, anchor="center" if columna != "observaciones" else "w")
        self.tabla_mascotas.pack(fill="both", expand=True, padx=18)
        acciones = tk.Frame(self.marco_mascotas, bg=BLANCO)
        acciones.pack(fill="x", padx=18, pady=14)
        self._boton(acciones, "Editar", self.editar_mascota).pack(side="left", padx=(0, 8))
        self._boton(acciones, "Eliminar", self.eliminar_mascota).pack(side="left")

    def _crear_seccion_cuidados(self) -> None:
        barra = tk.Frame(self.marco_cuidados, bg=BLANCO)
        barra.pack(fill="x", padx=18, pady=(18, 10))
        tk.Label(barra, text="Cuidados registrados", bg=BLANCO, fg=TEXTO,
                 font=("Segoe UI", 16, "bold")).pack(side="left")
        self._boton(barra, "+ Agregar cuidado", self.abrir_cuidado, True).pack(side="right")
        columnas = ("id", "mascota", "tipo", "fecha", "estado", "observaciones")
        self.tabla_cuidados = ttk.Treeview(self.marco_cuidados, columns=columnas, show="headings")
        titulos = ("ID", "Mascota", "Tipo", "Fecha", "Estado", "Observaciones")
        anchos = (50, 140, 155, 100, 100, 330)
        for columna, titulo, ancho in zip(columnas, titulos, anchos):
            self.tabla_cuidados.heading(columna, text=titulo)
            self.tabla_cuidados.column(columna, width=ancho, anchor="w" if columna == "observaciones" else "center")
        self.tabla_cuidados.tag_configure("realizado", foreground=GRIS)
        self.tabla_cuidados.pack(fill="both", expand=True, padx=18)
        acciones = tk.Frame(self.marco_cuidados, bg=BLANCO)
        acciones.pack(fill="x", padx=18, pady=14)
        self._boton(acciones, "Editar", self.editar_cuidado).pack(side="left", padx=(0, 8))
        self._boton(acciones, "Marcar como realizado", self.marcar_realizado).pack(side="left", padx=(0, 8))
        self._boton(acciones, "Eliminar", self.eliminar_cuidado).pack(side="left")

    def actualizar_listas(self) -> None:
        for item in self.tabla_mascotas.get_children():
            self.tabla_mascotas.delete(item)
        for mascota in self.base_datos.listar_mascotas():
            self.tabla_mascotas.insert("", "end", values=(mascota["id"], mascota["nombre"],
                mascota["especie"], mascota["edad"], mascota["observaciones"]))
        for item in self.tabla_cuidados.get_children():
            self.tabla_cuidados.delete(item)
        for cuidado in self.base_datos.listar_cuidados():
            etiqueta = ("realizado",) if cuidado["estado"] == "Realizado" else ()
            self.tabla_cuidados.insert("", "end", values=(cuidado["id"], cuidado["mascota"],
                cuidado["tipo"], fecha_para_mostrar(cuidado["fecha"]), cuidado["estado"],
                cuidado["observaciones"]), tags=etiqueta)

    @staticmethod
    def _id_seleccionado(tabla: ttk.Treeview, mensaje: str) -> int | None:
        seleccion = tabla.selection()
        if not seleccion:
            messagebox.showinfo("Huellitas", mensaje)
            return None
        return int(tabla.item(seleccion[0], "values")[0])

    def abrir_mascota(self, mascota: dict | None = None) -> None:
        VentanaMascota(self, self.base_datos, mascota)

    def editar_mascota(self) -> None:
        identificador = self._id_seleccionado(self.tabla_mascotas, "Seleccione una mascota para editar.")
        if identificador:
            self.abrir_mascota(self.base_datos.obtener_mascota(identificador))

    def eliminar_mascota(self) -> None:
        identificador = self._id_seleccionado(self.tabla_mascotas, "Seleccione una mascota para eliminar.")
        if identificador and messagebox.askyesno("Confirmar eliminación",
                "¿Desea eliminar la mascota y todos sus cuidados asociados?"):
            self.base_datos.eliminar_mascota(identificador)
            self.actualizar_listas()

    def abrir_cuidado(self, cuidado: dict | None = None) -> None:
        if not self.base_datos.listar_mascotas():
            messagebox.showinfo("Huellitas", "Primero debe registrar una mascota.")
            return
        VentanaCuidado(self, self.base_datos, cuidado)

    def editar_cuidado(self) -> None:
        identificador = self._id_seleccionado(self.tabla_cuidados, "Seleccione un cuidado para editar.")
        if identificador:
            self.abrir_cuidado(self.base_datos.obtener_cuidado(identificador))

    def marcar_realizado(self) -> None:
        identificador = self._id_seleccionado(self.tabla_cuidados, "Seleccione un cuidado.")
        if identificador:
            self.base_datos.marcar_realizado(identificador)
            self.actualizar_listas()

    def eliminar_cuidado(self) -> None:
        identificador = self._id_seleccionado(self.tabla_cuidados, "Seleccione un cuidado para eliminar.")
        if identificador and messagebox.askyesno("Confirmar eliminación", "¿Desea eliminar este cuidado?"):
            self.base_datos.eliminar_cuidado(identificador)
            self.actualizar_listas()


class VentanaFormulario(tk.Toplevel):
    def __init__(self, padre: AplicacionHuellitas, titulo: str) -> None:
        super().__init__(padre)
        self.padre = padre
        self.title(titulo)
        self.configure(bg=BLANCO)
        self.resizable(False, False)
        self.transient(padre)
        self.grab_set()
        self.columnconfigure(1, weight=1)
        tk.Label(self, text=titulo, bg=BLANCO, fg=TEXTO,
                 font=("Segoe UI", 16, "bold")).grid(row=0, column=0, columnspan=2,
                                                      sticky="w", padx=22, pady=(20, 16))

    def etiqueta(self, texto: str, fila: int) -> None:
        tk.Label(self, text=texto, bg=BLANCO, fg=TEXTO,
                 font=("Segoe UI", 10)).grid(row=fila, column=0, sticky="w", padx=(22, 12), pady=7)

    def acciones(self, fila: int, guardar) -> None:
        marco = tk.Frame(self, bg=BLANCO)
        marco.grid(row=fila, column=0, columnspan=2, sticky="e", padx=22, pady=(16, 20))
        self.padre._boton(marco, "Cancelar", self.destroy).pack(side="left", padx=(0, 8))
        self.padre._boton(marco, "Guardar", guardar, True).pack(side="left")


class VentanaMascota(VentanaFormulario):
    def __init__(self, padre: AplicacionHuellitas, base_datos: BaseDatos, mascota: dict | None) -> None:
        super().__init__(padre, "Editar mascota" if mascota else "Agregar mascota")
        self.base_datos, self.mascota = base_datos, mascota
        self.geometry("520x350")
        self.etiqueta("Nombre *", 1); self.nombre = ttk.Entry(self, width=38); self.nombre.grid(row=1, column=1, padx=(0, 22), pady=7)
        self.etiqueta("Especie *", 2); self.especie = ttk.Combobox(self, values=ESPECIES, state="readonly", width=35); self.especie.grid(row=2, column=1, padx=(0, 22), pady=7)
        self.etiqueta("Edad en años *", 3); self.edad = ttk.Entry(self, width=38); self.edad.grid(row=3, column=1, padx=(0, 22), pady=7)
        self.etiqueta("Observaciones", 4); self.observaciones = ttk.Entry(self, width=38); self.observaciones.grid(row=4, column=1, padx=(0, 22), pady=7)
        self.acciones(5, self.guardar)
        if mascota:
            self.nombre.insert(0, mascota["nombre"]); self.especie.set(mascota["especie"])
            self.edad.insert(0, str(mascota["edad"])); self.observaciones.insert(0, mascota["observaciones"])
        else:
            self.especie.set(ESPECIES[0])
        self.nombre.focus_set()

    def guardar(self) -> None:
        try:
            edad = int(self.edad.get())
            registro = Mascota(self.nombre.get(), self.especie.get(), edad,
                               self.observaciones.get(), self.mascota["id"] if self.mascota else None)
            if self.mascota:
                self.base_datos.actualizar_mascota(registro)
            else:
                self.base_datos.agregar_mascota(registro)
            self.padre.actualizar_listas(); self.destroy()
        except ValueError as error:
            messagebox.showerror("Datos inválidos", str(error), parent=self)


class VentanaCuidado(VentanaFormulario):
    def __init__(self, padre: AplicacionHuellitas, base_datos: BaseDatos, cuidado: dict | None) -> None:
        super().__init__(padre, "Editar cuidado" if cuidado else "Agregar cuidado")
        self.base_datos, self.cuidado = base_datos, cuidado
        self.mascotas = base_datos.listar_mascotas()
        self.mapa_mascotas = {f'{m["nombre"]} (ID {m["id"]})': m["id"] for m in self.mascotas}
        self.geometry("570x410")
        self.etiqueta("Mascota *", 1); self.mascota = ttk.Combobox(self, values=list(self.mapa_mascotas), state="readonly", width=38); self.mascota.grid(row=1, column=1, padx=(0, 22), pady=7)
        self.etiqueta("Tipo *", 2); self.tipo = ttk.Combobox(self, values=TIPOS_CUIDADO, state="readonly", width=38); self.tipo.grid(row=2, column=1, padx=(0, 22), pady=7)
        self.etiqueta("Fecha (DD/MM/AAAA) *", 3); self.fecha = ttk.Entry(self, width=41); self.fecha.grid(row=3, column=1, padx=(0, 22), pady=7)
        self.etiqueta("Estado *", 4); self.estado = ttk.Combobox(self, values=ESTADOS, state="readonly", width=38); self.estado.grid(row=4, column=1, padx=(0, 22), pady=7)
        self.etiqueta("Observaciones", 5); self.observaciones = ttk.Entry(self, width=41); self.observaciones.grid(row=5, column=1, padx=(0, 22), pady=7)
        self.acciones(6, self.guardar)
        self.tipo.set(TIPOS_CUIDADO[0]); self.estado.set(ESTADOS[0]); self.mascota.current(0)
        if cuidado:
            for texto, identificador in self.mapa_mascotas.items():
                if identificador == cuidado["mascota_id"]: self.mascota.set(texto)
            self.tipo.set(cuidado["tipo"]); self.fecha.insert(0, fecha_para_mostrar(cuidado["fecha"]))
            self.estado.set(cuidado["estado"]); self.observaciones.insert(0, cuidado["observaciones"])

    def guardar(self) -> None:
        try:
            registro = Cuidado(self.mapa_mascotas[self.mascota.get()], self.tipo.get(),
                fecha_a_iso(self.fecha.get()), self.estado.get(), self.observaciones.get(),
                self.cuidado["id"] if self.cuidado else None)
            if self.cuidado: self.base_datos.actualizar_cuidado(registro)
            else: self.base_datos.agregar_cuidado(registro)
            self.padre.actualizar_listas(); self.destroy()
        except (ValueError, KeyError) as error:
            messagebox.showerror("Datos inválidos", str(error) or "Seleccione una mascota válida.", parent=self)
