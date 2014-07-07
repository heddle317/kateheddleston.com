import datetime


def now_utc():
    return datetime.datetime.utcnow()


def format_date(date, format='%B %d, %Y'):
    return datetime.datetime.strftime(date, format)


def relative_time(date):
    time_diff = now_utc() - date
    if time_diff.days < 1:
        if time_diff.seconds < 60 * 60:
            return str(time_diff.seconds / 60) + " minutes ago"
        return str(time_diff.seconds / (60 * 60)) + " hours ago"
    elif time_diff.days < 31:
        return str(time_diff.days) + " days ago"
    elif time_diff.days < 365:
        return str(time_diff.days / 31) + " months ago"
    return str(time_diff.days / 365) + " years ago"
