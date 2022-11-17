# Author: Greg Champagne
# Program: Pokemon Best Defense Type Calculator
# Version 11-16-22 - v0.3

import random

""" THERE ARE 15,849,819,498,240 POSSIBLE TEAMS, WE SHALL FIND THE BEST ONE
HOW DO I WANT THE MATH TO WORK
1 - SOLO POKEMON GRADER
    A: Count a 4x weakness as more than a 2x Weakness but less than 2 different weaknesses
    B: Count a 4x resist as nearly as good as an immunity
    C: Exponential growth in point deduction for every additional weakness
2 - TEAM CREATOR
    A: Minimize Weaknesses
    B: Hugely Penalize Repeat Weaknesses
    C: Factor in what % of resistance to everything is achieved
    D: Just raw Resistance - Weakness differential
    E: Exponential growth in point addition for every additional immunity
"""
"""
THINGS TO ADD:
2. Ability to input a team more easily, better display of information while creating a team as well
4. Potentially differentiate between resists and immunities? Not a huge deal though
5. A version where you can input part of a team and have it sim the rest
6. A version where you only select from the top x poketypes, or just only the positive diff ones
7. A version of the random generator where it doesn't allow for exact repeat typing
    - Possibly also a version that doesn't allow for any repeat subtypes at all? Might be bad though
8. The ability to remove types from the running
"""
"""
INTERESTING MATH TIDBITS
There are 15,849,819,498,240 possible teams using any pokemon type
There are 4,293,656,640,000  possible teams when you remove all types with negative differential
There are 1,029,485,041,200  possible teams when you remove all types besides 1+ differentials
"""
"""
SURPRISING OBSERVATIONS
A: Water/Flying as a combo type / individually appear in most teams, often more than once
"""

# Small dict to change the strings of the types into easy to work with numbers
type_dict = dict({
    "Normal": 0,
    "Fire": 1,
    "Water": 2,
    "Grass": 3,
    "Electric": 4,
    "Ice": 5,
    "Fighting": 6,
    "Poison": 7,
    "Ground": 8,
    "Flying": 9,
    "Psychic": 10,
    "Bug": 11,
    "Rock": 12,
    "Ghost": 13,
    "Dragon": 14,
    "Dark": 15,
    "Steel": 16,
    "Fairy": 17
})


def main():
    base_types = create_base_types()
    dual_types = create_dual_types(base_types)
    dual_types = purge_types(dual_types, False, False, False)
    dual_types = correct_dual_types(dual_types)
    all_types = sort_poke_types(dual_types + base_types)
    even_plus_types = top_poketype_cutoff(all_types, 130)
    one_plus_types = top_poketype_cutoff(all_types, 103)
    # count_types(dual_types)
    # grid_view(all_types)
    # raw_differential_view(best_types)
    # team_test(all_types)
    # find_best_random(even_plus_types, 10000, 20)
    find_random_threshold(even_plus_types, 3100, 3)


# Class that handles the data for a specific type or dual type
class PokeType:
    def __init__(self, name, weak, resist, immune):
        self.name = name
        self.weak = weak
        self.resist = resist
        self.immune = immune
        self.double_weak = []
        self.double_resist = []
        self.total_weak = 0
        self.total_resist = 0
        self.differential = 0
        self.score = 0


