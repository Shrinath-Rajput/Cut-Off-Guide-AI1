import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

collegeItems = [
  {
    "id": "stanford",
    "rank": 1,
    "name": "Stanford University",
    "rating": "4.9",
    "location": "Stanford, California",
    "courses": ["CS", "Engineering", "MBA"],
    "feeLabel": "$56,000 / yr",
    "feeValue": 56000,
    "cutoff": "99.5%",
    "type": "Private",
    "state": "California",
    "image": "https://lh3.googleusercontent.com/aida-public/AB6AXuD3H4oNg_SwTzfTRJUPh6bA5a-OfI5-D3XguxBR_lRbk8HA8O5-jhDydRrQD8z3Oyev61VGU0sFJx4oDSSu7mN65Yq4JTGAh4PW6_y3LUMAuGxDLlm_QDg7oyc1bdYfbjYN4U8YWmsL8OwcEBzAY6cwN1vWkszJMHr8hi64Du10zvpy4DMkCvcAhnih5JwutryffQlRGG3K_ULjqKQgpMXQQIce1R9JsWIj0jWzmZ8ZkAYDkGAaJ00t",
    "acceptanceRate": "3.9%",
    "averagePackage": "$135k",
    "highestPackage": "$450k",
  },
  {
    "id": "mit",
    "rank": 2,
    "name": "Massachusetts Institute of Technology",
    "rating": "4.9",
    "location": "Cambridge, Massachusetts",
    "courses": ["Engineering", "CS", "Physics"],
    "feeLabel": "$55,450 / yr",
    "feeValue": 55450,
    "cutoff": "99.6%",
    "type": "Private",
    "state": "Massachusetts",
    "image": "https://lh3.googleusercontent.com/aida-public/AB6AXuDQk4oxUU88rmboCZNrKn7NmNMTquKZmbwKE8LYu6_mcvyR7whaRD08AhIN83wD4gbM39SxjMtoEsSory7uusYWgRRBoeto6XV6RxREUo67gO7_tfG5Wzqk_RhflUcnSXZ6gcJs3YwAwXm53GNJAzuzI7iYhS1mCZFUGRdwDNvpUiizKKozEk7YWUIZ1gEMzpLbFcFBZAtSxC9xaLEbK9DnT3bLkr1NBb4nn1I5BmhBOu73MSgXk6oY",
    "acceptanceRate": "4.0%",
    "averagePackage": "$128k",
    "highestPackage": "$420k",
  },
  {
    "id": "harvard",
    "rank": 3,
    "name": "Harvard University",
    "rating": "4.8",
    "location": "Cambridge, Massachusetts",
    "courses": ["Law", "Business", "Med"],
    "feeLabel": "$54,269 / yr",
    "feeValue": 54269,
    "cutoff": "99.4%",
    "type": "Private",
    "state": "Massachusetts",
    "image": "https://lh3.googleusercontent.com/aida-public/AB6AXuCY90ZS6vJTCwESsN-6T-V3ClglcvdauGVb0Q7ToUByMjp7YRvaAquogP64vo3hhdibvhKxlX_LiVm-usPlXRiqmR0eLzln3KFt_pXncv9QY3qVUNC1cS5AjGwub6IBzOr0IJjTnh_OeSICEQ65iJfNrA0818qdlDO4GVDYYNbQ-J2e0UKgSMxl5px5utybrLMwSWcyo-yEXCpfzLdgSaBgn4HmWU2XqBtSCd-7VawhlOR3TguYIl8a",
    "acceptanceRate": "3.2%",
    "averagePackage": "$130k",
    "highestPackage": "$440k",
  }
]

cutoffItems = [
    {
        "course": "Computer Engineering",
        "category": "Open",
        "gender": "Male",
        "university": "Mumbai University",
        "location": "Mumbai",
        "round": "Round 1",
        "percentile": "99.5",
        "rank": "150",
        "college_name": "VJTI Mumbai"
    },
    {
        "course": "Computer Engineering",
        "category": "OBC",
        "gender": "Female",
        "university": "Pune University",
        "location": "Pune",
        "round": "Round 2",
        "percentile": "98.2",
        "rank": "450",
        "college_name": "COEP Pune"
    }
]

async def seed_colleges():
    client = AsyncIOMotorClient(settings.MONGODB_URI)
    db = client[settings.MONGODB_DATABASE]
    
    # Drop existing collections to refresh seed data
    await db.colleges.drop()
    await db.cutoffs.drop()
    print("Dropped existing collections.")

    await db.colleges.insert_many(collegeItems)
    print(f"Inserted {len(collegeItems)} seed colleges!")

    await db.cutoffs.insert_many(cutoffItems)
    print(f"Inserted {len(cutoffItems)} seed cutoffs!")
        
    client.close()

if __name__ == "__main__":
    asyncio.run(seed_colleges())
