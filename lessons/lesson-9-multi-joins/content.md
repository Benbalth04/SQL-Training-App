Sometimes, information is spread across more than two tables, and combining them requires **multi-table joins**. You can chain multiple **INNER JOINs** to link three or more tables.

For example, to list people along with their city and country names:

```sql
SELECT p.Name AS PersonName, c.Name AS CityName, co.Name AS CountryName
FROM People p
INNER JOIN Cities c
ON p.CityID = c.CityID
INNER JOIN Countries co
ON c.CountryID = co.CountryID;
```
Each join follows a key relationship: People → Cities → Countries.
- **Join order** matters for clarity and correctness, especially when chaining multiple tables.
- **Aliasing** helps shorten table names and makes the query easier to read.

Check that each join references the correct keys to avoid mismatched or missing data. Multi-table joins are crucial when analysing datasets that are **related but stored in separate tables**, such as people, cities, and countries.

### **Exercise**