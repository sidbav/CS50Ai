import sys

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        for var in self.crossword.variables:
            for word in self.crossword.words:
                if len(word) != var.length:
                    self.domains[var].remove(word)


    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        if x == y:
            return False

        pair = self.crossword.overlaps[x, y]
        if pair == None:
            return False
        else:
            # ith character of x, jth character of y
            i, j = pair
            revised = False
            remove = []
            for wordx in self.domains[x]:
                satisfy = False
                for wordy in self.domains[y]:
                    if wordx[i] == wordy[j]:
                        satisfy= True

                if satisfy == False:
                    revised = True
                    remove.append(wordx)

            for word in remove:
                self.domains[x].remove(word)

            return revised


    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        if arcs == None:
            arcs = list(self.crossword.overlaps.keys())

        while len(arcs) != 0:
            x, y = arcs.pop(0)
            if self.revise(x, y):
                if len(self.domains[x]) == 0:
                    return False
                else:
                    for v in self.crossword.variables:
                        if v == y or v == x:
                            continue
                        else:
                            arcs.append((v, x))
        return True


    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        for value in assignment.values():
            if value == None or len(value) == 0:
                return False
        return True


    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        # First check that all values have strings that match the length of the
        # variable
        for key in assignment.keys():
            if assignment[key] != None:
                if len(assignment[key]) != key.length:
                    return False

        # Check that a word has not been used twice
        words_set = set()
        for value in assignment.values():
            if value != None:
                if value in words_set:
                    return False
                else:
                    words_set.add(value)

        # Check that all overlaps have been respected
        for key, value in self.crossword.overlaps.items():
            if value != None:
                x, y = key
                i, j = value
                if assignment[x] != None and assignment[y] != None:
                    if assignment[x][i] != assignment[y][j]:
                        return False

        return True


    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        # For now just return the possible values, and then we can implement the
        # funtion to return the ordered value
        return self.domains[var]


    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        # First lets just check to see how many elements still need to assigned
        variables = []
        for var in assignment.keys():
            if assignment[var] == None:
                variables.append(var)

        if len(variables) == 1:
            return variables[0]

        # If there is more than one element that needs to assigned, check which
        # element has the smallest domain
        smallest = 100000000
        smallest_list = []
        for var in variables:
            length = len(self.domains[var])
            if length < smallest:
                smallest = length
                smallest_list = []
                smallest_list.append(var)
            elif length == smallest:
                smallest_list.append(var)

        if len(smallest_list) == 1:
            return smallest_list[0]

        # If there are elements remaining which each have the same size domain,
        # lets pick the one with the highest degree
        degree = -100000
        res = None
        for var in smallest_list:
            count = 0
            for x in self.crossword.variables:
                if var == x:
                    continue
                if self.crossword.overlaps[(var, x)] != None:
                    count += 1
            if count > degree:
                degree = count
                res = var

        return res


    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if len(assignment) == 0:
            for var in self.crossword.variables:
                assignment[var] = None

        if self.assignment_complete(assignment):
            return assignment

        var = self.select_unassigned_variable(assignment)
        for value in self.order_domain_values(var, assignment):
            assignment[var] = value
            if self.consistent(assignment):
                res = self.backtrack(assignment)
                if res != None:
                    return res
            assignment[var] = None

        return None


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
