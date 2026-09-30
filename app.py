"""GitHub Intelligence Dashboard.

A Streamlit application interfacing directly with the GitHub REST API to
extract, aggregate, and visualize developer profiles, repository statistics,
and programming language distributions.
"""

from datetime import datetime
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from src.api import fetch_events, fetch_profile, fetch_repos
from src.utils import calculate_account_age

# ==============================================================================
# Page Configuration & Global Styling
# ==============================================================================

st.set_page_config(
    page_title="GitHub Intelligence",
    page_icon="assets/favicon.svg",
    layout="wide",
)


def load_css(file_path: str = "assets/style.css") -> None:
    """Read and inject an external CSS stylesheet into the Streamlit DOM.

    Args:
        file_path: Relative or absolute file path to the target stylesheet.
    """
    css_file = Path(file_path)
    if css_file.exists():
        with open(css_file, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


load_css()

# ==============================================================================
# Top Navigation & Brand Header
# ==============================================================================

# Interactive brand header: clicking returns to root URL / reloads clean state
st.markdown(
    """
    <a href="/" target="_self" style="text-decoration: none; color: inherit;">
        <h3 style="margin: 0; display: inline-block;">GITHUB INTEL DASHBOARD <span class="terminal-cursor"></span></h3>
    </a>
    """,
    unsafe_allow_html=True,
)
st.markdown("VIEW AND ANALYZE GITHUB PROFILES, REPOSITORIES, AND ACTIVITY IN REAL-TIME")

# ==============================================================================
# Search & Execution Controls
# ==============================================================================

# Inject client-side JavaScript to autofocus search input on programmatic reset
if st.session_state.pop("focus_search", False):
    components.html(
        """
        <script>
            const input = window.parent.document.querySelector('input[data-testid="stTextInputRootElement"] input, input[placeholder*="USERNAME"]');
            if (input) {
                input.focus();
            }
        </script>
        """,
        height=0,
        width=0,
    )

with st.form(key="search_form", border=False):
    col_input, col_btn = st.columns([4, 1], vertical_alignment="bottom")

    with col_input:
        raw_input = st.text_input(
            "Username",
            placeholder="ENTER GITHUB USERNAME",
            label_visibility="collapsed",
            key="target_input",
        ).strip()

    with col_btn:
        scan_clicked = st.form_submit_button(
            "INITIATE SCAN", type="primary", use_container_width=True
        )

# Quick-select sample profiles
p1, p2, p3, _ = st.columns([1, 1, 1, 3])
if p1.button("torvalds", use_container_width=True):
    st.session_state["active_user"] = "torvalds"
if p2.button("tiangolo", use_container_width=True):
    st.session_state["active_user"] = "tiangolo"
if p3.button("gaearon", use_container_width=True):
    st.session_state["active_user"] = "gaearon"

if scan_clicked and raw_input:
    st.session_state["active_user"] = raw_input

target_user = st.session_state.get("active_user", "")
st.divider()

# ==============================================================================
# Main Application View
# ==============================================================================

if not target_user:
    # --------------------------------------------------------------------------
    # Landing State: Overview and Highlights
    # --------------------------------------------------------------------------
    st.markdown(
        """
        <div style="text-align: center; margin-top: 1.5rem; margin-bottom: 2rem;">
            <h1 style="font-size: 2.2rem; letter-spacing: 2px;">
                EXPLORE. ANALYZE. VISUALIZE.
            </h1>
            <p style="color: #888888; font-size: 1rem;">
                Real-time developer profiles and repository analytics.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Feature cards (styled via assets/style.css to enforce uniform height)
    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown(
            """
            <div class="feature-card">
                <h4><span class="material-symbols-rounded" style="color: #00FF41;">visibility</span>PROFILE INSIGHTS</h4>
                <p>Explore follower metrics, public metadata, and developer biographies.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c2:
        st.markdown(
            """
            <div class="feature-card">
                <h4><span class="material-symbols-rounded" style="color: #00FF41;">bar_chart</span>STACK ANALYSIS</h4>
                <p>Parse public repositories to aggregate and visualize language distribution.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c3:
        st.markdown(
            """
            <div class="feature-card">
                <h4><span class="material-symbols-rounded" style="color: #00FF41;">radar</span>ACTIVITY TRACKING</h4>
                <p>Track public push events, account tenure, and recent contributions.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

else:
    # --------------------------------------------------------------------------
    # Loading State: Data Retrieval Progress
    # --------------------------------------------------------------------------
    with st.status(
        f"Fetching data for {target_user}...", expanded=True
    ) as status:
        st.write("> Connecting to GitHub REST API... [OK]")
        p_res = fetch_profile(target_user)

        st.write("> Extracting repository and language stats... [OK]")
        r_res = fetch_repos(target_user)

        st.write("> Inspecting public event stream and recent activity... [OK]")
        events = fetch_events(target_user)

        status.update(
            label=f"Data retrieved for {target_user}",
            state="complete",
            expanded=False,
        )

    # --------------------------------------------------------------------------
    # Error Handling & Diagnostic Routing
    # --------------------------------------------------------------------------
    if p_res.get("status") == "error":
        reason = p_res.get("reason")
        if reason == "not_found":
            st.error(
                f"User '{target_user}' not found on GitHub. Please check the username and try again."
            )
        elif reason == "rate_limit":
            st.error(
                "GitHub API rate limit exceeded (60 req/hr). Please wait a while before retrying."
            )
        elif reason == "network_timeout":
            st.error(
                "Network timeout occurred while fetching data. Please check your connection and try again."
            )
        else:
            st.error(
                f"An unexpected error occurred while fetching data (Code: {p_res.get('code')})."
            )

    else:
        prof = p_res["data"]
        repos = r_res["data"] if r_res.get("status") == "success" else []

        # ----------------------------------------------------------------------
        # Main Layout: Profile and Analytics (Two Columns)
        # ----------------------------------------------------------------------
        left_col, right_col = st.columns([1, 3])

        # Left Column: Profile Summary
        with left_col:
            # Smooth in-app navigation reset with automatic search input autofocus
            if st.button("← NEW SCAN", use_container_width=True):
                st.session_state["active_user"] = ""
                st.session_state["focus_search"] = True
                st.rerun()

            st.write("")

            if prof.get("avatar_url"):
                st.image(prof.get("avatar_url"), use_container_width=True)
            st.subheader(prof.get("name") or prof.get("login"))
            st.caption(f"@{prof.get('login')}")

            if prof.get("bio"):
                st.write(prof.get("bio"))

            st.divider()

            if prof.get("location"):
                st.write(f"**Location:** {prof.get('location')}")
            if prof.get("company"):
                st.write(f"**Company:** {prof.get('company')}")
            if prof.get("blog"):
                st.write(f"**Website:** {prof.get('blog')}")

        # Right Column: Tabbed Analytics
        with right_col:
            tab_overview, tab_codebase = st.tabs(["Overview", "Codebase Analytics"])

            with tab_overview:
                # Primary Metric Cards
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Followers", f"{prof.get('followers', 0):,}")
                m2.metric("Public Repos", prof.get("public_repos", 0))

                stars = sum(r.get("stargazers_count", 0) for r in repos)
                forks = sum(r.get("forks_count", 0) for r in repos)
                m3.metric("Total Stars", f"{stars:,}")
                m4.metric("Total Forks", f"{forks:,}")

                st.divider()

                # Account Activity & Tenure
                st.subheader("Account Details")
                age_str, date_str = calculate_account_age(prof.get("created_at"))

                raw_updated_at = prof.get("updated_at")
                last_updated = (
                    datetime.fromisoformat(
                        raw_updated_at.replace("Z", "+00:00")
                    ).strftime("%b %d, %Y")
                    if raw_updated_at
                    else "Unknown"
                )

                push_events = [e for e in events if e.get("type") == "PushEvent"]
                push_count = len(push_events)

                o1, o2, o3 = st.columns(3)
                o1.metric("Account Age", age_str, f"Created {date_str}")
                o2.metric("Last Active", last_updated)
                o3.metric(
                    "Recent Pushes",
                    f"{push_count} / 30 events",
                    "Public activity sample",
                )

                st.write("")
                d1, d2, d3 = st.columns(3)
                d1.write(f"**Public Gists:** {prof.get('public_gists', 0)}")
                d2.write(f"**Following:** {prof.get('following', 0)}")
                d3.write(f"**Hireable:** {'Yes' if prof.get('hireable') else 'No'}")

            with tab_codebase:
                # Language Distribution Chart
                st.subheader("Language Distribution")
                langs = [r.get("language") for r in repos if r.get("language")]

                if langs:
                    df = pd.DataFrame(langs, columns=["Language"])
                    counts = df["Language"].value_counts().reset_index()
                    counts.columns = ["Language", "Repositories"]

                    chart = (
                        alt.Chart(counts)
                        .mark_bar(color="#00FF41")
                        .encode(
                            x=alt.X(
                                "Repositories:Q",
                                title="Repository Count",
                                axis=alt.Axis(grid=False, tickMinStep=1),
                            ),
                            y=alt.Y(
                                "Language:N",
                                sort="-x",
                                title="",
                                axis=alt.Axis(
                                    grid=False,
                                    ticks=False,
                                    labelLimit=1000,
                                    minExtent=120,
                                ),
                            ),
                            tooltip=["Language", "Repositories"],
                        )
                        .properties(height=280)
                        .configure_view(strokeWidth=0)
                    )

                    st.altair_chart(chart, use_container_width=True)
                else:
                    st.info("No language data found in public repositories.")
