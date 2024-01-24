import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
from datetime import datetime, timedelta
from tkcalendar import Calendar, DateEntry
import mysql.connector

config = {
    'user': "root",
    'password': "",
    'host': "localhost",
    'database': 'PyDo'
}

mydb = mysql.connector.connect(
    host=config['host'],
    user=config['user'],
    password=config['password'],
    database=config['database']
)

mycursor = mydb.cursor(dictionary=True)
selected_item = None
manual_selection = False
demarrage_presse = False

fenetre = tk.Tk()
fenetre.title('PyDo')
fenetre.minsize(900, 200)
fenetre.geometry('900x200')

tree_frame = ttk.Frame(fenetre)
tree_frame.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.BOTH, expand=True)

columns = ('Liste des tâches', 'Date création', 'Date fixée', 'Temps restant', 'Statut','Date réalisation','ID')

tree = ttk.Treeview(tree_frame, columns=columns, show='headings')


tree.heading("Liste des tâches", text="Liste des tâches", command=lambda col='#1': on_column_click(col))
tree.heading("Date création", text="Date création", command=lambda col='#2': on_column_click(col))
tree.heading("Date fixée", text="Date fixée", command=lambda col='#3': on_column_click(col))
tree.heading('Temps restant', text="Temps restant", command=lambda col='#4': on_column_click(col))
tree.heading("Statut", text="Statut", command=lambda col='#5': on_column_click(col))
tree.heading("Date réalisation", text="Date réalisation", command=lambda col='#6': on_column_click(col))

tree.column('Liste des tâches', minwidth=250, anchor="center",stretch=True)
tree.column('Date création', width=20, minwidth=100, anchor="center",stretch=True)
tree.column('Date fixée', width=20, minwidth=100, anchor="center",stretch=True)
tree.column('Temps restant', width=20, minwidth=100, anchor="center",stretch=True)
tree.column('Statut', width=20, minwidth=100, anchor="center", stretch=True)
tree.column("Date réalisation", width=20, minwidth=100, anchor="center", stretch=True)

tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

def apply_background_color(task_status):

    if task_status == 'A faire':
        return '#d4e6f1'
    elif task_status == 'En cours':
        return '#f9e79f'
    elif task_status == 'Terminée':
        return '#abebc6'
    elif task_status == 'Échouée':
        return '#f2d7d5'

def calculate_time_remaining(chosen_date, chosen_time):
    current_datetime = datetime.now()
    chosen_datetime = datetime.strptime(f"{chosen_date} {chosen_time}", "%d-%m-%Y %H:%M")

    time_difference = chosen_datetime - current_datetime
    days, seconds = time_difference.days, time_difference.seconds
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    remaining_time = "".format(days, hours, minutes)

    return remaining_time

def get_tasks_from_database():
    query = "SELECT * FROM tache"
    mycursor.execute(query)
    tasks = mycursor.fetchall()

    for task in tasks:
        task_id = task['id_tache']
        task_name = task['nom_tache']
        creation_date = task['date_creation'].strftime("%d-%m-%Y %H:%M")
        date_fixee = task['date_fixee'].strftime("%d-%m-%Y %H:%M")
        task_status = task['id_etat']
        date_realisation = task['date_realisation'].strftime("%d-%m-%Y %H:%M") if task['date_realisation'] else ''

        task_status_text = value_to_text(task_status)
        date_fixee_parts = date_fixee.split(" ")
        remaining_time = calculate_time_remaining(date_fixee_parts[0], date_fixee_parts[1])

        tree.insert('', tk.END, values=(task_name, creation_date, date_fixee, remaining_time, task_status_text, date_realisation, task_id))

    update_background_colors_after_sort()

def update_background_colors_after_sort(event=None):
    tree.after(10, update_background_colors)

def update_background_colors():
    for item in tree.get_children():
        values = tree.item(item, 'values')
        task_status = values[4]
        tree.item(item, tags=(task_status,))
        tree.tag_configure(task_status, background=apply_background_color(task_status))

def value_to_text(etat_numerique):
    if etat_numerique == 1:
        return 'A faire'
    elif etat_numerique == 2:
        return 'En cours'
    elif etat_numerique == 3:
        return 'Terminée'
    elif etat_numerique == 4:
        return 'Échouée'

get_tasks_from_database()

