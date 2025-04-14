from tkinter import ttk, messagebox, simpledialog
import tkinter as tk
import struct
import json
import os

cwd = os.getcwd()
root = tk.Tk()

# File path & offset
name_offset = 0x0
sex_offset = 0x12
money_offset = 0x69250
bag_offsets = [
    (0x3f28, 0x3f2a), (0x3f2c, 0x3f2e), (0x3f30, 0x3f32),
    (0x3f34, 0x3f36), (0x3f38, 0x3f3a), (0x3f3c, 0x3f3e),
    (0x3f40, 0x3f42), (0x3f44, 0x3f46), (0x3f48, 0x3f4a),
    (0x3f4c, 0x3f4e), (0x3f50, 0x3f52), (0x3f54, 0x3f56),
    (0x3f58, 0x3f5a), (0x3f5c, 0x3f5e), (0x3f60, 0x3f62),
    (0x3f64, 0x3f66), (0x3f68, 0x3f6a), (0x3f6c, 0x3f6e),
    (0x3f70, 0x3f72), (0x3f74, 0x3f76), (0x3f78, 0x3f7a),
    (0x3f7c, 0x3f7e), (0x3f80, 0x3f82), (0x3f84, 0x3f86),
]

id_file = os.path.join(cwd, "data/data_id.json")
save_paths = [
    os.path.join(cwd, "savedata/character1.sav"),
    os.path.join(cwd, "savedata/character2.sav"),
    os.path.join(cwd, "savedata/character3.sav")
]

# Reading data functions
def read_name(character, offset, size):
    character.seek(offset)
    raw_data = character.read(size)
    name = "".join(s for s in raw_data.decode("ascii") if s.isprintable())
    return name.strip("\x00")

def read_2byte(character, offset, size):
    character.seek(offset)
    raw_data = character.read(size)
    return struct.unpack("<H", raw_data)[0]

def read_4byte(character, offset, size):
    character.seek(offset)
    raw_data = character.read(size)
    return struct.unpack("<L", raw_data)[0]

def bag_items(character, slot_offset, quantity_offset):
    item_slot = read_2byte(character, slot_offset, 2)
    item_quantity = read_2byte(character, quantity_offset, 2)
    return item_slot, item_quantity

def load_data(save_path):
    try:
        with open(save_path, "rb") as character, open(id_file, "r") as items:
            items_dict = json.load(items)
            db = dict(sorted(items_dict["items"].items(), key=lambda item: item[1]))
            name = read_name(character, name_offset, 16)
            if not name:
                return None
            sex = read_2byte(character, sex_offset, 2)
            money = read_4byte(character, money_offset, 4)
            data = []
            for i, (slot_offset, quantity_offset) in enumerate(bag_offsets, start=1):
                slot_item, slot_quantity = bag_items(character, slot_offset, quantity_offset)
                item_name = items_dict["items"].get(str(slot_item))
                data.append({"Slot": i, "Name": item_name, "Quantity": slot_quantity})
            return db, name, sex, money, data
    except FileNotFoundError:
        return None

def handle_double_click(event, tree, save_path, db):
    # Identify selected row and clumn
    item_id = tree.identify_row(event.y)
    column_id = tree.identify_column(event.x)

    if not item_id:
        return  # No selected row

    if column_id == "#2":  # Column "Name"
        current_values = tree.item(item_id, "values")
        slot_index = int(current_values[0]) - 1

        # Dropdown menu
        edit_window = create_edit_window()
        tk.Label(edit_window, text="Choose new item:").pack(pady=5)

        selected_id = tk.StringVar()
        dropdown = create_dropdown(db, edit_window, selected_id)
        dropdown.bind("<KeyRelease>", lambda event: update_dropdown(event, dropdown, db))

        tk.Button(
            edit_window,
            text="Confirm",
            command=lambda: confirm_edit_item(dropdown, db, save_path, slot_index, tree, edit_window)
        ).pack(pady=10)

    elif column_id == "#3":  # Clumn "Quantity"
        current_values = tree.item(item_id, "values")
        slot_index = int(current_values[0]) - 1
        new_quantity = simpledialog.askinteger(
            "Edit Quantity",
            "Enter new quantity (1-99):",
            minvalue=1,
            maxvalue=99
        )
        if new_quantity is not None:
            update_quantity_in_table(tree, save_path, db, slot_index, new_quantity)

# Functions for edit items/quantity
def create_edit_window():
    edit_window = tk.Toplevel(root)
    edit_window.iconbitmap(os.path.join(cwd, "data/clipboard.ico"))
    edit_window.title("Edit Item")
    return edit_window

