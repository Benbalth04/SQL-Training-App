Advanced aggregation techniques let you go beyond simple totals and averages. By combining aggregate functions with conditional logic, multi-step summaries, and joins, you can compute highly targeted metrics from your data.

### Conditional Aggregation with CASE
A CASE expression inside an aggregate allows you to count or sum only the rows that meet specific criteria. This is one of the most flexible tools for analytical SQL.

For example, counting how many countries have a population greater than 100 million:
```sql
SELECT 
    COUNT(CASE WHEN Population > 100000000 THEN 1 END) AS LargeCountries
FROM Countries;
```
Here, CASE returns 1 only when the condition is true. All other rows return NULL, and COUNT ignores NULL values—giving you a conditional count.
You can extend this pattern to build category-based summaries:

```sql
SELECT
    COUNT(CASE WHEN Population > 100000000 THEN 1 END) AS Large,
    COUNT(CASE WHEN Population BETWEEN 10000000 AND 100000000 THEN 1 END) AS Medium,
    COUNT(CASE WHEN Population < 10000000 THEN 1 END) AS Small
FROM Countries;
```
This approach produces multiple conditional metrics in a single pass over the table.

### Multi-Level Aggregations
Aggregations often need to be applied at multiple levels of detail—such as per region, per country, or across the entire dataset. GROUP BY enables this.
For example, counting how many cities belong to each country:
```sql
SELECT 
    co.Name AS CountryName,
    COUNT(ci.CityID) AS NumCities
FROM Countries co
LEFT JOIN Cities ci 
    ON co.CountryID = ci.CountryID
GROUP BY co.Name;
```
This produces a summary at the **country** level.
You can push aggregation further by creating region-level metrics, or combining multiple aggregates in the same grouped result:
```sql
SELECT 
    co.Region,
    COUNT(co.CountryID) AS NumCountries,
    SUM(co.Population) AS TotalPopulation,
    AVG(co.Population) AS AvgPopulation
FROM Countries co
GROUP BY co.Region;
```
Here you get three different metrics summarised at the **region** level.

### Combining Conditional Logic + Grouping
Conditional CASE expressions become even more powerful when used inside grouped queries. For example:
```sql
SELECT 
    co.Region,
    COUNT(CASE WHEN ci.Population > 5000000 THEN 1 END) AS CitiesOver5M
FROM Countries co
LEFT JOIN Cities ci 
    ON co.CountryID = ci.CountryID
GROUP BY co.Region;
```
This answers a more complex question:
**How many high-population cities exist in each region?**
By mixing CASE, GROUP BY, and joins, you can build highly customised summary logic that adapts to real-world data structures.

### **Exercise**