class MultilineEntryDialog(simpledialog.Dialog):
    
    def __init__(self, parent, title, prompt, max_length=50):
        self.max_length = max_length
        super().__init__(parent, title)

    def buttonbox(self):
        box = ttk.Frame(self)

        w = ttk.Button(box, text="OK", width=10, command=self.ok, default=tk.ACTIVE)
        w.pack(side="left", padx=5, pady=5)
        w = ttk.Button(box, text="Annuler", width=10, command=self.cancel)
        w.pack(side="left", padx=5, pady=5)

        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)

        box.pack()

    def body(self, master):
        tk.Label(master, text="Nouvelle tâche (max 50 caractères) :").grid(row=0, column=0, padx=10, pady=10)
        self.text_entry = tk.Text(master, height=5, width=40)
        self.text_entry.grid(row=0, column=1, padx=10, pady=10)

        tk.Label(master, text="Choisir une date :").grid(row=1, column=0, padx=10, pady=10)
        self.date_entry = DateEntry(master, width=12, background='darkblue', foreground='white', borderwidth=2)
        self.date_entry.grid(row=1, column=1, padx=10, pady=10, sticky='w')

        tk.Label(master, text="Choisir une heure :").grid(row=2, column=0, padx=10, pady=10)
        self.hour_combobox = ttk.Combobox(master, values=[str(i).zfill(2) for i in range(24)], state="readonly", width=6)
        self.hour_combobox.grid(row=2, column=1, padx=10, pady=10,sticky='w')

        tk.Label(master, text=" : ").grid(row=2, column=1, padx=(80,0), pady=10,sticky='w')

        self.minute_combobox = ttk.Combobox(master, values=[str(i).zfill(2) for i in range(60)], state="readonly", width=6)
        self.minute_combobox.grid(row=2, column=1, padx=105, pady=10,sticky='w')

        current_time = datetime.now().strftime("%H:%M")
        new_time = (datetime.strptime(current_time, "%H:%M") + timedelta(minutes=0)).strftime("%H:%M")

        self.hour_combobox.set(new_time.split(":")[0])
        self.minute_combobox.set(new_time.split(":")[1])
        self.date_entry.set_date(datetime.now().date())
        
        self.wm_minsize(width=580, height=240)
        self.resizable(False, False)

        return self.text_entry

    def apply(self):
        new_task = self.text_entry.get("1.0", "end-1c").strip()
        chosen_date = self.date_entry.get_date().strftime("%d-%m-%Y")
        chosen_hour = self.hour_combobox.get()
        chosen_minute = self.minute_combobox.get()
        
        if len(new_task) > self.max_length:
            messagebox.showwarning("Erreur", "La tâche ne doit pas dépasser 50 caractères.")
            self.result = None
        else:
            self.result = {'task': new_task, 'date': chosen_date, 'time': f"{chosen_hour.zfill(2)}:{chosen_minute.zfill(2)}"}

class ModifyTaskDialog(simpledialog.Dialog):
    
    def __init__(self, parent, title, task, date, time, max_length=50):
        self.task = task
        self.date = date
        self.time = time
        self.max_length = max_length
        super().__init__(parent, title)

    def buttonbox(self):
        box = ttk.Frame(self)

        w = ttk.Button(box, text="OK", width=10, command=self.ok, default=tk.ACTIVE)
        w.pack(side="left", padx=5, pady=5)
        w = ttk.Button(box, text="Annuler", width=10, command=self.cancel)
        w.pack(side="left", padx=5, pady=5)

        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)

        box.pack()

    def show_modify_dialog(self):
        result = self.result
        if result:
            modified_task = result['task']
            chosen_date = result['date']
            chosen_time = result['time']
            return {'task': modified_task, 'date': chosen_date, 'time': chosen_time}
        return None

    def body(self, master):
        tk.Label(master, text="Tâche à modifier (max 50 caractères) :").grid(row=0, column=0, padx=10, pady=10)
        self.text_entry = tk.Text(master, height=5, width=40)
        self.text_entry.insert(tk.END, self.task)
        self.text_entry.grid(row=0, column=1, padx=10, pady=10)

        tk.Label(master, text="Nouvelle Date :").grid(row=1, column=0, padx=10, pady=10)
        self.date_entry = DateEntry(master, width=12, background='darkblue', foreground='white', borderwidth=2)
        old_datetime_obj = datetime.strptime(self.time, "%d-%m-%Y %H:%M")
        new_datetime_obj = old_datetime_obj
        self.date_entry.set_date(new_datetime_obj.date())

        self.date_entry.grid(row=1, column=1, padx=10, pady=10, sticky='w')

        tk.Label(master, text="Nouvelle heure :").grid(row=2, column=0, padx=10, pady=10)

        self.hour_combobox = ttk.Combobox(master, values=[str(i).zfill(2) for i in range(24)], state="readonly", width=6)
        self.hour_combobox.set(new_datetime_obj.strftime("%H"))
        self.hour_combobox.grid(row=2, column=1, padx=10, pady=10,sticky='w')

        tk.Label(master, text=" : ").grid(row=2, column=1, padx=(80,0), pady=10,sticky='w')

        self.minute_combobox = ttk.Combobox(master, values=[str(i).zfill(2) for i in range(60)], state="readonly", width=6)
        self.minute_combobox.set(new_datetime_obj.strftime("%M"))
        self.minute_combobox.grid(row=2, column=1, padx=105, pady=10,sticky='w')

        self.wm_minsize(width=580, height=240)
        self.resizable(False, False)
        
        return self.text_entry

    def apply(self):
        modified_task = self.text_entry.get("1.0", "end-1c").strip()
        chosen_date = self.date_entry.get_date().strftime("%d-%m-%Y")
        chosen_hour = self.hour_combobox.get()
        chosen_minute = self.minute_combobox.get()

        if len(modified_task) > self.max_length:
            messagebox.showwarning("Erreur", "La tâche ne doit pas dépasser 50 caractères.")
            self.result = None
        else:
            self.result = {'task': modified_task, 'date': chosen_date, 'time': f"{chosen_hour.zfill(2)}:{chosen_minute.zfill(2)}"}

