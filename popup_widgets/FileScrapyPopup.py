from popup_widgets.OperationPopup import OperationPopup


class FileScrapyPopup(OperationPopup):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = '爬取视频'
