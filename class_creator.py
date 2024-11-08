import xml.etree.ElementTree as ET
from xml.dom import minidom
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import json

LIGHT_MODE_COLORS = {
    "bg": "#ffffff",
    "fg": "#000000",
    "entry_bg": "#ffffff",
    "button_bg": "#e0e0e0",
    "button_fg": "#000000",
    "frame_bg": "#ffffff"
}

DARK_MODE_COLORS = {
    "bg": "#3e3e3e",
    "fg": "#ffffff",
    "entry_bg": "#3e3e3e",
    "button_bg": "#555555",
    "button_fg": "#000000",
    "frame_bg": "#3e3e3e"
}

# Dark mode toggle function
def toggle_dark_mode():
    colors = DARK_MODE_COLORS if dark_mode_var.get() else LIGHT_MODE_COLORS
    root.config(bg=colors["bg"])
    frame.config(bg=colors["frame_bg"])
    
    for widget in frame.winfo_children():
        if isinstance(widget, ttk.Label):
            widget.config(background=colors["bg"], foreground=colors["fg"])
        elif isinstance(widget, ttk.Button):
            widget.config(style="Rounded.TButton")

    button_style = ttk.Style()
    button_style.configure("Rounded.TButton",
                           background=colors["button_bg"],
                           foreground=colors["button_fg"],
                           padding=(10, 5),
                           relief="flat")
    button_style.map("Rounded.TButton",
                     background=[("active", colors["button_bg"])],
                     foreground=[("active", colors["button_fg"])])

# Function to show help information
def show_help():
    help_text = (
        "This application helps generate XML files based on the provided configuration.\n\n"
        "Instructions:\n"
        "- Use 'Browse...' to select an input file (list.txt) with each item on a new line.\n"
        "  The format for each line should be: type,class (e.g., clothing,B43_AlphasKit).\n"
        "- Use 'Save As...' to specify where to save the output XML file.\n"
        "- Enter values for 'Nominal', 'Lifetime', 'Restock', etc., to set default values.\n"
        "- Toggle 'Dark Mode' to switch between light and dark themes.\n"
        "- Use 'Preview XML' to open a preview window showing the generated XML output based on the current configuration.\n\n"
        "Buttons:\n"
        "- Save Config: Save the current settings to a configuration file.\n"
        "- Load Config: Load settings from a previously saved configuration file.\n"
        "- Reset to Defaults: Reset all fields to their default values.\n\n"
        "Expected Input File Format:\n"
        "- Each line in 'list.txt' should follow this format: type,class\n"
        "  - For example: clothing,B43_AlphasKit or weapons,AK47\n\n"
        "Note:\n"
        "- Ensure the input file is formatted correctly for the application to process it without errors."
    )
    messagebox.showinfo("Help", help_text)


# Function to select the input file
def select_input_file():
    input_file = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
    input_file_entry.delete(0, tk.END)
    input_file_entry.insert(0, input_file)

# Function to select and save the output file
def save_output_file():
    output_file = filedialog.asksaveasfilename(defaultextension=".xml", filetypes=[("XML Files", "*.xml")])
    output_file_entry.delete(0, tk.END)
    output_file_entry.insert(0, output_file)

# Function to generate XML with default values
def generate_xml_from_list(input_file, output_file, nominal, lifetime, restock, min_val, quantmin, quantmax, cost, flags, preview=False):
    try:
        with open(input_file, 'r') as f:
            items = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        messagebox.showerror("Error", "Input file not found!")
        return

    xml_root = ET.Element("types")

    for line in items:
        try:
            item_type, item_name = line.split(",")
            item_type = item_type.strip().lower()
            item_name = item_name.strip()
        except ValueError:
            messagebox.showerror("Error", f"Invalid line format in input file: '{line}'")
            continue

        item_element = ET.SubElement(xml_root, "type", name=item_name)
        ET.SubElement(item_element, "nominal").text = nominal
        ET.SubElement(item_element, "lifetime").text = lifetime
        ET.SubElement(item_element, "restock").text = restock
        ET.SubElement(item_element, "min").text = min_val
        ET.SubElement(item_element, "quantmin").text = quantmin
        ET.SubElement(item_element, "quantmax").text = quantmax
        ET.SubElement(item_element, "cost").text = cost
        
        category_name = "clothes" if item_type == "clothing" else "weapons"
        ET.SubElement(item_element, "category", name=category_name)
        
        ET.SubElement(item_element, "flags", {
            "count_in_cargo": str(flags['count_in_cargo']),
            "count_in_hoarder": str(flags['count_in_hoarder']),
            "count_in_map": str(flags['count_in_map']),
            "count_in_player": str(flags['count_in_player']),
            "crafted": str(flags['crafted']),
            "deloot": str(flags['deloot'])
        })
        
        ET.SubElement(item_element, "usage", name="Town")
        
        for tier in ["Tier4", "Tier3", "Tier2", "Tier1"]:
            ET.SubElement(item_element, "value", name=tier)

    rough_string = ET.tostring(xml_root, 'utf-8')
    parsed = minidom.parseString(rough_string)
    pretty_xml = parsed.toprettyxml(indent="    ")

    if preview:
        preview_window = tk.Toplevel(root)
        preview_window.title("XML Preview")
        text = tk.Text(preview_window, wrap="word", font=("Segoe UI", 10))
        text.insert("1.0", pretty_xml)
        text.config(state="disabled")
        text.pack(expand=True, fill="both")
    else:
        with open(output_file, "w") as f:
            f.write(pretty_xml)
        messagebox.showinfo("Success", f"XML file '{output_file}' generated successfully with {len(items)} items.")

