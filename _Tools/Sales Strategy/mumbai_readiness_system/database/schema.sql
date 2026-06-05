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

CREATE TABLE IF NOT EXISTS ingestion_runs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  started_at TEXT NOT NULL,
  finished_at TEXT,
  collection_mode TEXT,
  source_name TEXT,
  status TEXT NOT NULL DEFAULT 'running',
  total_collected INTEGER DEFAULT 0,
  total_processed INTEGER DEFAULT 0,
  error_message TEXT,
  config_json TEXT
);

CREATE TABLE IF NOT EXISTS processed_snapshots (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  run_id INTEGER NOT NULL,
  business_id INTEGER NOT NULL,
  snapshot_at TEXT NOT NULL,
  dmi_score REAL,
  dmi_category TEXT,
  review_count INTEGER,
  rating REAL,
  digital_silence_index REAL,
  smartos_readiness_score REAL,
  inquiry_leakage_probability REAL,
  payload_json TEXT NOT NULL,
  FOREIGN KEY (run_id) REFERENCES ingestion_runs(id),
  FOREIGN KEY (business_id) REFERENCES businesses(id)
);

CREATE TABLE IF NOT EXISTS vir_snapshots (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  run_id INTEGER NOT NULL,
  business_id INTEGER NOT NULL,
  vir_id TEXT NOT NULL,
  schema_version TEXT,
  generated_at TEXT NOT NULL,
  collection_mode TEXT,
  data_source TEXT,
  payload_json TEXT NOT NULL,
  FOREIGN KEY (run_id) REFERENCES ingestion_runs(id),
  FOREIGN KEY (business_id) REFERENCES businesses(id)
);

CREATE TABLE IF NOT EXISTS dmi_history (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  run_id INTEGER NOT NULL,
  business_id INTEGER NOT NULL,
  score_at TEXT NOT NULL,
  dmi_score REAL NOT NULL,
  dmi_band TEXT,
  confidence REAL,
  discoverability_score REAL,
  trust_score REAL,
  conversion_score REAL,
  operations_score REAL,
  intelligence_score REAL,
  payload_json TEXT,
  FOREIGN KEY (run_id) REFERENCES ingestion_runs(id),
  FOREIGN KEY (business_id) REFERENCES businesses(id)
);

CREATE TABLE IF NOT EXISTS competitor_benchmarks (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  run_id INTEGER NOT NULL,
  business_id INTEGER NOT NULL,
  benchmark_type TEXT NOT NULL,
  cohort_key TEXT,
  cohort_size INTEGER,
  competitive_index REAL,
  position TEXT,
  biggest_gap TEXT,
  competitor_count INTEGER,
  radius_km REAL,
  payload_json TEXT NOT NULL,
  created_at TEXT NOT NULL,
  FOREIGN KEY (run_id) REFERENCES ingestion_runs(id),
  FOREIGN KEY (business_id) REFERENCES businesses(id)
);

CREATE TABLE IF NOT EXISTS recommendations (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  run_id INTEGER NOT NULL,
  business_id INTEGER NOT NULL,
  recommendation_type TEXT NOT NULL,
  priority_score REAL,
  product TEXT,
  action TEXT,
  reason TEXT,
  script TEXT,
  payload_json TEXT NOT NULL,
  created_at TEXT NOT NULL,
  FOREIGN KEY (run_id) REFERENCES ingestion_runs(id),
  FOREIGN KEY (business_id) REFERENCES businesses(id)
);

CREATE TABLE IF NOT EXISTS outcome_summaries (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  run_id INTEGER NOT NULL,
  business_id INTEGER NOT NULL,
  past_contact_count INTEGER DEFAULT 0,
  past_reply_count INTEGER DEFAULT 0,
  past_meeting_count INTEGER DEFAULT 0,
  past_win_count INTEGER DEFAULT 0,
  reply_rate REAL DEFAULT 0,
  meeting_rate REAL DEFAULT 0,
  win_rate REAL DEFAULT 0,
  payload_json TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  FOREIGN KEY (run_id) REFERENCES ingestion_runs(id),
  FOREIGN KEY (business_id) REFERENCES businesses(id)
);

CREATE TABLE IF NOT EXISTS outcome_events (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  run_id INTEGER NOT NULL,
  business_id INTEGER NOT NULL,
  outcome_date TEXT,
  channel TEXT,
  outcome TEXT,
  notes TEXT,
  payload_json TEXT NOT NULL,
  created_at TEXT NOT NULL,
  FOREIGN KEY (run_id) REFERENCES ingestion_runs(id),
  FOREIGN KEY (business_id) REFERENCES businesses(id)
);

CREATE INDEX IF NOT EXISTS idx_processed_snapshots_run ON processed_snapshots(run_id);
CREATE INDEX IF NOT EXISTS idx_processed_snapshots_business ON processed_snapshots(business_id);
CREATE INDEX IF NOT EXISTS idx_vir_snapshots_business ON vir_snapshots(business_id);
CREATE INDEX IF NOT EXISTS idx_dmi_history_business_time ON dmi_history(business_id, score_at);
CREATE INDEX IF NOT EXISTS idx_recommendations_run ON recommendations(run_id);
CREATE INDEX IF NOT EXISTS idx_outcome_events_business ON outcome_events(business_id);
