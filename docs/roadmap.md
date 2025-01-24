
# GraphQL-Driven Backend Roadmap

## Sequence diagram for diagnosis query flow

<img src="images/seq-diagram.svg" alt="Class-Diagram" width="900" />

## Class diagram for core backend components

<img src="images/class-diagram.svg" alt="Class-Diagram" width="900" />


## Flow diagram for backend development phases

<img src="images/graph.svg" alt="Diagram" width="600" />


## Phase 1: Core API with GraphQL Queries and Mocked Resolvers

### Tasks
1. **GraphQL Schema Design**:
   - Define the following queries and mutations:
     - **Queries**:
       - `queueDiagnosisQuery(patientId: ID!): Boolean` - Initiates a diagnosis query for a patient.
       - `queueGeolocationQuery(patientId: ID!): Boolean` - Initiates a geolocation query for a patient.
       - `fetchProvidersByAddress(address: AddressInput!): [Provider]` - Retrieves providers matching an address.
       - `fetchProvidersByQuery(queryId: ID!): [Provider]` - Retrieves providers linked to a specific query ID.
     - **Mutations**:
       - `enqueueDiagnosisQuery(patientId: ID!): String` - Queues a diagnosis query for processing and returns a tracking ID.
       - `enqueueGeolocationQuery(patientId: ID!): String` - Queues a geolocation query for processing and returns a tracking ID.

2. **Resolvers with Mocked Data**:
   - Implement mocked resolvers for these queries and mutations.
   - Use Pydantic models to define patient and provider schemas.
   - Simulate queuing and retrieval workflows.

3. **Unit Testing**:
   - Write tests for GraphQL resolvers using `pytest`.
   - Validate schema and ensure queries/mutations return expected outputs.

### Implementation Steps
- **GraphQL Schema**:
  ```python
  import strawberry

  @strawberry.type
  class Patient:
      id: str
      name: str
      age: int

  @strawberry.type
  class Query:
      @strawberry.field
      def queue_diagnosis_query(self, patient_id: str) -> bool:
          return True

      @strawberry.field
      def fetch_providers_by_address(self, address: str) -> list[str]:
          return ["Provider1", "Provider2"]

  schema = strawberry.Schema(query=Query)
  ```

- **Mock Data**:
  ```python
  from pydantic import BaseModel

  class MockPatient(BaseModel):
      id: str
      name: str
      age: int

  mock_patients = [
      MockPatient(id="1", name="John Doe", age=35),
      MockPatient(id="2", name="Jane Smith", age=28)
  ]
  ```

- **Unit Tests**:
  ```python
  import pytest
  from strawberry.test import GraphQLTestClient

  @pytest.fixture
  def client():
      return GraphQLTestClient(schema)

  def test_queue_diagnosis_query(client):
      query = """
      query {
          queueDiagnosisQuery(patientId: "1")
      }
      """
      result = client.query(query)
      assert result.data["queueDiagnosisQuery"] is True
  ```

### Deliverables
- Basic GraphQL schema with queries and mutations.
- Mocked resolvers for core functionality.
- Unit tests for schema validation.

---

## Phase 2: Domain Logic and Database Integration

### Tasks
1. **Domain Logic Integration**:
   - Connect GraphQL resolvers to domain interfaces:
     - `enqueueDiagnosisQuery` -> `IPatientStore.enqueue_diagnosis_query`.
     - `enqueueGeolocationQuery` -> `IPatientStore.enqueue_geolocation_query`.
     - `fetchProvidersByAddress` -> `IProviderRepository.fetch_providers_by_address`.
     - `fetchProvidersByQuery` -> `IProviderRepository.fetch_by_query`.

2. **Database Integration**:
   - Implement repository classes for patient and provider data.
   - Store queued queries and provider data in a relational database (e.g., PostgreSQL).

3. **Integration Testing**:
   - Write integration tests to validate resolver functionality with real database connections.

### Implementation Steps
- **Repository Pattern**:
  ```python
  from abc import ABC, abstractmethod

  class IPatientStore(ABC):
      @abstractmethod
      def enqueue_diagnosis_query(self, patient_id: str):
          pass

  class SupabasePatientStore(IPatientStore):
    async def enqueue_diagnosis_query(self, patient_id: str):
        async with async_session() as session:
            async with session.begin():
                patient = await session.execute(
                    select(Patient).where(Patient.id == patient_id)
                )
                patient = patient.scalar()
                if not patient:
                    raise ValueError(f"Patient with ID {patient_id} not found")
                print(f"Queuing diagnosis for {patient.name}")
                # Add logic for queuing with Supabase or another system
          print(f"Queuing diagnosis for {patient_id}")
  ```

