# SQL exercises (day 7)

Find the section for your variant (the number on your Practice data set file). Load the CSV files from the `tables` folder of your data set into your own schema first. Design the schema yourself: types, primary keys, foreign keys and indexes with a reason each.
Try each exercise on your own. Use `EXPLAIN` on exercises 3 and 4 before and after adding an index.

\---

## Variant 1: Library

Tables: `books` (main), `members` (each row points to a main row through `parent\_id`), `loans` (each row points to a row of `members` through `parent\_id`).

### 1\. List the first 10 active rows of the main table, newest first.

### 2\. Count the rows of books per status.

### 3\. Show each row of members with the name of its parent in books.

### 4\. Find the parents in books that have more than 2 rows in members.

### 5\. Find the rows of books that have NO row in members (a LEFT JOIN with a NULL check).

### 6\. Total the amount in members per label and show only labels above 1000.

### 7\. For each parent in books, rank its members rows by amount (a window function).

### 8\. Show the latest loans event for every row of members (a common table expression).

\---

## Variant 2: Clinic (synthetic data)

Tables: `patients` (main), `appointments` (each row points to a main row through `parent\_id`), `clinicians` (each row points to a row of `appointments` through `parent\_id`).

### 1\. List the first 10 active rows of the main table, newest first.

### 2\. Count the rows of patients per status.

### 3\. Show each row of appointments with the name of its parent in patients.

### 4\. Find the parents in patients that have more than 2 rows in appointments.

### 5\. Find the rows of patients that have NO row in appointments (a LEFT JOIN with a NULL check).

### 6\. Total the amount in appointments per label and show only labels above 1000.

### 7\. For each parent in patients, rank its appointments rows by amount (a window function).

### 8\. Show the latest clinicians event for every row of appointments (a common table expression).

\---

## Variant 3: Parcel logistics

Tables: `parcels` (main), `hubs` (each row points to a main row through `parent\_id`), `scan\_events` (each row points to a row of `hubs` through `parent\_id`).

### 1\. List the first 10 active rows of the main table, newest first.

### 2\. Count the rows of parcels per status.

### 3\. Show each row of hubs with the name of its parent in parcels.

### 4\. Find the parents in parcels that have more than 2 rows in hubs.

### 5\. Find the rows of parcels that have NO row in hubs (a LEFT JOIN with a NULL check).

### 6\. Total the amount in hubs per label and show only labels above 1000.

### 7\. For each parent in parcels, rank its hubs rows by amount (a window function).

### 8\. Show the latest scan\_events event for every row of hubs (a common table expression).

\---

## Variant 4: IT helpdesk

Tables: `tickets` (main), `agents` (each row points to a main row through `parent\_id`), `assets` (each row points to a row of `agents` through `parent\_id`).

### 1\. List the first 10 active rows of the main table, newest first.

### 2\. Count the rows of tickets per status.

### 3\. Show each row of agents with the name of its parent in tickets.

### 4\. Find the parents in tickets that have more than 2 rows in agents.

### 5\. Find the rows of tickets that have NO row in agents (a LEFT JOIN with a NULL check).

### 6\. Total the amount in agents per label and show only labels above 1000.

### 7\. For each parent in tickets, rank its agents rows by amount (a window function).

### 8\. Show the latest assets event for every row of agents (a common table expression).

\---

## Variant 5: Water utility

Tables: `outage\_reports` (main), `areas` (each row points to a main row through `parent\_id`), `crews` (each row points to a row of `areas` through `parent\_id`).

### 1\. List the first 10 active rows of the main table, newest first.

### 2\. Count the rows of outage\_reports per status.

### 3\. Show each row of areas with the name of its parent in outage\_reports.

### 4\. Find the parents in outage\_reports that have more than 2 rows in areas.

### 5\. Find the rows of outage\_reports that have NO row in areas (a LEFT JOIN with a NULL check).

### 6\. Total the amount in areas per label and show only labels above 1000.

### 7\. For each parent in outage\_reports, rank its areas rows by amount (a window function).

### 8\. Show the latest crews event for every row of areas (a common table expression).

\---

## Variant 6: Retail

Tables: `products` (main), `stock\_levels` (each row points to a main row through `parent\_id`), `orders` (each row points to a row of `stock\_levels` through `parent\_id`).

### 1\. List the first 10 active rows of the main table, newest first.

### 2\. Count the rows of products per status.

### 3\. Show each row of stock\_levels with the name of its parent in products.

### 4\. Find the parents in products that have more than 2 rows in stock\_levels.

### 5\. Find the rows of products that have NO row in stock\_levels (a LEFT JOIN with a NULL check).

### 6\. Total the amount in stock\_levels per label and show only labels above 1000.

### 7\. For each parent in products, rank its stock\_levels rows by amount (a window function).

### 8\. Show the latest orders event for every row of stock\_levels (a common table expression).

\---

## Variant 7: Training centre

Tables: `courses` (main), `learners` (each row points to a main row through `parent\_id`), `sessions` (each row points to a row of `learners` through `parent\_id`).

### 1\. List the first 10 active rows of the main table, newest first.

### 2\. Count the rows of courses per status.

### 3\. Show each row of learners with the name of its parent in courses.

### 4\. Find the parents in courses that have more than 2 rows in learners.

### 5\. Find the rows of courses that have NO row in learners (a LEFT JOIN with a NULL check).

### 6\. Total the amount in learners per label and show only labels above 1000.

### 7\. For each parent in courses, rank its learners rows by amount (a window function).

### 8\. Show the latest sessions event for every row of learners (a common table expression).

\---

## Variant 8: HR leave

Tables: `employees` (main), `leave\_requests` (each row points to a main row through `parent\_id`), `approvals` (each row points to a row of `leave\_requests` through `parent\_id`).

### 1\. List the first 10 active rows of the main table, newest first.

### 2\. Count the rows of employees per status.

### 3\. Show each row of leave\_requests with the name of its parent in employees.

### 4\. Find the parents in employees that have more than 2 rows in leave\_requests.

### 5\. Find the rows of employees that have NO row in leave\_requests (a LEFT JOIN with a NULL check).

### 6\. Total the amount in leave\_requests per label and show only labels above 1000.

### 7\. For each parent in employees, rank its leave\_requests rows by amount (a window function).

### 8\. Show the latest approvals event for every row of leave\_requests (a common table expression).
