
import tkinter as tk
import ast
import math
import operator

root = tk.Tk()
root.title("NextHikes Advanced Calculator")
root.geometry("420x680")
root.resizable(False, False)
root.configure(bg="#101A35")

BG = "#101A35"
DISPLAY_BG = "#DFFDF2"
BLUE = "#1D4ED8"
BLUE_LIGHT = "#2563EB"
BLUE_DARK = "#172554"
ORANGE = "#F59E0B"
RED = "#F05270"
WHITE = "#FFFFFF"
MUTED = "#94A3B8"

expression = ""
memory = 0
just_calculated = False

calculation_history = []

display = tk.StringVar()
history_text = tk.StringVar(value="Ready")

binary_ops = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
}

unary_ops = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}

functions = {
    "sin": lambda x: math.sin(math.radians(x)),
    "cos": lambda x: math.cos(math.radians(x)),
    "tan": lambda x: math.tan(math.radians(x)),
    "asin": lambda x: math.degrees(math.asin(x)),
    "acos": lambda x: math.degrees(math.acos(x)),
    "atan": lambda x: math.degrees(math.atan(x)),
    "sqrt": math.sqrt,
    "log": math.log10,
    "ln": math.log,
    "abs": abs,
    "factorial": math.factorial,
    "exp": math.exp,
}

constants = {
    "pi": math.pi,
    "e": math.e,
}


def safe_eval(expr):
    """Evaluate arithmetic without using Python eval()."""

    tree = ast.parse(expr, mode="eval")

    def visit(node):

        if isinstance(node, ast.Expression):
            return visit(node.body)

        if isinstance(node, ast.Constant):
            if type(node.value) in (int, float):
                return node.value

            raise ValueError("Invalid number")

        if isinstance(node, ast.BinOp):

            op_type = type(node.op)

            if op_type not in binary_ops:
                raise ValueError("Invalid operator")

            left = visit(node.left)
            right = visit(node.right)

            if op_type is ast.Pow and abs(right) > 1000:
                raise ValueError("Exponent too large")

            result = binary_ops[op_type](left, right)

            if isinstance(result, complex):
                raise ValueError("Complex result not supported")

            if not math.isfinite(result):
                raise ValueError("Result too large")

            return result

        if isinstance(node, ast.UnaryOp):

            op_type = type(node.op)

            if op_type not in unary_ops:
                raise ValueError("Invalid sign")

            return unary_ops[op_type](visit(node.operand))

        if isinstance(node, ast.Name):

            if node.id in constants:
                return constants[node.id]

            raise ValueError("Unknown constant")

        if isinstance(node, ast.Call):

            if not isinstance(node.func, ast.Name):
                raise ValueError("Invalid function")

            if node.func.id not in functions:
                raise ValueError("Unknown function")

            if node.keywords or len(node.args) != 1:
                raise ValueError("Invalid arguments")

            value = visit(node.args[0])

            if node.func.id == "factorial":

                if value < 0 or not float(value).is_integer():
                    raise ValueError("Factorial needs an integer")

                if value > 170:
                    raise ValueError("Number too large")

                value = int(value)

            result = functions[node.func.id](value)

            if not math.isfinite(result):
                raise ValueError("Invalid result")

            return result

        raise ValueError("Invalid expression")

    return visit(tree)


def format_result(value):

    if isinstance(value, float):

        if value.is_integer():
            return str(int(value))

        return f"{value:.12g}"

    return str(value)



def save_history(original_expression, result):

    calculation_history.append({
        "expression": original_expression,
        "result": result
    })


