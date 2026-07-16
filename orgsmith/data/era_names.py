"""Era-appropriate first names, bundled offline (M8).

A roster generated for a 1995 firm should not be full of names that first
became common in 2010. `cindergrove-advisors` (founded 1995) shipped with a
modern Faker roster, and the README called it a known anachronism reserved
for this turn.

The table is keyed by BIRTH decade. A person active in a given year was born
roughly 25-60 years earlier, so `foundation/scaffold.py` maps the org's era
to a band of birth decades and draws each first name from the decade that
person most plausibly carries. Names are pooled across gender: nothing
downstream models gender, and pooling keeps the draw a single stream.

Source: broadly the most common US given names by decade of birth (Social
Security card applications are the usual public basis for such lists). These
are representative, not exhaustive or authoritative; the goal is era FLAVOR
that survives a reader's glance, not demographic fidelity. No network, no
generated data: this is a literal table checked into the repo.

Decades below 1940 and above 2000 are handled by clamping in the caller, so
a 1930s-founded firm draws 1940s names and a 2020s firm draws 2000s names
rather than the table needing every edge.
"""

# 24-32 names per decade: enough that a 6-person roster plus a handful of
# externals rarely collides, few enough to stay curated and era-legible.
ERA_FIRST_NAMES: dict[int, list[str]] = {
    1940: [
        "James", "Robert", "John", "William", "Richard", "Charles", "David",
        "Thomas", "Ronald", "Gary", "Donald", "Kenneth", "Mary", "Barbara",
        "Patricia", "Carol", "Linda", "Nancy", "Sandra", "Judith", "Betty",
        "Margaret", "Shirley", "Joan", "Dorothy", "Joyce", "Marilyn",
        "Frances", "Gloria", "Janet",
    ],
    1950: [
        "Michael", "James", "Robert", "John", "David", "William", "Richard",
        "Thomas", "Mark", "Steven", "Gary", "Larry", "Mary", "Linda",
        "Patricia", "Susan", "Deborah", "Barbara", "Debra", "Karen", "Nancy",
        "Donna", "Cynthia", "Sandra", "Pamela", "Sharon", "Kathleen",
        "Carol", "Diane", "Brenda",
    ],
    1960: [
        "Michael", "David", "John", "James", "Robert", "Mark", "William",
        "Richard", "Thomas", "Jeffrey", "Steven", "Joseph", "Lisa", "Mary",
        "Susan", "Karen", "Kimberly", "Patricia", "Linda", "Donna", "Michelle",
        "Cynthia", "Sandra", "Deborah", "Tammy", "Pamela", "Lori", "Laura",
        "Julie", "Brenda",
    ],
    1970: [
        "Michael", "Christopher", "Jason", "David", "James", "John", "Robert",
        "Brian", "William", "Matthew", "Joseph", "Daniel", "Jennifer", "Amy",
        "Melissa", "Michelle", "Kimberly", "Lisa", "Angela", "Heather",
        "Stephanie", "Nicole", "Jessica", "Elizabeth", "Rebecca", "Kelly",
        "Christina", "Amanda", "Julie", "Laura",
    ],
    1980: [
        "Michael", "Christopher", "Matthew", "Joshua", "David", "James",
        "Daniel", "Robert", "John", "Joseph", "Jason", "Justin", "Jessica",
        "Jennifer", "Amanda", "Ashley", "Sarah", "Stephanie", "Melissa",
        "Nicole", "Elizabeth", "Heather", "Tiffany", "Michelle", "Amber",
        "Megan", "Rachel", "Amy", "Lauren", "Kayla",
    ],
    1990: [
        "Michael", "Christopher", "Matthew", "Joshua", "Jacob", "Nicholas",
        "Andrew", "Daniel", "Tyler", "Joseph", "Brandon", "David", "Ashley",
        "Jessica", "Emily", "Sarah", "Samantha", "Amanda", "Brittany",
        "Elizabeth", "Taylor", "Megan", "Hannah", "Kayla", "Lauren", "Stephanie",
        "Rachel", "Jennifer", "Nicole", "Alexis",
    ],
    2000: [
        "Jacob", "Michael", "Joshua", "Matthew", "Daniel", "Christopher",
        "Andrew", "Ethan", "Joseph", "William", "Anthony", "Ryan", "Emily",
        "Madison", "Emma", "Olivia", "Hannah", "Abigail", "Isabella", "Samantha",
        "Elizabeth", "Ashley", "Alexis", "Sarah", "Sophia", "Alyssa", "Grace",
        "Ava", "Taylor", "Brianna",
    ],
}

_MIN_DECADE = min(ERA_FIRST_NAMES)
_MAX_DECADE = max(ERA_FIRST_NAMES)


def names_for_birth_year(birth_year: int) -> list[str]:
    """The name pool for someone born in `birth_year`, clamping to the table's
    range so callers never have to know its bounds."""
    decade = (birth_year // 10) * 10
    decade = max(_MIN_DECADE, min(_MAX_DECADE, decade))
    return ERA_FIRST_NAMES[decade]
