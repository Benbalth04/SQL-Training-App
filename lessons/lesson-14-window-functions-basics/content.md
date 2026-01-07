Window functions allow you to perform calculations **across related rows while still keeping each row visible**. This makes them different from normal aggregate functions, which collapse rows into a single summary value. With window functions, you can compute totals, averages, rankings, and comparisons directly alongside the original data.

At the core of every window function is the **OVER()** clause, which defines how the window is applied.

### OVER() Basics
A window function follows the pattern:
```sql
AGGREGATE_FUNCTION(...) OVER (...)
```

Inside OVER(), you can specify:
- **PARTITION BY** → divides rows into groups
- **ORDER BY** → sets the row order for calculations
- (optional) **frame clauses** → define exactly which rows contribute to each calculation
Even without PARTITION BY or ORDER BY, the window function still evaluates per row—but using the entire table as a single window.

### Example: Running Totals with ORDER BY
Using ORDER BY inside the window defines the sequence in which calculations occur. A running total, for example:
```sql
SELECT 
    Name, 
    Population,
    SUM(Population) OVER (ORDER BY Population) AS RunningTotal
FROM Countries;
```
Each row’s RunningTotal includes the populations of all countries up to that point.
Unlike GROUP BY, every row remains in the output.

### Partitioned Calculations
**PARTITION BY** limits each calculation to a specific group, producing independent windows inside the same query.
For example, computing the total population within each region:
```sql
SELECT 
    Name, 
    Region, 
    Population,
    SUM(Population) OVER (PARTITION BY Region) AS RegionTotal
FROM Countries;
```
Each region gets its own subtotal, and each row still shows the individual country.

### Other Window Functions
Window functions are not limited to SUM. Nearly all aggregate functions can be used with a window, including:
- AVG() — moving averages or group-level averages
- MIN() / MAX() — find range values for each partition
- COUNT() — count of rows within each region
- Ranking functions (ROW_NUMBER, RANK, DENSE_RANK)

Example—ranking countries by population within each region:
```sql
SELECT 
    Name,
    Region,
    Population,
    RANK() OVER (PARTITION BY Region ORDER BY Population DESC) AS PopRankInRegion
FROM Countries;
```
This keeps every row but adds a ranking column that depends on neighbouring rows.

Window functions are one of the most efficient ways to layer analytical calculations directly into SQL while maintaining full row-level detail. They are foundational for reporting, time-series analysis, and complex comparisons.

### **Exercise**