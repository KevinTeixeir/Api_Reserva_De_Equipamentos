# API de Reserva de Equipamentos

## Descrição do Domínio

A API de Reserva de Equipamentos é um sistema para gerenciamento de empréstimos e reservas de recursos compartilhados, como notebooks, projetores e câmeras.

O objetivo é garantir o controle da disponibilidade dos equipamentos, evitar conflitos de horários, gerenciar manutenções e manter um histórico das alterações de estado das reservas.

O sistema foi desenvolvido utilizando FastAPI, SQLAlchemy, PostgreSQL e Docker.

---

## Entidades do Sistema

* **User:** usuário responsável pelas reservas.
* **Equipment:** equipamento disponível para empréstimo.
* **Reservation:** reserva realizada por um usuário.
* **Maintenance:** períodos de manutenção de equipamentos.
* **ReservationHistory:** histórico de alterações de status das reservas.

---

## Diagrama ER

```text
User (1) -------- (N) Reservation (N) -------- (1) Equipment
                              |
                              |
                              (1)
                              |
                              (N)
                    ReservationHistory

Equipment (1) ---- (N) Maintenance
```

---

## Estados da Reserva

```text
DRAFT → CONFIRMED → IN_USE → COMPLETED

DRAFT → CANCELED

CONFIRMED → CANCELED
```

Estados terminais:

* COMPLETED
* CANCELED

Não é permitido retornar de estados terminais.



## Regras de Negócio

# Regras de Negócio

## RN-001 — Reserva não pode sobrepor horários

| Campo             | Descrição                                                                                                            |
| ----------------- | -------------------------------------------------------------------------------------------------------------------- |
| **Identificador** | RN-001                                                                                                               |
| **Nome**          | Reserva não pode sobrepor horários                                                                                   |
| **Gatilho**       | Ao criar uma reserva                                                                                                 |
| **Pré-condição**  | O equipamento deve existir e estar disponível para reserva                                                           |
| **Ação**          | O sistema deve verificar se já existe uma reserva confirmada ou em uso para o mesmo equipamento no período informado |
| **Violação**      | HTTP 409 — `RESERVATION_CONFLICT`                                                                                    |

**Payload de erro:**

```json
{
  "error": "RESERVATION_CONFLICT",
  "message": "Já existe uma reserva para este equipamento no período solicitado.",
  "details": {
    "equipment_id": 10,
    "conflicting_reservation_id": 42
  }
}
```

---

## RN-002 — Equipamento em manutenção não pode ser reservado

| Campo             | Descrição                                                                                      |
| ----------------- | ---------------------------------------------------------------------------------------------- |
| **Identificador** | RN-002                                                                                         |
| **Nome**          | Equipamento em manutenção não pode ser reservado                                               |
| **Gatilho**       | Ao criar uma reserva                                                                           |
| **Pré-condição**  | O equipamento deve possuir status `available` e não ter manutenção ativa no período solicitado |
| **Ação**          | O sistema deve impedir a criação da reserva                                                    |
| **Violação**      | HTTP 409 — `EQUIPMENT_UNAVAILABLE`                                                             |

**Payload de erro:**

```json
{
  "error": "EQUIPMENT_UNAVAILABLE",
  "message": "O equipamento não está disponível para reserva.",
  "details": {
    "equipment_id": 10,
    "current_status": "maintenance"
  }
}
```

---

## RN-003 — Usuário suspenso não pode criar reservas

| Campo             | Descrição                                                           |
| ----------------- | ------------------------------------------------------------------- |
| **Identificador** | RN-003                                                              |
| **Nome**          | Usuário suspenso não pode criar reservas                            |
| **Gatilho**       | Ao criar uma reserva                                                |
| **Pré-condição**  | O usuário deve possuir status `active`                              |
| **Ação**          | O sistema deve validar o status do usuário antes de criar a reserva |
| **Violação**      | HTTP 403 — `USER_SUSPENDED`                                         |

**Payload de erro:**

```json
{
  "error": "USER_SUSPENDED",
  "message": "Usuário suspenso não pode criar reservas.",
  "details": {
    "user_id": 5
  }
}
```

---

## RN-004 — Usuário não pode possuir mais de três reservas futuras ativas

