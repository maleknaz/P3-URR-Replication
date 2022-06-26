from __future__ import annotations

import io
import json
import os
import zipfile
from pathlib import Path

import pandas
import requests


def all_apps() -> list[str]:
    df = pandas.read_csv('../Data/reviews.csv')
    return list(set(df.app))


def get_f_droid_index() -> dict[str, tuple[str, str]]:
    """
    Get F-Droid Index
    :return: {app name: source code repo}
    """
    buf = requests.get('https://f-droid.org/repo/index-v1.jar').content
    j = zipfile.ZipFile(io.BytesIO(buf)).read('index-v1.json')
    lst = json.loads(j)['apps']
    return {next(iter([lang['name'] for lang in item['localized'].values() if 'name' in lang]),
                 item['packageName']): (item['sourceCode'], item['packageName'])
            for item in lst if 'sourceCode' in item and 'localized' in item}


def find_app_repos() -> dict[str, str]:
    apps = all_apps()
    fdroid = get_f_droid_index()
    return {name: fdroid[name] if name in fdroid else None for name in apps}


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


def clone():
    for app, info in apps.items():
        if info is None:
            continue

        print(f'> Cloning {app}')
        url, pkg = info

        if 'git' not in url:
            print(f'{url} is not a git repository, please download it manually.')
            continue

        path = Path(__file__).parent / 'data' / pkg
        if path.is_dir():
            print(f'{path} exists, skipping.')
            continue

        ret = os.system(f'git clone "{url}" "{path.absolute()}"')
        assert ret == 0, f'Error! Git clone exited with return code {ret}'


if __name__ == '__main__':
    # print(find_app_repos())
    # nones = list(apps.values()).count(None)
    # print(f'{nones} out of {len(apps)} ({nones / len(apps) * 100:.0f}%) apps cannot be found in '
    #       f'f-droid repo with exact name match.')
    # print(list(apps_package_map.keys()))

    print('Cloning apps')
    clone()
