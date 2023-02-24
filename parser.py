import json
import pathlib
import os

logFolder = pathlib.Path("./reports")


def get_data(log):
    file = pathlib.Path(logFolder / log)
    print(log)

    text = open(file)
    data = json.load(text)

    bossPercent = round(100 - data['targets'][0]['healthPercentBurned'], 2)

    fullFight = data['phases'][0]
    timers = {}
    timers[fullFight['name']] = (fullFight['end'] - fullFight['start']) / 1000
    if 'subPhases' in fullFight:
        for subPhase in fullFight['subPhases']:
            phase = data['phases'][subPhase]
            timers[phase['name']] = (phase['end'] - phase['start']) / 1000

    playerDPS = {}
    playerDPS[fullFight['name']] = {}
    for player in data['players']:
        playerDPS[fullFight['name']][player['account']] = [player['dpsTargets'][i][0]['dps'] for i in range(len(player['dpsTargets']))]
    if 'subPhases' in fullFight:
        for subPhase in fullFight['subPhases']:
            playerDPS[data['phases'][subPhase]['name']] = {}
            for player in data['players']:
                playerDPS[data['phases'][subPhase]['name']][player['account']] = [player['dpsTargets'][i][subPhase]['dps'] for i in range(len(player['dpsTargets']))]

    for phase in playerDPS:
        print(phase)
        for player in playerDPS[phase]:
            print(player, '\t', playerDPS[phase][player])
        print()

    return 0


def main():
    for log in os.listdir(logFolder):
        get_data(log)


main()