def open_history():

    history_window = tk.Toplevel(root)
    history_window.title("Calculation History")
    history_window.geometry("380x480")
    history_window.resizable(False, False)
    history_window.configure(bg=BG)

    tk.Label(
        history_window,
        text="N E X T H I K E S",
        font=("Arial", 12, "bold"),
        bg=BG,
        fg="#60A5FA"
    ).pack(pady=(15, 2))

    tk.Label(
        history_window,
        text="CALCULATION HISTORY",
        font=("Arial", 14, "bold"),
        bg=BG,
        fg=WHITE
    ).pack(pady=(5, 12))

    count_label = tk.Label(
        history_window,
        text="Total calculations: 0",
        font=("Arial", 10),
        bg=BG,
        fg=MUTED
    )

    count_label.pack(pady=(0, 8))

    history_frame = tk.Frame(history_window, bg=BG)

    history_frame.pack(
        fill="both",
        expand=True,
        padx=12,
        pady=5
    )

    scrollbar = tk.Scrollbar(history_frame)
    scrollbar.pack(side="right", fill="y")

    history_list = tk.Listbox(
        history_frame,
        font=("Arial", 11),
        bg=DISPLAY_BG,
        fg=BLUE_DARK,
        selectbackground=BLUE,
        selectforeground=WHITE,
        yscrollcommand=scrollbar.set,
        relief="flat",
        bd=0,
        activestyle="none"
    )

    history_list.pack(
        fill="both",
        expand=True
    )

    scrollbar.config(command=history_list.yview)

    def refresh_history():

        history_list.delete(0, tk.END)

        count_label.config(
            text=f"Total calculations: {len(calculation_history)}"
        )

        if not calculation_history:

            history_list.insert(
                tk.END,
                "No calculation history yet."
            )

            return

        for item in reversed(calculation_history):

            history_list.insert(
                tk.END,
                f"{item['expression']} = {item['result']}"
            )

    def reuse_history(event=None):

        global expression, just_calculated

        selection = history_list.curselection()

        if not selection or not calculation_history:
            return

        index = selection[0]

        if index >= len(calculation_history):
            return

        item = calculation_history[::-1][index]

        expression = item["result"]

        display.set(expression)

        history_text.set("Previous result recalled")

        just_calculated = True

        history_window.destroy()

    def clear_history():

        calculation_history.clear()

        refresh_history()

        history_text.set("History cleared")

    history_list.bind(
        "<Double-Button-1>",
        reuse_history
    )

    button_frame = tk.Frame(
        history_window,
        bg=BG
    )

    button_frame.pack(
        fill="x",
        padx=12,
        pady=12
    )

    tk.Button(
        button_frame,
        text="Clear History",
        font=("Arial", 10, "bold"),
        bg=RED,
        fg=WHITE,
        activebackground="#FB7185",
        relief="flat",
        cursor="hand2",
        command=clear_history
    ).pack(
        side="left",
        fill="x",
        expand=True,
        padx=4,
        ipady=8
    )

    tk.Button(
        button_frame,
        text="Close",
        font=("Arial", 10, "bold"),
        bg=BLUE,
        fg=WHITE,
        activebackground=BLUE_LIGHT,
        relief="flat",
        cursor="hand2",
        command=history_window.destroy
    ).pack(
        side="right",
        fill="x",
        expand=True,
        padx=4,
        ipady=8
    )

    refresh_history()


def press(value):

    global expression, just_calculated

    if display.get() == "Error":
        expression = ""

    if just_calculated:

        if value in "+-*/%":
            pass
        else:
            expression = ""

    just_calculated = False

    if value in (
        "sin", "cos", "tan", "asin", "acos",
        "atan", "sqrt", "log", "ln", "abs",
        "factorial", "exp"
    ):

        expression += value + "("

    elif value == "π":
        expression += "pi"

    elif value == "e":
        expression += "e"

    elif value == "x²":
        expression += "**2"

    elif value == "xʸ":
        expression += "**"

    elif value == "√":
        expression += "sqrt("

    elif value == "×":
        expression += "*"

    elif value == "÷":
        expression += "/"

    elif value == "−":
        expression += "-"

    else:
        expression += value

    display.set(
        expression.replace("*", "×").replace("/", "÷")
    )

    history_text.set("")


def clear():

    global expression, just_calculated

    expression = ""
    just_calculated = False

    display.set("")
    history_text.set("Ready")


def backspace():

    global expression, just_calculated

    expression = expression[:-1]
    just_calculated = False

    display.set(
        expression.replace("*", "×").replace("/", "÷")
    )


def calculate():

    global expression, just_calculated

    if not expression:
        return

    try:

        original_expression = expression

        result = safe_eval(expression)

        formatted_result = format_result(result)

        save_history(
            original_expression.replace("*", "×").replace("/", "÷"),
            formatted_result
        )

        history_text.set(
            original_expression.replace("*", "×").replace("/", "÷")
            + " = " + formatted_result
        )

        expression = formatted_result

        display.set(expression)

        just_calculated = True

    except Exception:

        display.set("Error")

        history_text.set("Invalid calculation")

        expression = ""

        just_calculated = False


def percentage():

    global expression, just_calculated

    if not expression:
        return

    try:

        original_expression = expression

        result = safe_eval(expression) / 100

        formatted_result = format_result(result)

        save_history(
            original_expression.replace("*", "×").replace("/", "÷")
            + " %",
            formatted_result
        )

        expression = formatted_result

        display.set(expression)

        history_text.set("Percentage calculated")

        just_calculated = True

    except Exception:

        display.set("Error")

        expression = ""

        just_calculated = False


def memory_add():

    global memory

    try:

        memory += safe_eval(expression)

        history_text.set("Added to memory")

    except Exception:

        history_text.set("Nothing to add")


def memory_subtract():

    global memory

    try:

        memory -= safe_eval(expression)

        history_text.set("Subtracted from memory")

    except Exception:

        history_text.set("Nothing to subtract")


def memory_recall():

    global expression, just_calculated

    if just_calculated:
        expression = ""

    expression += format_result(memory)

    display.set(
        expression.replace("*", "×").replace("/", "÷")
    )

    just_calculated = False


def memory_clear():

    global memory

    memory = 0

    history_text.set("Memory cleared")



