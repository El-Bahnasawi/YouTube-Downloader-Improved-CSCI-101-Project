from tkinter import *
from tkinter import ttk, filedialog

def setup_gui(window, populate_qualities_func):
    """
    Set up the GUI components for the YouTube downloader.

    :param window: The main application window.
    :param populate_qualities_func: Function to populate available download qualities.
    :return: Dictionary of GUI components.
    """
    
    components = {}

    # Title
    window.title("YouTube Downloader")

    # Set up window properties
    window.geometry("1200x300")
    
     # GUI components setup...
    Label(window, text="YouTube Link").place(x=100, y=85)
    components["Link"] = StringVar()
    components["LinkEntry"] = Entry(window, textvariable=components["Link"], width=50)
    components["LinkEntry"].place(x=250, y=85, width=300, height=25)
    
    # Label to display the video name
    components["videoNameLabel"] = Label(window, text="", wraplength=600, font=("Arial", 12))
    components["videoNameLabel"].place(x=250, y=115)

    Label(window, text="Save To:").place(x=100, y=145)
    components["fileLocationLabel"] = Label(window, text="Not selected", bg="white", anchor='w')
    components["fileLocationLabel"].place(x=250, y=145, width=300, height=25)
    
    Button(window, text="Choose Folder", command=lambda: open_directory(components)).place(x=600, y=140)

    # Add more GUI components here...
    components["progressBar"] = ttk.Progressbar(window, orient="horizontal", length=400, mode="determinate")
    components["progressBar"].place(x=250, y=220)
    
    # Button to fetch available qualities
    components["fetchQualitiesButton"] = Button(window, text="Fetch Qualities", command=populate_qualities_func)
    components["fetchQualitiesButton"].place(x=600, y=80)  # Directly above the Choose Folder button

    # Dropdown menu (combobox) for qualities
    components["qualityDropdown"] = ttk.Combobox(window)
    components["qualityDropdown"].place(x=700, y=80, width=150)  # To the right of the Fetch Qualities button

    return components

def open_directory(components: dict) -> None:
    """
    Open the directory chooser and update the label with the chosen directory.

    :param components: Dictionary of GUI components.
    """
    FolderName = filedialog.askdirectory()
    if len(FolderName) > 1:
        components["fileLocationLabel"].config(text=FolderName)
    else:
        components["fileLocationLabel"].config(text="Please choose folder!")