import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
EXPORTS = ROOT / 'exports'

# ── Page config ──────────────────────────────
st.set_page_config(
    page_title='DigiVenue — Mumbai Intelligence',
    page_icon='🏛️',
    layout='wide',
)

# ── Header ───────────────────────────────────
st.markdown(
    """
    <div style="background:#1F1D1C;padding:24px 32px;border-radius:4px;margin-bottom:24px;">
        <h1 style="color:#FAF7F2;margin:0;font-size:28px;">🏛️ DigiVenue — Mumbai Banquet Intelligence</h1>
        <p style="color:#C5A059;margin:6px 0 0 0;font-size:15px;">
            Digital Maturity · Outreach Queue · Territory Clusters · Competitor Pressure
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Color map for DMI categories ─────────────
CATEGORY_COLORS = {
    'Digitally Invisible':   '#D94822',
    'Operationally Chaotic': '#E07B39',
    'Visibility Weak':       '#E8B84B',
    'Growth Ready':          '#5BAD6F',
    'Elite':                 '#2E7D52',
}

# ─────────────────────────────────────────────
#  SECTION 1 — Top KPI tiles
# ─────────────────────────────────────────────
stats_path = EXPORTS / 'bcda_statistics.json'
if stats_path.exists():
    stats = json.loads(stats_path.read_text(encoding='utf-8'))
    c1, c2, c3, c4 = st.columns(4)
    c1.metric('🏛️ Total Audited', stats.get('total_audited', '—'))
    c2.metric('⚠️ Need Modernization', f"{stats.get('pct_needing_modernization', '—')}%")
    c3.metric('⭐ Avg Google Rating', stats.get('average_rating', '—'))
    c4.metric('💬 Avg Reviews', stats.get('average_reviews', '—'))

# ─────────────────────────────────────────────
#  Data honesty banner — Real vs Estimate
# ─────────────────────────────────────────────
_tracker_path = EXPORTS / 'bcda_maturity_index_tracker.json'
if _tracker_path.exists():
    _t = pd.read_json(_tracker_path)
    if 'data_source' in _t.columns:
        real_n = int((_t['data_source'] == 'google_live').sum())
        est_n = int((_t['data_source'] == 'ai_estimate').sum())
        total_n = real_n + est_n
        if real_n == 0:
            st.warning(
                f"⚠️ **All {total_n} halls are AI ESTIMATES right now** — no real Google data yet. "
                "These numbers are for testing only. Run `check_live_setup.py` after adding your "
                "Google key to switch on real data. **Do not quote these numbers to hall owners yet.**"
            )
        elif est_n == 0:
            st.success(f"✅ **All {total_n} halls use REAL Google data.** Safe to quote in sales conversations.")
        else:
            st.info(
                f"📊 **Data mix:** {real_n} halls have REAL Google data · "
                f"{est_n} are still AI ESTIMATES (Google couldn't find them). "
                "Check the **Source** column before quoting any number."
            )
st.divider()

# ─────────────────────────────────────────────
#  SECTION 2 — DMI Distribution chart
# ─────────────────────────────────────────────
tracker_path = EXPORTS / 'bcda_maturity_index_tracker.json'
if tracker_path.exists():
    tracker = pd.read_json(tracker_path)

    st.subheader('📊 Digital Maturity Distribution')
    col_chart, col_table = st.columns([1, 2])

    with col_chart:
        cat_counts = tracker['dmi_category'].value_counts().reset_index()
        cat_counts.columns = ['Category', 'Count']
        category_order = ['Digitally Invisible', 'Operationally Chaotic', 'Visibility Weak', 'Growth Ready', 'Elite']
        cat_counts['Category'] = pd.Categorical(cat_counts['Category'], categories=category_order, ordered=True)
        cat_counts = cat_counts.sort_values('Category')

        fig = px.bar(
            cat_counts,
            x='Category',
            y='Count',
            color='Category',
            color_discrete_map=CATEGORY_COLORS,
            text='Count',
        )
        fig.update_traces(textposition='outside')
        fig.update_layout(
            showlegend=False,
            plot_bgcolor='white',
            margin=dict(t=20, b=20),
            xaxis_title='',
            yaxis_title='Number of Halls',
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_table:
        st.markdown('**All Venues — DMI Ranking** · Click 🗺 to open Google Maps')

        tracker_view = tracker.copy()
        if 'data_source' in tracker_view.columns:
            tracker_view['source_label'] = tracker_view['data_source'].map(
                {'google_live': '✅ Real', 'ai_estimate': '🤖 Estimate'}
            ).fillna('🤖 Estimate')

        display_cols = ['business_name', 'source_label', 'google_maps_url', 'suburb',
                        'dmi_score', 'dmi_category', 'recommended_product']
        available = [c for c in display_cols if c in tracker_view.columns]
        styled = (
            tracker_view[available]
            .sort_values('dmi_score', ascending=False)
            .rename(columns={
                'business_name': 'Hall Name',
                'source_label': 'Source',
                'google_maps_url': '🗺 Maps',
                'suburb': 'Area',
                'dmi_score': 'DMI Score',
                'dmi_category': 'Category',
                'recommended_product': 'Best Fit',
            })
        )

        col_config = {}
        if '🗺 Maps' in styled.columns:
            col_config['🗺 Maps'] = st.column_config.LinkColumn(
                '🗺 Maps',
                display_text='Open Maps',
                help='Click to open venue in Google Maps',
            )

        st.dataframe(styled, use_container_width=True, height=340, column_config=col_config)

    st.divider()

# ─────────────────────────────────────────────
#  SECTION 3 — Today's Outreach Queue
# ─────────────────────────────────────────────
queue_path = EXPORTS / 'daily_outreach_queue.csv'
if queue_path.exists():
    queue = pd.read_csv(queue_path)

    st.subheader("📞 Today's Outreach Queue")
    st.caption('Sorted by priority. Top halls to call / WhatsApp first.')

    # Top 5 priority cards
    st.markdown('**🔥 Top 5 Priority Calls Right Now**')
    top5 = queue.head(5)
    cols = st.columns(5)
    for i, (_, row) in enumerate(top5.iterrows()):
        cat = row.get('dmi_category', '')
        color = CATEGORY_COLORS.get(cat, '#888')
        with cols[i]:
            st.markdown(
                f"""
                <div style="border:2px solid {color};border-radius:6px;padding:12px;text-align:center;">
                    <div style="font-weight:bold;font-size:13px;color:#1F1D1C;">{row.get('business_name','—')}</div>
                    <div style="font-size:12px;color:#555;">{row.get('suburb','')}</div>
                    <div style="font-size:22px;font-weight:bold;color:{color};margin:6px 0;">{row.get('dmi_score','—')}</div>
                    <div style="font-size:11px;background:{color};color:white;border-radius:3px;padding:2px 4px;">{cat}</div>
                    <div style="font-size:12px;margin-top:6px;color:#D94822;">📱 {row.get('phone','—')}</div>
                    <div style="font-size:11px;color:#555;margin-top:4px;">👉 {row.get('recommended_product','—')}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown('<br>', unsafe_allow_html=True)

    # Full queue table
    st.markdown('**Full Queue (Top 50)** · Click 🗺 to open Google Maps')
    queue_display_cols = ['business_name', 'google_maps_url', 'suburb', 'phone', 'dmi_score', 'dmi_category',
                           'recommended_product', 'conversion_likelihood_score', 'data_quality_grade',
                           'priority_score', 'priority_reason', 'whatsapp_script']
    available_q = [c for c in queue_display_cols if c in queue.columns]
    queue_renamed = queue[available_q].head(50).rename(columns={
        'business_name': 'Hall',
        'google_maps_url': '🗺 Maps',
        'suburb': 'Area',
        'phone': 'Phone',
        'dmi_score': 'DMI',
        'dmi_category': 'Category',
        'recommended_product': 'Product',
        'conversion_likelihood_score': 'Conv. Likelihood',
        'data_quality_grade': 'Data Quality',
        'priority_score': 'Priority',
        'priority_reason': 'Why Priority',
        'whatsapp_script': 'WhatsApp Message',
    })

    st.markdown('**Queue Health Snapshot**')
    q1, q2, q3 = st.columns(3)
    q1.metric('Avg Conversion Likelihood', f"{queue.get('conversion_likelihood_score', pd.Series([0])).mean():.1f}")
    q2.metric('High Conversion Leads', int((queue.get('conversion_likelihood_score', pd.Series([0])) >= 70).sum()))
    q3.metric('Low Data Quality Leads', int((queue.get('data_quality_grade', pd.Series(['C'])) == 'C').sum()))

    queue_col_config = {}
    if '🗺 Maps' in queue_renamed.columns:
        queue_col_config['🗺 Maps'] = st.column_config.LinkColumn(
            '🗺 Maps',
            display_text='Open Maps',
            help='Click to open venue in Google Maps',
        )

    st.dataframe(
        queue_renamed,
        use_container_width=True,
        height=400,
        column_config=queue_col_config,
    )

    st.divider()

# ─────────────────────────────────────────────
#  SECTION 4 — Territory Intelligence
# ─────────────────────────────────────────────
territory_path = EXPORTS / 'territory_clusters.json'
if territory_path.exists():
    territories = pd.read_json(territory_path)

    st.subheader('🗺️ Territory Intelligence — Suburb Comparison')
    col_t1, col_t2 = st.columns([1, 1])

    with col_t1:
        if 'avg_dmi_score' in territories.columns and 'suburb' in territories.columns:
            fig2 = px.bar(
                territories.sort_values('avg_dmi_score'),
                x='avg_dmi_score',
                y='suburb',
                orientation='h',
                color='avg_dmi_score',
                color_continuous_scale=['#D94822', '#E8B84B', '#5BAD6F'],
                text='avg_dmi_score',
                labels={'avg_dmi_score': 'Avg DMI Score', 'suburb': 'Suburb'},
            )
            fig2.update_traces(texttemplate='%{text:.1f}', textposition='outside')
            fig2.update_layout(
                showlegend=False,
                plot_bgcolor='white',
                margin=dict(t=20),
                coloraxis_showscale=False,
            )
            st.plotly_chart(fig2, use_container_width=True)

    with col_t2:
        st.markdown('**Suburb Data**')
        st.dataframe(
            territories.sort_values('avg_dmi_score', ascending=False),
            use_container_width=True,
            height=300,
        )

    st.divider()

# ─────────────────────────────────────────────
#  SECTION 5 — Competitor Pressure Map
# ─────────────────────────────────────────────
competitor_path = EXPORTS / 'competitor_radius_map.json'
if competitor_path.exists():
    comp = pd.read_json(competitor_path)

    st.subheader('📍 Competitor Pressure — 3km Radius')
    st.caption('Use this in your pitch: "You have X competitors within 3km. Here is how you compare."')

    display_comp = ['business_name', 'suburb', 'competitor_count', 'sales_angle']
    available_c = [c for c in display_comp if c in comp.columns]
    st.dataframe(
        comp[available_c].sort_values('competitor_count', ascending=False),
        use_container_width=True,
        height=300,
    )

st.divider()

# ─────────────────────────────────────────────
#  SECTION 6 — Venue Intelligence Card (5 panels)
# ─────────────────────────────────────────────
panels_path = EXPORTS / 'intelligence_panels.json'
if panels_path.exists():
    panels = json.loads(panels_path.read_text(encoding='utf-8'))

    st.subheader('🎯 Venue Intelligence Card')
    st.caption('Pick a venue to see all 5 sales-intelligence panels — the same numbers appear in the Sales Tool.')

    # Sort venue names by DMI (weakest first = best opportunity)
    venue_names = sorted(panels.keys(), key=lambda n: panels[n].get('dmi_score', 0))
    selected = st.selectbox('Choose a venue', venue_names)

    if selected:
        v = panels[selected]
        src_badge = '✅ Real Google data' if v.get('data_source') == 'google_live' else '🤖 AI estimate'
        st.markdown(
            f"### {selected}  \n"
            f"{v.get('suburb','')} · DMI **{v.get('dmi_score','—')}** "
            f"({v.get('dmi_category','—')}) · {src_badge}"
        )

        c1, c2, c3 = st.columns(3)

        # Panel 1 — Territory Rank
        with c1:
            tr = v['territory_rank']
            st.markdown('#### 📍 Territory Rank')
            st.metric(f"In {tr['suburb']}", f"#{tr['suburb_rank']} of {tr['suburb_total']}")
            st.metric('Overall', f"#{tr['global_rank']} of {tr['global_total']}")

        # Panel 2 — Digital Silence
        with c2:
            ds = v['digital_silence']
            st.markdown('#### 🔇 Digital Silence Index')
            st.metric('Silence Score', f"{ds['score']}/100", ds['label'])
            for line in ds['lines']:
                st.write(f"• {line}")
            if ds['is_strong_digistories_signal']:
                st.success('Strong DigiStories signal')

        # Panel 3 — SmartOS Opportunity
        with c3:
            so = v['smartos_opportunity']
            st.markdown('#### ⚙️ SmartOS Opportunity')
            st.metric('Opportunity', f"{so['opportunity_score']}/100")
            for line in so['lines']:
                st.write(f"• {line}")

        c4, c5 = st.columns(2)

        # Panel 4 — Growth Momentum
        with c4:
            gm = v['growth_momentum']
            st.markdown('#### 📈 Growth Momentum')
            st.metric('Momentum', f"{gm['score']}/100", gm['label'])
            for line in gm['lines']:
                st.write(line)
            if gm['is_buying_signal']:
                st.success('🔥 Buying signal — they are actively growing')

        # Panel 5 — Relationship Intelligence
        with c5:
            rel = v['relationship']
            st.markdown('#### 🤝 Relationship Intelligence')
            if rel['tags']:
                st.markdown(' '.join(f"`{t}`" for t in rel['tags']))
            else:
                st.write('• No field intel captured yet')
                st.caption('Add notes in raw/relationship_intelligence.csv to enrich this.')
            if rel.get('notes'):
                st.info(rel['notes'])

    st.divider()

# ─────────────────────────────────────────────
#  Footer
# ─────────────────────────────────────────────
st.markdown(
    """
    <div style="text-align:center;color:#aaa;font-size:12px;margin-top:40px;">
        DigiVenue Intelligence System · Built for Rohit Nate · Data refreshes daily at 8:00 AM IST
    </div>
    """,
    unsafe_allow_html=True,
)
