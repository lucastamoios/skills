#!/usr/bin/env python3
"""Calculate overtime from BRCondos events and generate timesheet outputs."""

from __future__ import annotations

import argparse
import calendar
import json
import math
import re
import sys
from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any


TIMESTAMP_FORMAT = "%d/%m/%Y %H:%M:%S"

# The profile reader is a required resource of the shared skill distribution.
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "skill-config" / "scripts"))
import skill_profile




@dataclass(frozen=True)
class Event:
    name: str
    control_id: str
    timestamp: datetime
    direction: str


@dataclass
class DayResult:
    date: str
    weekday: str
    entry: str
    exit: str
    expected_exit: str
    break_start: str
    break_end: str
    overtime_minutes: int
    special: bool
    notes: list[str]


DEFAULT_PROFILE: dict[str, Any] = {
    "employer": {"name": "", "cpf": ""},
    "employee": {"name": "", "cpf": "", "role": "Empregada domestica", "ctps": ""},
    "schedule": {},
    "controls": {},
    "special_dates": [],
}


def deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    result = json.loads(json.dumps(base))
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def parse_hhmm(value: str) -> tuple[int, int]:
    match = re.fullmatch(r"(\d{2}):(\d{2})", value or "")
    if not match:
        raise ValueError(f"Invalid HH:MM value: {value!r}")
    hour, minute = map(int, match.groups())
    if hour > 23 or minute > 59:
        raise ValueError(f"Invalid HH:MM value: {value!r}")
    return hour, minute


def direction_for(control_id: str, controls: dict[str, str]) -> str:
    number = control_id.removeprefix("ControlId").strip().split("/", 1)[0]
    if number.startswith(controls["entry_prefix"]):
        return "entry"
    if number.startswith(controls["exit_prefix"]):
        return "exit"
    return "unknown"


def event_from_mapping(item: dict[str, Any], controls: dict[str, str]) -> Event:
    control_id = str(item.get("control_id") or item.get("controlId") or "").strip()
    timestamp_value = str(item.get("timestamp") or item.get("date") or "").strip()
    if not control_id or not timestamp_value:
        raise ValueError(f"Record is missing control_id or timestamp: {item!r}")
    return Event(
        name=str(item.get("name") or "").strip(),
        control_id=control_id.removeprefix("ControlId").strip(),
        timestamp=datetime.strptime(timestamp_value, TIMESTAMP_FORMAT),
        direction=direction_for(control_id, controls),
    )


def parse_raw_records(text: str, controls: dict[str, str]) -> list[Event]:
    pattern = re.compile(
        r"(?P<name>[^\n]+?)\s*\n(?:(?!ControlId)[^\n]*\n)*?"
        r"\s*ControlId\s+(?P<control>\d+/\d+)\s*\n"
        r"(?P<timestamp>\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2}:\d{2})",
        re.IGNORECASE,
    )
    events = [
        event_from_mapping(
            {
                "name": match.group("name").strip(),
                "control_id": match.group("control"),
                "timestamp": match.group("timestamp"),
            }, controls
        )
        for match in pattern.finditer(text)
    ]
    if not events:
        raise ValueError("No ControlId records were found in the input")
    return events


def load_events(path: Path, controls: dict[str, str]) -> list[Event]:
    text = path.read_text(encoding="utf-8")
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        return parse_raw_records(text, controls)
    records = payload.get("records", []) if isinstance(payload, dict) else payload
    if not isinstance(records, list):
        raise ValueError("JSON input must be a list or an object with a records list")
    return [event_from_mapping(item, controls) for item in records]


def load_profile(path: Path | None) -> dict[str, Any]:
    if path is None:
        configured = skill_profile.get("timesheet.profile")
        if not configured:
            raise ValueError("Configure timesheet.profile or pass --profile with a confirmed schedule and controls.")
        path = skill_profile.resolve_path(configured)
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("Profile must be a JSON object")
    profile = deep_merge(DEFAULT_PROFILE, payload)
    schedule = profile["schedule"]
    for key in ("start", "standard_end", "presence_minutes", "tolerance_minutes"):
        if key not in schedule:
            raise ValueError(f"Configure schedule.{key} in the private timesheet profile.")
    controls = profile["controls"]
    entry, exit_ = controls.get("entry_prefix"), controls.get("exit_prefix")
    if not isinstance(entry, str) or not isinstance(exit_, str) or not entry.isdigit() or not exit_.isdigit():
        raise ValueError("Configure numeric entry_prefix and exit_prefix in controls.")
    if entry.startswith(exit_) or exit_.startswith(entry):
        raise ValueError("Entry and exit prefixes must not overlap.")
    return profile