| Campo             | Descrição                                                                               |
| ----------------- | --------------------------------------------------------------------------------------- |
| **Identificador** | RN-004                                                                                  |
| **Nome**          | Limite de reservas futuras                                                              |
| **Gatilho**       | Ao criar uma reserva                                                                    |
| **Pré-condição**  | O usuário deve possuir menos de três reservas futuras com status `draft` ou `confirmed` |
| **Ação**          | O sistema deve contar as reservas futuras do usuário antes de criar uma nova reserva    |
| **Violação**      | HTTP 409 — `RESERVATION_LIMIT_EXCEEDED`                                                 |

**Payload de erro:**

```json
{
  "error": "RESERVATION_LIMIT_EXCEEDED",
  "message": "Usuário atingiu o limite de reservas futuras.",
  "details": {
    "user_id": 5,
    "current_reservations": 3
  }
}
```

---

## RN-005 — Transições de estado devem ser válidas

| Campo             | Descrição                                                                   |
| ----------------- | --------------------------------------------------------------------------- |
| **Identificador** | RN-005                                                                      |
| **Nome**          | Validação de transições de estado                                           |
| **Gatilho**       | Ao alterar o status de uma reserva                                          |
| **Pré-condição**  | A transição solicitada deve estar definida na máquina de estados da reserva |
| **Ação**          | O sistema deve permitir apenas transições válidas entre estados             |
| **Violação**      | HTTP 422 — `INVALID_STATUS_TRANSITION`                                      |

**Payload de erro:**

```json
{
  "error": "INVALID_STATUS_TRANSITION",
  "message": "A transição de estado solicitada não é permitida.",
  "details": {
    "current_status": "draft",
    "requested_status": "completed"
  }
}
```

---

## RN-006 — Reservas em estado terminal não podem ser alteradas

| Campo             | Descrição                                                     |
| ----------------- | ------------------------------------------------------------- |
| **Identificador** | RN-006                                                        |
| **Nome**          | Bloqueio de alteração em estado terminal                      |
| **Gatilho**       | Ao atualizar uma reserva                                      |
| **Pré-condição**  | A reserva não pode estar com status `completed` ou `canceled` |
| **Ação**          | O sistema deve bloquear qualquer alteração na reserva         |
| **Violação**      | HTTP 409 — `TERMINAL_STATE`                                   |

**Payload de erro:**

```json
{
  "error": "TERMINAL_STATE",
  "message": "Não é possível alterar uma reserva finalizada.",
  "details": {
    "reservation_id": 15,
    "current_status": "completed"
  }
}
```



## Decisões de Design

### Arquitetura em camadas

O projeto foi dividido em:

* Routers
* Services
* Repositories
* Models
* Schemas

Essa abordagem promove separação de responsabilidades e facilita manutenção e testes.

### Regras de negócio na camada de serviço

Toda a lógica de negócio foi implementada na camada de serviços, mantendo os routers responsáveis apenas pela orquestração das requisições.

## Por que os relacionamentos foram modelados dessa forma e não de outra?

Os relacionamentos do sistema foram definidos com base nas regras de negócio do domínio de reserva de equipamentos, buscando garantir consistência, rastreabilidade e normalização dos dados.

#### Usuário → Reserva (1:N)

O relacionamento entre Usuário e Reserva foi modelado como um para muitos, pois um mesmo usuário pode realizar diversas reservas ao longo do tempo, enquanto cada reserva pertence exclusivamente a um único usuário.

A utilização de um relacionamento N:N não seria adequada, pois uma reserva não pode ser compartilhada por múltiplos usuários.

---

#### Equipamento → Reserva (1:N)

O relacionamento entre Equipamento e Reserva também foi modelado como um para muitos. Um equipamento pode ser reservado inúmeras vezes em períodos diferentes, mas cada reserva está associada a apenas um equipamento.

Essa modelagem simplifica a verificação de conflitos de horário e permite controlar a disponibilidade de cada recurso individualmente.

---

#### Equipamento → Manutenção (1:N)

O relacionamento entre Equipamento e Manutenção foi modelado como um para muitos porque um equipamento pode passar por diversas manutenções ao longo do seu ciclo de vida.

Cada registro de manutenção representa um período específico de indisponibilidade e pertence a um único equipamento.

Separar a manutenção em uma entidade própria evita a duplicação de dados e permite preservar o histórico completo de intervenções realizadas.

