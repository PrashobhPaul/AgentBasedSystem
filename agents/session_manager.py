import pandas as pd

def get_available_sessions(interests):
    df = pd.read_csv("data/sessions.csv")
    return df[df["topic"].isin(interests) & (df["max_seats"] > 0)].to_dict(orient="records")

