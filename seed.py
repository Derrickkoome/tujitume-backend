from app.database import SessionLocal, engine
from app import models

# Create a database session
db = SessionLocal()

# 1. Create Users
client = models.User(name="Mama Mboga", email="client@test.com", role="client")
worker = models.User(name="Derrick Student", email="derrick@test.com", role="worker")

db.add(client)
db.add(worker)
db.commit()

# 2. Create a Gig (Posted by Client, ID=1)
gig = models.Gig(
    title="Clean my Kiosk",
    description="Need someone to wash the shelves.",
    price=500,
    status="OPEN",
    client_id=client.id
)
db.add(gig)
db.commit()

# 3. Create an Application (Worker applied to Gig, ID=1)
application = models.Application(
    worker_id=worker.id,
    gig_id=gig.id,
    status="PENDING"
)
db.add(application)
db.commit()

print("✅ Database successfully seeded with dummy data!")
db.close()