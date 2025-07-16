import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import random
import math
import os
import json
from collections import deque

# --------------------------------------------------
# Konstanter & resurstyper
# --------------------------------------------------
DEFAULT_WORLDS_FILE =3D "worlds.json"

RES_TYPES =3D [
    "Resurs",
    "Jaktmark", "Odlingsmark", "Betesmark", "Fiskevatten",
    "Armborstskytt", "B=C3=A5gskytt", "L=C3=A5ngb=C3=A5gskytt", "Fotsoldat"=
, "Fotsoldat -
l=C3=A4tt",
    "Fotsoldat - tung", "Marinsoldat", "Sj=C3=B6man",
    "Officer", "Riddare med v=C3=A4pnare", "Falkenerare", "Fogde", "H=C3=A4=
rold",
    "Livmedikus", "F=C3=B6rvaltare", "Duvhanterare", "Malmletare", "Munsk=
=C3=A4nk",
    "By", "Stad", "Nybygge",
    "Stridsh=C3=A4star", "Ridh=C3=A4star", "Packh=C3=A4star", "Dragh=C3=A4s=
tar", "Oxe", "F=C3=B6l",
    "J=C3=A4gare", "B=C3=A5tar",
    "Kvarn - vatten", "Kvarn - vind", "Bageri", "Smedja", "Garveri",
]

AREAL_TYPES =3D {"Jaktmark", "Odlingsmark", "Betesmark", "Fiskevatten"}
SOLDIER_TYPES =3D {
    "Armborstskytt", "B=C3=A5gskytt", "L=C3=A5ngb=C3=A5gskytt", "Fotsoldat"=
, "Fotsoldat -
l=C3=A4tt",
    "Fotsoldat - tung", "Marinsoldat", "Sj=C3=B6man"
}
CHARACTER_TYPES =3D {
    "Officer", "Riddare med v=C3=A4pnare", "Falkenerare", "Fogde", "H=C3=A4=
rold",
    "Livmedikus", "F=C3=B6rvaltare", "Duvhanterare", "Malmletare", "Munsk=
=C3=A4nk"
}
SETTLEMENT_TYPES =3D {"By", "Stad", "Nybygge"}
ANIMAL_TYPES =3D {"Stridsh=C3=A4star", "Ridh=C3=A4star", "Packh=C3=A4star",=
 "Dragh=C3=A4star",
"Oxe", "F=C3=B6l"}
MISC_COUNT_TYPES =3D {"J=C3=A4gare", "B=C3=A5tar"}
BUILDING_TYPES =3D {"Kvarn - vatten", "Kvarn - vind", "Bageri", "Smedja",
"Garveri"}

BORDER_TYPES =3D [
    "<Ingen>", "liten v=C3=A4g", "v=C3=A4g", "stor v=C3=A4g", "vildmark", "=
tr=C3=A4sk", "berg",
"vattendrag"
]
BORDER_COLORS =3D {
    "<Ingen>": "gray",
    "liten v=C3=A4g": "black",
    "v=C3=A4g": "black",
    "stor v=C3=A4g": "brown",
    "vildmark": "green",
    "tr=C3=A4sk": "darkgreen",
    "berg": "gray",
    "vattendrag": "blue"
}
NEIGHBOR_NONE =3D "<Ingen>"
NEIGHBOR_OTHER =3D "Annat land"
MAX_NEIGHBORS =3D 6

LEVNADSKOSTNADER =3D [
    "N=C3=B6dtorftigt leverne",
    "Gement leverne",
    "Gott leverne",
    "Mycket gott leverne",
    "Lyxliv"
]

# --------------------------------------------------
# Data manager
# --------------------------------------------------
def load_worlds_from_file():
    if os.path.exists(DEFAULT_WORLDS_FILE):
        try:
            with open(DEFAULT_WORLDS_FILE, "r", encoding=3D"utf-8") as f:
                return json.load(f)
        except:
            return {}
    else:
        return {}

def save_worlds_to_file(all_worlds):
    try:
        with open(DEFAULT_WORLDS_FILE, "w", encoding=3D"utf-8") as f:
            json.dump(all_worlds, f, ensure_ascii=3DFalse, indent=3D2)
    except Exception as e:
        print(f"Fel vid sparning: {e}")

# --------------------------------------------------
# Utils
# --------------------------------------------------
def roll_dice(expr: str, debug=3DFalse):
    expr_original =3D expr.strip()
    expr =3D expr_original.lower().strip()
    unlimited =3D False
    if expr.startswith("ob"):
        unlimited =3D True
        expr =3D expr[2:].strip()
    plus_mod =3D 0
    dice_part =3D expr
    if '+' in expr:
        parts =3D expr.split('+', 1)
        dice_part =3D parts[0]
        plus_mod =3D int(parts[1])
    if 'd' not in dice_part:
        if debug:
            return 0, f"Fel: saknar 'd' i '{expr_original}'"
        else:
            return 0, ""
    dparts =3D dice_part.split('d', 1)
    dice_count =3D int(dparts[0])
    total =3D 0
    details =3D []
    if not unlimited:
        rolls =3D []
        for _ in range(dice_count):
            val =3D random.randint(1,6)
            rolls.append(val)
            total +=3D val
        total +=3D plus_mod
        if debug:
            dbg =3D f"Sl=C3=A5r {dice_count}D =3D> {rolls} + {plus_mod} =3D=
 {total}"
            return total, dbg
        else:
            return total, ""
    else:
        queue =3D dice_count
        while queue>0:
            val =3D random.randint(1,6)
            queue -=3D 1
            if val =3D=3D 6:
                details.append("6->+2 nya")
                queue +=3D 2
            else:
                details.append(str(val))
                total +=3D val
        total +=3D plus_mod
        if debug:
            dbg =3D "\n".join(details) + f"\n+{plus_mod}=3D{total}"
            return total, dbg
        else:
            return total, ""

def generate_swedish_village_name():
    FORLEDER =3D [
        "Bj=C3=B6rk", "Gran", "Lind", "Sj=C3=B6", "Berg", "=C3=84lv", "Hav"=
, "H=C3=B6g", "L=C3=B6v",
"Ek",
        "Olof", "Erik", "Karl", "Ingrid", "Tor", "Frej", "Ulf", "Sig",
"Arne", "Hilda"
    ]
    EFTERLEDER =3D [
        "by", "torp", "hult", "=C3=A5s", "rud", "forsa", "vik", "n=C3=A4s",=
 "tuna",
"stad",
        "holm", "=C3=A4nge", "g=C3=A5rd", "hed", "dal", "strand", "lid", "s=
j=C3=B6",
"tr=C3=A4sk"
    ]
    return random.choice(FORLEDER) + random.choice(EFTERLEDER)

