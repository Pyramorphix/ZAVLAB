import json
import logging
from PyQt6.QtCore import QTimer, QObject
from PyQt6.QtWidgets import QApplication
import os

###Constants
TIMER_INTERVAL = 60000 # in ms = 1 minute

class AutoSaveManager(QObject):
    def __init__(self, parent=None, save_interval=TIMER_INTERVAL): 
        super().__init__(parent)
        self.save_interval = save_interval
        self.timer = QTimer()
        self.timer.timeout.connect(self.auto_save)
        self.timer.start(self.save_interval)
        
        log_dir = 'logs'
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        file_dir = 'files'
        if not os.path.exists(file_dir):
            os.makedirs(file_dir)

        logging.basicConfig(
            filename='logs/app_autosave.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
    
    def auto_save(self):
        try:
            sub_state = self.parent().plotter.get_state()  
            state = self.parent().get_state()
            self.save_to_file(sub_state, state)
            logging.info("Auto-save completed successfully")
        except Exception as e:
            logging.error(f"Auto-save error: {str(e)}")
    
    def save_to_file(self, sub_state, state, filename_subs="./files/autosave_backup_subplots.json", filename="./files/autosave_backup_table.json"):
        try:
            with open(filename_subs, 'w') as f:
                json.dump(sub_state, f, indent=4)
            # Creating a backup copy
            with open(f"{filename_subs}.backup", 'w') as f:
                json.dump(sub_state, f, indent=4)
            with open(filename, 'w') as f:
                json.dump(state, f, indent=4)
            # Creating a backup copy
            with open(f"{filename}.backup", 'w') as f:
                json.dump(state, f, indent=4)
        except Exception as e:
            logging.error(f"File recording error: {str(e)}")

    def load_backup(self, filename_subs="./files/sub_setting_final.json", filename="./files/settings_final.json", last_copy_subs="./files/autosave_backup_subplots.json", last_copy="./files/autosave_backup.json"):
        try:
            with open(filename_subs, 'r') as f:
                sub_state = json.load(f)
            with open(filename, 'r') as f:
                state = json.load(f)
            return (state, sub_state)
        except FileNotFoundError:
            logging.warning("The auto-save file was not found")
            return (None, None)
        except Exception as e:
            logging.error(f"File reading error: {str(e)}")
            # Пробуем загрузить из резервной копии
            try:
                with open(f"{last_copy_subs}.backup", 'r') as f:
                    sub_state = json.load(f)
                with open(f"{last_copy}.backup", 'r') as f:
                    state = json.load(f)
                return (state, sub_state)

            except Exception:
                return (None, None)
