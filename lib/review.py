from __init__ import CURSOR, CONN
from employee import Employee

class Review:
  
    all = {}

    def __init__(self, year, summary, employee_id, id=None):
        self.id = id
        self.year = year
        self.summary = summary
        self.employee_id = employee_id

    def __repr__(self):
        return f"<Review {self.id}: {self.year}, {self.summary}, Employee: {self.employee_id}>"

    @classmethod
    def create_table(cls):
        sql = """
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY,
            year INTEGER,
            summary TEXT,
            employee_id INTEGER,
            FOREIGN KEY (employee_id) REFERENCES employees(id)
        );
        """
        CURSOR.execute(sql)
        CONN.commit()

    @classmethod
    def drop_table(cls):
        sql = "DROP TABLE IF EXISTS reviews;"
        CURSOR.execute(sql)
        CONN.commit()

    def save(self):
        sql = "INSERT INTO reviews (year, summary, employee_id) VALUES (?, ?, ?)"
        CURSOR.execute(sql, (self.year, self.summary, self.employee_id))
        CONN.commit()
        self.id = CURSOR.lastrowid
        Review.all[self.id] = self
        return self

    @classmethod
    def create(cls, year, summary, employee_id):
        review = cls(year, summary, employee_id)
        return review.save()

    @classmethod
    def instance_from_db(cls, row):
        id, year, summary, emp_id = row
        instance = cls.all.get(id)
        if instance:
            instance.year = year
            instance.summary = summary
            instance.employee_id = emp_id
        else:
            instance = cls(year, summary, emp_id, id=id)
            cls.all[id] = instance
        return instance

    @classmethod
    def find_by_id(cls, id):
        sql = "SELECT * FROM reviews WHERE id = ?"
        row = CURSOR.execute(sql, (id,)).fetchone()
        return cls.instance_from_db(row) if row else None

    def update(self):
        sql = "UPDATE reviews SET year = ?, summary = ?, employee_id = ? WHERE id = ?"
        CURSOR.execute(sql, (self.year, self.summary, self.employee_id, self.id))
        CONN.commit()
        Review.all[self.id] = self
        return self

    def delete(self):
        sql = "DELETE FROM reviews WHERE id = ?"
        CURSOR.execute(sql, (self.id,))
        CONN.commit()
        Review.all.pop(self.id, None)
        self.id = None

    @classmethod
    def get_all(cls):
        sql = "SELECT * FROM reviews"
        rows = CURSOR.execute(sql).fetchall()
        return [cls.instance_from_db(row) for row in rows]

    # --- properties for validation ---
    @property
    def year(self):
        return self._year

    @year.setter
    def year(self, value):
        if not isinstance(value, int) or value < 2000:
            raise ValueError("Year must be an integer >= 2000")
        self._year = value

    @property
    def summary(self):
        return self._summary

    @summary.setter
    def summary(self, text):
        if not isinstance(text, str) or not text.strip():
            raise ValueError("Summary must be a non-empty string")
        self._summary = text

    @property
    def employee_id(self):
        return self._employee_id

    @employee_id.setter
    def employee_id(self, emp_id):
        if not isinstance(emp_id, int) or Employee.find_by_id(emp_id) is None:
            raise ValueError("employee_id must reference a persisted Employee")
        self._employee_id = emp_id