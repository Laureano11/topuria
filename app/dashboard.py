from __future__ import annotations

import math
from calendar import monthrange
from collections import defaultdict
from datetime import date, datetime, timedelta
from typing import Iterable

from sqlmodel import Session, select

from app.dates import iso_week_start, now_local_naive, parse_iso_datetime, today_local
from app.models import Habit, HabitEvent


CATEGORY_META = {
    "salud": {"label": "Salud", "icon": "❤️"},
    "dinero": {"label": "Dinero", "icon": "💰"},
    "estudio": {"label": "Estudio", "icon": "📚"},
    "trabajo": {"label": "Trabajo", "icon": "💼"},
}

CADENCE_LABELS = {
    "daily": "diario",
    "weekly": "semanal",
    "monthly": "mensual",
    "yearly": "anual",
    "streak": "racha",
}

CADENCE_WEIGHTS = {
    "daily": 10,
    "weekly": 18,
    "monthly": 30,
    "yearly": 50,
}

TAB_LABELS = {
    "weekly": "Semanal",
    "monthly": "Mensual",
    "yearly": "Anual",
}

FALLBACK_QUOTES = [
    ("No hace falta ir rápido. Hace falta no detenerse.", "Confucio"),
    ("La constancia vence lo que la fuerza no alcanza.", "Proverbio"),    
    ("Hacerlo seguido importa más que hacerlo perfecto.", "Anónimo"),
    ("El dolor que sientes ahora no se compara con la alegria que vendra.", "Anónimo"),
    ("Yo me tengo que parar de puntita para estar a tu altura pero vos no me llegas ni a los pies.", "Anónimo"),
    ("El dolor que sientes ahora no se compara con la alegria que vendra", "Anónimo"),
    ("Yo me tengo que parar de puntita para estar a tu altura pero vos no me llegas ni a los pies", "Anónimo"),
    ("Sos mas alto que yo pero no mas grande", "Anónimo"),
    ("Si Maradona esta en una fiesta de traje y ve venir una pelota embarrada, la para con el pecho", "Diego Maradona"),
    ("El secreto del exito es decir lo que dijiste que ibas a hacer", "Anónimo"),
    ("Si queres comprar sin mirar el precio, tenes que trabajar sin mirar el reloj", "Anónimo"),
    ("Tengo 22 años, no tengo nada para perder pero si todo por ganar", "Anónimo"),
    ("No tuve infancia, naci siendo grande", "Anónimo"),
("Los Beatles se mueren por tocar en una final del mundo, y Messi no haria jueguitos en un concierto de los Beatles", "Anónimo"),
("Ganar no es lo mas importante es lo unico que importa", "Anónimo"),
("Todos hizan la bandera pero solo uno la hizo", "Anónimo"),
("La vida no es justa, la vida es lo que es", "Anónimo"),
("Mira que el cementerio esta lleno de valientes", "Anónimo"),
("La plata va y viene el tiempo solo va", "Anónimo"),
("Nadie le importara por lo que pasaste hasta que ganas, así que gana", "Anónimo"),
("No pain no gain", "Anónimo"),
("The sunset is beautiful isn't it?", "Anónimo"),
("Work so hard that her biggest flex is that she used to know you", "Anónimo"),
("Yo naci siendo nadie y nadie sera como yo", "Anónimo"),
("Hay que juzgar las acciones por sus resultados y no por sus intenciones", "Anónimo"),
("Siempre me quejaba que me quitabas la sabana, ahora que la tengo toda para mi, nunca tuve tanto frio", "Anónimo"),
("In chess sometimes u win, and sometimes u learn", "Anónimo"),
("Hay años que construyen tu exito y hay años que construyen tu caracter", "Anónimo"),
("Es dificil ganarle a alguien que no celebra sus propias victorias", "Anónimo"),
("Quien quiere hacer algo encuentra una manera, quien no quiere hacer nada encuentra una excusa", "Anónimo"),
("You will never change ur life until you change something you do daily. The secret of your success is in your daily routine", "Anónimo"),
("Nobody hears a tree grow but everyone hears it fall", "Anónimo"),
("If people is doubting how far you can go, go so far that u cant hear them anymore", "Anónimo"),
("Take a chance and you may lose. Take not a chance and you have lost already", "Anónimo"),
("Never stay up late for something u wouldnt get up early for", "Anónimo"),
("No te quejes, incluso contigo mismo", "Anónimo"),
("Aquel que piensa mucho antes de dar un paso pasara toda la vida en un solo pie", "Anónimo"),
("It's not over until I win", "Anónimo"),
("Esta comprobado que la abeja aerodinamicamente no puede volar por su peso y su tamaño y cuerpo, solo que ella no lo sabe", "Anónimo"),
("Tanto si piensas que puedes como si piensas que no puedes, en ambos casos estas en lo cierto", "Henry Ford"),
("Stress doesn't come from hard work, stress come from no taking action over something that you can have some control over, stress come from ignoring things that you shouldn't be ignoring", "Jeff Bezos"),
("El momento en el que seras mas joven para empezar algo es hoy", "Anónimo"),
("No hay motivo de arriesgar algo que tienes y necesitas por algo que no tienes ni necesitas", "Warren Buffett"),
("Being uncomfortable is not being exhausted. Being uncomfortable is your mind quitting before ur body", "Anónimo"),
("Discipline is doing what u hate to do, but do it like you love it", "Mike Tyson"),
("Todos se lo merecen uno solo se lo gana", "Trueno"),
("The pain of regret is going to be so much stronger than the pain of discipline", "Anónimo"),
("Creer que podemos lograr algo casi siempre es necesario pero casi nunca es suficiente", "Anónimo"),
("No me gusta correr, por eso corro", "Anónimo"),
("La disciplina pesa gramos, el arrepentimiento toneladas", "Jim Rohn"),
("No tenés que tener ganas, solo tenés que hacerlo", "Anónimo"),
("Solo son un monton de copas vacias", "Hudson Hornet"),
("Es absurdo criticar la ignorancia del pasado con la inteligencia del presente", "Anónimo"),
("Lo difícil lo hago fácil. Lo imposible me toma un poco más de tiempo", "Anónimo"),
("Te van a criticar hagas lo que hagas, asi que por lo menos que te critiquen haciendo lo que te gusta", "Lichi Gapp"),
("Si crees que es cara la factura de haber fallado, espera que te llegue la factura de ni si quiera haberlo intentado", "El Xokas"),
("Maybe god is with him but he's not god", "Max Verstappen"),
("Me encontre con mi yo mas joven para tomar un cafe, prendi un pucho y se levanto se la mesa", "Anónimo"),
("The fears last seconds, the shame last days, but the regret is forever", "Anónimo"),
("El tiempo va a pasar de todas formas. El mejor tiempo para plantar un árbol fue hace 10 años, el segundo mejor es ahora", "Twitter"),
("Hated by everyone. Defeated by none...", "Max Verstappen"),
("Alguien con la mitad de tu IQ está ganando 10 veces más que vos porque no es lo suficientemente inteligente como para dudar de sí mismo", "Twitter finanzas"),
("You can't wait for everything to be perfect to start living your life", "Anónimo"),
("No sos tan importante como vos pensas, a nadie le importa lo que haces o decis asi que no tengas verguenza de nada, verguenza es no vender", "Beltrán Briones"),
("Puedo fallar 1, pero no 2 veces", "Hábitos Atómicos"),
("When you watch the sun go too long you can’t see anything else after", "TikTok de Messi"),
("Menos es mas, la vida se mejora quitando cosas no agregando mas", "Gemini"),
("Cuando lo hacés por vos, podés rendirte. Cuando lo hacés por ella (mamá), rendirse no es una opción", "Anónimo"),
("Yo puedo pintar lo que se me de la gana y sale como yo quiero, eso para mi es pintar bien", "Viejito de Tik Tok"),
("I always go flat out, if i crash, i crash", "Max Verstappen"),
("I dont know and i dont care", "Max Verstappen"),
("No soy exitoso porque tengo plata, yo soy exitoso porque mi mama me quiere", "Davo Xeneize"),
("El éxito es un juego. Cuantas más veces juegues, más veces ganarás. Y cuantas más veces ganes, mejor jugarás", "Libro Cómo Persuadir"),
("¿Estás resolviendo problemas reales por los que el mercado está dispuesto a pagar, o solo estás 'enamorado' de la idea de tener dinero?", "Anónimo"),
("No podés pretender la tranquilidad de quien busca lo ordinario si tu objetivo es lo extraordinario", "Anónimo"),
("Es mas facil ser feliz siendo que teniendo, porque lo q tenes viene de lo que sos", "Mauricio Macri"),
("La vida son 2 dias y uno esta lloviendo", "El Xokas"),
]