---

#### Reserva → Histórico de Reserva (1:N)

O relacionamento entre Reserva e Histórico de Reserva foi modelado como um para muitos para garantir auditoria e rastreabilidade das mudanças de estado.

Uma reserva pode passar por diversas transições ao longo do seu ciclo de vida, como:

* `draft → confirmed`
* `confirmed → in_use`
* `in_use → completed`

Cada alteração gera um novo registro no histórico, permitindo identificar quando e como a reserva evoluiu.

Armazenar apenas o status atual na tabela de reservas não seria suficiente para atender aos requisitos de auditoria e rastreabilidade.

---

### Justificativa da modelagem adotada

A modelagem escolhida segue os princípios de normalização e separação de responsabilidades, proporcionando os seguintes benefícios:

* redução da redundância de dados;
* manutenção da integridade referencial;
* facilidade de implementação das regras de negócio;
* rastreabilidade das mudanças de estado;
* melhor desempenho nas consultas relacionadas a reservas e disponibilidade de equipamentos;
* maior facilidade para evolução futura do sistema.

### Por que determinadas regras foram implementadas no Pydantic e outras na camada de serviço?

A separação entre validações no Pydantic e regras de negócio na camada de serviço foi definida com base no princípio da responsabilidade única.

Validações implementadas no Pydantic

O Pydantic foi utilizado para validar informações que dependem exclusivamente dos dados enviados na requisição, sem necessidade de consultar o banco de dados ou acessar outras entidades.

Essas validações ocorrem antes da execução da lógica de negócio e garantem que apenas dados estruturalmente válidos sejam processados pela aplicação.

Exemplos implementados:

verificação de campos obrigatórios;
validação de formato de e-mail;
tamanho mínimo e máximo de textos;
validação de que end_date seja posterior a start_date.

Exemplo:

@model_validator(mode="after")
def validate_dates(self):
    if self.end_date <= self.start_date:
        raise ValueError(
            "end_date must be greater than start_date"
        )

    return self

Essa regra foi implementada no Pydantic porque depende apenas dos valores presentes na própria requisição.

Regras implementadas na camada de serviço

A camada de serviço foi utilizada para implementar regras que dependem de consultas ao banco de dados, do estado de outras entidades ou do contexto atual do sistema.

Essas regras exigem acesso a informações que não estão disponíveis apenas nos dados enviados pelo cliente.

Exemplos implementados:

verificar se o usuário está suspenso;
verificar se o equipamento está disponível;
verificar se existe manutenção ativa no período solicitado;
identificar conflitos entre reservas;
limitar a quantidade de reservas futuras por usuário;
validar transições de estado;
impedir alterações em reservas com estado terminal.

Exemplo:

conflict = self.repository.find_conflicting_reservation(
    db,
    data.equipment_id,
    data.start_date,
    data.end_date,
)

if conflict:
    raise BusinessException(
        error="RESERVATION_CONFLICT",
        message="Já existe uma reserva para este período.",
        status_code=409,
    )

Essa regra foi implementada na camada de serviço porque exige consulta ao 
banco de dados e depende do estado atual das reservas existentes.

Justificativa da separação

A separação entre Pydantic e camada de serviço oferece os seguintes benefícios:

evita duplicação de regras de negócio;
mantém os schemas simples e focados na validação estrutural dos dados;
centraliza a lógica de negócio em um único local;
facilita a manutenção e evolução do sistema;
aumenta a reutilização das regras em diferentes endpoints;
melhora a testabilidade da aplicação.

Dessa forma, o Pydantic atua como a primeira barreira de validação, enquanto a camada de serviço é responsável por garantir 
a consistência do domínio e aplicar as regras de negócio.
---
### Por que a Migration 2 foi necessária? O que mudou no entendimento do domínio?

A Migration 2 foi criada para adicionar o índice composto idx_reservation_period na tabela reservations, utilizando os campos equipment_id, start_date e end_date.

Durante a modelagem inicial do sistema, o foco estava na implementação das funcionalidades essenciais do domínio, como cadastro de usuários, equipamentos, reservas e manutenções.

No entanto, ao implementar a regra de negócio RN-001 — Reserva não pode sobrepor horários, observou-se que a verificação de conflitos de reserva é uma das operações mais críticas e frequentes do sistema.

