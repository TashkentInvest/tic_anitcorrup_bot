"""Static reference data. Departments are synced into the database on startup."""

# code, uzbek, russian
DISTRICTS: list[tuple[str, str, str]] = [
    ("bektemir", "Bektemir tumani", "Бектемирский район"),
    ("chilonzor", "Chilonzor tumani", "Чиланзарский район"),
    ("mirobod", "Mirobod tumani", "Мирабадский район"),
    ("mirzo_ulugbek", "Mirzo Ulug'bek tumani", "Мирзо-Улугбекский район"),
    ("olmazor", "Olmazor tumani", "Алмазарский район"),
    ("shayxontoxur", "Shayxontoxur tumani", "Шайхантахурский район"),
    ("sirgali", "Sirg'ali tumani", "Сергелийский район"),
    ("uchtepa", "Uchtepa tumani", "Учтепинский район"),
    ("yakkasaroy", "Yakkasaroy tumani", "Яккасарайский район"),
    ("yashnobod", "Yashnobod tumani", "Яшнабадский район"),
    ("yunusobod", "Yunusobod tumani", "Юнусабадский район"),
    ("yangihayot", "Yangihayot tumani", "Янгихаётский район"),
]

# code, uzbek, russian (one forum topic per department)
DEPARTMENTS: list[tuple[str, str, str]] = [
    ("road", "Yo'l", "Дороги"),
    ("finance", "Moliya", "Финансы"),
    ("accounting", "Buxgalteriya", "Бухгалтерия"),
    ("hr", "Kadrlar", "Кадры"),
    ("apz", "APZ", "АПЗ"),
    ("renovation", "Renovatsiya", "Реновация"),
    ("land", "Yer", "Земля"),
    ("other", "Boshqa", "Другое"),
]

DISTRICT_BY_CODE = {c: (uz, ru) for c, uz, ru in DISTRICTS}
