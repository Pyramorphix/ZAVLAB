import sqlite3


class DatabaseManager:

    # ---------------------------------------------------
    def __init__(self, filename: str):
        self.database = sqlite3.connect(f"{filename}.db")
        self.create_tables()
        self.cursor = self.database.cursor()
    # ---------------------------------------------------



    # --------------------------------------------------------------------------------
    def create_tables(self):

        # Experiments
        # id | title
        self.database.execute('''
            CREATE TABLE IF NOT EXISTS experiments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                amount INTEGER NOT NULL
            )
        ''')


        # Fields
        # id | experiment_id | label | unit | type | error | formula | value
        self.database.execute('''
            CREATE TABLE IF NOT EXISTS fields (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                experiment_id INTEGER NOT NULL,
                label TEXT NOT NULL,
                unit TEXT,
                type TEXT NOT NULL CHECK(type IN ('gathered', 'calculated', 'const')),
                error TEXT,
                formula TEXT,
                value TEXT,
                FOREIGN KEY(experiment_id) REFERENCES experiments(id)
            )
        ''')


        # Data
        # id | experiment_id | field_id | row_num | value | error
        self.database.execute('''
            CREATE TABLE IF NOT EXISTS data_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                experiment_id INTEGER NOT NULL,
                field_id INTEGER NOT NULL,
                row_num INTEGER NOT NULL,
                value TEXT,
                error TEXT,
                FOREIGN KEY(experiment_id) REFERENCES experiments(id),
                FOREIGN KEY(field_id) REFERENCES fields(id),
                UNIQUE(experiment_id, field_id, row_num)
            )
        ''')


        # Write changes to file
        self.database.commit()
    # --------------------------------------------------------------------------------



    # ---------------------------------------------
    def add_experiment(self, experiment):
        self.cursor.execute('''
            INSERT INTO experiments (title, amount)
            VALUES (?, ?)
        ''', (experiment.title, experiment.amount))
        experiment.id = self.cursor.lastrowid
        self.database.commit()
    # ---------------------------------------------



    # -----------------------------------------------------------------
    def add_field(self, experiment_id, field):
        self.cursor.execute('''
            INSERT INTO fields (
                experiment_id, label, unit, type, error, formula, value
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            experiment_id,
            field.label,
            field.unit,
            field.field_type,
            field.error,
            field.formula,
            field.value
        ))
        field.id = self.cursor.lastrowid
        self.database.commit()
    # -----------------------------------------------------------------



    # ----------------------------------------------------------------------------------
    def save_data_entry(self, experiment_id, field_id, row_num, value=None, error=None):
        self.database.execute('''
            INSERT OR REPLACE INTO data_entries (
                experiment_id, field_id, row_num, value, error
            ) VALUES (?, ?, ?, ?, ?)
        ''', (experiment_id, field_id, row_num, value, error))
        self.database.commit()
    # ----------------------------------------------------------------------------------



    # -----------------------------------------------------------------------
    def get_experiment_data(self, experiment_id):
        self.cursor.execute('''
            SELECT f.id, f.type, f.label, f.unit, d.row_num, d.value, d.error
            FROM fields f
            LEFT JOIN data_entries d ON f.id = d.field_id
            WHERE f.experiment_id = ?
        ''', (experiment_id,))
        return self.cursor.fetchall()
    # -----------------------------------------------------------------------