DAY_NAMES = [
    "lunes",
    "martes",
    "miércoles",
    "jueves",
    "viernes",
    "sábado",
    "domingo",
]

MONTH_NAMES = [
    "enero",
    "febrero",
    "marzo",
    "abril",
    "mayo",
    "junio",
    "julio",
    "agosto",
    "septiembre",
    "octubre",
    "noviembre",
    "diciembre",
]


def build_dashboard_context(session: Session, active_tab: str = "weekly") -> dict:
    today = today_local()
    now = now_local_naive()
    habits = session.exec(
        select(Habit).where(Habit.active == True).order_by(Habit.id)  # noqa: E712
    ).all()
    habit_ids = [habit.id for habit in habits if habit.id is not None]

    events = []
    if habit_ids:
        events = session.exec(
            select(HabitEvent)
            .where(HabitEvent.habit_id.in_(habit_ids))
            .order_by(HabitEvent.occurred_at)
        ).all()

    events_by_habit: dict[int, list[HabitEvent]] = defaultdict(list)
    for event in events:
        events_by_habit[event.habit_id].append(event)

    positive_habits = [habit for habit in habits if habit.habit_kind != "avoid"]
    streak_habits = [habit for habit in habits if habit.habit_kind == "avoid"]
    daily_habits = [habit for habit in positive_habits if habit.cadence == "daily"]
    panel_habits = {
        cadence: [habit for habit in positive_habits if habit.cadence == cadence]
        for cadence in TAB_LABELS
    }

    daily_rows = [
        _build_daily_habit_row(habit, events_by_habit.get(habit.id, []), today)
        for habit in daily_habits
        if habit.id is not None
    ]

    streak_rows = [
        _build_streak_row(habit, events_by_habit.get(habit.id, []), now)
        for habit in streak_habits
        if habit.id is not None
    ]

    panel_rows = {
        cadence: [
            _build_multi_habit_row(habit, events_by_habit.get(habit.id, []), today)
            for habit in panel_habits[cadence]
            if habit.id is not None
        ]
        for cadence in TAB_LABELS
    }

    character = _build_character(habits, events_by_habit, streak_rows)
    category_progress = _build_category_progress(positive_habits, events_by_habit, today)
    stats = _build_stats(positive_habits, events_by_habit, today)
    quotes = FALLBACK_QUOTES
    quote_index = today.toordinal() % len(quotes)
    quote_text, quote_author = quotes[quote_index]

    return {
        "today_iso": today.isoformat(),
        "quote": quote_text,
        "quote_author": quote_author,
        "quote_index": quote_index,
        "quote_entries": [
            {"text": text, "author": author}
            for text, author in quotes
        ],
        "banner_date": format_date_banner(today),
        "header_date": format_date_header(today),
        "year_progress": build_year_progress(today),
        "active_tab": active_tab if active_tab in TAB_LABELS else "weekly",
        "tab_labels": TAB_LABELS,
        "stats": stats,
        "daily_habits": daily_rows,
        "streaks": streak_rows,
        "panel_habits": panel_rows,
        "annual_goals": panel_rows["yearly"],
        "character": character,
        "category_progress": category_progress,
        "categories": list(CATEGORY_META.values()),
        "cadence_labels": CADENCE_LABELS,
    }


