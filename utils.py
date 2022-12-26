from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta, SU, MO, TU, WE, TH, FR, SA
from tzlocal import get_localzone
import click
import pytz
import json
import sys
import os
import re


def get_config():
    fname = os.path.join(os.path.dirname(os.path.abspath(__file__)), "memconfig.json")
    with open(fname, "rt", encoding="utf-8") as fhandle:
        return json.load(fhandle)

def autocomplete(prefix, words):
    filtered_words = [w for w in words if w.startswith(prefix)]
    if len(filtered_words) < 1:
        return prefix
    if len(filtered_words) == 1:
        return filtered_words[0]
    
    match_str = prefix
    min_word_length = min(len(w) for w in filtered_words)
    idx = len(match_str)
    while True:
        if idx >= min_word_length:
            return match_str
        c = filtered_words[0][idx]
        for w in filtered_words[1:]:
            if w[idx] != c:
                return match_str
        idx += 1
        match_str += c

def convert_datetime_timezone(naive_datetime, from_timezone, to_timezone):
    from_tz_datetime = naive_datetime.replace(tzinfo=from_timezone)
    to_tz_datetime = naive_datetime.replace(tzinfo=to_timezone)
    diff = from_tz_datetime.timestamp() - to_tz_datetime.timestamp()
    return naive_datetime + timedelta(seconds=diff)

def convert_utc_to_local(naive_datetime):
    return convert_datetime_timezone(naive_datetime, pytz.utc, get_localzone())

def convert_local_to_utc(naive_datetime):
    return convert_datetime_timezone(naive_datetime, get_localzone(), pytz.utc)

def parse_delay(delaystr):
    now = datetime.now()   # Local Timezone
    today = datetime(now.year, now.month, now.day) # Local Timezone

    days_of_week = {
        "sunday": SU,
        "monday": MO, 
        "tuesday": TU,
        "wednesday": WE,
        "thursday": TH,
        "friday": FR,
        "saturday": SA
    }
    days_of_week_filtered = [d for d in days_of_week.keys() if d.startswith(delaystr.lower())]
    if len(days_of_week_filtered) > 1:
        raise click.ClickException(f"Multiple day of week matches: {', '.join(days_of_week_filtered)}")
    if len(days_of_week_filtered) == 1:
        rdd = days_of_week[days_of_week_filtered[0]]
        delaytarget = today + relativedelta(weekday=rdd(1))
        if today == delaytarget:
            delaytarget = delaytarget + timedelta(days=7)
        return convert_local_to_utc(delaytarget)

    match = re.search(r"^(?P<delay_number>\d+)(?P<delay_unit>(s|m|(mi)|h|d|w|(mo)|y))$", delaystr, flags=re.IGNORECASE)
    if match:
        delay_number = int(match.group("delay_number"))
        delay_unit = match.group("delay_unit").lower()
        delay_secs = delay_number
        if delay_unit == "m" or delay_unit == "mi":
            delay_secs = delay_number * 60
        if delay_unit == "h":
            delay_secs = delay_number * 60 * 60
        if delay_unit == "d":
            delay_secs = delay_number * 60 * 60 * 24
        if delay_unit == "w":
            delay_secs = delay_number * 60 * 60 * 24 * 7
        if delay_unit == "mo":
            delay_secs = delay_number * 60 * 60 * 24 * 30.44
        if delay_unit == "y":
            delay_secs = delay_number * 60 * 60 * 24 * 365.25
        delaytarget = now + timedelta(seconds=delay_secs)
        return convert_local_to_utc(delaytarget)

    try:
        delaytarget = datetime.fromisoformat(delaystr)
    except:
        raise click.ClickException(f"Unable to parse {delaystr} as ISO-formatted date")
    tzinfo = delaytarget.tzinfo
    tzinfo = tzinfo if tzinfo else get_localzone()
    return convert_datetime_timezone(delaytarget, tzinfo, pytz.utc)

def out(*args, **kwargs):
    debug = '--debug' in (arg.lower() for arg in sys.argv)
    if not debug:
        return
    outf = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
    with open(outf, "at", encoding="utf-8") as fh:
        kwargs["file"] = fh
        print(*args, **kwargs)