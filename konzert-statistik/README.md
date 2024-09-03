# 🎸 Die Ärzte Konzert Statistik

Statistiken zu allen Konzerten, auf denen du warst und Songs, die du live gesehen hast. Inspiriert von Gesprächen mit anderen Fans, welche Songs wir am häufigsten live gesehen haben.

> 🔗 https://die-aerzte.streamlit.app

## Details und Installation

Die App verwendet [Python](https://www.python.org/) 3.9+, die [setlist.fm API](https://api.setlist.fm/docs/1.0/ui/index.html) und [Streamlit](https://streamlit.io/) für Visualisierung und Hosting. Um sie lokal auszuführen, brauchst du einen setlist.fm-Account und einen [API-Key](https://www.setlist.fm/settings/api).

```bash
# Clone repo
git clone https://github.com/ines/die-aerzte
cd die-aerzte/konzert-statistik

# Install dependencies
pip install -r requirements.txt

# Set API key
export API_KEY=XXXXXXXXXX

# Run app
streamlit run app.py
```

Theoretisch ist es auch möglich, die App für andere Bands zu adaptieren, indem man die Environment-Variable `BAND_NAME` ändert. Ist allerdings nicht getestet.
