"""
AIME 2024 problems. Train = AIME I, Test = AIME II.
Answers are integers 0-999.
"""

TRAIN = [
    {
        "id": "2024_I_1",
        "answer": 204,
        "text": (
            "Every morning Aya goes for a $9$-kilometer-long walk and stops at a coffee shop afterwards. "
            "When she walks at a constant speed of $s$ kilometers per hour, the walk takes her 4 hours, "
            "including $t$ minutes spent in the coffee shop. When she walks $s+2$ kilometers per hour, "
            "the walk takes her 2 hours and 24 minutes, including $t$ minutes spent in the coffee shop. "
            "Suppose Aya walks at $s+\\frac{1}{2}$ kilometers per hour. Find the number of minutes the "
            "walk takes her, including the $t$ minutes spent in the coffee shop."
        ),
    },
    {
        "id": "2024_I_2",
        "answer": 25,
        "text": (
            "There exist real numbers $x$ and $y$, both greater than 1, such that "
            "$\\log_x(y^x) = \\log_y(x^{4y}) = 10$. Find $xy$."
        ),
    },
    {
        "id": "2024_I_3",
        "answer": 809,
        "text": (
            "Alice and Bob play the following game. A stack of $n$ tokens lies before them. "
            "The players take turns with Alice going first. On each turn, the player removes either "
            "$1$ token or $4$ tokens from the stack. Whoever removes the last token wins. Find the "
            "number of positive integers $n$ less than or equal to $2024$ for which there exists a "
            "strategy for Bob that guarantees that Bob will win the game regardless of Alice's play."
        ),
    },
    {
        "id": "2024_I_4",
        "answer": 116,
        "text": (
            "Jen enters a lottery by picking $4$ distinct numbers from $S=\\{1,2,3,\\cdots,9,10\\}$. "
            "$4$ numbers are randomly chosen from $S$. She wins a prize if at least two of her numbers "
            "were $2$ of the randomly chosen numbers, and wins the grand prize if all four of her "
            "numbers were the randomly chosen numbers. The probability of her winning the grand prize "
            "given that she won a prize is $\\tfrac{m}{n}$ where $m$ and $n$ are relatively prime "
            "positive integers. Find $m+n$."
        ),
    },
    {
        "id": "2024_I_5",
        "answer": 104,
        "text": (
            "Rectangles $ABCD$ and $EFGH$ are drawn such that $D,E,C,F$ are collinear. Also, "
            "$A,D,H,G$ all lie on a circle. If $BC=16$, $AB=107$, $FG=17$, and $EF=184$, "
            "what is the length of $CE$?"
        ),
    },
    {
        "id": "2024_I_6",
        "answer": 294,
        "text": (
            "Consider the paths of length $16$ that follow the lines from the lower left corner to "
            "the upper right corner on an $8 \\times 8$ grid. Find the number of such paths that "
            "change direction exactly four times."
        ),
    },
    {
        "id": "2024_I_7",
        "answer": 540,
        "text": (
            "Find the largest possible real part of "
            "$(75+117i)z+\\frac{96+144i}{z}$ "
            "where $z$ is a complex number with $|z|=4$. Here $i=\\sqrt{-1}$."
        ),
    },
    {
        "id": "2024_I_8",
        "answer": 197,
        "text": (
            "Eight circles of radius $34$ are sequentially tangent, and two of the circles are "
            "tangent to $AB$ and $BC$ of triangle $ABC$, respectively. $2024$ circles of radius $1$ "
            "can be arranged in the same manner. The inradius of triangle $ABC$ can be expressed as "
            "$\\frac{m}{n}$, where $m$ and $n$ are relatively prime positive integers. Find $m+n$."
        ),
    },
    {
        "id": "2024_I_9",
        "answer": 480,
        "text": (
            "Let $A$, $B$, $C$, and $D$ be points on the hyperbola "
            "$\\frac{x^2}{20} - \\frac{y^2}{24} = 1$ such that $ABCD$ is a rhombus whose diagonals "
            "intersect at the origin. Find the greatest real number that is less than $BD^2$ for all "
            "such rhombi."
        ),
    },
    {
        "id": "2024_I_10",
        "answer": 113,
        "text": (
            "Let $\\triangle ABC$ have side lengths $AB=5$, $BC=9$, $CA=10$. The tangents to the "
            "circumcircle of $\\triangle ABC$ at $B$ and $C$ intersect at point $D$, and $\\overline{AD}$ "
            "intersects the circumcircle at $P \\neq A$. The length of $AP$ is equal to $\\frac{m}{n}$, "
            "where $m$ and $n$ are relatively prime integers. Find $m+n$."
        ),
    },
    {
        "id": "2024_I_11",
        "answer": 371,
        "text": (
            "Each vertex of a regular octagon is independently colored either red or blue with equal "
            "probability. The probability that the octagon can then be rotated so that all of the blue "
            "vertices end up at positions where there had been red vertices is $\\tfrac{m}{n}$, where "
            "$m$ and $n$ are relatively prime positive integers. Find $m+n$."
        ),
    },
    {
        "id": "2024_I_12",
        "answer": 385,
        "text": (
            "Define $f(x)=||x|-\\tfrac{1}{2}|$ and $g(x)=||x|-\\tfrac{1}{4}|$. Find the number of "
            "intersections of the graphs of "
            "$y=4g(f(\\sin(2\\pi x)))$ and $x=4g(f(\\cos(3\\pi y)))$."
        ),
    },
    {
        "id": "2024_I_13",
        "answer": 110,
        "text": (
            "Let $p$ be the least prime number for which there exists a positive integer $n$ such that "
            "$n^4+1$ is divisible by $p^2$. Find the least positive integer $m$ such that $m^4+1$ is "
            "divisible by $p^2$."
        ),
    },
    {
        "id": "2024_I_14",
        "answer": 104,
        "text": (
            "Let $ABCD$ be a tetrahedron such that $AB=CD=\\sqrt{41}$, $AC=BD=\\sqrt{80}$, and "
            "$BC=AD=\\sqrt{89}$. There exists a point $I$ inside the tetrahedron such that the "
            "distances from $I$ to each of the faces of the tetrahedron are all equal. This distance "
            "can be written in the form $\\frac{m\\sqrt{n}}{p}$, where $m$, $n$, and $p$ are positive "
            "integers, $m$ and $p$ are relatively prime, and $n$ is not divisible by the square of "
            "any prime. Find $m+n+p$."
        ),
    },
    {
        "id": "2024_I_15",
        "answer": 721,
        "text": (
            "Let $\\mathcal{B}$ be the set of rectangular boxes with surface area $54$ and volume $23$. "
            "Let $r$ be the radius of the smallest sphere that can contain each of the rectangular "
            "boxes that are elements of $\\mathcal{B}$. The value of $r^2$ can be written as "
            "$\\frac{p}{q}$, where $p$ and $q$ are relatively prime positive integers. Find $p+q$."
        ),
    },
]

