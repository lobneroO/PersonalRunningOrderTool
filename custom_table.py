# Personal Running Order Tool
# Copyright (C) 2022  Tim Lobner
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from tkintertable import TableCanvas, TableModel


class CustomTable(TableCanvas):

    def delete_cells_no_interaction(self, rows, cols):
        """Clear the cell contents without a message box"""

        for col in cols:
            for row in rows:
                self.model.deleteCellRecord(row, col)
                self.redrawCell(row, col)

    def clear_data_no_interaction(self):
        """Delete cells from gui event without a message box"""

        rows = self.multiplerowlist
        cols = self.multiplecollist
        self.delete_cells_no_interaction(rows, cols)
