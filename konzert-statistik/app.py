import datetime
import os
from collections import Counter, defaultdict

import httpx
import streamlit as st

# https://api.setlist.fm/docs/1.0/ui/index.html
API = "https://api.setlist.fm/rest/1.0/user/{user_id}/attended?p={page}"
KEY = os.getenv("API_KEY")
BAND_NAME = os.getenv("BAND_NAME", "Die Ärzte")


def _request(user_id: str, page: int) -> dict:
    headers = {"Accept": "application/json", "x-api-key": KEY}
    r = httpx.get(API.format(user_id=user_id, page=page), headers=headers)
    r.raise_for_status()
    return r.json()


def _api_request(user_id: str, artist: str) -> list[dict]:
    page = 1
    res = _request(user_id, page)
    total = res["total"]
    setlists = res["setlist"]
    while len(setlists) < total:
        page += 1
        res = _request(user_id, page)
        setlists.extend(res["setlist"])
    return [setlist for setlist in setlists if setlist["artist"]["name"] == artist]


def get_data(
    user_id: str,
    artist: str,
    with_special: bool = False,
    with_covers: bool = False,
) -> tuple[list[dict], list[dict]]:
    res = _api_request(user_id, artist)
    songs = Counter()
    songs_by_year = defaultdict(Counter)
    years = set()
    all_concerts = []
    for setlist in res:
        date = list(reversed([int(num) for num in setlist["eventDate"].split("-")]))
        year = date[0]
        years.add(year)
        song_count = 0
        for song_list in setlist["sets"]["set"]:
            for song in song_list["song"]:
                name = song["name"]
                if not name:
                    continue
                if song.get("cover"):
                    if not with_covers:
                        continue
                    name = f"{name} ({song['cover']['name']} Cover)"
                if with_special and song.get("info"):
                    name = f"{name} ({song['info']})"
                songs[name] += 1
                song_count += 1
                songs_by_year[name][year] += 1
        concert = {
            "Datum": datetime.date(*date),
            "Stadt": setlist["venue"]["city"]["name"],
            "Location": setlist["venue"]["name"],
            "Tour": setlist.get("tour", {}).get("name"),
            "Songs": song_count,
            "URL": setlist["url"],
        }
        all_concerts.append(concert)
    all_songs_by_year = {
        song: [counts.get(year, 0) for year in sorted(years)]
        for song, counts in songs_by_year.items()
    }
    all_songs = [
        {
            "Song": song,
            "Prozent": round(count / len(all_concerts) * 100),
            "Anzahl": count,
            "Trend": all_songs_by_year[song],
        }
        for song, count in songs.items()
    ]
    all_songs = sorted(all_songs, key=lambda x: -x["Anzahl"])
    return all_songs, all_concerts


# Streamlit app
title = "Die Ärzte Konzert-Statistik"
st.set_page_config(page_title=title, initial_sidebar_state="expanded")
st.title(title)
user_name = st.text_input("Dein setlist.fm Benutzername")
col1, col2, col3 = st.columns(3)
with_covers = col1.checkbox(
    "Mit Cover-Songs",
    value=True,
    help='Zähle Cover-Songs (aber beachte, dass auch einige Klassiker, z.B. "BGS" als Cover gelten)',
)
with_special = col2.checkbox(
    "Mit Variationen",
    help='Zähle Variationen als separate Songs, z.B. "1/2 Lovesong" mit verschiedenen Intros, Live-Premieren etc.',
)
with_trend = col3.checkbox(
    "Experimentell: Trends",
    help="Zeige für jeden Song an, wie oft er über die Jahre der besuchten Konzerte gespielt wurde",
)
with st.sidebar:
    st.markdown("![](https://i.imgur.com/23Uw2Or.png)")
    st.header("Anleitung")
    st.markdown(
        """
    1. [Registriere](https://www.setlist.fm/signup) dich bei setlist.fm.
    2. Finde die Konzerte, auf denen du warst und klicke den "I was there"-Button unter der Setlist.
    3. Gib hier im oberen Feld deinen setlist.fm-Benutzernamen ein und bestätige mit `enter`.
    4. Viel Spaß! 🎸
    """
    )
    st.caption(
        "Konzert oder Setlist nicht dabei? Sorry, musst du leider selbst hinzufügen – aber setlist.fm ist ein Wiki, ist also möglich!"
    )
    st.divider()
    st.caption(
        """
        [Source](https://github.com/ines/die-aerzte/tree/main/konzert-statistik) ·
        Made with ❤️ by [Ines](https://ines.io)
        """
    )
if user_name:
    with st.spinner("Loading..."):
        songs, concerts = get_data(
            user_name, BAND_NAME, with_special=with_special, with_covers=with_covers
        )
    st.subheader(f"Songs ({len(songs)})")
    if not with_trend:
        for song in songs:
            del song["Trend"]
    st.dataframe(
        data=songs,
        use_container_width=True,
        height=600,
        column_config={
            "Prozent": st.column_config.NumberColumn(
                help="Prozent der Konzerte, bei denen Song gespielt wurde",
                min_value=0,
                max_value=100,
                step=1,
                format="%d%%",
            ),
            "Trend": st.column_config.AreaChartColumn(
                "Trend über die Jahre",
                width="small",
                help="Wie oft der Song über die Jahre der besuchten Konzerte gespielt wurde",
            ),
        },
    )
    st.subheader(f"Konzerte ({len(concerts)})")
    st.dataframe(
        data=concerts,
        use_container_width=True,
        height=600,
        column_config={
            "Datum": st.column_config.DateColumn(format="DD.MM.YYYY"),
            "URL": st.column_config.LinkColumn("", display_text="🔗"),
        },
    )
