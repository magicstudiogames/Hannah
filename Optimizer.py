import psutil
import sqlite3
from datetime import datetime
import win32gui


class Optimizer:
    def __init__(self, db_path):
        self.db_path = db_path
        self.critical_processes = {'explorer.exe', 'svchost.exe', 'csrss.exe', 'winlogon.exe'}
        self.context_patterns = {'gaming': {'notepad.exe', 'chrome.exe'},
                                 'editing': {'photoshop.exe', 'gimp.exe'},
                                 'programming': {'vscode.exe', 'pycharm.exe'}}
        self.load_preferences()

    def load_preferences(self):
        """Carrega preferências de otimização do banco de dados."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS preferences (key TEXT PRIMARY KEY, value TEXT)")
        cursor.execute("SELECT key, value FROM preferences WHERE key LIKE 'context_%'")
        for key, value in cursor.fetchall():
            self.context_patterns[key.replace('context_', '')] = eval(value)
        conn.close()

    def save_preference(self, key, value):
        """Salva preferências no banco de dados."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO preferences (key, value) VALUES (?, ?)", (key, str(value)))
        conn.commit()
        conn.close()

    def detect_context(self):
        """Detecta o contexto de uso com base em processos ativos."""
        active_processes = {p.info['name'].lower() for p in psutil.process_iter(['name'])}
        for context, patterns in self.context_patterns.items():
            if any(p in active_processes for p in patterns):
                return context
        return 'general'

    def optimize_processes(self):
        """Ajusta prioridades de processos com base no contexto."""
        context = self.detect_context()
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
            try:
                process_name = proc.info['name'].lower()
                if (proc.info['cpu_percent'] > 80 and
                        not self.is_foreground_process(proc) and
                        process_name not in self.critical_processes):
                    if context == 'gaming' and process_name not in self.context_patterns['gaming']:
                        proc.nice(psutil.HIGH_PRIORITY_CLASS)  # Prioridade alta para jogos
                    elif context in ['editing', 'programming'] and process_name not in self.critical_processes:
                        proc.nice(psutil.NORMAL_PRIORITY_CLASS)  # Normal para edição/programação
                    else:
                        proc.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
                    self.log_action("Otimização", f"Otimizado {process_name} para {context}")
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

    def optimize_startup_programs(self):
        """Otimiza programas de inicialização com aprovação manual."""
        # Simulação de ação perigosa
        startup_items = []  # Placeholder para lista de programas de inicialização
        if startup_items:
            self.notifier.notify("Ação Perigosa", "Deseja otimizar programas de inicialização?")
            if input("Digite 'sim' para prosseguir: ").lower() == 'sim':
                # Implementação futura com win32api/registry
                self.log_action("Otimização Inicialização", "Programas otimizados")
            else:
                self.log_action("Otimização Inicialização", "Cancelado pelo usuário")

    def is_foreground_process(self, process):
        """Verifica se o processo está em primeiro plano."""
        try:
            hwnd = win32gui.GetForegroundWindow()
            tid = win32gui.GetWindowThreadProcessId(hwnd)
            pid = process.info['pid']
            return pid in tid
        except Exception:
            return False

    def log_action(self, action, result):
        """Registra a ação no banco de dados."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO actions (action, result, timestamp) VALUES (?, ?, ?)",
                       (action, result, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        conn.close()

    def notifier(self):
        """Placeholder para notificador (será usado por Hannah)."""
        pass  # Substituído por injeção de dependência em Hannah
