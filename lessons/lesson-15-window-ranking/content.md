Ranking functions are a subset of window functions that assign positions or ranks to rows within a dataset or a partition. They are particularly useful for top-N analysis, tie handling, and grouping by relative position.

### ROW_NUMBER()
ROW_NUMBER() assigns a **unique sequential number** to each row in a partition or table, regardless of ties. Use it when you need a strict ordering without duplicates.
```sql
SELECT 
    Name, 
    Population,
    ROW_NUMBER() OVER (ORDER BY Population DESC) AS RowNum
FROM Countries;
```
Even if two countries have the same population, each will receive a distinct row number.

### RANK()
RANK() assigns the same rank to rows with identical values, but **leaves gaps** for ties:
```sql
SELECT 
    Name, 
    Population,
    RANK() OVER (ORDER BY Population DESC) AS Rank
FROM Countries;
```
Example: if two countries tie for rank 1, the next rank will be 3, not 2. This preserves the notion of relative position with ties.

### DENSE_RANK()
DENSE_RANK() is similar to RANK(), **but does not leave gaps** for ties:
```sql
SELECT 
    Name, 
    Population,
    DENSE_RANK() OVER (ORDER BY Population DESC) AS DenseRank
FROM Countries;
```
Tied rows share the same rank, and the next rank continues sequentially. This is useful when you want consecutive ranking numbers without gaps.

### NTILE(n)
NTILE(n) divides the result set into n **roughly equal buckets**, assigning a bucket number to each row:
```sql
SELECT 
    Name, 
    Population,
    NTILE(3) OVER (ORDER BY Population DESC) AS PopulationTier
FROM Countries;
```
This allows you to segment data into **tiers**, for example, high, medium, and low populations.

By combining these ranking functions with PARTITION BY and ORDER BY, you can perform sophisticated analyses such as **regional rankings, top performers, and percentile grouping**, all while retaining every row in the result set.

### **Exercise**