def generate_xml(preview=False):
    input_file = input_file_entry.get()
    output_file = output_file_entry.get()
    nominal = nominal_entry.get()
    lifetime = lifetime_entry.get()
    restock = restock_entry.get()
    min_val = min_entry.get()
    quantmin = quantmin_entry.get()
    quantmax = quantmax_entry.get()
    cost = cost_entry.get()

    flags = {
        "count_in_cargo": flag_vars["count_in_cargo"].get(),
        "count_in_hoarder": flag_vars["count_in_hoarder"].get(),
        "count_in_map": flag_vars["count_in_map"].get(),
        "count_in_player": flag_vars["count_in_player"].get(),
        "crafted": flag_vars["crafted"].get(),
        "deloot": flag_vars["deloot"].get()
    }

    if not input_file or not output_file:
        messagebox.showerror("Error", "Please select both input and output files.")
    else:
        generate_xml_from_list(input_file, output_file, nominal, lifetime, restock, min_val, quantmin, quantmax, cost, flags, preview=preview)

def reset_to_default():
    nominal_entry.delete(0, tk.END)
    nominal_entry.insert(0, "10")
    lifetime_entry.delete(0, tk.END)
    lifetime_entry.insert(0, "86400")
    restock_entry.delete(0, tk.END)
    restock_entry.insert(0, "400")
    min_entry.delete(0, tk.END)
    min_entry.insert(0, "5")
    quantmin_entry.delete(0, tk.END)
    quantmin_entry.insert(0, "-1")
    quantmax_entry.delete(0, tk.END)
    quantmax_entry.insert(0, "-1")
    cost_entry.delete(0, tk.END)
    cost_entry.insert(0, "100")
    
    for var in flag_vars.values():
        var.set(0)

def save_configuration():
    config = {
        "nominal": nominal_entry.get(),
        "lifetime": lifetime_entry.get(),
        "restock": restock_entry.get(),
        "min": min_entry.get(),
        "quantmin": quantmin_entry.get(),
        "quantmax": quantmax_entry.get(),
        "cost": cost_entry.get(),
        "flags": {flag: var.get() for flag, var in flag_vars.items()}
    }
    with open("config.json", "w") as f:
        json.dump(config, f)
    messagebox.showinfo("Saved", "Configuration saved successfully.")

def load_configuration():
    try:
        with open("config.json", "r") as f:
            config = json.load(f)
        nominal_entry.delete(0, tk.END)
        nominal_entry.insert(0, config["nominal"])
        lifetime_entry.delete(0, tk.END)
        lifetime_entry.insert(0, config["lifetime"])
        restock_entry.delete(0, tk.END)
        restock_entry.insert(0, config["restock"])
        min_entry.delete(0, tk.END)
        min_entry.insert(0, config["min"])
        quantmin_entry.delete(0, tk.END)
        quantmin_entry.insert(0, config["quantmin"])
        quantmax_entry.delete(0, tk.END)
        quantmax_entry.insert(0, config["quantmax"])
        cost_entry.delete(0, tk.END)
        cost_entry.insert(0, config["cost"])
        for flag, value in config["flags"].items():
            flag_vars[flag].set(value)
        messagebox.showinfo("Loaded", "Configuration loaded successfully.")
    except FileNotFoundError:
        messagebox.showerror("Error", "Configuration file not found.")

# Initialize main Tkinter window
root = tk.Tk()
root.title("XML Generator")
root.geometry("630x700")

