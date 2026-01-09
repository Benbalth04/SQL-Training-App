Nested analytical queries combine **Common Table Expressions (CTEs)** with **window functions** to perform multi-step calculations while keeping the SQL readable and modular. This approach allows you to compute several metrics simultaneously without losing individual row details.

### Layering Metrics with CTEs
CTEs let you break down complex calculations into manageable steps. For example, you can calculate the total population per region and then use it to rank countries within each region:
```sql
WITH RegionTotals AS (
    SELECT 
        Name, 
        Region, 
        Population,
        SUM(Population) OVER (PARTITION BY Region) AS RegionTotal
    FROM Countries
)
SELECT 
    Name, 
    Region, 
    Population, 
    RegionTotal,
    RANK() OVER (PARTITION BY Region ORDER BY Population DESC) AS RegionRank
FROM RegionTotals;
```
Here, RegionTotals acts as a **temporary table** holding subtotal information, which is then used to assign ranks within each region.

### Using Multiple Window Functions
You can also apply multiple window functions in a single query without intermediate tables:
```sql
SELECT 
    Name, 
    Region, 
    Population,
    SUM(Population) OVER (PARTITION BY Region ORDER BY Population) AS RunningTotal,
    LAG(Population) OVER (PARTITION BY Region ORDER BY Population) AS PrevPop,
    RANK() OVER (PARTITION BY Region ORDER BY Population DESC) AS RegionRank
FROM Countries;
```
This computes 
- A **running total** per region
- The **previous country’s** population for comparisons
- The **rank within the region**
All while keeping every row visible and intact.

Nested analytical queries are highly useful for layered calculations, sequential comparisons, and advanced reporting, making them a core technique in analytical SQL workflows.

### **Exercise**