# Class that handles a collection of PokeType's into a combined format
class Team:
    def __init__(self):
        self.names = []  # Name of every type
        self.weak = [0] * 18  # Amount of each weakness
        self.resist = [0] * 18  # Amount of each resist
        self.immune = [0] * 18  # Amount of each immune
        self.double_weak = [0] * 18  # Amount of each double_weak
        self.double_resist = [0] * 18  # Amount of each double_resist
        self.counters = [0] * 18  # Keeps track of which types this team counters
        self.weak_to = []  # The names of what it is weak to
        self.resistant_to = []  # The names of what it is resistant to
        self.total_weak = 0  # Total number of weaknesses (includes double)
        self.total_resist = 0  # Total number of resistances (includes double and immunities)
        self.total_immune = 0  # Total number of immunities
        self.total_dr = 0  # Total number of double resists
        self.total_dw = 0  # Total number of double weaknesses
        self.differential = 0  # Total weak - total resist
        self.resisted = 0  # Number of unique resists
        self.not_weak = 0  # Number of types the team is not weak to
        self.countered = 0  # Number of types that the team is not weak to AND has resisted
        self.weak_diversity = 0  # Score of how diverse what your team is weak to is, higher = worse
        self.resist_diversity = 0  # Score of how diverse what your team is resistant is, higher = better
        self.type_delta = [0] * 18  # List of types with total_resist - total_weak
        self.coverage = 0  # Total number of - type_delta elements, higher = worse
        self.coverage_types = []  # List of all of the types that the team is coverage to
        self.score = 0  # Score of the team as determined by one of the score methods

    """
    SCORING ALGORITHM SECTION
        - IMPORTANT SCORING DATA:
            - AvgD - 1.74 AvgW - 3.78 AvgR - 4.69 AvgI - 0.83 (STAT AVERAGES)
            - TAD - 10.44 TAW - 22.68 TAR - 28.14 TAI - 4.98  (STAT AVERAGES * 6)
    """

    # Attempt one at a scoring algorithm, with set weights, and linear score changes
    # Ideally the next version will have exponential based math, but wanted to test a basic version first
    def first_score(self):
        # Sets score at 1500, the base for most ELO systems
        self.score = 1500
        # Adds a 15 score increase for every resist the team has more than average expected (~28)
        if self.total_resist >= 28:
            self.score += (15 * (self.total_resist - 28))
        # Adds 5 points for every double resist for those being slightly better than normal resists
        self.score += (5 * self.total_dr)
        # Adds 10 points for every immunity to reward those being better than double and normal resists
        self.score += (10 * self.total_immune)
        # Removes 15 score for every weakness more than average expected (~23)
        self.score -= (15 * (self.total_weak - 23))
        # Removes an additional 5 points for every double weak
        self.score -= (5 * self.total_dw)
        # Adds 10 per point higher the differential is than average (~10)
        self.score += (10 * (self.differential - 10))
        # Adds 5 per each resisted
        self.score += (5 * self.resisted)
        # Adds 20 for every resisted more than 66% resisted
        self.score += (20 * (self.resisted - 12))
        # Adds 100 if all are resisted
        if self.resisted == 18:
            self.score += 100
        # Adds 15 per each non weak
        self.score += (15 * self.not_weak)
        # Adds 25 per each non weak more than or equal to 33%, but doesn't subtract if less than average
        if self.not_weak >= 6:
            self.score += (25 * (self.not_weak - 6))
        # Adds 15 per each countered type
        self.score += (15 * self.countered)
        # Adds 2 * ResDiversity to the score
        self.score += (2 * self.resist_diversity)
        # Subtract 4 times the WeakDiversity from the score
        self.score -= (4 * self.weak_diversity)
        # Subtract 50 times the coverage score cubed
        self.score += (50 * (self.coverage * self.coverage * self.coverage))
        # If perfect coverage, add 300
        if self.coverage == 0:
            self.score += 300

    # Scoring algorithm where the user can set their own weights
    def custom_score(self, weights):
        self.score = 0

    """
    OTHER TEAM METHODS
        set_stats
        add_to_team
        print_team
    """

    # Sets the stats for the non implicit stats
    def set_stats(self):
        # Sets the differential for a team
        self.differential = self.total_resist - self.total_weak
        # Sets the resisted / not_weak / countered for a team
        self.resisted = 0
        self.not_weak = 0
        self.countered = 0
        all_resist = [0] * 18
        all_weak = [0] * 18
        # Compile resist / double resist / immune into one pile
        # Does the same for the weak / double weak
        # Then checks if that type is countered or not, and if it is adds it to the counters / countered
        for i in range(0, len(self.resist)):
            all_resist[i] += (self.resist[i] + self.double_resist[i] + self.immune[i])
            all_weak[i] += (self.weak[i] + self.double_weak[i])
            if all_resist[i] > 0 and all_weak[i] == 0:
                self.countered += 1
                self.counters[i] = 1
        # Count up all of the unique times the team is not weak to a type and,
        # Count the diversity of what a team is weak to - i.e. it is bad to have multiple weak to the same type,
        # So this will be punished by squaring the amount that the team is weak to of every type, and summing all types
        for i in all_weak:
            self.weak_diversity += (i * i * i)
            if i == 0:
                self.not_weak += 1
        # Count up all the non zeroes as a type getting resisted
        # Same for resist diversity as for weak diversity, except the opposite being true for evaluations
        # In theory, every member of the team being resistant to a type would make that type obsolete
        for i in all_resist:
            self.resist_diversity += (i * i)
            if i != 0:
                self.resisted += 1
        # Takes the total all_resist - total all_weak for each type to gather which types are more weak than resisted
        for i in range(0, len(all_resist)):
            self.type_delta[i] = all_resist[i] - all_weak[i]
            if self.type_delta[i] < 0:
                self.coverage += self.type_delta[i]
                self.coverage_types.append(i)

    # Adds a PokeType to the team, currently lumps in immune with resistant_to
    # Uses the type_dict to convert the types into their positions in the type chart
    def add_to_team(self, the_type):
        self.names.append(the_type.name)
        for i in range(0, len(the_type.weak)):
            self.weak[type_dict.get(the_type.weak[i])] += 1
            # self.weak_to.append(the_type.weak[i])
            self.total_weak += 1
        for i in range(0, len(the_type.resist)):
            self.resist[type_dict.get(the_type.resist[i])] += 1
            # self.resistant_to.append(the_type.resist[i])
            self.total_resist += 1
        for i in range(0, len(the_type.double_weak)):
            self.double_weak[type_dict.get(the_type.double_weak[i])] += 1
            self.total_dw += 1
            # self.weak_to.append(the_type.double_weak[i])
            self.total_weak += 1
        for i in range(0, len(the_type.double_resist)):
            self.double_resist[type_dict.get(the_type.double_resist[i])] += 1
            # self.resistant_to.append(the_type.double_resist[i])
            self.total_resist += 1
            self.total_dr += 1
        for i in range(0, len(the_type.immune)):
            self.immune[type_dict.get(the_type.immune[i])] += 1
            self.total_immune += 1
            # self.resistant_to.append(the_type.immune[i])
            # self.immune_to.append(the_type.immune[i]) - If counting immune separately from resist
            self.total_resist += 1
        # If this is the last team, set the stats and then the score
        if len(self.names) == 6:
            self.set_stats()
            # This score method should be variable in the future
            self.first_score()

    # Method for printing out information of each team to the console, factors in a number for sorted lists
    def print_team(self, number):
        print(str(number) + " " + str(self.names))
        print(self.type_delta)
        print("Resisted: " + str(self.resisted) + "/18  Resists: " + str(self.total_resist))
        print("Non Weak: " + str(self.not_weak) + "/18  Weaknesses: " + str(self.total_weak))
        print("Counters: " + str(self.countered) + "/18   Differential: " + str(self.differential))
        print("ResDiversity: " + str(self.resist_diversity) + " WeakDiversity: " + str(self.weak_diversity))
        print("Coverage: " + str(self.coverage) + "  TEAM ELO SCORE: " + str(self.score))

