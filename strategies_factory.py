from strategies import VideoDownloadStrategy, PlaylistDownloadStrategy, ThumbnailDownloadStrategy, IDownloadStrategy

class StrategyFactory:
    """
    This serves as a factory for creating download strategies based on input parameters.
    It abstracts the creation process and offers a single point of modification when adding or removing strategies.
    """
    
    @staticmethod
    def get_strategy(strategy_type: str, link: str, folder: str, quality: str = None, progress_callback=None) -> IDownloadStrategy:
        """
        Returns an instance of a download strategy based on the provided strategy type.

        :param strategy_type: Type of strategy to create.
        :param link: The link to the content to be downloaded.
        :param folder: Destination folder for the download.
        :param quality: (optional) Quality of the content.
        :param progress_callback: (optional) Callback function to track download progress.
        :return: Instance of a download strategy.
        """
        if strategy_type == "video":
            return VideoDownloadStrategy(link=link, 
                                folder=folder, 
                                video_quality=quality, progress_callback=progress_callback)
        elif strategy_type == "playlist":
            return PlaylistDownloadStrategy(link=link, 
                                folder=folder, 
                                video_quality=quality,
                                progress_callback=progress_callback)
        elif strategy_type == "thumbnail":
            return ThumbnailDownloadStrategy(link, folder)
        else:
            raise ValueError(f"Strategy type '{strategy_type}' not recognized!")
