# Author: Greg Champagne
# Program: Pokemon Best Defense Type Calculator
# Version 11-16-22 - v0.2

"""
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


def main():
    base_types = create_base_types()
    dual_types = create_dual_types(base_types)
    dual_types = purge_impossible_types(dual_types)
    dual_types = correct_dual_types(dual_types)
    all_types = dual_types + base_types
    # count_types(dual_types)
    # raw_counter(all_types)
    # grid_view(all_types)
    # overview(all_types)
    raw_differential_view(all_types)


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
    count = 1
    for i in dual_types:
        print(str(count) + " " + i.name + " " + str(i.weak) + " /2w " + str(i.double_weak) + " /r" + str(i.resist) +
              " /2r " + str(i.double_resist) + " /i " + str(i.immune))
        count += 1


# Returns a basic score for each type combo with a score of:
# Resistance + (1.4 * Doubly Resistant) + (1.5 * Immunity) - Weakness - (1.8 * Doubly Weak)
def raw_counter(types):
    for i in range(0, len(types)):
        types[i].score = len(types[i].resist) + (1.2 * len(types[i].double_resist)) + (1.5 * len(types[i].immune))\
                         - len(types[i].weak) - (1.2 * len(types[i].double_weak))

    types.sort(key=lambda x: x.score, reverse=True)
    count = 1
    for i in range(0, len(types)):
        print(str(count) + " " + types[i].name + " " + str(round(types[i].score, 1)))
        count += 1


# Will show all of the data in helpful grid form, where each type specifically is represented
def grid_view(types):
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~ Normal - Fire - Water - Grass - Electric - Ice - Fighting - Poison - Ground - "
          "Flying - Psychic - Bug - Rock - Ghost - Dragon - Dark - Steel - Fairy")
    print("                             1       1       1       1        1        1       1         1        1        "
          "1         1       1     1       1       1       1       1       1")
    # 0 = immune


# Shows an informative overview of the data, that just shows raw weak / resist / immune totals
def overview(types):
    for i in range(0, len(types)):
        types[i].total_resist = len(types[i].resist) + len(types[i].double_resist)
        types[i].total_weak = len(types[i].weak) + len(types[i].double_weak)

    types.sort(key=lambda x: (x.total_weak, -x.total_resist, -len(x.immune)))
    count = 1
    for i in range(0, len(types)):
        print(str(count) + " " + types[i].name + " W:" + str(types[i].total_weak) +
              " R:" + str(types[i].total_resist) + " I:" + str(len(types[i].immune)))
        count += 1


# Basically just overview but with differential included and as the main factor of sorting
def raw_differential_view(types):
    for i in range(0, len(types)):
        types[i].total_resist = len(types[i].resist) + len(types[i].double_resist)
        types[i].total_weak = len(types[i].weak) + len(types[i].double_weak)
        types[i].differential = types[i].total_resist + len(types[i].immune) - types[i].total_weak

    types.sort(key=lambda x: (-x.differential, x.total_weak, -x.total_resist, -len(x.immune)))
    count = 1
    for i in range(0, len(types)):
        print(str(count) + " " + types[i].name + " D:" + str(types[i].differential) + " W:" + str(types[i].total_weak) +
              " R:" + str(types[i].total_resist) + " I:" + str(len(types[i].immune)))
        count += 1


# Possibly will edit this at some point, but I believe this to be the new correct impossible list given gen 9 pokemon
# https://bulbapedia.bulbagarden.net/wiki/List_of_type_combinations_by_abundance link to site of info
def purge_impossible_types(types):
    impossible = ["Normal/Rock", "Normal/Bug", "Normal/Steel", "Normal/Ice", "Fighting/Fairy",
                  "Ice/Poison", "Ground/Fairy", "Rock/Ghost", "Bug/Dragon", "Fire/Fairy"]

    good_types = []
    for i in range(0, len(types)):
        good = True
        for ii in range(0, len(impossible)):
            if types[i].name == impossible[ii]:
                good = False
        if good:
            good_types.append(types[i])

    return good_types

main()
