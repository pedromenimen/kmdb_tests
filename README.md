Para usar os testes basta colocar a pasta tests na raiz do projeto do dev e rodar os seguintes comandos
- pip install faker
- ./manage.py test tests/T1 (para os testes da tarefa 1, T2 para os testes da tarefa 2 e assim segue até T5)
Alguns devs não utilizam os recursos automáticos do django ou do rest framework, então algumas mensagens nas responses das rotas devem estar diferentes das mensagens do canvas. Caso algum dev tenha pré populado alguma tabela nas migrations alguns testes podem falhar. Corrigir imports conforme arquivos do dev.