def category_slug(value: str | None) -> str:
    normalized = (value or "").strip().lower()
    legacy_map = {
        "salud": "salud",
        "fitness": "salud",
        "adicciones": "salud",
        "dinero": "dinero",
        "estudio": "estudio",
        "desarrollo personal": "estudio",
        "trabajo": "trabajo",
    }
    return legacy_map.get(normalized, "trabajo")


def category_label(value: str | None) -> str:
    slug = category_slug(value)
    return CATEGORY_META[slug]["label"]


def normalize_category(value: str | None) -> str:
    return category_label(value)


def normalize_cadence(value: str | None) -> str:
    allowed = {"daily", "weekly", "monthly", "yearly", "streak"}
    return value if value in allowed else "daily"


def default_target_for_cadence(cadence: str) -> int:
    defaults = {
        "daily": 1,
        "weekly": 3,
        "monthly": 4,
        "yearly": 12,
        "streak": 7,
    }
    return defaults.get(cadence, 1)


def parse_started_at_text(raw_value: str | None) -> tuple[date | None, str | None]:
    if not raw_value:
        return None, None
    cleaned = raw_value.strip()
    if not cleaned:
        return None, None
    cleaned = cleaned.replace(" ", "T")
    if len(cleaned) == 10:
        cleaned = cleaned + "T00:00:00"
    parsed = datetime.fromisoformat(cleaned)
    return parsed.date(), parsed.isoformat(timespec="seconds")


