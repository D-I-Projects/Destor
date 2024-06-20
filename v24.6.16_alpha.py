import os
import logging
import datetime
import shutil
import requests
import threading
import configparser
import platform
from tkinter import filedialog, messagebox, BOTH, X
import customtkinter as ctk
from PIL import Image, ImageDraw, ImageTk
import pystray
from CTkListbox import *
import psutil
import sys
from pypresence import Presence
import time
import urllib.request
from threading import Thread
import tkinter.font as tkFont
import tkinter as tk
from tkinter import ttk
from pathlib import Path 
import subprocess
import re

RPC = None

current_version = "v24.6.16-alpha"

#Discord Client ID
client_id = "1245459087584661513"

appdata_dir = Path.home() / "AppData" / "Roaming"
directory = appdata_dir / "DT_FILES"
directory.mkdir(parents=True, exist_ok=True)
path = os.path.join(appdata_dir, directory)
print(appdata_dir)
print(path)

try:
    os.mkdir(path)
    print("Created '%s' succesfuly" % directory)
except FileExistsError:
    print("The folder '%s' already exists" % directory)
except PermissionError:
    print("No permissions '%s'" % directory)
except Exception as e:
    print(f"Error: {e}")

#Logger Settings
def log_settings():
    log_dir = os.path.join(directory, "", "Logs")
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    current_datetime = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    log_filename = os.path.join(log_dir, f"Destor{current_datetime}.log")

    logger = logging.getLogger("Destor")
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    file_handler = logging.FileHandler(log_filename)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger

logger = log_settings()

#Check connection
def check_internet_connection():
    try:
        response = requests.get("https://www.google.com", timeout=5)
        if response.status_code == 200:
            logger.info("Connection established!")
            return True
    except requests.RequestException:
        logger.critical("No connection! [CRITICAL], please solve this program before opening our program again!")
        messagebox.showwarning("Destor [CRITICAL]", "No internet! Cannot connect to (https://www.google.com). Server down? Please try again if you are connected to the internet! If it still doesnt work write us on our Discord Server or create a Issue on GitHub. We will solve it as fast as possible. Our program needs the Internet to sync our logo and other stuff. Please make sure that you have internet connection while using our Program! Maybe chedck if we released a new update on (https://github.com/wfxey/Destor)")
        return False
    
