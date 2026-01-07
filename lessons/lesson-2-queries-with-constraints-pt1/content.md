Filtering data is one of the most important skills in SQL. Most real-world queries don’t just retrieve all rows — they retrieve the right rows. The **WHERE** clause is how you tell SQL exactly which records should be included in the result.

Think of **WHERE** as giving SQL a set of rules. Only the rows that satisfy those rules will appear in the final output.

### Combining and refining conditions
You can combine several rules to narrow down your results:
- **AND** requires all conditions to be true
- **OR** (used later in the course) requires at least one to be true
- **NOT** lets you exclude values or conditions
For example, you might want to find countries in a certain region **and** with a population above a certain amount. Combining conditions makes your queries more precise and reduces the need for manual filtering later.

### Working with lists of values
The **IN** operator is a clean way to check if a value matches any value in a list. Instead of writing multiple comparisons like:

```sql 
WHERE Region = 'Asia' OR Region = 'Europe' OR Region = 'Africa'
```
You can write:
```sql
WHERE Region IN ('Asia', 'Europe', 'Africa')
```
This makes your queries shorter, easier to maintain, and easier to read.


### Filtering by ranges 
When you want values within a minimum and maximum range, the **BETWEEN** operator is a natural fit. It is inclusive, meaning it includes both boundary values:
```sql 
Population BETWEEN 5000000 AND 20000000
```
If you want to filter outside a range, you can use **NOT BETWEEN**.
Together, these operators let you create flexible and expressive filters without making your SQL complicated.

### Common Filtering Operators
| Operator | Condition | SQL Example |
|---|---|---|
| =, !=, <, <=, >, >= | Compare numerical or text values | Population **>** 1000000 |
| BETWEEN … AND … | Number is within range of two values (inclusive) | Population **BETWEEN** 1.5 AND 10.5 |
| NOT BETWEEN … AND … | Number is not within range of two values (inclusive) | Age **NOT BETWEEN** 18 AND 65 |
| IN (…) | 	Number exists in a list | Region **IN** ('Asia', 'Europe') |
| NOT IN (…) | 	Number does not exist in a list | CountryId **NOT IN** (1, 5) |

### Example
Here is a simple example that finds countries in Asia with populations over 100 million:

```sql
--Select query with constraints
SELECT Name, Population
FROM Countries
WHERE Region = 'Asia'
  AND Population > 100000000;
```

### **Exercise**

