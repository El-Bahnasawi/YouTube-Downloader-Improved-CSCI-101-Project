import os
from pytube import YouTube, Playlist
import subprocess
import win32com.client
import re
from pytube.exceptions import VideoUnavailable

class VideoStreamFetcher:
    """
    Helper class responsible for fetching video streams based on the desired quality from YouTube.
    """
    
    def __init__(self, yt: YouTube, video_quality: str = None) -> None:
        """
        Initialize the fetcher with the YouTube video and desired quality.

        :param yt: Instance of the YouTube video.
        :param video_quality: Desired video quality.
        """
        self.yt = yt
        self.video_quality = video_quality

    def get_video_stream(self):
        """Returns the video stream corresponding to the desired quality."""
        try:
            return self.yt.streams.filter(only_video=True, res=self.video_quality, file_extension="mp4").first()
        except Exception as e:
            print(f"Error fetching video stream of quality {self.video_quality}: {e}")
            return None

    def get_all_streams(self):
        """Returns all available streams for the video."""
        try:
            return self.yt.streams
        except Exception as e:
            if "is streaming live" in str(e):
                print("The video is a live stream and cannot be loaded.")
            else:
                print(f"Error fetching all streams: {e}")
            return []



class AudioStreamFetcher:
    def __init__(self, yt, video_quality):
        self.yt = yt
        self.video_quality = video_quality

    def get_audio_stream(self):
        try:
            if self.video_quality in ["1080p", "720p"]:
                stream = self.yt.streams.filter(only_audio=True).order_by("abr").desc().first()
            else:
                audio_qualities = self.yt.streams.filter(only_audio=True).order_by("abr").desc()
                stream = audio_qualities[2] if len(audio_qualities) > 2 else audio_qualities[-1]

            # If the desired quality isn't found, get the best available audio quality
            if not stream:
                stream = self.yt.streams.filter(only_audio=True).order_by("abr").desc().first()
            
            return stream
        except Exception as e:
            print(f"Error fetching audio stream: {e}")
            return None

class StreamDownloader:
    """
    Helper class responsible for downloading a given stream.
    """
    
    def __init__(self, folder: str) -> None:
        """
        Initialize the downloader with a destination folder.

        :param folder: Path to the destination folder.
        """
        self.folder = folder


    def download_stream(self, stream, prefix: str) -> str:
        """
        Download the provided stream with a given prefix and ensure a certain file extension.

        :param stream: Stream to be downloaded.
        :param prefix: Prefix for the saved file.
        :param file_extension: Desired file extension (without the dot). Default is None.
        :return: Path to the saved file.
        """

        # Normalize the folder path
        normalized_folder = os.path.normpath(self.folder)
        
        # Get the default filename that the stream would use
        default_filename = stream.default_filename
        
        # Build a new filename using the prefix
        new_filename = prefix + default_filename
        
        # Download the stream
        return stream.download(output_path=normalized_folder, filename=new_filename)


class FileMerger:
    """
    Helper class responsible for merging video and audio files into a single file.
    """
    
    def __init__(self, yt: YouTube, folder: str, video_quality: str) -> None:
        """
        Initialize the merger with the YouTube video, destination folder, and video quality.

        :param yt: Instance of the YouTube video.
        :param folder: Path to the destination folder.
        :param video_quality: Quality of the video file to merge.
        """
        self.yt = yt
        self.folder = folder
        self.video_quality = video_quality

    def merge(self, video_count: str = "", video_filename: str = "", audio_filename: str = "") -> None:
        """
        Merge video and audio files into a single file.

        :param video_filename: Path to the video file.
        :param audio_filename: Path to the audio file.
        """
        valid_title = "".join([c for c in self.yt.title if c.isalpha() or c.isdigit() or c == ' ']).rstrip()
        if video_count:
            output_filename = os.path.join(self.folder, f"{video_count}_{valid_title}_{self.video_quality}.mp4")
        else:
            output_filename = os.path.join(self.folder, f"{valid_title}_{self.video_quality}.mp4")
        cmd = [
            'ffmpeg',
            '-i', video_filename,
            '-i', audio_filename,
            '-c:v', 'copy',
            '-c:a', 'copy',
            output_filename
        ]
        try:
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error during merging video and audio: {e}")
            
        os.remove(video_filename)
        os.remove(audio_filename)