def redirect_target(tab: str | None) -> str:
    active = tab if tab in TAB_LABELS else "weekly"
    return f"/?tab={active}"


def format_date_header(value: date) -> str:
    return f"{DAY_NAMES[value.weekday()].capitalize()} · {value.day} de {MONTH_NAMES[value.month - 1]} · {value.year}"


def format_date_banner(value: date) -> str:
    month_short = MONTH_NAMES[value.month - 1][:3]
    return f"{DAY_NAMES[value.weekday()].capitalize()}, {value.day} {month_short} {value.year}"


def cadence_human_label(cadence: str) -> str:
    return TAB_LABELS.get(cadence, CADENCE_LABELS.get(cadence, cadence))


def build_year_progress(today: date) -> dict:
    day_of_year = today.timetuple().tm_yday
    days_in_year = 366 if _is_leap_year(today.year) else 365
    iso_week = today.isocalendar().week
    total_iso_weeks = date(today.year, 12, 28).isocalendar().week
    return {
        "day_of_year": day_of_year,
        "days_in_year": days_in_year,
        "day_percentage": int(round((day_of_year / days_in_year) * 100)),
        "week_of_year": iso_week,
        "weeks_in_year": total_iso_weeks,
        "week_percentage": int(round((iso_week / total_iso_weeks) * 100)),
    }


def _is_leap_year(year: int) -> bool:
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


def streak_start_iso(habit: Habit, habit_events: list[HabitEvent]) -> str:
    failures = [event for event in habit_events if event.event_type == "failure"]
    if failures:
        return failures[-1].occurred_at
    if habit.started_at_text:
        return habit.started_at_text
    if habit.started_at:
        return habit.started_at.isoformat() + "T00:00:00"
    return now_local_naive().isoformat(timespec="seconds")


def _build_daily_habit_row(habit: Habit, habit_events: list[HabitEvent], today: date) -> dict:
    done_today = any(
        event.event_type == "completion" and event.occurred_on == today for event in habit_events
    )
    return {
        "id": habit.id,
        "name": habit.name,
        "goal": habit.goal,
        "category_label": category_label(habit.category),
        "category_slug": category_slug(habit.category),
        "done_today": done_today,
        "cadence_label": cadence_human_label(habit.cadence),
    }


def _build_multi_habit_row(habit: Habit, habit_events: list[HabitEvent], today: date) -> dict:
    start, end = _period_bounds(habit.cadence, today)
    count = sum(
        1
        for event in habit_events
        if event.event_type == "completion" and start <= event.occurred_on <= end
    )
    target_count = habit.target_count or default_target_for_cadence(habit.cadence)
    dots = ["filled"] * min(count, target_count)
    dots.extend(["empty"] * max(0, target_count - count))
    if count > target_count:
        dots.extend(["extra"] * (count - target_count))
    return {
        "id": habit.id,
        "name": habit.name,
        "goal": habit.goal,
        "category_label": category_label(habit.category),
        "category_slug": category_slug(habit.category),
        "cadence": habit.cadence,
        "target_count": target_count,
        "current_count": count,
        "frequency_label": _frequency_label(habit.cadence, target_count),
        "dots": dots,
    }


