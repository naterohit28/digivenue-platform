from __future__ import annotations

import json
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import requests

SEED_PATH = Path(__file__).resolve().parents[1] / 'raw' / 'real_venues_seed.json'


@dataclass
class CollectorConfig:
    mode: str = 'mock'
    google_api_key: str | None = None
    max_results_per_query: int = 20
    request_timeout_sec: int = 12
    pause_between_calls_sec: float = 0.2


class GoogleMapsCollector:
    TEXT_SEARCH_URL = 'https://maps.googleapis.com/maps/api/place/textsearch/json'
    DETAILS_URL = 'https://maps.googleapis.com/maps/api/place/details/json'
    FIND_PLACE_URL = 'https://maps.googleapis.com/maps/api/place/findplacefromtext/json'

    def __init__(self, suburbs: list[str], queries: list[str], config: CollectorConfig):
        self.suburbs = suburbs
        self.queries = queries
        self.config = config

    def collect(self) -> list[dict[str, Any]]:
        # ── Not live / no key → estimates only ───────────────────
        if self.config.mode != 'live' or not self.config.google_api_key:
            return self._collect_mock()

        # ── Live mode ────────────────────────────────────────────
        # If we have the curated 106-venue list, look each one up by
        # name (targeted) so real data maps onto YOUR known halls.
        # Otherwise fall back to broad category search.
        try:
            if SEED_PATH.exists():
                return self._collect_live_targeted()
            return self._collect_live()
        except Exception:
            return self._collect_mock()

    # ─────────────────────────────────────────────────────────────
    #  TARGETED live lookup — finds each of YOUR 106 halls on Google
    #  Each hall is tagged data_source = google_live OR ai_estimate
    # ─────────────────────────────────────────────────────────────
    def _collect_live_targeted(self) -> list[dict[str, Any]]:
        seed_venues = json.loads(SEED_PATH.read_text(encoding='utf-8'))
        rows: list[dict[str, Any]] = []

        for venue in seed_venues:
            name = venue.get('business_name', '')
            area = venue.get('area', '')
            query = f"{name} {area} Maharashtra"

            place_id = None
            try:
                place_id = self._find_place_id(query)
            except Exception:
                place_id = None

            if place_id:
                try:
                    details = self._details(place_id)
                    real_row = self._format_row({'place_id': place_id}, details, venue.get('suburb', area))
                    # Keep the curated fields Google can't give us
                    real_row['area'] = venue.get('area', real_row.get('area'))
                    real_row['suburb'] = venue.get('suburb', real_row.get('suburb'))
                    real_row['venue_type'] = venue.get('venue_type')
                    real_row['capacity_min'] = venue.get('capacity_min')
                    real_row['capacity_max'] = venue.get('capacity_max')
                    real_row['pitch_strategy'] = venue.get('pitch_strategy', '')
                    real_row['data_source'] = 'google_live'
                    rows.append(real_row)
                    time.sleep(self.config.pause_between_calls_sec)
                    continue
                except Exception:
                    pass

            # Google could not find it → keep the AI estimate, tag it
            fallback = dict(venue)
            fallback['data_source'] = 'ai_estimate'
            rows.append(fallback)
            time.sleep(self.config.pause_between_calls_sec)

        return rows

    def _find_place_id(self, query: str) -> str | None:
        params = {
            'input': query,
            'inputtype': 'textquery',
            'fields': 'place_id',
            'key': self.config.google_api_key,
        }
        resp = requests.get(self.FIND_PLACE_URL, params=params, timeout=self.config.request_timeout_sec)
        resp.raise_for_status()
        candidates = resp.json().get('candidates', [])
        if candidates:
            return candidates[0].get('place_id')
        return None

    def _collect_live(self) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        seen_place_ids: set[str] = set()

        for suburb in self.suburbs:
            for query_template in self.queries:
                query = query_template.format(suburb=suburb)
                fetched = self._text_search(query)
                for place in fetched:
                    place_id = place.get('place_id')
                    if not place_id or place_id in seen_place_ids:
                        continue
                    seen_place_ids.add(place_id)

                    details = self._details(place_id)
                    formatted = self._format_row(place, details, suburb)
                    rows.append(formatted)

                time.sleep(self.config.pause_between_calls_sec)

        return rows

    def _text_search(self, query: str) -> list[dict[str, Any]]:
        params = {'query': query, 'key': self.config.google_api_key}
        resp = requests.get(self.TEXT_SEARCH_URL, params=params, timeout=self.config.request_timeout_sec)
        resp.raise_for_status()
        payload = resp.json()
        first_batch = payload.get('results', [])[: self.config.max_results_per_query]
        return first_batch

    def _details(self, place_id: str) -> dict[str, Any]:
        fields = ','.join(
            [
                'name',
                'formatted_address',
                'formatted_phone_number',
                'international_phone_number',
                'website',
                'url',
                'rating',
                'user_ratings_total',
                'geometry',
                'opening_hours',
                'reviews',
                'types',
            ]
        )
        params = {'place_id': place_id, 'fields': fields, 'key': self.config.google_api_key}
        resp = requests.get(self.DETAILS_URL, params=params, timeout=self.config.request_timeout_sec)
        resp.raise_for_status()
        return resp.json().get('result', {})

    def _format_row(self, place: dict[str, Any], details: dict[str, Any], suburb: str) -> dict[str, Any]:
        review_items = details.get('reviews', []) or []
        latest_review_date = None
        owner_response = 0
        if review_items:
            latest_review_ts = max((r.get('time', 0) for r in review_items), default=0)
            latest_review_date = datetime.utcfromtimestamp(latest_review_ts).date().isoformat() if latest_review_ts else None
            owner_response = 0

        geometry = details.get('geometry', {}).get('location', {})
        lat = geometry.get('lat')
        lng = geometry.get('lng')
        coords = f'{lat},{lng}' if lat is not None and lng is not None else None

        phones = [details.get('international_phone_number'), details.get('formatted_phone_number')]
        phone = next((p for p in phones if p), None)

        return {
            'external_id': details.get('place_id') or place.get('place_id'),
            'business_name': details.get('name') or place.get('name'),
            'category': (details.get('types') or place.get('types') or ['unknown'])[0],
            'area': suburb,
            'suburb': suburb,
            'address': details.get('formatted_address') or place.get('formatted_address'),
            'phone_numbers': phone,
            'website': details.get('website'),
            'google_maps_url': details.get('url') or f"https://maps.google.com/?q=place_id:{place.get('place_id')}",
            'rating': details.get('rating', place.get('rating', 0)),
            'review_count': details.get('user_ratings_total', place.get('user_ratings_total', 0)),
            'latest_review_date': latest_review_date,
            'owner_response_presence': owner_response,
            'photo_count': len(place.get('photos', []) or []),
            'coordinates': coords,
            'operating_hours': ', '.join(details.get('opening_hours', {}).get('weekday_text', []) or []),
            'google_confidence_score': 0.85,
            'data_source': 'google_live',
        }

    def _collect_mock(self) -> list[dict[str, Any]]:
        # ── Load real venue seed if available ────────────────────
        if SEED_PATH.exists():
            venues = json.loads(SEED_PATH.read_text(encoding='utf-8'))
            for v in venues:
                v.setdefault('data_source', 'ai_estimate')
            return venues

        # ── Fallback: generated mock names (original behaviour) ──
        out = []
        idx = 1
        for suburb in self.suburbs:
            for _ in self.queries:
                out.append(
                    {
                        'external_id': f'mock-{suburb}-{idx}',
                        'business_name': f'{suburb} Venue {idx}',
                        'category': 'banquet_hall',
                        'area': suburb,
                        'suburb': suburb,
                        'address': f'{suburb}, Mumbai, Maharashtra',
                        'phone_numbers': f'+91 98{idx:08d}',
                        'website': f'https://{suburb.lower().replace(" ","")}-venue{idx}.com',
                        'google_maps_url': f'https://maps.google.com/?q={suburb}+venue+{idx}',
                        'rating': round(3.6 + (idx % 10) * 0.1, 1),
                        'review_count': 5 + idx * 3,
                        'latest_review_date': datetime.utcnow().date().isoformat(),
                        'owner_response_presence': 1 if idx % 2 == 0 else 0,
                        'photo_count': 20 + idx,
                        'coordinates': '19.0760,72.8777',
                        'operating_hours': '10:00-22:00',
                        'google_confidence_score': 0.45,
                        'data_source': 'ai_estimate',
                    }
                )
                idx += 1
        return out

