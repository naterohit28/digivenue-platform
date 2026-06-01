CREATE TABLE IF NOT EXISTS businesses (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  external_id TEXT,
  business_name TEXT NOT NULL,
  category TEXT,
  area TEXT,
  suburb TEXT,
  address TEXT,
  phone_numbers TEXT,
  website TEXT,
  google_maps_url TEXT,
  rating REAL,
  review_count INTEGER,
  latest_review_date TEXT,
  owner_response_presence INTEGER,
  photo_count INTEGER,
  coordinates TEXT,
  operating_hours TEXT,
  business_status TEXT DEFAULT 'active',
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS social_profiles (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  business_id INTEGER NOT NULL,
  platform TEXT NOT NULL,
  username TEXT,
  followers INTEGER,
  following_count INTEGER,
  post_count INTEGER,
  reel_count INTEGER,
  last_post_date TEXT,
  last_reel_date TEXT,
  avg_views REAL,
  avg_engagement REAL,
  highlight_count INTEGER,
  whatsapp_cta_presence INTEGER,
  bio_quality INTEGER,
  tagged_vendors INTEGER,
  captured_at TEXT NOT NULL,
  FOREIGN KEY (business_id) REFERENCES businesses(id)
);
CREATE TABLE IF NOT EXISTS website_analysis (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  business_id INTEGER NOT NULL,
  mobile_responsive INTEGER,
  page_speed_score REAL,
  whatsapp_cta_presence INTEGER,
  inquiry_form_presence INTEGER,
  gallery_freshness_score REAL,
  seo_metadata_score REAL,
  https_usage INTEGER,
  social_links_count INTEGER,
  services_count INTEGER,
  website_quality_score REAL,
  confidence_score REAL,
  captured_at TEXT NOT NULL,
  FOREIGN KEY (business_id) REFERENCES businesses(id)
);
CREATE TABLE IF NOT EXISTS dmi_scores (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  business_id INTEGER NOT NULL,
  dmi_score REAL NOT NULL,
  dmi_category TEXT NOT NULL,
  smartos_readiness_score REAL,
  inquiry_leakage_probability REAL,
  digistories_opportunity_score REAL,
  score_breakdown TEXT,
  scored_at TEXT NOT NULL,
  FOREIGN KEY (business_id) REFERENCES businesses(id)
);
CREATE TABLE IF NOT EXISTS historical_snapshots (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  business_id INTEGER NOT NULL,
  snapshot_date TEXT NOT NULL,
  payload_json TEXT NOT NULL,
  FOREIGN KEY (business_id) REFERENCES businesses(id)
);
CREATE TABLE IF NOT EXISTS outreach_history (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  business_id INTEGER NOT NULL,
  outreach_date TEXT NOT NULL,
  channel TEXT,
  script TEXT,
  status TEXT,
  outcome_notes TEXT,
  FOREIGN KEY (business_id) REFERENCES businesses(id)
);
CREATE TABLE IF NOT EXISTS bca_members (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  business_id INTEGER,
  member_name TEXT,
  member_code TEXT,
  chapter TEXT,
  is_active INTEGER DEFAULT 1,
  FOREIGN KEY (business_id) REFERENCES businesses(id)
);
CREATE TABLE IF NOT EXISTS territory_clusters (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  suburb TEXT,
  area TEXT,
  cluster_tag TEXT,
  total_businesses INTEGER,
  avg_dmi REAL,
  updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS relationship_intelligence (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  business_name TEXT NOT NULL,
  second_generation_involvement INTEGER DEFAULT 0,
  bca_regular_presence INTEGER DEFAULT 0,
  modernization_mindset_score REAL DEFAULT 0,
  recently_renovated INTEGER DEFAULT 0,
  portal_complaint_signal INTEGER DEFAULT 0,
  operational_struggle_signal INTEGER DEFAULT 0,
  branding_spend_signal INTEGER DEFAULT 0,
  growth_hungry_signal INTEGER DEFAULT 0,
  notes TEXT,
  updated_at TEXT NOT NULL
);
