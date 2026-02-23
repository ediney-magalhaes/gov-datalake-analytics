# Políticas de Versionamento e Contribuição

Este documento estabelece as diretrizes de versionamento de código, ramificação (branching) e fluxo de trabalho para o desenvolvimento contínuo do **Data Lake Analytics GOV**, em conformidade com as exigências de Governança e Qualidade do Produto 2.

---

## 1. Estratégia de Branches (Ramificações)

Adotamos um fluxo simplificado baseado no **GitHub Flow**, garantindo agilidade e proteção ao código em produção:

* **`main`**: É a branch principal e protegida. Reflete o código homologado que está em produção (Camadas Bronze, Prata e Ouro funcionais).
* **`feature/nome-da-feature`**: Branches criadas a partir da `main` para desenvolver novas funcionalidades ou modelos de dados (Ex: `feature/ingestao-remuneracao`, `feature/stg-siape`).
* **`bugfix/nome-do-bug`**: Branches criadas para corrigir erros em produção (Ex: `bugfix/erro-tipagem-cpf`).

Todo código desenvolvido deve passar por revisão antes de ser integrado (merged) à branch `main`.

---

## 2. Padrão de Commits (Conventional Commits)

O histórico de versionamento do projeto segue a especificação rigorosa do [Conventional Commits](https://www.conventionalcommits.org/). As mensagens de commit devem ser claras, no tempo imperativo, e usar os seguintes prefixos estruturais:

| Prefixo | Quando usar? | Exemplo |
| :--- | :--- | :--- |
| `feat:` | Adição de uma nova funcionalidade, script Python ou modelo SQL (dbt). | `feat: cria modelo stg_siape_ativos na camada prata` |
| `fix:` | Resolução de um bug ou erro no código. | `fix: aplica regex para limpar caracteres especiais no header` |
| `docs:` | Criação ou alteração de documentação (Markdown, YML do dbt). | `docs: atualiza schema.yml com descricoes das colunas` |
| `refactor:` | Mudança no código que não adiciona feature nem corrige bug. | `refactor: otimiza loop de leitura do arquivo .zip em memoria` |
| `test:` | Adição ou correção de testes de qualidade de dados. | `test: adiciona teste de unicidade e not_null para CPF` |
| `chore:` | Atualização de tarefas de build, configuração ou dependências. | `chore: configura profiles.yml para o ambiente de dev` |

---

## 3. Fluxo de Entrega e CI/CD

O fluxo de trabalho foi desenhado para futura integração contínua (CI):

1. O Engenheiro atualiza o repositório local (`git pull`).
2. Cria uma nova branch para a sua tarefa (`git checkout -b feature/nova-tarefa`).
3. Desenvolve o código (Python para Ingestão ou SQL para dbt).
4. Realiza os commits semânticos (`git commit -m "feat: sua mensagem"`).
5. Envia a branch para o repositório remoto (`git push origin feature/nova-tarefa`).
6. Abre um *Pull Request* (PR) para revisão e execução dos pipelines de teste.

---

## 4. Definition of Done (DoD) - Critérios de Aceite

Antes de considerar uma entrega concluída ou abrir um Pull Request, o desenvolvedor deve garantir que os seguintes critérios foram atendidos:

- [ ] O código executa localmente sem erros.
- [ ] Logs estruturados de auditoria estão ativos e operantes (Camada Bronze).
- [ ] Nenhum dado sensível ou credencial (ex: `service_account.json`) foi commitado.
- [ ] **Os testes de qualidade do dbt (`dbt test`) foram executados e aprovados.**
- [ ] **A documentação do modelo (dicionário de dados) foi atualizada no arquivo `schema.yml`.**
- [ ] As mensagens de commit seguem o padrão *Conventional Commits*.
- [ ] dbt docs generate executado (quando alterar models/schema.yml)