"""
GENERAL METHODS
"""


# Sort all of the pokemon types by "best" to "worst"
def sort_poke_types(types):
    # Sort the list by differential, then weaks, then resists, then immunities
    for i in range(0, len(types)):
        types[i].total_resist = len(types[i].resist) + len(types[i].double_resist)
        types[i].total_weak = len(types[i].weak) + len(types[i].double_weak)
        types[i].differential = types[i].total_resist + len(types[i].immune) - types[i].total_weak
    types.sort(key=lambda x: (-x.differential, x.total_weak, -x.total_resist, -len(x.immune)))
    return types


# Simply randomly picks 6 possible pokemon and creates a team of them
def create_random_team(types):
    temp_team = Team()
    for i in range(0, 6):
        temp_team.add_to_team(types[random.randint(0, len(types) - 1)])

    return temp_team


# Creates x random teams, and sorts them based on elo score. Presents the top y
def find_best_random(types, x, y):
    teams = []
    for i in range(0, x):
        teams.append(create_random_team(types))

    teams.sort(key=lambda z: -z.score)
    for i in range(0, y):
        teams[i].print_team(i + 1)


# Loops until it finds a team with a score of or above x, y number of times
def find_random_threshold(types, x, y):
    found = False
    teams = []
    counter = 0
    attempts = 0
    while not found:
        attempts += 1
        temp_team = create_random_team(types)
        if temp_team.score >= x:
            counter += 1
            teams.append(temp_team)
            print("Found team " + str(counter) + " at attempt: " + str(attempts))
            if counter == y:
                found = True

    print("\nIt took " + str(attempts) + " attempts to find these!\n")
    teams.sort(key=lambda z: -z.score)
    for i in range(0, y):
        teams[i].print_team(i + 1)


