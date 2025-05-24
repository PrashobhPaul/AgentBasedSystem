def is_time_free(calendar, day, start, end):
    busy_slots = calendar.get(day, [])
    for slot in busy_slots:
        if not (end <= slot[0] or start >= slot[1]):
            return False
    return True
