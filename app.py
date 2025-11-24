from .database import Database
from .main_ui import MainApp
from .dialogs import LoginDialog, PolicyDialog

# Startup script

def run_app():
    db = Database()
    app = MainApp(db)

    # Show policy and login dialogs before mainloop
    pol = PolicyDialog(app)
    app.wait_window(pol)
    if not pol.accepted:
        print('Policy not accepted. Exiting.')
        return

    login = LoginDialog(app, db)
    app.wait_window(login)
    if not getattr(login, 'success', False):
        print('Login failed or cancelled. Exiting.')
        return

    app.mainloop()


if __name__ == '__main__':
    run_app()
