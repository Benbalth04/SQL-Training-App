In this lesson, we cover changing data in tables using basic DML (Data Manipulation Language) commands: INSERT, UPDATE, DELETE, and DROP. These commands let you add, modify, remove, or delete entire tables.

INSERT adds new rows to a table:
```sql
INSERT INTO Countries (Name, Region, Population)
VALUES ('France', 'Europe', 67000000);
```

UPDATE modifies existing rows:
```sql
UPDATE Countries
SET Population = 68000000
WHERE Name = 'France';
```

DELETE removes rows:
```sql
DELETE FROM Countries
WHERE Name = 'France';
```

DROP TABLE removes the table and all its data:
```sql
DROP TABLE Countries;
```

Understanding these commands is fundamental for managing your database and keeping your data accurate and up to date.
### **Exercise**