# Tests out the team feature by adding 6 pokemon to a team and seeing how it displays
def team_test(types):
    new_team = Team()
    new_team.add_to_team(types[37])
    new_team.add_to_team(types[0])
    new_team.add_to_team(types[104])
    new_team.add_to_team(types[33])
    new_team.add_to_team(types[23])
    new_team.add_to_team(types[20])
    new_team.print_team(0)
    """ OLD PRINT STATEMENT BEFORE PRINT_TEAM
    print(new_team.weak)
    print(new_team.resist)
    print(new_team.immune)
    print(new_team.double_resist)
    print(new_team.double_weak)
    """


# Manually Enters in all of the type data for each type, and returns the array of each base type
def create_base_types():
    types = [PokeType("Normal", ["Fighting"], [], ["Ghost"]),
             PokeType("Fire", ["Water", "Ground", "Rock"], ["Fire", "Grass", "Ice", "Bug", "Steel", "Fairy"], []),
             PokeType("Water", ["Electric", "Grass"], ["Fire", "Water", "Ice", "Steel"], []),
             PokeType("Grass", ["Fire", "Ice", "Poison", "Flying", "Bug"],
                      ["Water", "Electric", "Grass", "Ground"], []),
             PokeType("Electric", ["Ground"], ["Electric", "Flying", "Steel"], []),
             PokeType("Ice", ["Fire", "Rock", "Steel", "Fighting"], ["Ice"], []),
             PokeType("Fighting", ["Flying", "Psychic", "Fairy"], ["Bug", "Rock", "Dark"], []),
             PokeType("Poison", ["Ground", "Psychic"], ["Grass", "Fighting", "Poison", "Bug", "Fairy"], []),
             PokeType("Ground", ["Water", "Grass", "Ice"], ["Poison", "Rock"], ["Electric"]),
             PokeType("Flying", ["Electric", "Ice", "Rock"], ["Grass", "Fighting", "Ground", "Bug"], ["Ground"]),
             PokeType("Psychic", ["Bug", "Ghost", "Dark"], ["Fighting", "Psychic"], []),
             PokeType("Bug", ["Fire", "Flying", "Rock"], ["Grass", "Fighting", "Ground"], []),
             PokeType("Rock", ["Water", "Grass", "Fighting", "Ground", "Steel"],
                      ["Normal", "Flying", "Poison", "Fire"], []),
             PokeType("Ghost", ["Ghost", "Dark"], ["Poison", "Bug"], ["Normal", "Fighting"]),
             PokeType("Dragon", ["Ice", "Dragon", "Fairy"], ["Fire", "Water", "Grass", "Electric"], []),
             PokeType("Dark", ["Fighting", "Bug", "Fairy"], ["Ghost", "Dark"], ["Psychic"]),
             PokeType("Steel", ["Fire", "Fighting", "Ground"],
                      ["Normal", "Grass", "Ice", "Flying", "Psychic", "Bug", "Rock", "Dragon", "Steel", "Fairy"],
                      ["Poison"]),
             PokeType("Fairy", ["Poison", "Steel"], ["Fighting", "Bug", "Dark"], ["Dragon"])]

    return types


