Lots of data problems often require you to **summarise data by groups**, such as getting the total population for each region. The **GROUP BY** clause lets you combine rows that share the same value in one or more columns, and then apply aggregation functions like COUNT, SUM, AVG, MIN, and MAX to **each group**.

For example, if you want to find the total population **per region**, you can group countries by the **Region** column and sum their populations:

```sql 
SELECT Region, SUM(Population) AS TotalPopulation
FROM Countries
GROUP BY Region;
```

Here, SUM(Population) calculates the total population **for each region**, not the entire table. The GROUP BY Region ensures that the aggregation is done per group.

You can also **group by multiple columns**. For instance, if there were sub-regions or categories, you could group by **Region** and another column. Multi-column grouping is useful when analysing detailed patterns across groups.

```sql 
SELECT Region, SUM(Population) AS TotalPopulation
FROM Countries
GROUP BY Region, Sub-region;
```

### HAVING 
Another important concept is **HAVING**, which filters the results **after aggregation**. This is different from **WHERE**, which filters rows **before** grouping. For example, to show only regions with a total population over 100 million:


```sql
SELECT Region, SUM(Population) AS TotalPopulation
FROM Countries
GROUP BY Region
HAVING SUM(Population) > 100000000;
```
Using **GROUP BY** and **HAVING** together lets you create meaningful summaries and focus on the groups that matter most.

### **Exercise**