TEST = [
    {
        "id": "2024_II_1",
        "answer": 73,
        "text": (
            "Among the 900 residents of Aimeville, there are 195 who own a diamond ring, 367 who own "
            "a set of golf clubs, and 562 who own a garden spade. In addition, each of the 900 "
            "residents owns a bag of candy hearts. There are 437 residents who own exactly two of "
            "these things, and 234 residents who own exactly three of these things. Find the number "
            "of residents of Aimeville who own all four of these things."
        ),
    },
    {
        "id": "2024_II_2",
        "answer": 236,
        "text": (
            "A list of positive integers has the following properties: the sum of the items in the "
            "list is $30$; the unique mode of the list is $9$; the median of the list is a positive "
            "integer that does not appear in the list itself. Find the sum of the squares of all the "
            "items in the list."
        ),
    },
    {
        "id": "2024_II_3",
        "answer": 45,
        "text": (
            "Find the number of ways to place a digit in each cell of a 2x3 grid so that the sum of "
            "the two numbers formed by reading left to right is $999$, and the sum of the three "
            "numbers formed by reading top to bottom is $99$."
        ),
    },
    {
        "id": "2024_II_4",
        "answer": 33,
        "text": (
            "Let $x, y$ and $z$ be positive real numbers that satisfy the following system of equations: "
            "$\\log_2\\left(\\frac{x}{yz}\\right) = \\frac{1}{2}$, "
            "$\\log_2\\left(\\frac{y}{xz}\\right) = \\frac{1}{3}$, "
            "$\\log_2\\left(\\frac{z}{xy}\\right) = \\frac{1}{4}$. "
            "Then the value of $\\left|\\log_2(x^4y^3z^2)\\right|$ is $\\tfrac{m}{n}$ where $m$ and "
            "$n$ are relatively prime positive integers. Find $m+n$."
        ),
    },
    {
        "id": "2024_II_5",
        "answer": 80,
        "text": (
            "Let $ABCDEF$ be a convex equilateral hexagon in which all pairs of opposite sides are "
            "parallel. The triangle whose sides are extensions of segments $AB$, $CD$, and $EF$ has "
            "side lengths 200, 240, and 300. Find the side length of the hexagon."
        ),
    },
    {
        "id": "2024_II_6",
        "answer": 55,
        "text": (
            "Alice chooses a set $A$ of positive integers. Then Bob lists all finite nonempty sets $B$ "
            "of positive integers with the property that the maximum element of $B$ belongs to $A$. "
            "Bob's list has 2024 sets. Find the sum of the elements of $A$."
        ),
    },
    {
        "id": "2024_II_7",
        "answer": 699,
        "text": (
            "Let $N$ be the greatest four-digit positive integer with the property that whenever one "
            "of its digits is changed to $1$, the resulting number is divisible by $7$. Let $Q$ and "
            "$R$ be the quotient and remainder, respectively, when $N$ is divided by $1000$. Find $Q+R$."
        ),
    },
    {
        "id": "2024_II_8",
        "answer": 127,
        "text": (
            "Torus $T$ is the surface produced by revolving a circle with radius $3$ around an axis "
            "in the plane of the circle that is a distance $6$ from the center of the circle (so like "
            "a donut). Let $S$ be a sphere with a radius $11$. When $T$ rests on the inside of $S$, "
            "it is internally tangent to $S$ along a circle with radius $r_i$, and when $T$ rests on "
            "the outside of $S$, it is externally tangent to $S$ along a circle with radius $r_o$. "
            "The difference $r_i - r_o$ can be written as $\\tfrac{m}{n}$, where $m$ and $n$ are "
            "relatively prime positive integers. Find $m+n$."
        ),
    },
    {
        "id": "2024_II_9",
        "answer": 902,
        "text": (
            "There is a collection of $25$ indistinguishable white chips and $25$ indistinguishable "
            "black chips. Find the number of ways to place some of these chips in the $25$ unit cells "
            "of a $5 \\times 5$ grid such that: each cell contains at most one chip; all chips in the "
            "same row and all chips in the same column have the same colour; any additional chip "
            "placed on the grid would violate one or more of the previous two conditions."
        ),
    },
    {
        "id": "2024_II_10",
        "answer": 468,
        "text": (
            "Let $\\triangle ABC$ have incenter $I$, circumcenter $O$, inradius $6$, and circumradius "
            "$13$. Suppose that $\\overline{IA} \\perp \\overline{OI}$. Find $AB \\cdot AC$."
        ),
    },
    {
        "id": "2024_II_11",
        "answer": 601,
        "text": (
            "Find the number of triples of nonnegative integers $(a,b,c)$ satisfying $a+b+c=300$ and "
            "$a^2b + a^2c + b^2a + b^2c + c^2a + c^2b = 6{,}000{,}000$."
        ),
    },
    {
        "id": "2024_II_12",
        "answer": 23,
        "text": (
            "Let $O=(0,0)$, $A=\\left(\\tfrac{1}{2},0\\right)$, and "
            "$B=\\left(0,\\tfrac{\\sqrt{3}}{2}\\right)$ be points in the coordinate plane. Let "
            "$\\mathcal{F}$ be the family of segments $\\overline{PQ}$ of unit length lying in the "
            "first quadrant with $P$ on the $x$-axis and $Q$ on the $y$-axis. There is a unique "
            "point $C$ on $\\overline{AB}$, distinct from $A$ and $B$, that does not belong to any "
            "segment from $\\mathcal{F}$ other than $\\overline{AB}$. Then $OC^2 = \\tfrac{p}{q}$, "
            "where $p$ and $q$ are relatively prime positive integers. Find $p+q$."
        ),
    },
    {
        "id": "2024_II_13",
        "answer": 321,
        "text": (
            "Let $\\omega \\neq 1$ be a $13$th root of unity. Find the remainder when "
            "$\\prod_{k=0}^{12}(2 - 2\\omega^k + \\omega^{2k})$ is divided by $1000$."
        ),
    },
    {
        "id": "2024_II_14",
        "answer": 211,
        "text": (
            "Let $b \\ge 2$ be an integer. Call a positive integer $n$ $b$-eautiful if it has exactly "
            "two digits when expressed in base $b$ and these two digits sum to $\\sqrt{n}$. For "
            "example, $81$ is $13$-eautiful because $81 = 63_{13}$ and $6+3 = \\sqrt{81}$. Find the "
            "least integer $b \\ge 2$ for which there are more than ten $b$-eautiful integers."
        ),
    },
    {
        "id": "2024_II_15",
        "answer": 315,
        "text": (
            "Find the number of rectangles that can be formed inside a fixed regular dodecagon "
            "($12$-gon) where each side of the rectangle lies on either a side or a diagonal of "
            "the dodecagon."
        ),
    },
]
