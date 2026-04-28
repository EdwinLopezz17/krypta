import threading
import getpass
import customtkinter as ctk
from tkinter import messagebox

from db        import init_db
from auth      import master_exists, register_master, login
from krypta_ops import (
    add_entry, list_entries, get_password,
    delete_entry, copy_to_clipboard,
)

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

FONT_TITLE  = ("Segoe UI", 22, "bold")
FONT_BODY   = ("Segoe UI", 14)
FONT_SMALL  = ("Segoe UI", 12)
FONT_MONO   = ("Consolas", 13)

BG          = "#1a1a1a"
BG2         = "#242424"
BG3         = "#2e2e2e"
ACCENT      = "#3b82f6"
ACCENT_HOV  = "#2563eb"
DANGER      = "#ef4444"
DANGER_HOV  = "#dc2626"
TEXT        = "#f1f5f9"
TEXT_MUTED  = "#94a3b8"
RADIUS      = 10

class LoginView(ctk.CTkFrame):
    def __init__(self, master, on_success):
        super().__init__(master, fg_color=BG)
        self.on_success   = on_success
        self.is_first_run = not master_exists()
        self._build()

    def _build(self):
        self.grid_rowconfigure((0, 1, 2, 3, 4, 5), weight=1)
        self.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            self, text="🔐", font=("Segoe UI", 52),
            text_color=ACCENT,
        ).grid(row=0, column=0, pady=(60, 4))

        ctk.CTkLabel(
            self, text="Krypta", font=FONT_TITLE,
            text_color=TEXT,
        ).grid(row=1, column=0, pady=(0, 2))

        subtitle = "Crea tu contraseña maestra" if self.is_first_run else "Ingresa tu contraseña maestra"
        ctk.CTkLabel(
            self, text=subtitle, font=FONT_SMALL,
            text_color=TEXT_MUTED,
        ).grid(row=2, column=0, pady=(0, 32))

        # Campos
        inner = ctk.CTkFrame(self, fg_color="transparent")
        inner.grid(row=3, column=0, padx=60, sticky="ew")
        inner.grid_columnconfigure(0, weight=1)

        self.pwd_entry = ctk.CTkEntry(
            inner, placeholder_text="Contraseña maestra",
            show="●", height=44, font=FONT_BODY,
            corner_radius=RADIUS,
        )
        self.pwd_entry.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        self.pwd_entry.bind("<Return>", lambda e: self._submit())

        self.confirm_entry = None
        if self.is_first_run:
            self.confirm_entry = ctk.CTkEntry(
                inner, placeholder_text="Confirmar contraseña",
                show="●", height=44, font=FONT_BODY,
                corner_radius=RADIUS,
            )
            self.confirm_entry.grid(row=1, column=0, sticky="ew", pady=(0, 10))
            self.confirm_entry.bind("<Return>", lambda e: self._submit())

        label_btn = "Crear krypta" if self.is_first_run else "Entrar"
        ctk.CTkButton(
            inner, text=label_btn, height=44, font=FONT_BODY,
            corner_radius=RADIUS, fg_color=ACCENT,
            hover_color=ACCENT_HOV, command=self._submit,
        ).grid(row=2, column=0, sticky="ew", pady=(4, 0))

        self.error_label = ctk.CTkLabel(
            self, text="", font=FONT_SMALL, text_color=DANGER,
        )
        self.error_label.grid(row=4, column=0, pady=(10, 0))

    def _submit(self):
        pwd = self.pwd_entry.get()

        if self.is_first_run:
            confirm = self.confirm_entry.get() if self.confirm_entry else ""
            if len(pwd) < 8:
                self._error("Mínimo 8 caracteres.")
                return
            if pwd != confirm:
                self._error("Las contraseñas no coinciden.")
                return
            key = register_master(pwd)
            self.on_success(key)
        else:
            key = login(pwd)
            if key:
                self.on_success(key)
            else:
                self._error("Contraseña incorrecta.")
                self.pwd_entry.delete(0, "end")

    def _error(self, msg: str):
        self.error_label.configure(text=msg)


