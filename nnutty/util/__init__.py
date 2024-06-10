
def pretty_time_delta(time_delta):
    days, remainder = divmod(time_delta, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)

    # Format the time delta into "H hours, M minutes, S seconds left"
    pretty_time = f"{int(seconds)} seconds"
    if minutes > 0: pretty_time = f"{int(minutes)} minutes, "  + pretty_time
    if hours > 0: pretty_time = f"{int(hours)} hours, " + pretty_time
    if days > 0: pretty_time = f"{int(days)} days, " + pretty_time
    return pretty_time