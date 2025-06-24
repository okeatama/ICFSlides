import json

def roman_to_int(s):
    roman_map = {
        'I': 1, 'V': 5, 'X': 10, 'L': 50,
        'C': 100, 'D': 500, 'M': 1000
    }
    total = 0
    prev_value = 0
    
    for char in reversed(s.upper()):
        value = roman_map[char]
        if value < prev_value:
            total -= value
        else:
            total += value
            prev_value = value
    return total

with open("JSON/calendar.json","r") as file:
    calendar = json.load(file)

for month in calendar:
    for k, v in month.items():
        split_v = v.split()
        if set(split_v[-1]).issubset({"x","v","i"}):
            split_v[-1] = str(roman_to_int(split_v[-1]))
        new_v = "-".join(split_v)

        month[k] = new_v

with open("JSON/calendar.json", "w") as file:
    json.dump(calendar, file, indent=4)