# Combines every base type with every other base type to create the full list of dual types
def create_dual_types(types):
    dual_types = []
    for i in range(0, len(types) - 1):
        for ii in range(i+1, len(types)):
            name = types[i].name + "/" + types[ii].name
            weak = types[i].weak + types[ii].weak
            resist = types[i].resist + types[ii].resist
            immune = types[i].immune + types[ii].immune
            dual_types.append(PokeType(name, weak, resist, immune))

    return dual_types


# Removes repeats and tabulates 4x, 1/4, and replaces resists with immunity
def correct_dual_types(dual):
    corrected = []
    # For every dual type
    for i in range(0, len(dual)):
        # For each element in immune remove repeats
        for ii in range(0, len(dual[i].immune) - 1):
            for iii in range(ii + 1, len(dual[i].immune)):
                if dual[i].immune[ii] == dual[i].immune[iii] and dual[i].immune[ii] != "Null":
                    dual[i].immune[ii] = "Null"
        # For each element in weak besides the last, remove repeats
        for ii in range(0, len(dual[i].weak) - 1):
            # Compare to the elements after it, if the same, 4x weakness and null both
            for iii in range(ii + 1, len(dual[i].weak)):
                if dual[i].weak[ii] == dual[i].weak[iii] and dual[i].weak[ii] != "Null":
                    dual[i].double_weak.append(dual[i].weak[ii])
                    dual[i].weak[ii] = "Null"
                    dual[i].weak[iii] = "Null"
        # For each resist, do the same as the weak for loop
        for ii in range(0, len(dual[i].resist) - 1):
            for iii in range(ii + 1, len(dual[i].resist)):
                if dual[i].resist[ii] == dual[i].resist[iii] and dual[i].resist[ii] != "Null":
                    dual[i].double_resist.append(dual[i].resist[ii])
                    dual[i].resist[ii] = "Null"
                    dual[i].resist[iii] = "Null"
        # Now, for each resist, check it against weak to see if there's any that need to be null as well
        for ii in range(0, len(dual[i].resist)):
            for iii in range(0, len(dual[i].weak)):
                if dual[i].resist[ii] == dual[i].weak[iii] and dual[i].resist[ii] != "Null":
                    dual[i].resist[ii] = "Null"
                    dual[i].weak[iii] = "Null"
        # For all elements in immune, check against all in resist / weak to convert them to just immune
        for ii in range(0, len(dual[i].immune)):
            for iii in range(ii, len(dual[i].resist)):
                if ii < len(dual[i].immune) and iii < len(dual[i].resist):
                    if dual[i].immune[ii] == dual[i].resist[iii]:
                        dual[i].resist[iii] = "Null"
            for iii in range(ii, len(dual[i].weak)):
                if ii < len(dual[i].immune) and iii < len(dual[i].weak):
                    if dual[i].immune[ii] == dual[i].weak[iii]:
                        dual[i].weak[iii] = "Null"
        # Now that everything is fixed, create new arrays without bringing over the null elements
        resists = []
        weaks = []
        for ii in dual[i].resist:
            if ii != "Null":
                resists.append(ii)
        for ii in dual[i].weak:
            if ii != "Null":
                weaks.append(ii)
        dual[i].resist = resists
        dual[i].weak = weaks

        # Append the fixed dual type to the new array, and return that array when done
        corrected.append(dual[i])

    return corrected


# Returns the list of types, helpful for information checking and making sure things work lol
def count_types(dual_types):
    count = 0
    for i in dual_types:
        print(str(count) + " " + i.name + " " + str(i.weak) + " /2w " + str(i.double_weak) + " /r" + str(i.resist) +
              " /2r " + str(i.double_resist) + " /i " + str(i.immune))
        count += 1


