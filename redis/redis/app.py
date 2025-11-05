from flask import Flask, render_template_string, request, redirect, url_for, flash
from datetime import datetime
import os


# GRUPO:
# Andrey de Santana
# Guilherme Iliev Santos Sobral
# Nataly Aquino
class BancoDeDados:
    def __init__(self):
        self.tarefas = {}
        self.contador_id = 0
        print("✅ Banco de dados em memória inicializado!")
    
    def gerar_id(self):
        self.contador_id += 1
        return self.contador_id
    
    def criar_tarefa(self, titulo, descricao):
        """Cria uma nova tarefa"""
        if not titulo.strip():
            raise ValueError("O título não pode estar vazio.")
        
        id_tarefa = self.gerar_id()
        self.tarefas[id_tarefa] = {
            'id': id_tarefa,
            'titulo': titulo.strip(),
            'descricao': descricao.strip(),
            'status': 'Pendente',
            'data_criacao': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'data_atualizacao': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        return id_tarefa
    
    def obter_tarefa(self, id_tarefa):
        """Obtém uma tarefa pelo ID"""
        try:
            id_tarefa = int(id_tarefa)
            if id_tarefa not in self.tarefas:
                raise KeyError("Tarefa não encontrada.")
            return self.tarefas[id_tarefa]
        except ValueError:
            raise ValueError("ID da tarefa inválido.")
    
    def listar_tarefas(self):
        """Lista todas as tarefas"""
        return sorted(self.tarefas.values(), key=lambda x: x['id'])
    
    def atualizar_tarefa(self, id_tarefa, campo, valor):
        """Atualiza uma tarefa"""
        tarefa = self.obter_tarefa(id_tarefa)
        
        campos_validos = ['titulo', 'descricao', 'status']
        if campo not in campos_validos:
            raise ValueError(f"Campo inválido. Use: {', '.join(campos_validos)}")
        
        if campo == 'titulo' and not valor.strip():
            raise ValueError("O título não pode estar vazio.")
        elif campo == 'status' and valor not in ['Pendente', 'Em Progresso', 'Concluída']:
            raise ValueError("Status inválido. Use: Pendente, Em Progresso ou Concluída")
        
        tarefa[campo] = valor.strip()
        tarefa['data_atualizacao'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return True
    
    def deletar_tarefa(self, id_tarefa):
        """Remove uma tarefa"""
        tarefa = self.obter_tarefa(id_tarefa)
        del self.tarefas[tarefa['id']]
        return True
    
    def obter_estatisticas(self):
        """Retorna estatísticas das tarefas"""
        tarefas = self.listar_tarefas()
        total = len(tarefas)
        concluidas = sum(1 for t in tarefas if t['status'] == 'Concluída')
        pendentes = sum(1 for t in tarefas if t['status'] == 'Pendente')
        em_progresso = sum(1 for t in tarefas if t['status'] == 'Em Progresso')
        
        return {
            'total': total,
            'concluidas': concluidas,
            'pendentes': pendentes,
            'em_progresso': em_progresso
        }

db = BancoDeDados()

# ============================================
# FLASK APP
# ============================================
app = Flask(__name__)
app.secret_key = 'sua-chave-super-secreta-aqui-123'

TEMPLATE_BASE = '''
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ titulo }} - Os Cabeça Grande</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            background: linear-gradient(135deg, #0c0c0c 0%, #1a1a1a 100%);
            color: #ffffff;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            min-height: 100vh;
            padding: 20px;
            line-height: 1.6;
        }

        .container {
            max-width: 1000px;
            margin: 0 auto;
            background: rgba(30, 30, 30, 0.95);
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 20px 40px rgba(255, 140, 0, 0.1);
            border: 1px solid #333;
            backdrop-filter: blur(10px);
        }

        .header {
            text-align: center;
            margin-bottom: 40px;
            padding-bottom: 20px;
            border-bottom: 2px solid #ff6b00;
        }

        h1 {
            color: #ff6b00;
            font-size: 3em;
            margin-bottom: 10px;
            text-shadow: 0 2px 10px rgba(255, 107, 0, 0.3);
        }

        h2 {
            color: #ff8c00;
            margin: 25px 0 15px 0;
            font-size: 1.8em;
        }

        h3 {
            color: #ffa733;
            margin: 20px 0 10px 0;
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 25px 0;
        }

        .stat-card {
            background: linear-gradient(135deg, #252525 0%, #1a1a1a 100%);
            padding: 20px;
            border-radius: 12px;
            text-align: center;
            border: 1px solid #444;
            transition: transform 0.3s ease;
        }

        .stat-card:hover {
            transform: translateY(-5px);
        }

        .stat-number {
            font-size: 2.5em;
            font-weight: bold;
            color: #ff8c00;
            display: block;
        }

        .stat-label {
            color: #cccccc;
            font-size: 0.9em;
        }

        .form-group {
            margin-bottom: 25px;
        }

        input, textarea, select {
            width: 100%;
            padding: 15px;
            margin: 8px 0;
            background: #2a2a2a;
            color: #ffffff;
            border: 2px solid #444;
            border-radius: 10px;
            font-size: 16px;
            transition: all 0.3s ease;
        }

        input:focus, textarea:focus, select:focus {
            outline: none;
            border-color: #ff8c00;
            box-shadow: 0 0 0 3px rgba(255, 140, 0, 0.2);
            background: #333;
        }

        textarea {
            min-height: 100px;
            resize: vertical;
        }

        .btn {
            background: linear-gradient(135deg, #ff6b00 0%, #ff8c00 100%);
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 10px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s ease;
            text-decoration: none;
            display: inline-block;
            text-align: center;
        }

        .btn:hover {
            background: linear-gradient(135deg, #ff8c00 0%, #ffa733 100%);
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(255, 140, 0, 0.4);
        }

        .btn-danger {
            background: linear-gradient(135deg, #dc3545 0%, #c82333 100%);
        }

        .btn-danger:hover {
            background: linear-gradient(135deg, #c82333 0%, #a71e2a 100%);
        }

        .btn-secondary {
            background: linear-gradient(135deg, #6c757d 0%, #5a6268 100%);
        }

        .btn-secondary:hover {
            background: linear-gradient(135deg, #5a6268 0%, #495057 100%);
        }

        .tarefas-grid {
            display: grid;
            gap: 20px;
            margin: 30px 0;
        }

        .tarefa-card {
            background: linear-gradient(135deg, #252525 0%, #1e1e1e 100%);
            padding: 25px;
            border-radius: 15px;
            border-left: 5px solid #ff8c00;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }

        .tarefa-card:hover {
            transform: translateX(10px);
            box-shadow: 0 10px 25px rgba(255, 140, 0, 0.2);
        }

        .tarefa-card.concluida {
            border-left-color: #28a745;
            opacity: 0.9;
        }

        .tarefa-card.progresso {
            border-left-color: #ffc107;
        }

        .tarefa-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 15px;
        }

        .tarefa-titulo {
            font-size: 1.4em;
            font-weight: bold;
            color: #ffa733;
            margin-right: 15px;
        }

        .tarefa-status {
            background: #333;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: bold;
            white-space: nowrap;
        }

        .status-pendente { color: #ff6b00; }
        .status-progresso { color: #ffc107; }
        .status-concluida { color: #28a745; }

        .tarefa-descricao {
            color: #cccccc;
            margin-bottom: 15px;
            line-height: 1.5;
        }

        .tarefa-meta {
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 0.85em;
            color: #888;
            margin-top: 15px;
        }

        .tarefa-acoes {
            display: flex;
            gap: 10px;
            margin-top: 15px;
        }

        .mensagem {
            padding: 15px 20px;
            border-radius: 10px;
            margin: 20px 0;
            font-weight: bold;
            border: 2px solid transparent;
        }

        .sucesso {
            background: rgba(40, 167, 69, 0.2);
            color: #28a745;
            border-color: #28a745;
        }

        .erro {
            background: rgba(220, 53, 69, 0.2);
            color: #dc3545;
            border-color: #dc3545;
        }

        .vazio {
            text-align: center;
            padding: 60px 20px;
            color: #666;
        }

        .vazio i {
            font-size: 4em;
            margin-bottom: 20px;
            display: block;
            color: #444;
        }

        .form-acoes {
            display: flex;
            gap: 10px;
            justify-content: flex-start;
            margin-top: 20px;
        }

        @media (max-width: 768px) {
            .container {
                padding: 20px;
                margin: 10px;
            }

            h1 {
                font-size: 2.2em;
            }

            .stats-grid {
                grid-template-columns: 1fr;
            }

            .tarefa-header {
                flex-direction: column;
                gap: 10px;
            }

            .tarefa-meta {
                flex-direction: column;
                gap: 5px;
                align-items: flex-start;
            }

            .tarefa-acoes {
                flex-direction: column;
            }

            .form-acoes {
                flex-direction: column;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Os Cabeça Grande</h1>
            <p>Sistema de Gerenciamento de Tarefas para o Tio Vagner</p>
        </div>

        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for categoria, mensagem in messages %}
                    <div class="mensagem {{ categoria }}">{{ mensagem }}</div>
                {% endfor %}
            {% endif %}
        {% endwith %}

        {% block conteudo %}{% endblock %}
    </div>

    <script>
        // Confirmação para deletar tarefas
        function confirmarDelecao() {
            return confirm('Tem certeza que deseja excluir esta tarefa? Esta ação não pode ser desfeita.');
        }

        // Animação para os cards
        document.addEventListener('DOMContentLoaded', function() {
            const cards = document.querySelectorAll('.tarefa-card');
            cards.forEach((card, index) => {
                card.style.animationDelay = `${index * 0.1}s`;
            });
        });
    </script>
</body>
</html>
'''

# ============================================
# ROTAS DA APLICAÇÃO (CORRIGIDAS)
# ============================================

@app.route('/')
def index():
    """Página principal com lista de tarefas"""
    try:
        tarefas = db.listar_tarefas()
        stats = db.obter_estatisticas()

        html_index = '''
        <div class="stats-grid">
            <div class="stat-card">
                <span class="stat-number">{{ stats.total }}</span>
                <span class="stat-label">Total de Tarefas</span>
            </div>
            <div class="stat-card">
                <span class="stat-number">{{ stats.pendentes }}</span>
                <span class="stat-label">Pendentes</span>
            </div>
            <div class="stat-card">
                <span class="stat-number">{{ stats.em_progresso }}</span>
                <span class="stat-label">Em Progresso</span>
            </div>
            <div class="stat-card">
                <span class="stat-number">{{ stats.concluidas }}</span>
                <span class="stat-label">Concluídas</span>
            </div>
        </div>

        <div class="form-group">
            <h2>📝 Nova Tarefa</h2>
            <form action="/criar" method="POST">
                <input type="text" name="titulo" placeholder="Digite o título da tarefa..." required maxlength="100">
                <textarea name="descricao" placeholder="Descrição detalhada da tarefa (opcional)" maxlength="500"></textarea>
                <button type="submit" class="btn">➕ Criar Tarefa</button>
            </form>
        </div>

        <div class="tarefas-lista">
            <h2>📋 Minhas Tarefas</h2>
            
            {% if tarefas %}
                <div class="tarefas-grid">
                    {% for tarefa in tarefas %}
                        <div class="tarefa-card {{ 'concluida' if tarefa.status == 'Concluída' else 'progresso' if tarefa.status == 'Em Progresso' else '' }}">
                            <div class="tarefa-header">
                                <div class="tarefa-titulo">#{{ tarefa.id }} - {{ tarefa.titulo }}</div>
                                <div class="tarefa-status status-{{ tarefa.status.lower().replace(' ', '') }}">
                                    {% if tarefa.status == 'Concluída' %}✅
                                    {% elif tarefa.status == 'Em Progresso' %}🔄
                                    {% else %}⏳{% endif %}
                                    {{ tarefa.status }}
                                </div>
                            </div>
                            
                            {% if tarefa.descricao %}
                                <div class="tarefa-descricao">{{ tarefa.descricao }}</div>
                            {% endif %}
                            
                            <div class="tarefa-meta">
                                <div>
                                    <strong>Criada:</strong> {{ tarefa.data_criacao }}
                                </div>
                                {% if tarefa.data_atualizacao != tarefa.data_criacao %}
                                <div>
                                    <strong>Atualizada:</strong> {{ tarefa.data_atualizacao }}
                                </div>
                                {% endif %}
                            </div>
                            
                            <div class="tarefa-acoes">
                                <a href="/tarefa/{{ tarefa.id }}" class="btn">👁️ Detalhes</a>
                                <a href="/deletar/{{ tarefa.id }}" class="btn btn-danger" onclick="return confirmarDelecao()">🗑️ Excluir</a>
                            </div>
                        </div>
                    {% endfor %}
                </div>
            {% else %}
                <div class="vazio">
                    <div>📝</div>
                    <h3>Nenhuma tarefa encontrada</h3>
                    <p>Crie sua primeira tarefa usando o formulário acima!</p>
                </div>
            {% endif %}
        </div>
        '''
        
        return render_template_string(TEMPLATE_BASE.replace('{% block conteudo %}{% endblock %}', html_index), 
                                    titulo="Dashboard", tarefas=tarefas, stats=stats)
    
    except Exception as e:
        error_html = "<h2>Erro</h2><p>Ocorreu um erro ao carregar as tarefas.</p>"
        return render_template_string(TEMPLATE_BASE.replace('{% block conteudo %}{% endblock %}', error_html), 
                                    titulo="Erro")

@app.route('/criar', methods=['POST'])
def criar_tarefa():
    """Cria uma nova tarefa"""
    titulo = request.form.get('titulo', '').strip()
    descricao = request.form.get('descricao', '').strip()
    
    try:
        db.criar_tarefa(titulo, descricao)
        flash("✅ Tarefa criada com sucesso!", "sucesso")
    except Exception as e:
        flash(f"❌ Erro: {str(e)}", "erro")
    
    return redirect('/')

@app.route('/tarefa/<id>')
def detalhes_tarefa(id):
    """Exibe detalhes e permite editar uma tarefa"""
    try:
        tarefa = db.obter_tarefa(id)
        
        html_detalhes = '''
        <div class="form-acoes">
            <a href="/" class="btn btn-secondary">← Voltar</a>
        </div>

        <h2>✏️ Editando Tarefa #{{ tarefa.id }}</h2>
        
        <div class="tarefa-card {{ 'concluida' if tarefa.status == 'Concluída' else 'progresso' if tarefa.status == 'Em Progresso' else '' }}" style="margin: 20px 0;">
            <div class="tarefa-meta">
                <div><strong>ID:</strong> {{ tarefa.id }}</div>
                <div><strong>Criada em:</strong> {{ tarefa.data_criacao }}</div>
                {% if tarefa.data_atualizacao != tarefa.data_criacao %}
                <div><strong>Última atualização:</strong> {{ tarefa.data_atualizacao }}</div>
                {% endif %}
            </div>
        </div>

        <form action="/atualizar/{{ tarefa.id }}" method="POST">
            <div class="form-group">
                <label><strong>📝 Título:</strong></label>
                <input type="text" name="titulo" value="{{ tarefa.titulo }}" required maxlength="100">
            </div>
            
            <div class="form-group">
                <label><strong>📋 Descrição:</strong></label>
                <textarea name="descricao" maxlength="500">{{ tarefa.descricao }}</textarea>
            </div>
            
            <div class="form-group">
                <label><strong>📊 Status:</strong></label>
                <select name="status" required>
                    <option value="Pendente" {{ 'selected' if tarefa.status == 'Pendente' }}>⏳ Pendente</option>
                    <option value="Em Progresso" {{ 'selected' if tarefa.status == 'Em Progresso' }}>🔄 Em Progresso</option>
                    <option value="Concluída" {{ 'selected' if tarefa.status == 'Concluída' }}>✅ Concluída</option>
                </select>
            </div>
            
            <div class="form-acoes">
                <button type="submit" class="btn">💾 Salvar Alterações</button>
                <a href="/" class="btn btn-secondary">❌ Cancelar</a>
            </div>
        </form>
        '''
        
        return render_template_string(TEMPLATE_BASE.replace('{% block conteudo %}{% endblock %}', html_detalhes), 
                                    titulo=f"Editar Tarefa {id}", tarefa=tarefa)
    
    except Exception as e:
        flash(f"❌ Erro: {str(e)}", "erro")
        return redirect('/')

@app.route('/atualizar/<id>', methods=['POST'])
def atualizar_tarefa(id):
    """Atualiza uma tarefa existente"""
    try:
        titulo = request.form.get('titulo', '').strip()
        descricao = request.form.get('descricao', '').strip()
        status = request.form.get('status', '').strip()
        
        db.atualizar_tarefa(id, 'titulo', titulo)
        db.atualizar_tarefa(id, 'descricao', descricao)
        db.atualizar_tarefa(id, 'status', status)
        
        flash("✅ Tarefa atualizada com sucesso!", "sucesso")
    except Exception as e:
        flash(f"❌ Erro: {str(e)}", "erro")
    
    return redirect(f'/tarefa/{id}')

@app.route('/deletar/<id>')
def deletar_tarefa(id):
    """Remove uma tarefa"""
    try:
        db.deletar_tarefa(id)
        flash("🗑️ Tarefa excluída com sucesso!", "sucesso")
    except Exception as e:
        flash(f"❌ Erro: {str(e)}", "erro")
    
    return redirect('/')

# ============================================
# INICIALIZAÇÃO DA APLICAÇÃO
# ============================================

if __name__ == '__main__':  
    
    print("🚀 Iniciando TaskMaster...")
    print("📧 Acesse: http://127.0.0.1:5000")
    app.run(debug=True, host='127.0.0.1', port=5000)