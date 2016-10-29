class Table:

    def __init__(self):
        self.title = None
        self.headings = []
        self.rows = []
        self._longest = {}

    def set_title(self, title: str):
        self.title = title

    def set_headings(self, *headings):
        self.headings = headings
        self._update_longest(headings)

    def add_row(self, *cols, **kwargs):
        """
        Adds a row to the table

        :param cols: The columns to add to the row
        """

        self._update_longest(cols)

        row = Row()

        # Adding columns to row
        for col in cols:

            # Adding column to row
            if type(col) is Column:
                row.add_column(col)
            else:
                row.add_column(Column(col, 0))

        if not 'index' in kwargs:
            self.rows.append(row)
        else:
            self.rows.insert(kwargs['index'], row)

    def _update_longest(self, array):
        """
        Updates max column length
        :param array: The columns
        """

        for i, e in enumerate(array):
            length = len(e)

            # Replacing longest
            if not self._longest.get(i) or self._longest[i] < length:
                self._longest[i] = length

    def __str__(self):
        total_length = sum(self._longest.values()) + len(self._longest) * 3 + 2
        table = '.'.ljust(total_length - 2, '-') + '.\n'

        # Printing title if there is one
        if self.title:
            table += '| %s |\n' % self.title.center(total_length - 5)
            table += '|'.ljust(total_length - 2, '-') + '|\n'

        # Printing headings if there is some
        if self.headings:
            for i, heading in enumerate(self.headings):
                table += '| %s ' % heading.center(self._longest[i])

                if i == len(self.headings) - 1:
                    table += '|\n'
                    table += '|'.ljust(total_length - 2, '-') + '|\n'

        # Printing rows
        if self.rows:
            for row in self.rows:
                for i, col in enumerate(row.columns):
                    table += '| %s ' % col.to_s(self._longest[i])

                table += '|\n'

        table += "'".ljust(total_length - 2, '-') + "'"
        return table


class Row:

    def __init__(self, **kwargs):
        self.columns = kwargs.get('columns') or []

    def __len__(self):
        return len(self.columns)

    def add_column(self, col):
        self.columns.append(col)


class Column:

    def __init__(self, text, alignment=0):
        self.text = str(text)
        self.alignment = alignment

    def to_s(self, length: int):
        if self.alignment == 0:
            return self.text.ljust(length)
        elif self.alignment == 1:
            return self.text.center(length)
        else:
            return self.text.rjust(length)

    def __len__(self):
        return len(self.text)

    def __str__(self):
        return self.text