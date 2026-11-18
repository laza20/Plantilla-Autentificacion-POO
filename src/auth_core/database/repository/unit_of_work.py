from sqlmodel import Session


class UnitOfWork:

    def __init__(
            self, 
            session : Session):
        self.session = session

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):

        if exc_type is not None:
            self.session.rollback()
        else:
            self.session.commit()