# Configure grid layout to center the frame
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)

# Main frame for layout organization
frame = tk.Frame(root, bg=LIGHT_MODE_COLORS["frame_bg"], padx=10, pady=10)
frame.grid(row=0, column=0, padx=1, pady=1, sticky="nsew")

# Center frame and enable expansion
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)

dark_mode_var = tk.BooleanVar(value=False)
# Dark Mode Toggle
dark_mode_toggle = ttk.Checkbutton(frame, text="Dark Mode", variable=dark_mode_var, command=toggle_dark_mode)
dark_mode_toggle.grid(row=0, column=3, sticky="e", padx=5, pady=5)

toggle_dark_mode()

# Input and Output Fields
ttk.Label(frame, text="Input file (list.txt):").grid(row=1, column=0, sticky="w", padx=5, pady=5)
input_file_entry = tk.Entry(frame, width=40)
input_file_entry.grid(row=1, column=1, padx=5, pady=5)
ttk.Button(frame, text="Browse...", command=select_input_file, style="Rounded.TButton").grid(row=1, column=2, padx=5, pady=5)

ttk.Label(frame, text="Output file (output.xml):").grid(row=2, column=0, sticky="w", padx=5, pady=5)
output_file_entry = tk.Entry(frame, width=40)
output_file_entry.grid(row=2, column=1, padx=5, pady=5)
ttk.Button(frame, text="Save As...", command=save_output_file, style="Rounded.TButton").grid(row=2, column=2, padx=5, pady=5)

# Define Attribute Fields
attribute_labels = [
    ("Nominal", "10"),
    ("Lifetime", "86400"),
    ("Restock", "400"),
    ("Min", "5"),
    ("QuantMin", "-1"),
    ("QuantMax", "-1"),
    ("Cost", "100")
]
entries = []

for i, (label_text, default_value) in enumerate(attribute_labels, start=3):
    ttk.Label(frame, text=label_text + ":").grid(row=i, column=0, sticky="w", padx=5, pady=5)
    entry = tk.Entry(frame)
    entry.insert(0, default_value)
    entry.grid(row=i, column=1, padx=5, pady=5)
    entries.append(entry)

nominal_entry, lifetime_entry, restock_entry, min_entry, quantmin_entry, quantmax_entry, cost_entry = entries

# Flags Radio Buttons
flags_frame = ttk.LabelFrame(frame, text="Flags (1 for True, 0 for False)", padding=(10, 10))
flags_frame.grid(row=10, column=0, columnspan=3, padx=5, pady=10, sticky="w")

flag_vars = {
    "count_in_cargo": tk.IntVar(value=0),
    "count_in_hoarder": tk.IntVar(value=0),
    "count_in_map": tk.IntVar(value=1),
    "count_in_player": tk.IntVar(value=0),
    "crafted": tk.IntVar(value=0),
    "deloot": tk.IntVar(value=0)
}

for row, (flag, var) in enumerate(flag_vars.items()):
    ttk.Label(flags_frame, text=flag.replace("_", " ").title()).grid(row=row, column=0, sticky="w", padx=5, pady=5)
    ttk.Radiobutton(flags_frame, text="1", variable=var, value=1).grid(row=row, column=1, padx=5, pady=5)
    ttk.Radiobutton(flags_frame, text="0", variable=var, value=0).grid(row=row, column=2, padx=5, pady=5)

# Functional Buttons
preview_button = ttk.Button(frame, text="Preview XML", command=lambda: generate_xml(preview=True), style="Rounded.TButton")
preview_button.grid(row=12, column=0, padx=10, pady=5)

reset_button = ttk.Button(frame, text="Reset to Defaults", command=reset_to_default, style="Rounded.TButton")
reset_button.grid(row=12, column=1, padx=10, pady=5)

save_config_button = ttk.Button(frame, text="Save Config", command=save_configuration, style="Rounded.TButton")
save_config_button.grid(row=13, column=0, padx=10, pady=5)

load_config_button = ttk.Button(frame, text="Load Config", command=load_configuration, style="Rounded.TButton")
load_config_button.grid(row=13, column=1, padx=10, pady=5)

# Generate button
generate_button = ttk.Button(frame, text="Generate XML", command=generate_xml, style="Rounded.TButton")
generate_button.grid(row=12, column=2, padx=10, pady=5)

# Help Button
help_button = ttk.Button(frame, text="Help", command=show_help, style="Rounded.TButton")
help_button.grid(row=13, column=2, padx=10, pady=5)

root.mainloop()