#Icon download
def download_icon(icon_url, file_name):
    try:
        file_path = os.path.join(directory, file_name)
        if os.path.exists(file_path):
            logger.info(f"The file {file_name} already exists.")
            return
        response = requests.get(icon_url)
        if response.status_code == 200:
            with open(file_path, 'wb') as file:
                file.write(response.content)
            logger.info(f"The icon file has been successfully downloaded and saved as {file_path}.")
        else:
            logger.error(f"Failed to download the icon file. Status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        logger.error(f"An error occurred while downloading the icon file: {e}")
    except OSError as e:
        logger.error(f"An error occurred while writing the icon file: {e}")

if __name__ == "__main__":
    icon_url = "https://raw.githubusercontent.com/wfxey/wfxey/main/icon_destor_dark.png"
    file_name = "icon.png"
    
    download_icon(icon_url, file_name)

#Fonts
def download_archivo_black_font():
    font_folder = os.path.join(directory, 'font')
    archivo_black_folder = os.path.join(font_folder, 'archivo_black')

    os.makedirs(archivo_black_folder, exist_ok=True)

    font_url = "https://github.com/wfxey/wfxey/raw/main/font/ArchivoBlack-Regular.ttf"

    font_file_path = os.path.join(archivo_black_folder, 'ArchivoBlack-Regular.ttf')

    urllib.request.urlretrieve(font_url, font_file_path)
    print(f"Font file downloaded to: {font_file_path}")
    
#Config
class Config:
    def __init__(self):
        self.configparser = configparser
        self.platform = platform
        self.my_system = platform.uname()
        self.RAM = str(round(psutil.virtual_memory().total / (1024.**3))) + 'GB'

    def write_data(self):
        logger.info("Writing config.ini")
        config = self.configparser.ConfigParser()
        config['Hardware'] = {'RAM': self.RAM}
        config['System'] = {
            'System': self.my_system.system,
            'Release': self.my_system.release,
            'Version': self.my_system.version,
            'Machine': self.my_system.machine,
            'Processor': self.my_system.processor,
            'Python-Version': self.platform.python_version()
        }
        config['Advanced'] = {'Full-RAM': 'False', 'Developer': 'False'}

        config_path = os.path.join(appdata_dir, 'DT_FILES', 'config.ini')
        os.makedirs(os.path.dirname(config_path), exist_ok=True)  
        with open(config_path, 'w') as configfile:
            config.write(configfile)
        logger.info("Config.ini has been written.")

    def get_data(self, section, key, default=None):
        config = self.configparser.ConfigParser()
        config_path = os.path.join(appdata_dir, 'DT_FILES', 'config.ini')
        config.read(config_path)
        try:
            value = config[section][key]
            logger.info("Configuration value found: [%s] %s = %s", section, key, value)
            return value
        except KeyError:
            logger.error("Section '%s' or key '%s' not found in the configuration.", section, key)
            return default

config = Config()
config.write_data()

ram_value = config.get_data('Hardware', 'RAM', default='8GB')
logger.info(f"Hardware RAM: {ram_value}")

system_value = config.get_data('System', 'System', default='Unknown')
release_value = config.get_data('System', 'Release', default='Unknown')
developer_value = config.get_data('Advanced', 'Developer', default='False')

logger.info(f"System: {system_value}")
logger.info(f"Release: {release_value}")
logger.info(f"Developer: {developer_value}")

#Check for update
def check_for_updates():
    pass

def switch_after_download():
    switch(server_page)

#Stray
def load_image():
    """
    Lädt das Bild für das Tray-Icon.
    """
    image_path = os.path.join(appdata_dir, 'DT_FILES', 'icon.png')
    if os.path.exists(image_path):
        return Image.open(image_path)
    else:
        image = Image.new('RGB', (64, 64), (255, 255, 255))
        dc = ImageDraw.Draw(image)
        dc.rectangle((0, 0, 64, 64), fill=(0, 128, 255))
        dc.rectangle((16, 16, 48, 48), fill=(255, 255, 255))
        return image

def create_tray_icon():
    """
    Erstellt das Tray-Icon.
    """
    icon = pystray.Icon("test_icon")
    icon.icon = load_image()
    icon.title = "Destor v2.0"

    # Füge die Exit-Funktion zum Kontextmenü hinzu
    exit_action = pystray.MenuItem("Exit", exit_application)
    icon.menu = pystray.Menu(exit_action)

    icon.run()

def start_tray_icon():
    """
    Startet das Tray-Icon in einem separaten Thread.
    """
    tray_thread = threading.Thread(target=create_tray_icon, daemon=True)
    tray_thread.start()

def exit_application(icon):
    icon.stop()
    os._exit(0)

#Switching between Pages
def switch(page):
    for fm in main_fm.winfo_children():
        fm.destroy()
    page()

#Create CREATED_SERVERS.txt and override specific Line
def overwrite_specific_line(line_number, text):
    file_path = "DT_FILES/CREATED_SERVERS.txt"
    if not os.path.exists(file_path):
        with open(file_path, "w") as file:
            pass
    
    with open(file_path, "r") as file:
        lines = file.readlines()

    if len(lines) >= line_number:
        if line_number != 1:
            lines[line_number - 1] = text + "\n"
        else:
            lines.insert(0, "\n")
            lines.insert(1, text + "\n")
    else:
        lines.extend(["\n"] * (line_number - len(lines) - 1))
        lines.append(text + "\n")

    with open(file_path, "w") as file:
        file.writelines(lines)

#Check values
def read_specific_value_from_config(config_index, section, key):
    config_path = os.path.join(appdata_dir, 'DT_FILES', f'Server_{config_index}.ini')
    config = configparser.ConfigParser()

    if os.path.exists(config_path):
        config.read(config_path)
        if section in config and key in config[section]:
            return config[section][key], True
        else:
            return None, False
    else:
        return None, False

#Line 1
cs_value1, success1 = read_specific_value_from_config(1, 'Server', 'Server Name')
logger.debug("Line 1 = %s Success = %s", cs_value1, success1)
if success1:
    logger.debug("Line 1 wurde erfolgreich gelesen.")
else:
    logger.debug("Fehler beim Lesen von Line 1.")

#Line 2
cs_value2, success2 = read_specific_value_from_config(2, 'Server', 'Server Name')
logger.debug("Line 2 = %s Success = %s", cs_value2, success2)
if success2:
    logger.debug("Line 2 wurde erfolgreich gelesen.")
else:
    logger.debug("Fehler beim Lesen von Line 2.")

#Line 3
cs_value3, success3 = read_specific_value_from_config(3, 'Server', 'Server Name')
logger.debug("Line 3 = %s Success = %s", cs_value3, success3)
if success3:
    logger.debug("Line 3 wurde erfolgreich gelesen.")
else:
    logger.debug("Fehler beim Lesen von Line 3.")

#Line 4
cs_value4, success4 = read_specific_value_from_config(4, 'Server', 'Server Name')
logger.debug("Line 4 = %s Success = %s", cs_value4, success4)
if success4:
    logger.debug("Line 4 wurde erfolgreich gelesen.")
else:
    logger.debug("Fehler beim Lesen von Line 4.")

#Line 5
cs_value5, success5 = read_specific_value_from_config(5, 'Server', 'Server Name')
logger.debug("Line 5 = %s Success = %s", cs_value5, success5)
if success5:
    logger.debug("Line 5 wurde erfolgreich gelesen.")
else:
    logger.debug("Fehler beim Lesen von Line 5.")

#Some things
logger.info("Current Directory = %s", appdata_dir)

plugins_folder_path = os.path.join(directory, "plugins")
logger.info("Plugins folder path = %s", plugins_folder_path)

if not os.path.exists(plugins_folder_path):
    os.makedirs(plugins_folder_path)
    logger.info("Plugins folder created at: %s", plugins_folder_path)

#Remove Plugin
def remove_plugin():
    initial_dir = os.path.join(directory, "plugins")
    file_path = filedialog.askopenfilename(initialdir=initial_dir, filetypes=[("Jar files", "*.jar")])
    if not file_path:  
        return
    try:
        os.remove(file_path)  
        logger.info("Plugin successfully removed: %s", os.path.basename(file_path))
    except Exception as e:
        logger.error("Error removing plugin: %s", e)

#Add Plugin
def add_plugin():  
    initial_dir = os.path.join(appdata_dir)
    file_path = filedialog.askopenfilename(initialdir=initial_dir, filetypes=[("Jar files", "*.jar")])
    if file_path and os.path.isfile(file_path):
        plugins_folder = os.path.join(initial_dir, "DT_FILES", "plugins")
        if not os.path.exists(plugins_folder):
            os.makedirs(plugins_folder)
        try:
            shutil.copy(file_path, plugins_folder)
            logger.info("Plugin successfully added: %s", os.path.basename(file_path))
        except Exception as e:
            logger.error("Error adding plugin: %s", e)
    else:
        logger.info("No valid .jar file selected.")

def icon_path():
    return os.getenv('APPDATA')

def restart():
    python = sys.executable
    os.startfile(sys.argv[0])
    sys.exit()

if check_internet_connection():
    app = ctk.CTk()
    app.geometry("1100x600")
    app.title("Destor")
    app.wm_iconbitmap()
    icon = os.path.join(appdata_dir, "DT_FILES", "icon.png")
    if os.path.exists(icon):
        app.iconphoto(False, ImageTk.PhotoImage(file=icon))
    else:
        logger.error("Icon file not found: %s", icon)
    app.resizable(width=False, height=False)
    
    if sys.platform == "win32":
        threading.Thread(target=create_tray_icon, daemon=True).start()
    else:
        pass

        
    #Sidebar / Navigation Bar
    sidebar_fm = tk.Frame(app, bg="black", width=200)
    sidebar_fm.pack(side=tk.LEFT, fill=tk.Y)
    
    archivo_black_font_path = os.path.join('SC_FILES', 'font', 'archivo_black', 'ArchivoBlack-Regular.ttf')
    app.tk.call('lappend', 'auto_path', os.path.dirname(archivo_black_font_path))
    app.tk.call('font', 'create', 'archivo_black', '-family', 'ArchivoBlack-Regular', '-size', 16, '-weight', 'bold')

    server_builder_lbl = ctk.CTkLabel(sidebar_fm, text="DESTOR", font=("ArchivoBlack-Regular", 24, "bold"), text_color="white", bg_color="black")
    server_builder_lbl.pack(side=tk.TOP, pady=(15, 0), padx=10)
    
    options_fm = tk.Frame(sidebar_fm, bg="black")
    options_fm.pack(fill=tk.Y, padx=10, pady=10)

    home_btn = ctk.CTkButton(options_fm, text="Home", font=("Open Sans", 16), command=lambda: switch(home_page))
    home_btn.pack(fill=tk.X, pady=5)

    software_btn = ctk.CTkButton(options_fm, text="Server", font=("Open Sans", 16), command=lambda: switch(server_page))
    software_btn.pack(fill=tk.X, pady=5)
    
    settings_btn = ctk.CTkButton(options_fm, text="Settings", font=("Open Sans", 16), command=lambda: switch(settings_page))
    settings_btn.pack(fill=tk.X, pady=5)

    server_builder_lbl = tk.Label(sidebar_fm, text="Destor v24.6.16 Alpha", font=("Open Sans",8), fg="white", bg="black")
    server_builder_lbl.pack(side=tk.BOTTOM, pady=(0, 10), padx=10)

    main_fm = tk.Frame(app, bg="grey17")
    main_fm.pack(fill=tk.BOTH, expand=True)

#Home Page
def home_page():
    logger.info("Loaded Home Page")
    home_frame = ctk.CTkFrame(main_fm)
    home_frame.pack(fill=tk.BOTH, expand=True)
    tabview = ctk.CTkTabview(master=home_frame, width=900, height=550)
    tabview.pack(padx=40, pady=20)

    tabview.add("News")
    tabview.add("Changelog")
    tabview.add("About")
    tabview.set("News")
    
    #Elements for News
    label1 = ctk.CTkLabel(text="News", font=("Open Sans", 25), master=tabview.tab("News"))
    label1.pack(padx = 20, pady = 10)
    label = ctk.CTkLabel(text="Coming soon!", font=("Open Sans", 17), master=tabview.tab("News"))
    label.pack()
    
    #Elements for Changelog
    label = ctk.CTkLabel(text="Changelog", font=("Open Sans", 25), master=tabview.tab("Changelog"))
    label.pack(padx = 20, pady = 10)
    label = ctk.CTkLabel(text="- New design", font=("Open Sans", 13), master=tabview.tab("Changelog"))
    label.pack()
    label = ctk.CTkLabel(text="- Fixed the Launch Server function", font=("Open Sans", 13), master=tabview.tab("Changelog"))
    label.pack()
    label = ctk.CTkLabel(text="- Improved/New the installation file", font=("Open Sans", 13), master=tabview.tab("Changelog"))
    label.pack()
    label = ctk.CTkLabel(text="- System stray", font=("Open Sans", 13), master=tabview.tab("Changelog"))
    label.pack()
    label = ctk.CTkLabel(text="- New logo", font=("Open Sans", 13), master=tabview.tab("Changelog"))
    label.pack()
    label = ctk.CTkLabel(text="- New Name", font=("Open Sans", 13), master=tabview.tab("Changelog"))
    label.pack()
    label = ctk.CTkLabel(text="- Dashboard", font=("Open Sans", 13), master=tabview.tab("Changelog"))
    label.pack()
    label = ctk.CTkLabel(text="- Five servers at the same time", font=("Open Sans", 13), master=tabview.tab("Changelog"))
    label.pack()
    label = ctk.CTkLabel(text="- Better logging", font=("Open Sans", 13), master=tabview.tab("Changelog"))
    label.pack()
    label = ctk.CTkLabel(text="- Doesnt freeze anymore", font=("Open Sans", 13), master=tabview.tab("Changelog"))
    label.pack()
    label = ctk.CTkLabel(text="Contact us on Discord for more Informations!", font=("Open Sans", 15), master=tabview.tab("Changelog"))
    label.pack()
    
    #Elements for About
    label = ctk.CTkLabel(text="About", font=("Open Sans", 25), master=tabview.tab("About"))
    label.pack(padx = 20, pady = 10)
    
    label = ctk.CTkLabel(text="Destor v24.6.16 Alpha", font=("Open Sans", 13), master=tabview.tab("About"))
    label.pack()
    label = ctk.CTkLabel(text="@wfxey, @ivole32", font=("Open Sans", 13), master=tabview.tab("About"))
    label.pack()
    label = ctk.CTkLabel(text="Licenses are inside the licenses files in the LICENSES folder that is inncluded in the GitHub repository.", font=("Open Sans", 13), master=tabview.tab("About"))
    label.pack()
    label = ctk.CTkLabel(text="Copyright (c) 2024 D&I Projects", font=("Open Sans", 13), master=tabview.tab("About"))
    label.pack()
    
    
#Plugins
def plugins_page():
    logger.info("Loaded Plugins Page")
    plugins_frame = ctk.CTkFrame(main_fm)
    plugins_frame.pack(fill=tk.BOTH, expand=True)
    
    global listbox
    listbox = CTkListbox(plugins_frame)
    listbox.pack(fill="both", expand=True, padx=10, pady=10)
    
    create_button1 = ctk.CTkButton(plugins_frame, text="Add plugin", command=add_plugin)
    create_button1.pack(pady=10)  
    
    create_button2 = ctk.CTkButton(plugins_frame, text="Remove plugin", command=remove_plugin)
    create_button2.pack(pady=10)  
    
    plugins_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
    plugins_frame.pack(fill=tk.BOTH, expand=True)

    def show_folder_contents():
        global listbox
        listbox.delete(0, tk.END)
        for item in os.listdir(plugins_folder_path):
            listbox.insert(tk.END, item)
        app.after(1000, show_folder_contents)
        
    show_folder_contents()

#Server Page
def server_page():
    logger.info("Loaded Software Page")
    server_frame = ctk.CTkFrame(main_fm)
    server_frame.pack(fill=tk.BOTH, expand=True)
    
    def radiobutton_event():
        logger.info("Current radiobutton value: %s", radio_var.get())
    
    server_label = ctk.CTkLabel(server_frame, text="New Server", font=("Open Sans", 25))
    server_label.pack(pady=15)
    
    create_server_page_btn = ctk.CTkButton(server_frame, text="Create Server", font=("Open Sans", 15), command=lambda: switch(create_server_page))
    create_server_page_btn.pack(padx=20, pady=15)
    
    server_label = ctk.CTkLabel(server_frame, text="Your Servers", font=("Open Sans", 25))
    server_label.pack(pady=15)
    
    global radio_var
    radio_var = ctk.IntVar(value=0)
    
    server_buttons = []

    for i in range(1, 6):
        server_config, success = read_specific_value_from_config(i, 'Server', 'Server Name')
        
        if success:
            server_name = server_config
            radiobutton = ctk.CTkRadioButton(server_frame, text=server_name, command=radiobutton_event, variable=radio_var, value=i)
            radiobutton.pack(padx=10, pady=10)
            server_buttons.append(radiobutton)
        else:
            logger.info(f"Server {i} doesn't exist. (This is a common error!)")
    
    if server_buttons:
        confirm_button = ctk.CTkButton(server_frame, text="Confirm", command=lambda: switch(dashboard_page))
        confirm_button.pack(padx=10, pady=10)
        delete_button = ctk.CTkButton(server_frame, text="Delete", command=delete_server, fg_color="red3", hover_color="red4")
        delete_button.pack(padx=10, pady=10)
    else:
        label = ctk.CTkLabel(server_frame, text="No Servers available!")
        label.pack(pady=10, padx=10)
###############################################
def delete_server():
    selected_option = radio_var.get()
    after_delete_messagebox = messagebox.askyesno("Destor", "If you delete the server files there is no way to recover them! Are you sure you want to continue?")
    if not after_delete_messagebox:
        return
    else:
        if selected_option == 1:
            logger.info("Starting to delete Server 1")
            folder1 = "Server_1"
            file1 = "Server_1.ini"
            datei_pfad = os.path.join(directory, file1)
            ordner_pfad = os.path.join(directory, folder1)
            if os.path.isdir(ordner_pfad):
                shutil.rmtree(ordner_pfad)
                print(f"The folder '{ordner_pfad}' was deleted.")
            else:
                print(f"The folder '{ordner_pfad}' doesnt exist.")
                
            if os.path.isfile(datei_pfad):
                os.remove(datei_pfad)
                print(f"The file '{datei_pfad}' that is located in '{directory}' was deleted successfully.")
            else:
                print(f"The file '{datei_pfad}' that is located in '{directory}' does not exist.")
        
            switch(server_page)
        
        elif selected_option == 2:
            logger.info("Starting to delete Server 2")
            folder1 = "Server_2"
            file1 = "Server_2.ini"
            datei_pfad = os.path.join(directory, file1)
            ordner_pfad = os.path.join(directory, folder1)
            if os.path.isdir(ordner_pfad):
                shutil.rmtree(ordner_pfad)
                print(f"The folder '{ordner_pfad}' was deleted.")
            else:
                print(f"The folder '{ordner_pfad}' doesnt exist.")
                
            if os.path.isfile(datei_pfad):
                os.remove(datei_pfad)
                print(f"The file '{datei_pfad}' that is located in '{directory}' was deleted successfully.")
            else:
                print(f"The file '{datei_pfad}' that is located in '{directory}' does not exist.")
        
            switch(server_page)
            
        elif selected_option == 3:
            logger.info("Starting to delete Server 3")
            folder1 = "Server_3"
            file1 = "Server_3.ini"
            datei_pfad = os.path.join(directory, file1)
            ordner_pfad = os.path.join(directory, folder1)
            if os.path.isdir(ordner_pfad):
                shutil.rmtree(ordner_pfad)
                print(f"The folder '{ordner_pfad}' was deleted.")
            else:
                print(f"The folder '{ordner_pfad}' doesnt exist.")
                
            if os.path.isfile(datei_pfad):
                os.remove(datei_pfad)
                print(f"The file '{datei_pfad}' that is located in '{directory}' was deleted successfully.")
            else:
                print(f"The file '{datei_pfad}' that is located in '{directory}' does not exist.")
        
            switch(server_page)
            
        elif selected_option == 4:
            logger.info("Starting to delete Server 4")
            folder1 = "Server_4"
            file1 = "Server_4.ini"
            datei_pfad = os.path.join(directory, file1)
            ordner_pfad = os.path.join(directory, folder1)
            if os.path.isdir(ordner_pfad):
                shutil.rmtree(ordner_pfad)
                print(f"The folder '{ordner_pfad}' was deleted.")
            else:
                print(f"The folder '{ordner_pfad}' doesnt exist.")
                
            if os.path.isfile(datei_pfad):
                os.remove(datei_pfad)
                print(f"The file '{datei_pfad}' that is located in '{directory}' was deleted successfully.")
            else:
                print(f"The file '{datei_pfad}' that is located in '{directory}' does not exist.")
        
            switch(server_page)
            
        elif selected_option == 5:
            logger.info("Starting to delete Server 5")
            folder1 = "Server_5"
            file1 = "Server_5.ini"
            datei_pfad = os.path.join(directory, file1)
            ordner_pfad = os.path.join(directory, folder1)
            if os.path.isdir(ordner_pfad):
                shutil.rmtree(ordner_pfad)
                print(f"The folder '{ordner_pfad}' was deleted.")
            else:
                print(f"The folder '{ordner_pfad}' doesnt exist.")
                
            if os.path.isfile(datei_pfad):
                os.remove(datei_pfad)
                print(f"The file '{datei_pfad}' that is located in '{directory}' was deleted successfully.")
            else:
                print(f"The file '{datei_pfad}' that is located in '{directory}' does not exist.")
        
            switch(server_page)
###############################################
class Config_Server:
    def __init__(self, server_name, version, software, max_players, filename='config_server.ini'):
        self.configparser = configparser
        self.server_name = server_name
        self.version = version
        self.software = software
        self.max_players = max_players
        self.filename = filename

    def download_jar(self, jar_url, server_dir, progress_var, progress_label, root):
        jar_path = os.path.join(server_dir, 'server.jar')

        def reporthook(block_num, block_size, total_size):
            downloaded = block_num * block_size
            if total_size > 0:
                progress = min(int(downloaded / total_size * 100), 100)
                progress_var.set(progress)
                root.update_idletasks()

        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            req = urllib.request.Request(jar_url, headers=headers)
            with urllib.request.urlopen(req) as response:
                total_size = int(response.getheader('Content-Length').strip())
                with open(jar_path, 'wb') as out_file:
                    block_size = 8192
                    block_num = 0
                    while True:
                        chunk = response.read(block_size)
                        if not chunk:
                            break
                        out_file.write(chunk)
                        block_num += 1
                        reporthook(block_num, block_size, total_size)

            logger.info(f"Server JAR downloaded to {jar_path}")
            progress_label.configure(text="Download complete")
            root.update_idletasks()
            time.sleep(2)
            root.destroy()
            switch_after_download()
        except urllib.error.HTTPError as e:
            logger.error(f"HTTP Error: {e.code} - {e.reason}")
            progress_label.configure(text=f"HTTP Error: {e.code}")
        except Exception as e:
            logger.error(f"Error: {e}")
            progress_label.configure(text=f"Error: {e}")

    def start_download(self, jar_url, server_dir, progress_var, progress_label, root):
        progress_label.configure(text="Downloading...")
        threading.Thread(target=self.download_jar, args=(jar_url, server_dir, progress_var, progress_label, root)).start()

    def write_data(self):
        logger.info(f"Writing {self.filename}")
        config = self.configparser.ConfigParser()
        config["Server"] = {
            'Server Name': self.server_name,
            'Selected Version': self.version,
            'Selected Software': self.software,
            'Max Player': self.max_players,
        }
        os.makedirs(directory, exist_ok=True)

        for i in range(1, 6):
            config_path = os.path.join(directory, f'Server_{i}.ini')
            if not os.path.exists(config_path):
                with open(config_path, 'w') as configfile:
                    config.write(configfile)
                logger.info(f"Configuration saved to {config_path}")

                server_dir = os.path.join(directory, f'Server_{i}')
                os.makedirs(server_dir, exist_ok=True)
                jar_url = get_jar_url(self.version, self.software)
                if jar_url:
                    self.show_progress_window(jar_url, server_dir)
                else:
                    logger.warning("No URL found for JAR file.")
                
                return True
        else:
            logger.warning("Server limit reached. Cannot create more servers.")
            return False

    def show_progress_window(self, jar_url, server_dir):
        root = ctk.CTk()
        root.title("Downloads")
        root.geometry("350x70")
        progress_var = ctk.IntVar()
        progress_label = ctk.CTkLabel(root, text="Starting download...")
        progress_label.pack(pady=10)
        def after_trying_to_close():
            messagebox.showinfo("Destor", "The download isn't done yet!")
        root.protocol("WM_DELETE_WINDOW", after_trying_to_close)
        progressbar = ctk.CTkProgressBar(root, orientation="horizontal", width=300, mode="determinate", variable=progress_var)
        progressbar.pack(pady=10)

        self.start_download(jar_url, server_dir, progress_var, progress_label, root)

        root.mainloop()
        
    def get_data(self, section, key):
        config = configparser.ConfigParser()
        config_path = os.path.join(appdata_dir, 'DT_FILES', self.filename)
        config.read(config_path)
        return config[section][key]
###############################################
def create_server_page():
    logger.info("Loaded Create Server Page")
    create_server_frame = ctk.CTkFrame(main_fm)
    create_server_frame.pack(fill=tk.BOTH, expand=True)

    def confirm_create_server():
        server_name = entry.get()
        selected_version = selected_option.get()
        selected_software = software_option.get()
        player_count = int(round(player_slider.get()))
        logger.info(f"Server Name: {server_name}")
        logger.info(f"Selected Version: {selected_version}")
        logger.info(f"Selected Software: {selected_software}")
        logger.info(f"Max Player: {player_count}")

        config_server = Config_Server(server_name, selected_version, selected_software, player_count)
        success = config_server.write_data()
        
        if not success:
            messagebox.showwarning("Limit reached", "You can only own 5 servers at the same time!")

    def validate_inputs():
        if entry.get() and selected_option.get() != "Select Version" and software_option.get() != "Select Software":
            confirm_button.configure(state=tk.NORMAL, fg_color="green")
        else:
            confirm_button.configure(state=tk.DISABLED, fg_color="grey")

    def option_changed(choice):
        software_option.set("Select Software")
        software_menu.configure(values=[])

        if choice != "Select Version":
            software_menu.configure(state=tk.NORMAL, fg_color="grey7")
            software_menu.configure(values=["Bukkit", "Spigot", "Vanilla", "Paper"])
        else:
            software_menu.configure(state=tk.DISABLED, fg_color="grey")

        validate_inputs()

    settings_label = ctk.CTkLabel(create_server_frame, text="Create Server", font=("Open Sans", 25))
    settings_label.pack(pady=15)
    
    name_label = ctk.CTkLabel(create_server_frame, text="Server Name", font=("Open Sans", 13))
    name_label.pack()
    
    entry = ctk.CTkEntry(create_server_frame, width=180, height=30, border_width=1, corner_radius=10, fg_color="grey7", placeholder_text="Server Name")
    entry.pack(pady=10, padx=10)
    entry.bind("<KeyRelease>", lambda event: validate_inputs())

    software_label = ctk.CTkLabel(create_server_frame, text="Server Version", font=("Open Sans", 13))
    software_label.pack(pady=(20, 0))

    selected_option = ctk.StringVar(value="Select Version")
    option_menu = ctk.CTkOptionMenu(create_server_frame, values=["1.20.6", "1.20.4", "1.20.2", "1.19.4", "1.18.2", "1.16.5", "1.12.2"], variable=selected_option, command=option_changed)
    option_menu.pack(pady=20)

    software_label = ctk.CTkLabel(create_server_frame, text="Server Software", font=("Open Sans", 13))
    software_label.pack(pady=(20, 0))

    software_option = ctk.StringVar(value="Select Software")
    software_menu = ctk.CTkOptionMenu(create_server_frame, values=[], variable=software_option, command=lambda choice: validate_inputs())
    software_menu.pack(pady=10)
    software_menu.configure(state=tk.DISABLED, fg_color="grey")

    player_count_label = ctk.CTkLabel(create_server_frame, text="Max Player", font=("Open Sans", 13))
    player_count_label.pack(pady=(20, 0))

    player_slider_frame = ctk.CTkFrame(create_server_frame)
    player_slider_frame.pack(pady=20)

    def update_slider_label(value):
        rounded_value = int(round(float(value)))
        slider_label.configure(text=f"Max Player: {rounded_value}")
    player_slider = ctk.CTkSlider(player_slider_frame, from_=2, to=100, command=update_slider_label)
    player_slider.pack()

    slider_label = ctk.CTkLabel(player_slider_frame, text="Max Player: 50", font=("Open Sans", 13))
    slider_label.pack(pady=10)

    confirm_button = ctk.CTkButton(create_server_frame, text="Confirm", font=("Open Sans", 16), command=confirm_create_server, state=tk.DISABLED, fg_color="grey")
    confirm_button.pack(side=ctk.BOTTOM, pady=(0, 10), padx=10)

    validate_inputs()

###############################################
def dashboard_page():
    dashboard_frame = ctk.CTkFrame(main_fm)
    dashboard_frame.pack(fill=tk.BOTH, expand=True)
    selected_option = radio_var.get()
    
    def back():
        switch(server_page)
        
    def rules():
        switch(show_game_rules)
        
    def last_dashboard():
        switch(dashboard_page)
        
        
    def show_game_rules():
        logger.info("Displaying Game Rules")
        game_rules_frame = ctk.CTkFrame(main_fm)
        game_rules_frame.pack(fill=tk.BOTH, expand=True)
        
        def create_function_frame(parent, button_text, button_command, description_text, indicator_needed=False, fg_color=None):
            function_frame = ctk.CTkFrame(parent, fg_color=fg_color)
            function_frame.pack(fill=X, padx=10, pady=10)

            function_frame.columnconfigure(0, weight=1)
            function_frame.columnconfigure(1, weight=1)
            function_frame.columnconfigure(2, weight=1)

            button = ctk.CTkButton(function_frame, text=button_text, command=button_command)
            button.grid(row=0, column=0, sticky="w")

            indicator = None
            if indicator_needed:
                indicator = ctk.CTkLabel(function_frame, text="", font=("Open Sans", 15))
                indicator.grid(row=0, column=1, sticky="nsew")

            description = ctk.CTkLabel(function_frame, text=description_text, font=("Open Sans", 15))
            description.grid(row=0, column=2, sticky="e")

            return function_frame, button, indicator
        
        button_frame = ctk.CTkFrame(game_rules_frame)
        button_frame.pack(side=tk.BOTTOM, padx=10, pady=10)
        
        back_button = ctk.CTkButton(button_frame, text="Back", font=("Open Sans", 14), fg_color="red3", hover_color="red4", command=last_dashboard)
        back_button.pack(pady=10, padx=10)
    
    def start_server():
        selected_option = radio_var.get()
        logger.info(f"Starting server for option {selected_option}")
    
    if selected_option == 1:
        logger.info("Redirecting to Dashboard 1")

        label = ctk.CTkLabel(dashboard_frame, text="Dashboard", font=("Open Sans", 26))
        label.pack(padx=10, pady=10)

        textbox = ctk.CTkTextbox(dashboard_frame, width=700, height=200)
        textbox.configure(state="disabled") 
        textbox.pack(padx=10, pady=10)

        button_frame = ctk.CTkFrame(dashboard_frame)
        button_frame.pack(side=tk.BOTTOM, padx=10, pady=10)

        start_button = ctk.CTkButton(button_frame, text="Start Server", font=("Open Sans", 14), command=start_server)
        start_button.pack(side=tk.LEFT, padx=10, pady=10)

        back_button = ctk.CTkButton(button_frame, text="Back", font=("Open Sans", 14), fg_color="red3", hover_color="red4", command=back)
        back_button.pack(side=tk.RIGHT, padx=10, pady=10)
        
        game_rules_button = ctk.CTkButton(button_frame, text="Game Rules", font=("Open Sans", 14), command=rules)
        game_rules_button.pack(side=tk.LEFT, padx=10, pady=10)
        
    #Dashboard2
    elif selected_option == 2:
        logger.info("Redirecting to Dasboard 2")
        label = ctk.CTkLabel(dashboard_frame, text="2")
        label.pack()
    #Dashboard3
    elif selected_option == 3:
        logger.info("Redirecting to Dashboard 3")
        label = ctk.CTkLabel(dashboard_frame, text="3")
        label.pack()
    #Dashboard4
    elif selected_option == 4:
        logger.info("Redirecting to Dashboard 4")
    #Dashboard5
    elif selected_option == 5:
        logger.info("Redirecting to Dashboard 5")
###############################################
def get_jar_url(version, software):
    jar_urls = {
        "1.20.6": {
            "Bukkit": "https://download.getbukkit.org/craftbukkit/craftbukkit-1.20.6.jar",
            "Spigot": "https://download.getbukkit.org/spigot/spigot-1.20.6.jar",
            "Vanilla": "https://piston-data.mojang.com/v1/objects/145ff0858209bcfc164859ba735d4199aafa1eea/server.jar",
            "Paper": "https://api.papermc.io/v2/projects/paper/versions/1.20.6/builds/130/downloads/paper-1.20.6-130.jar"
        },
        "1.20.4": {
            "Bukkit": "https://download.getbukkit.org/craftbukkit/craftbukkit-1.20.4.jar",
            "Spigot": "https://download.getbukkit.org/spigot/spigot-1.20.4.jar",
            "Vanilla": "https://piston-data.mojang.com/v1/objects/8dd1a28015f51b1803213892b50b7b4fc76e594d/server.jar",
            "Paper": "https://api.papermc.io/v2/projects/paper/versions/1.20.4/builds/496/downloads/paper-1.20.4-496.jar"
        },
        "1.20.2": {
            "Bukkit": "https://download.getbukkit.org/craftbukkit/craftbukkit-1.20.2.jar",
            "Spigot": "https://download.getbukkit.org/spigot/spigot-1.20.2.jar",
            "Vanilla": "https://piston-data.mojang.com/v1/objects/5b868151bd02b41319f54c8d4061b8cae84e665c/server.jar",
            "Paper": "https://api.papermc.io/v2/projects/paper/versions/1.20.2/builds/318/downloads/paper-1.20.2-318.jar"
        },
        "1.19.4": {
            "Bukkit": "https://download.getbukkit.org/craftbukkit/craftbukkit-1.19.4.jar",
            "Spigot": "https://download.getbukkit.org/spigot/spigot-1.19.4.jar",
            "Vanilla": "https://piston-data.mojang.com/v1/objects/8f3112a1049751cc472ec13e397eade5336ca7ae/server.jar",
            "Paper": "https://api.papermc.io/v2/projects/paper/versions/1.19.4/builds/550/downloads/paper-1.19.4-550.jar"
        },
        "1.18.2": {
            "Bukkit": "https://download.getbukkit.org/craftbukkit/craftbukkit-1.18.2.jar",
            "Spigot": "https://download.getbukkit.org/spigot/spigot-1.18.2.jar",
            "Vanilla": "https://piston-data.mojang.com/v1/objects/c8f83c5655308435b3dcf03c06d9fe8740a77469/server.jar",
            "Paper": "https://api.papermc.io/v2/projects/paper/versions/1.18.2/builds/388/downloads/paper-1.18.2-388.jar"
        },
        "1.16.5": {
            "Bukkit": "https://cdn.getbukkit.org/craftbukkit/craftbukkit-1.16.5.jar",
            "Spigot": "https://cdn.getbukkit.org/spigot/spigot-1.16.5.jar",
            "Vanilla": "https://piston-data.mojang.com/v1/objects/1b557e7b033b583cd9f66746b7a9ab1ec1673ced/server.jar",
            "Paper": "https://api.papermc.io/v2/projects/paper/versions/1.16.5/builds/794/downloads/paper-1.16.5-794.jar"
        },
        "1.12.2": {
            "Bukkit": "https://cdn.getbukkit.org/craftbukkit/craftbukkit-1.12.2.jar",
            "Spigot": "https://cdn.getbukkit.org/spigot/spigot-1.12.2.jar",
            "Vanilla": "https://piston-data.mojang.com/v1/objects/886945bfb2b978778c3a0288fd7fab09d315b25f/server.jar",
            "Paper": "https://api.papermc.io/v2/projects/paper/versions/1.12.2/builds/1620/downloads/paper-1.12.2-1620.jar"
        },
    }

    if version in jar_urls and software in jar_urls[version]:
        return jar_urls[version][software]
    else:
        pass
###############################################
def settings_page():
    global toggle_button
    global indicator_label
    
    logger.info("Loaded Settings Page")
    settings_frame = ctk.CTkFrame(main_fm)
    settings_frame.pack(fill=BOTH, expand=True)

    settings_label = ctk.CTkLabel(settings_frame, text="General", font=("Open Sans", 25))
    settings_label.pack(pady=15)

    def explorer_open_dir(directory):
        logger.debug(f"Opening directory: {directory}")
        subprocess.Popen(['explorer', directory])
        
    def toggle_and_disable():
        toggle_button.configure(state=ctk.DISABLED)
        toggle_presence()
        time.sleep(1)
        toggle_button.configure(state=ctk.NORMAL)
        update_presence_indicator()
        
    def toggle_and_disable_theme():
        toggle_button.configure(state=ctk.DISABLED)
        toggle_theme()
        time.sleep(1)
        toggle_button.configure(state=ctk.NORMAL)
        update_theme_indicator()

    def create_function_frame(parent, button_text, button_command, description_text, indicator_needed=False, fg_color=None):
        function_frame = ctk.CTkFrame(parent, fg_color=fg_color)
        function_frame.pack(fill=X, padx=10, pady=10)

        function_frame.columnconfigure(0, weight=1)
        function_frame.columnconfigure(1, weight=1)
        function_frame.columnconfigure(2, weight=1)

        button = ctk.CTkButton(function_frame, text=button_text, command=button_command)
        button.grid(row=0, column=0, sticky="w")

        indicator = None
        if indicator_needed:
            indicator = ctk.CTkLabel(function_frame, text="", font=("Open Sans", 15))
            indicator.grid(row=0, column=1, sticky="nsew")

        description = ctk.CTkLabel(function_frame, text=description_text, font=("Open Sans", 15))
        description.grid(row=0, column=2, sticky="e")

        return function_frame, button, indicator

    toggle_presence_frame, toggle_button, indicator_label = create_function_frame(
        settings_frame,
        button_text="Discord rich presence",
        button_command=toggle_and_disable,
        description_text="Toggle Discord rich presence.   ",
        indicator_needed=True
    )
    
    change_theme_frame, _, _ = create_function_frame(
        settings_frame,
        button_text="Theme",
        button_command=toggle_and_disable_theme,
        description_text="Turn light mode on and off.   ",
        indicator_needed=True
    )

    check_for_update_frame, _, _ = create_function_frame(
        settings_frame,
        button_text="Check for update",
        button_command=check_for_updates,
        description_text="Checks for new updates.   ",
    )
    
    settings_label = ctk.CTkLabel(settings_frame, text="Developer", font=("Open Sans", 25))
    settings_label.pack(pady=15)
        
    update_code_frame, _, _ = create_function_frame(
        settings_frame,
        button_text="Update Code",
        button_command=restart,
        description_text="Restarts the Application.   "
    )
    
    open_explorer_frame, _, _ = create_function_frame(
        settings_frame,
        button_text="Open DT_FILES",
        button_command=lambda: explorer_open_dir(path),
        description_text="Open the AppData from Destor.   "
    )

    update_presence_indicator()
    update_theme_indicator()
###############################################
def read_status_from_file_theme():
    file_name = 'theme.txt'
    file_path = os.path.join(appdata_dir, 'DT_FILES', file_name)
    
    if not os.path.exists(file_path):
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w') as file:
                file.write('true')
            logger.info("File created with default status: true")
            return 'true'
        except Exception as e:
            logger.error(f"Failed to create file: {e}")
            return 'false'
    else:
        try:
            with open(file_path, 'r') as file:
                return file.read().strip().lower()
        except Exception as e:
            logger.error(f"Failed to read status from file: {e}")
            return 'false'

def toggle_theme():
    current_status = read_status_from_file_theme()
    new_status = 'false' if current_status == 'true' else 'true'
    try:
        file_path = os.path.join(directory, 'THEME.txt')
        with open(file_path, 'w') as file:
            file.write(new_status)
        logger.info(f"Light mode set to: {new_status}")
    except Exception as e:
        logger.error(f"Failed to write theme status to file: {e}")
        return
    theme_switch()
    update_theme_indicator()
    
def theme_switch():
    current_status = read_status_from_file_theme()
    if current_status == 'true':
        ctk.set_appearance_mode("Dark")
    else:
        ctk.set_appearance_mode("Light")
        
def update_theme_indicator():
    status = read_status_from_file_theme()
    indicator_label.configure(text="ON" if status == 'true' else "OFF")
###############################################
def read_status_from_file():
    file_name = 'DISCORD.txt'
    file_path = os.path.join(appdata_dir, 'DT_FILES', file_name)
    
    if not os.path.exists(file_path):
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w') as file:
                file.write('true')
            logger.info("File created with default status: true")
            return 'true'
        except Exception as e:
            logger.error(f"Failed to create file: {e}")
            return 'false'
    else:
        try:
            with open(file_path, 'r') as file:
                return file.read().strip().lower()
        except Exception as e:
            logger.error(f"Failed to read status from file: {e}")
            return 'false'

def toggle_presence():
    global RPC
    current_status = read_status_from_file()
    new_status = 'false' if current_status == 'true' else 'true'
    try:
        file_path = os.path.join(directory, 'DISCORD.txt')
        with open(file_path, 'w') as file:
            file.write(new_status)
        logger.info(f"Presence status set to: {new_status}")
    except Exception as e:
        logger.error(f"Failed to write status to file: {e}")
        return
    discord_rich_presence()
    update_presence_indicator()


def discord_rich_presence():
    global RPC
    current_status = read_status_from_file()
    if current_status == 'true':
        try:
            if RPC is None:
                RPC = Presence(client_id)
                RPC.connect()
                logger.info("Connected to Discord")
            presence_data = {
                'state': 'Playing',
                'details': 'Playing',
                'large_image': 'icon1',
                'large_text': 'Destor v2.0',
                'party_id': 'ae488379-351d-4a4f-ad32-2b9b01c91657',
                'party_size': [1, 1],
                'join': 'MTI4NzM0OjFpMmhuZToxMjMxMjM='
            }
            RPC.update(**presence_data)
            logger.info("Presence updated")
        except Exception as e:
            logger.error(f"Failed to update presence: {e}")
            RPC = None
    else:
        if RPC:
            try:
                RPC.close()
                logger.info("Discord connection closed")
                RPC = None
            except Exception as e:
                logger.error(f"Failed to close Discord connection: {e}")

def update_presence_indicator():
    status = read_status_from_file()
    indicator_label.configure(text="ON" if status == 'true' else "OFF")
###############################################
theme_switch()
discord_rich_presence()
home_page()
app.mainloop()
###############################################