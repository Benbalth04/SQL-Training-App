Advanced join patterns go beyond simple key-to-key matching. These techniques are useful for modelling **hierarchical relationships**, comparing rows within the same table, or joining based on **ranges** instead of exact equality.

### Self Joins
A self join occurs when a table is joined to itself. This allows you to compare rows within the same table or represent hierarchical relationships. Common use cases include:
- Finding employees and their managers
- Comparing attributes of different cities
- Linking countries with neighbouring countries (if stored in a single table)

```sql
-- Example: Find each person and their manager.
SELECT 
    p.Name AS Person,
    m.Name AS Manager
FROM People p
LEFT JOIN People m ON p.ManagerID = m.PersonID;
```
Here, the table People is used twice with aliases p and m. The LEFT JOIN ensures that people without a manager are still included, with Manager showing NULL.

### Multi-Join Conditions
Sometimes, a join needs more than one condition to match rows correctly. You can combine multiple conditions using AND or other logical operators.

```sql 
-- Example: Match cities to countries by both country ID and a region constraint:
SELECT *
FROM Cities c
JOIN Countries co
    ON c.CountryID = co.CountryID
   AND c.Region = co.Region;
```
Using multiple conditions ensures that the join only returns rows meeting all criteria, which reduces incorrect matches.

### Non-Equijoins (Range Joins)
A non-equijoin matches rows based on inequality conditions rather than exact equality (=). This is useful for scenarios like classification systems, pricing tiers, or time-range logic.

```sql
-- Example: Match people to countries based on age ranges:
SELECT 
    p.Name,
    c.CountryName
FROM People p
JOIN Countries c
    ON p.Age BETWEEN c.MinAge AND c.MaxAge;
```
Here, the join uses a range condition (BETWEEN) instead of a simple equality. Non-equijoins allow flexible relationships where exact matches are not sufficient.

Advanced joins like these are powerful tools for analysing complex relationships, hierarchies, and conditional groupings in your datasets. They expand the scenarios where SQL can combine and interpret data meaningfully.

### Cross Joins
A cross join returns the Cartesian product of two tables — every row from the first table is combined with every row from the second table. Unlike other joins, a cross join does not use a join condition.
Cross joins are useful when you intentionally need to **generate all possible combinations**, such as:
- Creating date or time grids
- Generating test data
- Expanding dimensions (e.g. every product × every region)

```sql
-- Example: Generate all combinations of products and regions
SELECT 
    p.ProductName,
    r.RegionName
FROM Products p
CROSS JOIN Regions r;
```
If Products has 10 rows and Regions has 5 rows, the result will contain 50 rows.

**Important**: Because row counts multiply quickly, cross joins can become extremely expensive if used unintentionally. Always be certain that a Cartesian product is what you want.

### **Exercise**
