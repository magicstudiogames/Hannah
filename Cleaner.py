import os
import shutil
import sqlite3
from datetime import datetime, timedelta


class Cleaner:
    def __init__(self, db_path):
        self.db_path = db_path
        self.safe_extensions = {'.tmp', '.temp', '.cache', '.bak', '.log'}
        self.load_preferences()

    def load_preferences(self):
        """Carrega preferências de limpeza do banco de dados."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS preferences (key TEXT PRIMARY KEY, value TEXT)")
        cursor.execute("SELECT value FROM preferences WHERE key = 'safe_extensions'")
        result = cursor.fetchone()
        if result:
            self.safe_extensions.update(eval(result[0]))  # Carrega extensões personalizadas
        conn.close()

    def save_preference(self, key, value):
        """Salva preferências no banco de dados."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO preferences (key, value) VALUES (?, ?)", (key, str(value)))
        conn.commit()
        conn.close()

    def clear_cache(self):
        """Limpa arquivos de cache e temporários antigos de forma segura."""
        temp_dirs = [os.path.expandvars(r"%TEMP%"), os.path.expandvars(r"%SystemRoot%\Temp")]
        total_size = 0

        for temp_dir in temp_dirs:
            try:
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        try:
                            file_age = datetime.now() - datetime.fromtimestamp(os.path.getmtime(file_path))
                            if (file.lower().endswith(tuple(self.safe_extensions)) or file_age > timedelta(days=7)):
                                size = os.path.getsize(file_path) / (1024 * 1024)
                                os.remove(file_path)
                                total_size += size
                                self.save_preference(f"cleaned_{file}", str(file_age.days))
                        except PermissionError:
                            continue
                        except Exception as e:
                            print(f"Erro ao processar {file_path}: {str(e)}")
                            continue
                    for dir in dirs:
                        dir_path = os.path.join(root, dir)
                        try:
                            if not os.listdir(dir_path):
                                shutil.rmtree(dir_path)
                        except PermissionError:
                            continue
            except Exception as e:
                print(f"Erro ao processar {temp_dir}: {str(e)}")
                continue

        result = {"size": round(total_size, 2)}
        self.log_action("Limpeza de Cache", f"Limpei {result['size']} MB")
        return result

    def clear_temp_files(self):
        """Limpa arquivos temporários adicionais (ex.: lixeira, logs)."""
        # Implementação futura com aprovação manual para lixeira
        pass

    def log_action(self, action, result):
        """Registra a ação no banco de dados."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO actions (action, result, timestamp) VALUES (?, ?, ?)",
                       (action, result, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        conn.close()
