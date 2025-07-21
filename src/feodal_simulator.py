# -*- coding: utf-8 -*-
"""Main application class for the feudal simulator."""
import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import random
import math
from collections import deque

from constants import (
    BORDER_TYPES,
    BORDER_COLORS,
    NEIGHBOR_NONE_STR,
    NEIGHBOR_OTHER_STR,
    MAX_NEIGHBORS,
)
from data_manager import load_worlds_from_file, save_worlds_to_file
from node import Node
from utils import roll_dice, generate_swedish_village_name
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
        self.map_active_node_tag = None # To potentially highlight hovered hex


        # --- Initial View ---
        self.show_no_world_view() # Show placeholder in right frame

        # Auto-load world file if only one world exists
        if len(self.all_worlds) == 1:
            only_world = next(iter(self.all_worlds))
            try:
                self.load_world(only_world)
            except Exception as e:
                print(f"Failed to auto-load world '{only_world}': {e}")

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
            # No status message here, usually called from other actions that add status
        #else:
        #    print("Warning: Tried to save world, but no active world or data.")


    def _clear_right_frame(self):
        """Destroys all widgets in the right frame."""
        # Important: Unbind map drag events if map exists
        if self.static_map_canvas:
            self.static_map_canvas.unbind("<ButtonPress-3>")
            self.static_map_canvas.unbind("<B3-Motion>")
            self.static_map_canvas.unbind("<ButtonRelease-3>")
            self.static_map_canvas.unbind("<Motion>") # For hover effects if added
            self.static_map_canvas = None # Clear reference

        for widget in self.right_frame.winfo_children():
            widget.destroy()
        self.map_drag_start_node_id = None # Reset drag state
        self.map_drag_line_id = None


    def show_no_world_view(self):
        """Displays a placeholder when no world is loaded or no node is selected."""
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
        ttk.Button(container, text="Hantera Härskare", command=self.show_manage_characters_view, width=20).pack(pady=5)
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
                f"Validerade och uppdaterade data vid laddning: {nodes_updated} noder, {chars_updated} härskare."
            )
            self.save_current_world()


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
        """Displays the UI for managing characters (härskare)."""
        if not self.active_world_name:
            messagebox.showinfo("Ingen Värld", "Ladda en värld först för att hantera härskare.", parent=self.root)
            return

        self._clear_right_frame()
        container = ttk.Frame(self.right_frame)
        container.pack(expand=True, fill='y', pady=20)

        ttk.Label(container, text="Hantera Härskare", font=("Arial", 14)).pack(pady=5)

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
                    messagebox.showerror("Fel", f"Kunde inte hitta data för härskare ID {char_id_str}", parent=self.root)
            else:
                messagebox.showinfo("Inget Val", "Välj en härskare i listan att redigera.", parent=self.root)


        def do_delete():
            char_id_to_delete_str = get_selected_char_id()
            if not char_id_to_delete_str:
                messagebox.showinfo("Inget Val", "Välj en härskare i listan att radera.", parent=self.root)
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

            confirm_message = f"Är du säker på att du vill radera härskaren '{char_name}' (ID: {char_id_to_delete_str})?"
            if ruled_nodes_info:
                confirm_message += "\n\nDenna härskare styr för närvarande:\n" + "\n".join(ruled_nodes_info[:5]) # Show first 5
                if len(ruled_nodes_info) > 5: confirm_message += "\n- ..."
                confirm_message += "\n\nOm du raderar härskaren kommer dessa förläningar att bli utan härskare."

            if messagebox.askyesno("Radera Härskare?", confirm_message, icon='warning', parent=self.root):
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
                    self.add_status_message(f"Härskare '{char_name}' (ID: {char_id_to_delete_str}) raderad. {nodes_updated_count} förläning(ar) uppdaterades.")
                    # Refresh the list view
                    self.show_manage_characters_view()
                else:
                    messagebox.showerror("Fel", f"Kunde inte radera, härskare med ID {char_id_to_delete_str} hittades ej (kanske redan raderad?).", parent=self.root)
                    self.show_manage_characters_view() # Refresh anyway


        # Button Frame
        button_frame = ttk.Frame(container)
        button_frame.pack(pady=10)
        ttk.Button(button_frame, text="Ny härskare", command=do_new).grid(row=0, column=0, padx=5, pady=2)
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
        title = "Skapa Ny Härskare" if is_new else f"Redigera Härskare (ID: {char_id})"
        ttk.Label(container, text=title, font=("Arial", 14)).pack(pady=(5, 15))

        # Use a frame for the form elements for better alignment
        form_frame = ttk.Frame(container)
        form_frame.pack(fill='x')

        # --- Form Fields ---
        # Name
        ttk.Label(form_frame, text="Namn:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        name_var = tk.StringVar(value=char_data.get("name", "") if char_data else "")
        name_entry = ttk.Entry(form_frame, textvariable=name_var, width=40)
        name_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        name_entry.focus() # Set focus to name field

        # Wealth (Example - Currently unused field)
        ttk.Label(form_frame, text="Förmögenhet:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        wealth_var = tk.IntVar(value=char_data.get("wealth", 0) if char_data else 0)
        wealth_spinbox = tk.Spinbox(form_frame, from_=0, to=1000000, textvariable=wealth_var, width=10) # Standard Spinbox for now
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


        # Skills (Example - Currently unused field, comma-separated string)
        ttk.Label(form_frame, text="Färdigheter:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        skills_var = tk.StringVar(value=", ".join(char_data.get("skills", [])) if char_data else "")
        skills_entry = ttk.Entry(form_frame, textvariable=skills_var, width=40)
        skills_entry.grid(row=3, column=1, padx=5, pady=5, sticky="ew")


        # Make the entry column expand
        form_frame.grid_columnconfigure(1, weight=1)
        form_frame.grid_rowconfigure(2, weight=1) # Allow description text box to expand vertically slightly


        # --- Save Action ---
        def do_save():
            name = name_var.get().strip()
            if not name:
                messagebox.showwarning("Namn Saknas", "Härskaren måste ha ett namn.", parent=self.root)
                name_entry.focus()
                return

            # Validate wealth? For now assume valid int.
            try: wealth = wealth_var.get()
            except tk.TclError: wealth = 0

            description = desc_text.get("1.0", tk.END).strip()
            # Simple skill parsing - split by comma, remove whitespace
            skills = [s.strip() for s in skills_var.get().split(',') if s.strip()]

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
                    "skills": skills
                }
                self.world_data.setdefault("characters", {})[new_id_str] = new_char_data
                self.add_status_message(f"Skapade ny härskare: '{name}' (ID: {new_id}).")

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
                    char_data_to_update["name"] = name
                    char_data_to_update["wealth"] = wealth
                    char_data_to_update["description"] = description
                    char_data_to_update["skills"] = skills
                    self.add_status_message(f"Uppdaterade härskare '{old_name}' -> '{name}' (ID: {char_id_str}).")

                    # Refresh tree items if this ruler changed name
                    if old_name != name:
                            if self.world_data and "nodes" in self.world_data:
                                for nid_str, ndata in self.world_data["nodes"].items():
                                    if str(ndata.get("ruler_id")) == char_id_str:
                                        try:
                                            self.refresh_tree_item(int(nid_str))
                                        except ValueError: pass # Skip non-int keys if any
                else:
                    messagebox.showerror("Fel", f"Kunde inte spara, härskare med ID {char_id_str} hittades ej.", parent=self.root)
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
        # Allow content to expand
        view_frame.grid_rowconfigure(1, weight=1)
        view_frame.grid_columnconfigure(0, weight=1)

        # --- Title Frame ---
        title_frame = ttk.Frame(view_frame)
        title_frame.pack(fill="x", pady=(0, 15))
        title_label = ttk.Label(title_frame, text=f"{display_name}", font=("Arial", 16, "bold"))
        title_label.pack(side=tk.LEFT)
        ttk.Label(title_frame, text=f" (ID: {node_id}, Djup: {depth})", font=("Arial", 10)).pack(side=tk.LEFT, anchor="s", padx=5)

        # --- Frame for the actual editor content ---
        editor_content_frame = ttk.Frame(view_frame)
        editor_content_frame.pack(fill="both", expand=True)


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


    def _create_delete_button(self, parent_frame, node_data):
        """Creates the delete button common to all node editors."""
        def do_delete():
            if not isinstance(node_data, dict) or 'node_id' not in node_data:
                messagebox.showerror("Fel", "Kan inte radera, ogiltig noddata.", parent=self.root)
                return

            node_id = node_data['node_id']
            # Recalculate depth for display name in message
            depth = self.get_depth_of_node(node_id)
            display_name = self.get_display_name_for_node(node_data, depth)

            confirm_msg = f"Är du säker på att du vill radera '{display_name}' (ID: {node_id})?"
            num_children = len(node_data.get("children", []))
            # Estimate total descendants for better warning
            descendant_count = self.count_descendants(node_id)

            if descendant_count > 0:
                confirm_msg += f"\n\nVARNING: Detta kommer även att radera {descendant_count} underliggande förläning(ar)!"
            elif num_children > 0: # Fallback if descendant count fails
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


    def _show_upper_level_node_editor(self, parent_frame, node_data, depth):
        """Editor for Kingdom, Furstendöme, Hertigdöme (Depth 0-2)."""
        node_id = node_data['node_id']

        # Use Notebook for better organization? Maybe overkill here.
        # Main content frame for this editor
        editor_frame = ttk.Frame(parent_frame)
        editor_frame.pack(fill="both", expand=True)
        editor_frame.grid_columnconfigure(1, weight=1) # Allow entry column to expand

        row_idx = 0
        # Name (uses 'name' field for these levels)
        ttk.Label(editor_frame, text="Namn:").grid(row=row_idx, column=0, sticky="w", padx=5, pady=3)
        name_var = tk.StringVar(value=node_data.get("name", ""))
        name_entry = ttk.Entry(editor_frame, textvariable=name_var, width=40)
        name_entry.grid(row=row_idx, column=1, sticky="ew", padx=5, pady=3)
        row_idx += 1

        # Custom Name (Optional extra identifier)
        ttk.Label(editor_frame, text="Eget Namn:").grid(row=row_idx, column=0, sticky="w", padx=5, pady=3)
        custom_name_var = tk.StringVar(value=node_data.get("custom_name", ""))
        custom_name_entry = ttk.Entry(editor_frame, textvariable=custom_name_var, width=40)
        custom_name_entry.grid(row=row_idx, column=1, sticky="ew", padx=5, pady=3)
        row_idx += 1

        # Population
        ttk.Label(editor_frame, text="Befolkning:").grid(row=row_idx, column=0, sticky="w", padx=5, pady=3)
        pop_var = tk.IntVar(value=node_data.get("population", 0))
        pop_entry = ttk.Entry(editor_frame, textvariable=pop_var, width=10)
        pop_entry.grid(row=row_idx, column=1, sticky="w", padx=5, pady=3)
        row_idx += 1

        # Number of Subfiefs
        ttk.Label(editor_frame, text="Antal Underförläningar (barnregioner):").grid(row=row_idx, column=0, sticky="w", padx=5, pady=3)
        sub_var = tk.IntVar(value=node_data.get("num_subfiefs", 0))
        # Use standard spinbox as ttk doesn't have one? Or just Entry + validation? Use Spinbox for now.
        sub_spinbox = tk.Spinbox(editor_frame, from_=0, to=100, textvariable=sub_var, width=5, font=('Arial', 10))
        sub_spinbox.grid(row=row_idx, column=1, sticky="w", padx=5, pady=3)
        row_idx += 1

        # Inline help explaining subfiefs
        help_text = "En underförläning är en region som lyder under denna. \nÄndra antalet för att skapa eller ta bort."
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

        def update_subfiefs_action():
            # Save potentially changed data before updating children
            node_data["name"] = name_var.get().strip()
            node_data["custom_name"] = custom_name_var.get().strip()
            try: node_data["population"] = pop_var.get()
            except tk.TclError: node_data["population"] = 0
            try:
                target_subfiefs = sub_var.get()
                if target_subfiefs < 0: target_subfiefs = 0 # Ensure non-negative
                node_data["num_subfiefs"] = target_subfiefs
            except tk.TclError: node_data["num_subfiefs"] = 0
            current_count = len(node_data.get("children", []))
            if abs(target_subfiefs - current_count) > 1:
                if not messagebox.askyesno(
                        "Bekräfta",
                        "Du är på väg att ändra antalet underförläningar med fler än en. Är du säker?",
                        parent=self.root):
                    return

            self.update_subfiefs_for_node(node_data)
            # The view will be refreshed by update_subfiefs_for_node finding this node again

        ttk.Button(button_frame, text="Uppdatera Underförläningar", command=update_subfiefs_action).pack(side=tk.LEFT, padx=5)

        def add_subnode_action():
            node_data["name"] = name_var.get().strip()
            node_data["custom_name"] = custom_name_var.get().strip()
            try: node_data["population"] = pop_var.get()
            except tk.TclError: node_data["population"] = 0
            new_count = node_data.get("num_subfiefs", 0) + 1
            sub_var.set(new_count)
            node_data["num_subfiefs"] = new_count
            self.update_subfiefs_for_node(node_data)

        ttk.Button(button_frame, text="Lägg till Underförläning", command=add_subnode_action).pack(side=tk.LEFT, padx=5)

        def save_node_action():
            old_name = node_data.get("name", "")
            old_custom_name = node_data.get("custom_name", "")
            old_pop = node_data.get("population", 0)

            new_name = name_var.get().strip()
            new_custom_name = custom_name_var.get().strip()
            try: new_pop = pop_var.get()
            except tk.TclError: new_pop = 0
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
                self.save_current_world()
                status = f"Nod {node_id} uppdaterad: " + ", ".join(status_details)
                self.add_status_message(status)
                self.refresh_tree_item(node_id) # Update tree display name
            else:
                self.add_status_message(f"Nod {node_id}: Inga ändringar att spara.")


        ttk.Button(button_frame, text="Spara Noddata", command=save_node_action).pack(side=tk.LEFT, padx=5)

        # --- Delete and Back Buttons Frame ---
        delete_back_frame = ttk.Frame(editor_frame)
        delete_back_frame.grid(row=row_idx, column=0, columnspan=2, pady=(20, 5))
        row_idx += 1

        delete_button = self._create_delete_button(delete_back_frame, node_data)
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
        row_idx += 1

        # Population
        ttk.Label(editor_frame, text="Befolkning:").grid(row=row_idx, column=0, sticky="w", padx=5, pady=3)
        pop_var = tk.IntVar(value=node_data.get("population", 0))
        pop_entry = ttk.Entry(editor_frame, textvariable=pop_var, width=10)
        pop_entry.grid(row=row_idx, column=1, sticky="w", padx=5, pady=3)
        row_idx += 1

        # Number of Subfiefs (Resources under the Jarldom)
        ttk.Label(editor_frame, text="Antal Underresurser:").grid(row=row_idx, column=0, sticky="w", padx=5, pady=3)
        sub_var = tk.IntVar(value=node_data.get("num_subfiefs", 0))
        sub_spinbox = tk.Spinbox(editor_frame, from_=0, to=100, textvariable=sub_var, width=5, font=('Arial', 10))
        sub_spinbox.grid(row=row_idx, column=1, sticky="w", padx=5, pady=3)
        row_idx += 1

        # --- Actions Frame ---
        ttk.Separator(editor_frame, orient=tk.HORIZONTAL).grid(row=row_idx, column=0, columnspan=2, sticky="ew", pady=(15, 10))
        row_idx += 1
        action_button_frame = ttk.Frame(editor_frame)
        action_button_frame.grid(row=row_idx, column=0, columnspan=2, pady=5)
        row_idx += 1


        def update_subfiefs_action():
            # Save potentially changed data before updating children
            new_custom_name = custom_name_var.get().strip()
            if not new_custom_name:
                messagebox.showwarning("Namn Saknas", "Ett Jarldöme måste ha ett namn.", parent=self.root)
                return
            node_data["custom_name"] = new_custom_name

            try: node_data["population"] = pop_var.get()
            except tk.TclError: node_data["population"] = 0
            try:
                target_subfiefs = sub_var.get()
                if target_subfiefs < 0: target_subfiefs = 0
                node_data["num_subfiefs"] = target_subfiefs
            except tk.TclError: node_data["num_subfiefs"] = 0
            node_data["res_type"] = "Resurs" # Ensure internal type is correct

            self.update_subfiefs_for_node(node_data)
            # View refreshed by update function finding this node again

        ttk.Button(action_button_frame, text="Uppdatera Underresurser", command=update_subfiefs_action).pack(side=tk.LEFT, padx=5)


        def save_node_action():
            old_custom_name = node_data.get("custom_name", "")
            old_pop = node_data.get("population", 0)

            new_custom_name = custom_name_var.get().strip()
            if not new_custom_name:
                messagebox.showwarning("Namn Saknas", "Ett Jarldöme måste ha ett namn.", parent=self.root)
                return
            try: new_pop = pop_var.get()
            except tk.TclError: new_pop = 0
            # num_subfiefs saved via its own button

            changes_made = False
            status_details = []
            if old_custom_name != new_custom_name:
                node_data["custom_name"] = new_custom_name; changes_made = True
                status_details.append(f"Namn: '{old_custom_name}' -> '{new_custom_name}'")
            if old_pop != new_pop:
                node_data["population"] = new_pop; changes_made = True
                status_details.append(f"Befolkning: {old_pop} -> {new_pop}")

            node_data["res_type"] = "Resurs" # Ensure internal type

            if changes_made:
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


        # --- Neighbor Editing ---
        neighbor_button_frame = ttk.Frame(action_button_frame) # Add to same action row
        neighbor_button_frame.pack(side=tk.LEFT, padx=15)
        ttk.Button(neighbor_button_frame, text="Redigera Grannar", command=lambda n=node_data: self.show_neighbor_editor(n)).pack()


        # --- Delete and Back Buttons Frame ---
        delete_back_frame = ttk.Frame(editor_frame)
        delete_back_frame.grid(row=row_idx, column=0, columnspan=2, pady=(20, 5))
        row_idx += 1

        delete_button = self._create_delete_button(delete_back_frame, node_data)
        delete_button.pack(side=tk.LEFT, padx=10)

        ttk.Button(delete_back_frame, text="< Stäng Vy", command=self.show_no_world_view).pack(side=tk.LEFT, padx=10)


    def show_neighbor_editor(self, node_data):
        """Displays the UI for editing the neighbors of a Jarldom."""
        self._clear_right_frame()
        node_id = node_data['node_id']
        custom_name = node_data.get("custom_name", f"Jarldom {node_id}")

        # --- Main container frame ---
        view_frame = ttk.Frame(self.right_frame, padding="10 10 10 10")
        view_frame.pack(fill="both", expand=True)

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

        self.save_current_world()
        self.populate_tree()  # Refresh the tree
        self.restore_tree_state(open_items, selection)
        self.show_node_view(node_data)  # Re-show the editor

    def delete_node_and_descendants(self, node_id):
        """Recursively deletes a node and all its children from world_data."""
        return self.world_manager.delete_node_and_descendants(node_id)

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
        self.map_logic = StaticMapLogic(
            self.world_data,
            30,
            30,
            hex_size=30,
            spacing=self.hex_spacing,
        )

        # Bottom button bar
        btn_fr = ttk.Frame(self.right_frame, style="Tool.TFrame")
        btn_fr.pack(fill="x", pady=5)
        ttk.Button(btn_fr, text="< Tillbaka", command=self.show_no_world_view).pack(side=tk.LEFT, padx=5)

        self.static_scale = 1.0
        self.static_map_canvas.bind("<MouseWheel>", self.on_static_map_zoom) # Windows/macOS
        self.static_map_canvas.bind("<Button-4>", self.on_static_map_zoom) # Linux scroll up
        self.static_map_canvas.bind("<Button-5>", self.on_static_map_zoom) # Linux scroll down

        # --- Drag and Drop for Neighbors ---
        self.static_map_canvas.bind("<ButtonPress-1>", self.on_static_map_button_press)
        self.static_map_canvas.bind("<B1-Motion>", self.on_static_map_mouse_motion)
        self.static_map_canvas.bind("<ButtonRelease-1>", self.on_static_map_button_release)

        self.place_jarldomes_bfs()
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
                    angle_deg = 60 * i - 30
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

        for x1, y1, x2, y2, color, width in self.map_logic.border_lines():
            self.static_map_canvas.create_line(
                x1,
                y1,
                x2,
                y2,
                fill=color,
                width=width,
                tags="border_line",
            )

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
            if target_node_tag:
                try:
                    target_node_id = int(target_node_tag.split("_")[1])
                    if target_node_id != self.map_drag_start_node_id:
                        self.attempt_link_neighbors(self.map_drag_start_node_id, target_node_id)
                except ValueError:
                    pass

            # Clean up drag line
            if self.map_drag_line:
                self.static_map_canvas.delete(self.map_drag_line)
                self.map_drag_line = None
            self.map_drag_start_node_id = None
            self.map_drag_start_coords = None
            self.reset_hex_highlights()

    def attempt_link_neighbors(self, node_id1, node_id2):
        """Attempts to link two Jarldoms as neighbors."""
        success, message = self.world_manager.attempt_link_neighbors(node_id1, node_id2)
        if success:
            self.save_current_world()
            self.draw_static_border_lines()
        self.add_status_message(message)

    def open_dynamic_map_view(self):
        """Opens the dynamic map view."""
        self._clear_right_frame()
        if not self.world_data:

            self.add_status_message("Varning: Ingen värld är laddad, kan inte visa dynamisk karta.")
            self.show_no_world_view()
            return
        self.dynamic_map_view = DynamicMapCanvas(self.right_frame, self, self.world_data)

        self.dynamic_map_view.show()
def main():
    root = tk.Tk()
    app = FeodalSimulator(root)
    root.mainloop()

if __name__ == "__main__":
    main()

