# 📄 Termo de Homologação (UAT) - Camada Bronze

**Projeto:** Data Lake Analytics GOV  
**Fase de Entrega:** Produto 2 - Ingestão e Camada Bronze  
**Data da Homologação:** 17 de Fevereiro de 2026  

---

## 👥 Participantes da Validação
* **Líder Técnico / Engenharia de Dados:** Ediney Junior
* **Área de Negócios (Cliente):** Equipe SGP e Diretoria ENAP *(Simulação para fins de Edital)*

---

## ✅ Critérios de Aceite e Validação Técnica

Os testes de carga foram executados em ambiente controlado, validando os seguintes requisitos arquiteturais e de negócio estabelecidos no edital:

- [x] **Volumetria e Integridade:** As contagens de linhas na Camada Bronze (BigQuery) conferem com a extração dos sistemas de origem (SIAPE e ENAP). Ex: *Carga ENAP homologada com 330.972 registros mensais.*
- [x] **Conformidade LGPD:** Auditoria nos dados inseridos confirmou que a coluna `CPF` foi anonimizada via Hash SHA-256 *in-flight*, impossibilitando a identificação direta do servidor público sem a chave reversa.
- [x] **Performance e FinOps:** O pipeline demonstrou alta eficiência computacional. A carga da base consolidada da ENAP foi processada integralmente em memória RAM, registrando velocidade média de **1.612 linhas processadas por segundo**.
- [x] **Resiliência e Logs:** Simulações de falha de conexão (Erro 404) e auditoria de volumetria foram registradas corretamente no arquivo `auditoria_bronze.log`.

---

## ✍️ Assinaturas de Aprovação

Atestamos que o **Produto 2 (Protótipo Funcional de Pipeline Integrado)** atende aos requisitos técnicos e de governança. O pipeline está autorizado a seguir para a construção das Camadas Prata e Ouro (Fase 3 - Transformação via dbt).

<br>

___________________________________________________
**Ediney Junior** *Engenheiro de Dados Sênior (Tech Lead)* <br>

___________________________________________________
**Equipe SGP / Validador do Edital** *Aprovação Funcional* ```

