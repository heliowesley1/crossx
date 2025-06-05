from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Aluno(db.Model):
    __tablename__ = 'alunos'
    ID_Aluno = db.Column(db.Integer, primary_key=True)
    Nome = db.Column(db.String(100), nullable=False)
    Endereco = db.Column(db.String(200))
    Cidade = db.Column(db.String(100))
    Estado = db.Column(db.String(2))
    Telefone = db.Column(db.String(20))
    Data_Matricula = db.Column(db.Date)
    Data_Desligamento = db.Column(db.Date)
    Data_Vencimento = db.Column(db.Date)

    pagamentos = db.relationship('Pagamento', backref='aluno', lazy=True, cascade="all, delete-orphan")

    @property #decorador que transforma metodo em atributo
    def alunoAtivo(self):
        if self.Data_Matricula and not self.Data_Desligamento:
            if self.Data_Vencimento and self.Data_Matricula < self.Data_Vencimento:
                return True
        return False

class Pagamento(db.Model):
    __tablename__ = 'pagamentos'
    ID_Pagamento = db.Column(db.Integer, primary_key=True)
    ID_Aluno = db.Column(db.Integer, db.ForeignKey('alunos.ID_Aluno'), nullable=False)
    Data = db.Column(db.Date, nullable=False, default=datetime)
    Valor = db.Column(db.Float, nullable=False)
    Tipo = db.Column(db.String(50), nullable=False)
