import datetime
import inflect


def now_utc():
    return datetime.datetime.utcnow()


def format_date(date, format='%B %d, %Y'):
    if not date:
        return ''
    return datetime.datetime.strftime(date, format)


def parse_date(date, format='%Y-%m-%dT%H:%M:%S'):
    if not date:
        return None
    return datetime.datetime.strptime(date, format)


def relative_time(date):
    if not date:
        return ''
    time_diff = now_utc() - date
    if time_diff.days < 1:
        if time_diff.seconds < 60 * 60:
            diff = time_diff.seconds / 60
            return "{} {} ago".format(diff, pluralize('minute', diff))
        diff = time_diff.seconds / (60 * 60)
        return "{} {} ago".format(diff, pluralize('hour', diff))
    elif time_diff.days < 31:
        diff = time_diff.days
        return "{} {} ago".format(diff, pluralize('day', diff))
    elif time_diff.days < 365:
        diff = time_diff.days / 31
        return "{} {} ago".format(diff, pluralize('month', diff))
    diff = time_diff.days / 365
    return "{} {} ago".format(diff, pluralize('year', diff))


def pluralize(word, num):
    if num != 1:
        p = inflect.engine()
        return p.plural(word)
    return word
