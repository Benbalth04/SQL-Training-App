Aggregations allow you to **summarise** data, giving you high-level insights without needing to inspect every row. The most common aggregation functions are **COUNT, SUM, AVG, MIN,** and **MAX**. These can help you answer questions like how many countries exist, the total population of a region, or the smallest and largest values in a dataset. Here are some examples of how you can use aggregation functions:

| Function | Description | Example |
|----------|-------------|---------|
| COUNT(column) | Counts the number of non-NULL values in a column | SELECT COUNT(CountryID) FROM Countries; |
| SUM(column)   | Returns the total sum of a numeric column | SELECT SUM(Population) FROM Countries; |
| AVG(column)   | Returns the average value of a numeric column | SELECT AVG(Population) FROM Countries; |
| MIN(column)   | Returns the smallest value in a column | SELECT MIN(Population) FROM Countries; |
| MAX(column)   | Returns the largest value in a column | SELECT MAX(Population) FROM Countries; |


Unlike standard SELECT queries, aggregation functions usually return a single value, unless you combine them with grouping (which you will explore in later lessons). Aggregations work on numeric columns, but COUNT is more flexible — it can be applied to any column, as it simply counts non-NULL values.

Aggregations are especially useful in early exploration, letting you understand broad patterns before diving into more complex analysis.

Here is an example showing the average population across all countries:

```sql
SELECT AVG(Population) AS AveragePopulation
FROM Countries;
```

These functions form the foundation of data summarisation in SQL and prepare you for more advanced techniques such as GROUP BY.
### **Exercise**