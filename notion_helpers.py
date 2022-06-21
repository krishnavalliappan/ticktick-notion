from datetime import datetime
from dateutil import tz


def ticktickDate_to_isoFormat(date, timezone):
    date = date[:-2] + ":" + date[-2:]
    utc_time = datetime.fromisoformat(date)
    local_timezone = tz.gettz(timezone)
    return utc_time.astimezone(local_timezone)


def priority_convert(priority_value):
    if priority_value == 1:
        return "Low"
    elif priority_value == 3:
        return "Medium"
    elif priority_value == 5:
        return "High 🔥"
    else:
        return "None"


def focus_summary_convert(focus_list, input_type):
    if focus_list:
        pomo_count = 0
        duration = 0
        for focus in focus_list:
            pomo_count = pomo_count + focus["pomoCount"]
            duration = duration + focus["pomoDuration"] + focus["stopwatchDuration"]
        if input_type == "pomo":
            return pomo_count
        else:
            return duration
    else:
        return 0


def add_checklist_content(task):
    list_items = []
    if task["items"]:
        list_items.append({
            "object": "block",
            "type": "heading_2",
            "heading_2": {
                "rich_text": [{"type": "text", "text": {"content": "Subtasks"}}]
            }
        })
        for item in task["items"]:
            title = item["title"]
            checked = False
            if item["status"] == 2:
                checked = True
            if item["status"] != 1:
                append_item = {
                    "object": "block",
                    "type": "to_do",
                    "to_do": {
                        "rich_text": [{"type": "text", "text": {"content": title}}],
                        "checked": checked,
                        "color": "default"
                    }
                }
                list_items.append(append_item)
    if task["content"]:
        list_items.append({
            "object": "block",
            "type": "heading_2",
            "heading_2": {
                "rich_text": [{"type": "text", "text": {"content": "Content"}}]
            }
        })
        append_item = {
            "type": "paragraph",
            "paragraph": {
                "rich_text": [{"type": "text", "text": {"content": task["content"]}}],
                "color": "default",
            }
        }
        list_items.append(append_item)

    return list_items


def kind_converter(kind):
    if kind == "CHECKLIST":
        return "Checklist Tasks"
    elif kind == "NOTE":
        return "Note"
    else:
        return "Task"


def recurring_task_check(task):
    if "repeatFlag" in task.keys():
        if task["repeatFlag"]:
            return True
