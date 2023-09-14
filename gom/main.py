import click
import pynvml
import time
import sys
from utils import show_table

pynvml.nvmlInit()

@click.group()
@click.version_option("0.2.0", prog_name="gom")
def main():
    pass

@click.command(help="Show GPU usage")
def show():
    show_table()

@click.command(help="Watch GPU usage")
def watch():
    while True:
        show_table(watch=True)
        time.sleep(1)
    

main.add_command(show)
main.add_command(watch)

if __name__ == "__main__":
    main()

pynvml.nvmlShutdown()