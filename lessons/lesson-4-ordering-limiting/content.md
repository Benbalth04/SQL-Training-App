Sorting your results helps you make sense of data quickly. SQL uses the **ORDER BY** clause to sort rows based on one or more columns. By default, sorting is **ascending** (ASC), which lists values from smallest to largest or alphabetically from A to Z. If you want the largest values first, you can switch to **descending** (DESC).

You can sort by text or numbers, and even by multiple columns. When two rows share the same value in the first column, SQL moves to the next column in your ORDER BY list to break the tie. This makes multi-column sorting especially useful for grouped or similar data.

To control how many rows appear in the output, SQL provides the **LIMIT** clause. LIMIT is handy when you want only a quick preview, the top few results, or a reduced dataset while testing queries.

Below is an example that sorts countries from the smallest to the largest population:

```sql
SELECT Name, Population
FROM Countries
ORDER BY Population ASC;
```

### **Exercise**