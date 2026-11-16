from tkinter import *
from tkinter import messagebox
import os
from PIL import ImageGrab
from datetime import datetime
from tkinter.scrolledtext import ScrolledText


# Molecule's Selection
selected_atom_to_move = None
first_bond_atom = None
last_x = 0
last_y = 0
bonds_placed = []
name_of_molecule = None
atom_mode_number = 0
formula_of_compund = None
steps_by_user = []
selected_bond_to_delete = None
selected_atom_to_delete = None

valency = {
    "C": 4,
    "H": 1, 
    "O": 2,
    "N": 3
}


def user_instructions():

    instruction = """
                                      MOLECULE BUILDER VERSION v0.2

    PLACE button : Allows you to place the atoms on the canvas, 
    select the atom in the top left and then place it

    MOVE button : Allows you to move around the atoms after it is placed

    BOND button : Allows you to bond between two atoms, select the single, double or triple bond 
    for the type of bonds to be formed between the two atoms

    Normal bond: Forms normal bonds, lines only

    Wedge bond : Click on this button and on a pre-existing single bond to make the solid wedge 
    bond and the direction of the first single bond created matters to the direction of the wedge bond

    Dash bond : Same as wedge bond but displays a dashed wedge bond

    Note: you cannot click on the wedge / dash bond and then create a bond, first create a normal bond 
    and then you can change the bond type to either wedge or dash
    But the first clicked atom has the tapered end and the second clicked atom has the bigger end of the bond
    Please click exaclty on the bond and not nearby

    Normal atom : Place only the letter of the atom without any colour

    Coloured atom: Place the atom but the atoms are coloured and in a circle
    
    Clear: Clears the canvas and you can build any molecule from scratch
    
    Export Molecule: First create a folder on your DESKTOP as molecules_saved and then after you build the 
    molecule you can click on at and a png image will automaticlly be saved into the folder

    Undo: Undo button lets you undo the actions done which can be bond or atom either
    the formula is also updated automatically and the undo button works until the canvas is cleared
    
    Formula Label; It shows the formula of the molecule and you might notice that sometimes
    it is showing the number of H but there isnt any H placed by you, the program automatically estimates
    the number of hydrogen in the molecule and after you build the whole skeleton
    and even if you do not place any hydrogens the formula accurately estimates the hydrogen

    Delete Button : Select the bond you want to delete and it becomes highlighted and then click on delete buttons
    to delete the selected bond
    

    Information versionwise and Updates

    About v0.3 (Under Development):
    Delete button

    About v0.2 :
    Normal and Colour atom option
    Export molecule
    Dash and Wedge bond 
    Rearranged the buttons to a much more appeasing order
    Option to select bond
    User Manual button
    Undo button
    Display the version info and updates
    
    About v0.1 :
    A Molecule builder from python
    Has C,H,O as atoms
    Place, bond, move mode 
    Clear button to clear the screen
    Formula label displaying the formula automatically
    Only coloured atoms"""

    display = Tk()
    display.geometry("900x700")
    display.title("User Instructions")
    display.config(background="#dcdcfd")

    text_area = ScrolledText(
        display, wrap = WORD,
        width = 40, height = 15
    )
    text_area.pack(padx = 10, pady = 10, fill = BOTH, expand = True)

    text_area.insert(END, instruction)


def undo_button():

    global steps_by_user, atoms_placed, bonds_placed
    global number_of_carbons, number_of_nitrogen, number_of_oxygen, number_of_hydrogen

    print("Undo")

    if len(steps_by_user) == 0:
        return 

    last_placed = steps_by_user.pop()

    if last_placed["id"] == "bond":
        temp12 = bonds_placed.pop()

        for line_id in temp12["line_ids"]:
            canvas.delete(line_id)

        for atom in atoms_placed:
            if atom["id"] == temp12["atom1"] or atom["id"] == temp12["atom2"]:
                atom["bond_order"] -= temp12['order']

        print(bonds_placed)

    else:
        temp11 = atoms_placed.pop()

        temp_element = temp11["element"]

        if temp_element == "C":
            number_of_carbons -= 1

        elif temp_element == "N":
            number_of_nitrogen -= 1

        elif temp_element == "O":
            number_of_oxygen -= 1

        elif temp_element == "H":
            number_of_hydrogen -= 1

        update_formula()

        temp11_circle = temp11["circle_id"]
        temp11_text = temp11["text_id"]
        canvas.delete(temp11_circle)
        canvas.delete(temp11_text)
        print(atoms_placed)

    print(steps_by_user)



