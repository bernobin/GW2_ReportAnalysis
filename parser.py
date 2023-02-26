import json
import pathlib
import os
import csv

# log folder
logFolder = pathlib.Path("./reports")

# skill id's
ccSkillIDs = {
    '14511':    'Backbreaker',
    '14359':    'Staggering Blow',
    '14516':    'Bulls Charge',
    '44937':    'Disrupting Stab'
}
backbreaker = 14511
staggering_blow = 14359
bulls_charge = 14516
disrupting_stab = 44937


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
                playerDPS[phaseDict['name']][playerDict['account']] = [
                    playerDict['dpsTargets'][j][phaseIndex]['dps'] for j in range(len(playerDict['dpsTargets']))
                ]

    link = data['uploadLinks'][0]

    return link, timers, playerDPS


def createDPScsv():
    with open('Samarog P1.csv', 'w') as p1, open('Samarog P2.csv', 'w') as p2, open('Samarog P3.csv', 'w') as p3, open('Samarog S1.csv', 'w') as s1, open('Samarog S2.csv', 'w') as s2:
        header = ['log', 'phase', 'timer', 'Balthazar.9024', 'Demolition Dieter.6952', 'edaquila.8014',
                  'EstiaStein.7531', 'KarlFranzOtto.7863', 'Nxxb.6820', 'Rosenrot.1293', 'SyNyxthete.2104',
                  'CineqPl.4126', 'oPeet.1702']

        writers = {
            'Phase 1':  csv.writer(p1),
            'Split 1':  csv.writer(s1),
            'Phase 2':  csv.writer(p2),
            'Split 2':  csv.writer(s2),
            'Phase 3':  csv.writer(p3)
        }

        for w in writers:
            writers[w].writerow(header)

        for log in os.listdir(logFolder):
            link, timers, playerDPS = get_data(log)

            for phase in timers:
                row = [0]*len(header)
                row[0] = link
                row[1] = phase
                row[2] = timers[phase]

                if phase == 'Split 1':
                    j = 2
                elif phase == 'Split 2':
                    j = 4
                else:
                    j = 0
                for player in playerDPS[phase]:
                    i = header.index(player)
                    row[i] = playerDPS[phase][player][j]

                if phase in writers:
                    writers[phase].writerow(row)

                print(row)
    return 0


def createTimercsv():
    with open('Samarog Timers.csv', 'w') as f:
        writer = csv.writer(f)

        header = ['log', 'p1', 's1', 'p2', 's2', 'p3']

        writer.writerow(header)

        for log in os.listdir(logFolder):
            link, timers, playerDPS = get_data(log)

            timers.pop('Full Fight', 'not found')

            row = [link]
            for phase in timers:
                row.append(timers[phase])

            writer.writerow(row)

    return 0


def getCCtimers(log):
    file = pathlib.Path(logFolder / log)

    text = open(file)
    data = json.load(text)

    ccTimings = {}
    for player in data['players']:
        name = player['account']
        ccTimings[name] = {}

        for skill in player['rotation']:
            id = str(skill['id'])
            if id in ccSkillIDs:
                ccTimings[name][ccSkillIDs[id]] = [
                    skill['skills'][i]['castTime'] for i in range(len(skill['skills']))
                ]

    link = data['uploadLinks'][0]

    ccStart = [
        data['targets'][0]['rotation'][3]['skills'][i]['castTime'] for i in range(len(data['targets'][0]['rotation'][3]['skills']))
    ]

    return link, ccTimings, ccStart

def createCCcsv():
    with open('Samarog CC.csv', 'w') as f:
        header = ['link', 'ccBar', 'Balthazar.9024', 'Demolition Dieter.6952', 'edaquila.8014',
                  'EstiaStein.7531', 'KarlFranzOtto.7863', 'Nxxb.6820', 'Rosenrot.1293', 'SyNyxthete.2104',
                  'CineqPl.4126', 'oPeet.1702']

        writer = csv.writer(f)
        writer.writerow(header)

        for log in os.listdir(logFolder):
            link, ccTimings, ccStart = getCCtimers(log)

            row = [0]*len(header)
            row[0] = link
            for i in range(len(ccStart)):
                row[1] = 'Breakbar ' + str(i+1)

                for player in ccTimings:
                    j = header.index(player)

                    firstHit = 60000
                    for skill in ccTimings[player]:
                        for cast in range(len(ccTimings[player][skill])):
                            castTime = ccTimings[player][skill][cast]
                            if castTime - ccStart[i] > 0 and castTime - ccStart[i] < firstHit:
                                firstHit = castTime - ccStart[i]

                    row[j] = firstHit

                print(row)
                writer.writerow(row)

    return 0





# creates Samarog P1, ..., S2 files
#createDPScsv()

# creates log - phase timers file
#createTimercsv()

# creates cc csv
createCCcsv()