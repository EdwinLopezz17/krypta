from app     import run
from updater import check_for_updates
import customtkinter as ctk

if __name__ == "__main__":
    run(on_ready=check_for_updates)
    