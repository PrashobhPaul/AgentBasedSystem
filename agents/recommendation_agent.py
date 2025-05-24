from agents.calendar_agent import is_time_free
from agents.session_manager import get_available_sessions
from utils.helpers import load_user_data

def recommend_sessions(user):
    user_data = load_user_data()
    profile = user_data.get(user)
    if not profile:
        return "User not found."
    
    interests = profile["interests"]
    calendar = profile["calendar"]
    registered = set(profile["registered_sessions"])
    
    sessions = get_available_sessions(interests)
    
    recommended = []
    for s in sessions:
        if s["session_id"] in registered:
            continue
        if is_time_free(calendar, s["day"], s["start_time"], s["end_time"]):
            recommended.append(s)
    
    if not recommended:
        return "No sessions found that match your interests and availability."
    return recommended
