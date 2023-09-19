import urllib.request
from PIL import Image
import re
from abc import ABC, abstractmethod
from pytube import YouTube, Playlist
from utils import VideoStreamFetcher, AudioStreamFetcher, StreamDownloader, FileMerger, CombinedProgress
import time

class IDownloadStrategy(ABC):    
    def __init__(self, link, folder):
        self.link = link
        self.folder = folder

    @abstractmethod
    def download(self):
        """Downloads the content based on the strategy's implementation."""
        pass

class VideoDownloadStrategy(IDownloadStrategy):
    def __init__(self, link, folder, video_quality, progress_callback, if_playlist_video_count=""):
        super().__init__(link, folder)
        self.video_quality = video_quality
        self.progress_callback = progress_callback
        self.if_playlist_video_count = if_playlist_video_count

    def download(self):
        if self._initiate_download():
            self._perform_download()

    def _initiate_download(self):
        """Attempt to initialize the YouTube object with retries."""
        for _ in range(3):  # Try 3 times
            try:
                self.yt = YouTube(self.link, on_progress_callback=self.progress_callback)
                return True
            except Exception as e:
                time.sleep(5)
                print(str(e))
        else:
            print("Failed to fetch the video after 3 attempts.")
            return False

    def _perform_download(self):
        """Execute the download actions assuming YouTube object is initialized."""
        video_fetcher = VideoStreamFetcher(yt=self.yt, video_quality=self.video_quality)
        audio_fetcher = AudioStreamFetcher(self.yt, self.video_quality)

        video_stream = video_fetcher.get_video_stream()
        audio_stream = audio_fetcher.get_audio_stream()

        # Make sure we have valid streams before proceeding
        if not video_stream or not audio_stream:
            print("Error fetching video or audio stream.")
            return

        combined_progress = CombinedProgress(video_stream=video_stream, 
                                             audio_stream=audio_stream, 
                                             progress_callback=self._update_combined_progress)
        
        downloader = StreamDownloader(folder=self.folder)

        self.yt.register_on_progress_callback(combined_progress.video_progress)
        video_filename = downloader.download_stream(stream=video_stream, prefix="video_")

        self.yt.register_on_progress_callback(combined_progress.audio_progress)  # Switch to audio progress
        audio_filename = downloader.download_stream(audio_stream, "audio_")

        file_merger = FileMerger(yt=self.yt, 
                                 folder=self.folder, 
                                 video_quality=self.video_quality)
        file_merger.merge(video_count=self.if_playlist_video_count, video_filename=video_filename, audio_filename=audio_filename)

    def _update_combined_progress(self, combined_percentage):
        if self.progress_callback:
            self.progress_callback(None, None, combined_percentage)


class PlaylistDownloadStrategy(IDownloadStrategy):
    def __init__(self, link, folder, video_quality, progress_callback):
        super().__init__(link, folder)
        self.video_quality = video_quality
        self.progress_callback = progress_callback
    
        self.playlist = Playlist(self.link)    
        self.folder += f"/{self.playlist.title}" 

    def download(self):
        for index, url in enumerate(self.playlist.video_urls):
            video = VideoDownloadStrategy(link=url, folder=self.folder, video_quality=self.video_quality, progress_callback=self.progress_callback, if_playlist_video_count=str(index + 1))
            video.download()


class ThumbnailDownloadStrategy(IDownloadStrategy):
    def __init__(self, link, folder):
        super().__init__(link, folder)

    def download(self):
        yt = YouTube(self.link)
        title = yt.title
        valid_filename = re.sub(r'[^\w\s-]', '', title).strip().replace(' ', '_')
        PicUrl = yt.thumbnail_url
        filename = f"{self.folder}/{valid_filename}.png"
        urllib.request.urlretrieve(PicUrl, filename)
        img = Image.open(filename)
        img.show()
        return img
