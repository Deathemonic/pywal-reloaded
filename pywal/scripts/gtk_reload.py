#!/usr/bin/env python3

try:
    import gi
    gi.require_version('Gtk', '3.0')
    from gi.repository import Gtk
except ImportError:
    print("[ERROR] gtk_reload: GTK reload requires PyGObject.")
    exit(1)


def main():
    Gtk.rc_reparse_all()


if __name__ == "__main__":
    main()
