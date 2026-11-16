# Business rule in its own file: it can be unit-tested without a database.
PRICE_PER_MINUTE = 0.25   # €
DAILY_CAP = 12.0          # € - maximum price for one day (24 h) of rental
MINUTES_PER_DAY = 24 * 60


def calculate_price(minutes: int) -> float:
    """€0.25 per started minute, never more than €12 per day.

    Stretch goal: the cap applies PER DAY. Every complete day of 24 h costs €12,
    and the remaining minutes are charged €0.25 each, again capped at €12.
      - 40 min           -> 10.00
      - 100 min          -> 12.00  (capped)
      - 24 h + 1 min     -> 12.00 + 0.25  = 12.25
      - 2 days + 2 h     -> 2 x 12 + min(120 x 0.25, 12) = 36.00
    """
    if minutes < 0:
        raise ValueError("minutes must be >= 0")
    full_days, remaining_minutes = divmod(minutes, MINUTES_PER_DAY)
    last_day = min(remaining_minutes * PRICE_PER_MINUTE, DAILY_CAP)
    return round(full_days * DAILY_CAP + last_day, 2)
