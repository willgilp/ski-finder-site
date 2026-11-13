from drafter import *
from dataclasses import dataclass

set_site_information(
    author="CS1 Student",
    description="Ski Finder helps skiers find skis based on their skill level, "
                "preferred terrain, and budget.",
    sources="",
    planning="",
    links=["https://github.com/willgilp/ski-finder-site"]
)


# This class stores information about one type of ski.
@dataclass
class Ski:
    name: str
    terrain: str
    skill_level: str
    price: int
    description: str
    is_favorite: bool


# This class stores all the information the website needs.
@dataclass
class State:
    skill_level: str
    preferred_terrain: str
    height: str
    weight: str
    budget: str
    ski_options: list[Ski]
    recommended_skis: list[Ski]
    favorite_skis: list[Ski]
    message: str
    viewing_ski: str


@route
def index(state: State) -> Page:
    """
    Initial page that you are greeted with.
    Gives you 3 different options of buttons to click from.
    """
    page = Page(state, [
        Header("Welcome to Ski Finder!"),
        "Find skis that fit your experience, preferred terrain, and budget.",
        "Not sure what certain ski terms mean? Ski Finder helps with that.",
        "",
        Button("Find My Skis", "questionnaire_page"),
        Button("View My Favorites", "favorites_page"),
        Button("About Ski Finder", "about_page")
    ])

    return page


@route
def questionnaire_page(state: State) -> Page:
    """
    Questionnaire page that helps you find skis recommended
    for your preferences.
    """
    page = Page(state, [
        Header("Ski Finder Questionnaire"),
        "Choose the answers that best describe you.",
        "",
        "What is your skiing skill level?",
        SelectBox("skill_level", [
            "Beginner", "Intermediate", "Advanced"
        ], state.skill_level),
        "",
        "What type of terrain do you prefer?",
        SelectBox("preferred_terrain", [
            "Groomed runs", "All-mountain", "Powder"
        ], state.preferred_terrain),
        "",
        "What is your height in inches?",
        TextBox("height", state.height),
        "",
        "What is your weight in pounds?",
        TextBox("weight", state.weight),
        "",
        "What is your budget?",
        SelectBox("budget", [
            "Under $300", "$300-$500", "$500-$800", "$800+"
        ], state.budget),
        "",
        Button("Find My Recommendations", "submit_preferences"),
        Button("Reset My Answers", "reset_questionnaire"),
        Button("Back to Home", "index")
    ])

    return page


@route
def submit_preferences(state: State, skill_level: str,
                       preferred_terrain: str, height: str,
                       weight: str, budget: str) -> Page:
    """
    This route receives all the answers from the questionnaire
    and processes the answers.
    """
    state.skill_level = skill_level
    state.preferred_terrain = preferred_terrain
    state.height = height
    state.weight = weight
    state.budget = budget

    state.recommended_skis = []

    budget_limit = 0

    if state.budget == "Under $300":
        budget_limit = 299
    elif state.budget == "$300-$500":
        budget_limit = 500
    elif state.budget == "$500-$800":
        budget_limit = 800
    else:
        budget_limit = 10000

    for ski in state.ski_options:
        if (ski.terrain == state.preferred_terrain
                and ski.skill_level == state.skill_level
                and ski.price <= budget_limit):
            state.recommended_skis.append(ski)

    # Give the user a message if there are no exact matches.
    if len(state.recommended_skis) == 0:
        state.message = (
            "No skis matched your answers. "
            "Try changing your terrain, skill level, or budget."
        )
    else:
        state.message = "These skis match your answers."

    return results_page(state)


@route
def results_page(state: State) -> Page:
    """
    Page that displays the ski recommendations.
    """
    content: list[Any] = [
        Header("Your Ski Recommendations"),
        state.message,
        "",
        "Skill level: " + state.skill_level,
        "Preferred terrain: " + state.preferred_terrain,
        "Budget: " + state.budget,
        ""
    ]

    # Display every ski in the recommendation list.
    if len(state.recommended_skis) == 0:
        content.append("There are no recommendations to display.")
    else:
        for ski in state.recommended_skis:
            content.append(Header(ski.name))
            content.append("Terrain: " + ski.terrain)
            content.append("Skill level: " + ski.skill_level)
            content.append("Sample price: $" + str(ski.price))
            content.append(ski.description)

            content.append(
                Button(
                    "View Details",
                    "ski_details_page",
                    {"ski_name": ski.name}
                )
            )

            content.append(
                Button(
                    "Add to Favorites",
                    "toggle_favorite",
                    {"ski_name": ski.name}
                )
            )
            content.append("")

    content.append(Button("Change My Answers", "questionnaire_page"))
    content.append(Button("View Favorites", "favorites_page"))
    content.append(Button("Back to Home", "index"))

    page = Page(state, content)

    return page


