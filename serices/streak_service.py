from datetime import datetime

def update_streak(user):
    today = datetime.utcnow().date()

    if "last_quiz_date" not in user:
        return 1

    last_date = user["last_quiz_date"].date()
    difference = (today - last_date).days

    if difference == 1:
        return user.get("streak", 0) + 1
    elif difference == 0:
        return user.get("streak", 0)
    else:
        return 1
