import json
from pathlib import Path


apps = {
    'AcDisplay': ('https://github.com/AChep/AcDisplay', 'com.achep.acdisplay'),
    'Turbo Editor ( Text Editor )': ('https://github.com/vmihalachi/turbo-editor', 'com.maskyn.fileeditorpro'),
    'Signal Private Messenger': ('https://github.com/signalapp/Signal-Android', 'org.thoughtcrime.securesms'),
    'Financius - Expense Manager': ('https://github.com/mvarnagiris/financius', 'com.code44.finance'),
    'BatteryBot Battery Indicator': ('https://github.com/darshan-/Battery-Indicator-Free', 'com.darshancomputing.BatteryIndicator'),
    'Duck Duck GO': ('https://github.com/duckduckgo/Android', 'com.duckduckgo.di'),
    'Calculator': ('https://github.com/jochem88/clean-calculator', 'home.jmstudios.calc'),
    '2048': ('https://github.com/SecUSo/privacy-friendly-2048', 'org.secuso.privacyfriendly2048'),
    'Autostarts': ('https://github.com/miracle2k/android-autostarts', 'com.elsdoerfer.android.autostarts'),
    'Muzei Live Wallpaper': ('https://github.com/muzei/muzei', 'net.nurik.roman.muzei'),
    'Marine Compass': None,
    'Device Control [root]': None,
    'Twidere for Twitter': ('https://github.com/TwidereProject/Twidere-Android', 'org.mariotaku.twidere.nyan'),
    'Abstract Art': ('https://github.com/gwhiteside/abstract-art', 'net.georgewhiteside.android.abstractart'),
    'Amaze File Manager': ('https://github.com/TeamAmaze/AmazeFileManager', 'com.amaze.filemanager'),
    'Clip Stack ✓ Clipboard Manager': ('https://github.com/heruoxin/Clip-Stack', 'com.catchingnow.tinyclipboardmanager'),
    'Tweet Lanes': ('https://github.com/chrislacy/TweetLanes', 'com.tweetlanes.android'),
    'Xabber': ('https://github.com/redsolution/xabber-android', 'com.xabber.android'),
    'Bankdroid': ('https://github.com/liato/android-bankdroid', 'com.liato.bankdroid'),
    'Last.fm': ('https://github.com/lastfm/lastfm-android', 'fm.last.android'),
    'Network Log': ('https://github.com/pragma-/networklog', 'com.googlecode.networklog'),
    'OctoDroid': ('https://github.com/slapperwan/gh4a', 'com.gh4a'),
    'Wally': None,
    'CatLog': ('https://github.com/nolanlawson/Catlog', 'com.nolanlawson.logcat'),
    'ConnectBot': ('https://github.com/connectbot/connectbot', 'org.connectbot'),
    'AntennaPod': ('https://github.com/AntennaPod/AntennaPod', 'de.danoeh.antennapod'),
    'SeriesGuide': ('https://github.com/UweTrottmann/SeriesGuide/', 'com.battlelancer.seriesguide.x'),
    'OS Monitor': ('https://github.com/eolwral/OSMonitor', 'com.eolwral.osmonitor'),
    'A Comic Viewer': ('https://github.com/robotmedia/droid-comic-viewer', 'net.androidcomics.acv'),
    'AnkiDroid Flashcards': ('https://github.com/ankidroid/Anki-Android', 'com.ichi2.anki.api'),
    'Terminal Emulator for Android': ('https://github.com/jackpal/Android-Terminal-Emulator', 'jackpal.androidterm'),
    'Adblock Plus': ('https://hg.adblockplus.org/adblockplusandroid', 'org.adblockplus.android'),
    'Bubble level': None,
    'DashClock Widget': ('https://github.com/romannurik/dashclock/', 'net.nurik.roman.dashclock'),
    'Pixel Dungeon': ('https://github.com/watabou/pixel-dungeon', 'com.watabou.pixeldungeon'),
    "Simon Tatham's Puzzles": ('https://github.com/chrisboyle/sgtpuzzles', 'name.boyle.chris.sgtpuzzles'),
    'MultiPicture Live Wallpaper': None,
    'c:geo': ('https://github.com/cgeo/cgeo', 'cgeo.geocaching'),
    'QKSMS - Open Source SMS & MMS': ('https://github.com/moezbhatti/qksms', 'com.moez.QKSMS'),
}

apps_package_map = {data[1]: name for name, data in apps.items() if data is not None}


if __name__ == '__main__':
    result = Path('/workspace/P3/UserRequestReferencer/scoring_result.csv')
    txt = result.read_text()

    entries = {}

    for part in txt.split('+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++\n\n'):
        lines = part.split('\n')
        if lines == ['']:
            continue
        review = lines[1].split(';')
        id = review[0]
        app = review[1]
        review_text = review[4]
        source_files = lines[2:]

        if app not in apps or apps[app] is None:
            continue
        pkg = apps[app][1]

        if pkg not in entries:
            entries[pkg] = []

        entries[pkg].append({'_id': id, 'reviewText': review_text, 'source': [{'path': s} for s in source_files if s]})

    Path(f'Data/RQ_2_Original/Lucene/Results').mkdir(parents=True, exist_ok=True)
    for pkg, lst in entries.items():
        Path(f'Data/RQ_2_Original/Lucene/Results/{pkg}.json').write_text(json.dumps(lst, indent=1))