def on_line_click(event):
    global selected_bond_to_delete

    clicked_item = event.widget.find_withtag("current")[0]
    
    for bond in list(bonds_placed):

        if clicked_item in bond["line_ids"]:

            selected_bond_to_delete = bond

            for line_id in bond['line_ids']:
                try:
                    canvas.itemconfig(line_id, fill = 'orange', width = 3)
                except:
                    pass


            if bond["order"] == 1 and stereo_type.get() != 'none' :
                target_stereo = stereo_type.get()
                apply_stereo(bond, target_stereo)

            break



def delete_button():
    global selected_bond_to_delete, bonds_placed

    if selected_bond_to_delete is not None:

        for line_id in selected_bond_to_delete['line_ids']:
            canvas.delete(line_id)

        for atom in atoms_placed:
            if atom['id'] == selected_bond_to_delete['atom1'] or atom['id'] == selected_bond_to_delete['atom2']:
                atom['bond_order'] -= selected_bond_to_delete['order']

        bonds_placed.remove(selected_bond_to_delete)

        update_formula()
        calculate_hydrogens()
        selected_bond_to_delete = None
        print("Bond deleted successfully")

    else:
        print("No bond selected")



def apply_stereo(bond, new_stereo):
    bond["stereo"] = new_stereo

    for line_id in bond["line_ids"]:
        canvas.delete(line_id)

    atom1 = next(a for a in atoms_placed if a["id"] == bond["atom1"])
    atom2 = next(a for a in atoms_placed if a["id"] == bond["atom2"])

    x1, y1 = atom1["x"], atom1['y']
    x2, y2 = atom2['x'], atom2['y']

    dx, dy = x2 - x1, y2 - y1
    length = (dx**2 + dy**2)**0.5

    if length == 0:
        return

    px, py = -dy / length, dx / length
    width = 8

    new_ids = []

    if bond["order"] == 1 and new_stereo == "wedge":
        poly_id = canvas.create_polygon(
            x1, y1,
            x2 + px*width, y2 + py*width,
            x2 - px*width, y2 - py*width,
            fill = 'black', tags = 'bond'
        )
        canvas.tag_lower(poly_id)
        new_ids = [poly_id]

    elif bond["order"] == 1 and new_stereo == "dash":
        num_dashes = 10

        width = 10

        for i in range(1, num_dashes + 1):
            fraction = i / num_dashes
            cx = x1 + dx*fraction
            cy = y1 + dy*fraction
            w = width*fraction

            line_id = canvas.create_line(
                cx + px*w, cy + py*w,
                cx - px*w, cy - py*w,
                width=2, fill = 'black', tags = 'bond'
            )
            canvas.tag_lower(line_id)
            new_ids.append(line_id)

    else:
        line_id = canvas.create_line(
            x1, y1,
            x2, y2,
            width=1.5, fill = "black", tags = "bond"
        )
        canvas.tag_lower(line_id)
        new_ids = [line_id]

    bond["line_ids"] = new_ids



def atom_mode_type():
    global atom_mode_number

    if atom_design_type.get() == 0:
        atom_mode_number = 0

    elif atom_design_type.get() == 2:
        atom_mode_number = 4