def modif_task():
    global selected_item

    selected_item = tree.selection()
    values = tree.item(selected_item, 'values')
    
    if selected_item and values[4] != 'Terminée' and values[4] != 'Échouée':
        dialog = ModifyTaskDialog(fenetre, "Modifier une tâche", values[0], values[1], values[2])
        result = dialog.result
        if result:
            modified_task = result['task']
            chosen_date = result['date']
            chosen_time = result['time']

            try:
                formatted_date_time = datetime.strptime(f"{chosen_date} {chosen_time}", "%d-%m-%Y %H:%M")
            except ValueError:
                messagebox.showwarning("Erreur", "La date et l'heure sélectionnées ne sont pas valides.")
                return

            current_datetime = datetime.now()
            if formatted_date_time <= current_datetime:
                messagebox.showwarning("Erreur", "La date et l'heure sélectionnées sont déjà passées.")
                return
            
            valeur_id_tache = values[-1]
            tree.item(selected_item, values=(modified_task, values[1], formatted_date_time.strftime("%d-%m-%Y %H:%M"), calculate_time_remaining(chosen_date, chosen_time), values[4],values[5],valeur_id_tache))   
            query = "UPDATE tache SET nom_tache = %s, date_fixee = %s WHERE id_tache = %s"
            mycursor.execute(query, (modified_task, formatted_date_time, valeur_id_tache))
            mydb.commit()
            mycursor.reset()

    update_time_remaining_for_in_progress_tasks()
    update_background_colors()

def add_task():
    global demarrage_presse
    demarrage_presse = False
    dialog = MultilineEntryDialog(fenetre, "Ajouter une tâche", "Nouvelle tâche :")
    result = dialog.result

    if result:
        new_task = result['task']
        chosen_date = result['date']
        chosen_time = result['time']

        try:
            formatted_date_time = datetime.strptime(f"{chosen_date} {chosen_time}", "%d-%m-%Y %H:%M")
        except ValueError:
            messagebox.showwarning("Erreur", "La date et l'heure sélectionnées ne sont pas valides.")
            return
        current_datetime = datetime.now()

        if formatted_date_time < current_datetime:
            messagebox.showwarning("Erreur", "La date et l'heure sélectionnées sont déjà passées.")
            return

        query = "INSERT INTO tache (nom_tache, date_creation, date_fixee, id_etat) VALUES (%s, %s, %s, %s)"
        values = (new_task, current_datetime, formatted_date_time, 1)
        mycursor.execute(query, values)
        mydb.commit()
        mycursor.reset()

        mycursor.execute("SELECT id_tache FROM tache ORDER BY id_tache DESC")
        id_tache=mycursor.fetchone()
        valeur_id_tache = id_tache['id_tache']
        mycursor.reset()
        
        tree.insert('', tk.END, values=(new_task, current_datetime.strftime("%d-%m-%Y %H:%M"),formatted_date_time.strftime("%d-%m-%Y %H:%M"),calculate_time_remaining(chosen_date, chosen_time),'A faire', '',valeur_id_tache))
        update_background_colors()
        

