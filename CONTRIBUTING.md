# 🤝 Políticas de Versionamento e Contribuição

Este documento estabelece as diretrizes de versionamento de código, ramificação (branching) e fluxo de trabalho para o desenvolvimento contínuo do **Data Lake Analytics GOV**, em conformidade com as exigências do Produto 2.

---

## 🌳 1. Estratégia de Branches (Ramificações)

Adotamos um fluxo simplificado baseado no **GitHub Flow**, garantindo agilidade e proteção ao código em produção:

* **`main`**: É a branch principal e protegida. Reflete o código que está em produção (Camadas Bronze, Prata e Ouro funcionais).
* **`feature/nome-da-feature`**: Branches criadas a partir da `main` para desenvolver novas funcionalidades (Ex: `feature/ingestao-sgp`, `feature/dbt-modelagem-ouro`).
* **`bugfix/nome-do-bug`**: Branches criadas para corrigir erros em produção (Ex: `bugfix/erro-divisao-zero-siape`).

Nenhum commit direto deve ser feito na `main` durante fases críticas. Todo código deve passar por um processo de *Pull Request (PR)*.

---

## 💬 2. Padrão de Commits (Conventional Commits)

O histórico de versionamento do projeto segue a especificação rigorosa do [Conventional Commits](https://www.conventionalcommits.org/). As mensagens de commit devem ser claras, no tempo imperativo, e usar os seguintes prefixos estruturais:

| Prefixo | Quando usar? | Exemplo |
| :--- | :--- | :--- |
| `feat:` | Adição de uma nova funcionalidade, script ou modelo dbt. | `feat: adiciona script de ingestao do SIAPE` |
| `fix:` | Resolução de um bug ou erro no código. | `fix: corrige divisao por zero no calculo de performance` |
| `docs:` | Criação ou alteração de documentação (Markdown, Dicionários). | `docs: cria termo de homologacao UAT da camada bronze` |
| `refactor:` | Mudança no código que não adiciona feature nem corrige bug (melhoria estrutural). | `refactor: otimiza loop de leitura do arquivo .zip em memoria` |
| `chore:` | Atualização de tarefas de build, configuração de pacotes (pip), etc. | `chore: instala pacote dbt-bigquery` |

---

## 🔄 3. Fluxo de Entrega (CI/CD Simulado)

1. O Engenheiro atualiza o repositório local (`git pull`).
2. Cria uma nova branch para a sua tarefa (`git checkout -b feature/nova-tarefa`).
3. Desenvolve o código Python ou SQL (dbt).
4. Realiza os commits semânticos (`git commit -m "feat: sua mensagem"`).
5. Sobe a branch para o repositório remoto (`git push origin feature/nova-tarefa`).
6. Abre um *Pull Request* para revisão do Líder Técnico antes do *merge* na branch `main`.