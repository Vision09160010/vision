from pydantic import BaseModel

class NoteItem(BaseModel):
    id: str
    parent: str
    clid: str
    score: float =0.0
    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        if isinstance(other, NoteItem):
            return self.id == other.id
        return False



class FAQItem(BaseModel):
    id: str
    question: str
    answer: str
    score: float =0.0