def take_image():

    canvas.update_idletasks()

    max_x = 0
    max_y = 0
    least_y = 1000
    least_x = 1000

    for every in atoms_placed:

        if every['x'] > max_x:
            max_x = every['x']

        if every['y'] > max_y:
            max_y = every['y']

        if every['x'] < least_x:
            least_x = every['x']

        if every['y'] < least_y:
            least_y = every['y']

    print("Max X: ", max_x, "\nMax Y: ", max_y)
    print("Least X: ", least_x, "\nLeast Y: ", least_y)

    root_x = canvas.winfo_rootx()
    root_y = canvas.winfo_rooty()

    x2 = max_x + root_x + 25
    y2 = max_y + root_y + 25
    x1 = least_x + root_x - 25
    y1 = least_y + root_y - 25

    scale = canvas.winfo_fpixels('1i')/72.0
    bbox = (
        int(x1), int(y1),
        int(x2), int(y2)
    )

    home_dir = os.path.expanduser("~")
    save_dir = os.path.join(home_dir, "Desktop", "molecules_saved")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    filename = f"molecule_{formula_of_compund}_{timestamp}.png" 

    os.makedirs('molecules_saved', exist_ok=True)
    save_path = os.path.join(save_dir, filename)

    img = ImageGrab.grab(bbox=bbox)
    img.save(save_path)
    print("Saved Successfully")



number_of_carbons = 0
number_of_hydrogen = 0
number_of_oxygen = 0
number_of_nitrogen = 0

# Choose mode, place, move, bond
def choose_mode():
    global mode, first_bond_atom

    if mode_number.get() == 0:
        mode = "place"
        first_bond_atom = None

    elif mode_number.get() == 1:
        mode = "move"
        first_bond_atom = None

    else:
        mode = "bond"
        first_bond_atom = None


# A message pop usp stating that valency has been exceeded
def exceeded_valency():
    messagebox.showwarning("Exceeded Valency", "The bond order of the atom exceeds maximum valency")


# Prints the name of the atom selected
def atom_selected():
    if radio_number.get() == 0:
        print("You have selected Carbon : C")

    elif radio_number.get() == 1:
        print("You have selected Hydrogen : H")

    else:
        print("You have selected Oxygen : O")



def update_formula():

    implicit_hydrogens = calculate_implicit_hydrogens()

    total_hydrogens = number_of_hydrogen + implicit_hydrogens

    formula.config(text = f"C{number_of_carbons} H{total_hydrogens} O{number_of_oxygen} N{number_of_nitrogen}")

    global formula_of_compund
    formula_of_compund = f"C{number_of_carbons} H{total_hydrogens} O{number_of_oxygen} N{number_of_nitrogen}"



def place_atom(event):
    global atom_id,  number_of_carbons, number_of_hydrogen, number_of_oxygen, number_of_nitrogen, steps_by_user

    atom_id = atom_id + 1
    selected_atom = radio_number.get()
    x1 = event.x
    y1 = event.y
    print(f"You placed {atoms[selected_atom]} at {x1} , {y1}")

    group_tag = f"atom_group_{atom_id}"

    type_1 = ['white', 'white', 17 , 15 ,atom_color[selected_atom], 'black', 12, 20]

    circle_id = canvas.create_oval(x1-type_1[atom_mode_number + 3], y1-type_1[atom_mode_number + 3], x1+type_1[atom_mode_number + 3], y1+type_1[atom_mode_number + 3], fill = type_1[atom_mode_number], tags=group_tag, outline = type_1[atom_mode_number + 1])

    text_id = canvas.create_text(x1, y1, text = atoms[selected_atom], tags = group_tag, fill = "black", font = ('Arial', type_1[atom_mode_number + 2]))

    atom_data = {
        "id": atom_id,
        "element" : atoms[selected_atom],
        "x": x1,
        "y": y1,
        "circle_id": circle_id,
        "text_id": text_id,
        "bond_order":0
    }

    temp = str(atom_data["element"])

    if temp == "C":
        number_of_carbons += 1

    elif temp == "H":
        number_of_hydrogen += 1

    elif temp == "O":
        number_of_oxygen += 1

    elif temp == "N":
        number_of_nitrogen += 1

    update_formula()

    atoms_placed.append(atom_data)
    steps_by_user.append(atom_data)

    print(atoms_placed)
    print(f"C{number_of_carbons}H{number_of_hydrogen}O{number_of_oxygen}")



