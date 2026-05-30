import ctypes
import sys
import subprocess
import tempfile
import shutil
from pathlib import Path


TASK_NAME = "TempCleaner"


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False


def request_admin():
    if getattr(sys, "frozen", False):
        file = sys.executable
        params = ""
    else:
        file = sys.executable
        params = f'"{Path(__file__).resolve()}"'

    ctypes.windll.shell32.ShellExecuteW(
        None,
        "runas",
        file,
        params,
        None,
        1
    )

    sys.exit()


def read_config():
    config_path = Path(__file__).parent / "config.txt"

    deep_clean = False
    debug = False
    auto_schedule = False

    if config_path.exists():
        text = config_path.read_text(encoding="utf-8")

        deep_clean = "deep_clean = True" in text
        debug = "debug = True" in text
        auto_schedule = "auto_schedule = True" in text

    return deep_clean, debug, auto_schedule


def create_task(deep_clean):
    if getattr(sys, "frozen", False):
        command = f'"{sys.executable}"'
    else:
        command = f'"{sys.executable}" "{Path(__file__).resolve()}"'

    args = [
        "schtasks",
        "/create",
        "/tn", TASK_NAME,
        "/tr", command,
        "/sc", "daily",
        "/mo", "3",
        "/f"
    ]

    if deep_clean:
        args += ["/rl", "HIGHEST"]

    subprocess.run(args, check=True)


def clean_folder(folder):
    folder = Path(folder)

    if not folder.exists():
        print("Cartella non trovata:", folder)
        return

    for item in folder.iterdir():
        try:
            if item.is_file() or item.is_symlink():
                item.unlink()
                print("File eliminato:", item)

            elif item.is_dir():
                shutil.rmtree(item)
                print("Cartella eliminata:", item)

        except PermissionError:
            print("Permesso negato:", item)

        except Exception as e:
            print("Saltato:", item, e)


def main():
    print("MAIN AVVIATO")
    print("ADMIN:", is_admin())
    deep_clean, debug, auto_schedule = read_config()

    if debug:
        print("EXE:", getattr(sys, "frozen", False))
        print("ADMIN:", is_admin())
        print("FILE:", Path(__file__).resolve())
        print("PYTHON/EXE:", sys.executable)
        print("DEEP CLEAN:", deep_clean)
        print("AUTO SCHEDULE:", auto_schedule)

    if deep_clean and not is_admin():
        print("Richiedo admin...")
        request_admin()
        return

    if auto_schedule:
        create_task(deep_clean)

    print("Pulizia temp utente...")
    clean_folder(tempfile.gettempdir())

    if deep_clean:
        print("Pulizia Windows Temp...")
        clean_folder(r"C:\Windows\Temp")

    print("Pulizia completata.")


if __name__ == "__main__":
    main()