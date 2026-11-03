CREATE TABLE employees (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    status TEXT NOT NULL,
    category TEXT NOT NULL,
    created_at DATE NOT NULL
);

CREATE TABLE leave_requests (
    id INTEGER PRIMARY KEY,
    parent_id INTEGER NOT NULL,
    label TEXT NOT NULL,
    amount NUMERIC(10, 2) NOT NULL,
    CONSTRAINT fk_leave_employee
        FOREIGN KEY (parent_id)
        REFERENCES employees(id)
);

CREATE TABLE approvals (
    id INTEGER PRIMARY KEY,
    parent_id INTEGER NOT NULL,
    event TEXT NOT NULL,
    happened_at DATE NOT NULL,
    CONSTRAINT fk_approval_leave
        FOREIGN KEY (parent_id)
        REFERENCES leave_requests(id)
);
