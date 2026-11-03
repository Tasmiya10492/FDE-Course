-- Create a sample orders table.
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY,
    customer_name TEXT NOT NULL,
    amount NUMERIC(10, 2) NOT NULL,
    order_date DATE NOT NULL
);

-- Insert sample orders.
-- ON CONFLICT makes repeated execution safe.
INSERT INTO orders (id, customer_name, amount, order_date)
VALUES
    (1, 'Aarav', 1500.00, '2026-10-01'),
    (2, 'Meera', 2500.00, '2026-10-05'),
    (3, 'Kabir', 1800.00, '2026-10-10')
ON CONFLICT (id)
DO UPDATE SET
    customer_name = EXCLUDED.customer_name,
    amount = EXCLUDED.amount,
    order_date = EXCLUDED.order_date;