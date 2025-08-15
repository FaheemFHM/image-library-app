from pathlib import Path
import sqlite3
from datetime import datetime
from PIL import Image
import time

DB_PATH = "database.db"
MEDIA_PATH = Path.cwd() / "../media"

class MediaDatabase:
    def __init__(self, db_path=DB_PATH, media_path=MEDIA_PATH):
        self.db_path = db_path
        self.media_path = media_path
        self.conn = self.connect()

    def connect(self):
        return sqlite3.connect(self.db_path)

    def close(self):
        if self.conn:
            self.conn.close()

    def delete_media_table(self):
        cursor = self.conn.cursor()
        try:
            cursor.execute("DROP TABLE IF EXISTS media")
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Error deleting media table: {e}")

    def create_tables(self):
        cursor = self.conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS media (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filepath TEXT NOT NULL UNIQUE,
            filename TEXT,
            type TEXT CHECK(type IN ('image', 'video')) NOT NULL,
            is_favourite INTEGER DEFAULT 0,
            width INTEGER,
            height INTEGER,
            filesize INTEGER,
            format TEXT,
            camera_model TEXT,
            times_viewed INTEGER DEFAULT 0,
            time_viewed INTEGER DEFAULT 0,
            date_captured TEXT,
            date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS tags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS media_tags (
            media_id INTEGER NOT NULL,
            tag_id INTEGER NOT NULL,
            PRIMARY KEY (media_id, tag_id),
            FOREIGN KEY (media_id) REFERENCES media(id) ON DELETE CASCADE,
            FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
        );
        """)

        self.conn.commit()

    def populate_media(self):
        cursor = self.conn.cursor()
        supported_exts = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.mp4', '.avi', '.mov', '.mkv'}

        media_dir = Path(self.media_path)

        for file in media_dir.iterdir():
            if not file.is_file():
                continue
            if file.suffix.lower() not in supported_exts:
                continue

            file_type = "video" if file.suffix.lower() in {'.mp4', '.avi', '.mov', '.mkv'} else "image"
            filesize = file.stat().st_size
            
            date_added = datetime.fromtimestamp(file.stat().st_ctime).strftime("%Y-%m-%d %H:%M:%S")

            width = height = None
            format_ = None
            date_captured = None
            camera_model = None

            if file_type == "image":
                try:
                    with Image.open(file) as img:
                        width, height = img.size
                        format_ = img.format
                        exif_data = img._getexif()
                        if exif_data:
                            date_captured = exif_data.get(36867)
                            camera_model = exif_data.get(272)
                except Exception as e:
                    print(f"Metadata error for {file.name}: {e}")

            try:
                cursor.execute("""
                    INSERT OR IGNORE INTO media (
                        filepath, filename, type, width, height,
                        filesize, format, date_captured, camera_model, date_added
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    str(file), file.name, file_type, width, height,
                    filesize, format_, date_captured, camera_model, date_added
                ))
            except Exception as e:
                print(f"DB insert error for {file.name}: {e}")

        self.conn.commit()

    def get_first_media(self, limit=10, media_type='image', get_head=True):
        cursor = self.conn.cursor()
        cursor.execute(f"""
            SELECT * FROM media
            WHERE type = ?
            ORDER BY id {"ASC" if get_head else "DESC"}
            LIMIT ?
        """, (media_type, limit))
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        return [dict(zip(columns, row)) for row in rows]

    def get_media_count(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM media")
        return cursor.fetchone()[0]

    def get_media_count_by_type(self, media_type="image"):
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM media WHERE type = ?", (media_type,))
        return cursor.fetchone()[0]

    def toggle_favourite(self, image_id, is_favourite):
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE media SET is_favourite = ? WHERE id = ?
        """, (1 if is_favourite else 0, image_id))
        self.conn.commit()

    def apply_filters(self, filters, filters_active):
        cursor = self.conn.cursor()
        where_clauses = []
        params = []

        # favourite
        if filters_active.get("is_favourite") and filters.get("is_favourite") is not None:
            where_clauses.append("is_favourite = ?")
            params.append(1 if filters["is_favourite"] else 0)

        # id
        if filters_active.get("id") and filters.get("id") is not None:
            where_clauses.append("id = ?")
            params.append(int(filters["id"]))

        # filename
        if filters_active.get("name") and filters.get("name") and filters["name"] != "":
            where_clauses.append("filename LIKE ?")
            params.append(f"%{filters['name']}%")

        # dropdowns
        text_fields = ["type", "format", "camera_model"]
        for field in text_fields:
            if filters_active.get(field) and filters.get(field) and filters[field] != "Any":
                where_clauses.append(f"{field} = ?")
                params.append(filters[field])

        # ranges
        range_filters = [
            ("filesize_min", "filesize_max", "filesize"),
            ("height_min", "height_max", "height"),
            ("width_min", "width_max", "width"),
            ("times_viewed_min", "times_viewed_max", "times_viewed"),
            ("time_viewed_min", "time_viewed_max", "time_viewed"),
            ("date_captured_min", "date_captured_max", "date_captured"),
            ("date_added_min", "date_added_max", "date_added"),
        ]

        for min_key, max_key, col in range_filters:
            col_base = col.split("_")[0]
            if filters_active.get(col_base) or filters_active.get(col):
                min_val = filters.get(min_key)
                max_val = filters.get(max_key)

                if min_val is not None:
                    where_clauses.append(f"{col} >= ?")
                    params.append(min_val)
                if max_val is not None:
                    where_clauses.append(f"{col} <= ?")
                    params.append(max_val)

        # main query
        sql = "SELECT * FROM media"
        if where_clauses:
            sql += " WHERE " + " AND ".join(where_clauses)
        sql += " ORDER BY id ASC"

        cursor.execute(sql, params)
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()

        return [dict(zip(columns, row)) for row in rows]