@route
def ski_details_page(state: State, ski_name: str) -> Page:
    """
    This page explains more in-depth details about the skis
    found for the user.
    """
    state.viewing_ski = ski_name

    content: list[Any] = [Header("Ski Details")]
    ski_found = False

    # Search the ski list for the selected ski.
    for ski in state.ski_options:
        if ski.name == ski_name:
            ski_found = True

            content.append(Header(ski.name))
            content.append("Terrain: " + ski.terrain)
            content.append("Skill level: " + ski.skill_level)
            content.append("Sample price: $" + str(ski.price))
            content.append("Description: " + ski.description)

            if ski.is_favorite:
                content.append("This ski is in your favorites.")
            else:
                content.append("This ski is not in your favorites.")

            content.append(
                Button(
                    "Add or Remove Favorite",
                    "toggle_favorite",
                    {"ski_name": ski.name}
                )
            )

    if ski_found == False:
        content.append("Sorry, that ski could not be found.")

    content.append(Button("Back to Recommendations", "results_page"))
    content.append(Button("Back to Home", "index"))

    page = Page(state, content)

    return page


@route
def toggle_favorite(state: State, ski_name: str) -> Page:
    """
    This route adds a ski to favorites or removes it.
    """
    for ski in state.ski_options:
        if ski.name == ski_name:

            if ski.is_favorite == False:
                ski.is_favorite = True
                state.favorite_skis.append(ski)
                state.message = ski.name + " was added to favorites."
            else:
                ski.is_favorite = False

                # Make a new list without the selected ski.
                remaining_favorites = []

                for favorite in state.favorite_skis:
                    if favorite.name != ski_name:
                        remaining_favorites.append(favorite)

                state.favorite_skis = remaining_favorites
                state.message = ski.name + " was removed from favorites."

    return results_page(state)


@route
def favorites_page(state: State) -> Page:
    """
    Page that displays the person's favorite skis.
    """
    content: list[Any] = [
        Header("My Favorite Skis"),
        state.message,
        ""
    ]

    if len(state.favorite_skis) == 0:
        content.append("You have not added any skis to your favorites yet.")
    else:
        # Display each ski in the favorites list.
        for ski in state.favorite_skis:
            content.append(Header(ski.name))
            content.append("Terrain: " + ski.terrain)
            content.append("Skill level: " + ski.skill_level)
            content.append("Sample price: $" + str(ski.price))

            content.append(
                Button(
                    "View Details",
                    "ski_details_page",
                    {"ski_name": ski.name}
                )
            )

            content.append(
                Button(
                    "Remove from Favorites",
                    "remove_favorite",
                    {"ski_name": ski.name}
                )
            )
            content.append("")

    content.append(Button("Back to Recommendations", "results_page"))
    content.append(Button("Back to Home", "index"))

    page = Page(state, content)

    return page


@route
def about_page(state: State) -> Page:
    """
    The about page explains the purpose of this website
    and its limitations.
    """
    page = Page(state, [
        Header("About Ski Finder"),
        "Ski Finder is designed to help beginners and other skiers "
        "understand what types of skis might fit their needs.",
        "",
        "The recommendations are based on skill level, preferred terrain, "
        "and budget.",
        "",
        "The prices are sample prices for this project. They are not "
        "live prices from ski stores.",
        "",
        "Height and weight are collected as part of the questionnaire, "
        "but this version does not calculate an exact ski length. "
        "I may include this in my finalized version.",
        "",
        Button("Back to Home", "index")
    ])

    return page


@route
def remove_favorite(state: State, ski_name: str) -> Page:
    """
    This function removes a ski that you favorited.
    """
    remaining_favorites = []

    for favorite in state.favorite_skis:
        if favorite.name != ski_name:
            remaining_favorites.append(favorite)

    state.favorite_skis = remaining_favorites

    for ski in state.ski_options:
        if ski.name == ski_name:
            ski.is_favorite = False

    state.message = ski_name + " was removed from favorites."

    return favorites_page(state)


@route
def reset_questionnaire(state: State) -> Page:
    """
    This route clears the questionnaire
    and recommendation information.
    """
    state.skill_level = "Beginner"
    state.preferred_terrain = "Groomed runs"
    state.height = ""
    state.weight = ""
    state.budget = "$300-$500"
    state.recommended_skis = []
    state.message = "Your answers have been reset."

    return questionnaire_page(state)


