Now we know how to select for specific columns of data from a table, but if you had a table with a hundred million rows of data, reading through all the rows would be inefficient and perhaps even impossible.

In order to filter certain results from being returned, we need to use a **WHERE** clause in the query. The clause is applied to each row of data by checking specific column values to determine whether it should be included in the results or not.

```sql
--Select query with constraints
SELECT column, another_column, …
FROM mytable
WHERE condition
    AND/OR another_condition
    AND/OR …;
```

More complex clauses can be constructed by joining numerous **AND** or **OR** logical keywords (ie. num_wheels >= 4 AND doors <= 2). And below are some useful operators that you can use for numerical data (ie. integer or floating point):


| Operator | Condition | SQL Example |
|---|---|---|
| =, !=, <, <=, >, >= | Standard numerical operators | col_name **!=** 4 |
| BETWEEN … AND … | Number is within range of two values (inclusive) | col_name **BETWEEN** 1.5 **AND** 10.5 |
| NOT BETWEEN … AND … | Number is not within range of two values (inclusive) | col_name **NOT BETWEEN** 1.5 **AND** 10.5 |
| IN (…) | 	Number exists in a list | col_name **IN** (2, 4, 6) |
| NOT IN (…) | 	Number does not exist in a list | col_name **NOT IN** (1, 3, 5) |

In addition to making the results more manageable to understand, writing clauses to constrain the set of rows returned also allows the query to run faster due to the reduction in unnecessary data being returned.

As you might have noticed by now, **SQL doesn't require you to write the keywords all capitalised**, but as a convention, it helps people distinguish SQL keywords from column and tables names, and makes the query easier to read.

### **Exercise**
Using the right constraints, find the information we need from the **Countries** table for each task below.
