"""View logic for managing worlds (list/load/copy/delete/create)."""
from __future__ import annotations

import copy
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
from typing import TYPE_CHECKING

from data_manager import load_worlds_from_file

if TYPE_CHECKING:  # pragma: no cover - for type hints only
    from feodal_simulator import FeodalSimulator


def show_manage_worlds_view(app: "FeodalSimulator", parent: tk.Misc) -> None:
    """Displays the UI for managing worlds (create, load, delete, copy)."""
    app._clear_right_frame()
    app.update_details_header("Världar")
    container = ttk.Frame(parent)
    container.pack(expand=True, fill="y", pady=20)

    ttk.Label(container, text="Hantera världar", font=("Arial", 14)).pack(pady=5)

    # Frame for listbox and scrollbar
    list_frame = ttk.Frame(container)
    list_frame.pack(pady=10, fill="x", padx=20)

    world_listbox = tk.Listbox(list_frame, height=10, exportselection=False, font=("Arial", 10))
    list_scroll = ttk.Scrollbar(list_frame, orient="vertical", command=world_listbox.yview)
    world_listbox.config(yscrollcommand=list_scroll.set)

    list_scroll.pack(side=tk.RIGHT, fill="y")
    world_listbox.pack(side=tk.LEFT, fill="x", expand=True)

    # Populate listbox
    app.all_worlds = load_worlds_from_file()  # Ensure latest data
    world_listbox.delete(0, tk.END)  # Clear previous entries
    for wname in sorted(app.all_worlds.keys()):
        world_listbox.insert(tk.END, wname)
        if wname == app.active_world_name:
            idx = world_listbox.size() - 1
            world_listbox.itemconfig(idx, {"bg": "#aaddff"})  # Highlight active slightly darker
            world_listbox.selection_set(idx)  # Select active

    # --- Actions ---
    def do_load():
        selection = world_listbox.curselection()
        if selection:
            wname = world_listbox.get(selection[0])
            app.load_world(wname)
            app.show_manage_worlds_view()  # Refresh view to show highlight

    def do_delete():
        selection = world_listbox.curselection()
        if selection:
            wname = world_listbox.get(selection[0])
            if messagebox.askyesno(
                "Radera Värld?",
                f"Är du säker på att du vill radera världen '{wname}'?\nDetta kan inte ångras.",
                icon="warning",
                parent=app.root,
            ):
                if wname in app.all_worlds:
                    del app.all_worlds[wname]
                    app.world_ui.persist_worlds(app.all_worlds)
                    app.add_status_message(f"Värld '{wname}' raderad.")
                    if app.active_world_name == wname:
                        app.active_world_name = None
                        app.world_data = None
                        app.root.title("Förläningssimulator - Ingen värld")
                        if app.tree.winfo_exists():
                            app.tree.delete(*app.tree.get_children())  # Clear tree
                        app.show_no_world_view()  # Update display if active world deleted
                    app.show_manage_worlds_view()  # Refresh list
                else:
                    messagebox.showerror(
                        "Fel",
                        f"Kunde inte hitta världen '{wname}' att radera.",
                        parent=app.root,
                    )
                    app.show_manage_worlds_view()  # Refresh list anyway

    def do_copy():
        selection = world_listbox.curselection()
        if selection:
            wname_to_copy = world_listbox.get(selection[0])
            new_name = simpledialog.askstring(
                "Kopiera Värld",
                f"Ange ett namn för kopian av '{wname_to_copy}':",
                parent=app.root,
            )
            if new_name:
                new_name = new_name.strip()
                if not new_name:
                    messagebox.showwarning(
                        "Ogiltigt Namn",
                        "Namnet på kopian får inte vara tomt.",
                        parent=app.root,
                    )
                    return
                if new_name == wname_to_copy:
                    messagebox.showwarning(
                        "Ogiltigt Namn",
                        "Kopian måste ha ett annat namn än originalet.",
                        parent=app.root,
                    )
                    return
                if new_name in app.all_worlds:
                    messagebox.showerror(
                        "Namnkonflikt",
                        f"En värld med namnet '{new_name}' finns redan.",
                        parent=app.root,
                    )
                    return
                if wname_to_copy in app.all_worlds:
                    app.all_worlds[new_name] = copy.deepcopy(app.all_worlds[wname_to_copy])
                    app.world_ui.persist_worlds(app.all_worlds)
                    app.add_status_message(
                        f"Kopierade världen '{wname_to_copy}' till '{new_name}'."
                    )
                    app.show_manage_worlds_view()  # Refresh list
                else:
                    messagebox.showerror(
                        "Fel",
                        f"Kunde inte hitta originalvärlden '{wname_to_copy}' att kopiera.",
                        parent=app.root,
                    )

    def do_create():
        app.create_new_world()
        # Refresh this view to show the new world
        app.show_manage_worlds_view()

    # Button Frame
    button_frame = ttk.Frame(container)
    button_frame.pack(pady=10)
    ttk.Button(button_frame, text="Skapa ny", command=do_create).grid(
        row=0, column=0, padx=5, pady=2
    )
    ttk.Button(button_frame, text="Ladda vald", command=do_load).grid(
        row=0, column=1, padx=5, pady=2
    )
    ttk.Button(button_frame, text="Kopiera vald", command=do_copy).grid(
        row=1, column=0, padx=5, pady=2
    )
    ttk.Button(
        button_frame, text="Radera vald", command=do_delete, style="Danger.TButton"
    ).grid(row=1, column=1, padx=5, pady=2)
    ttk.Button(
        button_frame, text="Skapa Drunok", command=app.create_drunok_world
    ).grid(row=2, column=0, columnspan=2, pady=(10, 2))

    # Back Button
    ttk.Button(container, text="< Tillbaka", command=app.show_data_menu_view).pack(
        pady=(15, 5)
    )


__all__ = ["show_manage_worlds_view"]
