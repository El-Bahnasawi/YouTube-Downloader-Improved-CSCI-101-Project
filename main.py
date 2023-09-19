from tkinter import Tk, Button, messagebox
import threading

from gui_setup import *
from utils import *
from strategies import *
from downloader_context import DownloaderContext

# Define a threading decorator for threaded functions
def threaded(func):
    """
    Decorator for threading functions to run them in the background.

    :param func: The function to be threaded.
    :return: Threaded version of the function.
    """
    def wrapper(*args, **kwargs):
        thread = threading.Thread(target=func, args=args, kwargs=kwargs, daemon=True)
        thread.start()
    return wrapper

@threaded
def progress_stream(stream, chunk, combined_percentage):
    components["progressBar"]['value'] = combined_percentage
    window.update_idletasks()

    if combined_percentage == 100:
        messagebox.showinfo(message="The video is successfully downloaded")


@threaded
def update_video_name_label(event=None):
    link = components["Link"].get()
    try:
        video_pattern = r'https?://www\.youtube\.com/watch\?v=[^&]+'

        if re.match(video_pattern, link):
            yt = YouTube(link)
            components["videoNameLabel"].config(text=yt.title)
        if "youtube.com/playlist?list=" in link:
            p = Playlist(link)
            components["videoNameLabel"].config(text=p.title)
    except Exception as e:
        components["videoNameLabel"].config(text="Error fetching video name.")

# Primary Functions with Threading
@threaded
def execute_download(strategy_type):
    link = components["Link"].get()
    folder = components["fileLocationLabel"]["text"]
    quality = components["qualityDropdown"].get() if strategy_type == "video" or "playlist" else None
    
    video_pattern = r'https?://www\.youtube\.com/watch\?v=[^&]+'
    if re.match(video_pattern, link) and strategy_type == "playlist":
        messagebox.showerror("Invalid Operation", "The provided link is a video link, not a playlist!")
        return
    if "youtube.com/playlist?list=" in link and strategy_type == "video":
        messagebox.showerror("Invalid Operation", "The provided link is a playlist link, not a video!")
        return
    if "youtube.com/playlist?list=" in link and strategy_type == "thumbnail":
        messagebox.showerror("Invalid Operation", "The provided link is a playlist link, a playlist doesn't have a thumbnail")
        return
    
    context = DownloaderContext(strategy_type=strategy_type, link=link, folder=folder, quality=quality, progress_callback=progress_stream)
    context.execute_download()

    
@threaded
def populate_qualities():
    link = components["Link"].get()
    dropdown_values = get_available_qualities(link)

    components["qualityDropdown"]["values"] = dropdown_values
    if dropdown_values:
        components["qualityDropdown"].set(dropdown_values[0])  # Set to the first value
    else:
        components["qualityDropdown"].set("")

# Reset Function
def reset_all():
    components["Link"].set("")
    components["videoNameLabel"].config(text="")
    components["qualityDropdown"].set("")
    components["progressBar"]['value'] = 0
    components["fileLocationLabel"].config(text="Not selected")

# Initialize and Bind to GUI
window = Tk()
components = setup_gui(window, populate_qualities)

Button(window, text="Download Playlist", command=lambda: execute_download("playlist")).place(x=250, y=180)
Button(window, text="Download Video", command=lambda: execute_download("video")).place(x=375, y=180)
Button(window, text="Download Thumbnail", command=lambda: execute_download("thumbnail")).place(x=490, y=180)
components["LinkEntry"].bind("<FocusOut>", update_video_name_label)
Button(window, text="Reset", command=reset_all).place(x=800, y=215, width=150)

window.mainloop()
