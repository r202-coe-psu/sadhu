from wtforms import widgets
from wtforms.fields import Field


class TagListField(Field):
    widget = widgets.TextInput()

    def __init__(self, label="", validators=None, remove_duplicates=True, **kwargs):
        super().__init__(label, validators, **kwargs)
        self.remove_duplicates = remove_duplicates

    def process_formdata(self, valuelist):
        if valuelist:
            self.data = [
                x.strip() for x in valuelist[0].split(",") if len(x.strip()) > 0
            ]
        else:
            self.data = []

        if self.remove_duplicates:
            self.data = list(self._remove_duplicates(self.data))

    def _value(self):
        if self.data:
            return ", ".join(self.data)
        else:
            return ""

    @classmethod
    def _remove_duplicates(cls, seq):
        """Remove duplicates in a case insensitive, but case preserving manner"""
        d = {}
        for item in seq:
            if item.lower() not in d:
                d[item.lower()] = True
                yield item


class TextListField(TagListField):
    widget = widgets.TextArea()
