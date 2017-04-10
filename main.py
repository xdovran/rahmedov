import sys
import argparse

from PyQt5.QtWidgets import QApplication
from gui.gui import Gui

app = QApplication(sys.argv)
app.setOrganizationDomain('rahmedov.com')
app.setObjectName('rahmedov')
app.setApplicationName('rahmedov')
app.setApplicationVersion('0.0.0')

parser = argparse.ArgumentParser(description='Home')
parser.add_argument('-r', '--root', type=str, default='', help='''Root Path''')

args = parser.parse_args()

g = Gui(root=args.root, parent=None)

g.show()
sys.exit(app.exec_())
