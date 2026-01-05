import sqlite3
import random

class Database:
    def __init__(self, path="dategram.db"):
        self.path = path
        self.create_tables()

    def create_tables(self):
        with sqlite3.connect(self.path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tg_id INTEGER UNIQUE,
                    username TEXT,
                    name TEXT, age INTEGER, gender TEXT, city TEXT, 
                    bio TEXT, interests TEXT, music_file_id TEXT, 
                    target_gender TEXT, my_type TEXT, target_type TEXT,
                    photo_id TEXT, 
                    is_active BOOLEAN DEFAULT 1, is_banned BOOLEAN DEFAULT 0,
                    referral_id INTEGER, referral_count INTEGER DEFAULT 0
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS reactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    from_id INTEGER, to_id INTEGER, type TEXT, message TEXT,
                    UNIQUE(from_id, to_id)
                )
            """)
            # Таблица жалоб
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    reporter_id INTEGER, 
                    reported_id INTEGER, 
                    reason TEXT, 
                    status TEXT DEFAULT 'pending'
                )
            """)
            # Таблица для динамических текстов (Правила, FAQ, Контакты)
            cursor.execute("CREATE TABLE IF NOT EXISTS texts (key TEXT PRIMARY KEY, content TEXT)")
            conn.commit()

    def add_user(self, data):
        with sqlite3.connect(self.path) as conn:
            old_user = conn.cursor().execute("SELECT referral_id, referral_count FROM users WHERE tg_id = ?", (data['tg_id'],)).fetchone()
            
            current_ref_id = None
            current_ref_count = 0
            
            if old_user:
                current_ref_id = old_user[0]
                current_ref_count = old_user[1]
            elif data.get('referral_id'):
                current_ref_id = data['referral_id']
                conn.cursor().execute("UPDATE users SET referral_count = referral_count + 1 WHERE tg_id = ?", (current_ref_id,))

            insert_data = {
                'tg_id': data['tg_id'],
                'username': data.get('username'),
                'name': data['name'],
                'age': data['age'],
                'gender': data['gender'],
                'city': data['city'],
                'bio': data['bio'],
                'interests': data.get('interests'),
                'music_file_id': data.get('music_file_id'),
                'target_gender': data.get('target_gender'),
                'my_type': data.get('my_type'),
                'target_type': data.get('target_type'),
                'photo': data.get('photo'),
                'referral_id': current_ref_id,
                'referral_count': current_ref_count
            }

            conn.cursor().execute("""
                INSERT OR REPLACE INTO users 
                (tg_id, username, name, age, gender, city, bio, interests, music_file_id, target_gender, my_type, target_type, photo_id, referral_id, referral_count)
                VALUES (:tg_id, :username, :name, :age, :gender, :city, :bio, :interests, :music_file_id, :target_gender, :my_type, :target_type, :photo, :referral_id, :referral_count)
            """, insert_data)

    def get_user(self, tg_id):
        with sqlite3.connect(self.path) as conn:
            conn.row_factory = sqlite3.Row
            return conn.cursor().execute("SELECT * FROM users WHERE tg_id = ?", (tg_id,)).fetchone()

    def update_field(self, tg_id, field, value):
        with sqlite3.connect(self.path) as conn:
            conn.cursor().execute(f"UPDATE users SET {field} = ? WHERE tg_id = ?", (value, tg_id))

    def search_users(self, user_tg_id):
        me = self.get_user(user_tg_id)
        if not me: return None
        
        my_gender = me['gender']
        required_gender = 'female' if my_gender == 'male' else 'male'
        
        query = """
            SELECT * FROM users
            WHERE tg_id != ? 
            AND is_active = 1 
            AND is_banned = 0
            AND gender = ? 
            AND tg_id NOT IN (SELECT to_id FROM reactions WHERE from_id = ?)
        """
        
        with sqlite3.connect(self.path) as conn:
            conn.row_factory = sqlite3.Row
            candidates = conn.cursor().execute(query, (user_tg_id, required_gender, user_tg_id)).fetchall()
            
        if not candidates: return None

        scored_candidates = []
        my_interests = set(x.strip().lower() for x in str(me['interests']).split(',')) if me['interests'] else set()
        
        for c in candidates:
            score = 0
            age_diff = abs(c['age'] - me['age'])
            if age_diff <= 2: score += 500
            elif age_diff <= 5: score += 200
            
            c_interests = set(x.strip().lower() for x in str(c['interests']).split(',')) if c['interests'] else set()
            matches = len(my_interests & c_interests)
            score += (matches * 50)
            
            if str(c['my_type']) == str(me['target_type']): score += 100
            scored_candidates.append((score + random.random(), c))
        
        scored_candidates.sort(key=lambda x: x[0], reverse=True)
        return scored_candidates[0][1]

    def get_incoming_likes(self, user_id):
        with sqlite3.connect(self.path) as conn:
            conn.row_factory = sqlite3.Row
            return conn.cursor().execute("SELECT u.*, r.message as msg_content FROM users u JOIN reactions r ON u.tg_id = r.from_id WHERE r.to_id = ? AND r.type = 'like' AND u.tg_id NOT IN (SELECT to_id FROM reactions WHERE from_id = ?)", (user_id, user_id)).fetchall()

    def get_matches(self, tg_id):
        with sqlite3.connect(self.path) as conn:
            conn.row_factory = sqlite3.Row
            return conn.cursor().execute("SELECT u.* FROM users u JOIN reactions r1 ON u.tg_id = r1.to_id JOIN reactions r2 ON u.tg_id = r2.from_id WHERE r1.from_id = ? AND r1.type = 'like' AND r2.to_id = ? AND r2.type = 'like'", (tg_id, tg_id)).fetchall()

    def add_reaction(self, from_id, to_id, r_type, msg=None):
        try:
            with sqlite3.connect(self.path) as conn:
                conn.cursor().execute("INSERT INTO reactions (from_id, to_id, type, message) VALUES (?, ?, ?, ?)", (from_id, to_id, r_type, msg))
            return True
        except: return False



    def get_all_users(self):
        # Используем для общей рассылки
        with sqlite3.connect(self.path) as conn:
            return [row[0] for row in conn.cursor().execute("SELECT tg_id FROM users WHERE is_active=1 AND is_banned=0").fetchall()]

    def get_users_by_criteria(self, criteria, value):
        # Сегментация
        query = "SELECT tg_id FROM users WHERE is_active = 1 AND is_banned = 0"
        params = []

        if criteria == 'gender':
            query += " AND gender = ?"
            params.append(value)
        elif criteria == 'city':
            query += " AND city LIKE ?"
            params.append(f"%{value}%")
        elif criteria == 'age':
            # value ожидается как tuple (min, max)
            min_age, max_age = value
            query += " AND age BETWEEN ? AND ?"
            params.extend([min_age, max_age])
        
        with sqlite3.connect(self.path) as conn:
            return [row[0] for row in conn.cursor().execute(query, params).fetchall()]

    def ban_user(self, uid): 
        self.update_field(uid, "is_banned", 1)

    # Работа с текстами (Правила, FAQ, Поддержка)
    def get_text(self, key): 
        with sqlite3.connect(self.path) as conn: 
            res = conn.cursor().execute("SELECT content FROM texts WHERE key=?",(key,)).fetchone()
            return res[0] if res else "Текст не задан."

    def set_text(self, key, val):
        with sqlite3.connect(self.path) as conn: 
            conn.cursor().execute("INSERT OR REPLACE INTO texts (key, content) VALUES (?, ?)", (key, val))

    # Работа с жалобами
    def add_report(self, r, t, reason):
        with sqlite3.connect(self.path) as conn: 
            conn.cursor().execute("INSERT INTO reports (reporter_id, reported_id, reason) VALUES (?, ?, ?)", (r, t, reason))
    
    def get_pending_report(self):
        with sqlite3.connect(self.path) as conn:
            conn.row_factory = sqlite3.Row
            return conn.cursor().execute("SELECT * FROM reports WHERE status = 'pending' LIMIT 1").fetchone()

    def resolve_report(self, report_id, status):
        # status: 'approved' (бан) или 'dismissed' (отказ)
        with sqlite3.connect(self.path) as conn:
            conn.cursor().execute("UPDATE reports SET status = ? WHERE id = ?", (status, report_id))