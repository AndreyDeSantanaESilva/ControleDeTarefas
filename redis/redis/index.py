import redis

def conectar_redis():
    """
    Conecta ao Redis local.
    Retorna o objeto de conexão ou None em caso de erro.
    """
    try:
        conexao = redis.Redis(
            host='localhost',   # servidor Redis local
            port=6379,          # porta padrão
            db=0,               # banco de dados 0
            decode_responses=True  # converte bytes para string automaticamente
        )
        # Testa a conexão
        if conexao.ping():
            print("✅ Conectado ao Redis com sucesso!")
        return conexao
    except redis.ConnectionError:
        print("❌ Erro: não foi possível conectar ao Redis.")
        return None

def main():
    r = conectar_redis()
    
    if r:
        # ---------------------------
        # 1️⃣ Inserindo valor simples
        # ---------------------------
        r.set("usuario:1001", "Nataly Aquino")
        print("🔹 Valor inserido:", r.get("usuario:1001"))

        # ---------------------------
        # 2️⃣ Inserindo hash (uma chave)
        # ---------------------------
        r.hset("teste:1001", "campo", "valor")
        print("🔸 Hash teste:", r.hgetall("teste:1001"))

        # ---------------------------
        # 3️⃣ Inserindo hash com múltiplos campos (forma correta)
        # ---------------------------
        r.hset("perfil:1001", mapping={
            "nome": "Nataly Aquino",
            "idade": "22",
            "email": "nataly@example.com"
        })
        print("📦 Perfil completo:", r.hgetall("perfil:1001"))

        # ---------------------------
        # 4️⃣ Listando todas as chaves
        # ---------------------------
        chaves = r.keys("*")
        print("🔑 Todas as chaves do Redis:", chaves)

        # ---------------------------
        # 5️⃣ Apagando uma chave (opcional)
        # ---------------------------
        # r.delete("teste:1001")
        # print("🗑 Chave teste:1001 deletada")

if __name__ == "__main__":
    main()