Para cada nova reserva, a aplicação precisa executar uma consulta semelhante à seguinte:

SELECT *
FROM reservations
WHERE equipment_id = ?
AND start_date < :end_date
AND end_date > :start_date;

Inicialmente, essa consulta era executada sem um índice específico. Embora isso seja suficiente para um volume reduzido de dados, o desempenho tende a degradar à medida que a quantidade de reservas cresce.

O entendimento do domínio evoluiu ao perceber que o sistema não precisava apenas garantir a consistência das regras de negócio, mas também manter um desempenho adequado em cenários com grande volume de reservas.

Por esse motivo, foi criada a Migration 2 para adicionar um índice composto otimizado para a consulta de conflitos de horário.

Essa decisão trouxe os seguintes benefícios:

redução do tempo de busca por reservas conflitantes;
melhoria do desempenho das operações de criação de reservas;
maior escalabilidade do sistema;
menor consumo de recursos do banco de dados;
adequação da estrutura de dados ao padrão real de uso da aplicação.

A Migration 2 representa uma evolução do entendimento do domínio, demonstrando que as decisões de modelagem de banco de dados podem ser ajustadas conforme novos requisitos funcionais e não funcionais são identificados.
---

### Qual seria o comportamento correto se dois usuários tentassem modificar o mesmo recurso simultaneamente?

No domínio de reserva de equipamentos, o principal cenário de concorrência ocorre quando dois usuários tentam criar uma reserva para o mesmo equipamento em períodos iguais ou sobrepostos.

Sem um mecanismo de controle de concorrência, ambas as operações poderiam validar a disponibilidade do equipamento ao mesmo tempo e criar reservas conflitantes, gerando inconsistência nos dados.

Para evitar esse problema, foi implementado um mecanismo de bloqueio pessimista utilizando SELECT FOR UPDATE.

Durante o processo de criação da reserva, o sistema bloqueia temporariamente o registro do equipamento antes de executar as validações de disponibilidade.

Exemplo simplificado da implementação:

equipment = (
    db.query(Equipment)
    .filter(Equipment.id == equipment_id)
    .with_for_update()
    .first()
)

Enquanto a primeira transação estiver em andamento, outras transações que tentarem acessar o mesmo equipamento para reserva deverão aguardar a liberação do bloqueio.

O fluxo ocorre da seguinte forma:

O usuário A solicita uma reserva para o equipamento.
O sistema bloqueia o registro do equipamento.
O usuário B tenta reservar o mesmo equipamento simultaneamente.
A transação do usuário B fica em espera.
O sistema conclui a reserva do usuário A e libera o bloqueio.
O sistema reavalia a solicitação do usuário B.
Caso exista conflito de horário, a operação é rejeitada com erro RESERVATION_CONFLICT.

Essa estratégia garante que apenas uma transação possa modificar o recurso por vez, eliminando condições de corrida e preservando a consistência dos dados.

A escolha pelo bloqueio pessimista foi adequada porque a operação de reserva envolve um recurso compartilhado e possui alta sensibilidade a conflitos.

Como alternativa, poderia ser utilizado o bloqueio otimista com controle de versão, porém essa abordagem exigiria tratamento adicional de conflitos e reprocessamento das transações.

Para este domínio, o bloqueio pessimista oferece uma solução mais simples e segura.

---

Quais estados são terminais? Por que não faz sentido retornar de um estado terminal?

A entidade Reserva possui o seguinte ciclo de vida:

draft → confirmed → in_use → completed
   └──────────────→ canceled

Os estados terminais definidos para o sistema são:

completed
canceled

Um estado terminal representa o encerramento definitivo do fluxo de negócio, não permitindo novas transições.

Estado completed

Uma reserva é marcada como completed quando o período de utilização do equipamento é finalizado com sucesso.

Após esse momento, a reserva passa a representar um fato histórico e imutável.

Permitir a alteração de uma reserva concluída poderia gerar inconsistências, como:

comprometimento da rastreabilidade do sistema;
alteração indevida do histórico de utilização do equipamento;
inconsistência em relatórios e métricas de uso;
perda da confiabilidade dos registros de auditoria.
Estado canceled

Uma reserva é marcada como canceled quando o usuário ou o sistema interrompe definitivamente o processo antes do uso do equipamento.

