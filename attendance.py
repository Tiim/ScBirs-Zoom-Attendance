import os
import csv
import json
from time import strptime, mktime
from datetime import datetime


DIR = '/mnt/d/Dropbox/SCBirs/zoom-reports'
with open(os.path.join(DIR, "alias.json"), "r") as j:
    data = json.load(j)
    ALIAS = [
        {
          'names': a['names'], 
          'aliases': [x.lower() for x in a['aliases']]
        }
        for a in data['aliases']
    ]
    IGNORED = data['ignored']



def get_files():
    files = os.listdir(DIR)
    files = [os.path.join(DIR, f) for f in files if ".csv" in f and not "anwesenheit" in f]
    return files


def get_students(name, email, date):
    date = date.isoformat()
    
    if date in IGNORED and ( name in IGNORED[date] or email in IGNORED[date]):
      return []

    for a in ALIAS:
        if name.lower() in a['aliases'] or email.lower() in a['aliases']:
            return a['names']

    print(f'Unknown name "{name}", "{email}, "{date}"')
    return [name]

    pass


def handle_entry(meta, attendance, filename):
    try:
      info = next(meta)
      time = strptime(info["Start Time"], "%d.%m.%Y %I:%M:%S %p")
      date = datetime.fromtimestamp(mktime(time))
      athletes = []

      for att in attendance:
          names = get_students(att["Name (Original Name)"], att["User Email"], date)
          athletes.extend(names)

      athletes.sort()

      return {'start': date.isoformat(), 'attendance': athletes}
    except KeyError:
      print("Error in file", filename)
      raise



def save_data(obj):
    with open(os.path.join(DIR, 'data.json'), 'w',  encoding='utf-8-sig') as outfile:
        json.dump(obj, outfile, indent=4)

    with open(os.path.join(DIR, "anwesenheit.csv"), "w", newline='', encoding='utf-8-sig') as outfile:
        csvw = csv.writer(outfile, delimiter=';', quotechar='"')
        for lesson in obj:
          for student in lesson['attendance']:
            csvw.writerow([lesson['start'], student])

def print_stats(obj):
  lessons = len(obj)
  total_students = sum([len(o['attendance']) for o in obj])

  print(f'Total:\n{lessons} Lektionen')
  print(f'{total_students} Teilnemer')
  print(f'{total_students/lessons:0.2f} Teilnemer pro Lektion')

def main():
    files = get_files()

    total_attendance = []
    for file in files:
        with open(file, "r", encoding='utf-8-sig') as f:
            data = f.readlines()
            metadata = csv.DictReader(data[:2])

            attendance = csv.DictReader(data[3:])
            total_attendance.append(handle_entry(metadata, attendance, file))

    total_attendance.sort(key=lambda x: x['start'])
    save_data(total_attendance)
    print_stats(total_attendance)
    pass


if __name__ == '__main__':
    main()
