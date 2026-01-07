Subqueries are queries placed **inside** another query. They allow SQL to answer questions that depend on the result of a separate calculation or lookup. Subqueries can return a **single value**, a **list of values**, or even behave like a **temporary table** inside a larger query.

Subqueries make complex logic easier to express without creating additional tables or rewriting duplicate logic.

### Scalar Subqueries
A scalar subquery **returns exactly one value**.
It can be used anywhere a normal value can appear—SELECT, WHERE, HAVING, even ORDER BY.

Example: find all countries with a population smaller than Japan’s:
```sql
SELECT Name, Population
FROM Countries
WHERE Population < (
    SELECT Population 
    FROM Countries 
    WHERE Name = 'Japan'
);
```
The inner query returns Japan’s population, and the outer query compares each row to that value.


### Table Subqueries
A **table subquery** returns multiple rows or columns.
These are often paired with IN, EXISTS, or placed in the FROM clause as a derived table.

Example: find all people who live in countries located in Oceania:
```sql
SELECT Name, Age
FROM People
WHERE CountryID IN (
    SELECT CountryID 
    FROM Countries 
    WHERE Region = 'Oceania'
);
```

The inner query produces a list of CountryIDs; the outer query filters using that list.

### Correlated Subqueries
A correlated subquery depends on the current row from the outer query.
Instead of running once, it runs once per row, allowing row-by-row comparison.

Example: find cities whose population is above the average population of cities in the same country:
```sql 
SELECT c.Name, c.Population
FROM Cities c
WHERE c.Population >
    (SELECT AVG(c2.Population)
     FROM Cities c2
     WHERE c2.CountryID = c.CountryID);
```

Here, the inner query calculates the **average population for that city’s country**, changing for each row in the outer query.
This kind of logic is useful for:
- comparing a row to a group it belongs to
- finding top/bottom performers within categories
- building hierarchical comparisons without joins

Subqueries—especially correlated ones—unlock advanced filtering and comparison techniques. They help express complex logic cleanly, reduce temporary table usage, and make SQL queries more modular and readable.

### **Exercise**
