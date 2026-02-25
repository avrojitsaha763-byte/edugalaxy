def get_medal(xp):
    if xp >= 300:
        return "Gold"
    elif xp >= 150:
        return "Silver"
    elif xp >= 50:
        return "Bronze"
    else:
        return "None"
