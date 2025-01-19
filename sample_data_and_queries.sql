-- Insert sample books
INSERT INTO books (title, author, isbn, publisher, publication_year, price, quantity, available, location)
VALUES 
('The Great Gatsby', 'F. Scott Fitzgerald', '978-0743273565', 'Scribner', 1925, 9.99, 5, 5, 'A1-23'),
('Python Programming', 'John Smith', '978-1234567890', NULL, NULL, 29.99, 3, 3, 'B2-15'),
('To Kill a Mockingbird', 'Harper Lee', '978-0446310789', 'Grand Central Publishing', 1960, 12.99, 4, 4, 'A2-15'),
('1984', 'George Orwell', '978-0451524935', 'Signet Classic', 1949, 8.99, 6, 6, 'B1-12');

-- Insert sample members
INSERT INTO members (name, email, phone, join_date, membership_type, max_books)
VALUES 
('John Doe', 'john@example.com', '123-456-7890', date('now'), 'Premium', 10),
('Jane Smith', 'jane@example.com', '098-765-4321', date('now'), 'Regular', 5);

-- Insert sample borrowings
INSERT INTO borrowings (book_id, member_id, borrow_date, due_date, status)
VALUES 
(1, 1, date('now', '-7 days'), date('now', '+7 days'), 'Active'),
(2, 2, date('now', '-3 days'), date('now', '+11 days'), 'Active');

-- Update book availability
UPDATE books SET available = available - 1 WHERE book_id IN (1, 2);

-- Sample Queries

-- 1. Get all available books
SELECT title, author, available
FROM books
WHERE available > 0;

-- 2. Get member borrowing history
SELECT m.name, b.title, br.borrow_date, br.due_date, br.status
FROM borrowings br
JOIN members m ON br.member_id = m.member_id
JOIN books b ON br.book_id = b.book_id
WHERE m.member_id = 1
ORDER BY br.borrow_date DESC;

-- 3. Get overdue books
SELECT b.title, m.name, br.borrow_date, br.due_date,
       julianday('now') - julianday(br.due_date) AS days_overdue
FROM borrowings br
JOIN books b ON br.book_id = b.book_id
JOIN members m ON br.member_id = m.member_id
WHERE br.status = 'Active' AND br.due_date < date('now')
ORDER BY days_overdue DESC;

-- 4. Get most borrowed books
SELECT b.title, b.author, COUNT(*) as borrow_count
FROM borrowings br
JOIN books b ON br.book_id = b.book_id
GROUP BY b.book_id
ORDER BY borrow_count DESC
LIMIT 5;

-- 5. Get members with active borrowings
SELECT m.name, m.email, COUNT(*) as active_borrowings
FROM members m
JOIN borrowings br ON m.member_id = br.member_id
WHERE br.status = 'Active'
GROUP BY m.member_id
HAVING active_borrowings > 0
ORDER BY active_borrowings DESC;