header_frame = tk.Frame(
    root,
    bg=BG
)

header_frame.pack(
    fill="x",
    padx=12,
    pady=(10, 5)
)


tk.Button(
    header_frame,
    text="📜 History",
    font=("Arial", 8, "bold"),
    bg=ORANGE,
    fg=WHITE,
    activebackground="#D97706",
    activeforeground=WHITE,
    relief="flat",
    bd=0,
    cursor="hand2",
    command=open_history
).pack(
    side="left",
    ipadx=4,
    ipady=2
)

tk.Label(
    header_frame,
    text="N E X T H I K E S",
    font=("Arial", 12, "bold"),
    bg=BG,
    fg="#60A5FA"
).pack(
    side="right",
    pady=5
)


tk.Label(
    root,
    text="SCIENTIFIC CALCULATOR",
    font=("Arial", 10),
    bg=BG,
    fg="#60A5FA"
).pack(
    pady=(0, 10)
)

screen = tk.Entry(
    root,
    textvariable=display,
    font=("Arial", 20, "bold"),
    justify="right",
    state="readonly",
    bg=DISPLAY_BG,
    fg=BLUE_DARK,
    readonlybackground=DISPLAY_BG,
    bd=0,
    relief="flat"
)

screen.pack(
    fill="x",
    padx=12,
    ipady=18
)


tk.Label(
    root,
    textvariable=history_text,
    font=("Arial", 10),
    anchor="e",
    bg=BG,
    fg=MUTED
).pack(
    fill="x",
    padx=15,
    pady=(5, 8)
)

buttons = [

    ("MC", memory_clear, MUTED),
    ("MR", memory_recall, MUTED),
    ("M+", memory_add, MUTED),
    ("M-", memory_subtract, MUTED),

    ("sin", lambda: press("sin"), BLUE_LIGHT),
    ("cos", lambda: press("cos"), BLUE_LIGHT),
    ("tan", lambda: press("tan"), BLUE_LIGHT),
    ("√", lambda: press("√"), BLUE_LIGHT),

    ("asin", lambda: press("asin"), BLUE),
    ("acos", lambda: press("acos"), BLUE),
    ("atan", lambda: press("atan"), BLUE),
    ("x²", lambda: press("x²"), BLUE),

    ("(", lambda: press("("), BLUE),
    (")", lambda: press(")"), BLUE),
    ("xʸ", lambda: press("xʸ"), BLUE),
    ("÷", lambda: press("÷"), BLUE),

    ("7", lambda: press("7"), BLUE_LIGHT),
    ("8", lambda: press("8"), BLUE_LIGHT),
    ("9", lambda: press("9"), BLUE_LIGHT),
    ("×", lambda: press("×"), BLUE),

    ("4", lambda: press("4"), BLUE_LIGHT),
    ("5", lambda: press("5"), BLUE_LIGHT),
    ("6", lambda: press("6"), BLUE_LIGHT),
    ("−", lambda: press("−"), BLUE),

    ("1", lambda: press("1"), BLUE_LIGHT),
    ("2", lambda: press("2"), BLUE_LIGHT),
    ("3", lambda: press("3"), BLUE_LIGHT),
    ("+", lambda: press("+"), BLUE),

    ("C", clear, BLUE),
    ("0", lambda: press("0"), BLUE_LIGHT),
    (".", lambda: press("."), BLUE_LIGHT),
    ("=", calculate, BLUE),

    ("π", lambda: press("π"), BLUE),
    ("e", lambda: press("e"), BLUE),
    ("%", percentage, BLUE),
    ("⌫", backspace, BLUE),
]


frame = tk.Frame(
    root,
    bg=BG
)

frame.pack(
    fill="both",
    expand=True,
    padx=8,
    pady=(0, 8)
)

for col in range(4):

    frame.grid_columnconfigure(
        col,
        weight=1,
        uniform="col"
    )

total_rows = (len(buttons) + 3) // 4

for row in range(total_rows):

    frame.grid_rowconfigure(
        row,
        weight=1,
        uniform="row"
    )

for index, (label, command, color) in enumerate(buttons):

    row, col = divmod(index, 4)

    btn = tk.Button(
        frame,
        text=label,
        font=("Arial", 12, "bold"),
        bg=color,
        fg=WHITE,
        activebackground="#60A5FA",
        activeforeground=BLUE_DARK,
        relief="flat",
        bd=0,
        cursor="hand2",
        command=command
    )

    btn.grid(
        row=row,
        column=col,
        padx=3,
        pady=3,
        sticky="nsew",
        ipadx=2,
        ipady=3
    )

def keyboard_input(event):

    key = event.char

    if key in "0123456789.()+-*/%":
        press(key)

    elif event.keysym == "Return":
        calculate()

    elif event.keysym == "BackSpace":
        backspace()

    elif event.keysym == "Escape":
        clear()


root.bind("<Key>", keyboard_input)


root.mainloop()
