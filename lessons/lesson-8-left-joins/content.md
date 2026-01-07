In this lesson, we will learn about **LEFT JOINs** and handling **missing data** in SQL. A **LEFT JOIN** returns all rows from the **left table** and the matching rows from the **right table**. If there is no match, the left table row still appears, but the right table columns will show **NULL**.

For example, to list all countries and their cities, even if some countries have no cities:

```sql
SELECT Countries.Name AS CountryName, Cities.Name AS CityName
FROM Countries
LEFT JOIN Cities
ON Countries.CountryID = Cities.CountryID;
```

- Countries with matching cities will show the city names.
- Countries without any cities will still appear, but the **CityName** column will be **NULL**. For example, Berlin would not be excluded from the results like it was last lesson when we used an INNER JOIN. 

This is useful when you want to ensure that no rows from the main table are lost due to missing matches.

```sql
SELECT Countries.Name AS CountryName
FROM Countries
LEFT JOIN Cities
ON Countries.CountryID = Cities.CountryID
WHERE Cities.Name IS NULL;
```
Here, **IS NULL** helps identify missing relationships.
Just like with INNER JOINs, **aliasing** works the same way with LEFT JOINs, making queries shorter and easier to read:

```sql
SELECT co.Name AS CountryName, ci.Name AS CityName
FROM Countries co
LEFT JOIN Cities ci
ON co.CountryID = ci.CountryID;
```

Remember, **LEFT JOIN** guarantees that all rows from the left table are included, while unmatched rows from the right table show **NULL**.
### **Exercise**