# Create the sample skis and the starting State.
starting_state = State(
    "Beginner",
    "Groomed runs",
    "",
    "",
    "$300-$500",
    [
        Ski(
            "Rossignol Experience 76",
            "Groomed runs",
            "Beginner",
            350,
            "A forgiving ski designed to help newer skiers learn "
            "and make turns on groomed trails.",
            False
        ),
        Ski(
            "Atomic Redster Q4",
            "Groomed runs",
            "Intermediate",
            450,
            "A frontside ski for skiers who enjoy making turns "
            "on prepared trails.",
            False
        ),
        Ski(
            "Salomon Stance 84",
            "All-mountain",
            "Intermediate",
            650,
            "An all-mountain ski for exploring different conditions "
            "around the resort.",
            False
        ),
        Ski(
            "Nordica Enforcer 94",
            "All-mountain",
            "Advanced",
            800,
            "A stronger all-mountain ski for experienced skiers "
            "who want stability at higher speeds.",
            False
        ),
        Ski(
            "K2 Mindbender 99Ti",
            "Powder",
            "Advanced",
            850,
            "A wider ski for experienced skiers who enjoy softer "
            "snow and off-trail conditions.",
            False
        ),
        Ski(
            "Salomon QST 92",
            "All-mountain",
            "Beginner",
            480,
            "A versatile ski that can help newer skiers explore "
            "more than just groomed trails.",
            False
        )
    ],
    [],
    [],
    "",
    ""
)


# Make a fresh State for each test.
def make_test_state() -> State:
    test_ski_options = []

    for ski in starting_state.ski_options:
        test_ski_options.append(
            Ski(
                ski.name,
                ski.terrain,
                ski.skill_level,
                ski.price,
                ski.description,
                False
            )
        )

    return State(
        "Beginner",
        "Groomed runs",
        "",
        "",
        "$300-$500",
        test_ski_options,
        [],
        [],
        "",
        ""
    )


# TESTS

# Test home page
test_state = make_test_state()
assert_equal(index(test_state).content[0], Header("Welcome to Ski Finder!"))

# Test questionnaire page
test_state = make_test_state()
assert_equal(
    questionnaire_page(test_state).content[0],
    Header("Ski Finder Questionnaire")
)

# Test submitting beginner preferences
test_state = make_test_state()
submit_preferences(
    test_state,
    "Beginner",
    "Groomed runs",
    "66",
    "150",
    "$300-$500"
)
assert_equal(test_state.skill_level, "Beginner")
assert_equal(test_state.preferred_terrain, "Groomed runs")
assert_equal(test_state.height, "66")
assert_equal(test_state.weight, "150")
assert_equal(len(test_state.recommended_skis), 1)
assert_equal(
    test_state.recommended_skis[0].name,
    "Rossignol Experience 76"
)

# Test submitting preferences with no matching skis
test_state = make_test_state()
submit_preferences(
    test_state,
    "Beginner",
    "Powder",
    "66",
    "150",
    "$300-$500"
)
assert_equal(len(test_state.recommended_skis), 0)

# Test results page
test_state = make_test_state()
test_state.recommended_skis.append(test_state.ski_options[0])
assert_equal(
    results_page(test_state).content[0],
    Header("Your Ski Recommendations")
)

# Test ski details page
test_state = make_test_state()
ski_details_page(test_state, "Rossignol Experience 76")
assert_equal(test_state.viewing_ski, "Rossignol Experience 76")

# Test adding a favorite
test_state = make_test_state()
toggle_favorite(test_state, "Rossignol Experience 76")
assert_equal(test_state.ski_options[0].is_favorite, True)
assert_equal(len(test_state.favorite_skis), 1)
assert_equal(
    test_state.favorite_skis[0].name,
    "Rossignol Experience 76"
)

# Test removing a favorite by toggling it again
test_state = make_test_state()
toggle_favorite(test_state, "Rossignol Experience 76")
toggle_favorite(test_state, "Rossignol Experience 76")
assert_equal(test_state.ski_options[0].is_favorite, False)
assert_equal(len(test_state.favorite_skis), 0)

# Test favorites page
test_state = make_test_state()
test_state.favorite_skis.append(test_state.ski_options[0])
test_state.ski_options[0].is_favorite = True
assert_equal(
    favorites_page(test_state).content[0],
    Header("My Favorite Skis")
)

# Test removing a favorite
test_state = make_test_state()
test_state.favorite_skis.append(test_state.ski_options[0])
test_state.ski_options[0].is_favorite = True
remove_favorite(test_state, "Rossignol Experience 76")
assert_equal(len(test_state.favorite_skis), 0)
assert_equal(test_state.ski_options[0].is_favorite, False)

# Test about page
test_state = make_test_state()
assert_equal(
    about_page(test_state).content[0],
    Header("About Ski Finder")
)

# Test resetting questionnaire
test_state = make_test_state()
test_state.skill_level = "Advanced"
test_state.preferred_terrain = "Powder"
test_state.height = "70"
test_state.weight = "180"
test_state.budget = "$800+"
test_state.recommended_skis.append(test_state.ski_options[0])

reset_questionnaire(test_state)

assert_equal(test_state.skill_level, "Beginner")
assert_equal(test_state.preferred_terrain, "Groomed runs")
assert_equal(test_state.height, "")
assert_equal(test_state.weight, "")
assert_equal(test_state.budget, "$300-$500")
assert_equal(len(test_state.recommended_skis), 0)


# Start the website.
start_server(starting_state)

