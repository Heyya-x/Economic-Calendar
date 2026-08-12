import re
from datetime import datetime, timedelta


INPUT = "US_KEY_raw.ics"
OUTPUT = "US_KEY.ics"


def fold_line(line):
    return line.replace("\n", "\\n")


def modify_event(event):

    # 获取开始时间
    dt_match = re.search(
        r"DTSTART(?:;TZID=.*?)?:(\d{8})T(\d{6})",
        event
    )

    if not dt_match:
        return event


    date = dt_match.group(1)
    time = dt_match.group(2)

    display_time = (
        time[:2] +
        ":" +
        time[2:4]
    )


    # 原 SUMMARY

    summary_match = re.search(
        r"SUMMARY:(.*)",
        event
    )

    if summary_match:

        old_summary = summary_match.group(1)

        if not old_summary.startswith(display_time):

            new_summary = (
                f"SUMMARY:{old_summary} {display_time}"
            )

            event = re.sub(
                r"SUMMARY:.*",
                new_summary,
                event
            )


    # 修改 DTSTART 全天事件

    event = re.sub(
        r"DTSTART(?:;TZID=.*?)?:\d{8}T\d{6}",
        f"DTSTART;VALUE=DATE:{date}",
        event
    )


    # 修改 DTEND

    dt = datetime.strptime(
        date,
        "%Y%m%d"
    )

    next_day = (
        dt + timedelta(days=1)
    ).strftime("%Y%m%d")


    event = re.sub(
        r"DTEND(?:;TZID=.*?)?:\d{8}T\d{6}",
        f"DTEND;VALUE=DATE:{next_day}",
        event
    )


    # 删除旧 VALARM

    event = re.sub(
        r"BEGIN:VALARM.*?END:VALARM",
        "",
        event,
        flags=re.S
    )


    # 添加 09:00 提醒

    alarm = f"""
BEGIN:VALARM
ACTION:DISPLAY
TRIGGER;VALUE=DATE-TIME:{date}T090000
DESCRIPTION:{display_time} Reminder
END:VALARM
"""


    event += alarm.strip()


    return event



with open(INPUT, encoding="utf-8") as f:
    content = f.read()


events = re.findall(
    r"BEGIN:VEVENT.*?END:VEVENT",
    content,
    flags=re.S
)


for event in events:

    new_event = modify_event(event)

    content = content.replace(
        event,
        new_event
    )


with open(
    OUTPUT,
    "w",
    encoding="utf-8"
) as f:

    f.write(content)


print("Done")
