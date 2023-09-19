from strategies_factory import StrategyFactory

class DownloaderContext:
    def __init__(self, strategy_type: str, link: str, folder: str, quality: str = None, progress_callback=None) -> None:
        """This holds the download strategy and provides an interface to execute it.
            The context provides a consistent way to execute different strategies.
            It decouples the strategy execution from the main program."""
        self._strategy = StrategyFactory.get_strategy(strategy_type=strategy_type, 
                                              link=link, 
                                              folder=folder, 
                                              quality=quality, 
                                              progress_callback=progress_callback)

    def execute_download(self) -> None:
        """Execute the download based on the chosen strategy."""
        return self._strategy.download()