def clear_molecule():
    global atom_id, selected_atom_to_move, first_bond_atom, number_of_oxygen, number_of_hydrogen, number_of_carbons, number_of_nitrogen, steps_by_user

    canvas.delete("all")

    atoms_placed.clear()
    bonds_placed.clear()
    steps_by_user.clear()

    number_of_carbons = 0
    number_of_hydrogen = 0
    number_of_oxygen = 0
    number_of_nitrogen = 0
    atom_id = 0

    selected_atom_to_move = None
    first_bond_atom = None

    formula.config(text = "C0 H0 O0 N0")



def canvas_click(event):

    if mode == "place":
        place_atom(event)

    elif mode == "move":
        select_atom(event)

    elif mode == "bond":
        select_bond_atom(event)



def update_bonds(atom_moved):

    for bond in bonds_placed:

        if bond["atom1"] == atom_moved["id"] or bond["atom2"] == atom_moved["id"]:
            print("This bond needs updating", bond)

        atom1_data = None
        atom2_data = None

        for atom in atoms_placed:

            if atom["id"] == bond["atom1"]:
                atom1_data = atom

            elif atom["id"] == bond["atom2"]:
                atom2_data = atom

        x1 = atom1_data["x"]
        y1 = atom1_data["y"]

        x2 = atom2_data["x"]
        y2 = atom2_data["y"]

        dx = x2 - x1
        dy = y2 - y1

        length = (dx**2 + dy**2)**0.5

        px = -dy / length
        py = dx / length

        offset = 6


        stereo = bond.get("stereo", 'none')

        # Single Bond
        if bond['order'] == 1:

            if stereo == 'wedge':
                width = 8

                canvas.coords(
                    bond["line_ids"][0],
                    x1, y1,
                    x2 + px*width, y2 + py*width,
                    x2 - px*width, y2 - py*width
                )

            elif stereo == "dash":
                width = 10
                num_dashes = len(bond["line_ids"])

                for i, line_id in enumerate(bond["line_ids"]):

                    fraction = (i+1) / num_dashes
                    cx = x1 + dx*fraction
                    cy = y1 + dy*fraction
                    w = width*fraction

                    canvas.coords(
                        line_id,
                        cx + px*w, cy + py*w,
                        cx - px*w, cy - py*w
                    )

            else:
                canvas.coords(
                    bond["line_ids"][0],
                    x1, y1,
                    x2, y2
                )
 

        # Double Bond
        elif bond["order"] == 2:

            canvas.coords(
                bond["line_ids"][0],
                x1 + px*offset,
                y1 + py*offset,
                x2 + px*offset,
                y2 + py*offset
            )

            canvas.coords(
                bond["line_ids"][1],
                x1 - px*offset,
                y1 - py*offset,
                x2 - px*offset,
                y2 - py*offset
            )

        # Triple Bond
        elif bond["order"] == 3:

            canvas.coords(
                bond["line_ids"][0],
                x1 + px*offset,
                y1 + py*offset,
                x2 + px*offset,
                y2 + py*offset
            )

            canvas.coords(
                bond["line_ids"][1],
                x1 ,
                y1 ,
                x2,
                y2 
            )

            canvas.coords(
                bond["line_ids"][2],
                x1 - px*offset,
                y1 - py*offset,
                x2 - px*offset,
                y2 - py*offset
            )

    

def calculate_hydrogens():

    total_implicit_hydrogens = 0

    for atom in atoms_placed:

        if atom["element"] == "C" or atom["element"] == "O":
            maximum_valency = valency[atom["element"]]
            used_valency = atom["bond_order"]

            remaining_valency = maximum_valency - used_valency

            total_implicit_hydrogens += remaining_valency

    print("Implicit hydrogens: ", total_implicit_hydrogens)



