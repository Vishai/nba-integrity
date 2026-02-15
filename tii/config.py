"""Case study definitions and constants for TII backtesting."""

CASES = {
    "A": {
        "team_abbr": "PHI",
        "team_id": 1610612755,
        "season": "2013-14",
        "team_name": "Philadelphia 76ers",
        "archetype": "The Obvious Tank",
        "expected_classification": "Red",
        "playoff_cutoff_seed": 8,
    },
    "B": {
        "team_abbr": "PHI",
        "team_id": 1610612755,
        "season": "2015-16",
        "team_name": "Philadelphia 76ers",
        "archetype": "The Obvious Tank (sustained)",
        "expected_classification": "Red",
        "playoff_cutoff_seed": 8,
    },
    "C": {
        "team_abbr": "POR",
        "team_id": 1610612757,
        "season": "2022-23",
        "team_name": "Portland Trail Blazers",
        "archetype": "Mid-Season Pivot / Integrity Failure",
        "expected_classification": "Orange/Red",
        "playoff_cutoff_seed": 10,
    },
    "D": {
        "team_abbr": "WAS",
        "team_id": 1610612764,
        "season": "2023-24",
        "team_name": "Washington Wizards",
        "archetype": "Legitimate Rebuild vs. Obvious Tank (ambiguous)",
        "expected_classification": "Yellow/Orange",
        "playoff_cutoff_seed": 10,
    },
    "E": {
        "team_abbr": "UTA",
        "team_id": 1610612762,
        "season": "2024-25",
        "team_name": "Utah Jazz",
        "archetype": "The Obvious Tank (current)",
        "expected_classification": "Red",
        "playoff_cutoff_seed": 10,
    },
    "F": {
        "team_abbr": "MIN",
        "team_id": 1610612750,
        "season": "2014-15",
        "team_name": "Minnesota Timberwolves",
        "archetype": "Legitimate Rebuild (control)",
        "expected_classification": "Green",
        "playoff_cutoff_seed": 8,
    },
    "G": {
        "team_abbr": "GSW",
        "team_id": 1610612744,
        "season": "2019-20",
        "team_name": "Golden State Warriors",
        "archetype": "Injury-Wrecked Contender (control)",
        "expected_classification": "Green",
        "playoff_cutoff_seed": 10,
    },
    "H": {
        "team_abbr": "OKC",
        "team_id": 1610612760,
        "season": "2023-24",
        "team_name": "Oklahoma City Thunder",
        "archetype": "Competitive Team — Strategic Rest/Shelving",
        "expected_classification": "Yellow",
        "playoff_cutoff_seed": 10,
    },
}

# Conference membership for elimination computation
EAST_TEAMS = {
    1610612755,  # PHI
    1610612764,  # WAS
    1610612738,  # BOS
    1610612751,  # BKN
    1610612752,  # NYK
    1610612761,  # TOR
    1610612741,  # CHI
    1610612739,  # CLE
    1610612765,  # DET
    1610612754,  # IND
    1610612749,  # MIL
    1610612737,  # ATL
    1610612766,  # CHA
    1610612748,  # MIA
    1610612753,  # ORL
}

WEST_TEAMS = {
    1610612744,  # GSW
    1610612746,  # LAC
    1610612747,  # LAL
    1610612756,  # PHX
    1610612758,  # SAC
    1610612743,  # DEN
    1610612750,  # MIN
    1610612760,  # OKC
    1610612757,  # POR
    1610612762,  # UTA
    1610612742,  # DAL
    1610612745,  # HOU
    1610612763,  # MEM
    1610612740,  # NOP
    1610612759,  # SAS
}

# All-Star break dates (Friday of ASB weekend)
ASB_DATES = {
    "2013-14": "2014-02-14",
    "2014-15": "2015-02-13",
    "2015-16": "2016-02-12",
    "2019-20": "2020-02-14",
    "2022-23": "2023-02-17",
    "2023-24": "2024-02-16",
    "2024-25": "2025-02-14",
}

# Trade deadline dates
TRADE_DEADLINES = {
    "2013-14": "2014-02-20",
    "2014-15": "2015-02-19",
    "2015-16": "2016-02-18",
    "2019-20": "2020-02-06",
    "2022-23": "2023-02-09",
    "2023-24": "2024-02-08",
    "2024-25": "2025-02-06",
}

# TII component weights (from Stewardship Reform Plan Section IV)
WEIGHTS = {
    "SAS": 0.30,
    "NRCI": 0.25,
    "RIS": 0.25,
    "BTCA": 0.20,
}

# Classification thresholds
CLASSIFICATIONS = [
    (0, 25, "Green"),
    (26, 50, "Yellow"),
    (51, 75, "Orange"),
    (76, 100, "Red"),
]


def get_case(case_id: str) -> dict:
    """Get case config by letter, raising if not found or skipped."""
    case_id = case_id.upper()
    if case_id not in CASES:
        raise ValueError(f"Unknown case '{case_id}'. Valid: {', '.join(CASES.keys())}")
    case = CASES[case_id]
    if case.get("skip"):
        raise ValueError(f"Case {case_id} is deferred: {case.get('note', 'no reason given')}")
    return case


def get_conference(team_id: int) -> str:
    """Return 'East' or 'West' for a team."""
    if team_id in EAST_TEAMS:
        return "East"
    if team_id in WEST_TEAMS:
        return "West"
    raise ValueError(f"Unknown team_id {team_id}")


def classify_tii(score: float) -> str:
    """Return Green/Yellow/Orange/Red for a TII score."""
    for low, high, label in CLASSIFICATIONS:
        if low <= score <= high:
            return label
    return "Red" if score > 100 else "Green"
