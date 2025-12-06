"""View logic for managing characters."""
from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover - for type hints only
    from feodal_simulator import FeodalSimulator


def show_manage_characters_view(app: "FeodalSimulator", parent: tk.Misc) -> None:
    """Displays the UI for managing characters (karaktärer)."""
    if not app.active_world_name:
        messagebox.showinfo(
            "Ingen Värld",
            "Ladda en värld först för att hantera karaktärer.",
            parent=app.root,
        )
        return

    app._clear_right_frame()
    app.update_details_header("Karaktärer")
    container = ttk.Frame(parent)
    container.pack(expand=True, fill="y", pady=20)

    ttk.Label(container, text="Hantera Karaktärer", font=("Arial", 14)).pack(pady=5)

    # Ensure characters structure exists
    if "characters" not in app.world_data:
        app.world_data["characters"] = {}

    # Frame for listbox and scrollbar
    list_frame = ttk.Frame(container)
    list_frame.pack(pady=10, fill="x", padx=20)

    char_listbox = tk.Listbox(list_frame, height=10, exportselection=False, font=("Arial", 10))
    list_scroll = ttk.Scrollbar(list_frame, orient="vertical", command=char_listbox.yview)
    char_listbox.config(yscrollcommand=list_scroll.set)

    list_scroll.pack(side=tk.RIGHT, fill="y")
    char_listbox.pack(side=tk.LEFT, fill="x", expand=True)

    # Populate listbox - sort by name for easier finding
    char_listbox.delete(0, tk.END)  # Clear previous entries
    sorted_chars = sorted(
        app.world_data.get("characters", {}).items(),
        key=lambda item: item[1].get("name", "").lower(),
    )
    char_id_map = {}  # Map listbox index to char_id
    for idx, (char_id_str, data) in enumerate(sorted_chars):
        display_text = f"{data.get('name', 'Namnlös')} (ID: {char_id_str})"
        char_listbox.insert(tk.END, display_text)
        char_id_map[idx] = char_id_str  # Store ID as string

    # --- Actions ---
    def get_selected_char_id():
        selection = char_listbox.curselection()
        if selection:
            list_index = selection[0]
            return char_id_map.get(list_index)
        return None

    def do_new():
        app.show_edit_character_view(None, is_new=True)

    def do_edit():
        char_id_str = get_selected_char_id()
        if char_id_str:
            char_data = app.world_data.get("characters", {}).get(char_id_str)
            if char_data:
                app.show_edit_character_view(char_data, is_new=False)
            else:
                messagebox.showerror(
                    "Fel",
                    f"Kunde inte hitta data för karaktär ID {char_id_str}",
                    parent=app.root,
                )
        else:
            messagebox.showinfo(
                "Inget Val",
                "Välj en karaktär i listan att redigera.",
                parent=app.root,
            )

    def do_delete():
        char_id_to_delete_str = get_selected_char_id()
        if not char_id_to_delete_str:
            messagebox.showinfo(
                "Inget Val",
                "Välj en karaktär i listan att radera.",
                parent=app.root,
            )
            return

        char_name = (
            app.world_data.get("characters", {})
            .get(char_id_to_delete_str, {})
            .get("name", "(namnlös)")
        )

        # Check if character is ruler in any nodes
        nodes_to_update: list[str] = []
        ruled_nodes_info = []

        for node_id_str, node_data in app.world_data.get("nodes", {}).items():
            if node_data.get("ruler_id") == int(char_id_to_delete_str):
                try:
                    node_id_int = int(node_id_str)
                except ValueError:
                    continue
                depth = app.get_depth_of_node(node_id_int)
                display_name = app.get_display_name_for_node(node_data, depth)
                ruled_nodes_info.append(f"- {display_name}")
                nodes_to_update.append(node_id_str)

        confirm_message = f"Är du säker på att du vill radera karaktären '{char_name}' (ID: {char_id_to_delete_str})?"
        if ruled_nodes_info:
            confirm_message += (
                "\n\nDenna karaktär styr för närvarande:\n" + "\n".join(ruled_nodes_info[:5])
            )
            if len(ruled_nodes_info) > 5:
                confirm_message += "\n- ..."
            confirm_message += "\n\nOm du raderar karaktären kommer dessa förläningar att bli utan härskare."

        if messagebox.askyesno(
            "Radera Karaktär?", confirm_message, icon="warning", parent=app.root
        ):
            nodes_updated_count = 0
            # Remove ruler_id from nodes
            for node_id_str_update in nodes_to_update:
                node_to_update = app.world_data.get("nodes", {}).get(node_id_str_update)
                if node_to_update:
                    node_to_update["ruler_id"] = None
                    nodes_updated_count += 1
                    # Refresh tree item visually if tree exists
                    if app.tree.winfo_exists() and app.tree.exists(node_id_str_update):
                        app.refresh_tree_item(int(node_id_str_update))

            # Delete character data
            if char_id_to_delete_str in app.world_data.get("characters", {}):
                del app.world_data["characters"][char_id_to_delete_str]
                app.save_current_world()
                app.add_status_message(
                    f"Karaktär '{char_name}' (ID: {char_id_to_delete_str}) raderad. {nodes_updated_count} förläning(ar) uppdaterades."
                )
                # Refresh the list view
                app.show_manage_characters_view()
            else:
                messagebox.showerror(
                    "Fel",
                    f"Kunde inte radera, karaktär med ID {char_id_to_delete_str} hittades ej (kanske redan raderad?).",
                    parent=app.root,
                )
                app.show_manage_characters_view()  # Refresh anyway

    # Button Frame
    button_frame = ttk.Frame(container)
    button_frame.pack(pady=10)
    ttk.Button(button_frame, text="Ny karaktär", command=do_new).grid(
        row=0, column=0, padx=5, pady=2
    )
    ttk.Button(button_frame, text="Redigera vald", command=do_edit).grid(
        row=0, column=1, padx=5, pady=2
    )
    ttk.Button(
        button_frame, text="Radera vald", command=do_delete, style="Danger.TButton"
    ).grid(row=1, column=0, columnspan=2, padx=5, pady=2)

    # Back Button
    ttk.Button(container, text="< Tillbaka", command=app.show_data_menu_view).pack(
        pady=(15, 5)
    )


__all__ = ["show_manage_characters_view"]
