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
        for var in self.crossword.variables:
            doms=self.domains[var].copy()
            for x in doms:
                if len(x)!=var.length:
                    self.domains[var].remove(x)

        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        #raise NotImplementedError

    def revise(self, x, y):
        if self.crossword.overlaps[x,y]!=None:
            doms_x=self.domains[x].copy()    
            for valx in doms_x:
                revised=False
                consistent=False
                for valy in self.domains[y]:
                #if self.crossword.overlaps[valx,valy]!=None:
                    i=self.crossword.overlaps[x,y][0]
                    j=self.crossword.overlaps[x,y][1]
                    if valx[i]==valy[j]:
                        consistent=True
                if consistent==False:
                    self.domains[x].remove(valx)
                    revised=True
        return revised


        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        raise NotImplementedError

    def ac3(self, arcs=None):
        if arcs==None:
            possible_arcs=[]
            for var in self.crossword.variables:
                for neighbour in self.crossword.neighbors(var):
                    possible_arcs.append((var,neighbour))
        else:
            possible_arcs=arcs
        while len(possible_arcs)!=0:
            arc=possible_arcs.pop(0)
            if self.revise(arc[0],arc[1]):
                if len(self.domains[arc[0]])==0:
                    return False
                else:
                    for z in self.crossword.neighbors(arc[0])-{arc[1]}:
                        possible_arcs.append((z,arc[0]))
        return True


        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        raise NotImplementedError

    def assignment_complete(self, assignment):
        return len(assignment)==len(self.crossword.variables)
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        raise NotImplementedError

    def consistent(self, assignment):
        distinct=True
        for v1 in assignment.keys():
            for v2 in assignment.keys():
                if v1!=v2 and assignment[v1]==assignment[v2]:
                    distinct=False
        node_consistent=True
        for var in assignment.keys():
            if var.length==len(assignment[var]):
                node_consistent=True
            else:
                node_consistent=False
        arc_consistent=True
        for var1 in assignment:
            for var2 in assignment:
                if var1!=var2 and self.crossword.overlaps[var1,var2]!=None:
                    i=self.crossword.overlaps[var1,var2][0]
                    j=self.crossword.overlaps[var1,var2][1]
                    #print(i,j)
                    if assignment[var1][i]!=assignment[var2][j]:
                        arc_consistent=False
        return (node_consistent and arc_consistent and distinct)

        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        raise NotImplementedError

    def order_domain_values(self, var, assignment):
        domain_var=self.domains[var].copy()
        neighbors=self.crossword.neighbors(var)
        for key in assignment.keys():
            if key in neighbors:
                neighbors.remove(key)
        values_elim=[]
        for word in domain_var:
            assignment[var]=word
            if self.consistent(assignment):
                num_removed=0
                for n in neighbors:
                    dom_n=self.domains[n].copy()
                    i=self.crossword.overlaps[var,n][0]
                    j=self.crossword.overlaps[var,n][1]
                    for val in dom_n:
                        if word[i]!=val[j]:
                            num_removed+=1
                values_elim.append((word,num_removed))
        final=sorted(values_elim,key=lambda tup:tup[1])
        ordered_values=[i[0] for i in final]
        return ordered_values
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        raise NotImplementedError

    def select_unassigned_variable(self, assignment):
        variables=self.crossword.variables
        vars_assigned=set(assignment.keys())
        unassigned_vars=variables-vars_assigned
        l=[]
        lens=[]
        for var in unassigned_vars:
            l.append((len(self.domains[var]),var))
            lens.append(len(self.domains[var]))
        min_removed_values=min(lens)
        new_list=[]
        for i in l:
            if i[0]==min_removed_values:
                new_list.append((len(self.crossword.neighbors(i[1])),var))
        final=sorted(new_list,key=lambda tup:tup[0])
        return final[0][1]
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        raise NotImplementedError

    def backtrack(self, assignment):
        if self.assignment_complete(assignment) and self.consistent(assignment):
            return assignment
        else:
            var=self.select_unassigned_variable(assignment)
            for val in self.domains[var]:
                assignment[var]=val
                if self.consistent(assignment):
                    if self.backtrack(assignment)!=None:
                        return self.backtrack(assignment)
                    else:
                        del assignment[var]
            return None
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        raise NotImplementedError


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
