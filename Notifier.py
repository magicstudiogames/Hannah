from win10toast import ToastNotifier
import time


class Notifier:
    def __init__(self):
        self.toaster = ToastNotifier()
        self.last_notification = 0
        self.notification_limit = 5  # Máximo de notificações por hora

    def notify(self, title, message, dangerous=False):
        """Exibe notificação com opção de aprovação para ações perigosas."""
        current_time = time.time()
        if current_time - self.last_notification >= 3600 / self.notification_limit:
            self.toaster.show_toast(title, message, duration=10)
            self.last_notification = current_time
            if dangerous:
                response = input(f"{message}\nDigite 'sim' para prosseguir ou 'nao' para cancelar: ").lower()
                return response == 'sim'
            return True
        return False
