Common Table Expressions (**CTEs**) allow you to structure SQL queries in cleaner, modular steps using the WITH clause. A CTE acts like a temporary, named result set that exists only for the duration of the query. This makes complex logic easier to read, debug, and maintain—especially when the query has multiple stages or repeated calculations.

### Basic CTE Structure 
A CTE works like a labelled subquery:
```sql
WITH AvgPopulation AS (
    SELECT AVG(Population) AS AvgPop
    FROM Countries
)
SELECT Name, Population
FROM Countries, AvgPopulation
WHERE Population > AvgPopulation.AvgPop;
```

The AvgPopulation CTE runs first, producing a single value.
The main query then uses that value to filter countries above the global average population.

### Chaining Multiple CTEs
You can define multiple CTEs in sequence. Each CTE can reference those defined before it, allowing you to build multi-step logic cleanly.
```sql
WITH CountryStats AS (
    SELECT 
        COUNT(*) AS CountryCount,
        SUM(Population) AS TotalPop
    FROM Countries
),
AboveAverage AS (
    SELECT 
        Name, 
        Population
    FROM Countries, CountryStats
    WHERE Population > (TotalPop / CountryCount)
)
SELECT *
FROM AboveAverage;
```
This example performs calculations in stages:
1. CountryStats computes totals.
2. AboveAverage uses those totals to filter the Countries table.
3. The final query simply selects from the prepared results.
Breaking complex queries into named steps like these keeps logic organised and avoids repeated calculations.

### Why Use CTEs?
CTEs provide several major benefits:
- **Readability** – Complex logic becomes clearer when broken into steps.
- **Reusability** – A CTE can be referenced multiple times without rewriting the same subquery.
- **Cleaner logic** – Replaces deeply nested subqueries with labelled, top-to-bottom structure.
- **Cleaner logic** – Replaces deeply nested subqueries with labelled, top-to-bottom structure.

They function like well-named variables for your query, making SQL far more maintainable as complexity grows.

### **Exercise**