# --------------------------------------------------
# Dynamisk Karta
# --------------------------------------------------
class DynamicMapCanvas:
    """
    En f=C3=B6renklad dynamisk karta.
    """
    def __init__(self, parent_frame, simulator, world_data):
        self.parent_frame =3D parent_frame
        self.simulator =3D simulator
        self.world_data =3D world_data
        self.canvas =3D None
        self.dynamic_scale =3D 1.0
        self.positions =3D {}

    def show(self):
        self.parent_frame.grid_rowconfigure(0, weight=3D1)
        self.parent_frame.grid_columnconfigure(0, weight=3D1)
        self.canvas =3D tk.Canvas(self.parent_frame, bg=3D"white",
scrollregion=3D(0,0,3000,2000))
        self.canvas.grid(row=3D0, column=3D0, sticky=3D"nsew")
        xsc =3D tk.Scrollbar(self.parent_frame, orient=3D"horizontal",
command=3Dself.canvas.xview)
        xsc.grid(row=3D1, column=3D0, sticky=3D"ew")
        ysc =3D tk.Scrollbar(self.parent_frame, orient=3D"vertical",
command=3Dself.canvas.yview)
        ysc.grid(row=3D0, column=3D1, sticky=3D"ns")
        self.canvas.config(xscrollcommand=3Dxsc.set, yscrollcommand=3Dysc.s=
et)

        btn_fr =3D tk.Frame(self.parent_frame, bg=3D"#f4f4f4")
        btn_fr.grid(row=3D2, column=3D0, sticky=3D"ew", pady=3D5)
        tk.Button(btn_fr, text=3D"< Tillbaka",
command=3Dself.simulator.show_no_world).pack(side=3Dtk.LEFT, padx=3D5)

        self.canvas.bind("<MouseWheel>", self.on_dynamic_map_zoom)
        self.canvas.bind("<Button-4>", self.on_dynamic_map_zoom)
        self.canvas.bind("<Button-5>", self.on_dynamic_map_zoom)

        self.draw_dynamic_map()

    def on_dynamic_map_zoom(self, event):
        if event.delta > 0 or event.num =3D=3D 4:
            factor =3D 1.1
        else:
            factor =3D 0.9
        self.dynamic_scale *=3D factor
        self.dynamic_scale =3D max(0.2, min(self.dynamic_scale, 5.0))
        self.canvas.scale("all", 0, 0, factor, factor)

    def draw_dynamic_map(self):
        self.canvas.delete("all")

        jarldomes =3D []
        for nd in self.world_data["nodes"].values():
            if self.simulator.get_depth_of_node(nd["node_id"]) =3D=3D 3:
                jarldomes.append(nd)
        if not jarldomes:
            self.simulator.add_status_message("Inga Jarld=C3=B6men att visa=
 i
dynamisk karta.")
            return

        w =3D 3000
        h =3D 2000
        self.positions =3D {}
        for nd in jarldomes:
            x =3D random.randint(200, w-200)
            y =3D random.randint(200, h-200)
            self.positions[nd["node_id"]] =3D (x, y)

        node_polygons =3D {}
        for nd in jarldomes:
            jid =3D nd["node_id"]
            x, y =3D self.positions[jid]
            neighbor_count =3D 0
            if "neighbors" in nd:
                for nb in nd["neighbors"]:
                    if isinstance(nb.get("id"), int):
                        neighbor_count +=3D 1
            sides =3D max(3, min(neighbor_count, 8))
            size =3D 40
            pts =3D []
            for k in range(sides):
                a_deg =3D (360/sides)*k
                a_rad =3D math.radians(a_deg)
                px =3D x + size*math.cos(a_rad)
                py =3D y + size*math.sin(a_rad)
                pts.extend([px, py])
            color_fill =3D "#ffdddd"
            outline =3D "red"
            poly_id =3D self.canvas.create_polygon(pts, fill=3Dcolor_fill,
outline=3Doutline, width=3D2)
            txt_id =3D self.canvas.create_text(x, y,
text=3Dnd.get("custom_name", nd["name"]), fill=3D"black")

            tag_dyn =3D f"dyn_{jid}"
            self.canvas.itemconfig(poly_id, tags=3D(tag_dyn,))
            self.canvas.itemconfig(txt_id, tags=3D(tag_dyn,))

            def on_click_node(event, n_id=3Djid):
                nd2 =3D self.world_data["nodes"].get(str(n_id))
                if nd2:
                    self.simulator.show_node_view(nd2)
            self.canvas.tag_bind(tag_dyn, "<Button-1>", on_click_node)

            node_polygons[jid] =3D {"cx": x, "cy": y, "polygon_id": poly_id=
}

        self.draw_dynamic_lines(node_polygons)

    def draw_dynamic_lines(self, node_polygons):
        for nd in self.world_data["nodes"].values():
            if self.simulator.get_depth_of_node(nd["node_id"]) =3D=3D 3 and
"neighbors" in nd:
                A_id =3D nd["node_id"]
                if A_id not in node_polygons:
                    continue
                A_cx =3D node_polygons[A_id]["cx"]
                A_cy =3D node_polygons[A_id]["cy"]
                for nb_info in nd["neighbors"]:
                    nbid =3D nb_info.get("id")
                    if isinstance(nbid, int) and nbid> A_id and nbid in
node_polygons:
                        B_cx =3D node_polygons[nbid]["cx"]
                        B_cy =3D node_polygons[nbid]["cy"]
                        border =3D nb_info.get("border", "<Ingen>")
                        color =3D BORDER_COLORS.get(border, "gray")
                        self.canvas.create_line(A_cx, A_cy, B_cx, B_cy,
fill=3Dcolor, width=3D2)

# --------------------------------------------------
# FeodalSimulator
# --------------------------------------------------
class FeodalSimulator:
    def __init__(self, root):
        self.root =3D root
        self.root.title("F=C3=B6rl=C3=A4ningssimulator - Ingen v=C3=A4rld")
        self.root.geometry("1100x700")

        self.all_worlds =3D load_worlds_from_file()
        self.active_world =3D None
        self.world_data =3D None

        self.main_frame =3D tk.Frame(self.root)
        self.main_frame.pack(fill=3D"both", expand=3DTrue)

        status_frame =3D tk.LabelFrame(self.root, text=3D"Status", padx=3D5=
,
pady=3D5)
        status_frame.pack(fill=3D"x", padx=3D5, pady=3D5)
        self.status_text =3D tk.Text(status_frame, height=3D7, wrap=3D"word=
")
        self.status_text.pack(side=3Dtk.LEFT, fill=3D"x", expand=3DTrue)
        status_scroll =3D tk.Scrollbar(status_frame,
command=3Dself.status_text.yview)
        status_scroll.pack(side=3Dtk.RIGHT, fill=3D"y")
        self.status_text.config(yscrollcommand=3Dstatus_scroll.set,
state=3D"disabled")

        top_menu =3D tk.Frame(self.main_frame)
        top_menu.pack(side=3Dtk.TOP, fill=3D"x")
        tk.Button(top_menu, text=3D"Hantera data",
command=3Dself.data_menu_view).pack(side=3Dtk.LEFT, padx=3D5, pady=3D5)

        self.map_button_frame =3D tk.Frame(top_menu)
        self.map_button_frame.pack(side=3Dtk.LEFT, padx=3D5, pady=3D5)
        tk.Button(self.map_button_frame, text=3D"Visa Karta",
command=3Dself.show_map_mode_buttons).pack(side=3Dtk.LEFT)

        # V=C3=A4nster
        left_frame =3D tk.Frame(self.main_frame)
        left_frame.pack(side=3Dtk.LEFT, fill=3D"both", padx=3D5, pady=3D5)
        self.tree =3D ttk.Treeview(left_frame)
        self.tree.pack(side=3Dtk.LEFT, fill=3D"both", expand=3DTrue)
        self.tree.column("#0", width=3D250)
        tree_vscroll =3D tk.Scrollbar(left_frame, orient=3D"vertical",
command=3Dself.tree.yview)
        tree_vscroll.pack(side=3Dtk.RIGHT, fill=3D"y")
        self.tree.configure(yscrollcommand=3Dtree_vscroll.set)
        tree_hscroll =3D tk.Scrollbar(left_frame, orient=3D"horizontal",
command=3Dself.tree.xview)
        tree_hscroll.pack(side=3Dtk.BOTTOM, fill=3D"x")
        self.tree.configure(xscrollcommand=3Dtree_hscroll.set)
        self.tree["columns"] =3D ("#0",)
        self.tree.heading("#0", text=3D"Struktur")
        self.tree.bind("<Double-1>", self.on_tree_double_click)

        # H=C3=B6ger
        self.right_frame =3D tk.Frame(self.main_frame, bg=3D"#f4f4f4")
        self.right_frame.pack(side=3Dtk.RIGHT, fill=3D"both", expand=3DTrue=
)

        self.dynamic_map =3D None

        style =3D ttk.Style()
        style.configure("BlackWhite.TCombobox", foreground=3D"black",
fieldbackground=3D"white")

        self.show_no_world()

    # Status
    def add_status_message(self, msg):
        self.status_text.config(state=3D"normal")
        self.status_text.insert("end", msg + "\n")
        self.status_text.see("end")
        self.status_text.config(state=3D"disabled")

    def save_current_world(self):
        if self.active_world:
            self.all_worlds[self.active_world] =3D self.world_data
            save_worlds_to_file(self.all_worlds)

    def show_no_world(self):
        for w in self.right_frame.winfo_children():
            w.destroy()
        if self.active_world:
            tk.Label(self.right_frame, text=3Df"Aktiv v=C3=A4rld:
{self.active_world}", bg=3D"#f4f4f4").pack(fill=3D"both", expand=3DTrue)
        else:
            tk.Label(self.right_frame, text=3D"Ingen v=C3=A4rld =C3=A4r akt=
iv.",
bg=3D"#f4f4f4").pack(fill=3D"both", expand=3DTrue)

    def store_open_states(self):
        open_dict =3D {}
        def gather(item):
            open_dict[item] =3D self.tree.item(item, 'open')
            for child in self.tree.get_children(item):
                gather(child)
        for top_item in self.tree.get_children():
            gather(top_item)
        selection =3D self.tree.selection()
        return open_dict, selection

    def restore_open_states(self, open_dict, selection):
        def apply_states(item):
            if item in open_dict:
                self.tree.item(item, open=3Dopen_dict[item])
            for cc in self.tree.get_children(item):
                apply_states(cc)
        for top_item in self.tree.get_children():
            apply_states(top_item)
        if selection:
            for s_item in selection:
                self.tree.selection_add(s_item)
                self.tree.focus(s_item)

    # Data
    def data_menu_view(self):
        for w in self.right_frame.winfo_children():
            w.destroy()
        fr =3D tk.Frame(self.right_frame, bg=3D"#f4f4f4")
        fr.pack(fill=3D"both", expand=3DTrue)
        tk.Label(fr, text=3D"Hantera data", font=3D("Arial", 14),
bg=3D"#f4f4f4").pack(pady=3D5)
        tk.Button(fr, text=3D"Hantera V=C3=A4rld",
command=3Dself.manage_worlds_view).pack(pady=3D5)
        tk.Button(fr, text=3D"Hantera H=C3=A4rskare",
command=3Dself.manage_characters_view).pack(pady=3D5)
        tk.Button(fr, text=3D"< Tillbaka",
command=3Dself.show_no_world).pack(pady=3D5)

    def manage_worlds_view(self):
        for w in self.right_frame.winfo_children():
            w.destroy()
        fr =3D tk.Frame(self.right_frame, bg=3D"#f4f4f4")
        fr.pack(fill=3D"both", expand=3DTrue)
        tk.Label(fr, text=3D"Hantera v=C3=A4rldar", font=3D("Arial", 14),
bg=3D"#f4f4f4").pack(pady=3D5)
        tk.Button(fr, text=3D"Skapa ny v=C3=A4rld",
command=3Dself.create_new_world).pack(pady=3D5)
        lb =3D tk.Listbox(fr, height=3D10)
        lb.pack(pady=3D5)
        self.all_worlds =3D load_worlds_from_file()
        for wname in sorted(self.all_worlds.keys()):
            lb.insert(tk.END, wname)
        def do_load():
            sel =3D lb.curselection()
            if sel:
                wname =3D lb.get(sel[0])
                self.load_world(wname)
        def do_delete():
            sel =3D lb.curselection()
            if sel:
                wname =3D lb.get(sel[0])
                if messagebox.askyesno("Radera?", f"Radera '{wname}'?"):
                    del self.all_worlds[wname]
                    save_worlds_to_file(self.all_worlds)
                    lb.delete(sel[0])
                    if self.active_world =3D=3D wname:
                        self.active_world =3D None
                        self.world_data =3D None
                        self.root.title("F=C3=B6rl=C3=A4ningssimulator - In=
gen v=C3=A4rld")
                        self.show_no_world()
        def do_copy():
            sel =3D lb.curselection()
            if sel:
                wname =3D lb.get(sel[0])
                new_name =3D simpledialog.askstring("Kopiera v=C3=A4rld", f=
"Kopia
av '{wname}'?")
                if new_name:
                    if new_name in self.all_worlds:
                        self.add_status_message(f"V=C3=A4rld '{new_name}' f=
inns
redan.")
                        return
                    import copy
                    self.all_worlds[new_name] =3D
copy.deepcopy(self.all_worlds[wname])
                    save_worlds_to_file(self.all_worlds)
                    lb.insert(tk.END, new_name)
                    self.add_status_message(f"Kopierade '{wname}' ->
'{new_name}'.")
        tk.Button(fr, text=3D"Ladda", command=3Ddo_load).pack(pady=3D2)
        tk.Button(fr, text=3D"Radera", command=3Ddo_delete).pack(pady=3D2)
        tk.Button(fr, text=3D"Kopiera", command=3Ddo_copy).pack(pady=3D2)
        tk.Button(fr, text=3D"< Tillbaka",
command=3Dself.data_menu_view).pack(pady=3D5)

    def create_new_world(self):
        wname =3D simpledialog.askstring("Ny v=C3=A4rld", "Namn p=C3=A5 ny =
v=C3=A4rld?")
        if not wname:
            return
        if wname in self.all_worlds:
            self.add_status_message(f"V=C3=A4rld '{wname}' finns redan.")
            return
        new_data =3D {
            "nodes": {},
            "next_node_id": 1,
            "characters": {}
        }
        root_id =3D new_data["next_node_id"]
        new_data["next_node_id"] +=3D 1
        new_data["nodes"][str(root_id)] =3D {
            "node_id": root_id,
            "parent_id": None,
            "name": "Kungarike (root)",
            "population": 100,
            "ruler_id": None,
            "num_subfiefs": 0,
            "children": []
        }
        self.all_worlds[wname] =3D new_data
        save_worlds_to_file(self.all_worlds)
        self.active_world =3D wname
        self.world_data =3D new_data
        self.root.title(f"F=C3=B6rl=C3=A4ningssimulator - {wname}")
        self.fill_tree()
        self.add_status_message(f"V=C3=A4rld '{wname}' skapad.")

    def load_world(self, wname):
        if wname not in self.all_worlds:
            return
        self.active_world =3D wname
        self.world_data =3D self.all_worlds[wname]
        self.root.title(f"F=C3=B6rl=C3=A4ningssimulator - {wname}")
        self.fill_tree()
        self.add_status_message(f"V=C3=A4rld '{wname}' laddad.")

    # Tree
    def fill_tree(self):
        if not self.world_data:
            return
        root_node =3D None
        for nd in self.world_data["nodes"].values():
            if nd["parent_id"] is None:
                root_node =3D nd
                break
        if not root_node:
            self.add_status_message("Ingen rotnod hittad.")
            return
        self.tree.delete(*self.tree.get_children())
        self.add_tree_node("", root_node)
        self.show_no_world()

    def add_tree_node(self, parent_iid, node):
        depth =3D self.get_depth_of_node(node["node_id"])
        label =3D self.get_display_name_for_node(node, depth)
        my_id =3D self.tree.insert(parent_iid, "end",
iid=3Dstr(node["node_id"]), text=3Dlabel, open=3D(depth=3D=3D0))
        for cid in node.get("children", []):
            child =3D self.world_data["nodes"].get(str(cid))
            if child:
                self.add_tree_node(my_id, child)

    def get_display_name_for_node(self, node, depth):
        if depth =3D=3D 0:
            return node.get("name", "Kungarike")
        elif depth =3D=3D 1:
            return "Furstend=C3=B6me"
        elif depth =3D=3D 2:
            return "Hertigd=C3=B6me"
        else:
            # res_type - custom_name - ev ruler
            rtype =3D node.get("res_type", "Resurs")
            custom =3D node.get("custom_name", "").strip()
            rid =3D node.get("ruler_id")
            ruler_str =3D ""
            if rid and str(rid) in self.world_data.get("characters", {}):
                ruler_str =3D self.world_data["characters"][str(rid)]["name=
"]
            parts =3D []
            if rtype:
                parts.append(rtype)
            if custom:
                parts.append(custom)
            if ruler_str:
                parts.append(ruler_str)
            return " - ".join(parts) if parts else node.get("name","Nod")

    def get_depth_of_node(self, node_id):
        d =3D 0
        c =3D self.world_data["nodes"].get(str(node_id))
        while c and c["parent_id"] is not None:
            d +=3D 1
            c =3D self.world_data["nodes"].get(str(c["parent_id"]))
        return d

    def on_tree_double_click(self, event):
        item_id =3D self.tree.focus()
        if not item_id or not self.world_data:
            return
        node =3D self.world_data["nodes"].get(item_id)
        if node:
            self.show_node_view(node)

    # H=C3=A4rskare
    def manage_characters_view(self):
        for w in self.right_frame.winfo_children():
            w.destroy()
        fr =3D tk.Frame(self.right_frame, bg=3D"#f4f4f4")
        fr.pack(fill=3D"both", expand=3DTrue)
        tk.Label(fr, text=3D"Hantera H=C3=A4rskare", font=3D("Arial", 14),
bg=3D"#f4f4f4").pack(pady=3D5)
        lb =3D tk.Listbox(fr, height=3D10)
        lb.pack(pady=3D5)
        if "characters" not in self.world_data:
            self.world_data["characters"] =3D {}
        sorted_chars =3D sorted(self.world_data["characters"].items(),
key=3Dlambda x: int(x[0]))
        for cid, data in sorted_chars:
            lb.insert(tk.END, f"{cid}: {data['name']}")

        def get_sel_id():
            sel =3D lb.curselection()
            if sel:
                line =3D lb.get(sel[0])
                return line.split(":")[0]
            return None

        def do_new():
            self.show_create_char_view(None)
        def do_edit():
            cid =3D get_sel_id()
            if cid:
                self.show_edit_char_view(cid)
        def do_delete():
            cid =3D get_sel_id()
            if cid and messagebox.askyesno("Radera?", f"Radera h=C3=A4rskar=
e
{cid}?"):
                for nd in self.world_data["nodes"].values():
                    if nd.get("ruler_id") =3D=3D cid:
                        nd["ruler_id"] =3D None
                if cid in self.world_data["characters"]:
                    del self.world_data["characters"][cid]
                self.save_current_world()
                self.manage_characters_view()

        tk.Button(fr, text=3D"Ny h=C3=A4rskare", command=3Ddo_new).pack(pad=
y=3D2)
        tk.Button(fr, text=3D"Redigera", command=3Ddo_edit).pack(pady=3D2)
        tk.Button(fr, text=3D"Radera", command=3Ddo_delete).pack(pady=3D2)
        tk.Button(fr, text=3D"< Tillbaka",
command=3Dself.data_menu_view).pack(pady=3D5)

    def show_create_char_view(self, node_data):
        for w in self.right_frame.winfo_children():
            w.destroy()
        fr =3D tk.Frame(self.right_frame, bg=3D"#f4f4f4")
        fr.pack(fill=3D"both", expand=3DTrue)
        tk.Label(fr, text=3D"Skapa Ny H=C3=A4rskare", font=3D("Arial", 14),
bg=3D"#f4f4f4").pack(pady=3D5)

        tk.Label(fr, text=3D"Namn:", bg=3D"#f4f4f4").pack()
        name_var =3D tk.StringVar()
        tk.Entry(fr, textvariable=3Dname_var).pack()

        def do_save():
            if "characters" not in self.world_data:
                self.world_data["characters"] =3D {}
            existing_ids =3D [int(k) for k in
self.world_data["characters"].keys()] if self.world_data["characters"] else
[]
            new_id =3D max(existing_ids)+1 if existing_ids else 1
            self.world_data["characters"][str(new_id)] =3D {
                "name": name_var.get(),
                "wealth": 0,
                "description": "",
                "skills": []
            }
            self.add_status_message(f"Skapade ny h=C3=A4rskare med ID {new_=
id}")
            if node_data is not None:
                node_data["ruler_id"] =3D str(new_id)
            self.save_current_world()
            self.manage_characters_view()

        tk.Button(fr, text=3D"Spara", command=3Ddo_save).pack(pady=3D5)
        tk.Button(fr, text=3D"< Tillbaka",
command=3Dself.manage_characters_view).pack(pady=3D5)

    def show_edit_char_view(self, cid):
        for w in self.right_frame.winfo_children():
            w.destroy()
        char =3D self.world_data["characters"].get(cid)
        if not char:
            return
        fr =3D tk.Frame(self.right_frame, bg=3D"#f4f4f4")
        fr.pack(fill=3D"both", expand=3DTrue)
        tk.Label(fr, text=3Df"Redigera H=C3=A4rskare (ID {cid})", font=3D("=
Arial",
14), bg=3D"#f4f4f4").pack(pady=3D5)

        tk.Label(fr, text=3D"Namn:", bg=3D"#f4f4f4").pack()
        name_var =3D tk.StringVar(value=3Dchar.get("name",""))
        tk.Entry(fr, textvariable=3Dname_var).pack()

        def do_save():
            char["name"] =3D name_var.get()
            self.save_current_world()
            self.manage_characters_view()

        tk.Button(fr, text=3D"Spara", command=3Ddo_save).pack(pady=3D5)
        tk.Button(fr, text=3D"< Tillbaka",
command=3Dself.manage_characters_view).pack(pady=3D5)

    # Och om man vill ha skill editor
    def open_skill_editor(self, *args, **kwargs):
        messagebox.showinfo("Skill Editor","Ej implementerad.")
        self.show_no_world()
    def show_skill_edit_view(self, *args, **kwargs):
        messagebox.showinfo("Skill Edit","Ej implementerad.")
        return

    # --------------------------------------------------
    # Visa/redigera noder
    # --------------------------------------------------
    def show_node_view(self, node):
        for w in self.right_frame.winfo_children():
            w.destroy()
        fr =3D tk.Frame(self.right_frame, bg=3D"#f4f4f4")
        fr.pack(fill=3D"both", expand=3DTrue)

        tk.Label(fr, text=3Df"Nod ID: {node['node_id']}", font=3D("Arial", =
14),
bg=3D"#f4f4f4").pack(pady=3D5)
        depth =3D self.get_depth_of_node(node["node_id"])
        if depth < 3:
            self.show_upper_node_editor(fr, node)
        elif depth =3D=3D 3:
            self.show_jarldome_editor(fr, node)
        else:
            self.show_resource_editor(fr, node)

    def show_upper_node_editor(self, parent_frame, node):
        # Kungarike, Furstend=C3=B6me, Hertigd=C3=B6me
        tk.Label(parent_frame, text=3D"Redigera =C3=B6verordnad nod",
bg=3D"#f4f4f4").pack(pady=3D5)

        def do_delete():
            if messagebox.askyesno("Radera?", f"Radera nod
{node['node_id']}?"):
                pid =3D node.get("parent_id")
                if pid is not None:
                    pnode =3D self.world_data["nodes"].get(str(pid))
                    if pnode and node["node_id"] in pnode.get("children",
[]):
                        pnode["children"].remove(node["node_id"])
                self.delete_node_and_descendants(node["node_id"])
                self.save_current_world()
                self.tree.delete(*self.tree.get_children())
                self.fill_tree()
                self.show_no_world()
        tk.Button(parent_frame, text=3D"Radera denna nod", fg=3D"red",
command=3Ddo_delete).pack(pady=3D2)

        tk.Label(parent_frame, text=3D"Namn:", bg=3D"#f4f4f4").pack()
        name_var =3D tk.StringVar(value=3Dnode.get("name",""))
        tk.Entry(parent_frame, textvariable=3Dname_var).pack()

        tk.Label(parent_frame, text=3D"Befolkning:", bg=3D"#f4f4f4").pack()
        pop_var =3D tk.IntVar(value=3Dnode.get("population",0))
        tk.Entry(parent_frame, textvariable=3Dpop_var, width=3D8).pack()

        tk.Label(parent_frame, text=3D"Antal underf=C3=B6rl=C3=A4ningar:",
bg=3D"#f4f4f4").pack()
        sub_var =3D tk.IntVar(value=3Dnode.get("num_subfiefs",0))
        tk.Spinbox(parent_frame, from_=3D0, to=3D50, textvariable=3Dsub_var=
,
width=3D5).pack()

        def update_subfiefs():
            node["name"] =3D name_var.get()
            node["population"] =3D pop_var.get()
            node["num_subfiefs"] =3D sub_var.get()
            self.update_subfiefs_for_node(node)
        tk.Button(parent_frame, text=3D"Uppdatera underf=C3=B6rl=C3=A4ninga=
r",
command=3Dupdate_subfiefs).pack(pady=3D5)

        def do_save():
            old =3D node.get("name","")
            node["name"] =3D name_var.get()
            node["population"] =3D pop_var.get()
            self.save_current_world()
            self.add_status_message(f"Nod {node['node_id']} uppdaterad:
'{old}' -> '{node['name']}'")
            self.tree.item(str(node["node_id"]),
text=3Dself.get_display_name_for_node(node,
self.get_depth_of_node(node["node_id"])))
        tk.Button(parent_frame, text=3D"Spara noddata",
command=3Ddo_save).pack(pady=3D5)
        tk.Button(parent_frame, text=3D"< Tillbaka",
command=3Dself.show_no_world).pack(pady=3D5)

    def show_jarldome_editor(self, parent_frame, node):
        # Jarld=C3=B6me-liknande, men du =C3=B6nskar att res_type=3D"Resurs=
" + random
name i "custom_name"
        tk.Label(parent_frame, text=3D"Redigera Jarld=C3=B6me (niv=C3=A5=3D=
2)",
font=3D("Arial",14), bg=3D"#f4f4f4").pack(pady=3D5)

        def do_delete():
            if messagebox.askyesno("Radera?", f"Radera nod
{node['node_id']}?"):
                pid =3D node.get("parent_id")
                if pid is not None:
                    pnode =3D self.world_data["nodes"].get(str(pid))
                    if pnode and node["node_id"] in
pnode.get("children",[]):
                        pnode["children"].remove(node["node_id"])
                self.delete_node_and_descendants(node["node_id"])
                self.save_current_world()
                self.tree.delete(*self.tree.get_children())
                self.fill_tree()
                self.show_no_world()
        tk.Button(parent_frame, text=3D"Radera denna nod", fg=3D"red",
command=3Ddo_delete).pack(pady=3D2)

        # Denna jarld=C3=B6me skapas med res_type=3D"Resurs" + custom_name=
=3Dslump.
        # Men om man byter i UI =3D> uppdatera custom_name =3D> uppdatera t=
r=C3=A4d.
        if not node.get("res_type"):
            node["res_type"] =3D "Resurs"
        if not node.get("custom_name"):
            # slump
            node["custom_name"] =3D generate_swedish_village_name()

        tk.Label(parent_frame, text=3D"Namnruta (custom_name) f=C3=B6r
slumpnamn:", bg=3D"#f4f4f4").pack()
        custom_name_var =3D tk.StringVar(value=3Dnode.get("custom_name","")=
)
        tk.Entry(parent_frame, textvariable=3Dcustom_name_var,
width=3D20).pack()

        tk.Label(parent_frame, text=3D"Befolkning (Jarld=C3=B6me):",
bg=3D"#f4f4f4").pack()
        pop_var =3D tk.IntVar(value=3Dnode.get("population",0))
        tk.Entry(parent_frame, textvariable=3Dpop_var, width=3D8).pack()

        tk.Label(parent_frame, text=3D"Antal underf=C3=B6rl=C3=A4ningar:",
bg=3D"#f4f4f4").pack()
        sub_var =3D tk.IntVar(value=3Dnode.get("num_subfiefs",0))
        tk.Spinbox(parent_frame, from_=3D0, to=3D50, textvariable=3Dsub_var=
,
width=3D5).pack()

        def update_subfiefs():
            node["custom_name"] =3D custom_name_var.get()
            node["population"] =3D pop_var.get()
            node["num_subfiefs"] =3D sub_var.get()
            self.update_subfiefs_for_node(node)

        tk.Button(parent_frame, text=3D"Uppdatera underf=C3=B6rl=C3=A4ninga=
r",
command=3Dupdate_subfiefs).pack(pady=3D5)

        def do_save():
            old =3D node.get("custom_name","")
            node["custom_name"] =3D custom_name_var.get()
            node["population"] =3D pop_var.get()
            node["res_type"] =3D "Resurs"  # for sure
            self.save_current_world()
            self.add_status_message(f"Jarld=C3=B6me (ID {node['node_id']})
uppdaterad: '{old}' -> '{node['custom_name']}'")
            self.tree.item(str(node["node_id"]),
text=3Dself.get_display_name_for_node(node, 3))
        tk.Button(parent_frame, text=3D"Spara jarld=C3=B6me",
command=3Ddo_save).pack(pady=3D5)
        tk.Button(parent_frame, text=3D"< Tillbaka",
command=3Dself.show_no_world).pack(pady=3D5)

    def show_resource_editor(self, parent_frame, node):
        # Djup>=3D4
        tk.Label(parent_frame, text=3D"Redigera Resurs", font=3D("Arial",14=
),
bg=3D"#f4f4f4").pack(pady=3D5)

        def do_delete():
            if messagebox.askyesno("Radera?", f"Radera nod
{node['node_id']}?"):
                pid =3D node.get("parent_id")
                if pid is not None:
                    pnode =3D self.world_data["nodes"].get(str(pid))
                    if pnode and node["node_id"] in
pnode.get("children",[]):
                        pnode["children"].remove(node["node_id"])
                self.delete_node_and_descendants(node["node_id"])
                self.save_current_world()
                self.tree.delete(*self.tree.get_children())
                self.fill_tree()
                self.show_no_world()
        tk.Button(parent_frame, text=3D"Radera denna resurs", fg=3D"red",
command=3Ddo_delete).pack(pady=3D2)

        # Resurstyp
        tk.Label(parent_frame, text=3D"Typ:", bg=3D"#f4f4f4").pack()
        res_type_var =3D tk.StringVar(value=3Dnode.get("res_type","Resurs")=
)
        cb_type =3D ttk.Combobox(parent_frame, textvariable=3Dres_type_var,
values=3Dsorted(RES_TYPES),
                               state=3D"readonly",
style=3D"BlackWhite.TCombobox", width=3D25)
        cb_type.pack()

        tk.Label(parent_frame, text=3D"Eget Namn (custom_name):",
bg=3D"#f4f4f4").pack()
        custom_name_var =3D tk.StringVar(value=3Dnode.get("custom_name","")=
)
        tk.Entry(parent_frame, textvariable=3Dcustom_name_var,
width=3D20).pack()

        # Ruler
        tk.Label(parent_frame, text=3D"V=C3=A4lj H=C3=A4rskare:", bg=3D"#f4=
f4f4").pack()
        chars_list =3D ["(ingen)"]
        if "characters" in self.world_data:
            for cid, cdat in self.world_data["characters"].items():
                chars_list.append(f"{cid}: {cdat['name']}")
        ruler_var =3D tk.StringVar()
        if node.get("ruler_id"):
            rid_str =3D str(node["ruler_id"])
            if rid_str in self.world_data["characters"]:
                nm =3D self.world_data["characters"][rid_str]["name"]
                ruler_var.set(f"{rid_str}: {nm}")
            else:
                ruler_var.set("(ingen)")
        else:
            ruler_var.set("(ingen)")
        cb_ruler =3D ttk.Combobox(parent_frame, textvariable=3Druler_var,
values=3Dchars_list,
                                state=3D"readonly",
style=3D"BlackWhite.TCombobox")
        cb_ruler.pack()

        # Underf=C3=B6rl=C3=A4ningar
        tk.Label(parent_frame, text=3D"Antal underf=C3=B6rl=C3=A4ningar:",
bg=3D"#f4f4f4").pack()
        sub_var =3D tk.IntVar(value=3Dnode.get("num_subfiefs",0))
        tk.Spinbox(parent_frame, from_=3D0, to=3D50, textvariable=3Dsub_var=
,
width=3D5).pack()

        # Subtyp-frame
        subtype_frame =3D tk.Frame(parent_frame, bg=3D"#f4f4f4")
        subtype_frame.pack(fill=3D"x", pady=3D5)

        def redraw_subtype():
            for w in subtype_frame.winfo_children():
                w.destroy()

            the_type =3D res_type_var.get()
            # Areal
            if the_type in AREAL_TYPES:
                row =3D tk.Frame(subtype_frame, bg=3D"#f4f4f4")
                row.pack(fill=3D"x", pady=3D2)
                tk.Label(row, text=3D"Areal:",
bg=3D"#f4f4f4").pack(side=3Dtk.LEFT, padx=3D5)
                area_var =3D tk.StringVar(value=3Dnode.get("area_size",""))
                tk.Entry(row, textvariable=3Darea_var,
width=3D10).pack(side=3Dtk.LEFT)
                tk.Label(row, text=3D"Kvalitet(1-5):",
bg=3D"#f4f4f4").pack(side=3Dtk.LEFT, padx=3D5)
                area_q_var =3D tk.IntVar(value=3Dnode.get("area_quality",1)=
)
                cb_q =3D ttk.Combobox(row, textvariable=3Darea_q_var,
values=3D[1,2,3,4,5],
                                    state=3D"readonly", width=3D3)
                cb_q.pack(side=3Dtk.LEFT)

                def store_areal():
                    node["area_size"] =3D area_var.get()
                    node["area_quality"] =3D area_q_var.get()
                tk.Button(subtype_frame, text=3D"Uppdatera Areal",
command=3Dstore_areal).pack(pady=3D5)

            elif the_type in SOLDIER_TYPES:
                row =3D tk.Frame(subtype_frame, bg=3D"#f4f4f4")
                row.pack(fill=3D"x", pady=3D2)
                tk.Label(row, text=3D"Antal soldater:",
bg=3D"#f4f4f4").pack(side=3Dtk.LEFT, padx=3D5)
                s_count_var =3D tk.IntVar(value=3Dnode.get("count",0))
                tk.Entry(row, textvariable=3Ds_count_var,
width=3D6).pack(side=3Dtk.LEFT)
                def store_soldiers():
                    node["count"] =3D s_count_var.get()
                tk.Button(subtype_frame, text=3D"Uppdatera Antal",
command=3Dstore_soldiers).pack(pady=3D5)

            elif the_type in CHARACTER_TYPES:
                tk.Label(subtype_frame, text=3D"Endast H=C3=A4rskare, ingen=
 extra
info.", bg=3D"#f4f4f4").pack(pady=3D5)

            elif the_type in SETTLEMENT_TYPES:
                # Bos=C3=A4ttning =3D> 4 st rutor + hantverkare
                row_b =3D tk.Frame(subtype_frame, bg=3D"#f4f4f4")
                row_b.pack(fill=3D"x", pady=3D2)
                tk.Label(row_b, text=3D"Fria b=C3=B6nder:",
bg=3D"#f4f4f4").pack(side=3Dtk.LEFT, padx=3D5)
                free_var =3D tk.IntVar(value=3Dnode.get("pop_free",0))
                tk.Entry(row_b, textvariable=3Dfree_var,
width=3D6).pack(side=3Dtk.LEFT)
                tk.Label(row_b, text=3D"Ofria:",
bg=3D"#f4f4f4").pack(side=3Dtk.LEFT, padx=3D5)
                serf_var =3D tk.IntVar(value=3Dnode.get("pop_serf",0))
                tk.Entry(row_b, textvariable=3Dserf_var,
width=3D6).pack(side=3Dtk.LEFT)
                tk.Label(row_b, text=3D"Tr=C3=A4lar:",
bg=3D"#f4f4f4").pack(side=3Dtk.LEFT, padx=3D5)
                slave_var =3D tk.IntVar(value=3Dnode.get("pop_slave",0))
                tk.Entry(row_b, textvariable=3Dslave_var,
width=3D6).pack(side=3Dtk.LEFT)
                tk.Label(row_b, text=3D"Borgare:",
bg=3D"#f4f4f4").pack(side=3Dtk.LEFT, padx=3D5)
                borg_var =3D tk.IntVar(value=3Dnode.get("pop_borgare",0))
                tk.Entry(row_b, textvariable=3Dborg_var,
width=3D6).pack(side=3Dtk.LEFT)

                def store_bos():
                    node["pop_free"] =3D free_var.get()
                    node["pop_serf"] =3D serf_var.get()
                    node["pop_slave"] =3D slave_var.get()
                    node["pop_borgare"] =3D borg_var.get()

                tk.Button(subtype_frame, text=3D"Uppdatera bos=C3=A4ttning"=
,
command=3Dstore_bos).pack(pady=3D5)

                # Hantverkare
                if not node.get("craftsmen"):
                    node["craftsmen"] =3D []

                tk.Label(subtype_frame, text=3D"Hantverkare( max 9 ):",
bg=3D"#f4f4f4").pack(anchor=3D"w")

                crafts_frame =3D tk.Frame(subtype_frame, bg=3D"#f4f4f4")
                crafts_frame.pack(fill=3D"x", pady=3D2)

                def refresh_crafts():
                    for xx in crafts_frame.winfo_children():
                        xx.destroy()

                    # existerande rader
                    for idx, craf in enumerate(node["craftsmen"]):
                        r =3D tk.Frame(crafts_frame, bg=3D"#f4f4f4")
                        r.pack(fill=3D"x", pady=3D1)
                        ctype_var =3D tk.StringVar(value=3Dcraf.get("type",=
""))
                        ccount_var =3D
tk.StringVar(value=3Dstr(craf.get("count",1)))

                        cb =3D ttk.Combobox(r, textvariable=3Dctype_var,

values=3D["Smed","Snickare","Bryggare","Bagare","Kock","Tunnbindare","Skr=
=C3=A4ddare"],
                                          state=3D"readonly", width=3D15)
                        cb.pack(side=3Dtk.LEFT, padx=3D3)
                        spin =3D ttk.Combobox(r, textvariable=3Dccount_var,
                                            values=3D[str(i) for i in
range(1,10)],
                                            state=3D"readonly", width=3D3)
                        spin.pack(side=3Dtk.LEFT, padx=3D3)

                        def do_store(ix=3Didx, var_t=3Dctype_var,
var_c=3Dccount_var):
                            node["craftsmen"][ix]["type"] =3D var_t.get()
                            node["craftsmen"][ix]["count"] =3D
int(var_c.get())

                        def do_del(ix=3Didx):
                            node["craftsmen"].pop(ix)
                            refresh_crafts()

                        tk.Button(r, text=3D"Spara",
command=3Ddo_store).pack(side=3Dtk.LEFT, padx=3D3)
                        tk.Button(r, text=3D"Radera",
command=3Ddo_del).pack(side=3Dtk.LEFT, padx=3D3)

                    # tom rad
                    if len(node["craftsmen"])<9:
                        row_add =3D tk.Frame(crafts_frame, bg=3D"#f4f4f4")
                        row_add.pack(fill=3D"x", pady=3D1)
                        tk.Label(row_add, text=3D"(Tom rad)",
bg=3D"#f4f4f4").pack(side=3Dtk.LEFT, padx=3D5)
                        def do_add_new():
                            node["craftsmen"].append({"type":"","count":1})
                            refresh_crafts()
                        tk.Button(row_add, text=3D"L=C3=A4gg till hantverka=
re",
command=3Ddo_add_new).pack(side=3Dtk.LEFT, padx=3D5)

                refresh_crafts()

            elif the_type in ANIMAL_TYPES or the_type in MISC_COUNT_TYPES
or the_type in BUILDING_TYPES:
                row =3D tk.Frame(subtype_frame, bg=3D"#f4f4f4")
                row.pack(fill=3D"x", pady=3D2)
                tk.Label(row, text=3D"Antal:",
bg=3D"#f4f4f4").pack(side=3Dtk.LEFT, padx=3D5)
                c_var =3D tk.IntVar(value=3Dnode.get("count",0))
                tk.Entry(row, textvariable=3Dc_var,
width=3D6).pack(side=3Dtk.LEFT)
                def store_x():
                    node["count"] =3D c_var.get()
                tk.Button(subtype_frame, text=3D"Uppdatera Antal",
command=3Dstore_x).pack(pady=3D5)

        def on_type_change(*args):
            node["res_type"] =3D res_type_var.get()
            redraw_subtype()

        res_type_var.trace_add("write", on_type_change)

        # Updatera undernoder
        def do_update_subfiefs():
            node["res_type"] =3D res_type_var.get()
            node["custom_name"] =3D custom_name_var.get()
            sel =3D ruler_var.get()
            if sel=3D=3D"(ingen)":
                node["ruler_id"] =3D None
            else:
                rid =3D sel.split(":")[0].strip()
                node["ruler_id"] =3D rid
            node["num_subfiefs"] =3D sub_var.get()
            self.update_subfiefs_for_node(node)

        tk.Button(parent_frame, text=3D"Uppdatera underf=C3=B6rl=C3=A4ninga=
r",
command=3Ddo_update_subfiefs).pack(pady=3D5)

        def do_save_resource():
            node["res_type"] =3D res_type_var.get()
            node["custom_name"] =3D custom_name_var.get()
            sel2 =3D ruler_var.get()
            node["ruler_id"] =3D None if sel2=3D=3D"(ingen)" else
sel2.split(":")[0].strip()
            node["num_subfiefs"] =3D sub_var.get()
            self.save_current_world()
            self.add_status_message(f"Resurs {node['node_id']} uppdaterad."=
)
            self.tree.item(str(node["node_id"]),
text=3Dself.get_display_name_for_node(node,
self.get_depth_of_node(node["node_id"])))
        tk.Button(parent_frame, text=3D"Spara resurs",
command=3Ddo_save_resource).pack(pady=3D5)

        redraw_subtype()

    # --------------------------------------------------
    # Subnoder
    # --------------------------------------------------
    def update_subfiefs_for_node(self, node):
        """
        Kungarike(d0)->Furstend=C3=B6me(d1)
        Furstend=C3=B6me(d1)->Hertigd=C3=B6me(d2)
        Hertigd=C3=B6me(d2)-> Jarld=C3=B6me(d3) med slump i custom_name men
res_type=3D"Resurs"
        Jarld=C3=B6me(d3)-> barn blir Resurs(d4)
        >=3D d4 =3D> "Nod"
        """
        open_dict, selection =3D self.store_open_states()

        current =3D len(node.get("children",[]))
        target =3D node.get("num_subfiefs",0)

        d =3D self.get_depth_of_node(node["node_id"])

        while current < target:
            self.world_data["next_node_id"] +=3D 1
            new_id =3D self.world_data["next_node_id"]

            if d =3D=3D 0:
                child_name =3D "Furstend=C3=B6me"
            elif d =3D=3D 1:
                child_name =3D "Hertigd=C3=B6me"
            elif d =3D=3D 2:
                # Jarld=C3=B6me =3D> res_type=3DResurs, slump i custom_name
                child_name =3D "Resurs"
            elif d =3D=3D 3:
                child_name =3D "Resurs"
            else:
                child_name =3D "Nod"

            if d=3D=3D2:
                # jarld=C3=B6me-liknande: node["res_type"] =3D "Resurs",
node["custom_name"] =3D slump
                cnode =3D {
                    "node_id": new_id,
                    "parent_id": node["node_id"],
                    "ruler_id": None,
                    "children": [],
                    "name": "",
                    "res_type": "Resurs",
                    "custom_name": generate_swedish_village_name(),
                    "num_subfiefs": 0,
                    "neighbors": [{"id": None, "border": None} for _ in
range(MAX_NEIGHBORS)],
                    "population": 0
                }
            elif d=3D=3D3:
                # barn till jarld=C3=B6me =3D> resurs
                cnode =3D {
                    "node_id": new_id,
                    "parent_id": node["node_id"],
                    "ruler_id": None,
                    "children": [],
                    "name": "",
                    "res_type": "Resurs",
                    "custom_name": "",
                    "num_subfiefs": 0
                }
            else:
                cnode =3D {
                    "node_id": new_id,
                    "parent_id": node["node_id"],
                    "ruler_id": None,
                    "children": [],
                    "name": child_name,
                    "num_subfiefs": 0
                }
                if d+1 =3D=3D 4:
                    cnode["res_type"] =3D "Resurs"
                    cnode["custom_name"] =3D ""
                    cnode["population"] =3D 0
                    cnode["count"] =3D 0
                    cnode["pop_free"] =3D 0
                    cnode["pop_serf"] =3D 0
                    cnode["pop_borgare"] =3D 0

            self.world_data["nodes"][str(new_id)] =3D cnode
            node.setdefault("children",[]).append(new_id)
            current+=3D1

        while current>target:
            rid =3D node["children"].pop()
            self.delete_node_and_descendants(rid)
            current-=3D1

        self.save_current_world()
        self.tree.delete(*self.tree.get_children())
        self.fill_tree()
        self.restore_open_states(open_dict, selection)
        self.show_node_view(node)

    def delete_node_and_descendants(self, node_id):
        nd =3D self.world_data["nodes"].get(str(node_id))
        if not nd:
            return
        for c in nd.get("children",[]):
            self.delete_node_and_descendants(c)
        if "neighbors" in nd:
            for nb in nd["neighbors"]:
                if nb.get("id") and nb["id"]!=3D"other":
                    self.remove_from_neighbors(nb.get("id"), node_id)
        if str(node_id) in self.world_data["nodes"]:
            del self.world_data["nodes"][str(node_id)]

    def remove_from_neighbors(self, that_id, this_id):
        n2 =3D self.world_data["nodes"].get(str(that_id))
        if not n2 or "neighbors" not in n2:
            return
        for nb in n2["neighbors"]:
            if nb.get("id") =3D=3D this_id:
                nb["id"] =3D None
                nb["border"] =3D None
                break

    def sync_neighbor(self, this_node_id, index):
        pass

    # Karta
    def show_map_mode_buttons(self):
        for widget in self.map_button_frame.winfo_children():
            if widget.cget("text") not in ("Visa Karta",):
                widget.destroy()
        tk.Button(self.map_button_frame, text=3D"Statisk",
command=3Dself.show_static_map_view).pack(side=3Dtk.LEFT, padx=3D2)
        tk.Button(self.map_button_frame, text=3D"Dynamisk",
command=3Dself.open_dynamic_map_view).pack(side=3Dtk.LEFT, padx=3D2)

    def show_static_map_view(self):
        for widget in self.right_frame.winfo_children():
            widget.destroy()
        map_fr =3D tk.Frame(self.right_frame, bg=3D"white")
        map_fr.pack(fill=3D"both", expand=3DTrue)
        map_fr.grid_rowconfigure(0, weight=3D1)
        map_fr.grid_columnconfigure(0, weight=3D1)
        self.static_map_canvas =3D tk.Canvas(map_fr, bg=3D"white",
scrollregion=3D(0,0,3000,2000))
        self.static_map_canvas.grid(row=3D0, column=3D0, sticky=3D"nsew")
        xsc =3D tk.Scrollbar(map_fr, orient=3D"horizontal",
command=3Dself.static_map_canvas.xview)
        xsc.grid(row=3D1, column=3D0, sticky=3D"ew")
        ysc =3D tk.Scrollbar(map_fr, orient=3D"vertical",
command=3Dself.static_map_canvas.yview)
        ysc.grid(row=3D0, column=3D1, sticky=3D"ns")
        self.static_map_canvas.config(xscrollcommand=3Dxsc.set,
yscrollcommand=3Dysc.set)
        btn_fr =3D tk.Frame(self.right_frame, bg=3D"#f4f4f4")
        btn_fr.pack(fill=3D"x", pady=3D5)
        tk.Button(btn_fr, text=3D"< Tillbaka",
command=3Dself.show_no_world).pack(side=3Dtk.LEFT, padx=3D5)
        self.static_scale =3D 1.0
        self.static_map_canvas.bind("<MouseWheel>", self.on_static_map_zoom=
)
        self.static_map_canvas.bind("<Button-4>", self.on_static_map_zoom)
        self.static_map_canvas.bind("<Button-5>", self.on_static_map_zoom)
        self.place_jarldomes_bfs()
        self.draw_static_hexgrid()
        self.draw_static_border_lines()

    def on_static_map_zoom(self, event):
        if event.delta>0 or event.num=3D=3D4:
            factor=3D1.1
        else:
            factor=3D0.9
        if not hasattr(self, "static_scale"):
            self.static_scale=3D1.0
        self.static_scale*=3Dfactor
        self.static_scale=3Dmax(0.2, min(self.static_scale, 5.0))
        self.static_map_canvas.scale("all",0,0,factor,factor)

    def place_jarldomes_bfs(self):
        self.static_rows=3D30
        self.static_cols=3D30
        jarldomes =3D {}
        for nd in self.world_data["nodes"].values():
            if self.get_depth_of_node(nd["node_id"])=3D=3D3:
                jarldomes[nd["node_id"]]=3Dnd
        adjacency=3D{}
        for jid, nd in jarldomes.items():
            neigh=3D[]
            if "neighbors" in nd:
                for nb in nd["neighbors"]:
                    nbid=3Dnb.get("id")
                    if isinstance(nbid,int) and nbid in jarldomes:
                        neigh.append(nbid)
            adjacency[jid]=3Dneigh
        self.map_static_positions=3D{}
        self.static_grid_occupied=3D[[None]*self.static_cols for _ in
range(self.static_rows)]
        visited=3Dset()
        center_r=3Dself.static_rows//2
        center_c=3Dself.static_cols//2
        r_step=3D0

        def get_hex_neighbors(rr, cc):
            if cc%2=3D=3D0:
                offsets=3D[(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(1,-1)]
            else:
                offsets=3D[(-1,0),(1,0),(0,-1),(0,1),(-1,1),(1,1)]
            res=3D[]
            for dr,dc in offsets:
                rr2=3Drr+dr
                cc2=3Dcc+dc
                if 0<=3Drr2<self.static_rows and 0<=3Dcc2<self.static_cols:
                    res.append((rr2,cc2))
            return res

        def bfs_component(start_jid,sr,sc):
            queue=3Ddeque([start_jid])
            self.map_static_positions[start_jid]=3D(sr,sc)
            self.static_grid_occupied[sr][sc]=3Dstart_jid
            visited.add(start_jid)
            while queue:
                cur=3Dqueue.popleft()
                cr,cc=3Dself.map_static_positions[cur]
                for nb_jid in adjacency[cur]:
                    if nb_jid not in visited:
                        placed=3DFalse
                        for (r2,c2) in get_hex_neighbors(cr,cc):
                            if self.static_grid_occupied[r2][c2] is None:
                                self.static_grid_occupied[r2][c2]=3Dnb_jid
                                self.map_static_positions[nb_jid]=3D(r2,c2)
                                visited.add(nb_jid)
                                queue.append(nb_jid)
                                placed=3DTrue
                                break
                        if not placed:
                            self.add_status_message(f"Kunde ej placera
jarld=C3=B6me {nb_jid} intill {cur}.")

        all_jids=3Dlist(jarldomes.keys())
        for jid in all_jids:
            if jid not in visited:
                base_r=3Dcenter_r+r_step
                base_c=3Dcenter_c+r_step
                if not (0<=3Dbase_r<self.static_rows and
0<=3Dbase_c<self.static_cols):
                    base_r, base_c=3D0,0
                if self.static_grid_occupied[base_r][base_c] is None:
                    bfs_component(jid,base_r,base_c)
                else:
                    done=3DFalse
                    for rr in range(self.static_rows):
                        if done:
                            break
                        for cc in range(self.static_cols):
                            if self.static_grid_occupied[rr][cc] is None:
                                bfs_component(jid,rr,cc)
                                done=3DTrue
                                break
                r_step+=3D1

    def draw_static_hexgrid(self):
        self.static_map_canvas.delete("all")
        hex_size=3D30
        x_off=3D50
        y_off=3D50
        for r in range(self.static_rows):
            for c in range(self.static_cols):
                cx=3Dx_off+c*(hex_size*1.5)
                cy=3Dy_off+r*(hex_size*math.sqrt(3)) +
(hex_size*math.sqrt(3)/2 if c%2 else 0)
                points=3D[]
                for k in range(6):
                    ang_deg=3D60*k+30
                    ang_rad=3Dmath.radians(ang_deg)
                    px=3Dcx+hex_size*math.cos(ang_rad)
                    py=3Dcy+hex_size*math.sin(ang_rad)
                    points.extend([px,py])
                jid=3Dself.static_grid_occupied[r][c]
                if jid is not None:
                    nd=3Dself.world_data["nodes"].get(str(jid))
                    if nd:
                        color_fill=3D"#ccffcc"
                        outline=3D"green"
                        name=3Dnd["name"]
                    else:
                        color_fill=3D"#ffdddd"
                        outline=3D"red"
                        name=3D"??"
                else:
                    color_fill=3D"#dddddd"
                    outline=3D"gray"
                    name=3D""
                poly_id=3Dself.static_map_canvas.create_polygon(points,
fill=3Dcolor_fill, outline=3Doutline, width=3D2)
                if name:
                    text_id=3Dself.static_map_canvas.create_text(cx, cy,
text=3Dname, fill=3D"black")
                    self.static_map_canvas.itemconfig(text_id,
tags=3D(f"hex_{r}_{c}",))
                self.static_map_canvas.itemconfig(poly_id,
tags=3D(f"hex_{r}_{c}",))

    def draw_static_border_lines(self):
        hex_size=3D30
        x_off=3D50
        y_off=3D50
        for r in range(self.static_rows):
            for c in range(self.static_cols):
                jid=3Dself.static_grid_occupied[r][c]
                if jid is None:
                    continue
                nodeA=3Dself.world_data["nodes"].get(str(jid))
                if not nodeA or "neighbors" not in nodeA:
                    continue
                cxA=3Dx_off+c*(hex_size*1.5)
                cyA=3Dy_off+r*(hex_size*math.sqrt(3)) +
(hex_size*math.sqrt(3)/2 if c%2 else 0)
                for nb_info in nodeA["neighbors"]:
                    nbid=3Dnb_info.get("id")
                    if isinstance(nbid,int) and nbid>jid:
                        if hasattr(self,"map_static_positions") and nbid in
self.map_static_positions:
                            rr2, cc2=3Dself.map_static_positions[nbid]
                            cxB=3Dx_off+cc2*(hex_size*1.5)

cyB=3Dy_off+rr2*(hex_size*math.sqrt(3))+(hex_size*math.sqrt(3)/2 if cc2%2
else 0)

color=3DBORDER_COLORS.get(nb_info.get("border","<Ingen>"),"gray")
                            self.static_map_canvas.create_line(cxA, cyA,
cxB, cyB, fill=3Dcolor, width=3D2)

    def on_static_map_zoom(self, event):
        if event.delta>0 or event.num=3D=3D4:
            factor=3D1.1
        else:
            factor=3D0.9
        if not hasattr(self,"static_scale"):
            self.static_scale=3D1.0
        self.static_scale*=3Dfactor
        self.static_scale=3Dmax(0.2, min(self.static_scale,5.0))
        self.static_map_canvas.scale("all",0,0,factor,factor)

    def open_dynamic_map_view(self):
        for widget in self.right_frame.winfo_children():
            widget.destroy()
        if not self.world_data:
            return
        self.dynamic_map=3DDynamicMapCanvas(self.right_frame, self,
self.world_data)
        self.dynamic_map.show()

if __name__=3D=3D"__main__":
    root=3Dtk.Tk()
    app=3DFeodalSimulator(root)
    root.mainloop()
