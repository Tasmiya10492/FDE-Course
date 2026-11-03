-- Day 7: SQL Exercises
-- Dataset: Variant 8 - HR Leave
-- Database: hr_leave

-- Exercise 1: List first 10 active employees, newest first.
SELECT *
FROM employees
WHERE status = 'active'
ORDER BY created_at DESC
LIMIT 10;


-- Exercise 2: Count employees per status.
SELECT status, COUNT(*) AS employee_count
FROM employees
GROUP BY status
ORDER BY status;

-- Exercise 3: Show each leave request with employee name.
SELECT
    lr.id AS leave_request_id,
    e.name AS employee_name,
    lr.label,
    lr.amount
FROM leave_requests lr
INNER JOIN employees e
    ON lr.parent_id = e.id
ORDER BY lr.id;

-- Exercise 4: Employees with more than 2 leave requests.
SELECT
    e.id,
    e.name,
    COUNT(lr.id) AS leave_request_count
FROM employees e
INNER JOIN leave_requests lr
    ON e.id = lr.parent_id
GROUP BY e.id, e.name
HAVING COUNT(lr.id) > 2
ORDER BY leave_request_count DESC;

-- Exercise 5: Employees with no leave requests.
SELECT
    e.id,
    e.name,
    e.status
FROM employees e
LEFT JOIN leave_requests lr
    ON e.id = lr.parent_id
WHERE lr.id IS NULL
ORDER BY e.id;

-- Exercise 6: Sum leave request amount by label, labels above 1000.
SELECT
    label,
    SUM(amount) AS total_amount
FROM leave_requests
GROUP BY label
HAVING SUM(amount) > 1000
ORDER BY total_amount DESC;

-- Exercise 7: Rank leave requests by amount per employee.
SELECT
    id AS leave_request_id,
    parent_id AS employee_id,
    label,
    amount,
    RANK() OVER (
        PARTITION BY parent_id
        ORDER BY amount DESC
    ) AS amount_rank
FROM leave_requests
ORDER BY parent_id, amount_rank;

-- Exercise 8: Latest approval event for every leave request.
WITH ranked_approvals AS (
    SELECT
        id,
        parent_id,
        event,
        happened_at,
        ROW_NUMBER() OVER (
            PARTITION BY parent_id
            ORDER BY happened_at DESC, id DESC
        ) AS row_num
    FROM approvals
)
SELECT
    parent_id AS leave_request_id,
    event AS latest_event,
    happened_at AS latest_event_date
FROM ranked_approvals
WHERE row_num = 1
ORDER BY parent_id;