Uma reserva cancelada deixa de produzir efeitos operacionais e não pode ser reativada.

Permitir a reabertura de uma reserva cancelada poderia gerar problemas como:

conflitos de horário com novas reservas já realizadas;
inconsistência no controle de disponibilidade do equipamento;
dificuldade de auditoria das decisões tomadas.
Implementação da regra

O sistema impede qualquer alteração em reservas que estejam em estados terminais.

Caso uma tentativa de modificação seja realizada, a API retorna o seguinte erro:

{
  "error": "TERMINAL_STATE",
  "message": "Não é possível alterar uma reserva finalizada.",
  "details": {
    "reservation_id": 15,
    "current_status": "completed"
  }
}

A adoção de estados terminais garante previsibilidade no fluxo de negócio, preserva a integridade dos dados e assegura a consistência histórica do sistema.

## Tecnologias Utilizadas

* Python 3.13
* FastAPI
* SQLAlchemy
* Pydantic v2
* PostgreSQL
* Alembic
* Docker
* Pytest

---

## Consistência em Cenários de Borda

Para garantir a integridade dos dados e a previsibilidade do sistema, foram identificados e tratados cenários de borda específicos do domínio de reserva de equipamentos.

### Cenário 1 — Exclusão de entidade pai com filhos ativos

**Situação:** tentativa de excluir um equipamento que possui reservas futuras ou manutenções ativas.

**Decisão adotada:** o sistema não permite a exclusão física do equipamento. Em vez disso, o equipamento deve ser marcado com o status `inactive`.

**Justificativa:** a exclusão física comprometeria a integridade referencial e causaria perda do histórico de utilização e manutenção do equipamento.

---

### Cenário 2 — Recurso indisponível

**Situação:** tentativa de criar uma reserva para um equipamento que está em manutenção ou marcado como inativo.

**Decisão adotada:** o sistema bloqueia a criação da reserva.

**Justificativa:** a disponibilidade do equipamento depende diretamente do seu estado operacional.


---

### Cenário 3 — Modificação de reserva em estado terminal

**Situação:** tentativa de alterar uma reserva com status `completed` ou `canceled`.

**Decisão adotada:** o sistema impede qualquer alteração na reserva.

**Justificativa:** estados terminais representam o encerramento definitivo do fluxo de negócio e devem ser imutáveis para garantir a rastreabilidade e a confiabilidade dos registros.



---

### Cenário 4 — Datas e horários sobrepostos

**Situação:** dois usuários tentam reservar o mesmo equipamento em períodos iguais ou sobrepostos.

**Decisão adotada:** o sistema identifica o conflito e rejeita a nova reserva.

**Justificativa:** um equipamento não pode ser utilizado simultaneamente por mais de um usuário.


---

### Cenário 5 — Período de reserva inválido

**Situação:** o usuário informa uma data de término anterior ou igual à data de início.

**Decisão adotada:** a requisição é rejeitada ainda na camada de validação.

**Justificativa:** uma reserva não pode possuir duração nula ou negativa.

Essa validação é realizada pelo Pydantic antes da execução das regras de negócio.




## Como Executar o Projeto Localmente

### 1. Clonar o repositório

```bash
git clone https://github.com/KevinTeixeir/Api_Reserva_De_Equipamentos.git
cd Api_Reserva_De_Equipamentos
```

### 2. Configurar as variáveis de ambiente

Crie um arquivo `.env` a partir do `.env.example`.

Exemplo:

```env
DATABASE_URL=postgresql://postgres:postgres@db:5432/reservations_db
SECRET_KEY=secret_key
PORT=8000
```

### 3. Subir os containers

```bash
docker compose up --build
```

### 4. Executar as migrations

```bash
docker compose run --rm api alembic upgrade head
```

### 5. Acessar a documentação da API

```text
http://localhost:8000/docs
```

---

## Testes Automatizados

Executar os testes:

```bash
docker compose run --rm api pytest
```

Executar os testes com cobertura:

```bash
docker compose run --rm api pytest --cov=app
```

Resultado esperado:

* 10 testes aprovados
* Cobertura superior a 80%

---

## Repositório

Código-fonte disponível em:

```text
https://github.com/KevinTeixeir/Api_Reserva_De_Equipamentos
```



