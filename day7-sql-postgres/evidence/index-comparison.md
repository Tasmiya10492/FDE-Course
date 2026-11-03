# Index Performance Comparison

## Index created

CREATE INDEX idx_leave_requests_parent_id
ON leave_requests(parent_id);

Reason:
The parent_id column is used to join leave_requests with employees.
The index can help locate leave requests belonging to an employee.

## Exercise 3: INNER JOIN

Before indexing:
- Hash Join
- Sequential Scan on employees
- Sequential Scan on leave_requests
- Estimated cost: 7.11..7.32

After indexing:
- Hash Join
- Sequential Scan on employees
- Sequential Scan on leave_requests
- Estimated cost: 7.11..7.32

## Exercise 4: GROUP BY and HAVING

Before indexing:
- Hash Join
- HashAggregate
- Sequential Scans on both tables
- Estimated cost: 6.02..6.07

After indexing:
- Hash Join
- HashAggregate
- Sequential Scans on both tables
- Estimated cost: 6.02..6.07

## Conclusion

PostgreSQL did not choose the new index for either query.
The dataset is relatively small (60 employees and 84 leave requests),
so sequential scans and hash joins were estimated to be cheaper.

Creating an index does not guarantee that PostgreSQL will use it.
The query planner chooses the execution strategy based on estimated cost.
