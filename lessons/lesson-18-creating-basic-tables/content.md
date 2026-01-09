In this lesson, we learn how to **create basic tables** in SQL using the **CREATE TABLE** statement. Defining tables correctly is essential to store and organise data effectively.

A table consists of **columns**, each with a **data type**, and optionally, constraints like **PRIMARY KEY** to ensure unique identifiers:

```sql 
CREATE TABLE Countries (
    CountryID INTEGER PRIMARY KEY AUTOINCREMENT,
    Name TEXT NOT NULL,
    Region TEXT NOT NULL,
    Population INTEGER NOT NULL
);
```
- **INTEGER, TEXT, and REAL** are common data types.
- **PRIMARY KEY** ensures each row is unique.
- **NOT NULL** prevents empty values in a column.
- **AUTOINCREMENT** automatically generates unique IDs for new rows.

You can also create a simple table with fewer constraints for practice:
```sql
CREATE TABLE Sample (
    ID INTEGER PRIMARY KEY,
    Description TEXT
);
```
Understanding table creation is fundamental before inserting, updating, or querying data. It lays the groundwork for structured and reliable databases.

### **Exercise**