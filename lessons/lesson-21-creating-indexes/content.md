Indexes are database objects that help SQL **find rows faster**. An index works a bit like a book index, allowing the database engine to locate data without scanning every row. Indexes are especially useful when filtering data using WHERE, ORDER BY, or JOIN conditions.

An index is created on one or more columns in a table. You do not change the data itself, only how quickly it can be accessed. Because indexes improve read performance but add a small cost to data changes, they should be created carefully and only when needed.

To create an index, you use the **CREATE INDEX** statement. You must give the index a name and specify the table and column it applies to. Index names should be descriptive so they are easy to understand later.

```sql
CREATE INDEX idx_countries_region
ON Countries (Region);
```

This index helps queries that filter or sort by the **Region** column run more efficiently. You can also create indexes on numeric columns, such as **Population**, if they are frequently used in filters.

### **Exercise**