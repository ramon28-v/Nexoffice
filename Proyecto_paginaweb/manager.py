import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import os
import webbrowser
import qrcode
from database import conectar, obtener_inventario, actualizar_stock, guardar_o_actualizar_producto

class AplicacionNexOffice:
    def __init__(self, root):
        self.root = root
        self.root.title("NexOffice | Ventura Tech Group")
        self.root.geometry("850x650")
        
        self.color_bg = "#1e222d"       
        self.color_card = "#282e3e"     
        self.color_accent = "#7dd3fc"   
        self.color_text = "#e0e6ed"     
        self.color_success = "#4ade80"  
        
        self.root.configure(bg=self.color_bg)
        conectar()
        self.cargar_datos_desde_db()
        self.configurar_estilos_ttk()
        self.pantalla_login()

    def configurar_estilos_ttk(self):
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", background=self.color_card, foreground=self.color_text, fieldbackground=self.color_card, rowheight=30)
        style.map("Treeview", background=[('selected', self.color_accent)], foreground=[('selected', self.color_bg)])

    def cargar_datos_desde_db(self):
        datos = obtener_inventario()
        self.inventario = {item[0]: {"precio": item[1], "stock": item[2]} for item in datos}

    def limpiar_pantalla(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def pantalla_login(self):
        self.limpiar_pantalla()
        self.root.geometry("450x500")
        tk.Label(self.root, text="NEXOFFICE", font=("Arial", 28, "bold"), bg=self.color_bg, fg=self.color_accent).pack(pady=40)
        frame = tk.Frame(self.root, bg=self.color_card, padx=35, pady=35)
        frame.pack()
        tk.Label(frame, text="Usuario", bg=self.color_card, fg=self.color_text).pack(anchor="w")
        self.ent_user = tk.Entry(frame, font=("Arial", 12), bg="#1e293b", fg="white")
        self.ent_user.pack(pady=8, fill="x")
        tk.Label(frame, text="Contraseña", bg=self.color_card, fg=self.color_text).pack(anchor="w")
        self.ent_pass = tk.Entry(frame, show="*", font=("Arial", 12), bg="#1e293b", fg="white")
        self.ent_pass.pack(pady=8, fill="x")
        tk.Button(frame, text="INGRESAR", command=self.validar_acceso, bg=self.color_accent, fg=self.color_bg, font=("bold")).pack(pady=25)

    def validar_acceso(self):
        if self.ent_user.get() == "ventura" and self.ent_pass.get() == "1234":
            self.pantalla_menu()
        else:
            messagebox.showerror("Error", "Usuario o clave incorrectos.")

    def pantalla_menu(self):
        self.limpiar_pantalla()
        self.root.geometry("800x600")
        tk.Label(self.root, text="PANEL VENTURA TECH", font=("Arial", 22, "bold"), bg=self.color_bg, fg=self.color_accent).pack(pady=40)
        btn_fm = tk.Frame(self.root, bg=self.color_bg)
        btn_fm.pack(expand=True)
        
        tk.Button(btn_fm, text="🛒 NUEVA VENTA", command=self.modulo_ventas, width=18, height=5, bg=self.color_card, fg=self.color_accent, font=("bold")).grid(row=0, column=0, padx=15)
        tk.Button(btn_fm, text="📦 INVENTARIO", command=self.modulo_inventario, width=18, height=5, bg=self.color_card, fg=self.color_text, font=("bold")).grid(row=0, column=1, padx=15)
        tk.Button(btn_fm, text="⚙️ AJUSTES", command=self.modulo_ajustes, width=18, height=5, bg="#334155", fg="#cbd5e1", font=("bold")).grid(row=0, column=2, padx=15)
        
        tk.Button(self.root, text="Cerrar Sesión", command=self.pantalla_login, bg="#f87171", fg="white").pack(side="bottom", pady=30)

    # --- VENTAS ---
    def modulo_ventas(self):
        self.limpiar_pantalla()
        self.cargar_datos_desde_db()
        self.root.geometry("1000x850")
        self.total_final = 0.0
        
        tk.Button(self.root, text="← Volver", command=self.pantalla_menu, bg="#3d4455", fg="white").pack(anchor="w", padx=20, pady=10)
        
        frame_cliente = tk.Frame(self.root, bg=self.color_card, padx=20, pady=15)
        frame_cliente.pack(fill="x", padx=20, pady=5)

        tk.Label(frame_cliente, text="CLIENTE:", bg=self.color_card, fg=self.color_text).grid(row=0, column=0, sticky="w")
        self.ent_cliente = tk.Entry(frame_cliente, width=30); self.ent_cliente.grid(row=0, column=1, padx=10, pady=5)
        
        tk.Label(frame_cliente, text="RNC:", bg=self.color_card, fg=self.color_text).grid(row=0, column=2, sticky="w")
        self.ent_rnc = tk.Entry(frame_cliente, width=20); self.ent_rnc.grid(row=0, column=3, padx=10, pady=5)

        tk.Label(frame_cliente, text="DIRECCIÓN:", bg=self.color_card, fg=self.color_text).grid(row=1, column=0, sticky="w")
        self.ent_direccion = tk.Entry(frame_cliente, width=30); self.ent_direccion.grid(row=1, column=1, padx=10, pady=5)

        tk.Label(frame_cliente, text="EQUIPO:", bg=self.color_card, fg=self.color_text).grid(row=1, column=2, sticky="w")
        self.combo_venta = ttk.Combobox(frame_cliente, values=list(self.inventario.keys()), state="readonly", width=35)
        self.combo_venta.grid(row=1, column=3, padx=10, pady=5)

        tk.Button(frame_cliente, text="AÑADIR", command=self.agregar_a_factura, bg=self.color_accent, fg=self.color_bg, font=("bold")).grid(row=1, column=4, padx=10)

        self.tree = ttk.Treeview(self.root, columns=("P", "Pr", "C", "S"), show="headings")
        self.tree.heading("P", text="Descripción"); self.tree.heading("Pr", text="Precio"); self.tree.heading("C", text="Cant"); self.tree.heading("S", text="Subtotal")
        self.tree.pack(fill="both", expand=True, padx=20, pady=10)

        self.lbl_total = tk.Label(self.root, text="TOTAL: RD$ 0.00", font=("Arial", 24, "bold"), bg=self.color_bg, fg=self.color_accent)
        self.lbl_total.pack()

        tk.Button(self.root, text="🔍 GENERAR FACTURA ELECTRÓNICA", command=self.mostrar_vista_previa, bg="#6366f1", fg="white", font=("bold"), pady=12).pack(pady=10)

    def agregar_a_factura(self):
        item = self.combo_venta.get()
        if item and self.inventario[item]["stock"] > 0:
            precio = self.inventario[item]["precio"]
            self.tree.insert("", "end", values=(item, f"{precio:,.2f}", 1, f"{precio:,.2f}"))
            self.total_final += precio
            self.lbl_total.config(text=f"TOTAL: RD$ {self.total_final:,.2f}")

    def mostrar_vista_previa(self):
        cliente = self.ent_cliente.get()
        if not cliente or not self.tree.get_children():
            messagebox.showwarning("Error", "Datos incompletos.")
            return

        # QR LOCAL
        ahora = datetime.now()
        id_f = ahora.strftime('%y%m%d%H%M')
        qr_img = qrcode.make(f"VTG-FACTURA\nID: {id_f}\nCliente: {cliente}\nTotal: RD$ {self.total_final:,.2f}")
        qr_path = os.path.abspath("temp_qr.png")
        qr_img.save(qr_path)

        items_h = ""
        for i in self.tree.get_children():
            v = self.tree.item(i)['values']
            items_h += f"<tr><td>{v[0]}</td><td style='text-align:center;'>1</td><td style='text-align:right;'>RD$ {v[1]}</td><td style='text-align:right;'>RD$ {v[3]}</td></tr>"

        html = f"""
        <!DOCTYPE html><html><head><meta charset="UTF-8"><style>
        @page {{ size: letter; margin: 10mm; }}
        body {{ font-family: sans-serif; padding: 20px; }}
        .invoice-box {{ max-width: 800px; margin: auto; padding: 30px; border: 1px solid #eee; min-height: 900px; display: flex; flex-direction: column; }}
        .header {{ display: flex; justify-content: space-between; border-bottom: 3px solid #7dd3fc; padding-bottom: 20px; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 30px; }}
        th, td {{ padding: 12px; border-bottom: 1px solid #eee; }}
        .footer-s {{ margin-top: auto; display: flex; justify-content: space-between; align-items: flex-end; border-top: 2px solid #1e222d; padding-top: 20px; }}
        @media print {{ .no-print {{ display: none; }} }}
        </style></head><body>
        <div class="no-print" style="text-align:center;"><button onclick="window.print()" style="padding:10px 20px; background:#22c55e; color:white; border:none; cursor:pointer;">🖨️ IMPRIMIR</button></div>
        <div class="invoice-box">
            <div class="header"><div><h1>VENTURA TECH GROUP</h1><span>NexOffice Solutions</span></div><div style="text-align:right;"><h2>FACTURA</h2><p>ID: {id_f}<br>{ahora.strftime('%d/%m/%Y')}</p></div></div>
            <p><strong>CLIENTE:</strong> {cliente.upper()}<br>RNC: {self.ent_rnc.get()}<br>DIR: {self.ent_direccion.get().upper()}</p>
            <div style="flex-grow:1;"><table><thead><tr><th>Descripción</th><th>Cant.</th><th>Unitario</th><th>Total</th></tr></thead><tbody>{items_h}</tbody></table></div>
            <div class="footer-s"><div><img src="file:///{qr_path}" width="100"><br><small>Autenticidad VTG</small></div><div style="text-align:right; font-size:24px;"><strong>TOTAL: RD$ {self.total_final:,.2f}</strong></div></div>
        </div></body></html>"""

        f_path = f"Factura_{cliente.replace(' ','_')}.html"
        with open(f_path, "w", encoding="utf-8") as f: f.write(html)
        webbrowser.open('file://' + os.path.realpath(f_path))
        
        for i in self.tree.get_children():
            actualizar_stock(self.tree.item(i)['values'][0], 1)
        self.modulo_ventas()

    # --- AJUSTES ---
    def modulo_ajustes(self):
        self.limpiar_pantalla()
        self.cargar_datos_desde_db()
        tk.Button(self.root, text="← Volver", command=self.pantalla_menu, bg="#3d4455", fg="white").pack(anchor="w", padx=20, pady=10)
        tk.Label(self.root, text="CONFIGURACIÓN DE PRODUCTOS", font=("Arial", 16, "bold"), bg=self.color_bg, fg=self.color_accent).pack(pady=10)

        frame = tk.Frame(self.root, bg=self.color_card, padx=20, pady=20)
        frame.pack(fill="x", padx=40, pady=10)

        tk.Label(frame, text="Nombre:", bg=self.color_card, fg=self.color_text).grid(row=0, column=0, pady=5)
        self.ent_a_nom = tk.Entry(frame, width=40); self.ent_a_nom.grid(row=0, column=1)
        tk.Label(frame, text="Precio:", bg=self.color_card, fg=self.color_text).grid(row=1, column=0, pady=5)
        self.ent_a_pre = tk.Entry(frame, width=20); self.ent_a_pre.grid(row=1, column=1, sticky="w")
        tk.Label(frame, text="Stock:", bg=self.color_card, fg=self.color_text).grid(row=2, column=0, pady=5)
        self.ent_a_stk = tk.Entry(frame, width=10); self.ent_a_stk.grid(row=2, column=1, sticky="w")

        def guardar():
            try:
                guardar_o_actualizar_producto(self.ent_a_nom.get(), float(self.ent_a_pre.get()), int(self.ent_a_stk.get()))
                messagebox.showinfo("Éxito", "Guardado.")
                self.modulo_ajustes()
            except: messagebox.showerror("Error", "Datos inválidos.")

        tk.Button(frame, text="💾 GUARDAR CAMBIOS", command=guardar, bg=self.color_success, fg=self.color_bg, font=("bold")).grid(row=3, column=1, pady=10, sticky="w")

        tree = ttk.Treeview(self.root, columns=("P", "Pr", "S"), show="headings", height=8)
        tree.heading("P", text="Producto"); tree.heading("Pr", text="Precio"); tree.heading("S", text="Stock")
        tree.pack(pady=10, padx=40, fill="x")
        for p, d in self.inventario.items(): tree.insert("", "end", values=(p, d['precio'], d['stock']))

        def editar(e):
            v = tree.item(tree.selection()[0])['values']
            self.ent_a_nom.delete(0, tk.END); self.ent_a_nom.insert(0, v[0])
            self.ent_a_pre.delete(0, tk.END); self.ent_a_pre.insert(0, v[1])
            self.ent_a_stk.delete(0, tk.END); self.ent_a_stk.insert(0, v[2])
        tree.bind("<<TreeviewSelect>>", editar)

    def modulo_inventario(self):
        self.limpiar_pantalla()
        self.cargar_datos_desde_db()
        tk.Button(self.root, text="← Volver", command=self.pantalla_menu, bg="#3d4455", fg="white").pack(anchor="w", padx=20, pady=10)
        for p, d in self.inventario.items():
            f = tk.Frame(self.root, bg=self.color_card, pady=5, padx=20)
            f.pack(fill="x", padx=40, pady=2)
            tk.Label(f, text=p, bg=self.color_card, fg=self.color_text).pack(side="left")
            tk.Label(f, text=f"Stock: {d['stock']}", bg=self.color_card, fg=self.color_success).pack(side="right")

if __name__ == "__main__":
    root = tk.Tk()
    app = AplicacionNexOffice(root)
    root.mainloop()