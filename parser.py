import json
import pathlib
import os
import csv

logFolder = pathlib.Path("./reports")


def get_data(log):
    file = pathlib.Path(logFolder / log)

    text = open(file)
    data = json.load(text)


    phaseNumbers = [0, 1, 5, 6, 10, 11]
    fightPhases = [False]*6
    for target in data['targets']:
        if target['healthPercentBurned'] == 100:
            if target['id'] == 17188:
                fightPhases[0], fightPhases[5] = True, True
            elif target['id'] == 17124:
                if fightPhases[2]:
                    fightPhases[3], fightPhases[4] = True, True
                else:
                    fightPhases[1], fightPhases[2] = True, True

    if len(data['targets'][0]['rotation']) > 6:
        fightPhases[1] = True
        if len(data['targets'][0]['rotation'][6]['skills']) == 2:
            fightPhases[3] = True


    timers = {}
    playerDPS = {}
    for i in range(len(fightPhases)):
        if fightPhases[i]:
            phaseIndex = phaseNumbers[i]
            phaseDict = data['phases'][phaseIndex]
            timers[phaseDict['name']] = (phaseDict['end'] - phaseDict['start'])/1000

            playerDPS[phaseDict['name']] = {}
            for playerDict in data['players']:
                playerDPS[phaseDict['name']][playerDict['account']] = playerDict['dpsTargets'][0][phaseIndex]['dps']
#                    [playerDict['dpsTargets'][j][phaseIndex]['dps'] for j in range(len(playerDict['dpsTargets']))]

    link = data['uploadLinks'][0]

    return link, timers, playerDPS


def main():
    with open('samarog_sheet.csv', 'w', encoding='UTF8') as f:
        header = ['log', 'phase', 'phase duration', 'Balthazar.9024', 'Demolition Dieter.6952', 'edaquila.8014',
                  'EstiaStein.7531', 'KarlFranzOtto.7863', 'Nxxb.6820', 'Rosenrot.1293', 'SyNyxthete.2104',
                  'CineqPl.4126', 'oPeet.1702']

        writer = csv.writer(f)
        writer.writerow(header)

        for log in os.listdir(logFolder):
            link, timers, playerDPS = get_data(log)


            timers2 = {}
            if 'Phase 1' in timers:
                timers2['Phase 1'] = timers['Phase 1']
            for phase in timers2:
                row = [0]*len(header)
                row[0] = link
                row[1] = phase
                row[2] = timers[phase]
                # how do we sort these
                for player in playerDPS[phase]:
                    i = header.index(player)
                    row[i] = playerDPS[phase][player]

                writer.writerow(row)
                print(row)



main()