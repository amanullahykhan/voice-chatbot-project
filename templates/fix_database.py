import sqlite3
import os

def fix_database():
    """Fix database schema issues"""
    db_file = 'chat_history.db'
    
    if not os.path.exists(db_file):
        print("❌ Database file not found. Starting fresh...")
        return
    
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    try:
        print("🔧 Checking database schema...")
        
        # 1. Check user_settings table
        cursor.execute("PRAGMA table_info(user_settings)")
        columns = [column[1] for column in cursor.fetchall()]
        print(f"Current user_settings columns: {columns}")
        
        # Add missing columns
        if 'voice_model' not in columns:
            print("➕ Adding voice_model column to user_settings...")
            cursor.execute("ALTER TABLE user_settings ADD COLUMN voice_model TEXT DEFAULT 'jenny'")
        
        # 2. Check messages table
        cursor.execute("PRAGMA table_info(messages)")
        columns = [column[1] for column in cursor.fetchall()]
        print(f"Current messages columns: {columns}")
        
        # Add missing columns
        missing_columns = []
        if 'voice_style' not in columns:
            missing_columns.append("voice_style")
        if 'audio_file' not in columns:
            missing_columns.append("audio_file")
        
        for col in missing_columns:
            print(f"➕ Adding {col} column to messages...")
            if col == 'audio_file':
                cursor.execute(f"ALTER TABLE messages ADD COLUMN {col} TEXT")
            else:
                cursor.execute(f"ALTER TABLE messages ADD COLUMN {col} TEXT DEFAULT 'genki'")
        
        conn.commit()
        print("✅ Database schema fixed successfully!")
        
    except Exception as e:
        print(f"❌ Error fixing database: {e}")
        conn.rollback()
    finally:
        conn.close()

def recreate_database():
    """Completely recreate database"""
    db_file = 'chat_history.db'
    
    # Backup old database if exists
    if os.path.exists(db_file):
        backup_file = f"{db_file}.backup_{os.path.getmtime(db_file)}"
        import shutil
        shutil.copy2(db_file, backup_file)
        print(f"📦 Backup created: {backup_file}")
    
    # Delete old database
    if os.path.exists(db_file):
        os.remove(db_file)
        print("🗑️ Old database removed")
    
    # Import and run init_db from app.py
    import app
    app.init_db()
    print("✨ New database created with correct schema")

if __name__ == "__main__":
    print("=" * 60)
    print("🔧 Database Fix Tool")
    print("=" * 60)
    
    print("\nChoose an option:")
    print("1. Try to fix existing database")
    print("2. Recreate database (recommended)")
    print("3. Check current schema")
    
    choice = input("\nEnter choice (1/2/3): ").strip()
    
    if choice == '1':
        fix_database()
    elif choice == '2':
        recreate_database()
    elif choice == '3':
        import sqlite3
        conn = sqlite3.connect('chat_history.db')
        cursor = conn.cursor()
        
        print("\n📊 Current Schema:")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        for table in tables:
            print(f"\n📋 Table: {table[0]}")
            cursor.execute(f"PRAGMA table_info({table[0]})")
            columns = cursor.fetchall()
            for col in columns:
                print(f"  - {col[1]} ({col[2]})")
        
        conn.close()
    else:
        print("❌ Invalid choice")