# Decisões de Design e Consistência do Domínio

## Decisões de Design Justificadas

###  Por que os relacionamentos foram modelados dessa forma?

O relacionamento entre Usuário e Reserva foi modelado como 1:N, pois um usuário pode realizar várias reservas ao longo do tempo, enquanto cada reserva pertence a apenas um usuário.

O relacionamento entre Equipamento e Reserva também foi modelado como 1:N, pois um mesmo equipamento pode ser reservado várias vezes em períodos diferentes.

O relacionamento entre Equipamento e Manutenção foi modelado como 1:N porque um equipamento pode passar por diversos períodos de manutenção durante seu ciclo de vida.

O relacionamento entre Reserva e Histórico de Reserva foi modelado como 1:N para permitir rastreabilidade completa das mudanças de estado. Cada reserva pode possuir múltiplos registros de alteração, mas cada registro pertence a uma única reserva.

Essa modelagem evita duplicação de dados, facilita auditoria e preserva o histórico operacional do sistema.

---

### Por que algumas regras foram implementadas no Pydantic e outras na camada de serviço?

As validações implementadas no Pydantic são regras que dependem apenas dos dados enviados na própria requisição.

Exemplos:

* A data de término deve ser posterior à data de início.
* Campos obrigatórios não podem estar vazios.
* O tamanho mínimo e máximo de textos deve ser respeitado.

Essas regras foram implementadas com `@model_validator` e `Field`.

Já as regras implementadas na camada de serviço dependem de informações externas, consultas ao banco de dados ou estados de outras entidades.

Exemplos:

* Verificar se existe conflito de horário.
* Validar se o usuário está suspenso.
* Verificar se o equipamento está em manutenção.
* Limitar o número de reservas futuras.
* Validar transições de estado.

Essas validações exigem acesso ao banco de dados e, portanto, pertencem à camada de serviço.

---

### Por que a Migration 2 foi necessária?

Inicialmente, o sistema realizava a verificação de conflitos de reserva utilizando consultas sobre as colunas `equipment_id`, `start_date` e `end_date` sem um índice específico.

Com a evolução do domínio, identificou-se que essa consulta seria executada frequentemente e poderia degradar o desempenho à medida que o número de reservas aumentasse.

Por esse motivo, foi criada a Migration 2 para adicionar o índice composto `idx_reservation_period`.

Essa decisão demonstra que o entendimento do domínio evoluiu de uma preocupação apenas funcional para uma preocupação também relacionada à escalabilidade e desempenho.

---

### Como o sistema trata modificações simultâneas no mesmo recurso?

O cenário crítico ocorre quando dois usuários tentam reservar o mesmo equipamento para o mesmo período simultaneamente.

Para evitar inconsistências, foi implementado bloqueio pessimista utilizando `SELECT FOR UPDATE`.

Durante o processo de criação da reserva, o registro do equipamento é bloqueado até o término da transação.

Assim, apenas uma operação pode validar e confirmar a reserva por vez.

Caso a primeira transação confirme a reserva, a segunda transação será reavaliada e receberá um erro de conflito.

Essa abordagem elimina condições de corrida e garante consistência dos dados.

---

### Quais estados são terminais?

Os estados terminais da entidade Reserva são:

* `completed`
* `canceled`

Após atingir um estado terminal, não é permitido retornar para estados anteriores.

Uma reserva concluída representa um processo já executado e registrado no histórico.

Uma reserva cancelada representa uma decisão definitiva de interrupção do fluxo.

Permitir a reabertura de estados terminais comprometeria a rastreabilidade e a consistência do histórico operacional.

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
========================================================================================= tests coverage ==========================================================================================
________________________________________________________________________ coverage: platform linux, python 3.13.14-final-0 _________________________________________________________________________

