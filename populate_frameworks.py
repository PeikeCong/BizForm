from models import SessionLocal, init_db, Framework, Category

init_db()
db = SessionLocal()

# Add SWOT Framework
swot = Framework(name="SWOT", description="A strategic planning tool to identify Strengths, Weaknesses, Opportunities, and Threats.")
swot.categories = [
    Category(name="Strengths"),
    Category(name="Weaknesses"),
    Category(name="Opportunities"),
    Category(name="Threats"),
]

# Add Porter's Five Forces Framework
porter = Framework(name="Porter’s Five Forces", description="A framework for analyzing the competitive intensity and attractiveness of an industry.")
porter.categories = [
    Category(name="Threat of New Entrants"),
    Category(name="Bargaining Power of Suppliers"),
    Category(name="Bargaining Power of Buyers"),
    Category(name="Threat of Substitutes"),
    Category(name="Industry Rivalry"),
]

# Commit both to the database
db.add_all([swot, porter])
db.commit()
db.close()

print("✅ Business consulting frameworks (SWOT + Porter's) inserted.")
