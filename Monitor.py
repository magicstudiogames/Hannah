import psutil
import sqlite3
from datetime import datetime
import os


class Monitor:
    def __init__(self, db_path, notifier):
        self.db_path = db_path
        self.notifier = notifier
        self.suspicious_patterns = {
            'crypto_mining': {
                'xmrig.exe', 'nicehash.exe', 'minerd.exe', 'cpuminer.exe', 'ethminer.exe',
                'ccminer.exe', 'cgminer.exe', 'nbminer.exe', 't-rex.exe'
            },
            'ransomware': {
                'wannacry.exe', 'notpetya.exe', 'locky.exe', 'revil.exe',
                'maze.exe', 'cerber.exe', 'ryuk.exe', 'darkside.exe'
            },
            'trojan': {
                'njrat.exe', 'darkcomet.exe', 'quasar.exe', 'remcos.exe', 'backdoor.exe',
                'poisonivy.exe', 'sub7.exe', 'zeus.exe', 'keylogger.exe'
            },
            'adware': {
                'couponprinter.exe', 'searchprotection.exe', 'adservice.exe',
                'dealply.exe', 'webdiscoverbrowser.exe'
            },
            'spyware': {
                'finfisher.exe', 'flexispy.exe', 'mspy.exe', 'spyagent.exe', 'spytech.exe'
            },
            'keylogger': {
                'keylogger.exe', 'spyrix.exe', 'actualkeylogger.exe', 'refog.exe'
            },
            'rootkit': {
                'tdss.exe', 'zeroaccess.exe', 'necurs.exe'
            },
            'worm': {
                'conficker.exe', 'blaster.exe', 'sasser.exe', 'iloveyou.exe'
            }
        }

        self.load_preferences()

    def load_preferences(self):
        """Carrega padrões de atividades suspeitas do banco de dados."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS preferences (key TEXT PRIMARY KEY, value TEXT)")
        cursor.execute("SELECT key, value FROM preferences WHERE key LIKE 'suspicious_%'")
        for key, value in cursor.fetchall():
            self.suspicious_patterns[key.replace('suspicious_', '')] = eval(value)
        conn.close()

    def save_preference(self, key, value):
        """Salva preferências no banco de dados."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO preferences (key, value) VALUES (?, ?)", (key, str(value)))
        conn.commit()
        conn.close()

    def check_system(self):
        """Monitora recursos e detecta atividades maliciosas."""
        cpu_usage = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        result = f"CPU: {cpu_usage}%, Memória: {memory.percent}%, Disco: {disk.percent}%"
        self.log_action("Monitoramento", result)

        if cpu_usage > 80:
            self.log_action("Aviso", "Uso de CPU alto. Otimização sugerida.")
        self.detect_malicious_activity()

    def detect_malicious_activity(self):
        """Detecta atividades suspeitas e notifica o usuário."""
        active_processes = {p.info['name'].lower() for p in psutil.process_iter(['name'])}
        for activity_type, patterns in self.suspicious_patterns.items():
            suspicious = active_processes & patterns
            if suspicious:
                for proc in suspicious:
                    details = f"Processo suspeito: {proc}, Tipo: {activity_type}, Local: {os.getcwd()}"
                    self.notifier.notify("Aviso de Segurança",
                                         f"{details}\nAção: Feche o programa ou escaneie com antivírus.")
                    self.save_preference(f"suspicious_{proc}", str(datetime.now()))
                    if input("Deseja encerrar o processo? (sim/nao): ").lower() == 'sim':
                        for p in psutil.process_iter(['name', 'pid']):
                            if p.info['name'].lower() == proc:
                                p.terminate()
                                self.log_action("Segurança", f"Encerrado {proc}")
                    break

    def log_action(self, action, result):
        """Registra a ação no banco de dados."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO actions (action, result, timestamp) VALUES (?, ?, ?)",
                       (action, result, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        conn.close()
