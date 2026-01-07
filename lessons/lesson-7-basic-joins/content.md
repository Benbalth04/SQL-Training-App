In this lesson, we will explore **basic joins** in SQL. Joins allow you to combine data from multiple tables based on a related column, usually a **primary key and foreign key relationship**. The most common type of join is the **INNER JOIN**, which returns rows that have matching values in both tables.

For example, suppose we have the following tables:

### Countries Table
| CountryID | Name      |
|-----------|-----------|
| 1         | Australia |
| 2         | Canada    |
| 3         | Japan     |

### Cities Table
| CityID | Name      | CountryID |
|--------|-----------|-----------|
| 1      | Sydney    | 1         |
| 2      | Melbourne | 1         |
| 3      | Toronto   | 2         |
| 4      | Tokyo     | 3         |
| 5      | Berlin    | 5         |

To list all cities along with their country names, you can join the **Cities** table with the **Countries** table using the **CountryID** column:

```sql 
SELECT Cities.Name AS CityName, Countries.Name AS CountryName
FROM Cities
INNER JOIN Countries
ON Cities.CountryID = Countries.CountryID;
```

The **INNER JOIN** ensures that only cities with a valid matching country are included. The query result would look like this:

| CityName  | CountryName |
|-----------|-------------|
| Sydney    | Australia   |
| Melbourne | Australia   |
| Toronto   | Canada      |
| Tokyo     | Japan       |

Notice that **Berlin is excluded** because its CountryID (5) does not exist in the **Countries** table.

You can also use table aliases to make your query shorter and more readable:

```sql 
SELECT c.Name AS CityName, co.Name AS CountryName
FROM Cities c
INNER JOIN Countries co
ON c.CountryID = co.CountryID;
```

Remember, INNER JOIN only returns rows with matches in both tables. This is different from a LEFT JOIN, which keeps all rows from the left table even if there is no match — we will cover that in the next lesson.

### **Exercise**