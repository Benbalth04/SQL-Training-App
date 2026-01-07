### Pattern Matching
In many situations, you’ll need to filter data based not on exact values, but on **patterns**. The **LIKE** operator allows you to do this by matching text using wildcard symbols. The most common wildcard is %, which represents any number of characters. This lets you search when you only know part of a value — for example, all country names that start with “A”, contain “land”, or end with “ia”.

Examples:
- 'A%' → starts with A
- '%land%' → contains “land” anywhere
- '%ia' → ends with “ia”

### Working with Missing Data
In real databases, not all information is complete. A missing value is stored as **NULL**, and NULL behaves differently from a normal value — it cannot be compared with = or !=.
To check for missing or present values, SQL provides:
- **IS NULL** → find rows missing a value
- **IS NOT NULL** → find rows with a value
Even if the Countries table contains no NULLs, understanding how to handle missing data is essential for real-world analysis.

### Removing Duplicates with DISTINCT
Sometimes you only want to see each unique value once. The **DISTINCT** keyword removes duplicate rows from the output. This is commonly used when exploring a dataset — for example, listing each region once rather than repeating it for every country.

```sql
SELECT DISTINCT Region
FROM Countries;
```
DISTINCT can be applied to one column or multiple columns, depending on how you want to group uniqueness.

### Example: Using LIKE for Pattern Matching
```sql
SELECT Name
FROM Countries
WHERE Name LIKE 'A%';
```

### **Exercise**