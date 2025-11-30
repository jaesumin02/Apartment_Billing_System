import customtkinter as ctk
from database import Database
from dialogs import LoginDialog, PolicyDialog
from ui.main_app import MainApp
from constants import DEFAULT_APPEARANCE, DEFAULT_COLOR_THEME

ctk.set_appearance_mode(DEFAULT_APPEARANCE)
ctk.set_default_color_theme(DEFAULT_COLOR_THEME)

def main():
    db = Database()
    root = ctk.CTk()
    root.withdraw()

    policy = PolicyDialog(root)
    root.wait_window(policy)

    login = LoginDialog(root, db)
    root.wait_window(login)
    if not getattr(login, 'success', False):
        root.destroy()
        db.close()
        return

    root.destroy()

    while True:
        app = MainApp(db)
        app.mainloop()
        if not getattr(app, 'logout_requested', False):
            break
        new_root = ctk.CTk()
        new_root.withdraw()
        login = LoginDialog(new_root, db)
        new_root.wait_window(login)
        if not getattr(login, 'success', False):
            new_root.destroy()
            break
        new_root.destroy()

    db.close()


if __name__ == '__main__':
    main()
