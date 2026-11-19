#!/usr/bin/env python3
"""
Sailight - Straßenbeleuchtungsverwaltung für Luxemburg
Eine GUI-Anwendung zur Verwaltung der öffentlichen Beleuchtung
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import json
from datetime import datetime


class Database:
    def __init__(self, db_path="sailight.db"):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("CREATE TABLE IF NOT EXISTS streetlights (id INTEGER PRIMARY KEY AUTOINCREMENT, light_id TEXT UNIQUE NOT NULL, location TEXT NOT NULL, street TEXT NOT NULL, city TEXT NOT NULL, postal_code TEXT, latitude REAL, longitude REAL, light_type TEXT DEFAULT 'LED', power_watt INTEGER DEFAULT 100, installation_date TEXT, status TEXT DEFAULT 'active', notes TEXT)")
            cursor.execute("CREATE TABLE IF NOT EXISTS control_commands (id INTEGER PRIMARY KEY AUTOINCREMENT, light_id TEXT NOT NULL, command TEXT NOT NULL, timestamp TEXT NOT NULL, executed_by TEXT, status TEXT DEFAULT 'pending')")
            cursor.execute("CREATE TABLE IF NOT EXISTS maintenance_logs (id INTEGER PRIMARY KEY AUTOINCREMENT, light_id TEXT NOT NULL, maintenance_type TEXT NOT NULL, description TEXT, date TEXT NOT NULL, technician TEXT, cost REAL)")
            cursor.execute("CREATE TABLE IF NOT EXISTS energy_consumption (id INTEGER PRIMARY KEY AUTOINCREMENT, light_id TEXT NOT NULL, date TEXT NOT NULL, consumption_kwh REAL NOT NULL)")
            cursor.execute("CREATE TABLE IF NOT EXISTS schedules (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, description TEXT, start_time TEXT NOT NULL, end_time TEXT NOT NULL, days TEXT NOT NULL, active BOOLEAN DEFAULT 1)")
            cursor.execute("CREATE TABLE IF NOT EXISTS light_schedules (id INTEGER PRIMARY KEY AUTOINCREMENT, light_id TEXT NOT NULL, schedule_id INTEGER NOT NULL)")
            conn.commit()
    
    def add_streetlight(self, data):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO streetlights (light_id, location, street, city, postal_code, latitude, longitude, light_type, power_watt, installation_date, status, notes) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (
                    data.get('light_id'), data.get('location'), data.get('street'), data.get('city'),
                    data.get('postal_code'), data.get('latitude'), data.get('longitude'),
                    data.get('light_type', 'LED'), data.get('power_watt', 100),
                    data.get('installation_date'), data.get('status', 'active'), data.get('notes', '')
                ))
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            return False
    
    def get_all_streetlights(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM streetlights")
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def get_streetlight_by_id(self, light_id):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM streetlights WHERE light_id = ?", (light_id,))
            columns = [col[0] for col in cursor.description]
            row = cursor.fetchone()
            return dict(zip(columns, row)) if row else None
    
    def update_streetlight(self, light_id, data):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE streetlights SET location = ?, street = ?, city = ?, postal_code = ?, latitude = ?, longitude = ?, light_type = ?, power_watt = ?, installation_date = ?, status = ?, notes = ? WHERE light_id = ?", (
                data.get('location'), data.get('street'), data.get('city'), data.get('postal_code'),
                data.get('latitude'), data.get('longitude'), data.get('light_type'), data.get('power_watt'),
                data.get('installation_date'), data.get('status'), data.get('notes'), light_id
            ))
            conn.commit()
            return cursor.rowcount > 0
    
    def delete_streetlight(self, light_id):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM streetlights WHERE light_id = ?", (light_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    def add_control_command(self, light_id, command, executed_by="system"):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO control_commands (light_id, command, timestamp, executed_by, status) VALUES (?, ?, ?, ?, ?)", (light_id, command, datetime.now().isoformat(), executed_by, 'executed'))
            conn.commit()
            return True
    
    def get_control_commands(self, light_id=None, limit=100):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            if light_id:
                cursor.execute("SELECT * FROM control_commands WHERE light_id = ? ORDER BY timestamp DESC LIMIT ?", (light_id, limit))
            else:
                cursor.execute("SELECT * FROM control_commands ORDER BY timestamp DESC LIMIT ?", (limit,))
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def add_maintenance_log(self, data):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO maintenance_logs (light_id, maintenance_type, description, date, technician, cost) VALUES (?, ?, ?, ?, ?, ?)", (
                data.get('light_id'), data.get('maintenance_type'), data.get('description'),
                data.get('date'), data.get('technician'), data.get('cost', 0)
            ))
            conn.commit()
            return True
    
    def get_maintenance_logs(self, light_id=None):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            if light_id:
                cursor.execute("SELECT * FROM maintenance_logs WHERE light_id = ? ORDER BY date DESC", (light_id,))
            else:
                cursor.execute("SELECT * FROM maintenance_logs ORDER BY date DESC")
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def add_energy_consumption(self, light_id, date, consumption):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO energy_consumption (light_id, date, consumption_kwh) VALUES (?, ?, ?)", (light_id, date, consumption))
            conn.commit()
            return True
    
    def get_energy_consumption(self, light_id=None, start_date=None, end_date=None):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM energy_consumption"
            params = []
            conditions = []
            if light_id:
                conditions.append("light_id = ?")
                params.append(light_id)
            if start_date:
                conditions.append("date >= ?")
                params.append(start_date)
            if end_date:
                conditions.append("date <= ?")
                params.append(end_date)
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            query += " ORDER BY date DESC"
            cursor.execute(query, params)
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def add_schedule(self, data):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO schedules (name, description, start_time, end_time, days, active) VALUES (?, ?, ?, ?, ?, ?)", (
                data.get('name'), data.get('description', ''), data.get('start_time'),
                data.get('end_time'), data.get('days', '[]'), data.get('active', True)
            ))
            conn.commit()
            return cursor.lastrowid
    
    def get_schedules(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM schedules")
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def assign_schedule_to_light(self, light_id, schedule_id):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO light_schedules (light_id, schedule_id) VALUES (?, ?)", (light_id, schedule_id))
            conn.commit()
            return True
    
    def get_stats(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM streetlights")
            total_lights = cursor.fetchone()[0]
            cursor.execute("SELECT status, COUNT(*) FROM streetlights GROUP BY status")
            status_counts = {row[0]: row[1] for row in cursor.fetchall()}
            cursor.execute("SELECT light_type, COUNT(*) FROM streetlights GROUP BY light_type")
            type_counts = {row[0]: row[1] for row in cursor.fetchall()}
            cursor.execute("SELECT SUM(consumption_kwh) FROM energy_consumption")
            total_consumption = cursor.fetchone()[0] or 0
            cursor.execute("SELECT COUNT(*) FROM maintenance_logs")
            total_maintenance = cursor.fetchone()[0]
            return {
                'total_lights': total_lights,
                'status_counts': status_counts,
                'type_counts': type_counts,
                'total_consumption_kwh': total_consumption,
                'total_maintenance': total_maintenance
            }


class SailightApp:
    def __init__(self, root):
        self.root = root
        self.db = Database()
        self.current_light_id = None
        
        self.root.title("Sailight - Straßenbeleuchtungsverwaltung Luxemburg")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        self.create_overview_tab()
        self.create_management_tab()
        self.create_control_tab()
        self.create_maintenance_tab()
        self.create_energy_tab()
        self.create_schedules_tab()
        self.create_stats_tab()
        
        self.create_menu()
        
        self.status_var = tk.StringVar()
        self.status_var.set("Bereit")
        self.status_bar = ttk.Label(
            self.main_frame,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.status_bar.pack(fill=tk.X, pady=(5, 0))
        
        self.load_sample_data()
        self.refresh_all_tables()
    
    def create_menu(self):
        menubar = tk.Menu(self.root)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Neue Laterne", command=self.add_streetlight_dialog)
        file_menu.add_command(label="Daten importieren", command=self.import_data)
        file_menu.add_command(label="Daten exportieren", command=self.export_data)
        file_menu.add_separator()
        file_menu.add_command(label="Beenden", command=self.root.quit)
        menubar.add_cascade(label="Datei", menu=file_menu)
        
        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(label="Einstellungen", command=self.show_settings)
        menubar.add_cascade(label="Bearbeiten", menu=edit_menu)
        
        view_menu = tk.Menu(menubar, tearoff=0)
        view_menu.add_command(label="Dashboard aktualisieren", command=self.refresh_all_tables)
        menubar.add_cascade(label="Ansicht", menu=view_menu)
        
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="Über Sailight", command=self.show_about)
        menubar.add_cascade(label="Hilfe", menu=help_menu)
        
        self.root.config(menu=menubar)
    
    def create_overview_tab(self):
        overview_frame = ttk.Frame(self.notebook)
        self.notebook.add(overview_frame, text="Uebersicht")
        
        search_frame = ttk.Frame(overview_frame)
        search_frame.pack(fill=tk.X, pady=5)
        ttk.Label(search_frame, text="Suche:").pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        search_btn = ttk.Button(search_frame, text="Suchen", command=self.search_streetlights)
        search_btn.pack(side=tk.LEFT, padx=5)
        
        filter_frame = ttk.Frame(overview_frame)
        filter_frame.pack(fill=tk.X, pady=5)
        ttk.Label(filter_frame, text="Status:").pack(side=tk.LEFT, padx=5)
        self.status_filter = tk.StringVar(value="alle")
        ttk.Combobox(filter_frame, textvariable=self.status_filter, values=["alle", "active", "inactive", "maintenance"]).pack(side=tk.LEFT, padx=5)
        ttk.Label(filter_frame, text="Typ:").pack(side=tk.LEFT, padx=5)
        self.type_filter = tk.StringVar(value="alle")
        ttk.Combobox(filter_frame, textvariable=self.type_filter, values=["alle", "LED", "Halogen", "Natrium", "Induktion"]).pack(side=tk.LEFT, padx=5)
        filter_btn = ttk.Button(filter_frame, text="Filter anwenden", command=self.apply_filters)
        filter_btn.pack(side=tk.LEFT, padx=5)
        
        tree_frame = ttk.Frame(overview_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        columns = ('ID', 'Standort', 'Strasse', 'Stadt', 'PLZ', 'Typ', 'Leistung', 'Status')
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings')
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, anchor=tk.W)
        self.tree.column('ID', width=80)
        self.tree.column('Standort', width=150)
        self.tree.column('Strasse', width=150)
        self.tree.column('Stadt', width=120)
        self.tree.column('PLZ', width=80)
        self.tree.column('Typ', width=100)
        self.tree.column('Leistung', width=80)
        self.tree.column('Status', width=100)
        self.tree.pack(fill=tk.BOTH, expand=True)
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.bind('<Double-1>', self.on_light_selected)
        
        action_frame = ttk.Frame(overview_frame)
        action_frame.pack(fill=tk.X, pady=5)
        ttk.Button(action_frame, text="Neu", command=self.add_streetlight_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Bearbeiten", command=self.edit_selected_light).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Loeschen", command=self.delete_selected_light).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Aktualisieren", command=self.refresh_overview_table).pack(side=tk.LEFT, padx=5)
    
    def create_management_tab(self):
        management_frame = ttk.Frame(self.notebook)
        self.notebook.add(management_frame, text="Verwaltung")
        form_frame = ttk.LabelFrame(management_frame, text="Laternendaten")
        form_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ttk.Label(form_frame, text="Laternen-ID:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.light_id_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.light_id_var, state='readonly').grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        ttk.Label(form_frame, text="Standort:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        self.location_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.location_var).grid(row=0, column=3, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Strasse:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.street_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.street_var).grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        ttk.Label(form_frame, text="Stadt:").grid(row=1, column=2, sticky=tk.W, padx=5, pady=5)
        self.city_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.city_var).grid(row=1, column=3, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(form_frame, text="PLZ:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.postal_code_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.postal_code_var).grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        ttk.Label(form_frame, text="Installationsdatum:").grid(row=2, column=2, sticky=tk.W, padx=5, pady=5)
        self.installation_date_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.installation_date_var).grid(row=2, column=3, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Breitengrad:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.latitude_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.latitude_var).grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)
        ttk.Label(form_frame, text="Laengengrad:").grid(row=3, column=2, sticky=tk.W, padx=5, pady=5)
        self.longitude_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.longitude_var).grid(row=3, column=3, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Laternentyp:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
        self.light_type_var = tk.StringVar()
        ttk.Combobox(form_frame, textvariable=self.light_type_var, values=['LED', 'Halogen', 'Natrium', 'Induktion', 'Sonstige']).grid(row=4, column=1, sticky=tk.W, padx=5, pady=5)
        ttk.Label(form_frame, text="Leistung (W):").grid(row=4, column=2, sticky=tk.W, padx=5, pady=5)
        self.power_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.power_var).grid(row=4, column=3, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Status:").grid(row=5, column=0, sticky=tk.W, padx=5, pady=5)
        self.status_var_form = tk.StringVar()
        ttk.Combobox(form_frame, textvariable=self.status_var_form, values=['active', 'inactive', 'maintenance', 'defective']).grid(row=5, column=1, sticky=tk.W, padx=5, pady=5)
        ttk.Label(form_frame, text="Notizen:").grid(row=5, column=2, sticky=tk.W, padx=5, pady=5)
        self.notes_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.notes_var).grid(row=5, column=3, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Beschreibung:").grid(row=6, column=0, sticky=tk.NW, padx=5, pady=5)
        self.description_text = tk.Text(form_frame, height=4, width=50)
        self.description_text.grid(row=6, column=1, columnspan=3, sticky=tk.W+tk.E, padx=5, pady=5)
        
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=7, column=0, columnspan=4, pady=10)
        ttk.Button(button_frame, text="Speichern", command=self.save_light_data).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Abbrechen", command=self.clear_light_form).pack(side=tk.LEFT, padx=5)

    def create_control_tab(self):
        control_frame = ttk.Frame(self.notebook)
        self.notebook.add(control_frame, text="Steuerung")
        control_pane = ttk.LabelFrame(control_frame, text="Steuerungszentrum")
        control_pane.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ttk.Label(control_pane, text="Laterne auswaehlen:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.control_light_var = tk.StringVar()
        self.control_light_combo = ttk.Combobox(control_pane, textvariable=self.control_light_var, state='readonly')
        self.control_light_combo.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(control_pane, text="Befehl:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.command_var = tk.StringVar()
        commands = ['EIN', 'AUS', 'DIMMEN 50%', 'DIMMEN 75%', 'BLINKEN', 'TEST']
        ttk.Combobox(control_pane, textvariable=self.command_var, values=commands, state='readonly').grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(control_pane, text="Ausgefuehrt von:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.executed_by_var = tk.StringVar(value="System")
        ttk.Entry(control_pane, textvariable=self.executed_by_var).grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Button(control_pane, text="Befehl ausfuehren", command=self.execute_command).grid(row=3, column=0, columnspan=2, pady=10)
        
        log_frame = ttk.LabelFrame(control_frame, text="Befehlsprotokoll")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        columns = ('Zeitstempel', 'Laterne', 'Befehl', 'Status', 'Ausgefuehrt von')
        self.command_tree = ttk.Treeview(log_frame, columns=columns, show='headings')
        for col in columns:
            self.command_tree.heading(col, text=col)
            self.command_tree.column(col, width=120, anchor=tk.W)
        self.command_tree.column('Zeitstempel', width=180)
        self.command_tree.column('Laterne', width=150)
        self.command_tree.pack(fill=tk.BOTH, expand=True)
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.command_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.command_tree.configure(yscrollcommand=scrollbar.set)
    
    def create_maintenance_tab(self):
        maintenance_frame = ttk.Frame(self.notebook)
        self.notebook.add(maintenance_frame, text="Wartung")
        maintenance_pane = ttk.LabelFrame(maintenance_frame, text="Wartungsmanagement")
        maintenance_pane.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ttk.Label(maintenance_pane, text="Laterne:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.maint_light_var = tk.StringVar()
        self.maint_light_combo = ttk.Combobox(maintenance_pane, textvariable=self.maint_light_var, state='readonly')
        self.maint_light_combo.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(maintenance_pane, text="Wartungstyp:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.maint_type_var = tk.StringVar()
        maint_types = ['Routinepruefung', 'Lampenersatz', 'Elektrische Reparatur', 'Reinigung', 'Software-Update']
        ttk.Combobox(maintenance_pane, textvariable=self.maint_type_var, values=maint_types, state='readonly').grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(maintenance_pane, text="Beschreibung:").grid(row=2, column=0, sticky=tk.NW, padx=5, pady=5)
        self.maint_desc_text = tk.Text(maintenance_pane, height=4, width=50)
        self.maint_desc_text.grid(row=2, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        
        ttk.Label(maintenance_pane, text="Datum:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.maint_date_var = tk.StringVar()
        ttk.Entry(maintenance_pane, textvariable=self.maint_date_var).grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(maintenance_pane, text="Techniker:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
        self.maint_technician_var = tk.StringVar()
        ttk.Entry(maintenance_pane, textvariable=self.maint_technician_var).grid(row=4, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(maintenance_pane, text="Kosten (EUR):").grid(row=5, column=0, sticky=tk.W, padx=5, pady=5)
        self.maint_cost_var = tk.StringVar()
        ttk.Entry(maintenance_pane, textvariable=self.maint_cost_var).grid(row=5, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Button(maintenance_pane, text="Wartungseintrag hinzufuegen", command=self.add_maintenance_entry).grid(row=6, column=0, columnspan=2, pady=10)
        
        log_frame = ttk.LabelFrame(maintenance_frame, text="Wartungsprotokoll")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        columns = ('Datum', 'Laterne', 'Typ', 'Techniker', 'Kosten', 'Beschreibung')
        self.maint_tree = ttk.Treeview(log_frame, columns=columns, show='headings')
        for col in columns:
            self.maint_tree.heading(col, text=col)
            self.maint_tree.column(col, width=120, anchor=tk.W)
        self.maint_tree.column('Beschreibung', width=200)
        self.maint_tree.pack(fill=tk.BOTH, expand=True)
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.maint_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.maint_tree.configure(yscrollcommand=scrollbar.set)
    
    def create_energy_tab(self):
        energy_frame = ttk.Frame(self.notebook)
        self.notebook.add(energy_frame, text="Energie")
        energy_pane = ttk.LabelFrame(energy_frame, text="Energieverbrauch")
        energy_pane.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ttk.Label(energy_pane, text="Laterne:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.energy_light_var = tk.StringVar()
        self.energy_light_combo = ttk.Combobox(energy_pane, textvariable=self.energy_light_var, state='readonly')
        self.energy_light_combo.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(energy_pane, text="Datum (YYYY-MM-DD):").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.energy_date_var = tk.StringVar()
        ttk.Entry(energy_pane, textvariable=self.energy_date_var).grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(energy_pane, text="Verbrauch (kWh):").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.energy_consumption_var = tk.StringVar()
        ttk.Entry(energy_pane, textvariable=self.energy_consumption_var).grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Button(energy_pane, text="Eintrag hinzufuegen", command=self.add_energy_entry).grid(row=3, column=0, columnspan=2, pady=10)
        
        table_frame = ttk.LabelFrame(energy_frame, text="Verbrauchsdaten")
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        columns = ('Datum', 'Laterne', 'Verbrauch (kWh)')
        self.energy_tree = ttk.Treeview(table_frame, columns=columns, show='headings')
        for col in columns:
            self.energy_tree.heading(col, text=col)
            self.energy_tree.column(col, width=120, anchor=tk.W)
        self.energy_tree.pack(fill=tk.BOTH, expand=True)
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.energy_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.energy_tree.configure(yscrollcommand=scrollbar.set)
        
        stats_frame = ttk.LabelFrame(energy_frame, text="Energie-Statistik")
        stats_frame.pack(fill=tk.X, padx=10, pady=10)
        ttk.Label(stats_frame, text="Gesamtverbrauch:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.total_consumption_var = tk.StringVar()
        ttk.Label(stats_frame, textvariable=self.total_consumption_var).grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)

    def create_schedules_tab(self):
        schedules_frame = ttk.Frame(self.notebook)
        self.notebook.add(schedules_frame, text="Zeitplaene")
        schedule_pane = ttk.LabelFrame(schedules_frame, text="Zeitplanverwaltung")
        schedule_pane.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ttk.Label(schedule_pane, text="Name:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.schedule_name_var = tk.StringVar()
        ttk.Entry(schedule_pane, textvariable=self.schedule_name_var).grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(schedule_pane, text="Beschreibung:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.schedule_desc_var = tk.StringVar()
        ttk.Entry(schedule_pane, textvariable=self.schedule_desc_var).grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(schedule_pane, text="Startzeit (HH:MM):").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.schedule_start_var = tk.StringVar()
        ttk.Entry(schedule_pane, textvariable=self.schedule_start_var).grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(schedule_pane, text="Endzeit (HH:MM):").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.schedule_end_var = tk.StringVar()
        ttk.Entry(schedule_pane, textvariable=self.schedule_end_var).grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(schedule_pane, text="Tage:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
        days_frame = ttk.Frame(schedule_pane)
        days_frame.grid(row=4, column=1, sticky=tk.W, padx=5, pady=5)
        self.day_vars = {}
        days = ['Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa', 'So']
        for i, day in enumerate(days):
            var = tk.BooleanVar()
            self.day_vars[day] = var
            ttk.Checkbutton(days_frame, text=day, variable=var).grid(row=0, column=i, sticky=tk.W)
        
        ttk.Label(schedule_pane, text="Aktiv:").grid(row=5, column=0, sticky=tk.W, padx=5, pady=5)
        self.schedule_active_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(schedule_pane, variable=self.schedule_active_var).grid(row=5, column=1, sticky=tk.W, padx=5, pady=5)
        
        button_frame = ttk.Frame(schedule_pane)
        button_frame.grid(row=6, column=0, columnspan=2, pady=10)
        ttk.Button(button_frame, text="Zeitplan hinzufuegen", command=self.add_schedule).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Zeitplan zuweisen", command=self.assign_schedule_dialog).pack(side=tk.LEFT, padx=5)
        
        table_frame = ttk.LabelFrame(schedules_frame, text="Zeitplaene")
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        columns = ('ID', 'Name', 'Beschreibung', 'Start', 'Ende', 'Tage', 'Aktiv')
        self.schedule_tree = ttk.Treeview(table_frame, columns=columns, show='headings')
        for col in columns:
            self.schedule_tree.heading(col, text=col)
            self.schedule_tree.column(col, width=100, anchor=tk.W)
        self.schedule_tree.column('Beschreibung', width=200)
        self.schedule_tree.pack(fill=tk.BOTH, expand=True)
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.schedule_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.schedule_tree.configure(yscrollcommand=scrollbar.set)
    
    def create_stats_tab(self):
        stats_frame = ttk.Frame(self.notebook)
        self.notebook.add(stats_frame, text="Statistik")
        stats_pane = ttk.LabelFrame(stats_frame, text="Statistiken")
        stats_pane.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        overview_frame = ttk.LabelFrame(stats_pane, text="Uebersicht")
        overview_frame.pack(fill=tk.X, pady=5)
        ttk.Label(overview_frame, text="Gesamtzahl Laternen:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.stats_total_lights_var = tk.StringVar()
        ttk.Label(overview_frame, textvariable=self.stats_total_lights_var).grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        ttk.Label(overview_frame, text="Aktive Laternen:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        self.stats_active_lights_var = tk.StringVar()
        ttk.Label(overview_frame, textvariable=self.stats_active_lights_var).grid(row=0, column=3, sticky=tk.W, padx=5, pady=5)
        ttk.Label(overview_frame, text="Gesamtverbrauch (kWh):").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.stats_consumption_var = tk.StringVar()
        ttk.Label(overview_frame, textvariable=self.stats_consumption_var).grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        ttk.Label(overview_frame, text="Wartungseingriffe:").grid(row=1, column=2, sticky=tk.W, padx=5, pady=5)
        self.stats_maintenance_var = tk.StringVar()
        ttk.Label(overview_frame, textvariable=self.stats_maintenance_var).grid(row=1, column=3, sticky=tk.W, padx=5, pady=5)
        
        chart_frame = ttk.LabelFrame(stats_pane, text="Verteilung nach Typ")
        chart_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        self.type_distribution_text = tk.Text(chart_frame, height=10)
        self.type_distribution_text.pack(fill=tk.BOTH, expand=True)
        
        status_frame = ttk.LabelFrame(stats_pane, text="Statusverteilung")
        status_frame.pack(fill=tk.X, pady=5)
        self.status_distribution_text = tk.Text(status_frame, height=5)
        self.status_distribution_text.pack(fill=tk.BOTH, expand=True)

    def load_sample_data(self):
        lights = self.db.get_all_streetlights()
        if len(lights) > 0:
            return
        
        sample_lights = [
            {'light_id': 'LUX-001', 'location': 'Place dArmes', 'street': 'Place dArmes', 'city': 'Luxemburg-Stadt', 'postal_code': 'L-1136', 'latitude': 49.6083, 'longitude': 6.1317, 'light_type': 'LED', 'power_watt': 120, 'installation_date': '2020-01-15', 'status': 'active', 'notes': 'Zentrale Platzbeleuchtung'},
            {'light_id': 'LUX-002', 'location': 'Avenue de la Liberte', 'street': 'Avenue de la Liberte', 'city': 'Luxemburg-Stadt', 'postal_code': 'L-1930', 'latitude': 49.6150, 'longitude': 6.1300, 'light_type': 'LED', 'power_watt': 150, 'installation_date': '2019-11-20', 'status': 'active', 'notes': 'Hauptverkehrsstrasse'},
            {'light_id': 'LUX-003', 'location': 'Rue de la Reine', 'street': 'Rue de la Reine', 'city': 'Esch-sur-Alzette', 'postal_code': 'L-4010', 'latitude': 49.5000, 'longitude': 5.9833, 'light_type': 'Natrium', 'power_watt': 200, 'installation_date': '2018-05-10', 'status': 'active', 'notes': 'Industriegebiet'},
            {'light_id': 'LUX-004', 'location': 'Grand Rue', 'street': 'Grand Rue', 'city': 'Differdange', 'postal_code': 'L-4530', 'latitude': 49.5250, 'longitude': 5.8833, 'light_type': 'LED', 'power_watt': 100, 'installation_date': '2021-03-01', 'status': 'maintenance', 'notes': 'Wartung erforderlich'},
            {'light_id': 'LUX-005', 'location': 'Rue du Marche', 'street': 'Rue du Marche', 'city': 'Ettelbrueck', 'postal_code': 'L-9050', 'latitude': 49.8500, 'longitude': 6.0500, 'light_type': 'Halogen', 'power_watt': 180, 'installation_date': '2017-09-15', 'status': 'inactive', 'notes': 'Temporaer deaktiviert'},
        ]
        
        for light in sample_lights:
            self.db.add_streetlight(light)
        
        sample_maintenance = [
            {'light_id': 'LUX-001', 'maintenance_type': 'Routinepruefung', 'description': 'Jaehrliche Inspektion durchgefuehrt', 'date': '2023-01-10', 'technician': 'Jean Mueller', 'cost': 150.0},
            {'light_id': 'LUX-003', 'maintenance_type': 'Lampenersatz', 'description': 'Natriumlampe ersetzt', 'date': '2023-02-15', 'technician': 'Pierre Schmidt', 'cost': 250.0},
        ]
        for maint in sample_maintenance:
            self.db.add_maintenance_log(maint)
        
        sample_energy = [
            ('LUX-001', '2023-01-01', 36.0),
            ('LUX-001', '2023-02-01', 34.5),
            ('LUX-002', '2023-01-01', 45.0),
            ('LUX-002', '2023-02-01', 43.2),
            ('LUX-003', '2023-01-01', 60.0),
        ]
        for light_id, date, consumption in sample_energy:
            self.db.add_energy_consumption(light_id, date, consumption)
        
        sample_schedules = [
            {'name': 'Standard', 'description': 'Standard-Beleuchtungszeitplan', 'start_time': '18:00', 'end_time': '06:00', 'days': json.dumps(['Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa', 'So']), 'active': True},
            {'name': 'Wochenende', 'description': 'Wochenend-Beleuchtung', 'start_time': '17:00', 'end_time': '07:00', 'days': json.dumps(['Sa', 'So']), 'active': True},
        ]
        for schedule in sample_schedules:
            schedule_id = self.db.add_schedule(schedule)
            for light_id in ['LUX-001', 'LUX-002']:
                self.db.assign_schedule_to_light(light_id, schedule_id)
        
        sample_commands = [
            ('LUX-001', 'EIN', 'System'),
            ('LUX-002', 'EIN', 'System'),
            ('LUX-003', 'EIN', 'System'),
        ]
        for light_id, command, executed_by in sample_commands:
            self.db.add_control_command(light_id, command, executed_by)
    
    def refresh_all_tables(self):
        self.refresh_overview_table()
        self.refresh_control_combo()
        self.refresh_maintenance_combo()
        self.refresh_energy_combo()
        self.refresh_command_log()
        self.refresh_maintenance_log()
        self.refresh_energy_table()
        self.refresh_schedules_table()
        self.refresh_stats()
    
    def refresh_overview_table(self):
        status_filter = self.status_filter.get()
        type_filter = self.type_filter.get()
        search_text = self.search_var.get().lower()
        lights = self.db.get_all_streetlights()
        filtered_lights = []
        for light in lights:
            if status_filter != 'alle' and light.get('status') != status_filter:
                continue
            if type_filter != 'alle' and light.get('light_type') != type_filter:
                continue
            if search_text:
                search_fields = [light.get('light_id', ''), light.get('location', ''), light.get('street', ''), light.get('city', ''), light.get('postal_code', '')]
                if not any(search_text in str(field).lower() for field in search_fields):
                    continue
            filtered_lights.append(light)
        for item in self.tree.get_children():
            self.tree.delete(item)
        for light in filtered_lights:
            self.tree.insert('', 'end', values=(light.get('light_id'), light.get('location'), light.get('street'), light.get('city'), light.get('postal_code'), light.get('light_type'), light.get('power_watt'), light.get('status')))
    
    def refresh_control_combo(self):
        lights = self.db.get_all_streetlights()
        light_ids = [light.get('light_id') for light in lights]
        self.control_light_combo['values'] = light_ids
        if light_ids:
            self.control_light_combo.current(0)
    
    def refresh_maintenance_combo(self):
        lights = self.db.get_all_streetlights()
        light_ids = [light.get('light_id') for light in lights]
        self.maint_light_combo['values'] = light_ids
        if light_ids:
            self.maint_light_combo.current(0)
    
    def refresh_energy_combo(self):
        lights = self.db.get_all_streetlights()
        light_ids = [light.get('light_id') for light in lights]
        self.energy_light_combo['values'] = light_ids
        if light_ids:
            self.energy_light_combo.current(0)

    def refresh_command_log(self):
        commands = self.db.get_control_commands(limit=50)
        for item in self.command_tree.get_children():
            self.command_tree.delete(item)
        for cmd in commands:
            self.command_tree.insert('', 'end', values=(cmd.get('timestamp'), cmd.get('light_id'), cmd.get('command'), cmd.get('status'), cmd.get('executed_by')))
    
    def refresh_maintenance_log(self):
        logs = self.db.get_maintenance_logs()
        for item in self.maint_tree.get_children():
            self.maint_tree.delete(item)
        for log in logs:
            self.maint_tree.insert('', 'end', values=(log.get('date'), log.get('light_id'), log.get('maintenance_type'), log.get('technician'), f"{log.get('cost', 0):.2f} EUR", log.get('description', '')[:50]))
    
    def refresh_energy_table(self):
        consumptions = self.db.get_energy_consumption()
        for item in self.energy_tree.get_children():
            self.energy_tree.delete(item)
        for cons in consumptions:
            self.energy_tree.insert('', 'end', values=(cons.get('date'), cons.get('light_id'), f"{cons.get('consumption_kwh', 0):.2f}"))
        total = sum(cons.get('consumption_kwh', 0) for cons in consumptions)
        self.total_consumption_var.set(f"{total:.2f} kWh")
    
    def refresh_schedules_table(self):
        schedules = self.db.get_schedules()
        for item in self.schedule_tree.get_children():
            self.schedule_tree.delete(item)
        for schedule in schedules:
            days = json.loads(schedule.get('days', '[]'))
            days_str = ', '.join(days)
            self.schedule_tree.insert('', 'end', values=(schedule.get('id'), schedule.get('name'), schedule.get('description', ''), schedule.get('start_time'), schedule.get('end_time'), days_str, 'Ja' if schedule.get('active') else 'Nein'))
    
    def refresh_stats(self):
        stats = self.db.get_stats()
        self.stats_total_lights_var.set(str(stats.get('total_lights', 0)))
        self.stats_active_lights_var.set(str(stats.get('status_counts', {}).get('active', 0)))
        self.stats_consumption_var.set(f"{stats.get('total_consumption_kwh', 0):.2f} kWh")
        self.stats_maintenance_var.set(str(stats.get('total_maintenance', 0)))
        type_counts = stats.get('type_counts', {})
        type_text = "Verteilung nach Laternentyp:\n"
        for light_type, count in type_counts.items():
            percentage = (count / stats.get('total_lights', 1)) * 100
            type_text += f"  {light_type}: {count} ({percentage:.1f}%)\n"
        self.type_distribution_text.delete(1.0, tk.END)
        self.type_distribution_text.insert(tk.END, type_text)
        status_counts = stats.get('status_counts', {})
        status_text = "Verteilung nach Status:\n"
        for status, count in status_counts.items():
            percentage = (count / stats.get('total_lights', 1)) * 100
            status_text += f"  {status}: {count} ({percentage:.1f}%)\n"
        self.status_distribution_text.delete(1.0, tk.END)
        self.status_distribution_text.insert(tk.END, status_text)
    
    def on_light_selected(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        item = self.tree.item(selected[0])
        light_id = item['values'][0]
        light = self.db.get_streetlight_by_id(light_id)
        if light:
            self.current_light_id = light_id
            self.fill_light_form(light)
            self.status_var.set(f"Laterne {light_id} ausgewaehlt")
    
    def fill_light_form(self, light):
        self.light_id_var.set(light.get('light_id', ''))
        self.location_var.set(light.get('location', ''))
        self.street_var.set(light.get('street', ''))
        self.city_var.set(light.get('city', ''))
        self.postal_code_var.set(light.get('postal_code', ''))
        self.latitude_var.set(str(light.get('latitude', '')))
        self.longitude_var.set(str(light.get('longitude', '')))
        self.light_type_var.set(light.get('light_type', ''))
        self.power_var.set(str(light.get('power_watt', '')))
        self.installation_date_var.set(light.get('installation_date', ''))
        self.status_var_form.set(light.get('status', ''))
        self.notes_var.set(light.get('notes', ''))
        self.description_text.delete(1.0, tk.END)
        self.description_text.insert(tk.END, light.get('notes', ''))
    
    def clear_light_form(self):
        self.light_id_var.set('')
        self.location_var.set('')
        self.street_var.set('')
        self.city_var.set('')
        self.postal_code_var.set('')
        self.latitude_var.set('')
        self.longitude_var.set('')
        self.light_type_var.set('LED')
        self.power_var.set('100')
        self.installation_date_var.set('')
        self.status_var_form.set('active')
        self.notes_var.set('')
        self.description_text.delete(1.0, tk.END)
        self.current_light_id = None

    def add_streetlight_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Neue Strassenlaterne hinzufuegen")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Laternen-ID:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        light_id_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=light_id_var).grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        ttk.Label(dialog, text="Standort:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        location_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=location_var).grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        ttk.Label(dialog, text="Strasse:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        street_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=street_var).grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        ttk.Label(dialog, text="Stadt:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        city_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=city_var).grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)
        ttk.Label(dialog, text="PLZ:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
        postal_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=postal_var).grid(row=4, column=1, sticky=tk.W, padx=5, pady=5)
        ttk.Label(dialog, text="Typ:").grid(row=5, column=0, sticky=tk.W, padx=5, pady=5)
        type_var = tk.StringVar(value='LED')
        ttk.Combobox(dialog, textvariable=type_var, values=['LED', 'Halogen', 'Natrium', 'Induktion']).grid(row=5, column=1, sticky=tk.W, padx=5, pady=5)
        ttk.Label(dialog, text="Leistung (W):").grid(row=6, column=0, sticky=tk.W, padx=5, pady=5)
        power_var = tk.StringVar(value='100')
        ttk.Entry(dialog, textvariable=power_var).grid(row=6, column=1, sticky=tk.W, padx=5, pady=5)
        
        def save_and_close():
            light_data = {
                'light_id': light_id_var.get(),
                'location': location_var.get(),
                'street': street_var.get(),
                'city': city_var.get(),
                'postal_code': postal_var.get(),
                'light_type': type_var.get(),
                'power_watt': int(power_var.get() or 100),
                'status': 'active',
                'installation_date': datetime.now().strftime('%Y-%m-%d')
            }
            if self.db.add_streetlight(light_data):
                messagebox.showinfo("Erfolg", "Laterne erfolgreich hinzugefuegt!")
                self.refresh_overview_table()
                self.refresh_control_combo()
                self.refresh_maintenance_combo()
                self.refresh_energy_combo()
                dialog.destroy()
            else:
                messagebox.showerror("Fehler", "Laternen-ID existiert bereits!")
        
        ttk.Button(dialog, text="Speichern", command=save_and_close).grid(row=7, column=0, pady=10, padx=5)
        ttk.Button(dialog, text="Abbrechen", command=dialog.destroy).grid(row=7, column=1, pady=10, padx=5)
    
    def edit_selected_light(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warnung", "Bitte waehlen Sie eine Laterne aus!")
            return
        item = self.tree.item(selected[0])
        light_id = item['values'][0]
        light = self.db.get_streetlight_by_id(light_id)
        if light:
            self.fill_light_form(light)
            self.current_light_id = light_id
            self.status_var.set(f"Bearbeite Laterne {light_id}")
    
    def save_light_data(self):
        if not self.current_light_id:
            messagebox.showwarning("Warnung", "Keine Laterne ausgewaehlt!")
            return
        light_data = {
            'location': self.location_var.get(),
            'street': self.street_var.get(),
            'city': self.city_var.get(),
            'postal_code': self.postal_code_var.get(),
            'latitude': float(self.latitude_var.get() or 0),
            'longitude': float(self.longitude_var.get() or 0),
            'light_type': self.light_type_var.get(),
            'power_watt': int(self.power_var.get() or 100),
            'installation_date': self.installation_date_var.get(),
            'status': self.status_var_form.get(),
            'notes': self.notes_var.get()
        }
        if self.db.update_streetlight(self.current_light_id, light_data):
            messagebox.showinfo("Erfolg", "Laterne erfolgreich aktualisiert!")
            self.refresh_overview_table()
            self.status_var.set(f"Laterne {self.current_light_id} aktualisiert")
        else:
            messagebox.showerror("Fehler", "Laterne konnte nicht aktualisiert werden!")
    
    def delete_selected_light(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warnung", "Bitte waehlen Sie eine Laterne aus!")
            return
        item = self.tree.item(selected[0])
        light_id = item['values'][0]
        if messagebox.askyesno("Bestaetigung", f"Moechten Sie die Laterne {light_id} wirklich loeschen?"):
            if self.db.delete_streetlight(light_id):
                messagebox.showinfo("Erfolg", "Laterne erfolgreich geloescht!")
                self.refresh_overview_table()
                self.clear_light_form()
                self.status_var.set(f"Laterne {light_id} geloescht")
            else:
                messagebox.showerror("Fehler", "Laterne konnte nicht geloescht werden!")
    
    def search_streetlights(self):
        self.refresh_overview_table()
    
    def apply_filters(self):
        self.refresh_overview_table()
    
    def execute_command(self):
        light_id = self.control_light_var.get()
        command = self.command_var.get()
        executed_by = self.executed_by_var.get()
        if not light_id or not command:
            messagebox.showwarning("Warnung", "Bitte waehlen Sie eine Laterne und einen Befehl aus!")
            return
        if self.db.add_control_command(light_id, command, executed_by):
            messagebox.showinfo("Erfolg", f"Befehl '{command}' fuer Laterne {light_id} ausgefuehrt!")
            self.refresh_command_log()
            self.status_var.set(f"Befehl '{command}' fuer {light_id} ausgefuehrt")

    def add_maintenance_entry(self):
        light_id = self.maint_light_var.get()
        maint_type = self.maint_type_var.get()
        description = self.maint_desc_text.get(1.0, tk.END).strip()
        date = self.maint_date_var.get()
        technician = self.maint_technician_var.get()
        if not light_id or not maint_type or not date:
            messagebox.showwarning("Warnung", "Bitte fuellen Sie alle Pflichtfelder aus!")
            return
        try:
            cost = float(self.maint_cost_var.get() or 0)
        except ValueError:
            cost = 0
        maint_data = {'light_id': light_id, 'maintenance_type': maint_type, 'description': description, 'date': date, 'technician': technician, 'cost': cost}
        if self.db.add_maintenance_log(maint_data):
            messagebox.showinfo("Erfolg", "Wartungseintrag erfolgreich hinzugefuegt!")
            self.refresh_maintenance_log()
            self.maint_desc_text.delete(1.0, tk.END)
            self.maint_date_var.set('')
            self.maint_technician_var.set('')
            self.maint_cost_var.set('')
            self.status_var.set(f"Wartungseintrag fuer {light_id} hinzugefuegt")
    
    def add_energy_entry(self):
        light_id = self.energy_light_var.get()
        date = self.energy_date_var.get()
        consumption = self.energy_consumption_var.get()
        if not light_id or not date or not consumption:
            messagebox.showwarning("Warnung", "Bitte fuellen Sie alle Pflichtfelder aus!")
            return
        try:
            consumption = float(consumption)
        except ValueError:
            messagebox.showerror("Fehler", "Verbrauch muss eine Zahl sein!")
            return
        if self.db.add_energy_consumption(light_id, date, consumption):
            messagebox.showinfo("Erfolg", "Energieverbrauchseintrag erfolgreich hinzugefuegt!")
            self.refresh_energy_table()
            self.energy_date_var.set('')
            self.energy_consumption_var.set('')
            self.status_var.set(f"Energieverbrauch fuer {light_id} hinzugefuegt")
    
    def add_schedule(self):
        name = self.schedule_name_var.get()
        description = self.schedule_desc_var.get()
        start_time = self.schedule_start_var.get()
        end_time = self.schedule_end_var.get()
        active = self.schedule_active_var.get()
        if not name or not start_time or not end_time:
            messagebox.showwarning("Warnung", "Bitte fuellen Sie alle Pflichtfelder aus!")
            return
        selected_days = []
        for day, var in self.day_vars.items():
            if var.get():
                selected_days.append(day)
        schedule_data = {'name': name, 'description': description, 'start_time': start_time, 'end_time': end_time, 'days': json.dumps(selected_days), 'active': active}
        schedule_id = self.db.add_schedule(schedule_data)
        if schedule_id:
            messagebox.showinfo("Erfolg", "Zeitplan erfolgreich hinzugefuegt!")
            self.refresh_schedules_table()
            self.schedule_name_var.set('')
            self.schedule_desc_var.set('')
            self.schedule_start_var.set('')
            self.schedule_end_var.set('')
            self.status_var.set(f"Zeitplan '{name}' hinzugefuegt")
    
    def assign_schedule_dialog(self):
        schedules = self.db.get_schedules()
        if not schedules:
            messagebox.showwarning("Warnung", "Es gibt keine Zeitplaene!")
            return
        lights = self.db.get_all_streetlights()
        if not lights:
            messagebox.showwarning("Warnung", "Es gibt keine Laternen!")
            return
        dialog = tk.Toplevel(self.root)
        dialog.title("Zeitplan zuweisen")
        dialog.geometry("400x200")
        dialog.transient(self.root)
        dialog.grab_set()
        ttk.Label(dialog, text="Laterne:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        light_var = tk.StringVar()
        ttk.Combobox(dialog, textvariable=light_var, values=[light.get('light_id') for light in lights], state='readonly').grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        ttk.Label(dialog, text="Zeitplan:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        schedule_var = tk.StringVar()
        ttk.Combobox(dialog, textvariable=schedule_var, values=[f"{s.get('id')} - {s.get('name')}" for s in schedules], state='readonly').grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        def assign():
            light_id = light_var.get()
            schedule_str = schedule_var.get()
            if not light_id or not schedule_str:
                messagebox.showwarning("Warnung", "Bitte waehlen Sie Laterne und Zeitplan aus!")
                return
            schedule_id = int(schedule_str.split(' - ')[0])
            if self.db.assign_schedule_to_light(light_id, schedule_id):
                messagebox.showinfo("Erfolg", "Zeitplan erfolgreich zugewiesen!")
                dialog.destroy()
        ttk.Button(dialog, text="Zuweisen", command=assign).grid(row=2, column=0, pady=10, padx=5)
        ttk.Button(dialog, text="Abbrechen", command=dialog.destroy).grid(row=2, column=1, pady=10, padx=5)
    
    def import_data(self):
        file_path = filedialog.askopenfilename(title="Daten importieren", filetypes=[("JSON-Dateien", "*.json"), ("Alle Dateien", "*.*")])
        if not file_path:
            return
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if 'streetlights' in data:
                for light in data['streetlights']:
                    self.db.add_streetlight(light)
                messagebox.showinfo("Erfolg", f"{len(data['streetlights'])} Laternen importiert!")
            if 'maintenance_logs' in data:
                for log in data['maintenance_logs']:
                    self.db.add_maintenance_log(log)
                messagebox.showinfo("Erfolg", f"{len(data['maintenance_logs'])} Wartungseingriffe importiert!")
            if 'energy_consumption' in data:
                for cons in data['energy_consumption']:
                    self.db.add_energy_consumption(cons.get('light_id'), cons.get('date'), cons.get('consumption_kwh'))
                messagebox.showinfo("Erfolg", f"{len(data['energy_consumption'])} Energieverbrauchseingriffe importiert!")
            self.refresh_all_tables()
            self.status_var.set("Daten importiert")
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Import: {str(e)}")
    
    def export_data(self):
        file_path = filedialog.asksaveasfilename(title="Daten exportieren", defaultextension=".json", filetypes=[("JSON-Dateien", "*.json"), ("Alle Dateien", "*.*")])
        if not file_path:
            return
        try:
            data = {
                'streetlights': self.db.get_all_streetlights(),
                'maintenance_logs': self.db.get_maintenance_logs(),
                'energy_consumption': self.db.get_energy_consumption(),
                'control_commands': self.db.get_control_commands(),
                'schedules': self.db.get_schedules()
            }
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            messagebox.showinfo("Erfolg", "Daten erfolgreich exportiert!")
            self.status_var.set(f"Daten nach {file_path} exportiert")
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Export: {str(e)}")
    
    def show_settings(self):
        messagebox.showinfo("Einstellungen", "Einstellungen-Fenster wird implementiert.")
    
    def show_about(self):
        about_text = "Sailight - Strassenbeleuchtungsverwaltung Luxemburg\n\nVersion: 1.0.0\n\nEine Anwendung zur Verwaltung der oeffentlichen Beleuchtung in Luxemburg."
        messagebox.showinfo("Ueber Sailight", about_text)


def main():
    root = tk.Tk()
    app = SailightApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
