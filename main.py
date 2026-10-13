from studytrack.database import initialize_database
from studytrack.ui import StudyTrackApp


def main():
    initialize_database()
    app = StudyTrackApp()
    app.mainloop()


if __name__ == "__main__":
    main()