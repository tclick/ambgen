"""Command-line interface."""
import click


@click.command()
@click.version_option()
def main() -> None:
    """Amber Generator."""


if __name__ == "__main__":
    main(prog_name="ambgen")  # pragma: no cover
