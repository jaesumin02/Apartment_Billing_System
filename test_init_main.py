import traceback
import sys
from database import Database
from ui.main_app import MainApp

if __name__ == '__main__':
    try:
        db = Database()
        app = MainApp(db)
        app.update()
        print('MainApp constructed and updated successfully')
        app.destroy()
        db.close()
    except Exception:
        traceback.print_exc()
        sys.exit(1)
