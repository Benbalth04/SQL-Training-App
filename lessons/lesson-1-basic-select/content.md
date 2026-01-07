To retrieve data from a SQL database, we need to write **SELECT** statements, which are often colloquially refered to as queries. A query in itself is just a statement which declares what data we are looking for, where to find it in the database, and optionally, how to transform it before it is returned. It has a specific syntax though, which is what we are going to learn in the following exercises.

As we mentioned in the introduction, you can think of a table in SQL as a type of an entity (ie. Dogs), and each row in that table is a specific instance of that type (ie. A pug, a beagle, a different colored pug, etc). This means that the columns would then represent the common properties shared by all instances of that entity (ie. Color of fur, length of tail, etc).

And given a table of data, the most basic query we could write would be one that selects for a couple columns (properties) of the table with all the rows (instances).

```sql
--Select query for a specific columns
SELECT column, another_column, …
FROM mytable;
```

The result of this query will be a two-dimensional set of rows and columns, effectively a copy of the table, but only with the columns that we requested.
If we want to retrieve absolutely all the columns of data from a table, we can then use the asterisk **(*)** shorthand in place of listing all the column names individually.

```sql
--Select query for all columns
SELECT *
FROM mytable;
```

This query, in particular, is really useful because it's a simple way to inspect a table by dumping all the data at once.


### **Exercise**
We will be using a database with data about Countries, Cities and People for most of our exercises. The first exercise will involve the **Countries** table, and the default query below shows all the properties for each country. To progress through this exercise, complete all the tasks listed below. Ensure your press submit (or **Control + Enter as a shortcut**) to check your answer for each task. Once each task is completed, you will be able to move onto the next lesson.

