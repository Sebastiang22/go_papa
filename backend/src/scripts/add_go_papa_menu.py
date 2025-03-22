import asyncio
import sys
import os

# Add the src directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.mysql_inventory_manager import MySQLInventoryManager

async def add_go_papa_menu_items():
    """Add Go Papa menu items to the inventory."""
    inventory_manager = MySQLInventoryManager()
    restaurant_id = "go_papa"
    
    # Menu items with their details
    menu_items = [
        # Go Papa
        {"name": "Go Papa X2", "quantity": 1, "unit": "porción", "price": 50000},
        {"name": "Go Papa Familiar", "quantity": 1, "unit": "porción", "price": 85000},
        
        # La Gringa
        {"name": "La Gringa X2", "quantity": 1, "unit": "porción", "price": 50000},
        {"name": "La Gringa Familiar", "quantity": 1, "unit": "porción", "price": 85000},
        
        # Chicken
        {"name": "Chicken X2", "quantity": 1, "unit": "porción", "price": 45000},
        {"name": "Chicken Familiar", "quantity": 1, "unit": "porción", "price": 75000},
        
        # La Mexa
        {"name": "La Mexa X2", "quantity": 1, "unit": "porción", "price": 45000},
        {"name": "La Mexa Familiar", "quantity": 1, "unit": "porción", "price": 75000},
        
        # Hawaiana
        {"name": "Hawaiana X2", "quantity": 1, "unit": "porción", "price": 45000},
        {"name": "Hawaiana Familiar", "quantity": 1, "unit": "porción", "price": 75000},
        
        # Montañera
        {"name": "Montañera X2", "quantity": 1, "unit": "porción", "price": 45000},
        {"name": "Montañera Familiar", "quantity": 1, "unit": "porción", "price": 75000},
        
        # La 21
        {"name": "La 21 X2", "quantity": 1, "unit": "porción", "price": 45000},
        {"name": "La 21 Familiar", "quantity": 1, "unit": "porción", "price": 75000},
        
        # Flamenca
        {"name": "Flamenca X2", "quantity": 1, "unit": "porción", "price": 35000},
        {"name": "Flamenca Familiar", "quantity": 1, "unit": "porción", "price": 75000},
        
        # Italiana
        {"name": "Italiana X2", "quantity": 1, "unit": "porción", "price": 35000},
        {"name": "Italiana Familiar", "quantity": 1, "unit": "porción", "price": 75000},
        
        # Clasica
        {"name": "Clasica X2", "quantity": 1, "unit": "porción", "price": 25000},
        {"name": "Clasica Familiar", "quantity": 1, "unit": "porción", "price": 75000},
        
        # Go Papita
        {"name": "Go Papita", "quantity": 1, "unit": "porción", "price": 21000},

        # Bebidas
        {"name": "Agua", "quantity": 1, "unit": "unidad", "price": 3000},
        {"name": "Soda", "quantity": 1, "unit": "unidad", "price": 5000},
        {"name": "Hit 200 ml", "quantity": 1, "unit": "unidad", "price": 3000},
        {"name": "Hit 400 ml", "quantity": 1, "unit": "unidad", "price": 5000},
        {"name": "Hit Familiar", "quantity": 1, "unit": "unidad", "price": 8000},
        {"name": "Cerveza Poker", "quantity": 1, "unit": "unidad", "price": 6000},
        {"name": "Coca Cola", "quantity": 1, "unit": "unidad", "price": 5000},
        {"name": "Coca Cola Zero", "quantity": 1, "unit": "unidad", "price": 5000},
        {"name": "Coca Cola 1.5 Lt", "quantity": 1, "unit": "unidad", "price": 9000},
        {"name": "Postobón 1.5 Lt", "quantity": 1, "unit": "unidad", "price": 8000},
        {"name": "Coca Cola 3 Lt", "quantity": 1, "unit": "unidad", "price": 16000},
    ]
    
    # Add each menu item to the inventory
    for item in menu_items:
        result = await inventory_manager.add_product(
            restaurant_id=restaurant_id,
            name=item["name"],
            quantity=item["quantity"],
            unit=item["unit"],
            price=item["price"]
        )
        
        if result:
            print(f"Added {item['name']} to inventory")
        else:
            print(f"Failed to add {item['name']} to inventory")

if __name__ == "__main__":
    asyncio.run(add_go_papa_menu_items())