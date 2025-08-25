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

    def clear_table(self, table_name, reset_id=True):
        cursor = self.conn.cursor()
        cursor.execute(f"DELETE FROM {table_name}")
        if reset_id:
            cursor.execute("DELETE FROM sqlite_sequence WHERE name = ?", (table_name,))
        self.conn.commit()

    def remove_tag_by_name(self, tag_name):
        cursor = self.conn.cursor()

        cursor.execute("SELECT id FROM tags WHERE name = ?", (tag_name,))
        tag_row = cursor.fetchone()
        if not tag_row:
            return False
        tag_id = tag_row[0]
        cursor.execute("DELETE FROM media_tags WHERE tag_id = ?", (tag_id,))
        cursor.execute("DELETE FROM tags WHERE id = ?", (tag_id,))

        self.conn.commit()
        return True

    def rename_tag(self, old_name, new_name):
        cursor = self.conn.cursor()

        cursor.execute("SELECT id FROM tags WHERE name = ?", (old_name,))
        tag_row = cursor.fetchone()
        if not tag_row:
            return False

        tag_id = tag_row[0]

        cursor.execute("SELECT id FROM tags WHERE name = ?", (new_name,))
        if cursor.fetchone():
            return False

        cursor.execute("UPDATE tags SET name = ? WHERE id = ?", (new_name, tag_id))

        self.conn.commit()
        return True

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

    def refresh_database(self):
        cursor = self.conn.cursor()

        try:
            cursor.execute("DROP TABLE IF EXISTS media_tags")
            cursor.execute("DROP TABLE IF EXISTS tags")
            cursor.execute("DROP TABLE IF EXISTS media")
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Error dropping tables: {e}")

        self.create_tables()
        self.populate_media()

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

            # Use st_mtime (modification time) instead of st_ctime (platform dependent)
            date_added = datetime.fromtimestamp(file.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")

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
                            # EXIF tag 36867 = DateTimeOriginal
                            raw_date = exif_data.get(36867)
                            if raw_date:
                                try:
                                    date_captured = datetime.strptime(raw_date, "%Y:%m:%d %H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")
                                except Exception:
                                    pass
                            # EXIF tag 272 = Model (camera)
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

    def get_highest_id(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT MAX(id) FROM media")
        result = cursor.fetchone()
        return result[0] if result[0] is not None else -1

    def get_unique_values(self, column_name, table="media"):
        cursor = self.conn.cursor()
        query = f"SELECT DISTINCT {column_name} FROM {table}"
        cursor.execute(query)
        results = cursor.fetchall()
        return [row[0] for row in results]

    def set_image_filename(self, image_id, new_filename):
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE media
            SET filename = ?
            WHERE id = ?
        """, (new_filename, image_id))
        self.conn.commit()

    def add_tag(self, tag_name):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id FROM tags WHERE name = ?", (tag_name,))
        if cursor.fetchone() is None:
            cursor.execute("INSERT INTO tags (name) VALUES (?)", (tag_name,))
            self.conn.commit()
            return True
        return False

    def get_all_tags(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT name FROM tags ORDER BY name ASC")
        return [row[0] for row in cursor.fetchall()]

    def set_image_tags(self, image_id, tag_names):
        cursor = self.conn.cursor()

        # Remove all existing tags
        cursor.execute("DELETE FROM media_tags WHERE media_id = ?", (image_id,))

        # Add the specified tags
        for tag_name in tag_names:
            # Try to find tag id
            cursor.execute("SELECT id FROM tags WHERE name = ?", (tag_name,))
            tag_row = cursor.fetchone()

            if tag_row:
                tag_id = tag_row[0]

            # Specify relation
            cursor.execute("""
                INSERT INTO media_tags (media_id, tag_id)
                VALUES (?, ?)
            """, (image_id, tag_id))

        self.conn.commit()

    def add_tags_to_image(self, image_id, tag_names):
        cursor = self.conn.cursor()

        for tag_name in tag_names:
            cursor.execute("SELECT id FROM tags WHERE name = ?", (tag_name,))
            tag_row = cursor.fetchone()
            
            if tag_row:
                tag_id = tag_row[0]
            else:
                cursor.execute("INSERT INTO tags (name) VALUES (?)", (tag_name,))
                tag_id = cursor.lastrowid

            cursor.execute("""
                INSERT OR IGNORE INTO media_tags (media_id, tag_id)
                VALUES (?, ?)
            """, (image_id, tag_id))

        self.conn.commit()

    def add_tag_to_images(self, tag_name, image_ids):
        cursor = self.conn.cursor()
        
        cursor.execute("SELECT id FROM tags WHERE name = ?", (tag_name,))
        tag_row = cursor.fetchone()
        
        if tag_row:
            tag_id = tag_row[0]
        else:
            cursor.execute("INSERT INTO tags (name) VALUES (?)", (tag_name,))
            tag_id = cursor.lastrowid

        for image_id in image_ids:
            cursor.execute("""
                INSERT OR IGNORE INTO media_tags (media_id, tag_id)
                VALUES (?, ?)
            """, (image_id, tag_id))

        self.conn.commit()

    def apply_filters(self, filters, filters_active):
        cursor = self.conn.cursor()
        where_clauses = []
        params = []

        # favourite
        if filters_active.get("is_favourite") and filters.get("is_favourite") is not None:
            where_clauses.append("m.is_favourite = ?")
            params.append(1 if filters["is_favourite"] else 0)

        # id
        if filters_active.get("id") and filters.get("id") is not None:
            where_clauses.append("m.id = ?")
            params.append(int(filters["id"]))

        # filename
        if filters_active.get("name") and filters.get("name") and filters["name"] != "":
            where_clauses.append("m.filename LIKE ?")
            params.append(f"%{filters['name']}%")

        # dropdowns
        text_fields = ["type", "format", "camera_model"]
        for field in text_fields:
            if filters_active.get(field) and filters.get(field) and filters[field] != "Any":
                where_clauses.append(f"m.{field} = ?")
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
                    if "date" in col:
                        where_clauses.append(f"datetime(m.{col}) >= datetime(?)")
                    else:
                        where_clauses.append(f"m.{col} >= ?")
                    params.append(min_val)

                if max_val is not None:
                    if "date" in col:
                        where_clauses.append(f"datetime(m.{col}) <= datetime(?)")
                    else:
                        where_clauses.append(f"m.{col} <= ?")
                    params.append(max_val)

        # tags
        tag_names = [t for t in (filters.get("tags") or []) if t]
        if tag_names:
            tag_mode = filters.get("tag_mode", "any")
            placeholders = ",".join("?" for _ in tag_names)

            match tag_mode:
                case "any":
                    # images with at least one of the tags
                    where_clauses.append(f"""
                        m.id IN (
                            SELECT media_id
                            FROM media_tags
                            JOIN tags ON media_tags.tag_id = tags.id
                            WHERE tags.name IN ({placeholders})
                        )
                    """)
                    params.extend(tag_names)

                case "all":
                    # images with at least all of the tags
                    where_clauses.append(f"""
                        m.id IN (
                            SELECT media_id
                            FROM media_tags
                            JOIN tags ON media_tags.tag_id = tags.id
                            WHERE tags.name IN ({placeholders})
                            GROUP BY media_id
                            HAVING COUNT(DISTINCT tags.name) = {len(tag_names)}
                        )
                    """)
                    params.extend(tag_names)

                case "exact":
                    # images with only these tags
                    where_clauses.append(f"""
                        m.id IN (
                            SELECT media_id
                            FROM media_tags
                            JOIN tags ON media_tags.tag_id = tags.id
                            GROUP BY media_id
                            HAVING 
                                COUNT(DISTINCT tags.name) = {len(tag_names)}
                                AND SUM(CASE WHEN tags.name IN ({placeholders}) THEN 1 ELSE 0 END) = {len(tag_names)}
                        )
                    """)
                    params.extend(tag_names)

                case "none":
                    # images with none of these tags
                    where_clauses.append(f"""
                        m.id NOT IN (
                            SELECT media_id
                            FROM media_tags
                            JOIN tags ON media_tags.tag_id = tags.id
                            WHERE tags.name IN ({placeholders})
                        )
                    """)
                    params.extend(tag_names)

                case _:
                    print(f"Unknown tag_mode: {tag_mode}")

        # main query
        sql = """
            SELECT m.*, GROUP_CONCAT(t.name, ',') as tags
            FROM media m
            LEFT JOIN media_tags mt ON m.id = mt.media_id
            LEFT JOIN tags t ON mt.tag_id = t.id
        """
        if where_clauses:
            sql += " WHERE " + " AND ".join(where_clauses)
        sql += " GROUP BY m.id"
        sql += f" ORDER BY {filters['sort_value']} "
        sql += "DESC" if filters['sort_dir'] else "ASC"

        cursor.execute(sql, params)
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()

        results = []
        for row in rows:
            row_dict = dict(zip(columns, row))
            row_dict["tags"] = row_dict["tags"].split(",") if row_dict["tags"] else []
            results.append(row_dict)

        return results