def get_bonded_atoms(atom):

    bonded_atoms = []

    for bond in bonds_placed:

        if bond["atom1"] == atom["id"]:
            bonded_atom_id = bond["atom2"]

        elif bond["atom2"] == atom["id"]:
            bonded_atom_id = bond["atom1"]

        else:
            continue

        for other_atom in atoms_placed:
            if other_atom["id"] == bonded_atom_id:
                bonded_atoms.append(other_atom)

    return bonded_atoms



def calculate_implicit_hydrogens():

    implicit_hydrogens = 0

    for atom in atoms_placed:

        if atom["element"] == "H":
            continue

        remaining_valency = valency[atom["element"]] - atom["bond_order"]

        if remaining_valency > 0:
            implicit_hydrogens += remaining_valency

    return implicit_hydrogens



def release_atom(event):
    global selected_atom_to_move

    selected_atom_to_move = None



def draw_bond(atom1, atom2, order):

    x1 = atom1["x"]
    y1 = atom1["y"]

    x2 = atom2["x"]
    y2 = atom2["y"]

    dx = x2 - x1
    dy = y2 - y1

    length = (dx**2 + dy**2)**0.5

    px = -dy / length
    py = dx / length

    offset = 6

    if order == 1:

        line_id = canvas.create_line(
            x1, y1,
            x2, y2,
            width = 1.5, fill='black', tags = "bond"
        )

        canvas.tag_lower(line_id)

        return [line_id]


    elif order == 2:

        line1 = canvas.create_line(
            x1 + px*offset,
            y1 + py*offset,
            x2 + px*offset,
            y2 + py*offset,
            width = 1.5, fill='black', tags = "bond"
        )

        line2 = canvas.create_line(
            x1 - px*offset,
            y1 - py*offset,
            x2 - px*offset,
            y2 - py*offset,
            width = 1.5, fill='black', tags = "bond"
        )

        canvas.tag_lower(line1)
        canvas.tag_lower(line2)

        return [line1, line2]


    elif order == 3:

        line1 = canvas.create_line(
            x1 + px * offset,
            y1 + py * offset,
            x2 + px * offset,
            y2 + py * offset,
            width=1.5, fill='black', tags = "bond"
        )

        line2 = canvas.create_line(
            x1,
            y1,
            x2,
            y2,
            width=1.5, fill='black', tags = "bond"
        )

        line3 = canvas.create_line(
            x1 - px * offset,
            y1 - py * offset,
            x2 - px * offset,
            y2 - py * offset,
            width=1.5, fill='black', tags = "bond"
        )

        canvas.tag_lower(line1)
        canvas.tag_lower(line2)
        canvas.tag_lower(line3)

        return [line1, line2, line3]



def select_bond_atom(event):
    global first_bond_atom, steps_by_user

    clicked_object = canvas.find_closest(event.x, event.y)[0]


    for atom in atoms_placed:

        if (clicked_object == atom["circle_id"] or clicked_object == atom["text_id"]):

            if first_bond_atom is None:

                first_bond_atom = atom
                print("First bond atom: ", atom)
                canvas.itemconfig(atom["circle_id"], fill = "#dcdcfd")

            else:

                second_bond_atom = atom

                if second_bond_atom["id"] == first_bond_atom["id"]:
                    print("Cannot bond an atom to itself")
                    first_bond_atom = None
                    return

                order = bond_order.get()

                first_used = first_bond_atom["bond_order"]
                second_used = second_bond_atom["bond_order"]

                first_max = valency[first_bond_atom["element"]]
                second_max = valency[second_bond_atom["element"]]

                if first_used + order > first_max:
                    exceeded_valency()
                    first_bond_atom = None
                    return

                if second_used + order > second_max:
                    exceeded_valency()
                    first_bond_atom = None
                    return

                second_bond_atom = atom

                if second_bond_atom["id"] == first_bond_atom["id"]:
                    print("Cannot bond an atom to itself")
                    return


                first_bond_atom["bond_order"] += order
                second_bond_atom["bond_order"] += order

                print(first_bond_atom["element"], first_bond_atom["bond_order"], "/", valency[first_bond_atom["element"]])

                print(second_bond_atom["element"],second_bond_atom["bond_order"], "/", valency[second_bond_atom["element"]])

                line_ids = draw_bond(first_bond_atom, second_bond_atom, order)


                bond_data = { "id": "bond", "atom1": first_bond_atom["id"], "atom2": second_bond_atom["id"], "order": bond_order.get(), "line_ids": line_ids , "stereo": "none"}

                bonds_placed.append(bond_data)
                steps_by_user.append(bond_data)

                update_formula()
                calculate_hydrogens()

                print("Bond created:", bond_data)
                print("Bonded atoms: ", get_bonded_atoms(first_bond_atom))

                canvas.itemconfig(first_bond_atom["circle_id"], fill = "white")
                first_bond_atom = None



