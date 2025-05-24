from agents.recommender_agent import recommend_sessions
from utils.helpers import load_faqs

def handle_user_query(user, query):
    faqs = load_faqs()
    if query.lower() in faqs:
        return faqs[query.lower()]
    if "recommend" in query.lower():
        return recommend_sessions(user)
    return "I'm still learning. Please ask about the event or request recommendations."