def _build_streak_row(habit: Habit, habit_events: list[HabitEvent], now: datetime) -> dict:
    failures = [event for event in habit_events if event.event_type == "failure"]
    current_start = parse_iso_datetime(streak_start_iso(habit, habit_events))
    current_delta = max(now - current_start, timedelta())

    historical_best = timedelta()
    anchor = parse_iso_datetime(habit.started_at_text) if habit.started_at_text else None
    if anchor is None and habit.started_at:
        anchor = datetime.fromisoformat(habit.started_at.isoformat() + "T00:00:00")
    if anchor is None:
        anchor = current_start

    previous = anchor
    for failure in failures:
        failure_dt = parse_iso_datetime(failure.occurred_at)
        if failure_dt >= current_start:
            break
        historical_best = max(historical_best, failure_dt - previous)
        previous = failure_dt

    best_delta = max(historical_best, current_delta)
    target_days = habit.target_count or default_target_for_cadence("streak")
    pct = min(100, int(current_delta.total_seconds() / max(target_days * 86400, 1) * 100))

    return {
        "id": habit.id,
        "name": habit.name,
        "goal": habit.goal,
        "category_label": category_label(habit.category),
        "category_slug": category_slug(habit.category),
        "current_iso": current_start.isoformat(timespec="seconds"),
        "current_text": humanize_timedelta(current_delta),
        "record_text": humanize_record(best_delta),
        "target_label": f"Objetivo: {target_days} días",
        "progress_pct": pct,
        "target_days": target_days,
        "current_days": current_delta.total_seconds() / 86400,
    }


def _build_stats(habits: list[Habit], events_by_habit: dict[int, list[HabitEvent]], today: date) -> list[dict]:
    week_start = iso_week_start(today)
    month_start = today.replace(day=1)
    year_start = today.replace(month=1, day=1)
    elapsed_week_days = (today - week_start).days + 1
    elapsed_month_days = today.day
    elapsed_year_days = (today - year_start).days + 1
    elapsed_weeks_month = math.ceil(elapsed_month_days / 7)
    elapsed_weeks_year = math.ceil(elapsed_year_days / 7)

    stats = []
    configs = [
        ("Hoy", "accent", {"daily"}, today, today),
        ("Esta semana", "estudio", {"daily", "weekly"}, week_start, today),
        ("Este mes", "dinero", {"daily", "weekly", "monthly"}, month_start, today),
        ("Este año", "trabajo", {"daily", "weekly", "monthly", "yearly"}, year_start, today),
    ]

    for label, stroke, cadences, start, end in configs:
        numerator = 0
        denominator = 0
        for habit in habits:
            if habit.habit_kind == "avoid" or habit.cadence not in cadences or habit.id is None:
                continue

            target = habit.target_count or default_target_for_cadence(habit.cadence)
            habit_events = events_by_habit.get(habit.id, [])
            numerator += sum(
                1
                for event in habit_events
                if event.event_type == "completion" and start <= event.occurred_on <= end
            )

            if label == "Hoy":
                denominator += 1
            elif label == "Esta semana":
                denominator += elapsed_week_days if habit.cadence == "daily" else target
            elif label == "Este mes":
                if habit.cadence == "daily":
                    denominator += elapsed_month_days
                elif habit.cadence == "weekly":
                    denominator += elapsed_weeks_month * target
                else:
                    denominator += target
            else:
                if habit.cadence == "daily":
                    denominator += elapsed_year_days
                elif habit.cadence == "weekly":
                    denominator += elapsed_weeks_year * target
                elif habit.cadence == "monthly":
                    denominator += today.month * target
                else:
                    denominator += target

        percentage = int(round((numerator / denominator) * 100)) if denominator else 0
        circumference = 94.2
        dash_offset = round(circumference * (1 - min(percentage, 100) / 100), 1)
        stats.append(
            {
                "label": label,
                "value": numerator,
                "total": denominator,
                "percentage": percentage,
                "stroke": stroke,
                "dash_offset": dash_offset,
                "sub_label": f"{percentage}% completado" if label != "Este año" else f"{percentage}% del año",
            }
        )

    return stats


