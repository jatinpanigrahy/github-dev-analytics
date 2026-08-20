import streamlit as st
import requests
import pandas as pd
import altair as alt
from datetime import datetime

st.set_page_config(page_title="GitHub Intelligence", layout="wide")

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
* { font-family: 'Inter', sans-serif; }
div[data-testid="metric-container"] {
    background: rgba(128, 128, 128, 0.04);
    border: 1px solid rgba(128, 128, 128, 0.12);
    padding: 16px;
    border-radius: 6px;
}
.empty-card {
    border: 1px solid rgba(128, 128, 128, 0.15);
    border-radius: 6px;
    padding: 20px;
    background: rgba(128, 128, 128, 0.02);
}
</style>
""",
    unsafe_allow_html=True,
)

st.title("GitHub Intelligence")
st.markdown(
    "View developer profiles, repository statistics, and programming languages."
)


@st.cache_data(ttl=3600)
def fetch_profile(username: str) -> dict:
    r = requests.get(f"https://api.github.com/users/{username}")
    return (
        {"status": "success", "data": r.json()}
        if r.status_code == 200
        else {"status": "error", "code": r.status_code}
    )


@st.cache_data(ttl=3600)
def fetch_repos(username: str) -> dict:
    r = requests.get(
        f"https://api.github.com/users/{username}/repos",
        params={"per_page": 100, "sort": "updated"},
    )
    return (
        {"status": "success", "data": r.json()}
        if r.status_code == 200
        else {"status": "error", "code": r.status_code}
    )


@st.cache_data(ttl=3600)
def fetch_events(username: str) -> list:
    r = requests.get(
        f"https://api.github.com/users/{username}/events/public",
        params={"per_page": 30},
    )
    return r.json() if r.status_code == 200 else []


def calculate_account_age(created_at_str: str) -> tuple:
    created_dt = datetime.strptime(created_at_str, "%Y-%m-%dT%H:%M:%SZ")
    delta = datetime.utcnow() - created_dt
    years = delta.days // 365
    months = (delta.days % 365) // 30
    return f"{years}y {months}m", created_dt.strftime("%b %d, %Y")


col_input, col_examples = st.columns([3, 2], vertical_alignment="bottom")

with col_input:
    target_user = st.text_input(
        "Username",
        placeholder="Enter GitHub username (e.g., torvalds)...",
        label_visibility="collapsed",
    ).strip()

with col_examples:
    c1, c2, c3, _ = st.columns([1, 1, 1, 1])
    if c1.button("torvalds", use_container_width=True):
        target_user = "torvalds"
    if c2.button("tiangolo", use_container_width=True):
        target_user = "tiangolo"
    if c3.button("pallets", use_container_width=True):
        target_user = "pallets"

st.divider()

if not target_user:
    st.subheader("How this tool works")

    sc1, sc2, sc3 = st.columns(3)
    with sc1:
        st.markdown(
            """
        <div class="empty-card">
            <h4>Profile Info</h4>
            <p style="font-size: 14px; color: gray;">Extracts basic user details, follower counts, and availability status.</p>
        </div>
        """,
            unsafe_allow_html=True,
        )
    with sc2:
        st.markdown(
            """
        <div class="empty-card">
            <h4>Code Stats</h4>
            <p style="font-size: 14px; color: gray;">Calculates total stars, forks, and the primary programming languages used.</p>
        </div>
        """,
            unsafe_allow_html=True,
        )
    with sc3:
        st.markdown(
            """
        <div class="empty-card">
            <h4>Recent Activity</h4>
            <p style="font-size: 14px; color: gray;">Checks account creation dates and recent public push events.</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

else:
    with st.spinner("Fetching data..."):
        p_res = fetch_profile(target_user)
        r_res = fetch_repos(target_user)
        events = fetch_events(target_user)

        if p_res["status"] == "error":
            st.error("User not found or API limits exceeded.")
        else:
            prof = p_res["data"]
            repos = r_res["data"] if r_res["status"] == "success" else []

            left_col, right_col = st.columns([1, 3])

            with left_col:
                st.image(prof.get("avatar_url"), width=180)
                st.subheader(prof.get("name") or prof.get("login"))
                st.caption(f"@{prof.get('login')}")

                if prof.get("bio"):
                    st.write(prof.get("bio"))
                if prof.get("location"):
                    st.write(f"Location: {prof.get('location')}")
                if prof.get("company"):
                    st.write(f"Company: {prof.get('company')}")
                if prof.get("blog"):
                    st.write(f"Website: {prof.get('blog')}")

            with right_col:
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Followers", f"{prof.get('followers', 0):,}")
                m2.metric("Public Repos", prof.get("public_repos", 0))

                stars = sum(r.get("stargazers_count", 0) for r in repos)
                forks = sum(r.get("forks_count", 0) for r in repos)
                m3.metric("Total Stars", f"{stars:,}")
                m4.metric("Total Forks", f"{forks:,}")

                st.write("")

                st.subheader("Languages")
                langs = [r.get("language") for r in repos if r.get("language")]

                if langs:
                    df = pd.DataFrame(langs, columns=["Language"])
                    counts = df["Language"].value_counts().reset_index()
                    counts.columns = ["Language", "Repositories"]

                    chart = (
                        alt.Chart(counts)
                        .mark_bar()
                        .encode(
                            x=alt.X(
                                "Repositories:Q",
                                title="Repository Count",
                                axis=alt.Axis(tickMinStep=1),
                            ),
                            y=alt.Y(
                                "Language:N",
                                sort="-x",
                                title="",
                                axis=alt.Axis(labelLimit=1000, minExtent=120),
                            ),
                            tooltip=["Language", "Repositories"],
                        )
                        .properties(height=250)
                    )

                    st.altair_chart(chart, use_container_width=True)
                else:
                    st.info("No language data found in public repositories.")

                st.divider()

                st.subheader("Account Details")

                age_str, date_str = calculate_account_age(prof.get("created_at"))
                last_updated = datetime.strptime(
                    prof.get("updated_at"), "%Y-%m-%dT%H:%M:%SZ"
                ).strftime("%b %d, %Y")

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

                d1, d2, d3 = st.columns(3)
                d1.write(f"**Public Gists:** {prof.get('public_gists', 0)}")
                d2.write(f"**Following:** {prof.get('following', 0)}")
                d3.write(f"**Hireable:** {'Yes' if prof.get('hireable') else 'No'}")