class CombinedProgress:
    """
    Helper class responsible for tracking and aggregating the download progress 
    of both video and audio streams.

    When downloading high-quality videos from platforms like YouTube, the video and 
    audio streams are often separate. `CombinedProgress` helps in tracking the overall 
    progress of both streams as they are downloaded concurrently.

    Attributes:
        video_stream: The video stream that is being tracked.
        audio_stream: The audio stream that is being tracked.
        video_bytes: The total bytes of the video stream downloaded so far.
        audio_bytes: The total bytes of the audio stream downloaded so far.
        total_bytes: The sum of the total bytes of both video and audio streams.
        progress_callback: A callback function that gets invoked as the download progresses.
        last_updated_percentage: The most recent progress percentage reported to avoid 
                                 frequent and minimal updates.
    """
    
    def __init__(self, video_stream, audio_stream, progress_callback) -> None:
        """
        Initialize the progress tracker with video and audio streams, and a progress callback.

        :param video_stream: Video stream to track.
        :param audio_stream: Audio stream to track.
        :param progress_callback: Callback function that gets triggered as download progresses.
                                  This callback function typically updates UI components.
        """
        self.video_stream = video_stream
        self.audio_stream = audio_stream
        self.video_bytes = 0
        self.audio_bytes = 0
        self.total_bytes = video_stream.filesize + audio_stream.filesize
        self.progress_callback = progress_callback
        self.last_updated_percentage = 0

    def video_progress(self, stream, chunk, bytes_remaining) -> None:
        """
        Callback function for the video download progress. It calculates how many bytes 
        of the video stream have been downloaded and triggers an update to the combined 
        progress.

        :param stream: The current stream being downloaded (should be the video stream).
        :param chunk: Segment of data being handled. Not used directly in this function but 
                      retained for signature consistency.
        :param bytes_remaining: How many bytes are left to download for this stream.
        """
        self.video_bytes = self.video_stream.filesize - bytes_remaining
        self._update_combined_progress()

    def audio_progress(self, stream, chunk, bytes_remaining) -> None:
        """
        Callback function for the audio download progress. Similar to `video_progress`, 
        but for the audio stream.

        :param stream: The current stream being downloaded (should be the audio stream).
        :param chunk: Segment of data being handled. Not used directly in this function but 
                      retained for signature consistency.
        :param bytes_remaining: How many bytes are left to download for this stream.
        """
        self.audio_bytes = self.audio_stream.filesize - bytes_remaining
        self._update_combined_progress()

    def _update_combined_progress(self) -> None:
        """
        Calculate the combined progress of both video and audio streams, and trigger 
        the callback if the progress change is significant (more than 5% difference 
        from the last reported percentage). This method is private and should not be 
        called outside the context of this class.
        """
        combined_bytes_downloaded = self.video_bytes + self.audio_bytes
        combined_percentage = (combined_bytes_downloaded / self.total_bytes) * 100

        # Update only if the difference in progress is more than 5%.
        if abs(combined_percentage - self.last_updated_percentage) > 5:
            self.progress_callback(combined_percentage)
            self.last_updated_percentage = combined_percentage


def get_youtube_object(link: str):
    """Return a YouTube object if the link is a valid YouTube link, otherwise None."""
    video_pattern = r'https?://www\.youtube\.com/watch\?v=[^&]+'
    if re.match(video_pattern, link):
        return YouTube(link)
    return None

def get_playlist_first_video(link: str):
    """Return the first video in a playlist, if the link is a valid playlist link, otherwise None."""
    if "youtube.com/playlist?list=" in link:
        playlist = Playlist(link)
        if playlist.video_urls:
            return YouTube(playlist.video_urls[0])
    return None

def get_available_qualities(link: str) -> list:
    """Retrieve available video qualities for a given YouTube link, specifically for the .mp4 file extension."""

    yt = get_youtube_object(link) or get_playlist_first_video(link)
    
    if not yt:
        print("The provided link is neither a YouTube video nor a playlist.")
        return []
    
    try:
        fetcher = VideoStreamFetcher(yt)
        all_streams = fetcher.get_all_streams()

        # We're only interested in .mp4 streams that have video content, so we filter those and extract the resolution.
        mp4_qualities = [stream.resolution for stream in all_streams if stream.video_codec and not stream.audio_codec and stream.subtype == "mp4"]

        # Sorting and de-duping qualities
        return sorted(list(set(mp4_qualities)), key=lambda x: int(x[:-1]))
    
    except VideoUnavailable:
        print("This video is unavailable.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    return []


def refresh_folder(folder_path):
    """Refresh a specific folder in Windows Explorer."""
    try:
        shell = win32com.client.Dispatch("Shell.Application")
        folder = shell.NameSpace(folder_path)
        if folder:
            folder.Self.InvokeVerb("refresh")
    except Exception as e:
        print(f"Error refreshing folder: {e}")