def create_dropdown(db, parent, selected_id):
    dropdown = ttk.Combobox(parent, textvariable=selected_id, values=list(db.values()), state="normal")
    dropdown.config(width=50)
    dropdown.pack(pady=5)
    return dropdown

def update_dropdown(event, dropdown, db):
    value = dropdown.get().lower()
    filtered_items = [item for item in db.values() if value in item.lower()]
    dropdown.config(values=filtered_items)

def confirm_edit_item(dropdown, db, save_path, slot_index, tree, edit_window):
    chosen_item = dropdown.get()
    if chosen_item:
        item_id = next((key for key, value in db.items() if value == chosen_item), None)
        
        edit_item_in_file(save_path, slot_index, item_id, db, tree) 
        edit_window.destroy()

def edit_item_in_file(save_path, slot_index, selected_id, db, tree):
    slot_offset, _ = bag_offsets[slot_index]
    try:
        with open(save_path, "r+b") as character:
            character.seek(slot_offset)
            character.write(struct.pack("<H", int(selected_id)))

        # Update table
        tree.item(tree.get_children()[slot_index], values=(slot_index + 1, db[selected_id], tree.item(tree.get_children()[slot_index], "values")[2]))
        messagebox.showinfo("Success", "Item updated successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to update item: {e}")

def update_quantity_in_table(tree, save_path, db, slot_index, new_quantity):
    new_quantity = min(new_quantity, 99)  # Max 99
    slot_offset, quantity_offset = bag_offsets[slot_index]
    try:
        with open(save_path, "r+b") as character:
            character.seek(quantity_offset)
            character.write(struct.pack("<H", new_quantity))

        # Update table
        item = tree.get_children()[slot_index]
        item_values = list(tree.item(item, "values"))
        item_values[2] = new_quantity
        tree.item(item, values=item_values)

        messagebox.showinfo("Success", "Quantity updated successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to update quantity: {e}")

# Characters functions
def create_character_frame(save_path, parent_frame):
    character_data = load_data(save_path)
    if character_data:
        db, name, sex, money, data = character_data

        frame = tk.Frame(parent_frame, borderwidth=2, relief="solid")
        frame.pack(side="top", pady=10, fill="x")

        tk.Label(frame, text=f"Name: {name}", font=("Arial", 14)).pack(pady=2)
        tk.Label(frame, text=f"Sex: {'Male' if sex == 1 else 'Female'}", font=("Arial", 14)).pack(pady=2)
        money_label = tk.Label(frame, text=f"Money: {money}z", font=("Arial", 14))
        money_label.pack(pady=2)

        tk.Button(frame, text="Add Max Money", command=lambda: add_max_money(save_path, money_label)).pack(pady=5)

        tree = ttk.Treeview(frame, columns=("Slot", "Name", "Quantity"), show="headings", height=8)
        tree.heading("Slot", text="Slot")
        tree.heading("Name", text="Name")
        tree.heading("Quantity", text="Quantity")
        tree.pack(pady=5)

        for item in data:
            tree.insert("", "end", values=(item["Slot"], item["Name"], item["Quantity"]))

        # Double click name/quantity
        tree.bind("<Double-1>", lambda event: handle_double_click(event, tree, save_path, db))

def add_max_money(save_path, money_label):
    try:
        with open(save_path, "r+b") as character:
            character.seek(money_offset)
            money_quantity = struct.pack("<L", 9999999)
            character.write(money_quantity)
        money_label.config(text="Money: 9999999z")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to add money: {e}")

def save_changes_action():
    response = messagebox.askyesno("Confirm", "Do you want to save changes?")
    if response:
        open(os.path.join(cwd, "modifications_done.flag"), "w").write("done")
        root.destroy()

def main():
    root.title("MHFU Savefile Editor")
    
    # Edit icon
    root.iconbitmap(os.path.join(cwd, "data/clipboard.ico"))

    # Scrollbar canvas
    main_frame = tk.Frame(root)
    main_frame.pack(fill="both", expand=True)

    canvas = tk.Canvas(main_frame)
    scrollbar = tk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas)

    # Link scroll to canvas
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Title and save changes button
    tk.Label(scrollable_frame, text="MHFU Savefile Editor", font=("Arial", 20, "bold")).pack(pady=10)
    tk.Button(scrollable_frame, text="Save Changes", command=save_changes_action).pack(pady=10)

    # Creating character frame for every character
    for save_path in save_paths:
        create_character_frame(save_path, scrollable_frame)

    root.update_idletasks()
    canvas_width = scrollable_frame.winfo_reqwidth() + scrollbar.winfo_width() + 20
    root.geometry(f"{canvas_width}x800")

    root.mainloop()
