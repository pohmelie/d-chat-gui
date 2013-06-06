class RichText():
    def __init__(self, form, plain_form):
        self.form = form
        self.plain_form = plain_form

    def apply(self, **values):
        return str.format(self.form, **values), str.format(self.plain_form, **values)

class RichTextStorage():
    def __init__(self, **defaults):
        self.rt = {}
        self.default = defaults

    def add_default(self, **values):
        self.default.update(values)

    def add_tag(self, tag, form, plain_form):
        self.rt[tag] = RichText(form, plain_form)

    def get(self, tag, **values):
        if tag in self.rt:
            v = self.default.copy()
            v.update(values)
            return self.rt[tag].apply(**v)


if __name__ == "__main__":
    rt = RichTextStorage(time_color="#00ff00")
    rt.add_tag("time", "<color={time_color}>[{time_value}]</color>", "[{time_value}]")

    print(rt.get("time", time_value="23:59:59"))
    print(rt.get("time", time_color="#ffffff", time_value="23:59:59"))
