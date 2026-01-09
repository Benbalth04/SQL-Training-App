A **recursive CTE** is a special type of Common Table Expression that repeatedly runs a query until a stopping condition is met. It is defined using **WITH RECURSIVE** and always has two parts: a **base query** (the starting point) and a **recursive query** (the part that repeats).

The recursive query references the CTE itself and builds on the results from the previous step. Each iteration adds new rows until the **termination condition** is reached. This pattern is useful for walking hierarchies, generating sequences, or performing repeated calculations.

In SQLite, recursive CTEs must use **UNION ALL** to combine the base and recursive parts. Care must be taken to ensure the recursion stops, otherwise the query will run indefinitely.

The example below uses the `Countries` table and assigns an increasing **level** number to each country, stopping after three iterations:

```sql
WITH RECURSIVE CountryLevels AS (
    SELECT Name, Population, 1 AS level
    FROM Countries
    UNION ALL
    SELECT Name, Population, level + 1
    FROM CountryLevels
    WHERE level < 3
)
SELECT * FROM CountryLevels;
```

Recursive CTEs are advanced SQL features. Always ensure your recursive condition is clear and limited to avoid performance issues.

### **Exercise**