Name                                         Stmts   Miss  Cover
----------------------------------------------------------------
app/__init__.py                                  0      0   100%
app/core/__init__.py                             0      0   100%
app/core/config.py                               8      0   100%
app/core/database.py                            16      4    75%
app/core/dependencies.py                         8      4    50%
app/core/exceptions.py                           9      0   100%
app/core/handlers.py                             7      0   100%
app/main.py                                     15      1    93%
app/models/__init__.py                           7      0   100%
app/models/equipment.py                         18      0   100%
app/models/maintenance.py                       24      0   100%
app/models/reservation.py                       31      0   100%
app/models/reservation_history.py               22      1    95%
app/models/user.py                              15      0   100%
app/repositories/__init__.py                     5      0   100%
app/repositories/equipment_repository.py        26     13    50%
app/repositories/maintenance_repository.py      12      4    67%
app/repositories/reservation_repository.py      34      3    91%
app/repositories/user_repository.py             17      0   100%
app/routers/__init__.py                          5      0   100%
app/routers/equipments.py                       18      3    83%
app/routers/maintenances.py                     10      1    90%
app/routers/reservations.py                     18      0   100%
app/routers/users.py                            13      0   100%
app/schemas/__init__.py                          5      0   100%
app/schemas/common.py                           22      0   100%
app/schemas/equipment.py                        20      0   100%
app/schemas/maintenance.py                      21      3    86%
app/schemas/reservation.py                      33      1    97%
app/schemas/user.py                             13      0   100%
app/services/__init__.py                         5      0   100%
app/services/equipment_service.py               27      9    67%
app/services/maintenance_service.py             18      7    61%
app/services/reservation_service.py             63      4    94%
app/services/user_service.py                    25      2    92%
----------------------------------------------------------------
TOTAL                                          590     60    90%
===================================================================================== short test summary info =====================================================================================
FAILED tests/test_pagination.py::test_reservation_pagination - pydantic_core._pydantic_core.PydanticSerializationError: Unable to serialize unknown type: <class 'app.models.reservation.Reservation'>
FAILED tests/test_reservations.py::test_unavailable_equipment_cannot_be_reserved - assert 201 == 409
=========================================================================== 2 failed, 10 passed, 61 warnings in 11.96s ============================================================================



-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
========================================================================================= tests coverage ==========================================================================================
________________________________________________________________________ coverage: platform linux, python 3.13.14-final-0 _________________________________________________________________________

Name                                         Stmts   Miss  Cover
----------------------------------------------------------------
app/__init__.py                                  0      0   100%
app/core/__init__.py                             0      0   100%
app/core/config.py                               8      0   100%
app/core/database.py                            16      4    75%
app/core/dependencies.py                         8      4    50%
app/core/exceptions.py                           9      0   100%
app/core/handlers.py                             7      0   100%
app/main.py                                     15      1    93%
app/models/__init__.py                           7      0   100%
app/models/equipment.py                         18      0   100%
app/models/maintenance.py                       24      0   100%
app/models/reservation.py                       31      0   100%
app/models/reservation_history.py               22      1    95%
app/models/user.py                              15      0   100%
app/repositories/__init__.py                     5      0   100%
app/repositories/equipment_repository.py        26     13    50%
app/repositories/maintenance_repository.py      12      4    67%
app/repositories/reservation_repository.py      34      3    91%
app/repositories/user_repository.py             17      0   100%
app/routers/__init__.py                          5      0   100%
app/routers/equipments.py                       18      3    83%
app/routers/maintenances.py                     10      1    90%
app/routers/reservations.py                     18      0   100%
app/routers/users.py                            13      0   100%
app/schemas/__init__.py                          5      0   100%
app/schemas/common.py                           22      0   100%
app/schemas/equipment.py                        20      0   100%
app/schemas/maintenance.py                      21      3    86%
app/schemas/reservation.py                      33      1    97%
app/schemas/user.py                             13      0   100%
app/services/__init__.py                         5      0   100%
app/services/equipment_service.py               27      9    67%
app/services/maintenance_service.py             18      7    61%
app/services/reservation_service.py             63      4    94%
app/services/user_service.py                    25      2    92%
----------------------------------------------------------------
TOTAL                                          590     60    90%
===================================================================================== short test summary info =====================================================================================
FAILED tests/test_pagination.py::test_reservation_pagination - pydantic_core._pydantic_core.PydanticSerializationError: Unable to serialize unknown type: <class 'app.models.reservation.Reservation'>
FAILED tests/test_reservations.py::test_unavailable_equipment_cannot_be_reserved - assert 201 == 409
=========================================================================== 2 failed, 10 passed, 61 warnings in 11.96s ============================================================================

PS C:\Users\paula\OneDrive\Área de Trabalho\Api_Reserva_De_Equipamentos> 