# database.py

import pymysql
from datetime import datetime
import os


class MySQLTracker:
    def __init__(self):
        self.config = {
            "host": "mysql-3aa52e18-gaamoucimohamed-ce85.d.aivencloud.com",
            "user": "avnadmin",
            "password": "AVNS_EvkT561hhvQyup2qsnX",
            "db": "defaultdb",
            "port": 26870,
            "charset": "utf8mb4",
            "cursorclass": pymysql.cursors.DictCursor,
            "connect_timeout": 10,
            "read_timeout": 10,
            "write_timeout": 10
        }
        self.create_table_if_not_exists()

    def get_connection(self):
        return pymysql.connect(**self.config)

    def create_table_if_not_exists(self):
        connection = self.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS email_events (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        campaign VARCHAR(255),
                        email VARCHAR(255),
                        type VARCHAR(50),
                        timestamp DATETIME,
                        target_url TEXT
                    )
                """)
                connection.commit()
                print("✅ Table 'email_events' ensured.")
        finally:
            connection.close()

    def log_event(self, campaign, email, event_type, target_url=None):
        connection = self.get_connection()
        try:
            with connection.cursor() as cursor:
                if event_type == "open":
                    cursor.execute("""
                        SELECT id FROM email_events
                        WHERE campaign=%s AND email=%s AND type='open'
                    """, (campaign, email))
                    if cursor.fetchone():
                        print(
                            f"⚠️ Duplicate open ignored for {email} - {campaign}")
                        return

                cursor.execute("""
                    INSERT INTO email_events (campaign, email, type, timestamp, target_url)
                    VALUES (%s, %s, %s, %s, %s)
                """, (campaign, email, event_type, datetime.utcnow(), target_url))
                connection.commit()
                print(
                    f"✅ Logged {event_type}: {email} - {campaign} ({target_url})")
        finally:
            connection.close()

    def get_stats(self):
        connection = self.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT DISTINCT campaign FROM email_events")
                campaigns = cursor.fetchall()

                cursor.execute("""
                    SELECT campaign, type, COUNT(*) as count
                    FROM email_events
                    GROUP BY campaign, type
                """)
                rows = cursor.fetchall()

                stats = {}
                for row in rows:
                    c = row["campaign"]
                    if c not in stats:
                        stats[c] = {"sent": 0, "open": 0, "click": 0}
                    stats[c][row["type"]] += row["count"]
                    stats[c]["sent"] += row["count"]

                sorted_campaigns = sorted(
                    stats.items(), key=lambda x: x[1]["sent"], reverse=True)[:5]

                total_open = sum(r["open"] for r in stats.values())
                total_click = sum(r["click"] for r in stats.values())

                return {
                    "emails_opened": total_open,
                    "emails_clicked": total_click,
                    "total_campaigns": len(campaigns),
                    "recent_campaigns": [
                        {
                            "subject": c,
                            "sent": data["sent"],
                            "opened": data["open"],
                            "clicked": data["click"]
                        }
                        for c, data in sorted_campaigns
                    ]
                }
        finally:
            connection.close()

