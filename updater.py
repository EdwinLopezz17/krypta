import threading
import webbrowser
import urllib.request
import urllib.error
import json
import customtkinter as ctk

CURRENT_VERSION  = "1.0.0"
GITHUB_USER      = "EdwinLopezz17"
GITHUB_REPO      = "krypta"
API_URL          = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/releases/latest"

BG = "#1a1a1a"
BG2 = "#242424"
BG3 = "#2e2e2e"
ACCENT = "#3b82f6"
DANGER = "#ef4444"
TEXT = "#f1f5f9"
TEXT_MUTED = "#94a3b8"
RADIUS = 10

def _parse_version(v: str) -> tuple[int, ...]:
    return tuple(int(x) for x in v.strip("v").split("."))


def _fetch_latest() -> dict | None:
    try:
        req = urllib.request.Request(
            API_URL,
            headers={"User-Agent": "Krypta-Updater"},
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode())
            return {
                "version": data["tag_name"],
                "url": data["html_url"],
            }
    except Exception:
        return None

class UpdateDialog(ctk.CTkToplevel):

    def __init__(self, master, latest_version: str, download_url: str):
        super().__init__(master)
        self.download_url = download_url

        self.title("Actualización disponible")
        self.geometry("400x220")
        self.resizable(False, False)
        self.configure(fg_color=BG)
        self.after(100, self.grab_set)

        self.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            self, text="Nueva versión disponible",
            font=("Segoe UI", 16, "bold"), text_color=TEXT,
        ).grid(row=0, column=0, pady=(28, 4))

        ctk.CTkLabel(
            self,
            text=f"Versión actual: {CURRENT_VERSION}\n"
                 f"Nueva versión: {latest_version}",
            font=("Segoe UI", 13), text_color=TEXT_MUTED,
            justify="left",
        ).grid(row=1, column=0, pady=(4, 20), padx=32, sticky="w")

        ctk.CTkLabel(
            self,
            text="Tu base de datos no se verá afectada.",
            font=("Segoe UI", 11), text_color=TEXT_MUTED,
        ).grid(row=2, column=0, pady=(0, 16))

        btns = ctk.CTkFrame(self, fg_color="transparent")
        btns.grid(row=3, column=0, padx=32, sticky="ew")
        btns.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(
            btns, text="Ahora no", height=40,
            font=("Segoe UI", 13), corner_radius=RADIUS,
            fg_color=BG3, hover_color=BG2, text_color=TEXT_MUTED,
            command=self.destroy,
        ).grid(row=0, column=0, sticky="ew", padx=(0, 6))

        ctk.CTkButton(
            btns, text="⬇  Descargar", height=40,
            font=("Segoe UI", 13), corner_radius=RADIUS,
            fg_color=ACCENT, hover_color="#2563eb",
            command=self._download,
        ).grid(row=0, column=1, sticky="ew", padx=(6, 0))

    def _download(self):
        webbrowser.open(self.download_url)
        self.destroy()


def check_for_updates(root: ctk.CTk) -> None:
    def _check():
        latest = _fetch_latest()
        if latest is None:
            return

        try:
            current = _parse_version(CURRENT_VERSION)
            remote  = _parse_version(latest["version"])
        except ValueError:
            return

        if remote > current:
            root.after(0, lambda: UpdateDialog(
                root,
                latest_version = latest["version"],
                download_url   = latest["url"],
            ))

    thread = threading.Thread(target=_check, daemon=True)
    thread.start()