# Will show all of the data in helpful grid form, where each type specifically is represented
def grid_view(types):
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~ Normal - Fire - Water - Grass - Electric - Ice - Fighting - Poison - Ground - "
          "Flying - Psychic - Bug - Rock - Ghost - Dragon - Dark - Steel - Fairy")
    print("                             1       1       1       1        1        1       1         1        1        "
          "1         1       1     1       1       1       1       1       1")
    # 0 = immune


# Basically just overview but with differential included and as the main factor of sorting
# Also added in a small sub method to calculate averages of each element for proper elo math
def raw_differential_view(types):
    # Calculate totals / differentials for each specific type, as well as sum their values
    resist_sum = 0
    weak_sum = 0
    diff_sum = 0
    imm_sum = 0
    for i in range(0, len(types)):
        resist_sum += types[i].total_resist
        weak_sum += types[i].total_weak
        diff_sum += types[i].differential
        imm_sum += len(types[i].immune)
    # Calculate the averages of all 3 values
    avg_resist = resist_sum / len(types)
    avg_weak = weak_sum / len(types)
    avg_diff = diff_sum / len(types)
    avg_imm = imm_sum / len(types)
    count = 0
    for i in range(0, len(types)):
        print(str(count) + " " + types[i].name + " D:" + str(types[i].differential) + " W:" + str(types[i].total_weak) +
              " R:" + str(types[i].total_resist) + " I:" + str(len(types[i].immune)))
        count += 1
    # Print out the calculated averages
    print("Avg D: " + str(round(avg_diff, 2)) + " Avg W: " + str(round(avg_weak, 2)) +
          " Avg R: " + str(round(avg_resist, 2)) + " Avg I: " + str(round(avg_imm, 2)))
    # RESULTS FOR GOOD MEASURE: AD - 1.74 AW - 3.78 AR - 4.69 AI - 0.83


# Possibly will edit this at some point, but I believe this to be the new correct impossible list given gen 9 pokemon
# https://bulbapedia.bulbagarden.net/wiki/List_of_type_combinations_by_abundance link to site of info
def purge_types(types, mega, personal, nine):
    # Types that don't exist now or in Gen 9 from what I know now
    impossible = ["Normal/Rock", "Normal/Bug", "Normal/Steel", "Normal/Ice", "Fighting/Fairy",
                  "Ice/Poison", "Ground/Fairy", "Rock/Ghost", "Bug/Dragon", "Fire/Fairy"]

    # Types that only exist as mega types, which don't exist at in Gen 9
    # If mega is False, they will not be included
    mega_types = ["Dragon/Fairy"]

    # Types that I'm now choosing to exclude because not in Gen 9 from my knowledge, and extremely limited if so
    not_in_gen_nine = ["Normal/Electric", "Water/Steel", "Grass/Steel", "Poison/Fairy", "Ground/Steel",
                       "Water/Dragon", "Electric/Dragon", "Psychic/Dragon", "Fire/Dragon", "Psychic/Dark",
                       "Water/Grass"]

    # I just personally don't want to include these, change this to true if you want any of these
    # If personal is false, they will not be included
    # REASONS FOR EACH: 1 - Dedenne nah 2 - Only through poke home for gen 9 3 - Only Oricorio / Legendary
    #                   4 - Zoruark pokehome only 5
    personally_against = ["Electric/Fairy", "Dragon/Steel", "Electric/Flying", "Normal/Ghost"]

    good_types = []
    for i in range(0, len(types)):
        good = True
        for ii in range(0, len(impossible)):
            if types[i].name == impossible[ii]:
                good = False
            if ii < len(mega_types):
                if types[i].name == mega_types[ii] and not mega:
                    good = False
            if ii < len(personally_against):
                if types[i].name == personally_against[ii] and not personal:
                    good = False
            if ii < len(not_in_gen_nine):
                if types[i].name == not_in_gen_nine[ii] and not nine:
                    good = False
        if good:
            good_types.append(types[i])

    return good_types


# Removes any pokemon past the cutoff number x from the list of pokemon types
# Is a way to reduce the amount of random guessing the machine will have to do to find good teams
def top_poketype_cutoff(types, x):
    best_types = []
    for i in range(0, x):
        best_types.append(types[i])

    return best_types

main()