def time_on(day: date, hhmm: str) -> datetime:
    hour, minute = parse_hhmm(hhmm)
    return datetime(day.year, day.month, day.day, hour, minute)


def format_hhmm(value: datetime | None, assumed: bool = False) -> str:
    if value is None:
        return ""
    return value.strftime("%H:%M") + ("*" if assumed else "")


def format_duration(minutes: int) -> str:
    hours, remainder = divmod(minutes, 60)
    return f"{hours}h{remainder:02d}m" if hours else f"{remainder}m"


def calculate(
    events: list[Event], profile: dict[str, Any], year: int, month: int
) -> tuple[list[DayResult], list[str], bool]:
    schedule = profile["schedule"]
    start_value = str(schedule["start"])
    standard_end_value = str(schedule["standard_end"])
    presence_minutes = int(schedule["presence_minutes"])
    tolerance_minutes = int(schedule["tolerance_minutes"])
    special_dates = {date.fromisoformat(value) for value in profile.get("special_dates", [])}

    grouped: dict[date, list[Event]] = defaultdict(list)
    anomalies: list[str] = []
    requires_confirmation = False
    for event in sorted(events, key=lambda current: current.timestamp):
        if event.timestamp.year != year or event.timestamp.month != month:
            anomalies.append(
                f"Ignored out-of-period record: {event.timestamp.strftime(TIMESTAMP_FORMAT)}"
            )
            continue
        grouped[event.timestamp.date()].append(event)

    if not grouped:
        anomalies.append("Nenhum registro encontrado no periodo solicitado")
        requires_confirmation = True

    results: list[DayResult] = []
    for day in sorted(grouped):
        day_events = grouped[day]
        entries = [event.timestamp for event in day_events if event.direction == "entry"]
        exits = [event.timestamp for event in day_events if event.direction == "exit"]
        unknown = [event for event in day_events if event.direction == "unknown"]
        notes: list[str] = []

        if unknown:
            notes.append(f"{len(unknown)} ControlId desconhecido(s)")
            anomalies.append(f"{day.strftime('%d/%m')}: ControlId desconhecido")
            requires_confirmation = True

        entry = min(entries) if entries else None
        exit_time = max(exits) if exits else None
        assumed_entry = False

        if len(entries) > 1:
            spread = math.ceil((max(entries) - min(entries)).total_seconds() / 60)
            notes.append(f"{len(entries)} entradas; primeira usada")
            anomalies.append(f"{day.strftime('%d/%m')}: {len(entries)} entradas ({spread} min entre elas)")
            requires_confirmation |= spread > 30
        if len(exits) > 1:
            spread = math.ceil((max(exits) - min(exits)).total_seconds() / 60)
            notes.append(f"{len(exits)} saidas; ultima usada")
            anomalies.append(f"{day.strftime('%d/%m')}: {len(exits)} saidas ({spread} min entre elas)")
            requires_confirmation |= spread > 30

        special = day.weekday() >= 5 or day in special_dates
        if not entries:
            if special:
                notes.append("entrada ausente")
                anomalies.append(f"{day.strftime('%d/%m')}: dia especial sem entrada")
            else:
                entry = time_on(day, start_value)
                assumed_entry = True
                notes.append("entrada assumida")
                anomalies.append(f"{day.strftime('%d/%m')}: entrada ausente; {start_value} assumido")
        if not exits:
            notes.append("saida ausente")
            anomalies.append(f"{day.strftime('%d/%m')}: saida ausente; extra zerada")

        overtime_minutes = 0
        expected_exit: datetime | None = None
        if not special and entry is not None and exit_time is not None:
            contract_start = time_on(day, start_value)
            difference_minutes = (entry - contract_start).total_seconds() / 60
            if abs(difference_minutes) > tolerance_minutes:
                notes.append("entrada fora da tolerancia; revisar")
                anomalies.append(
                    f"{day.strftime('%d/%m')}: entrada {entry.strftime('%H:%M')} fora da tolerancia"
                )
                requires_confirmation = True
            else:
                expected_exit = (
                    entry + timedelta(minutes=presence_minutes)
                    if entry < contract_start
                    else time_on(day, standard_end_value)
                )
                seconds = (exit_time - expected_exit).total_seconds()
                if seconds > 0:
                    overtime_minutes = math.ceil(seconds / 60)
                elif seconds < -30 * 60:
                    notes.append("saida antecipada; sem desconto")
                    anomalies.append(
                        f"{day.strftime('%d/%m')}: saida {exit_time.strftime('%H:%M')} antes do previsto"
                    )

        results.append(
            DayResult(
                date=day.isoformat(),
                weekday=calendar.day_name[day.weekday()],
                entry=format_hhmm(entry, assumed_entry),
                exit=format_hhmm(exit_time),
                expected_exit=format_hhmm(expected_exit),
                break_start="" if special else str(schedule.get("break_start") or ""),
                break_end="" if special else str(schedule.get("break_end") or ""),
                overtime_minutes=overtime_minutes,
                special=special,
                notes=notes,
            )
        )

    return results, anomalies, requires_confirmation


