In this lesson, we learn how to create multiple related tables and define FOREIGN KEY constraints to maintain data integrity. Foreign keys link rows in one table to rows in another, ensuring relationships between tables are consistent.

For example, the Cities table references the Countries table using CountryID as a foreign key:

```sql
CREATE TABLE Countries (
    CountryID INTEGER PRIMARY KEY AUTOINCREMENT,
    Name TEXT NOT NULL,
    Region TEXT NOT NULL,
    Population INTEGER NOT NULL
);

CREATE TABLE Cities (
    CityID INTEGER PRIMARY KEY AUTOINCREMENT,
    Name TEXT NOT NULL,
    CountryID INTEGER NOT NULL,
    Population INTEGER,
    FOREIGN KEY (CountryID) REFERENCES Countries(CountryID)
);
```

Key Points 
- PRIMARY KEY ensures each row is unique.
- FOREIGN KEY links tables and enforces referential integrity.
- NOT NULL ensures columns must have values.
- You can define multiple tables in a single script to model related data.

Creating multiple tables correctly is important for relational database design, avoiding orphaned rows, and enabling meaningful joins.

### Exercise
