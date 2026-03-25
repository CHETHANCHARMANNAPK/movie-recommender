import sqlite3

conn = sqlite3.connect('movies.db')
cursor = conn.cursor()

# List all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
print("Tables:", [t[0] for t in cursor.fetchall()])

# Show all registered users
print("\n--- Registered Users ---")
cursor.execute("SELECT id, username, email, created_at FROM users")
rows = cursor.fetchall()
if rows:
    print(f"{'ID':<5} {'Username':<20} {'Email':<30} {'Created At'}")
    print("-" * 80)
    for row in rows:
        print(f"{row[0]:<5} {row[1]:<20} {row[2]:<30} {row[3]}")
else:
    print("No users registered yet.")

print(f"\nTotal users: {len(rows)}")
conn.close()
