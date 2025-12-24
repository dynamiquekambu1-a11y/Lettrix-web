from datetime import datetime


class SafeDict(dict):
    def __missing__(self, key):
        return "{" + key + "}"


def pretty_date(s):
    if not s:
        return ""
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(s, fmt).strftime("%B %d, %Y")
        except:
            continue
    return s


def generate_leave_text(user_info):
    info = user_info.copy()
    info["start_date"] = pretty_date(info.get("start_date"))
    info["end_date"] = pretty_date(info.get("end_date"))
    info["submission_date"] = pretty_date(info.get("submission_date"))

    parts = []
    parts.append(f"To: {info.get('supervisor_name', '')}")
    parts.append(f"From: {info.get('employee_full_name', '')} ({info.get('position', '')})")
    if info.get("department"):
        parts.append(f"Department: {info.get('department')}")
    parts.append(f"Date: {info.get('submission_date', '')}")
    parts.append("")
    parts.append(f"Subject: Leave Request ({info.get('leave_type', '')})")
    parts.append("")
    parts.append(
        f"Dear {info.get('supervisor_name', '')},\n\n"
        f"I would like to request {info.get('total_days', '')} day(s) of {info.get('leave_type', '')} leave "
        f"from {info.get('start_date', '')} to {info.get('end_date', '')}. "
        f"The reason for this leave is as follows:\n{info.get('reason', '')}"
    )
    if info.get("emergency_contact"):
        parts.append(f"\nEmergency Contact: {info.get('emergency_contact')}")
    if info.get("backup_plan"):
        parts.append(f"\nBackup plan / coverage: {info.get('backup_plan')}")
    parts.append("")
    if info.get("signer_name") or info.get("signer_role"):
        parts.append(f"Sincerely,\n{info.get('signer_name', '')}\n{info.get('signer_role', '')}")

    full_text = "\n\n".join(parts)
    return {"full_text": full_text}