class AddView(ctk.CTkToplevel):
    def __init__(self, master, key: bytes, on_save, entry: dict = None):
        super().__init__(master)
        self.key      = key
        self.on_save  = on_save
        self.entry    = entry

        title = "Editar entrada" if entry else "Nueva entrada"
        self.title(title)
        self.geometry("420x380")
        self.resizable(False, False)
        self.configure(fg_color=BG)
        self._build()

        self.after(100, self.grab_set)

    def _build(self):
        self.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            self,
            text="Editar entrada" if self.entry else "Nueva entrada",
            font=FONT_TITLE, text_color=TEXT,
        ).grid(row=0, column=0, pady=(28, 20), padx=32, sticky="w")

        inner = ctk.CTkFrame(self, fg_color="transparent")
        inner.grid(row=1, column=0, padx=32, sticky="ew")
        inner.grid_columnconfigure(0, weight=1)

        def labeled_entry(row, placeholder, show=None):
            e = ctk.CTkEntry(
                inner, placeholder_text=placeholder,
                height=42, font=FONT_BODY,
                corner_radius=RADIUS, show=show or "",
            )
            e.grid(row=row, column=0, sticky="ew", pady=(0, 10))
            return e

        self.svc_entry  = labeled_entry(0, "Servicio  (ej: GitHub)")
        self.user_entry = labeled_entry(1, "Usuario   (ej: tu@email.com)")
        self.pass_entry = labeled_entry(2, "Contraseña", show="●")

        if self.entry:
            self.svc_entry.insert(0, self.entry["service"])
            self.svc_entry.configure(state="disabled")   # no cambiar servicio
            self.user_entry.insert(0, self.entry.get("username") or "")

        btn_row = ctk.CTkFrame(inner, fg_color="transparent")
        btn_row.grid(row=3, column=0, sticky="ew", pady=(8, 0))
        btn_row.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(
            btn_row, text="Cancelar", height=42,
            font=FONT_BODY, corner_radius=RADIUS,
            fg_color=BG3, hover_color=BG2,
            text_color=TEXT_MUTED, command=self.destroy,
        ).grid(row=0, column=0, sticky="ew", padx=(0, 6))

        label_save = "Guardar cambios" if self.entry else "Guardar"
        ctk.CTkButton(
            btn_row, text=label_save, height=42,
            font=FONT_BODY, corner_radius=RADIUS,
            fg_color=ACCENT, hover_color=ACCENT_HOV,
            command=self._save,
        ).grid(row=0, column=1, sticky="ew", padx=(6, 0))

        self.error_label = ctk.CTkLabel(
            self, text="", font=FONT_SMALL, text_color=DANGER,
        )
        self.error_label.grid(row=2, column=0, pady=(8, 0))

    def _save(self):
        service  = self.svc_entry.get().strip()
        username = self.user_entry.get().strip()
        password = self.pass_entry.get()

        if not service:
            self.error_label.configure(text="El servicio es obligatorio.")
            return
        if not password:
            self.error_label.configure(text="La contraseña es obligatoria.")
            return

        if self.entry:
            from krypta_ops import update_entry
            update_entry(self.entry["uuid"], service, username, password, self.key)
        else:
            add_entry(service, username, password, self.key)

        self.on_save()
        self.destroy()

