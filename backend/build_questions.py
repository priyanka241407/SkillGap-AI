"""
Build curated questions dataset for SkillGap AI.
Includes Python, SQL, Machine Learning, HTML and CSS, JavaScript, and Data Analysis.
Spans Beginner, Intermediate, and Advanced difficulties.
Each question includes accurate explanations and why_wrong details.
"""

import csv
import os

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
CSV_PATH = os.path.join(DATA_DIR, "questions.csv")

questions = [
    # ── PYTHON ─────────────────────────────────────────────────────────────
    # Beginner
    (1, "Python", "Beginner", "Which of the following is used to create a list in Python?", "Square brackets []", "Curly braces {}", "Parentheses ()", "Angle brackets <>", "A",
     "Square brackets [] are the standard Python syntax to define a mutable list (e.g., my_list = [1, 2, 3]).",
     "Curly braces {} create sets or dictionaries, parentheses () create tuples, and angle brackets are not valid list syntax in Python."),
    (2, "Python", "Beginner", "What keyword is used to define a function in Python?", "func", "def", "function", "define", "B",
     "The 'def' keyword (short for define) is the reserved keyword in Python used to declare a function.",
     "'func' is used in Go/Swift, 'function' is used in JavaScript, and 'define' is not a valid Python keyword."),
    (3, "Python", "Beginner", "What does the len() function return when passed a list?", "Converts list to lowercase", "Returns the number of elements in the list", "Creates a new empty list", "Sorts the list alphabetically", "B",
     "The built-in len() function returns the total number of items in an iterable object such as a list, string, or tuple.",
     "len() does not modify, sort, or create lists; it strictly returns an integer length count."),
    (4, "Python", "Beginner", "Which of these is an IMMUTABLE data type in Python?", "List", "Dictionary", "Set", "Tuple", "D",
     "Tuples are immutable in Python; once created, their elements cannot be modified, added, or removed.",
     "Lists, dictionaries, and sets are all mutable structures that can be altered after definition."),
    (5, "Python", "Beginner", "Which of these is NOT a valid built-in Python data type?", "Integer", "String", "Boolean", "Element", "D",
     "Python has standard built-in types such as int, str, bool, float, and list, but 'Element' is not a built-in type.",
     "Integer, String, and Boolean are standard core data types in Python."),
    # Intermediate
    (6, "Python", "Intermediate", "What does the expression [x**2 for x in range(5)] produce?", "[0, 1, 4, 9, 16]", "[1, 4, 9, 16, 25]", "[0, 2, 4, 6, 8]", "[1, 2, 3, 4, 5]", "A",
     "This list comprehension squares numbers in range(5) which generates 0, 1, 2, 3, and 4, producing [0, 1, 4, 9, 16].",
     "range(5) starts at index 0 and stops before 5 (0 to 4), so 25 is not included and values are squared, not doubled."),
    (7, "Python", "Intermediate", "What is the purpose of *args in a Python function definition?", "To pass keyword arguments as a dictionary", "To accept an arbitrary number of positional arguments as a tuple", "To enforce strict static type checking", "To pass arguments by memory reference only", "B",
     "*args collects extra positional arguments into a tuple, allowing functions to accept a variable number of parameters.",
     "**kwargs collects keyword arguments into a dictionary, whereas *args strictly handles positional arguments."),
    (8, "Python", "Intermediate", "What happens when you access a missing key using dict.get(key, default)?", "Raises a KeyError immediately", "Returns the default value without raising an error", "Inserts the key into the dictionary", "Returns None and deletes the dictionary", "B",
     "The .get() method safely retrieves a value for a key, returning the specified default (or None) if the key is not found.",
     "Direct square bracket access dict[key] raises KeyError, but .get() is designed specifically to prevent errors."),
    # Advanced
    (9, "Python", "Advanced", "What keyword is used to pause a function execution and turn it into a generator?", "return", "yield", "pause", "async", "B",
     "The 'yield' statement turns a function into a generator, producing values one at a time on demand and preserving state.",
     "'return' terminates function execution, whereas 'yield' pauses execution and retains local variables for subsequent next() calls."),
    (10, "Python", "Advanced", "What is the primary role of the Global Interpreter Lock (GIL) in CPython?", "Prevents memory leaks in NumPy", "Ensures only one native thread executes Python bytecode at a time", "Accelerates asynchronous network calls", "Automatically compiles Python to machine code", "B",
     "The GIL is a mutex in CPython that protects access to Python objects, preventing multiple native threads from executing bytecode concurrently.",
     "The GIL does not compile code to machine language nor does it speed up threads; it is a concurrency constraint to ensure thread-safe memory management."),

    # ── SQL ────────────────────────────────────────────────────────────────
    # Beginner
    (11, "SQL", "Beginner", "What does the SQL command 'SELECT * FROM users;' do?", "Selects all columns and rows from the users table", "Deletes the users table", "Inserts a new row into the users table", "Counts the total rows in the users table", "A",
     "The asterisk (*) is a wildcard that instructs SQL to return every column available in the specified table.",
     "DELETE removes data, INSERT adds data, and COUNT(*) is needed to calculate the row count."),
    (12, "SQL", "Beginner", "Which SQL clause is used to filter records that meet a specific condition?", "ORDER BY", "WHERE", "GROUP BY", "HAVING", "B",
     "The WHERE clause filters rows based on a specified boolean condition before grouping or sorting.",
     "ORDER BY sorts rows, GROUP BY combines rows by identical values, and HAVING filters aggregated groups."),
    (13, "SQL", "Beginner", "Which SQL keyword is used to return unique values and eliminate duplicates?", "UNIQUE", "DISTINCT", "DIFFERENT", "ISOLATE", "B",
     "SELECT DISTINCT removes duplicate rows from the query result set so each value appears only once.",
     "UNIQUE is a table constraint applied during schema creation, not the query clause used in a SELECT statement."),
    # Intermediate
    (14, "SQL", "Intermediate", "What is the key difference between INNER JOIN and LEFT JOIN?", "INNER JOIN only returns matching rows from both tables", "LEFT JOIN only returns rows with matching IDs", "INNER JOIN returns all rows from the left table", "There is no functional difference", "A",
     "INNER JOIN returns records that have matching values in both tables, whereas LEFT JOIN returns all records from the left table plus matches from the right.",
     "LEFT JOIN preserves all rows from the left table even when there are no corresponding rows in the right table (filling NULLs)."),
    (15, "SQL", "Intermediate", "When must the HAVING clause be used instead of the WHERE clause?", "When filtering rows based on aggregate functions like SUM() or COUNT()", "When filtering primary key columns", "When sorting alphabetical strings", "When joining more than three tables", "A",
     "HAVING filters data after grouping and aggregation (e.g., HAVING COUNT(*) > 5); WHERE cannot be used on aggregate functions.",
     "WHERE filters individual rows prior to aggregation, while HAVING operates on grouped aggregates."),
    # Advanced
    (16, "SQL", "Advanced", "Which window function assigns a sequential unique integer to rows within a partition?", "ROW_NUMBER()", "COUNT()", "DENSE_RANK()", "RANK_NUM()", "A",
     "ROW_NUMBER() computes a continuous sequence of integers (1, 2, 3...) for each row within a partition ordered by specified columns.",
     "RANK() and DENSE_RANK() handle ties with duplicate ranks, whereas ROW_NUMBER() always assigns unique sequential numbers."),
    (17, "SQL", "Advanced", "What is a Common Table Expression (CTE) in modern SQL?", "A permanent view saved to the hard disk", "A temporary named result set defined using the WITH clause", "An index used to speed up string queries", "A stored procedure for database backups", "B",
     "A CTE is a temporary named result set defined within the scope of a single SELECT, INSERT, UPDATE, or DELETE using the 'WITH' keyword.",
     "CTEs are not saved permanently like stored views or tables; they exist only during query execution."),

    # ── MACHINE LEARNING ───────────────────────────────────────────────────
    # Beginner
    (18, "Machine Learning", "Beginner", "What is supervised learning?", "Training a model on labeled input-output pairs", "Training a model without any target labels", "Clustering unorganized documents manually", "Writing hardcoded if-else statements", "A",
     "Supervised learning algorithms learn a mapping function from input variables to known target labels provided in the training data.",
     "Learning without labeled data is unsupervised learning, and hardcoded logic is not machine learning."),
    (19, "Machine Learning", "Beginner", "Which of the following is a classification problem?", "Predicting the exact sale price of a house", "Predicting whether an email is Spam or Not Spam", "Predicting tomorrow's temperature in Celsius", "Predicting the stock price of a company", "B",
     "Spam detection has categorical discrete classes (Spam vs. Not Spam), which is the definition of a classification task.",
     "Predicting continuous numerical numbers (house price, temperature, stock value) represents regression tasks."),
    (20, "Machine Learning", "Beginner", "What is the purpose of splitting data into training and test sets?", "To evaluate how well the model generalizes on unseen data", "To make the dataset twice as large", "To remove all missing values automatically", "To convert categorical data into numbers", "A",
     "Train-test splitting ensures the model is evaluated on unseen data to test how well it generalizes rather than memorizes.",
     "Splitting does not enlarge datasets or clean missing values; it provides unbiased validation."),
    # Intermediate
    (21, "Machine Learning", "Intermediate", "What does 'overfitting' mean in machine learning?", "Model performs well on training data but poorly on test data", "Model performs poorly on both training and test data", "Model trains too quickly", "Model has too few features to learn anything", "A",
     "Overfitting occurs when a complex model learns training noise and details so closely that it fails to generalize to new test data.",
     "Performing poorly on both sets is underfitting; fast training is simply computational efficiency."),
    (22, "Machine Learning", "Intermediate", "In classification, which metric is calculated as TP / (TP + FP)?", "Precision", "Recall", "Accuracy", "ROC-AUC", "A",
     "Precision measures the proportion of positive identifications that were actually correct: TP / (TP + FP).",
     "Recall is TP / (TP + FN), and Accuracy is (TP + TN) / Total. Precision measures exactness."),
    (23, "Machine Learning", "Intermediate", "What is the primary advantage of Random Forest over a single Decision Tree?", "Reduces variance and overfitting by averaging multiple trees", "Requires zero training data", "Always achieves 100% test accuracy", "Does not require numerical inputs", "A",
     "Random Forest is an ensemble of decision trees trained on bootstrap samples; averaging predictions reduces variance and resists overfitting.",
     "Random Forests still require proper data and feature prep, and no model guarantees 100% accuracy."),
    # Advanced
    (24, "Machine Learning", "Advanced", "What is the main purpose of Principal Component Analysis (PCA)?", "Dimensionality reduction while preserving maximum variance", "Classifying non-linear audio recordings", "Hyperparameter tuning for neural nets", "Removing outliers from datasets", "A",
     "PCA is an unsupervised technique that projects high-dimensional data onto orthogonal axes (principal components) that maximize variance.",
     "PCA is not a classifier or hyperparameter tuner; its primary use is feature reduction and multicollinearity reduction."),
    (25, "Machine Learning", "Advanced", "How does L1 regularization (Lasso) differ from L2 regularization (Ridge)?", "L1 can shrink feature coefficients completely to zero, performing feature selection", "L2 adds the absolute sum of coefficients", "L1 only works on decision trees", "L2 causes severe underfitting on small datasets", "A",
     "L1 regularization adds an absolute weight penalty (|w|) which drives redundant feature weights to exactly zero, yielding sparse models.",
     "L2 adds squared weight penalty (w^2) shrinking weights smoothly without setting them strictly to zero."),

    # ── HTML AND CSS ───────────────────────────────────────────────────────
    # Beginner
    (26, "HTML and CSS", "Beginner", "Which HTML tag is used to define an internal hyperlink?", "<link>", "<a>", "<href>", "<navlink>", "B",
     "The <a> (anchor) tag with the href attribute specifies a hyperlink destination in HTML.",
     "<link> links external stylesheets in the <head>, <href> is an attribute (not a tag), and <navlink> is not an HTML tag."),
    (27, "HTML and CSS", "Beginner", "What does the CSS Box Model consist of, from inside to outside?", "Content, Padding, Border, Margin", "Content, Margin, Border, Padding", "Border, Content, Padding, Margin", "Margin, Border, Padding, Content", "A",
     "The CSS box model structure from inside out is: Content area -> Padding -> Border -> Margin.",
     "Padding directly surrounds content inside the border, while margin creates space outside the border."),
    (28, "HTML and CSS", "Beginner", "Which CSS property changes the text color of an element?", "color", "text-color", "font-color", "text-style", "A",
     "In CSS, the 'color' property sets the foreground color of text.",
     "'text-color' and 'font-color' are invalid CSS properties."),
    # Intermediate
    (29, "HTML and CSS", "Intermediate", "In CSS Flexbox, which property aligns items along the MAIN axis?", "justify-content", "align-items", "align-content", "flex-direction", "A",
     "justify-content aligns flex items along the main axis (horizontal by default), while align-items aligns along the cross axis.",
     "align-items controls cross-axis alignment, and flex-direction sets whether the main axis is row or column."),
    (30, "HTML and CSS", "Intermediate", "What does the CSS media query @media (max-width: 768px) target?", "Screens with a viewport width of 768 pixels or narrower", "Screens wider than 768 pixels only", "Print documents only", "High resolution 4K monitors", "A",
     "max-width: 768px applies CSS rules to screens up to 768px wide, commonly used for mobile and tablet breakpoints.",
     "min-width: 768px would target screens 768px and wider."),
    # Advanced
    (31, "HTML and CSS", "Advanced", "What creates a new stacking context for the z-index property in CSS?", "An element with position: relative and an integer z-index", "Any paragraph tag with margin: 0", "Applying color: red to a container", "Setting display: inline on an image", "A",
     "A positioned element (relative, absolute, or fixed) with an integer z-index establishes a new local stacking context.",
     "Standard static elements do not create stacking contexts and ignore z-index properties."),
    (32, "HTML and CSS", "Advanced", "Which CSS properties are best animated on the GPU without triggering layout reflows?", "transform and opacity", "width and height", "margin and top", "padding and font-size", "A",
     "Modern browsers optimize 'transform' and 'opacity' on the GPU compositor thread without triggering expensive DOM reflows.",
     "Animating layout properties like width, height, and margin causes CPU reflow and repaint on every frame."),

    # ── JAVASCRIPT ─────────────────────────────────────────────────────────
    # Beginner
    (33, "JavaScript", "Beginner", "What is the main difference between 'let' and 'var' in JavaScript?", "let has block scope while var has function scope", "var cannot be reassigned", "let is only used for numbers", "There is no difference in modern browsers", "A",
     "'let' declarations are block-scoped (constrained to the nearest enclosing curly braces), preventing accidental global leakage.",
     "'var' is function-scoped and hoisted, while 'const' prevents reassignment."),
    (34, "JavaScript", "Beginner", "What method outputs diagnostic messages to the web browser developer console?", "console.log()", "print()", "document.write()", "system.out.println()", "A",
     "console.log() is the standard method used in JavaScript to print variables and objects to the browser console.",
     "print() opens the browser print dialog window, and system.out.println() is Java syntax."),
    (35, "JavaScript", "Beginner", "Which Array method creates a NEW array populated with transformed elements?", "map()", "forEach()", "filter()", "pop()", "A",
     ".map() transforms each element and returns a brand-new array of equal length without mutating the original.",
     ".forEach() executes a side effect but returns undefined; .filter() selects a subset based on a boolean check."),
    # Intermediate
    (36, "JavaScript", "Intermediate", "What does the strict equality operator (===) do compared to loose equality (==)?", "Checks both value and type without type coercion", "Converts both values to strings first", "Only checks memory address references", "Performs variable assignment", "A",
     "The strict equality operator (===) checks both value and data type without performing implicit type conversion.",
     "The loose equality operator (==) performs type coercion (e.g., '5' == 5 evaluates to true)."),
    (37, "JavaScript", "Intermediate", "What is a closure in JavaScript?", "A function that retains access to its lexical scope even when executed outside that scope", "A method that immediately closes browser tabs", "A function that has no return statement", "An object with strictly private properties", "A",
     "A closure is created when an inner function captures variables from its enclosing outer function environment.",
     "Closures are a core functional programming pattern, not related to closing windows or terminating loops."),
    # Advanced
    (38, "JavaScript", "Advanced", "In the JavaScript Event Loop, which queue executes before the next macrotask?", "Microtasks (Promises, queueMicrotask)", "Macrotasks always execute first", "Both queues execute simultaneously on multiple threads", "Priority is chosen randomly by browser engine", "A",
     "The microtask queue (Promise callbacks, process.nextTick) is processed completely after the current script and before the next macrotask (setTimeout, setInterval).",
     "Macrotasks wait until all pending microtasks in the queue are exhausted."),
    (39, "JavaScript", "Advanced", "What is the purpose of the 'useCallback' hook in React?", "Memoizes a callback function instance to prevent unnecessary child re-renders", "Triggers asynchronous HTTP API requests", "Replaces Redux for global application state", "Forces an immediate synchronous re-render", "A",
     "useCallback returns a memoized version of a callback that only changes if specified dependencies change, optimizing child component renders.",
     "useEffect handles side-effects like fetching, and useReducer/Context manages complex state."),

    # ── DATA ANALYSIS ──────────────────────────────────────────────────────
    # Beginner
    (40, "Data Analysis", "Beginner", "What is the median of the following dataset: [2, 5, 8, 12, 15]?", "8", "7.4", "12", "5", "A",
     "The median is the middle value in an ordered dataset. For [2, 5, 8, 12, 15], the middle element at index 2 is 8.",
     "7.4 is the calculated arithmetic mean ((2+5+8+12+15)/5), but median refers strictly to the sorted middle element."),
    (41, "Data Analysis", "Beginner", "Which Pandas method displays a concise statistical summary (mean, std, min, max, quartiles)?", "df.describe()", "df.info()", "df.head()", "df.tail()", "A",
     "df.describe() calculates summary statistics including count, mean, standard deviation, min, 25%, 50%, 75%, and max.",
     "df.info() prints data types and non-null counts, while df.head() displays the first 5 rows."),
    (42, "Data Analysis", "Beginner", "Which Python library is built specifically on top of Matplotlib for statistical graphics?", "Seaborn", "Flask", "Django", "Requests", "A",
     "Seaborn is a Python data visualization library based on Matplotlib that provides attractive statistical graphics with minimal code.",
     "Flask and Django are web frameworks, and Requests is an HTTP networking library."),
    # Intermediate
    (43, "Data Analysis", "Intermediate", "What does a Pearson correlation coefficient of -0.85 indicate?", "A strong negative linear relationship between two variables", "No relationship between variables", "A strong positive linear relationship", "A data entry error", "A",
     "Pearson r values range from -1 to +1; a value of -0.85 indicates that as one variable increases, the other strongly decreases linearly.",
     "Values close to 0 indicate no linear correlation, and +0.85 would indicate a strong positive relationship."),
    (44, "Data Analysis", "Intermediate", "In Pandas, which method is used to fill missing (NaN) values with a specified replacement?", "df.fillna()", "df.dropna()", "df.replace_null()", "df.clean()", "A",
     "df.fillna(value) fills NaN cells with specified values (such as column mean, median, or zero).",
     "df.dropna() removes rows containing NaNs rather than imputing replacements."),
    # Advanced
    (45, "Data Analysis", "Advanced", "What is the Interquartile Range (IQR) used for in exploratory data analysis?", "Measuring statistical dispersion and detecting outliers (Q3 - Q1)", "Calculating the total sum of columns", "Converting continuous features to strings", "Balancing categorical class distributions", "A",
     "The IQR is the difference between the 75th percentile (Q3) and 25th percentile (Q1); values beyond 1.5 * IQR are typically flagged as outliers.",
     "IQR measures spread and variance resistance, not totals or class balancing."),
    (46, "Data Analysis", "Advanced", "In hypothesis testing, what does a p-value less than 0.05 typically signify?", "Evidence to reject the null hypothesis at the 5% significance level", "The hypothesis is 95% proven true", "The dataset has 5% missing rows", "The test must be restarted with more data", "A",
     "A p-value < 0.05 indicates the observed data is unlikely under the null hypothesis, giving statistical grounds to reject it.",
     "P-values measure probability of observing data under H0, not proof of truth or missing row percentages."),

    # ── Additional Skills from SkillGap (Pandas, React, Git, Deep Learning) ─
    (47, "Pandas", "Beginner", "Which function is used to read a CSV file into a DataFrame in Pandas?", "pd.read_csv()", "pd.open_csv()", "pd.load_csv()", "pd.import_csv()", "A",
     "pd.read_csv() is the standard and most widely used function in Pandas to load CSV data into a DataFrame.",
     "Functions like open_csv() or load_csv() do not exist in the Pandas library."),
    (48, "Pandas", "Intermediate", "How do you select a single column named 'Salary' from a DataFrame df?", "df['Salary']", "df(Salary)", "df{Salary}", "df.column('Salary')", "A",
     "df['Salary'] (or df.Salary) accesses the Series representing the 'Salary' column.",
     "Parentheses () call methods, and curly braces {} are invalid syntax for DataFrame indexing."),
    (49, "React", "Beginner", "What hook is used to manage state in a React functional component?", "useState", "useEffect", "useContext", "useRef", "A",
     "useState is the foundational React hook for declaring state variables in functional components.",
     "useEffect is for side-effects, useContext is for global context consumption, and useRef is for mutable references."),
    (50, "Git", "Beginner", "What command is used to save staged changes to your local Git repository?", "git commit -m 'message'", "git push", "git clone", "git pull", "A",
     "git commit records staged snapshots in the local repository history.",
     "git push uploads local commits to a remote server, while git pull downloads remote changes."),
]

with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["id", "skill", "difficulty", "question", "option_a", "option_b", "option_c", "option_d", "correct", "explanation", "why_wrong"])
    for q in questions:
        writer.writerow(list(q))

print(f"Successfully wrote {len(questions)} questions to {CSV_PATH}")
