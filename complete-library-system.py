import sqlite3
from datetime import datetime, timedelta

class LibraryManagementSystem:
    def __init__(self, db_name="library.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        # Books table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS books (
                book_id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                isbn TEXT UNIQUE NOT NULL,
                publisher TEXT,
                publication_year INTEGER,
                price DECIMAL(10,2),
                quantity INTEGER NOT NULL,
                available INTEGER NOT NULL,
                description TEXT,
                location TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Members table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS members (
                member_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                phone TEXT,
                address TEXT,
                join_date DATE NOT NULL,
                membership_type TEXT DEFAULT 'Regular',
                max_books INTEGER DEFAULT 5,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Borrowings table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS borrowings (
                borrow_id INTEGER PRIMARY KEY AUTOINCREMENT,
                book_id INTEGER NOT NULL,
                member_id INTEGER NOT NULL,
                borrow_date DATE NOT NULL,
                due_date DATE NOT NULL,
                return_date DATE,
                status TEXT DEFAULT 'Active',
                FOREIGN KEY (book_id) REFERENCES books(book_id),
                FOREIGN KEY (member_id) REFERENCES members(member_id)
            )
        ''')

        self.conn.commit()

    def add_book(self, title, author, isbn, quantity, publisher=None, 
                publication_year=None, price=None, description=None, location=None):
        try:
            self.cursor.execute('''
                INSERT INTO books (
                    title, author, isbn, publisher, publication_year,
                    price, quantity, available, description, location
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (title, author, isbn, publisher, publication_year,
                  price, quantity, quantity, description, location))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def add_member(self, name, email, phone=None, address=None, 
                  membership_type='Regular', max_books=5):
        try:
            join_date = datetime.now().date()
            self.cursor.execute('''
                INSERT INTO members (
                    name, email, phone, address, join_date,
                    membership_type, max_books
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (name, email, phone, address, join_date,
                  membership_type, max_books))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def borrow_book(self, book_id, member_id):
        try:
            # Check book availability
            self.cursor.execute('SELECT available FROM books WHERE book_id = ?', (book_id,))
            available = self.cursor.fetchone()

            if not available or available[0] <= 0:
                return False, "Book not available"

            # Create borrowing record
            borrow_date = datetime.now().date()
            due_date = borrow_date + timedelta(days=14)  # 14 days borrowing period

            self.cursor.execute('''
                INSERT INTO borrowings (book_id, member_id, borrow_date, due_date)
                VALUES (?, ?, ?, ?)
            ''', (book_id, member_id, borrow_date, due_date))

            # Update book availability
            self.cursor.execute('''
                UPDATE books 
                SET available = available - 1
                WHERE book_id = ?
            ''', (book_id,))

            self.conn.commit()
            return True, "Book borrowed successfully"
        except Exception as e:
            self.conn.rollback()
            return False, str(e)

    def return_book(self, borrow_id):
        try:
            return_date = datetime.now().date()
            
            self.cursor.execute('''
                UPDATE borrowings 
                SET return_date = ?, status = 'Returned'
                WHERE borrow_id = ? AND return_date IS NULL
            ''', (return_date, borrow_id))

            if self.cursor.rowcount > 0:
                # Get book_id from borrowing record
                self.cursor.execute('SELECT book_id FROM borrowings WHERE borrow_id = ?', (borrow_id,))
                book_id = self.cursor.fetchone()[0]

                # Update book availability
                self.cursor.execute('''
                    UPDATE books 
                    SET available = available + 1
                    WHERE book_id = ?
                ''', (book_id,))

                self.conn.commit()
                return True, "Book returned successfully"
            return False, "No matching borrowing record found"
        except Exception as e:
            self.conn.rollback()
            return False, str(e)

    def get_member_history(self, member_id):
        self.cursor.execute('''
            SELECT 
                books.title,
                b.borrow_date,
                b.due_date,
                b.return_date,
                b.status
            FROM borrowings b
            JOIN books ON b.book_id = books.book_id
            WHERE b.member_id = ?
            ORDER BY b.borrow_date DESC
        ''', (member_id,))
        return self.cursor.fetchall()

    def __del__(self):
        self.conn.close()

def main():
    # Create a new instance of the library system
    print("Initializing Library Management System...")
    library = LibraryManagementSystem("test_library.db")
    
    # Test 1: Add Books
    print("\nAdding sample books...")
    success = library.add_book(
        title="The Great Gatsby",
        author="F. Scott Fitzgerald",
        isbn="978-0743273565",
        quantity=5,
        publisher="Scribner",
        price=9.99,
        location="A1-23"
    )
    print(f"Added first book: {'Success' if success else 'Failed'}")

    success = library.add_book(
        title="Python Programming",
        author="John Smith",
        isbn="978-1234567890",
        quantity=3,
        price=29.99,
        location="B2-15"
    )
    print(f"Added second book: {'Success' if success else 'Failed'}")

    # Test 2: Add Members
    print("\nAdding sample members...")
    success = library.add_member(
        name="John Doe",
        email="john@example.com",
        phone="123-456-7890",
        membership_type="Premium"
    )
    print(f"Added first member: {'Success' if success else 'Failed'}")

    success = library.add_member(
        name="Jane Smith",
        email="jane@example.com",
        phone="098-765-4321"
    )
    print(f"Added second member: {'Success' if success else 'Failed'}")

    # Test 3: Borrow Books
    print("\nTesting book borrowing...")
    success, message = library.borrow_book(book_id=1, member_id=1)
    print(f"First borrowing: {message}")

    # Test 4: Return Books
    print("\nTesting book return...")
    success, message = library.return_book(borrow_id=1)
    print(f"Return book: {message}")

    # Test 5: Check Member History
    print("\nChecking member borrowing history...")
    history = library.get_member_history(member_id=1)
    print(f"Number of borrowing records for member 1: {len(history)}")
    for record in history:
        print(f"Book: {record[0]}, Borrowed: {record[1]}, Due: {record[2]}, Returned: {record[3]}, Status: {record[4]}")

    # Final Summary
    print("\nFinal Database Summary:")
    library.cursor.execute("SELECT COUNT(*) FROM books")
    print(f"Total books: {library.cursor.fetchone()[0]}")
    library.cursor.execute("SELECT COUNT(*) FROM members")
    print(f"Total members: {library.cursor.fetchone()[0]}")
    library.cursor.execute("SELECT COUNT(*) FROM borrowings")
    print(f"Total borrowings: {library.cursor.fetchone()[0]}")

if __name__ == "__main__":
    main()