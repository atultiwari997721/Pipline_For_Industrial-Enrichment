\
\
\
   
FRACTION_MAP = {
    0.015625: "1/64",
    0.03125: "1/32",
    0.046875: "3/64",
    0.0625: "1/16",
    0.078125: "5/64",
    0.09375: "3/32",
    0.109375: "7/64",
    0.125: "1/8",
    0.140625: "9/64",
    0.15625: "5/32",
    0.171875: "11/64",
    0.1875: "3/16",
    0.203125: "13/64",
    0.21875: "7/32",
    0.234375: "15/64",
    0.25: "1/4",
    0.265625: "17/64",
    0.28125: "9/32",
    0.296875: "19/64",
    0.3125: "5/16",
    0.328125: "21/64",
    0.34375: "11/32",
    0.359375: "23/64",
    0.375: "3/8",
    0.390625: "25/64",
    0.40625: "13/32",
    0.421875: "27/64",
    0.4375: "7/16",
    0.453125: "29/64",
    0.46875: "15/32",
    0.484375: "31/64",
    0.5: "1/2",
    0.515625: "33/64",
    0.53125: "17/32",
    0.546875: "35/64",
    0.5625: "9/16",
    0.578125: "37/64",
    0.59375: "19/32",
    0.609375: "39/64",
    0.625: "5/8",
    0.640625: "41/64",
    0.65625: "21/32",
    0.671875: "43/64",
    0.6875: "11/16",
    0.703125: "45/64",
    0.71875: "23/32",
    0.734375: "47/64",
    0.75: "3/4",
    0.765625: "49/64",
    0.78125: "25/32",
    0.796875: "51/64",
    0.8125: "13/16",
    0.828125: "53/64",
    0.84375: "27/32",
    0.859375: "55/64",
    0.875: "7/8",
    0.890625: "57/64",
    0.90625: "29/32",
    0.921875: "59/64",
    0.9375: "15/16",
    0.953125: "61/64",
    0.96875: "31/32",
    0.984375: "63/64",
}

APPROVED_UOM = {
                         
    "inch": "in",
    "inches": "in",
    "in.": "in",
    "in": "in",
    "\"": "in",
    "foot": "ft",
    "feet": "ft",
    "ft.": "ft",
    "ft": "ft",
    "'": "ft",
    "yard": "yd",
    "yards": "yd",
    "yd": "yd",
    "millimeter": "mm",
    "millimeters": "mm",
    "mm": "mm",
    "centimeter": "cm",
    "centimeters": "cm",
    "cm": "cm",
    "meter": "m",
    "meters": "m",
    "m": "m",

    "volt": "V",
    "volts": "V",
    "v": "V",
    "vac": "VAC",
    "vdc": "VDC",
    "amp": "A",
    "amps": "A",
    "ampere": "A",
    "amperes": "A",
    "a": "A",
    "milliamp": "mA",
    "watt": "W",
    "watts": "W",
    "w": "W",
    "kilowatt": "kW",
    "kw": "kW",
    "kilowatt-hour": "kW-hr",
    "kwh": "kW-hr",
    "kw-hr": "kW-hr",
    "hertz": "Hz",
    "hz": "Hz",

    "psi": "psi",
    "psig": "psig",
    "bar": "bar",
    "gpm": "gpm",
    "gallons per minute": "gpm",
    "cfm": "cfm",
    "decibel": "dBA",
    "decibels": "dBA",
    "dba": "dBA",
    "db": "dBA",

    "pound": "lb",
    "pounds": "lb",
    "lbs": "lb",
    "lb": "lb",
    "ounce": "oz",
    "ounces": "oz",
    "oz": "oz",
    "gram": "g",
    "grams": "g",
    "g": "g",
    "kilogram": "kg",
    "kilograms": "kg",
    "kg": "kg",

    "rpm": "rpm",
    "revolutions per minute": "rpm",

    "piece": "pc",
    "pieces": "pc",
    "pc": "pc",
    "pack": "pk",
    "pk": "pk",
    "box": "box",
    "pair": "pr",
    "set": "set",
    "roll": "roll",
}

def normalize_uom(raw_uom: str) -> str:
                                                                             
    if not raw_uom:
        return ""
    clean = raw_uom.strip().lower()
    return APPROVED_UOM.get(clean, raw_uom.strip())

def decimal_to_trade_fraction(val: float, tolerance: float = 0.01) -> str:
\
\
\
       
    integer_part = int(val)
    decimal_part = round(val - integer_part, 6)

    if decimal_part == 0:
        return str(integer_part)

    closest_fraction = None
    min_diff = float("inf")
    for d_val, frac_str in FRACTION_MAP.items():
        diff = abs(d_val - decimal_part)
        if diff < min_diff:
            min_diff = diff
            closest_fraction = frac_str

    if min_diff <= tolerance and closest_fraction:
        if integer_part == 0:
            return closest_fraction
        return f"{integer_part}-{closest_fraction}"

    return f"{val:.2f}".rstrip("0").rstrip(".")

def format_dimension_string(raw_dim_str: str) -> str:
\
\
\
       
    if not raw_dim_str:
        return ""
    s = raw_dim_str.replace('"', ' in').replace("'", " ft")
    return s