def build_whatsapp(results: list[DayResult], anomalies: list[str]) -> str:
    lines: list[str] = []
    if anomalies:
        lines.append("Anomalias para revisar:")
        lines.extend(f"- {item}" for item in anomalies)
        lines.append("")

    total = 0
    for result in results:
        if not result.special and result.overtime_minutes > 0:
            day = datetime.fromisoformat(result.date).strftime("%d/%m")
            lines.append(f"{day} → {format_duration(result.overtime_minutes)}")
            total += result.overtime_minutes

    special_results = [result for result in results if result.special]
    if special_results and any(line and not line.startswith("-") for line in lines):
        lines.append("")
    weekday_names = {5: "sabado", 6: "domingo"}
    for result in special_results:
        parsed = datetime.fromisoformat(result.date)
        label = weekday_names.get(parsed.weekday(), "especial")
        period = f"{result.entry or '?'}-{result.exit or '?'}"
        lines.append(f"{parsed.strftime('%d/%m')} {label} → {period}")

    if lines and lines[-1] != "":
        lines.append("")
    lines.append(f"Total: {format_duration(total)}")
    return "\n".join(lines).strip() + "\n"


def generate_pdf(
    output_path: Path,
    profile: dict[str, Any],
    results: list[DayResult],
    year: int,
    month: int,
    draft: bool,
) -> None:
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfbase.pdfmetrics import stringWidth
        from reportlab.pdfgen import canvas
    except ImportError as exc:
        raise RuntimeError("reportlab is required to generate the PDF") from exc

    width, height = A4
    pdf = canvas.Canvas(str(output_path), pagesize=A4)
    pdf.setTitle(f"Folha de ponto {month:02d}/{year}")
    left, right = 36, width - 36

    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawCentredString(width / 2, height - 38, f"Folha de Ponto - Periodo: {month:02d}/{year}")
    if draft:
        pdf.setFillColor(colors.red)
        pdf.setFont("Helvetica-Bold", 8)
        pdf.drawCentredString(width / 2, height - 51, "RASCUNHO: REVISAR ANOMALIAS ANTES DE ASSINAR")
        pdf.setFillColor(colors.black)

    employer = profile["employer"]
    employee = profile["employee"]
    y = height - 70
    box_height = 42
    for title, rows in (
        ("Empregador(a)", [("Nome", employer.get("name", "")), ("CPF", employer.get("cpf", ""))]),
        (
            "Empregado(a)",
            [
                ("Nome", employee.get("name", "")),
                ("CPF", employee.get("cpf", "")),
                ("Cargo", employee.get("role", "")),
                ("CTPS", employee.get("ctps", "")),
            ],
        ),
    ):
        current_height = box_height if title == "Empregador(a)" else 58
        pdf.rect(left, y - current_height, right - left, current_height)
        pdf.setFont("Helvetica-Bold", 8)
        pdf.drawString(left + 4, y - 10, title)
        pdf.line(left, y - 14, right, y - 14)
        pdf.setFont("Helvetica", 8)
        if title == "Empregador(a)":
            pdf.drawString(left + 4, y - 29, f"Nome: {rows[0][1]}")
            pdf.drawString(width / 2 + 6, y - 29, f"CPF: {rows[1][1]}")
        else:
            pdf.drawString(left + 4, y - 29, f"Nome: {rows[0][1]}")
            pdf.drawString(width / 2 + 6, y - 29, f"CPF: {rows[1][1]}")
            pdf.line(left, y - 39, right, y - 39)
            pdf.drawString(left + 4, y - 52, f"Cargo: {rows[2][1]}")
            pdf.drawString(width / 2 + 6, y - 52, f"CTPS: {rows[3][1]}")
        y -= current_height + 12

    columns = [
        ("Dia", 28),
        ("Entrada", 57),
        ("Inicio intervalo", 74),
        ("Fim intervalo", 70),
        ("Saida", 57),
        ("Hora extra", 67),
        ("Assinatura do empregado(a)", right - left - 353),
    ]
    header_height = 27
    row_height = 14.2
    table_top = y
    table_bottom = table_top - header_height - (31 * row_height)
    pdf.rect(left, table_bottom, right - left, table_top - table_bottom)

    x = left
    pdf.setFont("Helvetica-Bold", 6.5)
    for label, column_width in columns:
        if x > left:
            pdf.line(x, table_bottom, x, table_top)
        words = label.split()
        if len(words) > 1 and stringWidth(label, "Helvetica-Bold", 6.5) > column_width - 4:
            midpoint = max(1, len(words) // 2)
            pdf.drawCentredString(x + column_width / 2, table_top - 10, " ".join(words[:midpoint]))
            pdf.drawCentredString(x + column_width / 2, table_top - 19, " ".join(words[midpoint:]))
        else:
            pdf.drawCentredString(x + column_width / 2, table_top - 16, label)
        x += column_width
    pdf.line(left, table_top - header_height, right, table_top - header_height)

    results_by_day = {datetime.fromisoformat(item.date).day: item for item in results}
    days_in_month = calendar.monthrange(year, month)[1]
    pdf.setFont("Helvetica", 7)
    for row in range(1, 32):
        row_top = table_top - header_height - ((row - 1) * row_height)
        row_bottom = row_top - row_height
        pdf.line(left, row_bottom, right, row_bottom)
        pdf.drawCentredString(left + columns[0][1] / 2, row_bottom + 4, str(row))
        result = results_by_day.get(row)
        values = ["", "", "", "", ""]
        if result and row <= days_in_month:
            values = [
                result.entry,
                result.break_start,
                result.break_end,
                result.exit,
                "especial" if result.special else (format_duration(result.overtime_minutes) if result.overtime_minutes else ""),
            ]
        x = left + columns[0][1]
        for value, (_, column_width) in zip(values, columns[1:6]):
            pdf.drawCentredString(x + column_width / 2, row_bottom + 4, value)
            x += column_width

    notes: list[str] = []
    if any(item.entry.endswith("*") for item in results):
        notes.append("* Entrada assumida conforme a regra de calculo.")
    if not profile["schedule"].get("break_start") or not profile["schedule"].get("break_end"):
        notes.append("Intervalo nao preenchido porque o horario nao foi informado.")
    if notes:
        pdf.setFont("Helvetica", 6.5)
        notes_y = table_bottom - 11
        for note in notes:
            pdf.drawString(left, notes_y, note)
            notes_y -= 9

    pdf.setFont("Helvetica", 6)
    pdf.drawRightString(right, 18, "Gerado a partir do historico de acessos do BRCondos")
    pdf.save()


def parse_month(value: str) -> tuple[int, int]:
    match = re.fullmatch(r"(\d{4})-(\d{2})", value)
    if not match:
        raise ValueError("Month must use YYYY-MM")
    year, month = map(int, match.groups())
    if not 1 <= month <= 12:
        raise ValueError("Month must use YYYY-MM")
    return year, month


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--records", type=Path, required=True, help="BRCondos JSON or raw text")
    parser.add_argument("--profile", type=Path, help="Optional profile JSON")
    parser.add_argument("--month", required=True, help="Reference month in YYYY-MM")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--confirmed", action="store_true", help="Mark significant anomalies as reviewed")
    args = parser.parse_args()

    year, month = parse_month(args.month)
    profile = load_profile(args.profile)
    events = load_events(args.records, profile["controls"])
    if not profile["employee"].get("name"):
        names = sorted({event.name for event in events if event.name})
        if len(names) == 1:
            profile["employee"]["name"] = names[0]

    results, anomalies, requires_confirmation = calculate(events, profile, year, month)
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    suffix = f"{year}-{month:02d}"
    calculation_path = output_dir / f"calculo-{suffix}.json"
    whatsapp_path = output_dir / f"resumo-whatsapp-{suffix}.txt"
    pdf_path = output_dir / f"folha-ponto-{suffix}.pdf"

    total_minutes = sum(item.overtime_minutes for item in results if not item.special)
    payload = {
        "period": suffix,
        "status": "review_required" if requires_confirmation and not args.confirmed else "final",
        "requires_confirmation": requires_confirmation and not args.confirmed,
        "anomalies": anomalies,
        "total_overtime_minutes": total_minutes,
        "total_overtime": format_duration(total_minutes),
        "days": [asdict(item) for item in results],
    }
    calculation_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    whatsapp_path.write_text(build_whatsapp(results, anomalies), encoding="utf-8")
    generate_pdf(
        pdf_path,
        profile,
        results,
        year,
        month,
        draft=requires_confirmation and not args.confirmed,
    )

    print(json.dumps({
        "calculation": str(calculation_path),
        "whatsapp": str(whatsapp_path),
        "pdf": str(pdf_path),
        "status": payload["status"],
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
