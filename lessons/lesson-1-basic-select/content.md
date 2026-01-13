To retrieve data from a SQL database, we need to write **SELECT** statements, which are often colloquially referred to as queries. A query is simply a statement that declares what data we are looking for, where to find it in the database, and optionally, how to transform it before it is returned. SQL queries follow a specific syntax, which is what we are going to learn in the following exercises.

You can think of a table in SQL as a type of entity (e.g. Dogs), where each row represents a specific instance of that entity (e.g. a pug, a beagle, a different-coloured pug, etc). The columns then represent the common properties shared by all instances of that entity (e.g. fur colour, tail length, etc).

Given a table of data, the most basic query we can write is one that selects a few columns (properties) from the table while returning all of the rows (instances).

```sql
--Select query for a specific columns
SELECT column, another_column, …
FROM mytable;
```

The result of this query is a two-dimensional set of rows and columns—effectively a copy of the table, but only containing the columns that we requested.
If we want to retrieve **all** columns from a table, we can use the asterisk (*) shorthand instead of listing each column individually.

```sql
--Select query for all columns
SELECT *
FROM mytable;
```

This query, in particular, is really useful because it's a simple way to inspect a table by dumping all the data at once.

### Formatting and Spacing SQL Queries
While SQL does not require specific spacing or line breaks to work correctly, following common formatting conventions makes queries much easier to read, understand, and debug—especially as they become more complex.

#### Keywords on Their Own Lines
A widely accepted convention is to place each major SQL keyword on its own line. This makes the structure of the query visually clear and helps you quickly understand what the query is doing.

```sql
SELECT column, another_column
FROM mytable;
```

As queries grow, this becomes even more important:
```sql
SELECT column, another_column
FROM mytable
WHERE condition;
```

#### When to Press Enter
As a general rule of thumb:
- Press Enter before each major SQL keyword
- Common keywords you will often see on new lines include:
    - SELECT
    - FROM
    - WHERE
    - GROUP BY
    - HAVING
    - ORDER BY

This style helps you visually scan a query and immediately identify each part’s purpose.

#### Capitalisation
SQL keywords are commonly written in **UPPERCASE**, while table and column names are written in lowercase or camelCase:

```sql
SELECT name, population
FROM countries;
```
This is not required by SQL, but it is a strong convention that improves readability and makes keywords stand out from data identifiers.

#### Why Formatting Matters
Good spacing and formatting:
- Makes queries easier to read and reason about
- Reduces mistakes in longer queries
- Helps you (and others) understand queries months later
- Matches the style used in most professional SQL codebases
    
Throughout these lessons, queries will be written using this formatting style, and you are encouraged to follow it in your own solutions.

### **Exercise**
We will be using a database with data about Countries, Cities and People for most of our exercises. The first exercise will involve the **Countries** table, and the default query below shows all the properties for each country. To progress through this exercise, complete all the tasks listed below. Ensure your press submit (or **Control + Enter as a shortcut**) to check your answer for each task. Once each task is completed, you will be able to move onto the next lesson.

