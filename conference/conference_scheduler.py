from enum import Enum
import json
import random, math

""" Increment clcock time to identify the remaining time 
"""

def increment_clock_time(base_clock_time, value):
  current = base_clock_time
  mm = (current % 100)
  hh = int(current/100) + math.floor((mm + value)/60)
  mm = (mm + value) % 60
  return hh * 100 + mm
  
""" Intitializing the TalkType Constraints """

class TalkType(Enum):
  KEYNOTE = 30
  REGULAR_TALK = 30
  WORKSHOP = 60
  LIGHTNING = 15
  CLOSING = 30
  LUNCH = 60
  TEA = 15

""" Duration appending to talk type and comparing the time"""

class Talk(object):
  def __init__(self, j):
    self.__dict__ = j
    self.duration = TalkType[self.type].value
  def __lt__(self, other):
    return self.duration < other.duration
  
""" Scheduling talk and adding duration to talk
    Adding start time , end time, talk type and description
"""    
class ScheduledTalk:
  def __init__(self, start_time, talk):
    self.start_time = start_time
    self.end_time = increment_clock_time(start_time, talk.duration)
    self.talk_type = talk.type
    self.description = talk.description
  
  def __lt__(self, other):
    return self.start_time < other.start_time
  
  def __str__(self):
    return "{:04d}".format(self.start_time) + " " + self.talk_type + " " + self.description
  
  def __repr__(self):
    return str(self)
  
""" List of talks in the sorted reverse order
    getting all talks based on duration, start time and end time
    Caling the get talk method and unsheduled talks
"""  
class TalksHelper:
  def __init__(self, list_of_talks):
    self.list_of_talks = sorted(list_of_talks, reverse=True)
    
  def get_talks(self, total_duration, start_time, exclude=[]):
    remaining_talks = []
    selected_talks = []
    duration_left = total_duration
    for talk in self.list_of_talks:
      if talk.type in exclude: 
        remaining_talks.append(talk)    
        continue
      if talk.duration <= duration_left:
        selected_talks.append(talk)
        duration_left -= talk.duration
      else:
        remaining_talks.append(talk)
    
    self.list_of_talks = remaining_talks
    
    random.shuffle(selected_talks)
    
    clock_time = start_time
    scheduled_talks = []
    
    for talk in selected_talks:
      scheduled_talks.append(ScheduledTalk(clock_time, talk))
      clock_time = increment_clock_time(clock_time, talk.duration)

    return scheduled_talks
  
  def get_talk_type(self, talk_type, start_time):
    remaining_talks = []
    selected_talk = None
    for talk in self.list_of_talks:
      if talk.type == talk_type and not selected_talk:
        selected_talk = talk
      else:
        remaining_talks.append(talk)
    
    self.list_of_talks = remaining_talks
    return ScheduledTalk(start_time, selected_talk)
  
  def get_unscheduled_talks(self):
    return self.list_of_talks

""" Merge shedules and remove talks from list """

def merge_schedule(schedule_a, schedule_b):
  a = sorted(schedule_a)
  b = sorted(schedule_b)
  
  merged_schedule = []
  while len(a) + len(b) > 0:
    if len(a) == 0:
      merged_schedule.append(b[0])
      b.pop(0)
    elif len(b) == 0:
      merged_schedule.append(a[0])
      a.pop(0)
    elif b[0].start_time >= a[0].start_time and \
       b[0].start_time < a[0].end_time:
      merged_schedule.append(b[0])
      b.pop(0)
      a.pop(0)
    else:
      merged_schedule.append(a[0])
      a.pop(0)
  return merged_schedule

""" Main method and defining the number of days  """

def __main__():
  DAYS = 2
  
  with open("../data/talks.json") as f:
    data = json.loads(f.read())
  
  talks = []
  for obj in data['talks']:
    talk = Talk(obj)
    talks.append(talk)
  talks_helper = TalksHelper(talks)
   
  lunch_time = Talk({'type': 'LUNCH', 'description': ''})
  tea_time = Talk({'type': 'TEA', 'description': ''})
  
  day_schedule = {}
  for day in range(1, DAYS + 1):
    # definfing the base schedule with the constraints KEYNOTE,CLOSING AND TEA time
    base_schedule = []
    base_schedule += [talks_helper.get_talk_type("KEYNOTE", 900)]
    base_schedule += talks_helper.get_talks(60 * 3, 930, ['KEYNOTE', 'CLOSING'])
    base_schedule += [ScheduledTalk(1230, lunch_time)]
    base_schedule += talks_helper.get_talks(90, 1330, ['KEYNOTE', 'CLOSING'])
    base_schedule += [ScheduledTalk(1500, tea_time)]
    base_schedule += talks_helper.get_talks(105, 1515, ['KEYNOTE', 'CLOSING'])
    base_schedule += [talks_helper.get_talk_type("CLOSING", 1700)]
    day_schedule[(day, 1)] = base_schedule
  # Track Shedule define and display the events    
  while len(talks_helper.get_unscheduled_talks()):
    track_index = int(len(day_schedule.keys()) / DAYS) + 1
    day_index = (len(day_schedule.keys()) % DAYS) + 1
    track_schedule = []
    track_schedule += talks_helper.get_talks(60 * 3, 930, ['KEYNOTE', 'CLOSING'])
    track_schedule += talks_helper.get_talks(90, 1330, ['KEYNOTE', 'CLOSING'])
    track_schedule += talks_helper.get_talks(105, 1515, ['KEYNOTE', 'CLOSING'])
    
    day_schedule[(day_index, track_index)] = \
        merge_schedule(day_schedule[(day_index, 1)], track_schedule)
        
  # Sorting the schedule based the duration
  for key in sorted(day_schedule.keys()):
    schedule = day_schedule[key]
    print ("\n\nDay " + str(key[0]) + " Track " + str(key[1]) + ":")
    for talk in schedule:
      print (talk)
  
__main__()
