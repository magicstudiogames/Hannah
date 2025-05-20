import schedule
import time
import sqlite3
from Cleaner import Cleaner
from Optimizer import Optimizer
from Monitor import Monitor
from Notifier import Notifier

import ctypes


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


if not is_admin():
    print("Por favor, execute este script como administrador.")
    import sys

    sys.exit(1)


class Hannah:
    def __init__(self):
        self.db_path = "hannah.db"
        self.setup_database()
        self.notifier = Notifier()
        self.cleaner = Cleaner(self.db_path)
        self.optimizer = Optimizer(self.db_path)
        self.monitor = Monitor(self.db_path, self.notifier)

    def setup_database(self):
        """Configura o banco de dados SQLite."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS actions
                         (id INTEGER PRIMARY KEY, action TEXT, result TEXT, timestamp TEXT)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS preferences
                         (key TEXT PRIMARY KEY, value TEXT)''')
        conn.commit()
        conn.close()

    def automate_tasks(self):
        """Decide e executa tarefas automaticamente com base em padrões."""
        # Limpeza automática
        result = self.cleaner.clear_cache()
        if result['size'] > 0:
            self.notifier.notify("Limpeza Automática", f"Limpei {result['size']} MB")

        # Otimização automática
        self.optimizer.optimize_processes()

        # Monitoramento contínuo
        self.monitor.check_system()

    def main_loop(self):
        """Loop principal com automação e aprendizado."""
        schedule.every(1).hour.do(self.automate_tasks)
        schedule.every(5).minutes.do(self.monitor.check_system)
        schedule.every(1).minutes.do(self.optimizer.optimize_processes)

        self.automate_tasks()  # Executa no início

        try:
            while True:
                schedule.run_pending()
                time.sleep(60)
        except KeyboardInterrupt:
            print("Interrompido pelo usuário. Encerrando...")
        except Exception as e:
            self.notifier.notify("Erro Crítico", f"Loop interrompido: {str(e)}")


if __name__ == "__main__":
    hannah = Hannah()
    hannah.main_loop()