def show_calendar():
    cal_dialog = tk.Toplevel(fenetre)
    cal = Calendar(cal_dialog, selectmode="day", year=2022, month=1, day=1)
    cal.pack()

def delete_selected_item():
    selected_item = tree.focus()
    if selected_item:
        values = tree.item(selected_item, 'values')
        valeur_id_tache = values[-1]
        if values:
            confirm = messagebox.askyesno("Suppression de tâche", "Êtes-vous certain de vouloir supprimer cette tâche ?")
            if confirm:
                query_delete = "DELETE FROM tache WHERE id_tache = %s"
                mycursor.execute(query_delete, (valeur_id_tache,))
                mydb.commit()

                tree.delete(selected_item)

                messagebox.showinfo("Suppression réussie", "La tâche a été supprimée avec succès.")



def update_time_remaining(selected_item):
    global demarrage_presse

    if demarrage_presse and selected_item:
        if tree.exists(selected_item):
            values = tree.item(selected_item, 'values')
            valeur_id_tache = values[-1]
            if len(values) >= 4:
                task_time = values[2]
                remaining_time = calculate_time_remaining_from_now(task_time)
                tree.item(selected_item, values=(values[0], values[1], values[2], remaining_time, values[4],'',valeur_id_tache))
                tree.set(selected_item, 'Statut', values[4])

    if demarrage_presse and selected_item == None:
        demarrage_presse = False

    fenetre.after(1000, lambda si=selected_item: update_time_remaining(tree, si))


def calculate_time_remaining_from_now(task_time):
    if not task_time:
        return ''

    task_datetime = datetime.strptime(task_time, "%d-%m-%Y %H:%M")
    current_datetime = datetime.now()

    if current_datetime > task_datetime:
        return ''

    time_difference = task_datetime - current_datetime
    days, seconds = divmod(time_difference.total_seconds(), 24 * 3600)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    days, hours, minutes, seconds = int(days), int(hours), int(minutes), int(seconds)

    if days > 0:
        remaining_time = "{:02} j {:02} h {:02} min".format(days, hours, minutes)
    elif hours > 0:
        remaining_time = "{:02} h {:02} min".format(hours, minutes)
    elif minutes > 0:
        remaining_time = "{:02} min {:02} s".format(minutes, seconds)
    elif minutes < 1:
        remaining_time = "{:02} s".format(seconds)
    else:
        remaining_time = ""

    if days == 0 and hours == 0 and minutes == 0 and seconds == 0:
        remaining_time = ""

    return remaining_time

def start_timer():
    global selected_item
    current_selection = tree.selection()

    if current_selection:
        selected_item = current_selection[0]
    for item in tree.get_children():
        values = tree.item(item, 'values')
        if len(values) >= 3 and values[4] == 'En cours':
            task_time = values[2]
            valeur_id_tache = values[-1]
            remaining_time = calculate_time_remaining_from_now(task_time)
            tree.item(item, values=(values[0], values[1], values[2], remaining_time, 'En cours', '',valeur_id_tache))

    fenetre.after(1000, start_timer)
    update_time_remaining_for_in_progress_tasks()

def update_time_remaining_for_in_progress_tasks():
    current_datetime = datetime.now()

    for item in tree.get_children():
        values = tree.item(item, 'values')
        valeur_id_tache = values[-1]
        if len(values) >= 4 and values[4] == 'En cours':
            task_time = values[2]
            remaining_time = calculate_time_remaining_from_now(task_time)
            
            if remaining_time == "":
                tree.item(item, values=(values[0], values[1], values[2], '', 'Échouée', "",valeur_id_tache))
                update_background_colors()
                query = "UPDATE tache SET id_etat = %s WHERE id_tache = %s"
                mycursor.execute(query, (4, valeur_id_tache))
                mydb.commit()
                mycursor.reset()

        elif len(values) >= 4 and values[4] == 'A faire':
            task_time = values[2]
            task_datetime = datetime.strptime(task_time, "%d-%m-%Y %H:%M")

            if task_datetime <= current_datetime + timedelta(seconds=1):
                tree.item(item, values=(values[0], values[1], values[2], '', 'Échouée', "", valeur_id_tache))
                update_background_colors()
                query = "UPDATE tache SET id_etat = %s WHERE id_tache = %s"
                mycursor.execute(query, (4, valeur_id_tache))
                mydb.commit()
                mycursor.reset() 

    fenetre.after(1000, update_time_remaining_for_in_progress_tasks)
    