class KryptaView(ctk.CTkFrame):
    def __init__(self, master, key: bytes):
        super().__init__(master, fg_color=BG)
        self.key     = key
        self.entries = []
        self._build()
        self._load_entries()

    def _build(self):
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        top = ctk.CTkFrame(self, fg_color=BG2, corner_radius=0, height=64)
        top.grid(row=0, column=0, sticky="ew")
        top.grid_columnconfigure(1, weight=1)
        top.grid_propagate(False)

        ctk.CTkLabel(
            top, text="🔐 Krypta", font=("Segoe UI", 16, "bold"),
            text_color=TEXT,
        ).grid(row=0, column=0, padx=20, pady=18)

        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", lambda *_: self._load_entries())

        search = ctk.CTkEntry(
            top, placeholder_text="🔍  Buscar servicio...",
            textvariable=self.search_var,
            height=36, font=FONT_BODY, corner_radius=RADIUS,
        )
        search.grid(row=0, column=1, padx=12, pady=14, sticky="ew")

        ctk.CTkButton(
            top, text="＋", width=42, height=36,
            font=("Segoe UI", 18), corner_radius=RADIUS,
            fg_color=ACCENT, hover_color=ACCENT_HOV,
            command=self._open_add,
        ).grid(row=0, column=2, padx=(0, 16), pady=14)

        self.list_frame = ctk.CTkScrollableFrame(
            self, fg_color=BG, corner_radius=0,
        )
        self.list_frame.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
        self.list_frame.grid_columnconfigure(0, weight=1)

        self.status_label = ctk.CTkLabel(
            self, text="", font=FONT_SMALL, text_color=TEXT_MUTED, height=28,
        )
        self.status_label.grid(row=2, column=0, pady=(0, 6))

    def _load_entries(self):
        q = self.search_var.get().strip()
        self.entries = list_entries(q)
        self._render_entries()

    def _render_entries(self):
        for w in self.list_frame.winfo_children():
            w.destroy()

        if not self.entries:
            ctk.CTkLabel(
                self.list_frame,
                text="Sin resultados" if self.search_var.get() else "Krypta vacío — añade tu primera contraseña",
                font=FONT_BODY, text_color=TEXT_MUTED,
            ).grid(row=0, column=0, pady=40)
            self.status_label.configure(text="")
            return

        for i, entry in enumerate(self.entries):
            self._entry_row(i, entry)

        n = len(self.entries)
        self.status_label.configure(text=f"{n} entrada{'s' if n != 1 else ''}")

    def _entry_row(self, row: int, entry: dict):
        card = ctk.CTkFrame(
            self.list_frame, fg_color=BG2,
            corner_radius=RADIUS, height=64,
        )
        card.grid(row=row, column=0, sticky="ew", padx=16, pady=(6, 0))
        card.grid_columnconfigure(1, weight=1)
        card.grid_propagate(False)

        ctk.CTkLabel(
            card, text="🔑", font=("Segoe UI", 20),
        ).grid(row=0, column=0, padx=(16, 10), pady=18)

        info = ctk.CTkFrame(card, fg_color="transparent")
        info.grid(row=0, column=1, sticky="ew", pady=12)

        ctk.CTkLabel(
            info, text=entry["service"],
            font=("Segoe UI", 14, "bold"), text_color=TEXT,
            anchor="w",
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            info,
            text=entry.get("username") or "sin usuario",
            font=FONT_SMALL, text_color=TEXT_MUTED,
            anchor="w",
        ).grid(row=1, column=0, sticky="w")

        btns = ctk.CTkFrame(card, fg_color="transparent")
        btns.grid(row=0, column=2, padx=12, pady=12)

        ctk.CTkButton(
            btns, text="Copiar", width=76, height=32,
            font=FONT_SMALL, corner_radius=8,
            fg_color=BG3, hover_color=ACCENT,
            text_color=TEXT,
            command=lambda e=entry: self._copy(e),
        ).grid(row=0, column=0, padx=(0, 6))

        ctk.CTkButton(
            btns, text="Editar", width=70, height=32,
            font=FONT_SMALL, corner_radius=8,
            fg_color=BG3, hover_color=ACCENT,
            text_color=TEXT,
            command=lambda e=entry: self._open_edit(e),
        ).grid(row=0, column=1, padx=(0, 6))

        ctk.CTkButton(
            btns, text="✕", width=32, height=32,
            font=FONT_SMALL, corner_radius=8,
            fg_color=BG3, hover_color=DANGER,
            text_color=TEXT_MUTED,
            command=lambda e=entry: self._delete(e),
        ).grid(row=0, column=2)

    def _copy(self, entry: dict):
        pwd = get_password(entry["uuid"], self.key)
        if pwd:
            copy_to_clipboard(pwd, clear_after=30)
            self._flash_status(f"✓ Copiado: {entry['service']} — se borrará en 30s")
        else:
            messagebox.showerror("Error", "No se pudo descifrar la contraseña.")

    def _delete(self, entry: dict):
        ok = messagebox.askyesno(
            "Eliminar",
            f"¿Eliminar '{entry['service']}'?\nEsta acción no se puede deshacer.",
        )
        if ok:
            delete_entry(entry["uuid"])
            self._load_entries()

    def _open_add(self):
        AddView(self.winfo_toplevel(), self.key, self._load_entries)

    def _open_edit(self, entry: dict):
        AddView(self.winfo_toplevel(), self.key, self._load_entries, entry=entry)

    def _flash_status(self, msg: str, duration: int = 4000):
        self.status_label.configure(text=msg, text_color=ACCENT)
        self.after(duration, lambda: self.status_label.configure(
            text="", text_color=TEXT_MUTED,
        ))

class KryptaApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Krypta")
        self.geometry("680x520")
        self.minsize(520, 420)
        self.configure(fg_color=BG)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        init_db()
        self._show_login()

    def _show_login(self):
        self._clear()
        LoginView(self, on_success=self._show_krypta).grid(
            row=0, column=0, sticky="nsew",
        )

    def _show_krypta(self, key: bytes):
        self._clear()
        KryptaView(self, key=key).grid(
            row=0, column=0, sticky="nsew",
        )

    def _clear(self):
        for w in self.winfo_children():
            w.destroy()

def run():
    app = KryptaApp()
    app.mainloop()