def select_atom(event):
    global selected_atom_to_move, last_x, last_y

    clicked_object = canvas.find_closest(event.x, event.y)[0]

    for atom in atoms_placed:
        if clicked_object == atom["circle_id"] or clicked_object == atom["text_id"]:
            selected_atom_to_move = atom
            last_y = event.y
            last_x = event.x

            print("You selected: ", atom)

    print(clicked_object)


def move_atom(event):
    global last_y, last_x

    if selected_atom_to_move is not None:

        dx = event.x - last_x
        dy = event.y - last_y

        canvas.move(selected_atom_to_move["circle_id"], dx, dy)
        canvas.move(selected_atom_to_move["text_id"], dx, dy)

        selected_atom_to_move["x"] += dx
        selected_atom_to_move["y"] += dy

        update_bonds(selected_atom_to_move)

        last_x = event.x
        last_y = event.y



# temporary function
def test_click(event):
    print(canvas.find_closest(event.x, event.y))


# create window
window = Tk() 
window.geometry("1450x1000")
window.title("Molecule Builder")
window.config(background="#dcdcfd")

bond_order = IntVar()
bond_order.set(1)

canvas = Canvas(window, height=700, width = 1250, background="white")


label = Label(window, text = "Welcome to version v0.2", background="#dcdcfd", font = ('Arial',13, 'bold'), fg = "black")

label.pack()


# Radio Buttons

button_frame = Frame(window, background="#dcdcfd")
button_frame.pack(side = TOP, anchor = 'w', padx = 5)


right_frame = Frame(window, background=  "#dcdcfc", width = 200)
right_frame.pack(side = RIGHT, fill = Y, padx = 10, pady = 10)


atoms = ["C", "H", "O", "N"]
atom_color = ['#eb385c', "#4dd53e", "#4951db", "#ffff00"]
atoms_placed = []
atom_id = 0
mode = "place"


radio_number = IntVar()

for index in range(len(atoms)):
    radiobutton = Radiobutton(
        button_frame, 
        text = atoms[index],
        variable = radio_number, 
        value = index,
        padx = 25, pady = 10,
        font = ("Arial", 17),
        command= atom_selected,
        indicatoron = False,
        activebackground="#ebe1fa",
        activeforeground="#acacac",
        selectcolor= "#6bef1e",
    )

    radiobutton.pack(side = LEFT, padx = 5)

canvas.bind("<Button-1>", canvas_click)
canvas.pack(padx = 30, pady = 15)


modes_canvas = ["Place", "Move", "Bond"]
mode_number = IntVar()
mode_number.set(0)

for index in range(len(modes_canvas)):
    radiobutton1 = Radiobutton(
        button_frame,
        text = modes_canvas[index],
        variable=mode_number,
        value = index,
        padx = 25,
        pady = 10,
        font = ("Arial", 17), 
        command = choose_mode,
        indicatoron = False,
        activebackground="#ebe1fa",
        activeforeground="#acacac",
        selectcolor= "#6bef1e"
        
    )
    radiobutton1.pack(side = RIGHT, padx = 3, anchor="w")