column_sort_order = {'#1': 'ascendant', '#2': 'ascendant', '#3': 'ascendant', '#4': 'ascendant', '#5': 'ascendant', '#6': 'ascendant'}

def on_column_click(col):
    global column_sort_order
    current_items = [(item, tree.item(item, 'values')) for item in tree.get_children()]

    if column_sort_order[col] == 'ascendant':
        column_sort_order[col] = 'descendant'
    else:
        column_sort_order[col] = 'ascendant'

    reverse_sort = column_sort_order[col] == 'descendant'
    sorting_key = lambda x: x[1][int(col[-1])-1]

    sorted_items = sorted(current_items, key=sorting_key, reverse=reverse_sort)
    tree.delete(*tree.get_children())

    for item, values in sorted_items:
        tree.insert('', tk.END, values=values)

    update_time_remaining_for_in_progress_tasks()
    start_timer()


def item_selected(event=None):
    global selected_item
    for selected_item in tree.selection():
        tree.item(selected_item)

def update_temps_restant_en_cours(selected_item):
    if tree.exists(selected_item):
        
        values = tree.item(selected_item, 'values')
        valeur_id_tache = values[-1]
        if len(values) >= 3 and values[4] != 'Échouée':
            task_time = values[2]

            if values[4] != 'Terminée':
                remaining_time = calculate_time_remaining_from_now(task_time)

                if remaining_time == "":
                    tree.item(selected_item, values=(values[0], values[1], values[2], '', 'Échouée','',valeur_id_tache)) 
                else:
                    tree.item(selected_item, values=(values[0], values[1], values[2], remaining_time, 'En cours','',valeur_id_tache))

            fenetre.after(1000, lambda si=selected_item: update_temps_restant_en_cours(si))

def demarrer():
    global demarrage_presse

    if not selected_item or not tree.exists(selected_item):
        messagebox.showwarning("Avertissement", "Veuillez sélectionner une tâche avant de démarrer.")
        return
    values = tree.item(selected_item, 'values')

    if values and len(values) >= 5 and values[4] != 'Échouée' or 'Terminée':
        demarrage_presse = not demarrage_presse
        update_temps_restant_en_cours(selected_item)

        valeur_id_tache = values[-1]
        query = "UPDATE tache SET id_etat = %s WHERE id_tache = %s"
        mycursor.execute(query, (2, valeur_id_tache))
        mydb.commit()
        mycursor.reset()
            
def complete_selected_item():
    global demarrage_presse, selected_item
    values = tree.item(selected_item, 'values')

    if values[4] != 'Terminée':
        confirm = messagebox.askyesno("Tâche accomplie ?", "Êtes-vous certain de vouloir terminer cette tâche ?")
        if confirm:
            demarrage_presse = False
            values = list(values)
            values[5] = datetime.now().strftime("%d-%m-%Y %H:%M")

            valeur_id_tache = values[-1]
            tree.item(selected_item, values=(values[0], values[1], values[2], '', 'Terminée',values[5],valeur_id_tache))
            query = "UPDATE tache SET id_etat = %s, date_realisation = NOW() WHERE id_tache = %s"
            mycursor.execute(query, (3, valeur_id_tache))
            mydb.commit()
            mycursor.reset()
                
button_frame = ttk.Frame(fenetre)
button_frame.pack(side=tk.LEFT, padx=10)

button1 = ttk.Button(button_frame, text="Démarrer", command=demarrer)
button1.grid(row=1, column=0, pady=5)

button2 = ttk.Button(button_frame, text="Ajouter", command=add_task)
button2.grid(row=0, column=0, pady=5)

button3 = ttk.Button(button_frame, text="Modifier", command=modif_task)
button3.grid(row=2, column=0, pady=5)

button4 = ttk.Button(button_frame, text="Supprimer", command=delete_selected_item)
button4.grid(row=4, column=0, pady=5)

button5 = ttk.Button(button_frame, text="Terminer", command=complete_selected_item)
button5.grid(row=3, column=0, pady=5)

tree.bind('<<TreeviewSelect>>', item_selected)

scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
tree.configure(yscroll=scrollbar.set)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

selected_item = tree.focus()
if selected_item:
        values = tree.item(selected_item, 'values')
        if values and len(values) >= 4 and values[4] == 'Échouée':
            tree.tag_configure('Échouée', background=apply_background_color('Échouée', values[2]))

fenetre.after(10, update_background_colors_after_sort)

tree.bind("<ButtonRelease-1>", update_background_colors_after_sort)
update_background_colors()
start_timer()
fenetre.mainloop()