def _build_category_progress(
    habits: list[Habit],
    events_by_habit: dict[int, list[HabitEvent]],
    today: date,
) -> list[dict]:
    month_start = today.replace(day=1)
    elapsed_month_days = today.day
    elapsed_weeks_month = math.ceil(elapsed_month_days / 7)
    totals = {slug: {"done": 0, "target": 0} for slug in CATEGORY_META}

    for habit in habits:
        if habit.habit_kind == "avoid" or habit.cadence == "yearly" or habit.id is None:
            continue

        slug = category_slug(habit.category)
        target = habit.target_count or default_target_for_cadence(habit.cadence)
        if habit.cadence == "daily":
            totals[slug]["target"] += elapsed_month_days
        elif habit.cadence == "weekly":
            totals[slug]["target"] += elapsed_weeks_month * target
        elif habit.cadence == "monthly":
            totals[slug]["target"] += target

        totals[slug]["done"] += sum(
            1
            for event in events_by_habit.get(habit.id, [])
            if event.event_type == "completion" and month_start <= event.occurred_on <= today
        )

    rows = []
    for slug, meta in CATEGORY_META.items():
        done = totals[slug]["done"]
        target = totals[slug]["target"]
        pct = int(round((done / target) * 100)) if target else 0
        rows.append(
            {
                "slug": slug,
                "label": meta["label"],
                "percentage": pct,
            }
        )
    return rows


def _build_character(
    habits: list[Habit],
    events_by_habit: dict[int, list[HabitEvent]],
    streak_rows: list[dict],
) -> dict:
    total_xp = 0
    category_xp = {slug: 0 for slug in CATEGORY_META}
    for habit in habits:
        if habit.id is None or habit.habit_kind == "avoid":
            continue
        weight = CADENCE_WEIGHTS.get(habit.cadence, 10)
        slug = category_slug(habit.category)
        completions = sum(
            1 for event in events_by_habit.get(habit.id, []) if event.event_type == "completion"
        )
        gained = completions * weight
        category_xp[slug] += gained
        total_xp += gained

    for streak in streak_rows:
        bonus = int(streak["current_days"] * 4)
        slug = streak["category_slug"]
        category_xp[slug] += bonus
        total_xp += bonus

    level, level_floor, next_requirement = level_from_xp(total_xp)
    level_progress = total_xp - level_floor
    next_level_delta = next_requirement - level_floor
    xp_pct = int(round((level_progress / next_level_delta) * 100)) if next_level_delta else 0

    attributes = []
    for slug, meta in CATEGORY_META.items():
        score = category_xp[slug]
        fill = min(100, score if score < 100 else 35 + min(65, score // 4))
        attributes.append(
            {
                "slug": slug,
                "label": meta["label"],
                "score": score,
                "fill": fill,
            }
        )

    available_today = sum(
        CADENCE_WEIGHTS.get(habit.cadence, 10)
        for habit in habits
        if habit.habit_kind != "avoid" and habit.cadence == "daily"
    )

    return {
        "name": "Laureano",
        "avatar": "🧑‍💻",
        "level": level,
        "xp": total_xp,
        "xp_into_level": level_progress,
        "xp_needed": next_level_delta,
        "xp_to_next_total": next_requirement,
        "xp_pct": xp_pct,
        "attributes": attributes,
        "available_today": available_today,
    }


def _period_bounds(cadence: str, today: date) -> tuple[date, date]:
    if cadence == "weekly":
        return iso_week_start(today), today
    if cadence == "monthly":
        return today.replace(day=1), today
    if cadence == "yearly":
        return today.replace(month=1, day=1), today
    return today, today


def _frequency_label(cadence: str, target_count: int) -> str:
    unit = {
        "weekly": "vez por semana" if target_count == 1 else "veces por semana",
        "monthly": "vez por mes" if target_count == 1 else "veces por mes",
        "yearly": "vez por año" if target_count == 1 else "veces por año",
    }.get(cadence, "vez")
    return f"{target_count} {unit}"


def level_from_xp(xp: int) -> tuple[int, int, int]:
    level = 1
    floor = 0
    next_total = 300
    step = 300
    while xp >= next_total:
        level += 1
        floor = next_total
        step += 80
        next_total += step
    return level, floor, next_total


def humanize_timedelta(delta: timedelta) -> str:
    total_seconds = max(int(delta.total_seconds()), 0)
    days = total_seconds // 86400
    hours = (total_seconds % 86400) // 3600
    minutes = (total_seconds % 3600) // 60
    return f"{days}d {hours}h {minutes}m"


def humanize_record(delta: timedelta) -> str:
    total_days = max(delta.total_seconds() / 86400, 0)
    if total_days >= 2:
        return f"Récord personal: {int(total_days)} días"
    if total_days >= 1:
        return "Récord personal: 1 día"
    hours = max(int(delta.total_seconds() // 3600), 0)
    return f"Récord personal: {hours} horas"