bond_orders = [
    ("Single", 1), ("Double", 2), ("Triple", 3)]


for text, value in bond_orders:
    bond_button = Radiobutton(
        button_frame,
        padx = 25, pady = 10,
        text = text,
        variable= bond_order,
        value = value,
        font = ('Arial', 15),
        indicatoron = False,
        activebackground="#ebe1fa",
        activeforeground="#acacac",
        selectcolor= "#6bef1e",
        command= lambda: print("Bond order: ", bond_order.get())
    )

    bond_button.pack(side = LEFT, anchor = 'e', padx = 3)


canvas.bind("<B1-Motion>", move_atom)
canvas.bind("<ButtonRelease-1>", release_atom)
canvas.tag_bind("bond", "<Button-1>", on_line_click)

#Display Formula

print(f"C{number_of_carbons}H{number_of_hydrogen}O{number_of_oxygen}")

formula = Label(
    right_frame,
    text= f"C{number_of_carbons} H{number_of_hydrogen} O{number_of_oxygen} N{number_of_nitrogen}",
    font = ("Arial", 15),
    padx = 10, pady = 10
)
formula.pack(side = TOP, padx = 5, pady = 10)

clear_button = Button(
    right_frame, 
    text="Clear", 
    command=clear_molecule, 
    font = ("Arial", 11),
    background='#dcdcfd',
    padx = 10, pady = 10
)
clear_button.pack(side = TOP, anchor='w', pady = 8)


export_image = Button(
    right_frame,
    text = "Export Molecule",
    font = ("Arial", 11),
    command= take_image,
    padx = 5,
    pady = 10
)
export_image.pack(side = TOP, anchor='w', pady = 10)


atom_design = [("Normal", 0), ("Colored", 2)]
atom_design_type = IntVar()
temp1 = 0

for i, j in atom_design:
    atom_mode = Radiobutton(
        right_frame,
        text = i + " Atom",
        font = ("Arial", 11),
        value = j,
        variable= atom_design_type,
        command= atom_mode_type,
        indicatoron=0,
        padx = 10, pady = 15,
        width = 13,
        activebackground="#ebe1fa",
        activeforeground="#acacac",
        selectcolor= "#6bef1e",
    )
    atom_mode.pack(side = TOP, anchor = 'w', pady = 5)
    temp1 = temp1 + 1



stereo_type = StringVar()
stereo_type.set("none")

stereo_options = [("Normal", "none"), ("Wedge", "wedge"), ("Dash", "dash")]

for text, value in stereo_options:
    stereo_button = Radiobutton(
        right_frame,
        padx = 15,
        pady = 15,
        text = text + " Bond",
        value = value,
        variable= stereo_type,
        font = ("Arial", 12),
        indicatoron=False,
        activebackground="#ebe1fa",
        selectcolor= "#6bef1e",
        width = 12
    )
    stereo_button.pack(side = TOP, anchor='w', pady = 5)


instructions = Button(
    right_frame,
    padx = 10,
    pady = 15,
    text = "User Manual",
    command= user_instructions,
    font = ('Arial', 12)
)
instructions.pack(anchor= 'w', side = BOTTOM, padx = 5, pady = 35)


undo = Button(
    right_frame,
    padx = 10,
    pady = 12,
    text = "Undo",
    command= undo_button,
    font = ("Arial", 12)
)
undo.pack(anchor='e',side = LEFT, padx = 0, pady = 5 )


delete_setting = StringVar()

delete = Button(
    right_frame,
    padx = 10,
    pady = 10,
    text = "Delete",
    command = delete_button,
    font = ("Arial", 12)
)
delete.pack(anchor = 'e', side = LEFT, padx = 0, pady = 5)

# Place window on the screen
window.mainloop()