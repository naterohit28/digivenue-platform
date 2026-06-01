import json
import os
import sqlite3
from datetime import datetime
from pathlib import Path




def load_settings(root: Path) -> dict:
    with (root / 'configs' / 'settings.json').open('r', encoding='utf-8') as f:
        return json.load(f)


def load_google_api_key(root: Path, env_var: str = 'GOOGLE_MAPS_API_KEY') -> str | None:
    """
    Finds the Google Maps API key from (in order):
      1. An environment variable (GOOGLE_MAPS_API_KEY)
      2. configs/secrets.local.json  ->  {"GOOGLE_MAPS_API_KEY": "..."}

    Returns None if no usable key is found (placeholder text is ignored).
    """
    # 1. Environment variable wins
    env_key = os.getenv(env_var)
    if env_key and env_key.strip() and 'PASTE' not in env_key:
        return env_key.strip()

    # 2. secrets.local.json
    secrets_path = root / 'configs' / 'secrets.local.json'
    if secrets_path.exists():
        try:
            data = json.loads(secrets_path.read_text(encoding='utf-8'))
            key = data.get(env_var, '')
            if key and key.strip() and 'PASTE' not in key:
                return key.strip()
        except Exception:
            return None

    return None


def utc_now() -> str:
    return datetime.utcnow().isoformat(timespec='seconds')


class DB:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row

    def init_schema(self, schema_file: Path) -> None:
        sql = schema_file.read_text(encoding='utf-8')
        self.conn.executescript(sql)
        self.conn.commit()

    def upsert_business(self, row: dict) -> int:
        now = utc_now()
        ext = row.get('external_id')
        if ext:
            existing = self.conn.execute('SELECT id FROM businesses WHERE external_id=?', (ext,)).fetchone()
        else:
            existing = self.conn.execute(
                'SELECT id FROM businesses WHERE business_name=? AND suburb=?',
                (row['business_name'], row.get('suburb')),
            ).fetchone()
        if existing:
            bid = existing['id']
            self.conn.execute(
                '''UPDATE businesses SET category=?, area=?, suburb=?, address=?, phone_numbers=?, website=?,
                google_maps_url=?, rating=?, review_count=?, latest_review_date=?, owner_response_presence=?,
                photo_count=?, coordinates=?, operating_hours=?, updated_at=? WHERE id=?''',
                (
                    row.get('category'), row.get('area'), row.get('suburb'), row.get('address'),
                    row.get('phone_numbers'), row.get('website'), row.get('google_maps_url'),
                    row.get('rating'), row.get('review_count'), row.get('latest_review_date'),
                    row.get('owner_response_presence'), row.get('photo_count'), row.get('coordinates'),
                    row.get('operating_hours'), now, bid,
                ),
            )
        else:
            cur = self.conn.execute(
                '''INSERT INTO businesses (external_id,business_name,category,area,suburb,address,phone_numbers,
                website,google_maps_url,rating,review_count,latest_review_date,owner_response_presence,photo_count,
                coordinates,operating_hours,created_at,updated_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
                (
                    row.get('external_id'), row['business_name'], row.get('category'), row.get('area'),
                    row.get('suburb'), row.get('address'), row.get('phone_numbers'), row.get('website'),
                    row.get('google_maps_url'), row.get('rating'), row.get('review_count'), row.get('latest_review_date'),
                    row.get('owner_response_presence'), row.get('photo_count'), row.get('coordinates'),
                    row.get('operating_hours'), now, now,
                ),
            )
            bid = cur.lastrowid
        self.conn.commit()
        return bid

    def insert_social(self, business_id: int, profile: dict) -> None:
        self.conn.execute(
            '''INSERT INTO social_profiles (business_id,platform,username,followers,following_count,post_count,reel_count,
            last_post_date,last_reel_date,avg_views,avg_engagement,highlight_count,whatsapp_cta_presence,bio_quality,
            tagged_vendors,captured_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
            (
                business_id, profile.get('platform', 'instagram'), profile.get('username'), profile.get('followers'),
                profile.get('following'), profile.get('post_count'), profile.get('reel_count'), profile.get('last_post_date'),
                profile.get('last_reel_date'), profile.get('avg_views'), profile.get('avg_engagement'),
                profile.get('highlight_count'), profile.get('whatsapp_cta_presence'), profile.get('bio_quality'),
                profile.get('tagged_vendors'), utc_now(),
            ),
        )
        self.conn.commit()

    def insert_website_analysis(self, business_id: int, row: dict) -> None:
        self.conn.execute(
            '''INSERT INTO website_analysis (business_id,mobile_responsive,page_speed_score,whatsapp_cta_presence,
            inquiry_form_presence,gallery_freshness_score,seo_metadata_score,https_usage,social_links_count,
            services_count,website_quality_score,confidence_score,captured_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)''',
            (
                business_id, row.get('mobile_responsive'), row.get('page_speed_score'), row.get('whatsapp_cta_presence'),
                row.get('inquiry_form_presence'), row.get('gallery_freshness_score'), row.get('seo_metadata_score'),
                row.get('https_usage'), row.get('social_links_count'), row.get('services_count'),
                row.get('website_quality_score'), row.get('confidence_score'), utc_now(),
            ),
        )
        self.conn.commit()

    def insert_score(self, business_id: int, score_row: dict) -> None:
        self.conn.execute(
            '''INSERT INTO dmi_scores (business_id,dmi_score,dmi_category,smartos_readiness_score,
            inquiry_leakage_probability,digistories_opportunity_score,score_breakdown,scored_at)
            VALUES (?,?,?,?,?,?,?,?)''',
            (
                business_id, score_row['dmi_score'], score_row['dmi_category'], score_row['smartos_readiness_score'],
                score_row['inquiry_leakage_probability'], score_row['digistories_opportunity_score'],
                json.dumps(score_row['score_breakdown']), utc_now(),
            ),
        )
        self.conn.commit()

    def snapshot(self, business_id: int, payload: dict) -> None:
        self.conn.execute(
            'INSERT INTO historical_snapshots (business_id,snapshot_date,payload_json) VALUES (?,?,?)',
            (utc_now()[:10], utc_now(), json.dumps(payload)),
        )
        self.conn.commit()

    def latest_business_scores(self):
        return self.conn.execute(
            '''SELECT b.id,b.business_name,b.area,b.suburb,b.website,b.rating,b.review_count,
               b.phone_numbers,b.business_status,d.dmi_score,d.dmi_category,d.smartos_readiness_score,
               d.inquiry_leakage_probability,d.digistories_opportunity_score,d.score_breakdown,d.scored_at
               FROM businesses b
               JOIN dmi_scores d ON d.business_id=b.id
               WHERE d.id IN (SELECT MAX(id) FROM dmi_scores GROUP BY business_id)'''
        ).fetchall()

