from flask import request, jsonify, render_template
from .model.models import db, Aluno, Pagamento
from datetime import datetime, timedelta

def rotas(app):
    @app.route('/')
    def Index():
        return render_template('index.html')

    @app.route('/alunos', methods=['POST'])
    def cadastrarAluno():
        data = request.get_json()
        if not data or not data.get('nome'):
            return jsonify({"erro": "Nome é obrigatório."}), 400
        
        data_matricula_str = data.get('data_Matricula')
        data_matricula = datetime.strptime(data_matricula_str, '%Y-%m-%d').date() \
                         if data_matricula_str else datetime.now().date()

        novoAluno = Aluno(
            Nome=data['nome'],
            Endereco=data.get('endereco'),
            Cidade=data.get('cidade'), 
            Estado=data.get('uf'),
            Telefone=data.get('telefone'),
            Data_Matricula=data_matricula,
            Data_Desligamento=datetime.strptime(data['data_Desligamento'], '%Y-%m-%d').date() if data.get('data_Desligamento') else None
        )
        if novoAluno.Data_Matricula:
            novoAluno.Data_Vencimento = novoAluno.Data_Matricula + timedelta(days=30)

        db.session.add(novoAluno)
        db.session.commit()
        return jsonify({"mensagem": "Aluno criado com sucesso!", "id": novoAluno.ID_Aluno}), 201

    @app.route('/alunos', methods=['GET'])
    def listarAlunos():
        alunos = Aluno.query.all()
        saida = []
        for aluno in alunos:
            saida.append({
                'idAluno': aluno.ID_Aluno,
                'nome': aluno.Nome,
                'endereco': aluno.Endereco,
                'cidade': aluno.Cidade,
                'uf': aluno.Estado,
                'telefone': aluno.Telefone,
                'dataMatricula': aluno.Data_Matricula.strftime('%Y-%m-%d') if aluno.Data_Matricula else None,
                'dataDesligamento': aluno.Data_Desligamento.strftime('%Y-%m-%d') if aluno.Data_Desligamento else None,
                'dataVencimento': aluno.Data_Vencimento.strftime('%Y-%m-%d') if aluno.Data_Vencimento else None,
                'ativo': aluno.alunoAtivo
            })
        return jsonify(saida)

    @app.route('/alunos/<int:aluno_id>', methods=['GET'])
    def buscarAluno(aluno_id):
        aluno = Aluno.query.get(aluno_id)
        if aluno is None:
            return jsonify({"erro": "Aluno não encontrado."}), 404
        
        return jsonify({
            'idAluno': aluno.ID_Aluno,
            'nome': aluno.Nome,
            'endereco': aluno.Endereco,
            'cidade': aluno.Cidade,
            'uf': aluno.Estado,
            'telefone': aluno.Telefone,
            'dataMatricula': aluno.Data_Matricula.strftime('%Y-%m-%d') if aluno.Data_Matricula else None,
            'dataDesligamento': aluno.Data_Desligamento.strftime('%Y-%m-%d') if aluno.Data_Desligamento else None,
            'dataVencimento': aluno.Data_Vencimento.strftime('%Y-%m-%d') if aluno.Data_Vencimento else None,
            'ativo': aluno.alunoAtivo
        })

    @app.route('/alunos/<int:aluno_id>', methods=['PUT'])
    def atualizarAluno(aluno_id):
        aluno = Aluno.query.get(aluno_id)
        if aluno is None:
            return jsonify({"erro": "Aluno não encontrado."}), 404
        
        data = request.get_json()

        aluno.Nome = data.get('nome', aluno.Nome)
        aluno.Endereco = data.get('endereco', aluno.Endereco)
        aluno.Cidade = data.get('cidade', aluno.Cidade)
        aluno.Estado = data.get('uf', aluno.Estado)
        aluno.Telefone = data.get('telefone', aluno.Telefone)


        if 'data_Desligamento' in data:
            aluno.Data_Desligamento = datetime.strptime(data['data_Desligamento'], '%Y-%m-%d').date() if data['data_Desligamento'] else None
            if aluno.Data_Desligamento and aluno.Data_Matricula and not aluno.alunoAtivo:
                aluno.Data_Vencimento = aluno.Data_Desligamento

        db.session.commit()
        return jsonify({"mensagem": "Dados do aluno atualizados com sucesso!"})

    @app.route('/alunos/<int:aluno_id>', methods=['DELETE'])
    def deletarAluno(aluno_id):
        aluno = Aluno.query.get(aluno_id)
        if aluno is None:
            return jsonify({"erro": "Aluno não encontrado."}), 404
        if aluno.alunoAtivo:
            return jsonify({"erro": "Aluno ativo não pode ser removido."}), 400
        if not aluno.Data_Desligamento:
            return jsonify({"erro": "Aluno ativo não pode ser removido."}), 400

        db.session.delete(aluno)
        db.session.commit()
        return jsonify({"mensagem": "Aluno removido com sucesso!"})

    @app.route('/pagamentos', methods=['GET'])
    def mostrarTodosPagamentos():
        pagamentos = Pagamento.query.all()
        saida = []
        for pagamento in pagamentos:
            saida.append({
                'idPagamento': pagamento.ID_Pagamento,
                'idAluno': pagamento.ID_Aluno,
                'data': pagamento.Data.strftime('%Y-%m-%d'),
                'valor': pagamento.Valor,
                'tipo': pagamento.Tipo
            })
        return jsonify(saida)

    @app.route('/pagamentos', methods=['POST'])
    def registrarPagamento():
        data = request.get_json()
        if not data or not all(k in data for k in ('idAluno', 'valor', 'tipo')):
            return jsonify({"erro": "Dados de pagamento incompletos (idAluno, valor, tipo são obrigatórios).", "dados_recebidos": data}), 400

        if data['tipo'] not in ['dinheiro', 'cartão']:
            return jsonify({"erro": "Tipo de pagamento inválido. Deve ser 'dinheiro' ou 'cartão'."}), 400

        aluno = Aluno.query.get(data['idAluno'])
        if not aluno:
            return jsonify({"erro": "Aluno não encontrado."}), 404

        data_Pagamento = datetime.strptime(data['data'], '%Y-%m-%d').date() if data.get('data') else datetime().date()

        novoPagamento = Pagamento(
            ID_Aluno=data['idAluno'],
            Valor=data['valor'],
            Tipo=data['tipo'],
            Data=data_Pagamento
        )
        db.session.add(novoPagamento)
        db.session.commit()
        return jsonify({"mensagem": "Pagamento registrado com sucesso!", "id": novoPagamento.ID_Pagamento}), 201

    @app.route('/pagamentos/<int:pagamento_id>', methods=['DELETE'])
    def deletarPagamento(pagamento_id):
        pagamento = Pagamento.query.get(pagamento_id)
        if pagamento is None:
            return jsonify({"erro": "Pagamento não encontrado."}), 404
        
        db.session.delete(pagamento)
        db.session.commit()
        return jsonify({"mensagem": "Pagamento excluído com sucesso!"})