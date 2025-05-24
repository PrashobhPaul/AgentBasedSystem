import pandas as pd

def get_available_sessions(interests):
    df = pd.read_csv("data/sessions.csv")
    return df[df["topic"].isin(interests) & (df["max_seats"] > 0)].to_dict(orient="records")

def get_faq_response(query):
    faq = {
        "when is the event": "The event is on 25-27 May 2025.",
        "where is the event": "International Convention Center.",
        "what are the guidelines": "Carry your badge and follow COVID rules.",
        "who are the speakers": "Top speakers include Dr. A, Dr. B."
    }
    return faq.get(query.lower(), "Sorry, I don’t have that info.")