- **Database Models**:
  ```python
  # Manage database migrations with Alembic for schema updates and versioning.
  from alembic import op
  import sqlalchemy as sa

  # Example migration script for adding a new column to the Patient table
  def upgrade():
      op.add_column('patients', sa.Column('phone_number', sa.String(), nullable=True))

  def downgrade():
      op.drop_column('patients', 'phone_number')

  # Integrate Alembic with Supabase or other relational databases via SQLAlchemy.
  from alembic.config import Config
  from alembic import command

  alembic_cfg = Config("alembic.ini")

  # Run migration
  command.upgrade(alembic_cfg, 'head')
  from sqlalchemy import Column, Integer, String, create_engine, MetaData
  from sqlalchemy.ext.declarative import declarative_base

  Base = declarative_base()

  class Patient(Base):
      __tablename__ = 'patients'
      id = Column(String, primary_key=True)
      name = Column(String)
      age = Column(Integer)

  engine = create_engine("postgresql://user:password@localhost/db")
  Base.metadata.create_all(engine)
  ```

- **Integration Tests**:
  ```python
  def test_enqueue_diagnosis_query():
      store = SupabasePatientStore()
      result = store.enqueue_diagnosis_query("1")
      assert result is None  # Assuming no return value for simplicity
  ```

### Deliverables
- Fully integrated resolvers using domain interfaces.
- Database-backed repository implementations.
- End-to-end tests for resolver and database workflows.

---

## Phase 3: Advanced Features and Real-Time Capabilities

### Tasks
1. **Real-Time Features**:
   - Implement GraphQL subscriptions for:
     - `queryStatusUpdated(queryId: ID!): QueryStatus` - Notifies patients about updates to their queries.
     - `providerStatusChanged(providerId: ID!): Provider` - Notifies changes in provider availability or status.

2. **Authentication and Role-Based Access Control (RBAC)**:
   - **Supabase JWT Verification**:
     ```python
     import os
     import jwt

     def verify_token(token):
         secret = os.getenv("supabase_secret")
         try:
             payload = jwt.decode(token, secret, algorithms=["HS256"])
             return payload
         except jwt.ExpiredSignatureError:
             return None
     ```

3. **Subscriptions**:
   ```python
   import asyncio
   from strawberry.subscriptions import GraphQLWSHandler
   from typing import Dict, AsyncGenerator
   from collections import defaultdict

   # Global dict to store queues for each query  
   _status_queues: Dict[str, asyncio.Queue] = defaultdict(asyncio.Queue)

  async def flush_query_queues():
    for queue in _status_queues:
      is_empty = False
      try:  
        if queue.empty():
          queue.task_done()
      except ValueError:
        del _status_queues[query_id]  

  async def query_status_updated(query_id: str) -> AsyncGenerator[dict, None]:
      queue = _status_queues[query_id]
      
       while True:
           status_update = await queue.get()
           yield status_update
           queue.task_done()

  async def publish_status_update(query_id: str, status: str):  
    """Helper function to publish status updates"""  
    if query_id in _status_queues:  
        await _status_queues[query_id].put({"status": status, "queryId": query_id})
  

   @strawberry.type
   class Subscription:
       @strawberry.subscription
       async def query_status_updated(self, query_id: str) -> str:
           async for status in query_status_updated(query_id):
               yield status
   ```

### Deliverables
- Real-time subscriptions for query and provider updates.
- Authentication and RBAC using Supabase tokens with fallback mechanisms for vendor independence.

---

## Phase 4: Observability and Deployment

### Tasks
1. **Monitoring and Logging**:
   ```yaml
   scrape_configs:
     - job_name: 'graphql-server'
       static_configs:
         - targets: ['localhost:8000']
   ```

2. **CI/CD Pipelines**:
   ```yaml
   name: CI/CD
   on: [push]
   jobs:
     build:
       runs-on: ubuntu-latest
       steps:
       - name: Check out code
         uses: actions/checkout@v3
       - name: Set up Python
         uses: actions/setup-python@v3
       - name: Install dependencies
         run: pip install -r requirements.txt
       - name: Run tests
         run: pytest
   ```

### Deliverables
- Logging and monitoring tools for API performance.
- Automated CI/CD pipelines for testing and deployment.
- Production-ready backend with optimized subscriptions.

---

## Summary of Deliverables

| **Phase**         | **Deliverables**                                                                                   |
|--------------------|---------------------------------------------------------------------------------------------------|
| **Phase 1**       | Initial GraphQL schema, mocked resolvers, and unit tests.                                         |
| **Phase 2**       | Fully integrated resolvers with domain logic and database connections.                             |
| **Phase 3**       | Real-time subscriptions, advanced filters, recommendations, and secure endpoints.                 |
| **Phase 4**       | Observability tools, CI/CD pipelines, and production-ready deployment.                            |


