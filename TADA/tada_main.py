from src.tada_ui import TadaUi

if __name__ == '__main__':
    try:
        TadaUi().mainloop()
    except Exception as e:
        print(f"{type(e)}: {e}")
        input("Press Enter to exit...")
