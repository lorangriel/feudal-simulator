# -*- coding: utf-8 -*-
"""Main application class for the feudal simulator."""
import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import random
import math
from collections import deque
from typing import Callable

from constants import (
    BORDER_TYPES,
    BORDER_COLORS,
    NEIGHBOR_NONE_STR,
    NEIGHBOR_OTHER_STR,
    MAX_NEIGHBORS,
    JARLDOM_RESOURCE_TYPES,
    SETTLEMENT_TYPES,
    CRAFTSMAN_TYPES,
    BUILDING_TYPES,
    SOLDIER_TYPES,
    ANIMAL_TYPES,
    CHARACTER_TYPES,
    FISH_QUALITY_LEVELS,
    MAX_FISHING_BOATS,
)
from data_manager import load_worlds_from_file, save_worlds_to_file
from node import Node
from utils import (
    roll_dice,
    generate_swedish_village_name,
    generate_character_name,
    ScrollableFrame,
)
from dynamic_map import DynamicMapCanvas
from map_logic import StaticMapLogic
from world_manager import WorldManager

# --------------------------------------------------
# Main Application Class: FeodalSimulator
# --------------------------------------------------
class FeodalSimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("Förläningssimulator - Ingen värld")
        self.root.geometry("1150x800") # Increased size slightly

        self.all_worlds = load_worlds_from_file()
        self.active_world_name = None
        self.world_data = None # Holds the data for the active world
        self.world_manager = WorldManager(self.world_data)
        self.pending_save_callback: Callable[[], None] | None = None

        # --- Styling ---
        self.style = ttk.Style()
        try:
            # Try themed styles first
            self.style.theme_use('clam') # Or 'alt', 'default', 'classic'
        except tk.TclError:
            print("Clam theme not available, using default.")
            self.style.theme_use('default')

        # Configure styles for widgets
        self.style.configure("TLabel", background="#f4f4f4", padding=3, font=('Arial', 10))
        self.style.configure("TButton", padding=5, font=('Arial', 10))
        self.style.configure("Tool.TFrame", background="#eeeeee") # Frame for toolbars
        self.style.configure("Content.TFrame", background="#f4f4f4") # Main content frame bg
        self.style.configure("Treeview", rowheight=25, fieldbackground="white", font=('Arial', 10))
        self.style.configure("Treeview.Heading", font=('Arial', 10, 'bold'), padding=5)
        # Style for neighbor combobox highlighting
        self.style.configure("Highlight.TCombobox", fieldbackground="light green") # Used for existing neighbors
        self.style.configure("BlackWhite.TCombobox", foreground="black", fieldbackground="white") # Default combobox
        self.style.configure("Danger.TButton", foreground="red", font=('Arial', 10, 'bold'))
        self.style.configure("Danger.TCombobox", foreground="red", fieldbackground="white")


        # --- Main Layout ---
        self.main_frame = ttk.Frame(self.root, style="Content.TFrame")
        self.main_frame.pack(fill="both", expand=True)

        # Top Menu Bar Frame
        top_menu_frame = ttk.Frame(self.main_frame, style="Tool.TFrame")
        top_menu_frame.pack(side=tk.TOP, fill="x", pady=(0, 5))
        ttk.Button(top_menu_frame, text="Hantera data", command=self.show_data_menu_view).pack(side=tk.LEFT, padx=5, pady=5)

        # Frame specifically for Map buttons (to dynamically add/remove static/dynamic)
        self.map_button_frame = ttk.Frame(top_menu_frame, style="Tool.TFrame")
        self.map_button_frame.pack(side=tk.LEFT, padx=5, pady=5)
        self.map_mode_base_button = ttk.Button(self.map_button_frame, text="Visa Karta", command=self.show_map_mode_buttons)
        self.map_mode_base_button.pack(side=tk.LEFT)

        # --- Main Panes ---
        # PanedWindow for resizable split
        self.paned_window = tk.PanedWindow(self.main_frame, orient=tk.HORIZONTAL, sashrelief=tk.RAISED, bg="#cccccc", sashwidth=8) # Thicker sash
        self.paned_window.pack(fill="both", expand=True, padx=5, pady=5)

        # Left Frame (for Treeview)
        left_frame = ttk.Frame(self.paned_window, width=350, relief=tk.SUNKEN, borderwidth=1) # Start width, add border
        left_frame.pack(fill="both", expand=True) # Pack is needed for PanedWindow children

        # Treeview scrollbars (Place them correctly relative to the tree)
        tree_vscroll = ttk.Scrollbar(left_frame, orient="vertical")
        tree_hscroll = ttk.Scrollbar(left_frame, orient="horizontal") # Placed under the tree

        # Treeview widget
        self.tree = ttk.Treeview(left_frame, yscrollcommand=tree_vscroll.set, xscrollcommand=tree_hscroll.set, selectmode='browse')

        # Configure scrollbars AFTER tree exists
        tree_vscroll.config(command=self.tree.yview)
        tree_hscroll.config(command=self.tree.xview) # Command for horizontal scrollbar

        # Pack order: vscroll right, hscroll bottom (under tree), tree fills the rest
        tree_vscroll.pack(side=tk.RIGHT, fill="y")
        tree_hscroll.pack(side=tk.BOTTOM, fill="x") # This puts it under the treeview
        self.tree.pack(side=tk.LEFT, fill="both", expand=True) # Tree fills remaining space

        # Treeview setup
        self.tree["columns"] = ("#0",) # Use only the tree column
        self.tree.heading("#0", text="Struktur")
        self.tree.column("#0", width=300, minwidth=200, stretch=tk.YES) # Allow stretching
        self.tree.bind("<Double-1>", self.on_tree_double_click)

        # Add left frame to PanedWindow
        self.paned_window.add(left_frame) # Add weight


        # Right Frame (for details, editors, maps)
        self.right_frame = ttk.Frame(self.paned_window, style="Content.TFrame", width=750, relief=tk.SUNKEN, borderwidth=1)
        self.right_frame.pack(fill="both", expand=True)
        self.paned_window.add(self.right_frame) # Add weight

        # Set initial sash position (approx 1/3)
        self.root.update_idletasks() # Ensure sizes are calculated
        sash_pos = int(self.root.winfo_width() * 0.3)
        try:
            self.paned_window.sash_place(0, sash_pos, 0)
        except tk.TclError:
            pass # Sometimes fails on first launch


        # --- Status Bar ---
        status_frame = ttk.LabelFrame(self.root, text="Status", padding=5)
        status_frame.pack(side=tk.BOTTOM, fill="x", padx=5, pady=5)
        self.status_text = tk.Text(status_frame, height=6, wrap="word", state="disabled", relief=tk.FLAT, bg="#f0f0f0", font=('Arial', 9)) # Smaller font
        status_scroll = ttk.Scrollbar(status_frame, command=self.status_text.yview)
        self.status_text.config(yscrollcommand=status_scroll.set)
        status_scroll.pack(side=tk.RIGHT, fill="y")
        self.status_text.pack(side=tk.LEFT, fill="both", expand=True)

        # --- Map related attributes (initialized later) ---
        self.dynamic_map_view = None
        self.static_map_canvas = None
        self.map_logic = None
        self.static_scale = 1.0
        self.map_static_positions = {} # node_id -> (r, c) in hex grid
        self.map_hex_centers = {} # node_id -> (cx, cy) on canvas
        self.map_hex_tags = {} # (r, c) -> tag string
        self.map_tag_to_nodeid = {} # tag string -> node_id
        self.static_grid_occupied = [] # [r][c] -> node_id or None
        self.static_rows = 35 # Slightly larger grid
        self.static_cols = 35
        self.hex_size = 35 # Default hex size
        self.hex_spacing = 15  # Space between hexagons on static map
        self.hex_size_unconnected_factor = 0.7 # Factor for unconnected hexes
        # For map drag-and-drop
        self.map_drag_start_node_id = None
        self.map_drag_start_coords = None
        self.map_drag_line_id = None
        self.map_active_node_tag = None  # To potentially highlight hovered hex

        # --- Initial View ---
        self.show_no_world_view() # Show placeholder in right frame

        # Auto-load world file if only one world exists
        if len(self.all_worlds) == 1:
            only_world = next(iter(self.all_worlds))
            try:
                self.load_world(only_world)
            except Exception as e:
                print(f"Failed to auto-load world '{only_world}': {e}")

    @staticmethod
    def calculate_population_from_fields(data: dict) -> int:
        """Compute total population from category fields."""
        try:
            free_p = int(data.get("free_peasants", 0) or 0)
            unfree_p = int(data.get("unfree_peasants", 0) or 0)
            thralls = int(data.get("thralls", 0) or 0)
            burghers = int(data.get("burghers", 0) or 0)
        except ValueError:
            free_p = unfree_p = thralls = burghers = 0
        total = free_p + unfree_p + thralls + burghers
        if total:
            return total
        try:
            return int(data.get("population", 0) or 0)
        except ValueError:
            return 0

    # --- Status Methods ---
    def add_status_message(self, msg):
        """Adds a message to the status bar."""
        try:
            self.status_text.config(state="normal")
            self.status_text.insert("end", msg + "\n")
            self.status_text.see("end") # Scroll to the end
            self.status_text.config(state="disabled")
        except tk.TclError as e:
            print(f"Error adding status message: {e}") # Handle cases where widget might be destroyed

    # --- World Data Handling ---
    def save_current_world(self):
        """Saves the currently active world data back to the main dictionary and file."""
        if self.active_world_name and self.world_data:
            self.all_worlds[self.active_world_name] = self.world_data
            save_worlds_to_file(self.all_worlds)
            self.refresh_dynamic_map()
            # No status message here, usually called from other actions that add status
        #else:
        #    print("Warning: Tried to save world, but no active world or data.")

    def commit_pending_changes(self):
        """If an editor save callback is pending, call it before switching views."""
        if self.pending_save_callback:
            try:
                self.pending_save_callback()
            finally:
                self.pending_save_callback = None


    def _clear_right_frame(self):
        """Destroys all widgets in the right frame."""
        # Important: Unbind map drag events if map exists
        if self.static_map_canvas:
            self.static_map_canvas.unbind("<Motion>")  # For hover effects if added
            self.static_map_canvas = None  # Clear reference

        for widget in self.right_frame.winfo_children():
            widget.destroy()
        self.map_drag_start_node_id = None  # Reset drag state
        self.map_drag_line_id = None
        self.hex_drag_node_id = None
        self.hex_drag_start = None


    def show_no_world_view(self):
        """Displays a placeholder when no world is loaded or no node is selected."""
        self.commit_pending_changes()
        self._clear_right_frame()
        label_text = "Ingen värld är aktiv.\n\nAnvänd 'Hantera data' för att skapa eller ladda en värld."
        if self.active_world_name:
            label_text = f"Aktiv värld: {self.active_world_name}\n\nDubbelklicka på en nod i trädet till vänster för att redigera den."

        lbl = ttk.Label(self.right_frame, text=label_text, justify=tk.CENTER, font=("Arial", 12), anchor="center")
        # Pack label to center it
        lbl.pack(expand=True, fill="both")


    # --- Treeview State Handling ---
    def store_tree_state(self):
        """Stores the open/closed state and selection of tree items."""
        if not self.tree.winfo_exists(): return set(), () # Handle widget destroyed case
        open_items = set()
        def gather_open(item_id):
            try:
                if self.tree.item(item_id, 'open'):
                    open_items.add(item_id)
                for child_id in self.tree.get_children(item_id):
                    gather_open(child_id)
            except tk.TclError: pass # Item might not exist anymore

        for top_item_id in self.tree.get_children():
            gather_open(top_item_id)

        selection = self.tree.selection()
        return open_items, selection

    def restore_tree_state(self, open_items, selection):
        """Restores the open/closed state and selection of tree items."""
        if not self.tree.winfo_exists(): return # Handle widget destroyed case
        def apply_state(item_id):
            try:
                if self.tree.exists(item_id): # Check if item still exists
                    if item_id in open_items:
                        self.tree.item(item_id, open=True)
                    else:
                        self.tree.item(item_id, open=False) # Ensure closed if not in set
                    for child_id in self.tree.get_children(item_id):
                        apply_state(child_id)
            except tk.TclError: pass # Item might have been deleted during refresh

        for top_item_id in self.tree.get_children():
            apply_state(top_item_id)

        if selection:
            try:
                # Filter selection to only include existing items
                valid_selection = tuple(s for s in selection if self.tree.exists(s))
                if valid_selection:
                    self.tree.selection_set(valid_selection) # Set selection
                    self.tree.focus(valid_selection[0]) # Focus on the first selected item
                    self.tree.see(valid_selection[0]) # Ensure it's visible
            except tk.TclError:
                print("Warning: Could not fully restore tree selection (items might have changed).")


    # --- Data Management Menus ---
    def show_data_menu_view(self):
        """Displays the main data management menu."""
        self._clear_right_frame()
        container = ttk.Frame(self.right_frame)
        container.pack(expand=True) # Center the buttons

        ttk.Label(container, text="Hantera data", font=("Arial", 16, "bold")).pack(pady=(10, 20))
        ttk.Button(container, text="Hantera Världar", command=self.show_manage_worlds_view, width=20).pack(pady=5)
        ttk.Button(container, text="Hantera Karaktärer", command=self.show_manage_characters_view, width=20).pack(pady=5)
        ttk.Separator(container, orient=tk.HORIZONTAL).pack(fill='x', pady=15, padx=20)
        ttk.Button(container, text="< Tillbaka", command=self.show_no_world_view, width=20).pack(pady=5)

    def show_manage_worlds_view(self):
        """Displays the UI for managing worlds (create, load, delete, copy)."""
        self._clear_right_frame()
        container = ttk.Frame(self.right_frame)
        container.pack(expand=True, fill='y', pady=20)

        ttk.Label(container, text="Hantera världar", font=("Arial", 14)).pack(pady=5)

        # Frame for listbox and scrollbar
        list_frame = ttk.Frame(container)
        list_frame.pack(pady=10, fill='x', padx=20)

        world_listbox = tk.Listbox(list_frame, height=10, exportselection=False, font=('Arial', 10))
        list_scroll = ttk.Scrollbar(list_frame, orient="vertical", command=world_listbox.yview)
        world_listbox.config(yscrollcommand=list_scroll.set)

        list_scroll.pack(side=tk.RIGHT, fill='y')
        world_listbox.pack(side=tk.LEFT, fill='x', expand=True)


        # Populate listbox
        self.all_worlds = load_worlds_from_file() # Ensure latest data
        world_listbox.delete(0, tk.END) # Clear previous entries
        for wname in sorted(self.all_worlds.keys()):
            world_listbox.insert(tk.END, wname)
            if wname == self.active_world_name:
                idx = world_listbox.size() - 1
                world_listbox.itemconfig(idx, {'bg':'#aaddff'}) # Highlight active slightly darker
                world_listbox.selection_set(idx) # Select active

        # --- Actions ---
        def do_load():
            selection = world_listbox.curselection()
            if selection:
                wname = world_listbox.get(selection[0])
                self.load_world(wname)
                # self.show_no_world_view() # Go back after loading? Or stay in manage view? Stay for now.
                self.show_manage_worlds_view() # Refresh view to show highlight

        def do_delete():
            selection = world_listbox.curselection()
            if selection:
                wname = world_listbox.get(selection[0])
                if messagebox.askyesno("Radera Värld?", f"Är du säker på att du vill radera världen '{wname}'?\nDetta kan inte ångras.", icon='warning', parent=self.root):
                    if wname in self.all_worlds:
                        del self.all_worlds[wname]
                        save_worlds_to_file(self.all_worlds)
                        # world_listbox.delete(selection[0]) # Let refresh handle delete
                        self.add_status_message(f"Värld '{wname}' raderad.")
                        if self.active_world_name == wname:
                            self.active_world_name = None
                            self.world_data = None
                            self.root.title("Förläningssimulator - Ingen värld")
                            if self.tree.winfo_exists(): self.tree.delete(*self.tree.get_children()) # Clear tree
                            self.show_no_world_view() # Update display if active world deleted
                        self.show_manage_worlds_view() # Refresh list
                    else:
                        messagebox.showerror("Fel", f"Kunde inte hitta världen '{wname}' att radera.", parent=self.root)
                        self.show_manage_worlds_view() # Refresh list anyway


        def do_copy():
            selection = world_listbox.curselection()
            if selection:
                wname_to_copy = world_listbox.get(selection[0])
                new_name = simpledialog.askstring("Kopiera Värld", f"Ange ett namn för kopian av '{wname_to_copy}':", parent=self.root)
                if new_name:
                    new_name = new_name.strip()
                    if not new_name:
                        messagebox.showwarning("Ogiltigt Namn", "Namnet på kopian får inte vara tomt.", parent=self.root)
                        return
                    if new_name == wname_to_copy:
                        messagebox.showwarning("Ogiltigt Namn", "Kopian måste ha ett annat namn än originalet.", parent=self.root)
                        return
                    if new_name in self.all_worlds:
                        messagebox.showerror("Namnkonflikt", f"En värld med namnet '{new_name}' finns redan.", parent=self.root)
                        return
                    # Deep copy the world data
                    import copy
                    if wname_to_copy in self.all_worlds:
                        self.all_worlds[new_name] = copy.deepcopy(self.all_worlds[wname_to_copy])
                        save_worlds_to_file(self.all_worlds)
                        # world_listbox.insert(tk.END, new_name) # Let refresh handle insert
                        self.add_status_message(f"Kopierade världen '{wname_to_copy}' till '{new_name}'.")
                        self.show_manage_worlds_view() # Refresh list
                    else:
                        messagebox.showerror("Fel", f"Kunde inte hitta originalvärlden '{wname_to_copy}' att kopiera.", parent=self.root)


        def do_create():
            self.create_new_world()
            # Refresh this view to show the new world
            self.show_manage_worlds_view()


        # Button Frame
        button_frame = ttk.Frame(container)
        button_frame.pack(pady=10)
        ttk.Button(button_frame, text="Skapa ny", command=do_create).grid(row=0, column=0, padx=5, pady=2)
        ttk.Button(button_frame, text="Ladda vald", command=do_load).grid(row=0, column=1, padx=5, pady=2)
        ttk.Button(button_frame, text="Kopiera vald", command=do_copy).grid(row=1, column=0, padx=5, pady=2)
        ttk.Button(button_frame, text="Radera vald", command=do_delete, style="Danger.TButton").grid(row=1, column=1, padx=5, pady=2)
        ttk.Button(button_frame, text="Skapa Drunok", command=self.create_drunok_world).grid(row=2, column=0, columnspan=2, pady=(10,2))


        # Back Button
        ttk.Button(container, text="< Tillbaka", command=self.show_data_menu_view).pack(pady=(15, 5))

    def create_new_world(self):
        """Prompts for a name and creates a new empty world."""
        wname = simpledialog.askstring("Ny Värld", "Ange namn på den nya världen:", parent=self.root)
        if not wname:
            return
        wname = wname.strip()
        if not wname:
            messagebox.showwarning("Ogiltigt Namn", "Namnet på världen får inte vara tomt.", parent=self.root)
            return

        if wname in self.all_worlds:
            messagebox.showerror("Namnkonflikt", f"En värld med namnet '{wname}' finns redan.", parent=self.root)
            return

        # Basic world structure with a root node
        new_data = {
            "nodes": {},
            "next_node_id": 1,
            "characters": {}
        }
        root_id = new_data["next_node_id"]
        # node IDs must be strings in the dictionary keys
        new_data["nodes"][str(root_id)] = {
            "node_id": root_id, # Store int ID also inside node
            "parent_id": None, # Root node has no parent
            "name": "Kungarike", # Default name for root
            "custom_name": wname, # Use world name as custom name for root
            "population": 0,
            "ruler_id": None,
            "num_subfiefs": 0,
            "children": []
        }
        new_data["next_node_id"] += 1 # Increment for the next node

        self.all_worlds[wname] = new_data
        save_worlds_to_file(self.all_worlds)

        # Optionally load the new world immediately
        self.load_world(wname)
        self.add_status_message(f"Värld '{wname}' skapad och laddad.")

    def create_drunok_world(self):
        """Create the predefined world 'Drunok' with fixed hierarchy."""
        wname = "Drunok"
        if wname in self.all_worlds:
            if not messagebox.askyesno(
                "Överskriv?",
                f"Världen '{wname}' finns redan. Vill du ersätta den?",
                parent=self.root,
            ):
                return

        new_data = {"nodes": {}, "next_node_id": 1, "characters": {}}

        def add_node(parent_id, name, custom_name="", num_subfiefs=0):
            nid = new_data["next_node_id"]
            new_data["nodes"][str(nid)] = {
                "node_id": nid,
                "parent_id": parent_id,
                "name": name,
                "custom_name": custom_name,
                "population": 0,
                "ruler_id": None,
                "num_subfiefs": num_subfiefs,
                "children": [],
            }
            new_data["next_node_id"] += 1
            if parent_id is not None:
                new_data["nodes"][str(parent_id)]["children"].append(nid)
            return nid

        root_id = add_node(None, "Kungarike", wname)

        structure = {
            "Kintikla": [
                ("Lugdum", 12),
                ("Rhonum", 15),
                ("Dimveden", 8),
                ("Altona", 9),
            ],
            "Val Pavane": [
                ("Iltariet", 50),
                ("Durum", 22),
                ("Angird", 24),
                ("Talarra", 26),
            ],
            "Pavara": [
                ("Val Timan", 7),
                ("Arlons Kronomarker", 19),
                ("Ramdors fallna marker", 2),
            ],
            "Valo": [
                ("Val Ordos", 14),
                ("Valdus", 8),
                ("Nanar", 8),
                ("Namira", 8),
            ],
        }

        world_manager = WorldManager(new_data)

        for principality, duchies in structure.items():
            fid = add_node(root_id, "Furstendöme", principality)
            for duchy_name, jarldom_count in duchies:
                did = add_node(fid, "Hertigdöme", duchy_name, jarldom_count)
                world_manager.update_subfiefs_for_node(new_data["nodes"][str(did)])

        self.all_worlds[wname] = new_data
        save_worlds_to_file(self.all_worlds)

        self.load_world(wname)
        self.add_status_message("Förinställd värld 'Drunok' skapad och laddad.")

    def load_world(self, wname):
        """Loads the specified world and populates the tree."""
        if wname not in self.all_worlds:
            messagebox.showerror("Fel", f"Världen '{wname}' kunde inte hittas.", parent=self.root)
            return

        self.active_world_name = wname
        # Make a deep copy to avoid modifying the master dict inadvertently before saving
        import copy
        self.world_data = copy.deepcopy(self.all_worlds[wname])
        self.world_manager.set_world_data(self.world_data)

        # --- Data Validation and Initialization on Load ---
        nodes_updated, chars_updated = self.world_manager.validate_world_data()
        if nodes_updated > 0 or chars_updated > 0:
            self.add_status_message(
                f"Validerade och uppdaterade data vid laddning: {nodes_updated} noder, {chars_updated} karaktärer."
            )
            self.save_current_world()

        # Ensure population totals are consistent upon load
        self.world_manager.update_population_totals()

        # Load any saved static map positions
        self.load_static_positions()


        self.root.title(f"Förläningssimulator - {wname}")
        self.populate_tree()
        self.show_no_world_view() # Clear right panel initially
        self._auto_select_single_root()
        self.add_status_message(f"Värld '{wname}' laddad.")
        # Reset map buttons
        self.hide_map_mode_buttons()


    # --- Treeview Population and Interaction ---
    def populate_tree(self):
        """Clears and refills the treeview based on the current world_data."""
        if not self.tree.winfo_exists(): return # Check if tree exists

        open_state, selection = self.store_tree_state() # Store state before clearing
        self.tree.delete(*self.tree.get_children()) # Clear existing items

        if not self.world_data or not self.world_data.get("nodes"):
            # self.add_status_message("Kan inte fylla trädet: Ingen världsdata eller inga noder.")
            return

        # Find the root node(s) (parent_id is None)
        root_nodes_data = []
        node_dict = self.world_data.get("nodes", {})
        all_node_ids_in_dict = {int(k) for k in node_dict.keys() if k.isdigit()}

        for node_id_int in all_node_ids_in_dict:
            node_data = node_dict.get(str(node_id_int))
            if node_data and node_data.get("parent_id") is None:
                # Ensure node_id is present in the data itself and matches key
                if node_data.get("node_id") != node_id_int: node_data["node_id"] = node_id_int
                root_nodes_data.append(node_data)

        if not root_nodes_data:
            # Try finding nodes with parent_id pointing outside the known set (potential orphans as roots)
            for node_id_int in all_node_ids_in_dict:
                node_data = node_dict.get(str(node_id_int))
                parent_id = node_data.get("parent_id")
                if node_data and parent_id is not None and parent_id not in all_node_ids_in_dict:
                    print(f"Warning: Node {node_id_int} has parent {parent_id} not in dataset. Treating as root.")
                    node_data["parent_id"] = None # Fix orphan state
                    if node_data.get("node_id") != node_id_int: node_data["node_id"] = node_id_int
                    root_nodes_data.append(node_data)

        if not root_nodes_data:
            self.add_status_message("Fel: Ingen rotnod (med parent_id=null eller ogiltigt parent_id) hittades.")
            return
        elif len(root_nodes_data) > 1:
            self.add_status_message(f"Varning: Flera ({len(root_nodes_data)}) rotnoder hittades. Visar alla.")

        # Sort roots by ID for consistency.
        root_nodes_data.sort(key=lambda n: n.get("node_id", 0))

        # Recursively add nodes starting from the root(s)
        for root_node in root_nodes_data:
            self._add_tree_node_recursive("", root_node)

        # Restore previous open/selection state
        self.restore_tree_state(open_state, selection)

        # Ensure the main view is cleared after populating if no selection restored
        if not self.tree.selection():
            self.show_no_world_view()


    def _add_tree_node_recursive(self, parent_iid, node_data):
        """Helper function to recursively add nodes to the treeview."""
        node_id = node_data.get("node_id")
        if node_id is None:
            print(f"Warning: Skipping node data without node_id: {node_data}")
            return # Skip nodes without ID

        node_id_str = str(node_id)
        # Prevent adding duplicates if tree logic somehow allows it
        if self.tree.exists(node_id_str):
            # print(f"Debug: Node {node_id_str} already exists in tree, skipping add.")
            return

        depth = self.get_depth_of_node(node_id)
        display_name = self.get_display_name_for_node(node_data, depth)

        # Insert item into tree
        try:
            # Add tags for potential styling based on depth or type later
            tags = (f"depth_{depth}",)
            my_iid = self.tree.insert(parent_iid, "end", iid=node_id_str, text=display_name, open=(depth < 1), tags=tags) # Open only root initially
        except tk.TclError as e:
            print(f"Warning: Failed to insert node {node_id_str} ('{display_name}') into tree. Error: {e}")
            return # Skip this node and its children if insert fails


        # Add children recursively
        children_ids = node_data.get("children", [])
        if children_ids:
            # Optional: Sort children, e.g., by name or ID
            child_nodes = []
            valid_children_ids = []
            for cid in children_ids:
                child_data = self.world_data.get("nodes", {}).get(str(cid))
                if child_data:
                    # Ensure node_id consistency
                    if child_data.get("node_id") != cid: child_data["node_id"] = cid
                    child_nodes.append(child_data)
                    valid_children_ids.append(cid)
                else:
                    print(f"Warning: Child ID {cid} listed in parent {node_id} not found in nodes data.")

            # Correct children list in parent if discrepancies found
            if node_data.get("children") != valid_children_ids:
                print(f"Correcting children list for node {node_id}")
                node_data["children"] = valid_children_ids


            # Sort children by their display name for consistent order
            child_nodes.sort(key=lambda n: self.get_display_name_for_node(n, depth + 1))

            for child_data in child_nodes:
                self._add_tree_node_recursive(my_iid, child_data)

    def _auto_select_single_root(self):
        """If there is only one root node, select and open it."""
        if not self.tree.winfo_exists():
            return
        roots = self.tree.get_children("")
        if len(roots) == 1:
            root_iid = roots[0]
            self.tree.selection_set(root_iid)
            self.tree.focus(root_iid)
            node_data = self.world_data.get("nodes", {}).get(root_iid)
            if node_data:
                self.show_node_view(node_data)


    def get_display_name_for_node(self, node_data, depth):
        """Return a readable name for a node at the given depth."""
        return self.world_manager.get_display_name_for_node(node_data, depth)


    def get_depth_of_node(self, node_id):
        """Calculates the depth of a node in the hierarchy (0 for root)."""
        return self.world_manager.get_depth_of_node(node_id)

    def clear_depth_cache(self):
        """Clears the node depth cache, needed when hierarchy changes."""
        self.world_manager.clear_depth_cache()


    def on_tree_double_click(self, event):
        """Handles double-clicking on an item in the treeview."""
        item_id_str = self.tree.focus() # Get the IID of the focused item
        if not item_id_str or not self.world_data:
            return

        # Check if item exists before trying to access data
        if not self.tree.exists(item_id_str):
            self.add_status_message(f"Fel: Trädnod ID {item_id_str} finns inte längre.")
            return

        node_data = self.world_data.get("nodes", {}).get(item_id_str)
        if node_data:
            self.show_node_view(node_data)
        else:
            self.add_status_message(f"Fel: Kunde inte hitta data för nod ID {item_id_str}")

    def refresh_tree_item(self, node_id):
        """Updates the text of a specific item in the tree."""
        if not self.tree.winfo_exists(): return # Check if tree exists

        node_id_str = str(node_id)
        if self.tree.exists(node_id_str):
            node_data = self.world_data.get("nodes", {}).get(node_id_str)
            if node_data:
                # Recalculate depth as it might affect display name
                depth = self.get_depth_of_node(node_id)
                display_name = self.get_display_name_for_node(node_data, depth)
                try:
                    self.tree.item(node_id_str, text=display_name)
                except tk.TclError as e:
                    print(f"Error refreshing tree item {node_id_str}: {e}")


    # --- Character Management ---
    def show_manage_characters_view(self):
        """Displays the UI for managing characters (karaktärer)."""
        if not self.active_world_name:
            messagebox.showinfo(
                "Ingen Värld",
                "Ladda en värld först för att hantera karaktärer.",
                parent=self.root,
            )
            return

        self._clear_right_frame()
        container = ttk.Frame(self.right_frame)
        container.pack(expand=True, fill='y', pady=20)

        ttk.Label(container, text="Hantera Karaktärer", font=("Arial", 14)).pack(pady=5)

        # Ensure characters structure exists
        if "characters" not in self.world_data:
            self.world_data["characters"] = {}

        # Frame for listbox and scrollbar
        list_frame = ttk.Frame(container)
        list_frame.pack(pady=10, fill='x', padx=20)

        char_listbox = tk.Listbox(list_frame, height=10, exportselection=False, font=('Arial', 10))
        list_scroll = ttk.Scrollbar(list_frame, orient="vertical", command=char_listbox.yview)
        char_listbox.config(yscrollcommand=list_scroll.set)

        list_scroll.pack(side=tk.RIGHT, fill='y')
        char_listbox.pack(side=tk.LEFT, fill='x', expand=True)

        # Populate listbox - sort by name for easier finding
        char_listbox.delete(0, tk.END) # Clear previous entries
        sorted_chars = sorted(self.world_data.get("characters", {}).items(), key=lambda item: item[1].get('name', '').lower())
        char_id_map = {} # Map listbox index to char_id
        for idx, (char_id_str, data) in enumerate(sorted_chars):
            display_text = f"{data.get('name', 'Namnlös')} (ID: {char_id_str})"
            char_listbox.insert(tk.END, display_text)
            char_id_map[idx] = char_id_str # Store ID as string

        # --- Actions ---
        def get_selected_char_id():
            selection = char_listbox.curselection()
            if selection:
                list_index = selection[0]
                return char_id_map.get(list_index)
            return None

        def do_new():
            # Pass None for char_data, indicating it's new
            self.show_edit_character_view(None, is_new=True)

        def do_edit():
            char_id_str = get_selected_char_id()
            if char_id_str:
                char_data = self.world_data.get("characters",{}).get(char_id_str)
                if char_data:
                    # Pass the actual character data dictionary
                    self.show_edit_character_view(char_data, is_new=False)
                else:
                    messagebox.showerror(
                        "Fel",
                        f"Kunde inte hitta data för karaktär ID {char_id_str}",
                        parent=self.root,
                    )
            else:
                messagebox.showinfo(
                    "Inget Val",
                    "Välj en karaktär i listan att redigera.",
                    parent=self.root,
                )


        def do_delete():
            char_id_to_delete_str = get_selected_char_id()
            if not char_id_to_delete_str:
                messagebox.showinfo(
                    "Inget Val",
                    "Välj en karaktär i listan att radera.",
                    parent=self.root,
                )
                return

            char_name = self.world_data.get("characters", {}).get(char_id_to_delete_str, {}).get('name', f'ID {char_id_to_delete_str}')

            # Check if character rules any nodes
            ruled_nodes_info = []
            nodes_to_update = []
            if self.world_data and "nodes" in self.world_data:
                for node_id_str, node_data in self.world_data["nodes"].items():
                    # Compare ruler_id (might be int or str) with char_id_to_delete (which is str)
                    if str(node_data.get("ruler_id")) == char_id_to_delete_str:
                        try:
                            depth = self.get_depth_of_node(int(node_id_str))
                            display_name = self.get_display_name_for_node(node_data, depth)
                            ruled_nodes_info.append(f"- {display_name}")
                            nodes_to_update.append(node_id_str)
                        except ValueError: continue # Skip if node_id is not int

            confirm_message = (
                f"Är du säker på att du vill radera karaktären '{char_name}' (ID: {char_id_to_delete_str})?"
            )
            if ruled_nodes_info:
                confirm_message += "\n\nDenna karaktär styr för närvarande:\n" + "\n".join(ruled_nodes_info[:5])
                if len(ruled_nodes_info) > 5: confirm_message += "\n- ..."
                confirm_message += "\n\nOm du raderar karaktären kommer dessa förläningar att bli utan härskare."

            if messagebox.askyesno("Radera Karaktär?", confirm_message, icon='warning', parent=self.root):
                nodes_updated_count = 0
                # Remove ruler_id from nodes
                for node_id_str_update in nodes_to_update:
                    node_to_update = self.world_data.get("nodes", {}).get(node_id_str_update)
                    if node_to_update:
                        node_to_update["ruler_id"] = None
                        nodes_updated_count += 1
                        # Refresh tree item visually if tree exists
                        if self.tree.winfo_exists() and self.tree.exists(node_id_str_update):
                            self.refresh_tree_item(int(node_id_str_update))


                # Delete character data
                if char_id_to_delete_str in self.world_data.get("characters", {}):
                    del self.world_data["characters"][char_id_to_delete_str]
                    self.save_current_world()
                    self.add_status_message(
                        f"Karaktär '{char_name}' (ID: {char_id_to_delete_str}) raderad. {nodes_updated_count} förläning(ar) uppdaterades."
                    )
                    # Refresh the list view
                    self.show_manage_characters_view()
                else:
                    messagebox.showerror(
                        "Fel",
                        f"Kunde inte radera, karaktär med ID {char_id_to_delete_str} hittades ej (kanske redan raderad?).",
                        parent=self.root,
                    )
                    self.show_manage_characters_view() # Refresh anyway


        # Button Frame
        button_frame = ttk.Frame(container)
        button_frame.pack(pady=10)
        ttk.Button(button_frame, text="Ny karaktär", command=do_new).grid(row=0, column=0, padx=5, pady=2)
        ttk.Button(button_frame, text="Redigera vald", command=do_edit).grid(row=0, column=1, padx=5, pady=2)
        ttk.Button(button_frame, text="Radera vald", command=do_delete, style="Danger.TButton").grid(row=1, column=0, columnspan=2, padx=5, pady=2)

        # Back Button
        ttk.Button(container, text="< Tillbaka", command=self.show_data_menu_view).pack(pady=(15, 5))


    def show_edit_character_view(self, char_data, is_new=False, parent_node_data=None):
        """Shows the form to create or edit a character. char_data is the dict or None if new."""
        self._clear_right_frame()
        container = ttk.Frame(self.right_frame, padding="10 10 10 10")
        container.pack(expand=True, pady=20, padx=20, fill='both') # Fill frame

        char_id = char_data.get("char_id") if char_data and not is_new else None # Get existing ID only if editing
        title = "Skapa Ny Karaktär" if is_new else f"Redigera Karaktär (ID: {char_id})"
        ttk.Label(container, text=title, font=("Arial", 14)).pack(pady=(5, 15))

        # Use a frame for the form elements for better alignment
        form_frame = ttk.Frame(container)
        form_frame.pack(fill='x')

        # --- Form Fields ---
        # Name
        ttk.Label(form_frame, text="Namn:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        default_name = generate_character_name()
        name_var = tk.StringVar(
            value=char_data.get("name", default_name) if char_data else default_name
        )
        name_entry = ttk.Entry(form_frame, textvariable=name_var, width=40)
        name_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        name_entry.focus() # Set focus to name field

        # Wealth (Example - Currently unused field)
        ttk.Label(form_frame, text="Förmögenhet:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        wealth_var = tk.StringVar(value=str(char_data.get("wealth", 0) if char_data else 0))
        wealth_spinbox = tk.Spinbox(form_frame, from_=0, to=1000000, textvariable=wealth_var, width=10)
        wealth_spinbox.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        # Description (Example - Currently unused field)
        ttk.Label(form_frame, text="Beskrivning:").grid(row=2, column=0, padx=5, pady=5, sticky="nw")
        desc_text_frame = ttk.Frame(form_frame) # Frame for text and scrollbar
        desc_text_frame.grid(row=2, column=1, padx=5, pady=5, sticky="ewns")
        desc_text_frame.grid_rowconfigure(0, weight=1)
        desc_text_frame.grid_columnconfigure(0, weight=1)
        desc_text = tk.Text(desc_text_frame, height=4, width=40, wrap="word", relief=tk.SUNKEN, borderwidth=1, font=('Arial', 10))
        desc_text.grid(row=0, column=0, sticky="nsew")
        desc_text.insert("1.0", char_data.get("description", "") if char_data else "")
        # Add scrollbar for description
        desc_scroll = ttk.Scrollbar(desc_text_frame, orient="vertical", command=desc_text.yview)
        desc_scroll.grid(row=0, column=1, sticky="ns")
        desc_text.config(yscrollcommand=desc_scroll.set)


        # Skills - presented as up to 9 dropdown rows with dynamic add/remove
        ttk.Label(form_frame, text="F\u00e4rdigheter:").grid(row=3, column=0, padx=5, pady=5, sticky="nw")
        skills_frame = ttk.Frame(form_frame)
        skills_frame.grid(row=3, column=1, padx=5, pady=5, sticky="w")

        none_skill = "Ingen skill"
        skill_choices = [f"Skill #{i}" for i in range(1, 10)]
        skill_vars: list[tk.StringVar] = []
        level_vars: list[tk.StringVar] = []

        level_choices = []
        for i in range(1, 7):
            level_choices.append(str(i))
            for j in range(1, 4):
                level_choices.append(f"{i}+{j}")
        level_choices.append("7")

        def on_skill_change(*_):
            has_empty = any(v.get() == none_skill for v in skill_vars)
            if not has_empty and len(skill_vars) < 9:
                add_skill_var()
            render_skill_rows()

        def add_skill_var(skill: str = none_skill, level: str = "1") -> None:
            svar = tk.StringVar(value=skill)
            lvar = tk.StringVar(value=level)
            svar.trace_add("write", on_skill_change)
            skill_vars.append(svar)
            level_vars.append(lvar)

        def delete_skill_row(idx: int) -> None:
            if 0 <= idx < len(skill_vars):
                skill_vars.pop(idx)
                level_vars.pop(idx)
                if not skill_vars:
                    add_skill_var()
                render_skill_rows()

        def render_skill_rows() -> None:
            for widget in skills_frame.winfo_children():
                widget.destroy()
            selected = {v.get() for v in skill_vars if v.get() != none_skill}
            for i, (svar, lvar) in enumerate(zip(skill_vars, level_vars)):
                options = [none_skill] + [ch for ch in skill_choices if ch == svar.get() or ch not in selected]
                combo = ttk.Combobox(
                    skills_frame,
                    textvariable=svar,
                    values=options,
                    state="readonly",
                    width=20,
                )
                combo.grid(row=i, column=0, padx=2, pady=2, sticky="w")
                level_combo = ttk.Combobox(
                    skills_frame,
                    textvariable=lvar,
                    values=level_choices,
                    state="readonly",
                    width=6,
                )
                level_combo.grid(row=i, column=1, padx=2, pady=2, sticky="w")
                ttk.Button(
                    skills_frame,
                    text="Radera",
                    command=lambda idx=i: delete_skill_row(idx),
                ).grid(row=i, column=2, padx=2, pady=2)

        existing_skills = char_data.get("skills", []) if char_data else []
        for s in existing_skills[:9]:
            if isinstance(s, dict):
                add_skill_var(s.get("name", none_skill), s.get("level", "1"))
            else:
                add_skill_var(str(s), "1")
        if not skill_vars or (len(skill_vars) < 9 and all(v.get() != none_skill for v in skill_vars)):
            add_skill_var()
        render_skill_rows()

        ttk.Label(form_frame, text="Typ:").grid(row=4, column=0, padx=5, pady=5, sticky="w")
        type_var = tk.StringVar(value=char_data.get("type", "") if char_data else "")
        type_combo = ttk.Combobox(form_frame, textvariable=type_var, values=list(CHARACTER_TYPES), state="readonly", width=30)
        type_combo.grid(row=4, column=1, padx=5, pady=5, sticky="w")

        ttk.Label(form_frame, text="Jarld\u00f6me:").grid(row=5, column=0, padx=5, pady=5, sticky="w")
        ruler_var = tk.StringVar()
        jarldom_options = []
        if self.world_data and "nodes" in self.world_data:
            jarldoms = []
            for nid_str, n in self.world_data["nodes"].items():
                try:
                    nid = int(nid_str)
                except ValueError:
                    continue
                if self.get_depth_of_node(nid) == 3:
                    name = n.get("custom_name", f"Jarld\u00f6me {nid}")
                    jarldoms.append((nid, name))
            jarldoms.sort(key=lambda j: j[1].lower())
            jarldom_options = [f"{jid}: {name}" for jid, name in jarldoms]
        if char_data and char_data.get("ruler_of") is not None:
            rid = char_data["ruler_of"]
            for opt in jarldom_options:
                if opt.startswith(f"{rid}:"):
                    ruler_var.set(opt)
                    break
        ruler_combo = ttk.Combobox(form_frame, textvariable=ruler_var, values=jarldom_options, state="readonly", width=40)
        ruler_combo.grid(row=5, column=1, padx=5, pady=5, sticky="w")

        def refresh_ruler_visibility(*_):
            if type_var.get() == "H\u00e4rskare":
                ruler_combo.grid()
            else:
                ruler_combo.grid_remove()
                ruler_var.set("")

        type_var.trace_add("write", refresh_ruler_visibility)
        refresh_ruler_visibility()


        # Make the entry column expand
        form_frame.grid_columnconfigure(1, weight=1)
        form_frame.grid_rowconfigure(2, weight=1) # Allow description text box to expand vertically slightly


        # --- Save Action ---
        def do_save():
            name = name_var.get().strip()
            if not name:
                messagebox.showwarning(
                    "Namn Saknas",
                    "Karaktären måste ha ett namn.",
                    parent=self.root,
                )
                name_entry.focus()
                return

            # Validate wealth
            try:
                wealth = int(wealth_var.get() or "0", 10)
            except (tk.TclError, ValueError):
                wealth = 0

            description = desc_text.get("1.0", tk.END).strip()
            skills = [
                {"name": s.get(), "level": l.get()}
                for s, l in zip(skill_vars, level_vars)
                if s.get() != none_skill
            ]
            type_val = type_var.get().strip()
            ruler_of = None
            if type_val == "Härskare" and ruler_var.get():
                try:
                    ruler_of = int(ruler_var.get().split(":")[0])
                except ValueError:
                    ruler_of = None

            if is_new:
                # Find next available character ID (ensure thread-safety if ever needed)
                existing_ids = []
                if self.world_data and "characters" in self.world_data:
                    for k in self.world_data["characters"].keys():
                            try: existing_ids.append(int(k))
                            except ValueError: pass
                new_id = max(existing_ids) + 1 if existing_ids else 1
                new_id_str = str(new_id)

                new_char_data = {
                    "char_id": new_id, # Store ID also inside the dict
                    "name": name,
                    "wealth": wealth,
                    "description": description,
                    "skills": skills,
                    "type": type_val,
                    "ruler_of": ruler_of,
                }
                self.world_data.setdefault("characters", {})[new_id_str] = new_char_data
                self.add_status_message(
                    f"Skapade ny karaktär: '{name}' (ID: {new_id})."
                )

                if ruler_of is not None:
                    jnode = self.world_data.get("nodes", {}).get(str(ruler_of))
                    if jnode is not None:
                        jnode["ruler_id"] = new_id_str
                        self.refresh_tree_item(ruler_of)

                # If created from a node view, assign the new ruler immediately
                if parent_node_data:
                    parent_node_id = parent_node_data['node_id']
                    parent_node_data["ruler_id"] = new_id_str # Store ID as string
                    self.add_status_message(f"Tilldelade '{name}' som härskare till nod {parent_node_id}.")
                    self.refresh_tree_item(parent_node_id)
                    # Go back to the node view after assigning
                    self.show_node_view(parent_node_data)
                    return # Don't go to character list

            else: # Editing existing
                char_id_str = str(char_id) # Use the ID passed in
                if char_id_str in self.world_data.get("characters", {}):
                    char_data_to_update = self.world_data["characters"][char_id_str]
                    old_name = char_data_to_update.get("name", "")
                    old_ruler = char_data_to_update.get("ruler_of")
                    old_type = char_data_to_update.get("type", "")
                    char_data_to_update["name"] = name
                    char_data_to_update["wealth"] = wealth
                    char_data_to_update["description"] = description
                    char_data_to_update["skills"] = skills
                    char_data_to_update["type"] = type_val
                    char_data_to_update["ruler_of"] = ruler_of
                    self.add_status_message(
                        f"Uppdaterade karaktär '{old_name}' -> '{name}' (ID: {char_id_str})."
                    )

                    # Refresh tree items if this ruler changed name
                    if old_name != name or old_ruler != ruler_of:
                            if self.world_data and "nodes" in self.world_data:
                                for nid_str, ndata in self.world_data["nodes"].items():
                                    if str(ndata.get("ruler_id")) == char_id_str:
                                        try:
                                            self.refresh_tree_item(int(nid_str))
                                        except ValueError:
                                            pass

                    if old_ruler is not None and old_ruler != ruler_of:
                        old_node = self.world_data.get("nodes", {}).get(str(old_ruler))
                        if old_node and str(old_node.get("ruler_id")) == char_id_str:
                            old_node["ruler_id"] = None
                            self.refresh_tree_item(old_ruler)
                    if ruler_of is not None:
                        new_node = self.world_data.get("nodes", {}).get(str(ruler_of))
                        if new_node:
                            new_node["ruler_id"] = char_id_str
                            self.refresh_tree_item(ruler_of)
                else:
                    messagebox.showerror(
                        "Fel",
                        f"Kunde inte spara, karaktär med ID {char_id_str} hittades ej.",
                        parent=self.root,
                    )
                    return


            self.save_current_world()
            # Go back to the list view after saving/creating (unless assigned from node view)
            self.show_manage_characters_view()


        # --- Buttons ---
        button_frame = ttk.Frame(container)
        button_frame.pack(pady=(20, 10))
        # Define back command based on context
        back_command = lambda n=parent_node_data: self.show_node_view(n) if n else self.show_manage_characters_view()

        ttk.Button(button_frame, text="Spara", command=do_save).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="Avbryt", command=back_command).pack(side=tk.LEFT, padx=10)


    # --------------------------------------------------
    # Node Viewing and Editing
    # --------------------------------------------------
    def show_node_view(self, node_data):
        """Displays the appropriate editor for the given node in the right frame."""
        self.commit_pending_changes()
        self._clear_right_frame()

        if not isinstance(node_data, dict):
            self.add_status_message(f"Fel: Ogiltig noddata mottagen: {node_data}")
            self.show_no_world_view()
            return

        node_id = node_data.get("node_id")
        if node_id is None:
            self.add_status_message("Fel: Kan inte visa nodvy, noden saknar ID.")
            self.show_no_world_view()
            return

        # Recalculate depth just in case cache is stale (though updates should clear it)
        # self.clear_depth_cache() # Uncomment if depth issues suspected
        depth = self.get_depth_of_node(node_id)
        display_name = self.get_display_name_for_node(node_data, depth)

        # --- Main container frame with padding ---
        view_frame = ttk.Frame(self.right_frame, padding="10 10 10 10")
        view_frame.pack(fill="both", expand=True)
        view_frame.grid_rowconfigure(1, weight=1)
        view_frame.grid_columnconfigure(0, weight=1)

        # --- Title Frame ---
        title_frame = ttk.Frame(view_frame)
        title_frame.pack(fill="x", pady=(0, 15))
        title_label = ttk.Label(title_frame, text=f"{display_name}", font=("Arial", 16, "bold"))
        title_label.pack(side=tk.LEFT)
        ttk.Label(title_frame, text=f" (ID: {node_id}, Djup: {depth})", font=("Arial", 10)).pack(side=tk.LEFT, anchor="s", padx=5)

        # --- Scrollable area for editor content ---
        scroll_frame = ScrollableFrame(view_frame)
        scroll_frame.pack(fill="both", expand=True)
        editor_content_frame = scroll_frame.content


        # --- Call specific editor based on depth ---
        if depth < 0: # Error case (orphan/cycle)
            ttk.Label(editor_content_frame, text="Fel: Kan inte bestämma nodens position i hierarkin.", foreground="red").pack(pady=10)
        elif depth < 3:
            self._show_upper_level_node_editor(editor_content_frame, node_data, depth)
        elif depth == 3:
            self._show_jarldome_editor(editor_content_frame, node_data)
        else: # depth >= 4
            self._show_resource_editor(editor_content_frame, node_data, depth)

        # Common Back button (place it outside the specific editors if preferred)
        # back_button = ttk.Button(view_frame, text="< Stäng Vy", command=self.show_no_world_view)
        # back_button.pack(side=tk.BOTTOM, pady=(10, 0)) # Example placement


    def _create_delete_button(self, parent_frame, node_data, is_modified=None):
        """Creates the delete button common to all node editors.

        Parameters
        ----------
        parent_frame : ttk.Frame
            The frame where the button should be placed.
        node_data : dict
            Dictionary representing the node to delete.
        is_modified : Callable[[], bool] | None
            Optional callback that returns ``True`` if the editor has
            unsaved changes. If provided, the user will be warned before
            deletion if changes are detected.
        """

        def do_delete():
            if not isinstance(node_data, dict) or 'node_id' not in node_data:
                messagebox.showerror("Fel", "Kan inte radera, ogiltig noddata.", parent=self.root)
                return

            node_id = node_data['node_id']
            # Recalculate depth for display name in message
            depth = self.get_depth_of_node(node_id)
            display_name = self.get_display_name_for_node(node_data, depth)

            confirm_msg = f"Är du säker på att du vill radera '{display_name}' (ID: {node_id})?"
            if callable(is_modified) and is_modified():
                confirm_msg += "\n\nObservera: Noden har osparade ändringar." 
            num_children = len(node_data.get("children", []))
            # Estimate total descendants for better warning
            descendant_count = self.world_manager.count_descendants(node_id)

            if descendant_count > 0:
                confirm_msg += f"\n\nVARNING: Detta kommer även att radera {descendant_count} underliggande förläning(ar)!"
            elif num_children > 0:  # Fallback if descendant count fails
                confirm_msg += f"\n\nVARNING: Detta kommer även att radera {num_children} direkta underförläning(ar)!"


            if messagebox.askyesno("Radera Nod?", confirm_msg, icon='warning', parent=self.root):
                parent_id = node_data.get("parent_id")

                # Store tree state before modifying structure
                open_items, selection = self.store_tree_state()

                # Remove from parent's children list (handle string/int IDs)
                if parent_id is not None:
                        parent_node = self.world_data.get("nodes", {}).get(str(parent_id))
                        if parent_node and "children" in parent_node:
                            parent_children = parent_node["children"]
                            if node_id in parent_children:
                                parent_children.remove(node_id)
                            elif str(node_id) in parent_children: # Handle string IDs
                                parent_children.remove(str(node_id))
                            # Ensure children are stored as ints after modification
                            parent_node["children"] = [int(c) for c in parent_children if str(c).isdigit()]


                # Delete the node and all its descendants
                deleted_count_total = self.delete_node_and_descendants(node_id)

                self.save_current_world()
                self.add_status_message(f"Raderade nod '{display_name}' (ID: {node_id}) och {deleted_count_total-1} underliggande nod(er).")

                # Refresh the entire tree efficiently
                self.populate_tree() # This clears and refills
                self.restore_tree_state(open_items, selection) # Restore open/selection state

                self.show_no_world_view() # Clear the right panel

        delete_button = ttk.Button(parent_frame, text="Radera Nod (och underliggande)", command=do_delete, style="Danger.TButton")
        return delete_button

    def _auto_save_field(self, node_data, key, value, refresh_tree=False):
        node_data[key] = value
        self.save_current_world()
        if refresh_tree:
            self.refresh_tree_item(node_data.get("node_id"))


    def _show_upper_level_node_editor(self, parent_frame, node_data, depth):
        """Editor for Kingdom, Furstendöme, Hertigdöme (Depth 0-2)."""
        node_id = node_data['node_id']

        # Use Notebook for better organization? Maybe overkill here.
        # Main content frame for this editor
        editor_frame = ttk.Frame(parent_frame)
        editor_frame.pack(fill="both", expand=True)
        editor_frame.grid_columnconfigure(1, weight=1) # Allow entry column to expand

        row_idx = 0

        parent_forest = 0
        parent_id = node_data.get("parent_id")
        if parent_id and self.world_data:
            parent = self.world_data.get("nodes", {}).get(str(parent_id))
            if parent:
                try:
                    parent_forest = int(parent.get("forest_land", 0) or 0)
                except (ValueError, TypeError):
                    parent_forest = 0
        # Name (uses 'name' field for these levels)
        ttk.Label(editor_frame, text="Namn:").grid(row=row_idx, column=0, sticky="w", padx=5, pady=3)
        name_var = tk.StringVar(value=node_data.get("name", ""))
        name_entry = ttk.Entry(editor_frame, textvariable=name_var, width=40)
        name_entry.grid(row=row_idx, column=1, sticky="ew", padx=5, pady=3)
        name_var.trace_add("write", lambda *_: self._auto_save_field(node_data, "name", name_var.get().strip(), True))
        row_idx += 1

        # Custom Name (Optional extra identifier)
        ttk.Label(editor_frame, text="Eget Namn:").grid(row=row_idx, column=0, sticky="w", padx=5, pady=3)
        custom_name_var = tk.StringVar(value=node_data.get("custom_name", ""))
        custom_name_entry = ttk.Entry(editor_frame, textvariable=custom_name_var, width=40)
        custom_name_entry.grid(row=row_idx, column=1, sticky="ew", padx=5, pady=3)
        custom_name_var.trace_add("write", lambda *_: self._auto_save_field(node_data, "custom_name", custom_name_var.get().strip(), True))
        row_idx += 1

        # Population
        pop_label = ttk.Label(editor_frame, text="Befolkning:")
        pop_label.grid(row=row_idx, column=0, sticky="w", padx=5, pady=3)
        calculated_pop = int(node_data.get("population", 0))
        pop_var = tk.StringVar(value=str(calculated_pop))
        pop_entry = ttk.Entry(editor_frame, textvariable=pop_var, width=10)
        pop_entry.grid(row=row_idx, column=1, sticky="w", padx=5, pady=3)
        row_idx += 1

        # Inline help explaining subfiefs
        help_text = "En underförläning lyder under denna region.\nKlicka 'Skapa Nod' för att lägga till en." 
        ttk.Label(editor_frame, text=help_text, wraplength=300).grid(row=row_idx, column=0, columnspan=2, sticky="w", padx=5, pady=(0,5))
        row_idx += 1

        # List current children for quick reference
        ttk.Label(editor_frame, text="Nuvarande underförläningar:").grid(row=row_idx, column=0, sticky="nw", padx=5, pady=3)
        children_list = tk.Listbox(editor_frame, height=5)
        for cid in node_data.get("children", []):
            child = self.world_data.get("nodes", {}).get(str(cid))
            if child:
                children_list.insert(tk.END, self.get_display_name_for_node(child, depth + 1))
        children_list.grid(row=row_idx, column=1, sticky="ew", padx=5, pady=3)
        row_idx += 1

        # --- Actions Frame ---
        ttk.Separator(editor_frame, orient=tk.HORIZONTAL).grid(row=row_idx, column=0, columnspan=2, sticky="ew", pady=(15, 10))
        row_idx += 1
        button_frame = ttk.Frame(editor_frame)
        button_frame.grid(row=row_idx, column=0, columnspan=2, pady=5)
        row_idx += 1

        def create_subnode_action():
            node_data["name"] = name_var.get().strip()
            node_data["custom_name"] = custom_name_var.get().strip()
            try:
                node_data["population"] = int(pop_var.get() or "0")
            except (tk.TclError, ValueError):
                node_data["population"] = 0
            node_data["num_subfiefs"] = len(node_data.get("children", [])) + 1
            self.update_subfiefs_for_node(node_data)

        ttk.Button(button_frame, text="Skapa Nod", command=create_subnode_action).pack(side=tk.LEFT, padx=5)

        def save_node_action():
            old_name = node_data.get("name", "")
            old_custom_name = node_data.get("custom_name", "")
            old_pop = node_data.get("population", 0)
            old_area = node_data.get("tunnland", 0)

            new_name = name_var.get().strip()
            new_custom_name = custom_name_var.get().strip()
            try:
                new_pop = int(pop_var.get() or "0")
            except (tk.TclError, ValueError):
                new_pop = 0
            # num_subfiefs is saved via its own button

            changes_made = False
            status_details = []
            if old_name != new_name:
                node_data["name"] = new_name; changes_made = True
                status_details.append(f"Namn: '{old_name}' -> '{new_name}'")
            if old_custom_name != new_custom_name:
                node_data["custom_name"] = new_custom_name; changes_made = True
                status_details.append(f"Eget namn: '{old_custom_name}' -> '{new_custom_name}'")
            if old_pop != new_pop:
                node_data["population"] = new_pop; changes_made = True
                status_details.append(f"Befolkning: {old_pop} -> {new_pop}")

            if changes_made:
                self.world_manager.update_population_totals()
                self.save_current_world()
                status = f"Nod {node_id} uppdaterad: " + ", ".join(status_details)
                self.add_status_message(status)
                self.refresh_tree_item(node_id) # Update tree display name
            else:
                self.add_status_message(f"Nod {node_id}: Inga ändringar att spara.")


        ttk.Button(button_frame, text="Spara Noddata", command=save_node_action).pack(side=tk.LEFT, padx=5)
        self.pending_save_callback = save_node_action

        # --- Delete and Back Buttons Frame ---
        delete_back_frame = ttk.Frame(editor_frame)
        delete_back_frame.grid(row=row_idx, column=0, columnspan=2, pady=(20, 5))
        row_idx += 1

        def unsaved_changes() -> bool:
            try:
                current_pop = int(pop_var.get() or "0")
            except (tk.TclError, ValueError):
                current_pop = 0
            current_sub = len(node_data.get("children", []))
            return (
                name_var.get().strip() != node_data.get("name", "")
                or custom_name_var.get().strip() != node_data.get("custom_name", "")
                or current_pop != node_data.get("population", 0)
                or current_sub != node_data.get("num_subfiefs", 0)
            )

        delete_button = self._create_delete_button(delete_back_frame, node_data, unsaved_changes)
        delete_button.pack(side=tk.LEFT, padx=10)

        ttk.Button(delete_back_frame, text="< Stäng Vy", command=self.show_no_world_view).pack(side=tk.LEFT, padx=10)


    def _show_jarldome_editor(self, parent_frame, node_data):
        """Editor for Jarldoms (Depth 3)."""
        node_id = node_data['node_id']

        # Ensure necessary fields exist and format neighbors
        if "custom_name" not in node_data or not node_data["custom_name"]:
            node_data["custom_name"] = generate_swedish_village_name()
        node_data["res_type"] = "Resurs" # Internal type is always Resurs
        if "neighbors" not in node_data or not isinstance(node_data["neighbors"], list):
            node_data["neighbors"] = []
        for key in (
            "work_available",
            "work_needed",
            "storage_silver",
            "storage_basic",
            "storage_luxury",
            "jarldom_area",
        ):
            if key not in node_data:
                node_data[key] = 0
        # Ensure neighbor list has correct length and structure
        validated_neighbors = []
        current_neighbors = node_data["neighbors"]
        valid_jarldom_ids = {int(nid) for nid, nd in self.world_data.get("nodes", {}).items() if self.get_depth_of_node(int(nid)) == 3 and nid != str(node_id)}

        for i in range(MAX_NEIGHBORS):
            n_data = {}
            if i < len(current_neighbors) and isinstance(current_neighbors[i], dict):
                n_data = current_neighbors[i]

            n_id = n_data.get("id")
            n_border = n_data.get("border", NEIGHBOR_NONE_STR)

            # Validate ID
            final_id = None
            if n_id == NEIGHBOR_OTHER_STR: final_id = NEIGHBOR_OTHER_STR
            elif isinstance(n_id, int) and n_id in valid_jarldom_ids: final_id = n_id
            elif str(n_id).isdigit() and int(n_id) in valid_jarldom_ids: final_id = int(n_id)
            # Allow None

            # Validate border type
            if n_border not in BORDER_TYPES: n_border = NEIGHBOR_NONE_STR
            if final_id is None: n_border = NEIGHBOR_NONE_STR # Force border to None if no neighbor

            validated_neighbors.append({"id": final_id, "border": n_border})

        node_data["neighbors"] = validated_neighbors


        # Main content frame for this editor
        editor_frame = ttk.Frame(parent_frame)
        editor_frame.pack(fill="both", expand=True)
        editor_frame.grid_columnconfigure(1, weight=1) # Allow entry column to expand

        row_idx = 0
        # Custom Name (Primary identifier for Jarldoms)
        ttk.Label(editor_frame, text="Namn (Jarldöme):").grid(row=row_idx, column=0, sticky="w", padx=5, pady=3)
        custom_name_var = tk.StringVar(value=node_data.get("custom_name", ""))
        custom_name_entry = ttk.Entry(editor_frame, textvariable=custom_name_var, width=40)
        custom_name_entry.grid(row=row_idx, column=1, sticky="ew", padx=5, pady=3)
        custom_name_var.trace_add("write", lambda *_: self._auto_save_field(node_data, "custom_name", custom_name_var.get().strip(), True))
        row_idx += 1

        # Population
        pop_label = ttk.Label(editor_frame, text="Befolkning:")
        pop_label.grid(row=row_idx, column=0, sticky="w", padx=5, pady=3)
        calculated_pop = int(node_data.get("population", 0))
        pop_var = tk.StringVar(value=str(calculated_pop))
        pop_entry = ttk.Entry(editor_frame, textvariable=pop_var, width=10)
        pop_entry.grid(row=row_idx, column=1, sticky="w", padx=5, pady=3)

        row_idx += 1

        # Ruler selection
        ttk.Label(editor_frame, text="Härskare:").grid(row=row_idx, column=0, sticky="w", padx=5, pady=3)
        ruler_var = tk.StringVar()

        # Build list of character options
        char_usage: dict[str, int] = {}
        for nid_str, n in self.world_data.get("nodes", {}).items():
            rid = n.get("ruler_id")
            if rid is None:
                continue
            char_usage[str(rid)] = char_usage.get(str(rid), 0) + 1

        char_list: list[tuple[str, str]] = []
        for cid_str, cdata in self.world_data.get("characters", {}).items():
            name = cdata.get("name", f"ID {cid_str}")
            char_list.append((cid_str, name))
        char_list.sort(key=lambda x: x[1].lower())

        option_map: dict[str, str | None] = {"Ny härskare": "NEW", "Ingen karaktär": None}
        for cid_str, name in char_list:
            count = char_usage.get(cid_str, 0)
            disp = f"{cid_str}: {name}"
            if count:
                disp += f" ({count})"
            option_map[disp] = cid_str

        ruler_combo = ttk.Combobox(editor_frame, textvariable=ruler_var, values=list(option_map.keys()), state="readonly", width=40, style="BlackWhite.TCombobox")
        ruler_combo.grid(row=row_idx, column=1, sticky="ew", padx=5, pady=3)

        def refresh_ruler_style() -> None:
            sel = option_map.get(ruler_var.get())
            rid = None
            if sel and sel not in (None, "NEW"):
                rid = str(sel)
            if rid and char_usage.get(rid, 0) > (1 if str(node_data.get("ruler_id")) == rid else 0):
                ruler_combo.config(style="Danger.TCombobox")
            else:
                ruler_combo.config(style="BlackWhite.TCombobox")

        def create_new_ruler() -> str:
            existing_ids = [int(k) for k in self.world_data.get("characters", {})]
            new_id = max(existing_ids) + 1 if existing_ids else 1
            new_name = generate_character_name()
            new_data = {
                "char_id": new_id,
                "name": new_name,
                "wealth": 0,
                "description": "",
                "skills": [],
                "type": "Härskare",
                "ruler_of": node_id,
            }
            self.world_data.setdefault("characters", {})[str(new_id)] = new_data
            self.add_status_message(f"Skapade ny härskare '{new_name}' (ID: {new_id}).")
            return str(new_id)

        def on_ruler_change(*_args):
            sel = option_map.get(ruler_var.get())
            if sel == "NEW":
                new_id = create_new_ruler()
                node_data["ruler_id"] = new_id
                option_map.clear()
                # rebuild options with new character included
                char_usage.clear()
                for nid_str, n in self.world_data.get("nodes", {}).items():
                    rid = n.get("ruler_id")
                    if rid is None:
                        continue
                    char_usage[str(rid)] = char_usage.get(str(rid), 0) + 1
                char_list.clear()
                for cid_str, cdata in self.world_data.get("characters", {}).items():
                    name = cdata.get("name", f"ID {cid_str}")
                    char_list.append((cid_str, name))
                char_list.sort(key=lambda x: x[1].lower())
                option_map.update({"Ny härskare": "NEW", "Ingen karaktär": None})
                for cid_str, name in char_list:
                    count = char_usage.get(cid_str, 0)
                    disp = f"{cid_str}: {name}"
                    if count:
                        disp += f" ({count})"
                    option_map[disp] = cid_str
                ruler_combo.config(values=list(option_map.keys()))
                # set selection to new char
                for disp, cid in option_map.items():
                    if cid == new_id:
                        ruler_var.set(disp)
                        break
                self.save_current_world()
                self.refresh_tree_item(node_id)
            elif sel is None:
                node_data["ruler_id"] = None
            else:
                node_data["ruler_id"] = str(sel)
            refresh_ruler_style()
            update_owner_nodes_list()

        ruler_var.trace_add("write", on_ruler_change)

        # Set up owner list helper before initial selection triggers callback
        extra_owner_var = tk.StringVar()

        def update_owner_nodes_list() -> None:
            rid = node_data.get("ruler_id")
            if rid is None:
                extra_owner_var.set("")
                return
            ids = [str(node_id)]
            for nid_str, n in self.world_data.get("nodes", {}).items():
                if int(nid_str) == node_id:
                    continue
                if str(n.get("ruler_id")) == str(rid):
                    ids.append(nid_str)
            ids = sorted(set(ids), key=lambda x: int(x))
            extra_owner_var.set(", ".join(ids))

        # Set initial selection
        initial_rid = node_data.get("ruler_id")
        if initial_rid is None:
            ruler_var.set("Ingen karaktär")
        else:
            for disp, cid in option_map.items():
                if cid is not None and cid != "NEW" and str(cid) == str(initial_rid):
                    ruler_var.set(disp)
                    break
        refresh_ruler_style()
        update_owner_nodes_list()

        row_idx += 1

        ttk.Label(editor_frame, text="Ägarnoder:").grid(row=row_idx, column=0, sticky="w", padx=5, pady=3)
        extra_owner_entry = ttk.Entry(editor_frame, textvariable=extra_owner_var, width=40)
        extra_owner_entry.grid(row=row_idx, column=1, sticky="ew", padx=5, pady=3)

        row_idx += 1

        # Work days available and needed
        ttk.Label(editor_frame, text="Dagsverken Tillg.").grid(row=row_idx, column=0, sticky="w", padx=5, pady=3)
        work_av_var = tk.StringVar(value=str(node_data.get("work_available", 0)))
        work_av_entry = ttk.Entry(editor_frame, textvariable=work_av_var, width=6)
        work_av_entry.grid(row=row_idx, column=1, sticky="w", padx=5, pady=3)

        row_idx += 1

        ttk.Label(editor_frame, text="Dagsverken Behov:").grid(row=row_idx, column=0, sticky="w", padx=5, pady=3)
        work_need_var = tk.StringVar(value=str(node_data.get("work_needed", 0)))
        work_need_entry = ttk.Entry(editor_frame, textvariable=work_need_var, width=6)
        work_need_entry.grid(row=row_idx, column=1, sticky="w", padx=5, pady=3)

        row_idx += 1

        ttk.Label(editor_frame, text="Lager Silver/Bas/Lyx:").grid(row=row_idx, column=0, sticky="w", padx=5, pady=3)
        storage_frame = ttk.Frame(editor_frame)
        storage_frame.grid(row=row_idx, column=1, sticky="w", padx=5, pady=3)
        silver_var = tk.StringVar(value=str(node_data.get("storage_silver", 0)))
        basic_var = tk.StringVar(value=str(node_data.get("storage_basic", 0)))
        luxury_var = tk.StringVar(value=str(node_data.get("storage_luxury", 0)))
        ttk.Entry(storage_frame, textvariable=silver_var, width=4).pack(side=tk.LEFT, padx=2)
        ttk.Entry(storage_frame, textvariable=basic_var, width=4).pack(side=tk.LEFT, padx=2)
        ttk.Entry(storage_frame, textvariable=luxury_var, width=4).pack(side=tk.LEFT, padx=2)

        row_idx += 1

        ttk.Label(editor_frame, text="Areal totalt:").grid(row=row_idx, column=0, sticky="w", padx=5, pady=3)
        area_var = tk.StringVar(value=str(node_data.get("jarldom_area", 0)))
        area_entry = ttk.Entry(editor_frame, textvariable=area_var, width=8)
        area_entry.grid(row=row_idx, column=1, sticky="w", padx=5, pady=3)

        row_idx += 1

        # Removed numeric control for subresources
        row_idx += 0

        # --- Actions Frame ---
        ttk.Separator(editor_frame, orient=tk.HORIZONTAL).grid(row=row_idx, column=0, columnspan=2, sticky="ew", pady=(15, 10))
        row_idx += 1
        action_button_frame = ttk.Frame(editor_frame)
        action_button_frame.grid(row=row_idx, column=0, columnspan=2, pady=5)
        row_idx += 1




        def save_node_action():
            old_custom_name = node_data.get("custom_name", "")
            old_pop = node_data.get("population", 0)
            old_work_av = int(node_data.get("work_available", 0) or 0)
            old_work_need = int(node_data.get("work_needed", 0) or 0)
            old_silver = int(node_data.get("storage_silver", 0) or 0)
            old_basic = int(node_data.get("storage_basic", 0) or 0)
            old_lux = int(node_data.get("storage_luxury", 0) or 0)
            old_area = int(node_data.get("jarldom_area", 0) or 0)

            new_custom_name = custom_name_var.get().strip()
            if not new_custom_name:
                messagebox.showwarning("Namn Saknas", "Ett Jarldöme måste ha ett namn.", parent=self.root)
                return
            try:
                new_pop = int(pop_var.get() or "0")
            except (tk.TclError, ValueError):
                new_pop = 0
            try:
                new_work_av = int(work_av_var.get() or "0")
            except (tk.TclError, ValueError):
                new_work_av = 0
            try:
                new_work_need = int(work_need_var.get() or "0")
            except (tk.TclError, ValueError):
                new_work_need = 0
            try:
                new_silver = int(silver_var.get() or "0")
            except (tk.TclError, ValueError):
                new_silver = 0
            try:
                new_basic = int(basic_var.get() or "0")
            except (tk.TclError, ValueError):
                new_basic = 0
            try:
                new_lux = int(luxury_var.get() or "0")
            except (tk.TclError, ValueError):
                new_lux = 0
            try:
                new_area = int(area_var.get() or "0")
            except (tk.TclError, ValueError):
                new_area = 0
            # num_subfiefs saved via its own button

            changes_made = False
            status_details = []
            if old_custom_name != new_custom_name:
                node_data["custom_name"] = new_custom_name; changes_made = True
                status_details.append(f"Namn: '{old_custom_name}' -> '{new_custom_name}'")
            if old_pop != new_pop:
                node_data["population"] = new_pop; changes_made = True
                status_details.append(f"Befolkning: {old_pop} -> {new_pop}")
            if old_work_av != new_work_av:
                node_data["work_available"] = new_work_av; changes_made = True
            if old_work_need != new_work_need:
                node_data["work_needed"] = new_work_need; changes_made = True
            if old_silver != new_silver:
                node_data["storage_silver"] = new_silver; changes_made = True
            if old_basic != new_basic:
                node_data["storage_basic"] = new_basic; changes_made = True
            if old_lux != new_lux:
                node_data["storage_luxury"] = new_lux; changes_made = True
            if old_area != new_area:
                node_data["jarldom_area"] = new_area; changes_made = True

            # Handle ruler assignment
            selected_val = option_map.get(ruler_var.get())
            if selected_val == "NEW":
                # new ruler already created in callback
                new_ruler_id = node_data.get("ruler_id")
            elif selected_val is None:
                new_ruler_id = None
            else:
                new_ruler_id = str(selected_val)

            old_ruler_id = node_data.get("ruler_id")
            if str(old_ruler_id) != str(new_ruler_id):
                node_data["ruler_id"] = new_ruler_id
                changes_made = True
                status_details.append("Härskare uppdaterad")
                if old_ruler_id is not None:
                    old_char = self.world_data.get("characters", {}).get(str(old_ruler_id))
                    if old_char and old_char.get("ruler_of") == node_id:
                        old_char["ruler_of"] = None
                if new_ruler_id is not None:
                    new_char = self.world_data.get("characters", {}).get(str(new_ruler_id))
                    if new_char:
                        new_char["ruler_of"] = node_id

            # Assign additional owner nodes
            if new_ruler_id is not None:
                extra_ids = []
                for part in extra_owner_var.get().split(','):
                    part = part.strip()
                    if part.isdigit() and len(part) <= 4:
                        extra_ids.append(int(part))
                for eid in extra_ids:
                    other = self.world_data.get("nodes", {}).get(str(eid))
                    if other:
                        if str(other.get("ruler_id")) != new_ruler_id:
                            other["ruler_id"] = new_ruler_id
                            self.refresh_tree_item(eid)

            node_data["res_type"] = "Resurs" # Ensure internal type

            if changes_made:
                self.world_manager.update_population_totals()
                self.save_current_world()
                status = f"Jarldöme {node_id} uppdaterad: " + ", ".join(status_details)
                self.add_status_message(status)
                self.refresh_tree_item(node_id) # Update tree display name
                # Also update map if visible
                if self.static_map_canvas and self.static_map_canvas.winfo_exists():
                    self.update_static_hex_label(node_id)
            else:
                self.add_status_message(f"Jarldöme {node_id}: Inga ändringar att spara.")


        ttk.Button(action_button_frame, text="Spara Jarldöme", command=save_node_action).pack(side=tk.LEFT, padx=5)
        self.pending_save_callback = save_node_action

        def create_subnode_action():
            save_node_action()
            node_data["num_subfiefs"] = len(node_data.get("children", [])) + 1
            self.update_subfiefs_for_node(node_data)

        ttk.Button(action_button_frame, text="Skapa Nod", command=create_subnode_action).pack(side=tk.LEFT, padx=5)


        # --- Neighbor Editing ---
        neighbor_button_frame = ttk.Frame(action_button_frame) # Add to same action row
        neighbor_button_frame.pack(side=tk.LEFT, padx=15)
        ttk.Button(neighbor_button_frame, text="Redigera Grannar", command=lambda n=node_data: self.show_neighbor_editor(n)).pack()


        # --- Delete and Back Buttons Frame ---
        delete_back_frame = ttk.Frame(editor_frame)
        delete_back_frame.grid(row=row_idx, column=0, columnspan=2, pady=(20, 5))
        row_idx += 1

        def unsaved_changes() -> bool:
            try:
                current_pop = int(pop_var.get() or "0")
            except (tk.TclError, ValueError):
                current_pop = 0
            current_sub = len(node_data.get("children", []))
            try:
                cur_av = int(work_av_var.get() or "0")
            except (tk.TclError, ValueError):
                cur_av = 0
            try:
                cur_need = int(work_need_var.get() or "0")
            except (tk.TclError, ValueError):
                cur_need = 0
            try:
                cur_sil = int(silver_var.get() or "0")
            except (tk.TclError, ValueError):
                cur_sil = 0
            try:
                cur_basic = int(basic_var.get() or "0")
            except (tk.TclError, ValueError):
                cur_basic = 0
            try:
                cur_lux = int(luxury_var.get() or "0")
            except (tk.TclError, ValueError):
                cur_lux = 0
            try:
                cur_area = int(area_var.get() or "0")
            except (tk.TclError, ValueError):
                cur_area = 0
            return (
                custom_name_var.get().strip() != node_data.get("custom_name", "")
                or current_pop != node_data.get("population", 0)
                or current_sub != node_data.get("num_subfiefs", 0)
                or cur_av != int(node_data.get("work_available", 0) or 0)
                or cur_need != int(node_data.get("work_needed", 0) or 0)
                or cur_sil != int(node_data.get("storage_silver", 0) or 0)
                or cur_basic != int(node_data.get("storage_basic", 0) or 0)
                or cur_lux != int(node_data.get("storage_luxury", 0) or 0)
                or cur_area != int(node_data.get("jarldom_area", 0) or 0)
            )

        delete_button = self._create_delete_button(delete_back_frame, node_data, unsaved_changes)
        delete_button.pack(side=tk.LEFT, padx=10)

        ttk.Button(delete_back_frame, text="< Stäng Vy", command=self.show_no_world_view).pack(side=tk.LEFT, padx=10)


    def _show_resource_editor(self, parent_frame, node_data, depth):
        """Editor for resource nodes at depth >=4."""
        node_id = node_data["node_id"]

        # Ensure res_type exists
        if "res_type" not in node_data or not node_data["res_type"]:
            node_data["res_type"] = JARLDOM_RESOURCE_TYPES[0]

        editor_frame = ttk.Frame(parent_frame)
        editor_frame.pack(fill="both", expand=True)
        editor_frame.grid_columnconfigure(1, weight=1)
        editor_frame.grid_columnconfigure(2, weight=0)

        row_idx = 0

        ttk.Label(editor_frame, text="Resurstyp:").grid(row=row_idx, column=0, sticky="w", padx=5, pady=3)
        res_var = tk.StringVar(value=node_data.get("res_type", JARLDOM_RESOURCE_TYPES[0]))
        res_combo = ttk.Combobox(editor_frame, textvariable=res_var, values=JARLDOM_RESOURCE_TYPES, state="readonly")
        res_combo.grid(row=row_idx, column=1, sticky="w", padx=5, pady=3)
        save_button = ttk.Button(editor_frame, text="Spara Nod")
        save_button.grid(row=row_idx, column=2, sticky="w", padx=5, pady=3)
        row_idx += 1

        ttk.Label(editor_frame, text="Eget Namn:").grid(row=row_idx, column=0, sticky="w", padx=5, pady=3)
        custom_var = tk.StringVar(value=node_data.get("custom_name", ""))
        custom_entry = ttk.Entry(editor_frame, textvariable=custom_var, width=40)
        custom_entry.grid(row=row_idx, column=1, sticky="ew", padx=5, pady=3)
        custom_var.trace_add("write", lambda *_: self._auto_save_field(node_data, "custom_name", custom_var.get().strip(), True))
        row_idx += 1

        pop_label = ttk.Label(editor_frame, text="Befolkning:")
        pop_label.grid(row=row_idx, column=0, sticky="w", padx=5, pady=3)
        calculated_pop = int(node_data.get("population", 0))
        pop_var = tk.StringVar(value=str(calculated_pop))
        pop_entry = ttk.Entry(editor_frame, textvariable=pop_var, width=10)
        pop_entry.grid(row=row_idx, column=1, sticky="w", padx=5, pady=3)
        row_idx += 1

        area_label = ttk.Label(editor_frame, text="Tunnland:")
        area_var = tk.StringVar(value=str(node_data.get("tunnland", 0)))
        area_entry = ttk.Entry(editor_frame, textvariable=area_var, width=10)
        area_label.grid(row=row_idx, column=0, sticky="w", padx=5, pady=3)
        area_entry.grid(row=row_idx, column=1, sticky="w", padx=5, pady=3)
        row_idx += 1

        # --- Gods specific fields ---
        manor_label = ttk.Label(editor_frame, text="Godsareal:")
        manor_var = tk.StringVar(value=str(node_data.get("manor_land", 0)))
        manor_entry = ttk.Entry(editor_frame, textvariable=manor_var, width=10)

        cultivated_label = ttk.Label(editor_frame, text="Odlingsmark:")
        cultivated_var = tk.StringVar(value=str(node_data.get("cultivated_land", 0)))
        c_frame = ttk.Frame(editor_frame)
        cultivated_entry = ttk.Entry(c_frame, textvariable=cultivated_var, width=10)
        cq_label = ttk.Label(editor_frame, text="Odlingskvalitet:")
        cq_var = tk.StringVar(value=str(node_data.get("cultivated_quality", 3)))
        cq_combo = ttk.Combobox(
            editor_frame,
            textvariable=cq_var,
            values=[str(i) for i in range(1, 6)],
            state="readonly",
            width=5,
        )

        fallow_label = ttk.Label(editor_frame, text="Trädad mark:")
        fallow_var = tk.StringVar(value=str(node_data.get("fallow_land", 0)))
        f_frame = ttk.Frame(editor_frame)
        fallow_entry = ttk.Entry(f_frame, textvariable=fallow_var, width=10)
        herd_label = ttk.Label(editor_frame, text="Boskap:")
        herd_var = tk.StringVar(value="Ja" if node_data.get("has_herd") else "Nej")
        herd_combo = ttk.Combobox(
            editor_frame, textvariable=herd_var, values=["Ja", "Nej"], state="readonly", width=5
        )

        forest_label = ttk.Label(editor_frame, text="Skogsmark:")
        forest_var = tk.StringVar(value=str(node_data.get("forest_land", 0)))
        forest_entry = ttk.Entry(editor_frame, textvariable=forest_var, width=10)
        hunt_label = ttk.Label(editor_frame, text="Jaktkvalitet:")
        hunt_var = tk.StringVar(value=str(node_data.get("hunt_quality", 3)))
        hunt_combo = ttk.Combobox(
            editor_frame,
            textvariable=hunt_var,
            values=[str(i) for i in range(1, 6)],
            state="readonly",
            width=5,
        )

        law_label = ttk.Label(editor_frame, text="Jaktlag:")
        law_var = tk.StringVar(value=str(node_data.get("hunting_law", 0)))
        law_combo = ttk.Combobox(editor_frame, textvariable=law_var, state="readonly", width=5)

        # Grid placement (initially hidden; visibility controlled below)
        manor_label.grid(row=row_idx, column=0, sticky="w", padx=5, pady=3)
        manor_entry.grid(row=row_idx, column=1, sticky="w", padx=5, pady=3)
        row_idx += 1

        cultivated_label.grid(row=row_idx, column=0, sticky="w", padx=5, pady=3)
        c_frame.grid(row=row_idx, column=1, sticky="w", padx=5, pady=3)
        cultivated_entry.pack(side=tk.LEFT)
        cq_label.grid(row=row_idx, column=2, sticky="w", padx=5, pady=3)
        cq_combo.grid(row=row_idx, column=3, sticky="w", padx=5, pady=3)
        row_idx += 1

        fallow_label.grid(row=row_idx, column=0, sticky="w", padx=5, pady=3)
        f_frame.grid(row=row_idx, column=1, sticky="w", padx=5, pady=3)
        fallow_entry.pack(side=tk.LEFT)
        herd_label.grid(row=row_idx, column=2, sticky="w", padx=5, pady=3)
        herd_combo.grid(row=row_idx, column=3, sticky="w", padx=5, pady=3)
        row_idx += 1

        forest_label.grid(row=row_idx, column=0, sticky="w", padx=5, pady=3)
        forest_entry.grid(row=row_idx, column=1, sticky="w", padx=5, pady=3)
        law_label.grid(row=row_idx, column=2, sticky="w", padx=5, pady=3)
        law_combo.grid(row=row_idx, column=3, sticky="w", padx=5, pady=3)
        hunt_label.grid(row=row_idx, column=4, sticky="w", padx=5, pady=3)
        hunt_combo.grid(row=row_idx, column=5, sticky="w", padx=5, pady=3)
        row_idx += 1

        water_label = ttk.Label(editor_frame, text="Fiskekvalitet:")
        fish_var = tk.StringVar(value=node_data.get("fish_quality", node_data.get("water_quality", "Normalt")))
        fish_combo = ttk.Combobox(
            editor_frame, textvariable=fish_var, values=FISH_QUALITY_LEVELS, state="readonly"
        )
        water_label.grid(row=row_idx, column=0, sticky="w", padx=5, pady=3)
        fish_combo.grid(row=row_idx, column=1, sticky="w", padx=5, pady=3)
        row_idx += 1

        boats_label = ttk.Label(editor_frame, text="Fiskebåtar:")
        boats_var = tk.StringVar(value=str(node_data.get("fishing_boats", 0)))
        boats_combo = ttk.Combobox(
            editor_frame,
            textvariable=boats_var,
            values=[str(i) for i in range(MAX_FISHING_BOATS + 1)],
            state="readonly",
            width=5,
        )
        boats_label.grid(row=row_idx, column=0, sticky="w", padx=5, pady=3)
        boats_combo.grid(row=row_idx, column=1, sticky="w", padx=5, pady=3)
        row_idx += 1

        gamekeeper_label = ttk.Label(editor_frame, text="Jägarmästare:")
        gamekeeper_var = tk.StringVar()
        gk_options = ["Ingen karaktär"]
        if self.world_data and "characters" in self.world_data:
            for cid_str, cdata in self.world_data["characters"].items():
                if cdata.get("type") == "Jägarmästare":
                    name = cdata.get("name", f"ID {cid_str}")
                    gk_options.append(f"{cid_str}: {name}")
                    if node_data.get("gamekeeper_id") is not None and str(node_data.get("gamekeeper_id")) == str(cid_str):
                        gamekeeper_var.set(f"{cid_str}: {name}")
        if not gamekeeper_var.get():
            gamekeeper_var.set("Ingen karaktär")
        gamekeeper_combo = ttk.Combobox(editor_frame, textvariable=gamekeeper_var, values=gk_options, state="readonly", width=40)
        gamekeeper_label.grid(row=row_idx, column=0, sticky="w", padx=5, pady=3)
        gamekeeper_combo.grid(row=row_idx, column=1, sticky="w", padx=5, pady=3)
        row_idx += 1

        parent_forest = 0
        parent_id = node_data.get("parent_id")
        if parent_id and self.world_data:
            parent = self.world_data.get("nodes", {}).get(str(parent_id))
            if parent:
                try:
                    parent_forest = int(parent.get("forest_land", 0) or 0)
                except (ValueError, TypeError):
                    parent_forest = 0

        max_hunters = max(0, parent_forest // 10)
        hunter_label = ttk.Label(editor_frame, text="Jägare:")
        hunter_var = tk.StringVar(value=str(node_data.get("hunters", 0)))
        hunter_combo = ttk.Combobox(editor_frame, textvariable=hunter_var, values=[str(i) for i in range(max_hunters + 1)], state="readonly", width=5)
        hunter_label.grid(row=row_idx, column=0, sticky="w", padx=5, pady=3)
        hunter_combo.grid(row=row_idx, column=1, sticky="w", padx=5, pady=3)
        row_idx += 1

        def refresh_area_visibility(*args):
            if res_var.get() in {"Vildmark", "Jaktmark"}:
                area_label.grid()
                area_entry.grid()
                pop_label.grid_remove()
                pop_entry.grid_remove()
            elif res_var.get() == "Djur":
                area_label.grid_remove()
                area_entry.grid_remove()
                pop_label.grid_remove()
                pop_entry.grid_remove()
            else:
                area_label.grid_remove()
                area_entry.grid_remove()
                pop_label.grid()
                pop_entry.grid()

        def refresh_water_visibility(*_):
            if res_var.get() in {"Hav", "Flod"}:
                water_label.grid()
                fish_combo.grid()
                boats_label.grid()
                boats_combo.grid()
            else:
                water_label.grid_remove()
                fish_combo.grid_remove()
                boats_label.grid_remove()
                boats_combo.grid_remove()

        def refresh_hunt_visibility(*_):
            if res_var.get() == "Jaktmark":
                gamekeeper_label.grid()
                gamekeeper_combo.grid()
                hunter_label.grid()
                hunter_combo.grid()
            else:
                gamekeeper_label.grid_remove()
                gamekeeper_combo.grid_remove()
                hunter_label.grid_remove()
                hunter_combo.grid_remove()

        def update_law_options(*_):
            try:
                fl = int(forest_var.get() or "0")
            except (ValueError, TypeError):
                fl = 0
            max_val = max(0, fl // 50)
            law_combo.config(values=[str(i) for i in range(0, max_val + 1)])
            try:
                cur = int(law_var.get() or "0")
            except (ValueError, TypeError):
                cur = 0
            if cur > max_val:
                law_var.set(str(max_val))
            if fl > 50 and res_var.get() == "Gods":
                law_label.grid()
                law_combo.grid()
            else:
                law_label.grid_remove()
                law_combo.grid_remove()

        def refresh_gods_visibility(*_):
            if res_var.get() == "Gods":
                manor_label.grid()
                manor_entry.grid()
                cultivated_label.grid()
                c_frame.grid()
                cq_label.grid()
                cq_combo.grid()
                fallow_label.grid()
                f_frame.grid()
                herd_label.grid()
                herd_combo.grid()
                forest_label.grid()
                forest_entry.grid()
                law_label.grid()
                law_combo.grid()
                hunt_label.grid()
                hunt_combo.grid()
                update_law_options()
            else:
                manor_label.grid_remove()
                manor_entry.grid_remove()
                cultivated_label.grid_remove()
                c_frame.grid_remove()
                cq_label.grid_remove()
                cq_combo.grid_remove()
                fallow_label.grid_remove()
                f_frame.grid_remove()
                herd_label.grid_remove()
                herd_combo.grid_remove()
                forest_label.grid_remove()
                forest_entry.grid_remove()
                law_label.grid_remove()
                law_combo.grid_remove()
                hunt_label.grid_remove()
                hunt_combo.grid_remove()

        def handle_herd_toggle(*_):
            val = herd_var.get()
            existing_id = None
            for cid in node_data.get("children", []):
                cnode = self.world_data.get("nodes", {}).get(str(cid))
                if cnode and cnode.get("res_type") == "Djur":
                    existing_id = cid
                    break
            if val == "Ja" and existing_id is None:
                open_items, selection = self.store_tree_state()
                new_id = self.world_data.get("next_node_id", 1)
                while str(new_id) in self.world_data.get("nodes", {}):
                    new_id += 1
                self.world_data["next_node_id"] = new_id + 1
                new_node = {
                    "node_id": new_id,
                    "parent_id": node_id,
                    "name": "Resurs",
                    "custom_name": "",
                    "res_type": "Djur",
                    "children": [],
                    "num_subfiefs": 0,
                }
                self.world_data.setdefault("nodes", {})[str(new_id)] = new_node
                node_data.setdefault("children", []).append(new_id)
                self.world_manager.clear_depth_cache()
                self.world_manager.update_population_totals()
                self.save_current_world()
                self.populate_tree()
                self.restore_tree_state(open_items, selection)
            elif val == "Nej" and existing_id is not None:
                child = self.world_data.get("nodes", {}).get(str(existing_id))
                has_data = bool(child.get("animals")) or bool(child.get("custom_name")) or child.get("children")
                if has_data:
                    if not messagebox.askyesno(
                        "Ta bort Djur",
                        "Underresursen inneh\u00e5ller data och kommer tas bort. Forts\u00e4tt?",
                        parent=self.root,
                    ):
                        herd_var.set("Ja")
                        return
                open_items, selection = self.store_tree_state()
                self.delete_node_and_descendants(existing_id)
                if existing_id in node_data.get("children", []):
                    node_data["children"].remove(existing_id)
                self.world_manager.clear_depth_cache()
                self.world_manager.update_population_totals()
                self.save_current_world()
                self.populate_tree()
                self.restore_tree_state(open_items, selection)

        res_var.trace_add("write", refresh_area_visibility)
        refresh_area_visibility()
        res_var.trace_add("write", refresh_water_visibility)
        refresh_water_visibility()
        res_var.trace_add("write", refresh_hunt_visibility)
        refresh_hunt_visibility()
        res_var.trace_add("write", refresh_gods_visibility)
        refresh_gods_visibility()
        forest_var.trace_add("write", update_law_options)
        update_law_options()
        herd_var.trace_add("write", handle_herd_toggle)

        # Removed numeric field for subresources
        row_idx += 0

        settlement_row = row_idx
        settlement_frame = ttk.Frame(editor_frame)
        row_idx += 1

        settlement_type_var = tk.StringVar(value=node_data.get("settlement_type", "By"))
        free_var = tk.StringVar(value=str(node_data.get("free_peasants", 0)))
        unfree_var = tk.StringVar(value=str(node_data.get("unfree_peasants", 0)))
        thrall_var = tk.StringVar(value=str(node_data.get("thralls", 0)))
        burgher_var = tk.StringVar(value=str(node_data.get("burghers", 0)))

        def update_population_display(*_args) -> None:
            """Update population field based on category counts."""
            try:
                total = (
                    int(free_var.get() or "0", 10)
                    + int(unfree_var.get() or "0", 10)
                    + int(thrall_var.get() or "0", 10)
                    + int(burgher_var.get() or "0", 10)
                )
            except ValueError:
                total = 0
            pop_var.set(str(total))

        for v in (free_var, unfree_var, thrall_var, burgher_var):
            v.trace_add("write", update_population_display)
        update_population_display()

        craftsman_rows: list[dict] = []

        def update_craftsman_options() -> None:
            """Refresh available craftsman choices for each row."""
            selected = {
                r["type_var"].get() for r in craftsman_rows if r["type_var"].get()
            }
            for r in craftsman_rows:
                combo = r.get("type_combo")
                if not combo:
                    continue
                current = r["type_var"].get()
                choices = [
                    t for t in CRAFTSMAN_TYPES if t not in selected or t == current
                ]
                combo.config(values=choices)

        def create_craftsman_row(c_type: str = "", c_count: int = 1, blank: bool = False):
            if len(craftsman_rows) >= 9:
                return
            row = {}
            frame = ttk.Frame(craft_frame)
            type_var = tk.StringVar(value=c_type)
            count_var = tk.StringVar(value=str(c_count))
            type_combo = ttk.Combobox(frame, textvariable=type_var, state="readonly", width=15)
            count_combo = ttk.Combobox(frame, textvariable=count_var, values=[str(i) for i in range(1,10)], state="readonly", width=3)
            del_btn = ttk.Button(frame, text="Radera", command=lambda r=row: remove_craftsman_row(r))
            type_combo.pack(side=tk.LEFT, padx=5)
            count_combo.pack(side=tk.LEFT, padx=5)
            del_btn.pack(side=tk.LEFT, padx=5)
            frame.pack(fill="x", pady=2)
            row.update({"frame": frame, "type_var": type_var, "count_var": count_var, "type_combo": type_combo, "blank": blank})
            craftsman_rows.append(row)
            def on_type_change(*args, r=row):
                # Prevent duplicate craftsman types across rows
                selected = r["type_var"].get()
                if selected:
                    for other in craftsman_rows:
                        if other is not r and other["type_var"].get() == selected:
                            # Revert selection if another row already uses this type
                            r["type_var"].set("")
                            return
                if r.get("blank") and r["type_var"].get():
                    r["blank"] = False
                    add_blank_row_if_needed()
                update_craftsman_options()
            type_var.trace_add("write", on_type_change)
            update_craftsman_options()

        def remove_craftsman_row(row):
            if row in craftsman_rows:
                row["frame"].destroy()
                craftsman_rows.remove(row)
                add_blank_row_if_needed()
                update_craftsman_options()

        def add_blank_row_if_needed():
            if len(craftsman_rows) < 9 and not any(r.get("blank") for r in craftsman_rows):
                create_craftsman_row(blank=True)
            update_craftsman_options()

        ttk.Label(settlement_frame, text="Bosättningstyp:").grid(row=0, column=0, sticky="w", padx=5, pady=3)
        type_combo = ttk.Combobox(settlement_frame, textvariable=settlement_type_var, values=list(SETTLEMENT_TYPES), state="readonly")
        type_combo.grid(row=0, column=1, sticky="w", padx=5, pady=3)

        row_fields = [
            ("Friabönder:", free_var),
            ("Ofria bönder:", unfree_var),
            ("Trälar:", thrall_var),
            ("Borgare:", burgher_var),
        ]
        for idx, (label, var) in enumerate(row_fields, start=1):
            ttk.Label(settlement_frame, text=label).grid(row=idx, column=0, sticky="w", padx=5, pady=3)
            ttk.Entry(settlement_frame, textvariable=var, width=10).grid(row=idx, column=1, sticky="w", padx=5, pady=3)

        ttk.Label(settlement_frame, text="Hantverkare:").grid(row=5, column=0, sticky="nw", padx=5, pady=(10, 3))
        craft_frame = ttk.Frame(settlement_frame)
        craft_frame.grid(row=5, column=1, sticky="w", pady=(10, 3))

        soldier_label = ttk.Label(editor_frame, text="Soldater:")
        soldier_label.grid(row=row_idx, column=0, sticky="nw", padx=5, pady=(10, 3))
        soldier_frame = ttk.Frame(editor_frame)
        soldier_frame.grid(row=row_idx, column=1, sticky="w", pady=(10, 3))
        row_idx += 1

        soldier_rows: list[dict] = []

        animal_label = ttk.Label(editor_frame, text="Djur:")
        animal_label.grid(row=row_idx, column=0, sticky="nw", padx=5, pady=(10, 3))
        animal_frame = ttk.Frame(editor_frame)
        animal_frame.grid(row=row_idx, column=1, sticky="w", pady=(10, 3))
        row_idx += 1

        animal_rows: list[dict] = []

        character_label = ttk.Label(editor_frame, text="Karaktärer:")
        character_label.grid(row=row_idx, column=0, sticky="nw", padx=5, pady=(10, 3))
        character_frame = ttk.Frame(editor_frame)
        character_frame.grid(row=row_idx, column=1, sticky="w", pady=(10, 3))
        row_idx += 1

        character_rows: list[dict] = []

        building_label = ttk.Label(editor_frame, text="Byggnader:")
        building_label.grid(row=row_idx, column=0, sticky="nw", padx=5, pady=(10, 3))
        building_frame = ttk.Frame(editor_frame)
        building_frame.grid(row=row_idx, column=1, sticky="w", pady=(10, 3))
        row_idx += 1

        building_rows: list[dict] = []

        jarldom_options: list[str] = []
        if self.world_data and "nodes" in self.world_data:
            jarldoms = []
            for nid_str, n in self.world_data["nodes"].items():
                try:
                    nid = int(nid_str)
                except ValueError:
                    continue
                if self.get_depth_of_node(nid) == 3:
                    name = n.get("custom_name", f"Jarldöme {nid}")
                    jarldoms.append((nid, name))
            jarldoms.sort(key=lambda j: j[1].lower())
            jarldom_options = [f"{jid}: {name}" for jid, name in jarldoms]

        def update_soldier_options() -> None:
            selected = {r["type_var"].get() for r in soldier_rows if r["type_var"].get()}
            for r in soldier_rows:
                combo = r.get("type_combo")
                if not combo:
                    continue
                current = r["type_var"].get()
                choices = [t for t in SOLDIER_TYPES if t not in selected or t == current]
                combo.config(values=choices)

        def create_soldier_row(s_type: str = "", s_count: int = 0, blank: bool = False):
            row = {}
            frame = ttk.Frame(soldier_frame)
            type_var = tk.StringVar(value=s_type)
            count_var = tk.StringVar(value=str(s_count))
            type_combo = ttk.Combobox(frame, textvariable=type_var, state="readonly", width=15)
            count_entry = ttk.Entry(frame, textvariable=count_var, width=6)
            del_btn = ttk.Button(frame, text="Radera", command=lambda r=row: remove_soldier_row(r))
            type_combo.pack(side=tk.LEFT, padx=5)
            count_entry.pack(side=tk.LEFT, padx=5)
            del_btn.pack(side=tk.LEFT, padx=5)
            frame.pack(fill="x", pady=2)
            row.update({"frame": frame, "type_var": type_var, "count_var": count_var, "type_combo": type_combo, "blank": blank})
            soldier_rows.append(row)

            def on_type_change(*_args, r=row):
                selected = r["type_var"].get()
                if selected:
                    for other in soldier_rows:
                        if other is not r and other["type_var"].get() == selected:
                            r["type_var"].set("")
                            return
                if r.get("blank") and r["type_var"].get():
                    r["blank"] = False
                    add_blank_soldier_row_if_needed()
                update_soldier_options()

            type_var.trace_add("write", on_type_change)
            update_soldier_options()

        def remove_soldier_row(row):
            if row in soldier_rows:
                row["frame"].destroy()
                soldier_rows.remove(row)
                add_blank_soldier_row_if_needed()
                update_soldier_options()

        def add_blank_soldier_row_if_needed():
            if not any(r.get("blank") for r in soldier_rows):
                create_soldier_row(blank=True)
            update_soldier_options()

        def update_animal_options() -> None:
            selected = {r["type_var"].get() for r in animal_rows if r["type_var"].get()}
            for r in animal_rows:
                combo = r.get("type_combo")
                if not combo:
                    continue
                current = r["type_var"].get()
                choices = [t for t in ANIMAL_TYPES if t not in selected or t == current]
                combo.config(values=choices)

        def create_animal_row(a_type: str = "", a_count: int = 0, blank: bool = False):
            row = {}
            frame = ttk.Frame(animal_frame)
            type_var = tk.StringVar(value=a_type)
            count_var = tk.StringVar(value=str(a_count))
            type_combo = ttk.Combobox(frame, textvariable=type_var, state="readonly", width=15)
            count_entry = ttk.Entry(frame, textvariable=count_var, width=6)
            del_btn = ttk.Button(frame, text="Radera", command=lambda r=row: remove_animal_row(r))
            type_combo.pack(side=tk.LEFT, padx=5)
            count_entry.pack(side=tk.LEFT, padx=5)
            del_btn.pack(side=tk.LEFT, padx=5)
            frame.pack(fill="x", pady=2)
            row.update({"frame": frame, "type_var": type_var, "count_var": count_var, "type_combo": type_combo, "blank": blank})
            animal_rows.append(row)

            def on_type_change(*_args, r=row):
                if r.get("blank") and r["type_var"].get():
                    r["blank"] = False
                    add_blank_animal_row_if_needed()
                update_animal_options()

            type_var.trace_add("write", on_type_change)
            update_animal_options()

        def remove_animal_row(row):
            if row in animal_rows:
                row["frame"].destroy()
                animal_rows.remove(row)
                add_blank_animal_row_if_needed()
                update_animal_options()

        def add_blank_animal_row_if_needed():
            if not any(r.get("blank") for r in animal_rows):
                create_animal_row(blank=True)
            update_animal_options()

        def update_character_options() -> None:
            selected = {r["type_var"].get() for r in character_rows if r["type_var"].get()}
            for r in character_rows:
                combo = r.get("type_combo")
                if not combo:
                    continue
                current = r["type_var"].get()
                choices = [t for t in CHARACTER_TYPES if t not in selected or t == current]
                combo.config(values=choices)

        def create_character_row(c_type: str = "", ruler_id: int | None = None, blank: bool = False):
            row = {}
            frame = ttk.Frame(character_frame)
            type_var = tk.StringVar(value=c_type)
            ruler_var = tk.StringVar()
            type_combo = ttk.Combobox(frame, textvariable=type_var, state="readonly", width=20)
            ruler_combo = ttk.Combobox(frame, textvariable=ruler_var, values=jarldom_options, state="readonly", width=40)
            del_btn = ttk.Button(frame, text="Radera", command=lambda r=row: remove_character_row(r))
            type_combo.pack(side=tk.LEFT, padx=5)
            ruler_combo.pack(side=tk.LEFT, padx=5)
            del_btn.pack(side=tk.LEFT, padx=5)
            frame.pack(fill="x", pady=2)
            row.update({
                "frame": frame,
                "type_var": type_var,
                "ruler_var": ruler_var,
                "type_combo": type_combo,
                "ruler_combo": ruler_combo,
                "blank": blank,
            })
            character_rows.append(row)

            if ruler_id is not None:
                for opt in jarldom_options:
                    if opt.startswith(f"{ruler_id}:"):
                        ruler_var.set(opt)
                        break

            def refresh_ruler_visibility(*_args, r=row):
                if r["type_var"].get() == "Härskare":
                    r["ruler_combo"].grid()
                else:
                    r["ruler_var"].set("")
                    r["ruler_combo"].grid_remove()

            def on_type_change(*_args, r=row):
                selected = r["type_var"].get()
                if selected:
                    for other in character_rows:
                        if other is not r and other["type_var"].get() == selected:
                            r["type_var"].set("")
                            return
                if r.get("blank") and r["type_var"].get():
                    r["blank"] = False
                    add_blank_character_row_if_needed()
                update_character_options()
                refresh_ruler_visibility()

            type_var.trace_add("write", on_type_change)
            refresh_ruler_visibility()
            update_character_options()

        def remove_character_row(row):
            if row in character_rows:
                row["frame"].destroy()
                character_rows.remove(row)
                add_blank_character_row_if_needed()
                update_character_options()

        def add_blank_character_row_if_needed():
            if not any(r.get("blank") for r in character_rows):
                create_character_row(blank=True)
            update_character_options()

        def update_building_options() -> None:
            selected = {r["type_var"].get() for r in building_rows if r["type_var"].get()}
            for r in building_rows:
                combo = r.get("type_combo")
                if not combo:
                    continue
                current = r["type_var"].get()
                choices = [t for t in BUILDING_TYPES if t not in selected or t == current]
                combo.config(values=choices)

        def create_building_row(b_type: str = "", b_count: int = 0, blank: bool = False):
            row = {}
            frame = ttk.Frame(building_frame)
            type_var = tk.StringVar(value=b_type)
            count_var = tk.StringVar(value=str(b_count))
            type_combo = ttk.Combobox(frame, textvariable=type_var, state="readonly", width=20)
            count_entry = ttk.Entry(frame, textvariable=count_var, width=6)
            del_btn = ttk.Button(frame, text="Radera", command=lambda r=row: remove_building_row(r))
            type_combo.pack(side=tk.LEFT, padx=5)
            count_entry.pack(side=tk.LEFT, padx=5)
            del_btn.pack(side=tk.LEFT, padx=5)
            frame.pack(fill="x", pady=2)
            row.update({"frame": frame, "type_var": type_var, "count_var": count_var, "type_combo": type_combo, "blank": blank})
            building_rows.append(row)

            def on_type_change(*_args, r=row):
                selected = r["type_var"].get()
                if selected:
                    for other in building_rows:
                        if other is not r and other["type_var"].get() == selected:
                            r["type_var"].set("")
                            return
                if r.get("blank") and r["type_var"].get():
                    r["blank"] = False
                    add_blank_building_row_if_needed()
                update_building_options()

            type_var.trace_add("write", on_type_change)
            update_building_options()

        def remove_building_row(row):
            if row in building_rows:
                row["frame"].destroy()
                building_rows.remove(row)
                add_blank_building_row_if_needed()
                update_building_options()

        def add_blank_building_row_if_needed():
            if not any(r.get("blank") for r in building_rows):
                create_building_row(blank=True)
            update_building_options()

        for c in node_data.get("craftsmen", []):
            ctype = c.get("type", "")
            count = c.get("count", 1)
            create_craftsman_row(ctype, count)

        for s in node_data.get("soldiers", []):
            stype = s.get("type", "")
            scount = s.get("count", 0)
            create_soldier_row(stype, scount)

        for ch in node_data.get("characters", []):
            ctype = ch.get("type", "")
            rid = ch.get("ruler_id")
            if isinstance(rid, str) and rid.isdigit():
                rid = int(rid)
            elif not isinstance(rid, int):
                rid = None
            create_character_row(ctype, rid)

        for a in node_data.get("animals", []):
            atype = a.get("type", "")
            acount = a.get("count", 0)
            create_animal_row(atype, acount)

        for b in node_data.get("buildings", []):
            btype = b.get("type", "")
            bcount = b.get("count", 0)
            create_building_row(btype, bcount)

        add_blank_row_if_needed()
        update_craftsman_options()
        add_blank_soldier_row_if_needed()
        update_soldier_options()
        add_blank_character_row_if_needed()
        update_character_options()
        add_blank_animal_row_if_needed()
        update_animal_options()
        add_blank_building_row_if_needed()
        update_building_options()

        def refresh_settlement_visibility(*args):
            if res_var.get() == "Bosättning":
                settlement_frame.grid(
                    row=settlement_row,
                    column=0,
                    columnspan=2,
                    sticky="ew",
                    pady=5,
                )
            else:
                settlement_frame.grid_remove()

            if res_var.get() == "Soldater":
                soldier_label.grid()
                soldier_frame.grid()
            else:
                soldier_label.grid_remove()
                soldier_frame.grid_remove()

            if res_var.get() == "Djur":
                animal_label.grid()
                animal_frame.grid()
            else:
                animal_label.grid_remove()
                animal_frame.grid_remove()

            if res_var.get() == "Karaktärer":
                character_label.grid()
                character_frame.grid()
            else:
                character_label.grid_remove()
                character_frame.grid_remove()

            if res_var.get() == "Byggnader":
                building_label.grid()
                building_frame.grid()
            else:
                building_label.grid_remove()
                building_frame.grid_remove()

        res_var.trace_add("write", refresh_settlement_visibility)
        refresh_settlement_visibility()

        ttk.Separator(editor_frame, orient=tk.HORIZONTAL).grid(row=row_idx, column=0, columnspan=2, sticky="ew", pady=(15, 10))
        row_idx += 1
        action_frame = ttk.Frame(editor_frame)
        action_frame.grid(row=row_idx, column=0, columnspan=2, pady=5)
        row_idx += 1

        def update_subfiefs_action():
            node_data["custom_name"] = custom_var.get().strip()
            node_data["res_type"] = res_var.get().strip()
            node_data["settlement_type"] = settlement_type_var.get().strip()
            try:
                node_data["free_peasants"] = int(free_var.get() or "0", 10)
            except (tk.TclError, ValueError):
                node_data["free_peasants"] = 0
            try:
                node_data["unfree_peasants"] = int(unfree_var.get() or "0", 10)
            except (tk.TclError, ValueError):
                node_data["unfree_peasants"] = 0
            try:
                node_data["thralls"] = int(thrall_var.get() or "0", 10)
            except (tk.TclError, ValueError):
                node_data["thralls"] = 0
            try:
                node_data["burghers"] = int(burgher_var.get() or "0", 10)
            except (tk.TclError, ValueError):
                node_data["burghers"] = 0
            node_data["craftsmen"] = [
                {"type": r["type_var"].get(), "count": int(r["count_var"].get())}
                for r in craftsman_rows
                if r["type_var"].get()
            ]
            node_data["soldiers"] = [
                {"type": r["type_var"].get(), "count": int(r["count_var"].get() or 0)}
                for r in soldier_rows
                if r["type_var"].get()
            ]
            node_data["characters"] = [
                {
                    "type": r["type_var"].get(),
                    "ruler_id": (
                        int(r["ruler_var"].get().split(":")[0])
                        if r["type_var"].get() == "Härskare" and r["ruler_var"].get()
                        else None
                    ),
                }
                for r in character_rows
                if r["type_var"].get()
            ]
            if res_var.get() == "Djur":
                node_data["animals"] = [
                    {"type": r["type_var"].get(), "count": int(r["count_var"].get() or 0)}
                    for r in animal_rows
                    if r["type_var"].get()
                ]
            else:
                node_data.pop("animals", None)
            node_data["buildings"] = [
                {"type": r["type_var"].get(), "count": int(r["count_var"].get() or 0)}
                for r in building_rows
                if r["type_var"].get()
            ]
            if res_var.get() in {"Hav", "Flod"}:
                node_data["fish_quality"] = fish_var.get()
                try:
                    node_data["fishing_boats"] = int(boats_var.get() or "0", 10)
                except (tk.TclError, ValueError):
                    node_data["fishing_boats"] = 0
            else:
                node_data.pop("fish_quality", None)
                node_data.pop("fishing_boats", None)
            temp_data = dict(node_data)
            if res_var.get() in {"Vildmark", "Jaktmark"}:
                try:
                    node_data["tunnland"] = int(area_var.get() or "0", 10)
                except (tk.TclError, ValueError):
                    node_data["tunnland"] = 0
                temp_data["population"] = 0
            elif res_var.get() == "Djur":
                temp_data["population"] = 0
            else:
                try:
                    manual_pop = int(pop_var.get() or "0")
                except (tk.TclError, ValueError):
                    manual_pop = 0
                temp_data["population"] = manual_pop
            node_data["population"] = self.calculate_population_from_fields(temp_data)
            node_data["num_subfiefs"] = len(node_data.get("children", [])) + 1
            self.update_subfiefs_for_node(node_data)

        ttk.Button(action_frame, text="Skapa Nod", command=update_subfiefs_action).pack(side=tk.LEFT, padx=5)

        def save_node_action():
            old_custom = node_data.get("custom_name", "")
            old_pop = node_data.get("population", 0)
            old_type = node_data.get("res_type", "")
            old_settlement_type = node_data.get("settlement_type", "By")
            old_free = int(node_data.get("free_peasants", 0))
            old_unfree = int(node_data.get("unfree_peasants", 0))
            old_thralls = int(node_data.get("thralls", 0))
            old_burghers = int(node_data.get("burghers", 0))
            old_craftsmen = node_data.get("craftsmen", [])
            old_soldiers = node_data.get("soldiers", [])
            old_characters = node_data.get("characters", [])
            old_animals = node_data.get("animals", [])
            old_buildings = node_data.get("buildings", [])
            old_area = node_data.get("tunnland", 0)
            old_quality = node_data.get("fish_quality", node_data.get("water_quality", "Normalt"))
            old_boats = int(node_data.get("fishing_boats", 0))
            old_gamekeeper = node_data.get("gamekeeper_id")
            old_hunters = int(node_data.get("hunters", 0))
            old_manor = int(node_data.get("manor_land", 0))
            old_cultivated = int(node_data.get("cultivated_land", 0))
            old_cq = int(node_data.get("cultivated_quality", 3))
            old_fallow = int(node_data.get("fallow_land", 0))
            old_has_herd = bool(node_data.get("has_herd", False))
            old_forest = int(node_data.get("forest_land", 0))
            old_hq = int(node_data.get("hunt_quality", 3))
            old_law = int(node_data.get("hunting_law", 0))

            new_custom = custom_var.get().strip()
            try:
                manual_pop = int(pop_var.get() or "0")
            except (tk.TclError, ValueError):
                manual_pop = 0
            try:
                manual_area = int(area_var.get() or "0", 10)
            except (tk.TclError, ValueError):
                manual_area = 0
            new_type = res_var.get().strip()
            new_settlement_type = settlement_type_var.get().strip()
            try:
                new_free = int(free_var.get() or "0", 10)
            except (tk.TclError, ValueError):
                new_free = 0
            try:
                new_unfree = int(unfree_var.get() or "0", 10)
            except (tk.TclError, ValueError):
                new_unfree = 0
            try:
                new_thralls = int(thrall_var.get() or "0", 10)
            except (tk.TclError, ValueError):
                new_thralls = 0
            try:
                new_burghers = int(burgher_var.get() or "0", 10)
            except (tk.TclError, ValueError):
                new_burghers = 0
            new_quality = fish_var.get()
            try:
                new_boats = int(boats_var.get() or "0", 10)
            except (tk.TclError, ValueError):
                new_boats = 0
            try:
                new_manor = int(manor_var.get() or "0", 10)
            except (tk.TclError, ValueError):
                new_manor = 0
            try:
                new_cultivated = int(cultivated_var.get() or "0", 10)
            except (tk.TclError, ValueError):
                new_cultivated = 0
            try:
                new_cq = int(cq_var.get() or "3", 10)
            except (tk.TclError, ValueError):
                new_cq = 3
            try:
                new_fallow = int(fallow_var.get() or "0", 10)
            except (tk.TclError, ValueError):
                new_fallow = 0
            new_has_herd = herd_var.get() == "Ja"
            try:
                new_forest = int(forest_var.get() or "0", 10)
            except (tk.TclError, ValueError):
                new_forest = 0
            try:
                new_hq = int(hunt_var.get() or "3", 10)
            except (tk.TclError, ValueError):
                new_hq = 3
            try:
                new_law = int(law_var.get() or "0", 10)
            except (tk.TclError, ValueError):
                new_law = 0
            jk_sel = gamekeeper_var.get()
            new_gamekeeper = None
            if jk_sel and jk_sel != "Ingen karaktär" and ":" in jk_sel:
                new_gamekeeper = int(jk_sel.split(":")[0])
            try:
                new_hunters = int(hunter_var.get() or "0", 10)
            except (tk.TclError, ValueError):
                new_hunters = 0
            try:
                new_manor = int(manor_var.get() or "0", 10)
            except (tk.TclError, ValueError):
                new_manor = 0
            try:
                new_cultivated = int(cultivated_var.get() or "0", 10)
            except (tk.TclError, ValueError):
                new_cultivated = 0
            try:
                new_cq = int(cq_var.get() or "3", 10)
            except (tk.TclError, ValueError):
                new_cq = 3
            try:
                new_fallow = int(fallow_var.get() or "0", 10)
            except (tk.TclError, ValueError):
                new_fallow = 0
            new_has_herd = herd_var.get() == "Ja"
            try:
                new_forest = int(forest_var.get() or "0", 10)
            except (tk.TclError, ValueError):
                new_forest = 0
            try:
                new_hq = int(hunt_var.get() or "3", 10)
            except (tk.TclError, ValueError):
                new_hq = 3
            try:
                new_law = int(law_var.get() or "0", 10)
            except (tk.TclError, ValueError):
                new_law = 0
            new_craftsmen = [
                {"type": r["type_var"].get(), "count": int(r["count_var"].get())}
                for r in craftsman_rows
                if r["type_var"].get()
            ]
            new_soldiers = [
                {"type": r["type_var"].get(), "count": int(r["count_var"].get() or 0)}
                for r in soldier_rows
                if r["type_var"].get()
            ]
            new_characters = [
                {
                    "type": r["type_var"].get(),
                    "ruler_id": (
                        int(r["ruler_var"].get().split(":")[0])
                        if r["type_var"].get() == "Härskare" and r["ruler_var"].get()
                        else None
                    ),
                }
                for r in character_rows
                if r["type_var"].get()
            ]
            if new_type == "Djur":
                new_animals = [
                    {"type": r["type_var"].get(), "count": int(r["count_var"].get() or 0)}
                    for r in animal_rows
                    if r["type_var"].get()
                ]
            else:
                new_animals = []
            new_buildings = [
                {"type": r["type_var"].get(), "count": int(r["count_var"].get() or 0)}
                for r in building_rows
                if r["type_var"].get()
            ]
            new_soldiers = [
                {"type": r["type_var"].get(), "count": int(r["count_var"].get() or 0)}
                for r in soldier_rows
                if r["type_var"].get()
            ]
            new_characters = [
                {
                    "type": r["type_var"].get(),
                    "ruler_id": (
                        int(r["ruler_var"].get().split(":")[0])
                        if r["type_var"].get() == "Härskare" and r["ruler_var"].get()
                        else None
                    ),
                }
                for r in character_rows
                if r["type_var"].get()
            ]

            if new_type in {"Vildmark", "Djur"}:
                new_pop = 0
            else:
                new_pop = self.calculate_population_from_fields({
                    "population": manual_pop,
                    "free_peasants": new_free,
                    "unfree_peasants": new_unfree,
                    "thralls": new_thralls,
                    "burghers": new_burghers,
                })

            changes = False
            details = []
            if old_custom != new_custom:
                node_data["custom_name"] = new_custom
                changes = True
                details.append(f"Namn: '{old_custom}' -> '{new_custom}'")
            if old_type == "Vildmark":
                if old_area != manual_area:
                    node_data["tunnland"] = manual_area
                    changes = True
                    details.append(f"Tunnland: {old_area} -> {manual_area}")
            else:
                if old_pop != new_pop:
                    node_data["population"] = new_pop
                    changes = True
                    details.append(f"Befolkning: {old_pop} -> {new_pop}")
            if old_type != new_type:
                node_data["res_type"] = new_type
                changes = True
                details.append(f"Typ: '{old_type}' -> '{new_type}'")
            if old_settlement_type != new_settlement_type:
                node_data["settlement_type"] = new_settlement_type
                changes = True
            if old_free != new_free:
                node_data["free_peasants"] = new_free
                changes = True
            if old_unfree != new_unfree:
                node_data["unfree_peasants"] = new_unfree
                changes = True
            if old_thralls != new_thralls:
                node_data["thralls"] = new_thralls
                changes = True
            if old_burghers != new_burghers:
                node_data["burghers"] = new_burghers
                changes = True
            if new_type == "Gods":
                if old_manor != new_manor:
                    node_data["manor_land"] = new_manor
                    changes = True
                    diff = new_manor - old_manor
                    jarldom_id = node_id
                    while jarldom_id is not None and self.get_depth_of_node(jarldom_id) > 3:
                        jnode = self.world_data.get("nodes", {}).get(str(jarldom_id))
                        if not jnode:
                            break
                        jarldom_id = jnode.get("parent_id")
                    if jarldom_id is not None:
                        jnode = self.world_data.get("nodes", {}).get(str(jarldom_id))
                        if jnode is not None:
                            try:
                                cur_area = int(jnode.get("jarldom_area", 0))
                            except (ValueError, TypeError):
                                cur_area = 0
                            jnode["jarldom_area"] = cur_area - diff
                if old_cultivated != new_cultivated:
                    node_data["cultivated_land"] = new_cultivated
                    changes = True
                if old_cq != new_cq:
                    node_data["cultivated_quality"] = new_cq
                    changes = True
                if old_fallow != new_fallow:
                    node_data["fallow_land"] = new_fallow
                    changes = True
                if old_has_herd != new_has_herd:
                    node_data["has_herd"] = new_has_herd
                    changes = True
                if old_forest != new_forest:
                    node_data["forest_land"] = new_forest
                    changes = True
                if old_hq != new_hq:
                    node_data["hunt_quality"] = new_hq
                    changes = True
                if old_law != new_law:
                    node_data["hunting_law"] = new_law
                    changes = True
            if old_craftsmen != new_craftsmen:
                node_data["craftsmen"] = new_craftsmen
                changes = True
            if old_characters != new_characters:
                node_data["characters"] = new_characters
                changes = True
            if old_soldiers != new_soldiers:
                node_data["soldiers"] = new_soldiers
                changes = True
            if new_type == "Djur":
                if old_animals != new_animals:
                    node_data["animals"] = new_animals
                    changes = True
                if "population" in node_data:
                    del node_data["population"]
                    changes = True
            else:
                if "animals" in node_data:
                    del node_data["animals"]
                    changes = True
            if old_buildings != new_buildings:
                node_data["buildings"] = new_buildings
                changes = True
            if new_type in {"Hav", "Flod"}:
                if old_quality != new_quality:
                    node_data["fish_quality"] = new_quality
                    changes = True
                if old_boats != new_boats:
                    node_data["fishing_boats"] = new_boats
                    changes = True
            else:
                if "fish_quality" in node_data:
                    del node_data["fish_quality"]
                    changes = True
                if "fishing_boats" in node_data:
                    del node_data["fishing_boats"]
                    changes = True
            if new_type != "Gods":
                for key in (
                    "manor_land",
                    "cultivated_land",
                    "cultivated_quality",
                    "fallow_land",
                    "has_herd",
                    "forest_land",
                    "hunt_quality",
                    "hunting_law",
                ):
                    if key in node_data:
                        del node_data[key]
                        changes = True
            if old_gamekeeper != new_gamekeeper:
                node_data["gamekeeper_id"] = new_gamekeeper
                changes = True
            if old_hunters != new_hunters:
                node_data["hunters"] = new_hunters
                changes = True

            if changes:
                self.world_manager.update_population_totals()
                self.save_current_world()
                status = f"Resurs {node_id} uppdaterad: " + ", ".join(details)
                self.add_status_message(status)
                self.refresh_tree_item(node_id)
            else:
                self.add_status_message(f"Resurs {node_id}: Inga ändringar att spara.")

        save_button.configure(command=save_node_action)
        ttk.Button(action_frame, text="Spara Resurs", command=save_node_action).pack(side=tk.LEFT, padx=5)
        self.pending_save_callback = save_node_action

        delete_back_frame = ttk.Frame(editor_frame)
        delete_back_frame.grid(row=row_idx, column=0, columnspan=2, pady=(20, 5))
        row_idx += 1

        def unsaved_changes() -> bool:
            try:
                manual_pop = int(pop_var.get() or "0")
            except (tk.TclError, ValueError):
                manual_pop = 0
            try:
                manual_area = int(area_var.get() or "0", 10)
            except (tk.TclError, ValueError):
                manual_area = 0
            current_sub = len(node_data.get("children", []))
            try:
                new_free = int(free_var.get() or "0", 10)
            except (tk.TclError, ValueError):
                new_free = 0
            try:
                new_unfree = int(unfree_var.get() or "0", 10)
            except (tk.TclError, ValueError):
                new_unfree = 0
            try:
                new_thralls = int(thrall_var.get() or "0", 10)
            except (tk.TclError, ValueError):
                new_thralls = 0
            try:
                new_burghers = int(burgher_var.get() or "0", 10)
            except (tk.TclError, ValueError):
                new_burghers = 0
            new_quality = fish_var.get()
            try:
                new_boats = int(boats_var.get() or "0", 10)
            except (tk.TclError, ValueError):
                new_boats = 0
            new_craftsmen = [
                {"type": r["type_var"].get(), "count": int(r["count_var"].get())}
                for r in craftsman_rows
                if r["type_var"].get()
            ]
            new_soldiers = [
                {"type": r["type_var"].get(), "count": int(r["count_var"].get() or 0)}
                for r in soldier_rows
                if r["type_var"].get()
            ]
            new_characters = [
                {
                    "type": r["type_var"].get(),
                    "ruler_id": (
                        int(r["ruler_var"].get().split(":")[0])
                        if r["type_var"].get() == "Härskare" and r["ruler_var"].get()
                        else None
                    ),
                }
                for r in character_rows
                if r["type_var"].get()
            ]
            if res_var.get() == "Djur":
                new_animals = [
                    {"type": r["type_var"].get(), "count": int(r["count_var"].get() or 0)}
                    for r in animal_rows
                    if r["type_var"].get()
                ]
            else:
                new_animals = []
            new_buildings = [
                {"type": r["type_var"].get(), "count": int(r["count_var"].get() or 0)}
                for r in building_rows
                if r["type_var"].get()
            ]
            if res_var.get() in {"Vildmark", "Djur"}:
                new_pop = 0
            else:
                new_pop = self.calculate_population_from_fields({
                    "population": manual_pop,
                    "free_peasants": new_free,
                    "unfree_peasants": new_unfree,
                    "thralls": new_thralls,
                    "burghers": new_burghers,
                })

            return (
                res_var.get().strip() != node_data.get("res_type", JARLDOM_RESOURCE_TYPES[0])
                or custom_var.get().strip() != node_data.get("custom_name", "")
                or (res_var.get() not in {"Vildmark", "Jaktmark"} and new_pop != node_data.get("population", 0))
                or (res_var.get() in {"Vildmark", "Jaktmark"} and manual_area != node_data.get("tunnland", 0))
                or settlement_type_var.get().strip() != node_data.get("settlement_type", "By")
                or new_free != int(node_data.get("free_peasants", 0))
                or new_unfree != int(node_data.get("unfree_peasants", 0))
                or new_thralls != int(node_data.get("thralls", 0))
                or new_burghers != int(node_data.get("burghers", 0))
                or new_craftsmen != node_data.get("craftsmen", [])
                or new_soldiers != node_data.get("soldiers", [])
                or new_characters != node_data.get("characters", [])
                or new_animals != node_data.get("animals", [])
                or new_buildings != node_data.get("buildings", [])
                or current_sub != node_data.get("num_subfiefs", 0)
                or new_quality != node_data.get("fish_quality", node_data.get("water_quality", "Normalt"))
                or new_boats != int(node_data.get("fishing_boats", 0))
                or new_gamekeeper != node_data.get("gamekeeper_id")
                or new_hunters != int(node_data.get("hunters", 0))
                or new_manor != int(node_data.get("manor_land", 0))
                or new_cultivated != int(node_data.get("cultivated_land", 0))
                or new_cq != int(node_data.get("cultivated_quality", 3))
                or new_fallow != int(node_data.get("fallow_land", 0))
                or new_has_herd != bool(node_data.get("has_herd", False))
                or new_forest != int(node_data.get("forest_land", 0))
                or new_hq != int(node_data.get("hunt_quality", 3))
                or new_law != int(node_data.get("hunting_law", 0))
            )

        del_button = self._create_delete_button(delete_back_frame, node_data, unsaved_changes)
        del_button.pack(side=tk.LEFT, padx=10)
        ttk.Button(delete_back_frame, text="< Stäng Vy", command=self.show_no_world_view).pack(side=tk.LEFT, padx=10)


    def show_neighbor_editor(self, node_data):
        """Displays the UI for editing the neighbors of a Jarldom."""
        self._clear_right_frame()
        node_id = node_data['node_id']
        custom_name = node_data.get("custom_name", f"Jarldom {node_id}")

        # --- Main container frame ---
        scroll_view = ScrollableFrame(self.right_frame, padding="10 10 10 10")
        scroll_view.pack(fill="both", expand=True)
        view_frame = scroll_view.content

        ttk.Label(view_frame, text=f"Redigera Grannar för: {custom_name}", font=("Arial", 14)).pack(pady=(0, 15))

        # --- Get list of potential neighbors (other Jarldoms) ---
        other_jarldoms_data = []
        if self.world_data and "nodes" in self.world_data:
            for jid_str, jnode in self.world_data["nodes"].items():
                try:
                    jid = int(jid_str)
                except ValueError:
                    continue  # Skip non-integer keys
                # Exclude self, check depth == 3
                if jid != node_id and self.get_depth_of_node(jid) == 3:
                    jname = jnode.get("custom_name", f"Jarldom {jid}")
                    neighbor_count = sum(
                        1
                        for nb in jnode.get("neighbors", [])
                        if nb.get("id") is not None
                    )
                    other_jarldoms_data.append(
                        {
                            "id": jid,
                            "name": jname,
                            "neighbor_count": neighbor_count,
                        }
                    )

        # Sort by name
        other_jarldoms_data.sort(key=lambda j: j["name"].lower())

        # Prepare display list for comboboxes
        neighbor_choices = [
            NEIGHBOR_NONE_STR,
            NEIGHBOR_OTHER_STR,
        ] + [
            f"{j['id']}: {j['name']} ({j['neighbor_count']})" for j in other_jarldoms_data
        ]
        valid_neighbor_ids = {j['id'] for j in other_jarldoms_data}  # Set of valid Jarldom IDs

        # --- Frame for the neighbor rows ---
        neighbors_frame = ttk.Frame(view_frame)
        neighbors_frame.pack(fill="x", pady=10)

        # Store combobox variables and widgets
        self.neighbor_vars = [tk.StringVar() for _ in range(MAX_NEIGHBORS)]
        self.border_vars = [tk.StringVar() for _ in range(MAX_NEIGHBORS)]
        self.neighbor_combos = [None] * MAX_NEIGHBORS # Store widget refs if needed later
        self.border_combos = [None] * MAX_NEIGHBORS

        # Get current neighbors and ensure list is correct length/format
        current_neighbors = node_data.get("neighbors", [])
        validated_current_neighbors = []
        for i in range(MAX_NEIGHBORS):
            n_data = {}
            if i < len(current_neighbors) and isinstance(current_neighbors[i], dict):
                n_data = current_neighbors[i]
            n_id = n_data.get("id")
            n_border = n_data.get("border", NEIGHBOR_NONE_STR)
            final_id = None
            if n_id == NEIGHBOR_OTHER_STR: final_id = NEIGHBOR_OTHER_STR
            elif isinstance(n_id, int) and n_id in valid_neighbor_ids: final_id = n_id
            elif str(n_id).isdigit() and int(n_id) in valid_neighbor_ids: final_id = int(n_id)
            if n_border not in BORDER_TYPES: n_border = NEIGHBOR_NONE_STR
            if final_id is None: n_border = NEIGHBOR_NONE_STR
            validated_current_neighbors.append({"id": final_id, "border": n_border})

        # Update node_data immediately if validation changed anything (defensive)
        if node_data.get("neighbors") != validated_current_neighbors:
            print(f"Corrected neighbor list format for node {node_id} on editor open.")
            node_data["neighbors"] = validated_current_neighbors
            # No save here, just ensures consistency for the editor setup below


        # --- Create 6 rows for neighbors ---
        for i in range(MAX_NEIGHBORS):
            row_frame = ttk.Frame(neighbors_frame)
            row_frame.pack(fill="x", pady=3)

            ttk.Label(row_frame, text=f"Slot {i+1}:", width=7).pack(side=tk.LEFT, padx=(0, 5)) # Use slot index

            # Neighbor selection combobox
            neighbor_combo = ttk.Combobox(row_frame, textvariable=self.neighbor_vars[i], values=neighbor_choices, state="readonly", width=40, style="BlackWhite.TCombobox") # Default style

            current_neighbor_id = validated_current_neighbors[i].get("id")
            initial_neighbor_value = NEIGHBOR_NONE_STR
            is_valid_neighbor = False

            if current_neighbor_id == NEIGHBOR_OTHER_STR:
                initial_neighbor_value = NEIGHBOR_OTHER_STR
                is_valid_neighbor = True # Treat "Other" as valid for border setting
            elif isinstance(current_neighbor_id, int):
                # Find the display string for this ID
                found = False
                for j in other_jarldoms_data:
                        if j["id"] == current_neighbor_id:
                            initial_neighbor_value = f"{j['id']}: {j['name']}"
                            found = True
                            break
                if found:
                        neighbor_combo.config(style="Highlight.TCombobox") # Highlight existing valid neighbor
                        is_valid_neighbor = True
                else: # ID exists but isn't in the current list (maybe deleted?)
                        initial_neighbor_value = f"{current_neighbor_id}: Okänd/Raderad?"
                        # Keep ID in validated list? No, validation already cleared it. Set var correctly.
                        initial_neighbor_value = NEIGHBOR_NONE_STR


            self.neighbor_vars[i].set(initial_neighbor_value)
            neighbor_combo.pack(side=tk.LEFT, padx=5, fill='x', expand=True) # Allow expansion
            self.neighbor_combos[i] = neighbor_combo # Store widget if needed


            # Border type selection combobox
            border_combo = ttk.Combobox(row_frame, textvariable=self.border_vars[i], values=BORDER_TYPES, state="readonly", width=15)
            current_border = validated_current_neighbors[i].get("border", NEIGHBOR_NONE_STR)
            # Set border var based on validated neighbor and border
            self.border_vars[i].set(current_border if (is_valid_neighbor or current_neighbor_id is not None) else NEIGHBOR_NONE_STR)
            border_combo.pack(side=tk.LEFT, padx=5)
            self.border_combos[i] = border_combo # Store widget if needed

        # --- Save and Back Buttons ---
        button_frame = ttk.Frame(view_frame)
        button_frame.pack(pady=10)

        def save_neighbors_action():
            if not self.world_data:
                return
            new_neighbors = []
            something_changed = False
            for i in range(MAX_NEIGHBORS):
                nb_val = self.neighbor_vars[i].get()
                border_val = self.border_vars[i].get()
                nb_id = None
                if nb_val == NEIGHBOR_OTHER_STR:
                    nb_id = NEIGHBOR_OTHER_STR
                elif ":" in nb_val:
                    try:
                        cand = int(nb_val.split(":")[0])
                        if cand in valid_neighbor_ids:
                            nb_id = cand
                    except ValueError:
                        nb_id = None
                if nb_val == NEIGHBOR_NONE_STR or nb_id is None:
                    nb_id = None
                    border_val = NEIGHBOR_NONE_STR
                if border_val not in BORDER_TYPES:
                    border_val = NEIGHBOR_NONE_STR
                entry = {"id": nb_id, "border": border_val}
                new_neighbors.append(entry)
                if i >= len(node_data.get("neighbors", [])) or node_data["neighbors"][i] != entry:
                    something_changed = True

            if something_changed:
                node_data["neighbors"] = new_neighbors
                # Ensure bidirectional links are kept in sync
                self.world_manager.update_neighbors_for_node(node_id, new_neighbors)
                self.save_current_world()
                self.add_status_message(
                    f"Jarldom {node_id}: Grannar uppdaterade."
                )
                self.refresh_tree_item(node_id)
                if self.static_map_canvas and self.static_map_canvas.winfo_exists():
                    self.draw_static_border_lines()
            else:
                self.add_status_message(f"Jarldom {node_id}: Inga ändringar i grannar.")

        ttk.Button(button_frame, text="Spara Grannar", command=save_neighbors_action).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="< Tillbaka", command=lambda n=node_data: self.show_node_view(n)).pack(side=tk.LEFT, padx=5)


    # --------------------------------------------------
    # Subnode Management
    # --------------------------------------------------
    def update_subfiefs_for_node(self, node_data):
        """
        Manages the creation/deletion of subfiefs based on the 'num_subfiefs' value.
        Hierarchy: Kungarike(d0) -> Furstendöme(d1) -> Hertigdöme(d2) -> Jarldöme(d3) -> Resurs(d4+)
        Jarldömen (d3) have res_type="Resurs" and a random name in custom_name.
        """
        open_items, selection = self.store_tree_state()

        self.world_manager.update_subfiefs_for_node(node_data)
        self.world_manager.clear_depth_cache()
        self.world_manager.update_population_totals()

        self.save_current_world()
        self.populate_tree()  # Refresh the tree
        self.restore_tree_state(open_items, selection)
        self.show_node_view(node_data)  # Re-show the editor

    def delete_node_and_descendants(self, node_id):
        """Recursively deletes a node and all its children from world_data."""
        deleted = self.world_manager.delete_node_and_descendants(node_id)
        self.world_manager.clear_depth_cache()
        self.world_manager.update_population_totals()
        return deleted

    # --------------------------------------------------
    # Map Views
    # --------------------------------------------------
    def show_map_mode_buttons(self):
        """Displays buttons to switch between static and dynamic map views."""
        # Clear existing map mode buttons (except the base "Visa Karta")
        for widget in self.map_button_frame.winfo_children():
            if widget != self.map_mode_base_button:
                widget.destroy()

        ttk.Button(self.map_button_frame, text="Statisk", command=self.show_static_map_view).pack(side=tk.LEFT, padx=2)
        ttk.Button(self.map_button_frame, text="Dynamisk", command=self.open_dynamic_map_view).pack(side=tk.LEFT, padx=2)

    def hide_map_mode_buttons(self):
        """Hides the static and dynamic map buttons."""
        for widget in self.map_button_frame.winfo_children():
            if widget != self.map_mode_base_button:
                widget.destroy()
        self._clear_right_frame() # Also clear map view when hiding buttons

    def show_static_map_view(self):
        """Displays the static hex-based map of Jarldoms."""
        self._clear_right_frame()
        map_fr = ttk.Frame(self.right_frame)
        map_fr.pack(fill="both", expand=True)
        map_fr.grid_rowconfigure(0, weight=1)
        map_fr.grid_columnconfigure(0, weight=1)
        self.static_map_canvas = tk.Canvas(map_fr, bg="white", scrollregion=(0,0,3000,2000))
        self.static_map_canvas.grid(row=0, column=0, sticky="nsew")
        xsc = ttk.Scrollbar(map_fr, orient="horizontal", command=self.static_map_canvas.xview)
        xsc.grid(row=1, column=0, sticky="ew")
        ysc = ttk.Scrollbar(map_fr, orient="vertical", command=self.static_map_canvas.yview)
        ysc.grid(row=0, column=1, sticky="ns")
        self.static_map_canvas.config(xscrollcommand=xsc.set, yscrollcommand=ysc.set)

        # Map logic
        rows = max(self.static_rows, 30)
        cols = max(self.static_cols, 30)
        self.map_logic = StaticMapLogic(
            self.world_data,
            rows,
            cols,
            hex_size=30,
            spacing=self.hex_spacing,
        )

        if self.map_static_positions:
            self.map_logic.map_static_positions = {}
            self.map_logic.static_grid_occupied = [
                [None] * self.map_logic.cols for _ in range(self.map_logic.rows)
            ]
            for nid, (r, c) in self.map_static_positions.items():
                while r >= self.map_logic.rows:
                    self.map_logic.static_grid_occupied.append(
                        [None] * self.map_logic.cols
                    )
                    self.map_logic.rows += 1
                while c >= self.map_logic.cols:
                    for row in self.map_logic.static_grid_occupied:
                        row.append(None)
                    self.map_logic.cols += 1
                self.map_logic.map_static_positions[nid] = (r, c)
                self.map_logic.static_grid_occupied[r][c] = nid
            self.static_rows = self.map_logic.rows
            self.static_cols = self.map_logic.cols
            self.static_grid_occupied = self.map_logic.static_grid_occupied
        else:
            self.place_jarldomes_bfs()

        # Bottom button bar
        btn_fr = ttk.Frame(self.right_frame, style="Tool.TFrame")
        btn_fr.pack(fill="x", pady=5)
        ttk.Button(btn_fr, text="< Tillbaka", command=self.show_no_world_view).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_fr, text="Gruppera Hierarki", command=self.on_hierarchy_layout).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_fr, text="Spara positioner", command=self.save_static_positions).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_fr, text="Rensa länkar", command=self.clear_all_neighbor_links).pack(side=tk.LEFT, padx=5)

        self.static_scale = 1.0
        self.static_map_canvas.bind("<MouseWheel>", self.on_static_map_zoom) # Windows/macOS
        self.static_map_canvas.bind("<Button-4>", self.on_static_map_zoom) # Linux scroll up
        self.static_map_canvas.bind("<Button-5>", self.on_static_map_zoom) # Linux scroll down

        # --- Drag and Drop for Neighbors ---
        self.static_map_canvas.bind("<ButtonPress-1>", self.on_static_map_button_press)
        self.static_map_canvas.bind("<B1-Motion>", self.on_static_map_mouse_motion)
        self.static_map_canvas.bind("<ButtonRelease-1>", self.on_static_map_button_release)

        # --- Drag hexes to new positions ---
        self.static_map_canvas.bind("<ButtonPress-3>", self.on_hex_drag_start)
        self.static_map_canvas.bind("<B3-Motion>", self.on_hex_drag_motion)
        self.static_map_canvas.bind("<ButtonRelease-3>", self.on_hex_drag_end)

        self.draw_static_hexgrid()
        self.draw_static_border_lines()

    def on_static_map_zoom(self, event):
        """Zooms the static map view."""
        if event.delta > 0 or event.num == 4:
            factor = 1.1
        else:
            factor = 0.9
        if not hasattr(self, "static_scale"):
            self.static_scale = 1.0
        self.static_scale *= factor
        self.static_scale = max(0.1, min(self.static_scale, 10.0))
        self.static_map_canvas.scale("all", 0, 0, factor, factor)

    def place_jarldomes_bfs(self):
        """Places Jarldoms on the grid using :class:`StaticMapLogic`."""
        if not self.map_logic:
            self.map_logic = StaticMapLogic(
                self.world_data,
                self.static_rows,
                self.static_cols,
                hex_size=30,
                spacing=self.hex_spacing,
            )
        self.map_logic.place_jarldomes_bfs(self.get_depth_of_node)
        self.map_static_positions = self.map_logic.map_static_positions
        self.static_grid_occupied = self.map_logic.static_grid_occupied
        self.static_rows = self.map_logic.rows
        self.static_cols = self.map_logic.cols

    def place_jarldomes_hierarchy(self):
        """Places Jarldoms grouped by hierarchy using :class:`StaticMapLogic`."""
        if not self.map_logic:
            self.map_logic = StaticMapLogic(
                self.world_data,
                self.static_rows,
                self.static_cols,
                hex_size=30,
                spacing=self.hex_spacing,
            )
        self.map_logic.place_jarldomes_hierarchy(self.get_depth_of_node)
        self.map_static_positions = self.map_logic.map_static_positions
        self.static_grid_occupied = self.map_logic.static_grid_occupied
        self.static_rows = self.map_logic.rows
        self.static_cols = self.map_logic.cols

    def auto_link_adjacent_hexes(self):
        """Create neighbor links for all adjacent hexagons."""
        if not (self.map_logic and self.world_data):
            return

        nodes = self.world_data.get("nodes", {})
        for nid1, nid2, direction in self.map_logic.adjacent_hex_pairs():
            success, _ = self.world_manager.attempt_link_neighbors(
                nid1, nid2, slot1=direction
            )
            if success:
                node1 = nodes.get(str(nid1))
                node2 = nodes.get(str(nid2))
                if node1 and node2:
                    node1["neighbors"][direction - 1]["border"] = "liten väg"
                    opp = ((direction + 2) % MAX_NEIGHBORS) + 1
                    node2["neighbors"][opp - 1]["border"] = "liten väg"
        self.save_current_world()

    def on_hierarchy_layout(self):
        """Callback for hierarchy grouping button."""
        self.place_jarldomes_hierarchy()
        self.auto_link_adjacent_hexes()
        self.draw_static_hexgrid()
        self.draw_static_border_lines()

    def draw_static_hexgrid(self):
        """Draws the hex grid and places Jarldom names."""
        if not self.static_map_canvas: return
        self.static_map_canvas.delete("all")
        hex_size = 30
        
        for r in range(self.static_rows):
            for c in range(self.static_cols):
                center_x, center_y = self.map_logic.hex_center(r, c)
                points = []
                for i in range(6):
                    # Rotate hexagons so that their flat surfaces face
                    # north and south.  Using ``60 * i`` aligns the top and
                    # bottom edges horizontally, matching the flat-top grid
                    # layout defined in :class:`StaticMapLogic`.
                    angle_deg = 60 * i
                    angle_rad = math.radians(angle_deg)
                    px = center_x + hex_size * math.cos(angle_rad)
                    py = center_y + hex_size * math.sin(angle_rad)
                    points.extend([px, py])

                node_id = self.static_grid_occupied[r][c]
                fill_color = "#dddddd"
                outline_color = "gray"
                name = ""
                if node_id is not None:
                    node_data = self.world_data["nodes"].get(str(node_id))
                    if node_data:
                        fill_color = "#ccffcc"
                        outline_color = "green"
                        name = node_data.get("custom_name", f"ID:{node_id}")
                    else:
                        fill_color = "#ffdddd"
                        outline_color = "red"
                        name = f"Fel: {node_id}"

                poly_id = self.static_map_canvas.create_polygon(points, fill=fill_color, outline=outline_color, width=2, tags=(f"hex_{r}_{c}", f"node_{node_id}" if node_id else ""))
                if name:
                    text_id = self.static_map_canvas.create_text(center_x, center_y, text=name, fill="black", anchor="center", tags=(f"hex_{r}_{c}", f"node_{node_id}" if node_id else ""))

                # Bind double-click to open node view
                if node_id:
                    def on_hex_double_click(event, n_id=node_id):
                        node = self.world_data["nodes"].get(str(n_id))
                        if node:
                            self.show_node_view(node)
                    self.static_map_canvas.tag_bind(f"node_{node_id}", "<Double-Button-1>", on_hex_double_click)

    def draw_static_border_lines(self):
        """Draws border lines between neighboring Jarldoms on the static map."""
        if not self.static_map_canvas:
            return
        self.static_map_canvas.delete("border_line")
        for x1, y1, x2, y2, color, width, id1, id2 in self.map_logic.border_lines_with_ids():
            tag = f"border_{min(id1, id2)}_{max(id1, id2)}"

            # Fill the border area polygon first so the line appears on top
            pos1 = self.map_static_positions.get(id1)
            pos2 = self.map_static_positions.get(id2)
            if pos1 and pos2:
                r1, c1 = pos1
                r2, c2 = pos2
                direction = self.map_logic.direction_index(r1, c1, r2, c2)
                p1, p2 = self.map_logic.hex_side_points(r1, c1, direction)
                opp = ((direction + 2) % MAX_NEIGHBORS) + 1
                p3, p4 = self.map_logic.hex_side_points(r2, c2, opp)
                self.static_map_canvas.create_polygon(
                    *p1,
                    *p2,
                    *p3,
                    *p4,
                    fill=color,
                    outline="",
                    tags=("border_line", tag),
                )

            self.static_map_canvas.create_line(
                x1,
                y1,
                x2,
                y2,
                fill=color,
                width=width,
                tags=("border_line", tag),
            )

            # Bind right-click to open border menu when clicking inside polygon
            self.static_map_canvas.tag_bind(tag, "<ButtonPress-3>", self.on_border_right_click)

    def on_border_right_click(self, event):
        item = self.static_map_canvas.find_withtag("current")
        if not item:
            return
        tags = self.static_map_canvas.gettags(item)
        pair_tag = next((t for t in tags if t.startswith("border_")), None)
        if not pair_tag:
            return
        try:
            _prefix, id1_str, id2_str = pair_tag.split("_")
            id1 = int(id1_str)
            id2 = int(id2_str)
        except ValueError:
            return

        menu = tk.Menu(self.static_map_canvas, tearoff=0)
        for bt in BORDER_TYPES:
            menu.add_command(
                label=bt,
                command=lambda bt_val=bt, n1=id1, n2=id2: self.set_border_type(n1, n2, bt_val)
            )
        menu.post(event.x_root, event.y_root)

    def set_border_type(self, id1: int, id2: int, border_type: str) -> None:
        changed = self.world_manager.set_border_between(id1, id2, border_type)
        if changed:
            self.save_current_world()
            self.draw_static_border_lines()

    def reset_hex_highlights(self):
        """Resets hex colors on the static map to their default values."""
        if not self.static_map_canvas:
            return
        for r in range(self.static_rows):
            for c in range(self.static_cols):
                node_id = self.static_grid_occupied[r][c]
                tag = f"hex_{r}_{c}"
                if node_id is None:
                    self.static_map_canvas.itemconfig(tag, fill="#dddddd", outline="gray")
                else:
                    self.static_map_canvas.itemconfig(tag, fill="#ccffcc", outline="green")

    def highlight_neighbor_candidates(self, start_node_id):
        """Highlights potential neighbors when starting a link drag.

        Nodes that share the same parent as ``start_node_id`` are colored yellow
        while existing neighbors are highlighted in red.
        """
        if not self.static_map_canvas or not self.world_data:
            return
        self.reset_hex_highlights()
        start_node = self.world_data.get("nodes", {}).get(str(start_node_id))
        if not start_node:
            return
        parent_id = start_node.get("parent_id")

        neighbor_ids = set()
        for nb in start_node.get("neighbors", []):
            nb_id = nb.get("id")
            if isinstance(nb_id, int):
                neighbor_ids.add(nb_id)

        sibling_ids = set()
        if parent_id is not None:
            for nid_str, nd in self.world_data.get("nodes", {}).items():
                try:
                    nid = int(nid_str)
                except ValueError:
                    continue
                if nid != start_node_id and nd.get("parent_id") == parent_id and self.get_depth_of_node(nid) == 3:
                    sibling_ids.add(nid)

        for sid in sibling_ids:
            pos = self.map_static_positions.get(sid)
            if pos:
                r, c = pos
                # Yellow highlight for nodes sharing the same parent
                self.static_map_canvas.itemconfig(
                    f"hex_{r}_{c}", fill="#ffffaa", outline="green"
                )

        for nid in neighbor_ids:
            pos = self.map_static_positions.get(nid)
            if pos:
                r, c = pos
                self.static_map_canvas.itemconfig(f"hex_{r}_{c}", fill="#ffcccc", outline="red")

    def on_static_map_button_press(self, event):
        """Handles mouse button press on the static map for drag start."""
        item = self.static_map_canvas.find_closest(event.x, event.y)[0]
        tags = self.static_map_canvas.gettags(item)
        node_tag = next((tag for tag in tags if tag.startswith("node_")), None)
        if node_tag:
            try:
                self.map_drag_start_node_id = int(node_tag.split("_")[1])
                self.map_drag_start_coords = (event.x, event.y)
                self.highlight_neighbor_candidates(self.map_drag_start_node_id)
            except ValueError:
                self.map_drag_start_node_id = None
                self.reset_hex_highlights()
        else:
            self.map_drag_start_node_id = None
            self.reset_hex_highlights()

    def on_static_map_mouse_motion(self, event):
        """Handles mouse motion during a drag operation on the static map."""
        if self.map_drag_start_node_id:
            end_coords = (self.static_map_canvas.canvasx(event.x), self.static_map_canvas.canvasy(event.y)) # Use canvas coords
            start_coords = self.map_drag_start_coords # Assuming this is already canvas coords

            if self.map_drag_line_id: # Check if line exists using its ID
                # Update existing line
                self.static_map_canvas.coords(self.map_drag_line_id, start_coords[0], start_coords[1], end_coords[0], end_coords[1])
            else:
                # Create the line if it doesn't exist
                self.map_drag_line_id = self.static_map_canvas.create_line(start_coords[0], start_coords[1], end_coords[0], end_coords[1], fill="blue", width=3, dash=(4, 4), tags="drag_line")

    def on_static_map_button_release(self, event):
        """Handles mouse button release on the static map for drag end (potential neighbor link)."""
        if self.map_drag_start_node_id:
            item = self.static_map_canvas.find_closest(event.x, event.y)[0]
            tags = self.static_map_canvas.gettags(item)
            target_node_tag = next((tag for tag in tags if tag.startswith("node_")), None)
            target_hex_tag = next((t for t in tags if t.startswith("hex_")), None)
            if target_node_tag:
                try:
                    target_node_id = int(target_node_tag.split("_")[1])
                    if target_node_id != self.map_drag_start_node_id:
                        self.attempt_link_neighbors(self.map_drag_start_node_id, target_node_id)
                except ValueError:
                    pass
            elif target_hex_tag:
                try:
                    _p, r_str, c_str = target_hex_tag.split("_")
                    r = int(r_str)
                    c = int(c_str)
                    if self.static_grid_occupied[r][c] is None:
                        if self.move_node_to_hex(self.map_drag_start_node_id, r, c):
                            self.draw_static_hexgrid()
                            self.draw_static_border_lines()
                except ValueError:
                    pass

            # Clean up drag line
            if self.map_drag_line_id:
                self.static_map_canvas.delete(self.map_drag_line_id)
                self.map_drag_line_id = None
            self.map_drag_start_node_id = None
            self.map_drag_start_coords = None
            self.reset_hex_highlights()

    # --------------------------------------------------
    # Hex drag and drop (right mouse button)
    # --------------------------------------------------
    def on_hex_drag_start(self, event):
        item = self.static_map_canvas.find_closest(event.x, event.y)[0]
        tags = self.static_map_canvas.gettags(item)
        hex_tag = next((t for t in tags if t.startswith("hex_")), None)
        if not hex_tag:
            return
        try:
            _prefix, r_str, c_str = hex_tag.split("_")
            r = int(r_str)
            c = int(c_str)
        except ValueError:
            return
        nid = self.static_grid_occupied[r][c]
        if nid is not None:
            self.hex_drag_node_id = nid
            self.hex_drag_start = (r, c)

    def on_hex_drag_motion(self, event):
        # Optional visual feedback could be added here
        pass

    def on_hex_drag_end(self, event):
        if self.hex_drag_node_id is None:
            return
        item = self.static_map_canvas.find_closest(event.x, event.y)[0]
        tags = self.static_map_canvas.gettags(item)
        hex_tag = next((t for t in tags if t.startswith("hex_")), None)
        target = None
        if hex_tag:
            try:
                _p, r_str, c_str = hex_tag.split("_")
                target = (int(r_str), int(c_str))
            except ValueError:
                target = None
        if target and self.static_grid_occupied[target[0]][target[1]] is None:
            moved = self.move_node_to_hex(self.hex_drag_node_id, target[0], target[1])
            if moved:
                self.draw_static_hexgrid()
                self.draw_static_border_lines()
        self.hex_drag_node_id = None
        self.hex_drag_start = None

    def attempt_link_neighbors(self, node_id1, node_id2):
        """Attempts to link two Jarldoms as neighbors."""
        slot = None
        if (
            getattr(self, "map_logic", None)
            and node_id1 in getattr(self, "map_static_positions", {})
            and node_id2 in getattr(self, "map_static_positions", {})
        ):
            r1, c1 = self.map_static_positions[node_id1]
            r2, c2 = self.map_static_positions[node_id2]
            slot = self.map_logic.direction_index(r1, c1, r2, c2)
        success, message = self.world_manager.attempt_link_neighbors(
            node_id1, node_id2, slot1=slot
        )
        if success:
            self.save_current_world()
            self.draw_static_border_lines()
        self.add_status_message(message)

    # --------------------------------------------------
    # Hex relocation helpers
    # --------------------------------------------------
    def move_node_to_hex(self, node_id: int, r: int, c: int) -> bool:
        """Move ``node_id`` to ``(r, c)`` if free and update neighbors."""
        if node_id not in self.map_static_positions:
            return False
        if r < 0 or r >= self.static_rows or c < 0 or c >= self.static_cols:
            return False
        if self.static_grid_occupied[r][c] is not None:
            return False

        old_r, old_c = self.map_static_positions[node_id]
        self.static_grid_occupied[old_r][old_c] = None
        self.static_grid_occupied[r][c] = node_id
        self.map_static_positions[node_id] = (r, c)
        if self.map_logic:
            self.map_logic.map_static_positions = self.map_static_positions
            self.map_logic.static_grid_occupied = self.static_grid_occupied

        empty = [{"id": None, "border": NEIGHBOR_NONE_STR} for _ in range(MAX_NEIGHBORS)]
        self.world_manager.update_neighbors_for_node(node_id, list(empty))

        # Remove references from any other node pointing at ``node_id``
        if self.world_data:
            nodes_dict = self.world_data.get("nodes", {})
            for nid_str, node in list(nodes_dict.items()):
                try:
                    nid = int(nid_str)
                except ValueError:
                    continue
                if nid == node_id:
                    continue
                neighbors = node.get("neighbors", [])
                if len(neighbors) < MAX_NEIGHBORS:
                    neighbors.extend(
                        {"id": None, "border": NEIGHBOR_NONE_STR}
                        for _ in range(MAX_NEIGHBORS - len(neighbors))
                    )
                    node["neighbors"] = neighbors
                changed = False
                for nb in neighbors:
                    if nb.get("id") == node_id:
                        nb["id"] = None
                        nb["border"] = NEIGHBOR_NONE_STR
                        changed = True
                if changed:
                    self.world_manager.update_neighbors_for_node(nid, list(neighbors))

        return True

    def recalculate_map_neighbors(self) -> None:
        """Clear all Jarldom neighbor links and relink adjacent hexes."""
        if not (self.world_data and self.map_logic):
            return
        empty = [{"id": None, "border": NEIGHBOR_NONE_STR} for _ in range(MAX_NEIGHBORS)]
        for nid_str, node in self.world_data.get("nodes", {}).items():
            try:
                nid = int(nid_str)
            except ValueError:
                continue
            if self.get_depth_of_node(nid) == 3:
                self.world_manager.update_neighbors_for_node(nid, list(empty))

        self.auto_link_adjacent_hexes()

    def clear_all_neighbor_links(self) -> None:
        """Remove all neighbor links between Jarldoms after confirmation."""
        if not self.world_data:
            return
        if not messagebox.askyesno(
            "Rensa länkar?",
            "Detta tar bort alla grannlänkar. Vill du fortsätta?",
            icon="warning",
            parent=self.root,
        ):
            return

        empty = [{"id": None, "border": NEIGHBOR_NONE_STR} for _ in range(MAX_NEIGHBORS)]
        for nid_str, node in self.world_data.get("nodes", {}).items():
            try:
                nid = int(nid_str)
            except ValueError:
                continue
            if self.get_depth_of_node(nid) == 3:
                self.world_manager.update_neighbors_for_node(nid, list(empty))

        self.save_current_world()
        if self.static_map_canvas and self.static_map_canvas.winfo_exists():
            self.draw_static_border_lines()
        self.add_status_message("Alla grannlänkar rensade.")

    def save_static_positions(self):
        """Store current hex positions on each node and save to file."""
        if not self.world_data:
            return
        for nid, (r, c) in self.map_static_positions.items():
            node = self.world_data.get("nodes", {}).get(str(nid))
            if node is not None:
                node["hex_row"] = r
                node["hex_col"] = c
        self.save_current_world()
        self.add_status_message("Positioner sparade")

    def load_static_positions(self):
        """Load saved hex coordinates from nodes into memory."""
        self.map_static_positions = {}
        self.static_grid_occupied = []
        if not self.world_data:
            return
        max_r = max_c = 0
        for nid_str, node in self.world_data.get("nodes", {}).items():
            try:
                nid = int(nid_str)
            except ValueError:
                continue
            r = node.get("hex_row")
            c = node.get("hex_col")
            if isinstance(r, int) and isinstance(c, int):
                self.map_static_positions[nid] = (r, c)
                max_r = max(max_r, r)
                max_c = max(max_c, c)
        self.static_rows = max(self.static_rows, max_r + 1)
        self.static_cols = max(self.static_cols, max_c + 1)
        self.static_grid_occupied = [
            [None] * self.static_cols for _ in range(self.static_rows)
        ]
        for nid, (r, c) in self.map_static_positions.items():
            while r >= self.static_rows:
                self.static_grid_occupied.append([None] * self.static_cols)
                self.static_rows += 1
            while c >= self.static_cols:
                for row in self.static_grid_occupied:
                    row.append(None)
                self.static_cols += 1
            self.static_grid_occupied[r][c] = nid

    def open_dynamic_map_view(self):
        """Opens the dynamic map view."""
        self._clear_right_frame()
        if not self.world_data:

            self.add_status_message("Varning: Ingen värld är laddad, kan inte visa dynamisk karta.")
            self.show_no_world_view()
            return
        self.dynamic_map_view = DynamicMapCanvas(self.right_frame, self, self.world_data)

        self.dynamic_map_view.show()

    def refresh_dynamic_map(self):
        """Redraw the dynamic map if it is currently shown."""
        if getattr(self, "dynamic_map_view", None):
            self.dynamic_map_view.set_world_data(self.world_data)
            self.dynamic_map_view.draw_dynamic_map()
def main():
    root = tk.Tk()
    app = FeodalSimulator(root)
    root.mainloop()

if __name__ == "__main__":
    main()

