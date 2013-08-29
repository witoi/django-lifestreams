
class BasePlugin(object):
    def __init__(self, feed):
        self.feed = feed

    def update(self):
        handler = self.get_handler()
        for item in handler.update(**self.get_update_kwargs()):
            self.create_item(item)
        return self

    def get_handler(self):
        raise NotImplementedError("Subclassing BasePlugin must implement get_handler method.")

    def create_item(self, item):
        raise NotImplementedError("Subclassing BasePlugin must implement create_item method.")

    def get_update_kwargs(self):
        raise NotImplementedError("Subclassing BasePlugin must implement get_update_kwargs method.")